import os
import sys
import json
import random

from src.graph import Graph
from src.bfs_dfs import bfs, dfs
from src.dijkstra import dijkstra, reconstruct_path
from src.bellman_ford import bellman_ford, reconstruct_path_bf
from src.loader_parte2 import build_graph, save_report
from src.metrics import (
    run_timed,
    describe_graph,
    format_bfs_result,
    format_dfs_result,
    format_dijkstra_result,
    format_bf_result,
    build_performance_table,
    save_json,
)
from src.visualizations import (
    plot_degree_distribution,
    plot_in_out_degree_distribution,
    plot_degree_scatter,
    plot_weight_distribution,
    plot_performance_bars,
    plot_distance_heatmap,
    plot_algorithm_comparison_lines,
    plot_bfs_layers,
    plot_dfs_edge_classes,
    plot_dijkstra_paths,
    plot_bellman_ford_scenarios,
    plot_top_hubs_ranking,
    plot_category_distribution,
    export_graph_sample_pyvis,
)

PREFERRED_SOURCES = [
    "United_States", "Science", "Africa",
    "Europe", "Mathematics", "Philosophy",
    "Brazil", "Music", "Film",
]

PREFERRED_PAIRS = [
    ("United_States", "Africa"),
    ("Science", "Philosophy"),
    ("Mathematics", "Music"),
    ("Europe", "Brazil"),
    ("Film", "Science"),
]


def pick_nodes(graph, preferred, n):
    result = [p for p in preferred if p in graph.nodes]
    if len(result) < n:
        extras = [
            node for node in sorted(graph.nodes, key=lambda u: -graph.degree(u))
            if node not in result
        ]
        result += extras[: n - len(result)]
    return result[:n]


def directed_degree_summary(graph, limit=10):
    in_degree = {node: 0 for node in graph.nodes}
    out_degree = {node: graph.degree(node) for node in graph.nodes}
    for _, v, _ in graph.edges():
        in_degree[v] = in_degree.get(v, 0) + 1

    top_out = sorted(out_degree.items(), key=lambda item: (-item[1], item[0]))[:limit]
    top_in = sorted(in_degree.items(), key=lambda item: (-item[1], item[0]))[:limit]
    return {
        "top_out_degree": [{"node": node, "degree": degree} for node, degree in top_out],
        "top_in_degree": [{"node": node, "degree": degree} for node, degree in top_in],
        "avg_in_degree": round(sum(in_degree.values()) / max(len(in_degree), 1), 2),
        "avg_out_degree": round(sum(out_degree.values()) / max(len(out_degree), 1), 2),
    }


def weight_summary(graph):
    weights = [w for _, _, w in graph.edges()]
    if not weights:
        return {}
    return {
        "min": min(weights),
        "max": max(weights),
        "avg": round(sum(weights) / len(weights), 6),
        "model": "peso = 1 / grau_de_saida da origem",
        "interpretation": (
            "arestas saindo de artigos com poucos links recebem maior peso; "
            "arestas saindo de hubs recebem menor peso individual"
        ),
    }


def build_avd_notes():
    return [
        "Cores de algoritmos foram mantidas consistentes nos graficos comparativos.",
        "Graficos de barras e linhas usam eixos rotulados para favorecer comparabilidade.",
        "O heatmap separa distancia infinita de distancia zero para evitar leitura enganosa.",
        "A visualizacao interativa reduz ruido com amostragem, transparencia e filtros por categoria.",
        "Bellman-Ford aparece observado porque foi executado em subgrafo controlado pelo custo O(V*E).",
        "A principal limitacao visual e a densidade: 119.882 arestas sobrepostas tornam o grafo completo ilegivel sem filtros.",
    ]


def save_avd_markdown(report, out_dir):
    graph = report["graph_description"]
    degree = graph["degree_stats"]
    lines = [
        "# Notas Analiticas AVD - Parte 2",
        "",
        "## Contexto",
        "O dataset Wikispeedia foi modelado como grafo dirigido e ponderado: cada artigo e um no, cada hiperlink e uma aresta, e o peso segue a regra `1 / grau_de_saida`.",
        "",
        "## Leitura do Dataset",
        f"- Nos: {graph['num_nodes']}",
        f"- Arestas: {graph['num_edges']}",
        f"- Grau medio de saida: {degree.get('avg')}",
        f"- Grau maximo de saida: {degree.get('max')}",
        f"- Grau mediano de saida: {degree.get('median')}",
        "",
        "## Insights Visuais",
        "- A distribuicao de graus tem cauda longa: poucos artigos funcionam como hubs, enquanto a maioria concentra poucos links de saida.",
        "- A comparacao entre grau de entrada e saida ajuda a separar artigos que apontam para muitos temas daqueles que recebem muitas referencias.",
        "- O heatmap de Dijkstra evidencia quais pares sao proximos no modelo ponderado e evita confundir distancia infinita com distancia zero.",
        "- Os graficos de desempenho usam cores consistentes por algoritmo para reduzir carga cognitiva e melhorar comparabilidade.",
        "",
        "## Comparacao dos Algoritmos",
        "- BFS e adequado quando o objetivo e minimizar numero de saltos, ignorando pesos.",
        "- DFS e adequado para explorar profundidade, ciclos e classificacao de arestas.",
        "- Dijkstra e adequado para pesos nao negativos e caminhos de menor custo no modelo escolhido.",
        "- Bellman-Ford e adequado quando ha pesos negativos, mas seu custo O(V*E) limita o uso no grafo completo.",
        "",
        "## Limitacoes AVD",
        "- O grafo completo com 119.882 arestas sofre com sobreposicao visual; por isso filtros, amostragem e transparencia sao essenciais.",
        "- O peso `1 / grau_de_saida` favorece links de artigos especializados e pode reduzir a importancia visual de hubs generalistas.",
        "- Comparar Bellman-Ford com os outros algoritmos exige cuidado, pois ele foi executado em subgrafo controlado para manter viabilidade.",
        "",
        "## Arquivos Visuais Gerados",
        "- `degree_distribution.png`",
        "- `in_out_degree_distribution.png`",
        "- `degree_in_out_scatter.png`",
        "- `weight_distribution.png`",
        "- `performance_bars.png`",
        "- `comparison_lines.png`",
        "- `bfs_layers.png`",
        "- `dfs_edge_classes.png`",
        "- `dijkstra_paths.png`",
        "- `bellman_ford_scenarios.png`",
        "- `distance_heatmap.png`",
        "- `grafo_interativo.html`",
    ]
    path = os.path.join(out_dir, "parte2_avd_notes.md")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"Notas AVD salvas em {path}")
        return path
    except PermissionError as exc:
        print(f"AVISO: nao foi possivel salvar {path}: {exc}")
        return None


def run_parte2(data_dir, out_dir, alg=None, source=None, target=None):
    os.makedirs(out_dir, exist_ok=True)

    print("=== Construindo grafo Wikispeedia ===")
    graph, _, _, article_categories = build_graph(data_dir)

    nodes_list = list(graph.nodes)
    if not nodes_list:
        print("Grafo vazio. Verifique os arquivos em data/dataset_parte2/")
        sys.exit(1)

    bfs_sources = pick_nodes(graph, PREFERRED_SOURCES, 3)

    dijk_pairs = [
        (u, v) for u, v in PREFERRED_PAIRS if u in graph.nodes and v in graph.nodes
    ]
    top_nodes = [
        n for n in sorted(graph.nodes, key=lambda u: -graph.degree(u))
    ]
    while len(dijk_pairs) < 5 and len(top_nodes) >= 2:
        u, v = top_nodes.pop(0), top_nodes.pop(0)
        if (u, v) not in dijk_pairs:
            dijk_pairs.append((u, v))

    bf_src = bfs_sources[0]
    bf_tgt = bfs_sources[1] if len(bfs_sources) > 1 else nodes_list[1]

    graph_info = describe_graph(graph)
    graph_info["directed_degree_summary"] = directed_degree_summary(graph)
    graph_info["weight_summary"] = weight_summary(graph)
    print(json.dumps(graph_info, indent=2, default=str))

    performance_log = []
    report = {
        "dataset": "Wikispeedia — Wikipedia Navigation Links",
        "graph_description": graph_info,
        "bfs": [],
        "dfs": [],
        "dijkstra": [],
        "bellman_ford": [],
        "avd_notes": build_avd_notes(),
    }

    print("\n=== BFS ===")
    for src in bfs_sources:
        res, t, mem = run_timed(bfs, graph, src, track_memory=True)
        fmt = format_bfs_result(res, src)
        fmt["time_s"] = t
        fmt["mem_kb"] = mem
        report["bfs"].append(fmt)
        performance_log.append({"algorithm": "BFS", "task": f"source={src}", "time_s": t, "mem_kb": mem})
        print(f"BFS {src}: {res['visited_count']} nós, {len(res['layers'])} camadas, {t:.4f}s")

    print("\n=== DFS ===")
    for src in bfs_sources:
        res, t, mem = run_timed(dfs, graph, src, track_memory=True)
        fmt = format_dfs_result(res, src)
        fmt["time_s"] = t
        fmt["mem_kb"] = mem
        report["dfs"].append(fmt)
        performance_log.append({"algorithm": "DFS", "task": f"source={src}", "time_s": t, "mem_kb": mem})
        print(f"DFS {src}: ciclo={res['has_cycle']}, {res['visited_count']} nós, {t:.4f}s")

    print("\n=== Dijkstra ===")
    distance_matrix = {}
    sample_labels = []
    for u, v in dijk_pairs[:5]:
        try:
            res, t, mem = run_timed(dijkstra, graph, u, v, track_memory=True)
            path = reconstruct_path(res["parent"], u, v)
            fmt = format_dijkstra_result(res["dist"], res["parent"], u, v, path)
            fmt["time_s"] = t
            fmt["mem_kb"] = mem
            report["dijkstra"].append(fmt)
            performance_log.append({"algorithm": "Dijkstra", "task": f"{u}->{v}", "time_s": t, "mem_kb": mem})
            if u not in distance_matrix:
                distance_matrix[u] = {}
                sample_labels.append(u)
            if v not in sample_labels:
                sample_labels.append(v)
            distance_matrix[u][v] = res["dist"].get(v, float("inf"))
            print(f"Dijkstra {u}->{v}: dist={fmt['distance']}, path_len={fmt['path_length']}, {t:.4f}s")
        except ValueError as e:
            print(f"  AVISO Dijkstra: {e}")

    heatmap_labels = sample_labels[:8]
    for u in heatmap_labels:
        distance_matrix.setdefault(u, {})
        try:
            res = dijkstra(graph, u)
            for v in heatmap_labels:
                distance_matrix[u][v] = res["dist"].get(v, float("inf"))
        except ValueError:
            pass

    print("\n=== Preparando subgrafo para Bellman-Ford (top 200 nós) ===")
    top200 = sorted(graph.nodes, key=lambda u: -graph.degree(u))[:200]
    top200_set = set(top200)
    bf_graph = Graph(directed=True)
    for u in top200:
        bf_graph.add_node(u)
    for u in top200:
        for v, w in graph.get_neighbors(u):
            if v in top200_set:
                bf_graph.add_edge(u, v, w)
    print(f"Subgrafo BF: {bf_graph.num_nodes()} nós, {bf_graph.num_edges()} arestas")

    bf_src_sub = bf_src if bf_src in top200_set else top200[0]
    bf_tgt_sub = bf_tgt if bf_tgt in top200_set else top200[1]

    print("\n=== Bellman-Ford (pesos normais) ===")
    res, t, mem = run_timed(bellman_ford, bf_graph, bf_src_sub, track_memory=True)
    path = reconstruct_path_bf(res["parent"], bf_src_sub, bf_tgt_sub)
    fmt = format_bf_result(res, bf_src_sub, bf_tgt_sub, path)
    fmt["time_s"] = t
    fmt["mem_kb"] = mem
    fmt["scenario"] = "normal_weights"
    fmt["note"] = "Executado em subgrafo dos 200 nós mais conectados"
    report["bellman_ford"].append(fmt)
    performance_log.append({"algorithm": "Bellman-Ford", "task": f"{bf_src_sub}->{bf_tgt_sub}", "time_s": t, "mem_kb": mem})
    print(f"BF {bf_src_sub}->{bf_tgt_sub}: dist={fmt['distance']}, neg_cycle={fmt['has_negative_cycle']}, {t:.4f}s")

    print("\n=== Bellman-Ford (peso negativo sem ciclo negativo) ===")
    g_neg = Graph(directed=True)
    g_neg.add_edge("BF_A", "BF_B", 4.0)
    g_neg.add_edge("BF_A", "BF_C", 2.0)
    g_neg.add_edge("BF_C", "BF_B", -1.0)
    g_neg.add_edge("BF_B", "BF_D", 3.0)
    g_neg.add_edge("BF_C", "BF_D", 5.0)
    neg_u, neg_v = "BF_A", "BF_D"
    res_neg, t, mem = run_timed(bellman_ford, g_neg, neg_u, track_memory=True)
    path_neg = reconstruct_path_bf(res_neg["parent"], neg_u, neg_v)
    fmt_neg = format_bf_result(res_neg, neg_u, neg_v, path_neg)
    fmt_neg["time_s"] = t
    fmt_neg["mem_kb"] = mem
    fmt_neg["scenario"] = "negative_weight_no_cycle"
    fmt_neg["injected_edge"] = "BF_C->BF_B w=-1.0"
    fmt_neg["note"] = "Executado em grafo controlado sem ciclo negativo para validar corretude"
    report["bellman_ford"].append(fmt_neg)
    performance_log.append({"algorithm": "Bellman-Ford", "task": f"neg_no_cycle_{neg_u}->{neg_v}", "time_s": t, "mem_kb": mem})
    print(f"BF neg {neg_u}->{neg_v}: dist={fmt_neg['distance']}, neg_cycle={fmt_neg['has_negative_cycle']}, {t:.4f}s")

    print("\n=== Bellman-Ford (ciclo negativo detectado) ===")
    cycle_g = Graph(directed=True)
    a, b, c = bfs_sources[0], bfs_sources[1], bfs_sources[2] if len(bfs_sources) >= 3 else nodes_list[2]
    cycle_g.add_edge(a, b, -1.0)
    cycle_g.add_edge(b, c, -1.0)
    cycle_g.add_edge(c, a, -1.0)
    res_cycle, t, mem = run_timed(bellman_ford, cycle_g, a, track_memory=True)
    fmt_cycle = {
        "scenario": "negative_cycle_detected",
        "nodes_in_cycle": [a, b, c],
        "injected_edges": [f"{a}->{b}", f"{b}->{c}", f"{c}->{a}"],
        "has_negative_cycle": res_cycle["has_negative_cycle"],
        "time_s": t,
        "mem_kb": mem,
    }
    report["bellman_ford"].append(fmt_cycle)
    performance_log.append({"algorithm": "Bellman-Ford", "task": "neg_cycle_detection", "time_s": t, "mem_kb": mem})
    print(f"BF ciclo negativo detectado: {res_cycle['has_negative_cycle']}, {t:.4f}s")

    report["performance_table"] = build_performance_table(performance_log)
    save_report(report, out_dir)
    save_avd_markdown(report, out_dir)

    print("\n=== Gerando visualizações ===")
    plot_degree_distribution(graph, out_dir)
    plot_in_out_degree_distribution(graph, out_dir)
    plot_degree_scatter(graph, out_dir)
    plot_weight_distribution(graph, out_dir)
    plot_performance_bars(performance_log, out_dir)
    plot_algorithm_comparison_lines(performance_log, out_dir)
    plot_bfs_layers(report["bfs"], out_dir)
    plot_dfs_edge_classes(report["dfs"], out_dir)
    plot_dijkstra_paths(report["dijkstra"], out_dir)
    plot_bellman_ford_scenarios(report["bellman_ford"], out_dir)
    plot_top_hubs_ranking(graph, out_dir, n=15)
    plot_category_distribution(article_categories, out_dir)
    if heatmap_labels:
        plot_distance_heatmap(distance_matrix, heatmap_labels, out_dir)
    export_graph_sample_pyvis(graph, out_dir, article_categories=article_categories)

    print("\n=== Gerando dashboard analítico ===")
    try:
        from src.dashboard_parte2 import generate_dashboard
        from pathlib import Path
        dash_path = generate_dashboard(data_dir=Path(data_dir), out_dir=Path(out_dir))
        print(f"Dashboard gerado em {dash_path}")
    except Exception as exc:
        print(f"AVISO: nao foi possivel gerar o dashboard: {exc}")

    print(f"\n=== Parte 2 concluída. Saídas em {out_dir} ===")
    return report
