import os
import json
from collections import Counter, defaultdict


ALGORITHM_COLORS = {
    "BFS": "#2563EB",
    "DFS": "#059669",
    "Dijkstra": "#D97706",
    "Bellman-Ford": "#DC2626",
}

EDGE_CLASS_COLORS = {
    "tree": "#2563EB",
    "back": "#DC2626",
    "forward": "#D97706",
    "cross": "#64748B",
}


def _style_axes(ax):
    ax.grid(axis="y", color="#E5E7EB", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _save_fig(fig, out_dir, filename):
    path = os.path.join(out_dir, filename)
    fig.tight_layout()
    try:
        fig.savefig(path, dpi=160, bbox_inches="tight")
    except PermissionError:
        stem, ext = os.path.splitext(filename)
        path = os.path.join(out_dir, f"{stem}_avd{ext}")
        fig.savefig(path, dpi=160, bbox_inches="tight")
    return path


def plot_degree_distribution(graph, out_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib nao instalado; pulando grafico de distribuicao de graus.")
        return None

    degrees = [graph.degree(u) for u in graph.nodes]
    counter = Counter(degrees)
    x = sorted(counter.keys())
    y = [counter[d] for d in x]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x, y, color="#2563EB", edgecolor="white", linewidth=0.5)
    ax.set_xlabel("Grau de saida", fontsize=12)
    ax.set_ylabel("Frequencia (escala log)", fontsize=12)
    ax.set_title("Distribuicao de Graus de Saida - Wikispeedia", fontsize=14)
    ax.set_yscale("log")
    _style_axes(ax)
    path = _save_fig(fig, out_dir, "degree_distribution.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def _directed_degrees(graph):
    out_degrees = {u: graph.degree(u) for u in graph.nodes}
    in_degrees = {u: 0 for u in graph.nodes}
    for u, v, _ in graph.edges():
        in_degrees.setdefault(u, 0)
        in_degrees[v] = in_degrees.get(v, 0) + 1
    return in_degrees, out_degrees


def plot_in_out_degree_distribution(graph, out_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    in_degrees, out_degrees = _directed_degrees(graph)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    for ax, values, title, color in [
        (axes[0], out_degrees.values(), "Grau de Saida", "#2563EB"),
        (axes[1], in_degrees.values(), "Grau de Entrada", "#059669"),
    ]:
        counter = Counter(values)
        x = sorted(counter.keys())
        y = [counter[d] for d in x]
        ax.bar(x, y, color=color, edgecolor="white", linewidth=0.4)
        ax.set_title(title)
        ax.set_xlabel("Grau")
        ax.set_yscale("log")
        _style_axes(ax)
    axes[0].set_ylabel("Frequencia (escala log)")
    fig.suptitle("Distribuicao de Grau em Grafo Dirigido", fontsize=14)
    path = _save_fig(fig, out_dir, "in_out_degree_distribution.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_degree_scatter(graph, out_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    in_degrees, out_degrees = _directed_degrees(graph)
    xs = [out_degrees[u] for u in graph.nodes]
    ys = [in_degrees.get(u, 0) for u in graph.nodes]
    sizes = [10 + min(out_degrees[u] + in_degrees.get(u, 0), 250) * 0.25 for u in graph.nodes]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(xs, ys, s=sizes, color="#2563EB", alpha=0.35, edgecolors="none")
    ax.set_title("Relacao entre Grau de Saida e Entrada")
    ax.set_xlabel("Grau de saida")
    ax.set_ylabel("Grau de entrada")
    _style_axes(ax)
    path = _save_fig(fig, out_dir, "degree_in_out_scatter.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_weight_distribution(graph, out_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    weights = [w for _, _, w in graph.edges()]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(weights, bins=40, color="#7C3AED", edgecolor="white", linewidth=0.5)
    ax.set_title("Distribuicao dos Pesos das Arestas")
    ax.set_xlabel("Peso = 1 / grau de saida")
    ax.set_ylabel("Quantidade de arestas")
    _style_axes(ax)
    path = _save_fig(fig, out_dir, "weight_distribution.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_performance_bars(performance_entries, out_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    alg_times = {}
    for entry in performance_entries:
        alg = entry["algorithm"]
        alg_times.setdefault(alg, []).append(entry["time_s"])

    algs = [a for a in ALGORITHM_COLORS if a in alg_times]
    avg_times = [sum(alg_times[a]) / len(alg_times[a]) for a in algs]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(algs, avg_times, color=[ALGORITHM_COLORS[a] for a in algs], edgecolor="white")
    ax.set_ylabel("Tempo medio (s)", fontsize=12)
    ax.set_title("Desempenho Medio por Algoritmo", fontsize=14)
    for bar, val in zip(bars, avg_times):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{val:.4f}s",
                ha="center", va="bottom", fontsize=9)
    _style_axes(ax)
    fig.text(
        0.02, 0.01,
        "Obs.: Bellman-Ford foi medido em subgrafo controlado por custo O(V*E).",
        fontsize=9, color="#475569"
    )
    path = _save_fig(fig, out_dir, "performance_bars.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_distance_heatmap(distance_matrix, labels, out_dir):
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        return None

    all_labels = list(labels)
    for u, row in distance_matrix.items():
        if u not in all_labels:
            all_labels.append(u)
        for v in row:
            if v not in all_labels:
                all_labels.append(v)

    n = len(all_labels)
    matrix = []
    masked_positions = []
    for i, u in enumerate(all_labels):
        row_values = []
        for j, v in enumerate(all_labels):
            d = distance_matrix.get(u, {}).get(v, float("inf"))
            if d == float("inf"):
                row_values.append(float("nan"))
                masked_positions.append((i, j))
            else:
                row_values.append(d)
        matrix.append(row_values)

    arr = np.array(matrix, dtype=float)
    positive = arr[np.isfinite(arr) & (arr > 0)]
    vmin = float(positive.min()) if positive.size else None
    vmax = float(positive.max()) if positive.size else None
    fig, ax = plt.subplots(figsize=(8, 7))
    cmap = plt.cm.coolwarm.copy()
    cmap.set_bad(color="#E5E7EB")
    im = ax.imshow(arr, cmap=cmap, aspect="auto", vmin=vmin, vmax=vmax)
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(all_labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(all_labels, fontsize=8)
    for i, j in masked_positions:
        ax.text(j, i, "inf", ha="center", va="center", fontsize=7, color="#64748B")
    fig.colorbar(im, ax=ax, label="Distancia ponderada (positivas normalizadas)")
    ax.set_title("Heatmap de Distancias entre Pares (Dijkstra)", fontsize=13)
    path = _save_fig(fig, out_dir, "distance_heatmap.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_algorithm_comparison_lines(performance_entries, out_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    alg_series = {}
    for entry in performance_entries:
        alg_series.setdefault(entry["algorithm"], []).append(entry["time_s"])

    fig, ax = plt.subplots(figsize=(9, 5))
    markers = {"BFS": "o", "DFS": "s", "Dijkstra": "^", "Bellman-Ford": "D"}
    for alg in [a for a in ALGORITHM_COLORS if a in alg_series]:
        times = alg_series[alg]
        ax.plot(
            range(1, len(times) + 1), times, label=alg,
            marker=markers.get(alg, "o"), color=ALGORITHM_COLORS[alg], linewidth=2,
        )
    ax.set_xlabel("Tarefa dentro do algoritmo", fontsize=11)
    ax.set_ylabel("Tempo (s)", fontsize=11)
    ax.set_title("Comparacao de Tempo por Tarefa", fontsize=13)
    ax.legend()
    _style_axes(ax)
    fig.text(
        0.02, 0.01,
        "Cada ponto representa uma fonte, par origem-destino ou cenario de teste.",
        fontsize=9, color="#475569"
    )
    path = _save_fig(fig, out_dir, "comparison_lines.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_bfs_layers(bfs_entries, out_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    if not bfs_entries:
        return None

    labels = [entry["source"] for entry in bfs_entries]
    max_layer = max(max(map(int, entry["layer_sizes"].keys())) for entry in bfs_entries)
    x = range(len(labels))
    bottoms = [0] * len(labels)
    palette = ["#DBEAFE", "#93C5FD", "#60A5FA", "#3B82F6", "#2563EB", "#1D4ED8", "#1E40AF", "#1E3A8A"]

    fig, ax = plt.subplots(figsize=(10, 5))
    for layer in range(max_layer + 1):
        vals = [entry["layer_sizes"].get(str(layer), entry["layer_sizes"].get(layer, 0)) for entry in bfs_entries]
        ax.bar(x, vals, bottom=bottoms, label=f"Camada {layer}", color=palette[layer % len(palette)], edgecolor="white")
        bottoms = [b + v for b, v in zip(bottoms, vals)]

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("Nos visitados")
    ax.set_title("BFS: Alcance por Camadas")
    ax.legend(ncol=4, fontsize=8)
    _style_axes(ax)
    path = _save_fig(fig, out_dir, "bfs_layers.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_dfs_edge_classes(dfs_entries, out_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    if not dfs_entries:
        return None

    labels = [entry["source"] for entry in dfs_entries]
    classes = ["tree", "back", "forward", "cross"]
    x = range(len(labels))
    bottoms = [0] * len(labels)

    fig, ax = plt.subplots(figsize=(9, 5))
    for cls in classes:
        vals = [entry["edge_class_counts"].get(cls, 0) for entry in dfs_entries]
        ax.bar(x, vals, bottom=bottoms, label=cls, color=EDGE_CLASS_COLORS[cls], edgecolor="white")
        bottoms = [b + v for b, v in zip(bottoms, vals)]
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("Arestas classificadas")
    ax.set_title("DFS: Classificacao de Arestas por Fonte")
    ax.legend()
    _style_axes(ax)
    path = _save_fig(fig, out_dir, "dfs_edge_classes.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_dijkstra_paths(dijkstra_entries, out_dir):
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        return None

    if not dijkstra_entries:
        return None

    labels = [f"{e['source']} -> {e['target']}" for e in dijkstra_entries]
    distances = [0 if e["distance"] == float("inf") else e["distance"] for e in dijkstra_entries]
    hops = [(e.get("path_length") or 1) - 1 for e in dijkstra_entries]
    x = np.arange(len(labels))
    width = 0.38

    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax2 = ax1.twinx()
    bars1 = ax1.bar(x - width / 2, distances, width, label="Distancia ponderada", color=ALGORITHM_COLORS["Dijkstra"])
    bars2 = ax2.bar(x + width / 2, hops, width, label="Saltos", color="#64748B")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=25, ha="right", fontsize=8)
    ax1.set_ylabel("Distancia ponderada")
    ax2.set_ylabel("Saltos no caminho")
    ax1.set_title("Dijkstra: Custo Ponderado vs Quantidade de Saltos")
    ax1.bar_label(bars1, fmt="%.3f", fontsize=8, padding=2)
    ax2.bar_label(bars2, fmt="%d", fontsize=8, padding=2)
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")
    _style_axes(ax1)
    ax2.spines["top"].set_visible(False)
    path = _save_fig(fig, out_dir, "dijkstra_paths.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_bellman_ford_scenarios(bf_entries, out_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    if not bf_entries:
        return None

    labels = []
    times = []
    colors = []
    for entry in bf_entries:
        scenario = entry.get("scenario", "cenario")
        labels.append(scenario.replace("_", "\n"))
        times.append(entry.get("time_s", 0))
        colors.append("#DC2626" if entry.get("has_negative_cycle") else ALGORITHM_COLORS["Bellman-Ford"])

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, times, color=colors, edgecolor="white")
    ax.set_ylabel("Tempo (s)")
    ax.set_title("Bellman-Ford: Cenarios de Peso Negativo")
    ax.bar_label(bars, labels=[f"{v:.4f}s" for v in times], fontsize=9, padding=3)
    _style_axes(ax)
    path = _save_fig(fig, out_dir, "bellman_ford_scenarios.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_top_hubs_ranking(graph, out_dir, n=15):
    """Ranking dos N maiores hubs por grau de saida (barras horizontais)."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib nao instalado; pulando ranking de hubs.")
        return None

    from urllib.parse import unquote as _unq

    pairs = sorted(((u, graph.degree(u)) for u in graph.nodes),
                   key=lambda x: x[1], reverse=True)[:n]
    labels = [_unq(u).replace("_", " ") for u, _ in pairs]
    values = [d for _, d in pairs]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(range(len(labels)), values, color="#0ea5e9", edgecolor="white", linewidth=0.5)
    # Destaque para o top 3
    for i, b in enumerate(bars[:3]):
        b.set_color("#f59e0b")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("Grau (numero de links de saida)", fontsize=12)
    ax.set_title(f"Top {n} Hubs do Wikispeedia", fontsize=14)
    ax.grid(axis="x", color="#E5E7EB", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    # Anotar valores nas barras
    for i, v in enumerate(values):
        ax.text(v + max(values) * 0.005, i, str(v), va="center", fontsize=9, color="#374151")
    path = _save_fig(fig, out_dir, "top_hubs_ranking.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


def plot_category_distribution(article_categories, out_dir):
    """Distribuicao de artigos por categoria (barras horizontais ordenadas).

    article_categories pode ser:
      - dict {article: str_category}, ou
      - dict {article: set([categories])} (formato do loader; usa _node_cat)
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib nao instalado; pulando distribuicao de categorias.")
        return None

    if not article_categories:
        print("Sem dados de categorias; pulando.")
        return None

    # Detectar formato: se valores sao sets, usar _node_cat para resolver categoria principal
    sample = next(iter(article_categories.values()))
    if isinstance(sample, (set, list, tuple)):
        cat_map = _node_cat(article_categories)
    else:
        cat_map = article_categories

    counter = Counter(cat_map.values())
    items = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    labels = [c.replace("_", " ") for c, _ in items]
    values = [c for _, c in items]

    # Cores: usar paleta similar aos node colors do grafo interativo
    palette = ["#34d399", "#0ea5e9", "#c084fc", "#fde047", "#fb923c", "#4ade80",
               "#bae6fd", "#e879f9", "#f472b6", "#fb7c3c", "#a78bfa", "#fbbf24",
               "#22d3ee", "#86efac", "#f87171", "#94a3b8"]
    colors = [palette[i % len(palette)] for i in range(len(labels))]

    fig, ax = plt.subplots(figsize=(10, max(5, len(labels) * 0.35)))
    bars = ax.barh(range(len(labels)), values, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("Numero de artigos", fontsize=12)
    ax.set_title("Distribuicao de Artigos por Categoria", fontsize=14)
    ax.grid(axis="x", color="#E5E7EB", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    total = sum(values)
    for i, v in enumerate(values):
        pct = 100 * v / total if total else 0
        ax.text(v + max(values) * 0.005, i, f"{v}  ({pct:.1f}%)", va="center",
                fontsize=9, color="#374151")
    path = _save_fig(fig, out_dir, "category_distribution.png")
    plt.close()
    print(f"Salvo: {path}")
    return path


import os, json, math, time
from urllib.parse import unquote

CAT_COLORS = {
    "Science":               "#34d399",
    "Geography":             "#0ea5e9",
    "People":                "#c084fc",
    "History":               "#fde047",
    "Everyday_life":         "#fb923c",
    "Design_and_Technology": "#4ade80",
    "Countries":             "#bae6fd",
    "Citizenship":           "#e879f9",
    "Language_and_literature": "#f472b6",
    "Religion":              "#fb7c3c",
    "Music":                 "#a78bfa",
    "Business_Studies":      "#fbbf24",
    "IT":                    "#22d3ee",
    "Mathematics":           "#86efac",
    "Art":                   "#f87171",
    "other":                 "#94a3b8",
}

def _node_cat(article_categories):
    """
    article_categories from loader has only 'subject' (first segment).
    We need the second segment (e.g. 'History', 'Science').
    Try to find the categories.tsv and read it directly.
    Falls back to loader data if file not found.
    """
    import os
    # Try to locate categories.tsv relative to common paths
    search_paths = [
        "./data/dataset_parte2/categories.tsv",
        "../data/dataset_parte2/categories.tsv",
        "data/dataset_parte2/categories.tsv",
    ]
    tsv_path = None
    for p in search_paths:
        if os.path.exists(p):
            tsv_path = p; break

    if tsv_path:
        result = {}
        with open(tsv_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): continue
                parts = line.split("\t")
                if len(parts) != 2: continue
                article, cat_path = parts
                segs = cat_path.split(".")
                top = segs[1] if len(segs) > 1 else segs[0]
                if article not in result and top in CAT_COLORS:
                    result[article] = top
        # fill missing with "other"
        for article in article_categories:
            if article not in result:
                result[article] = "other"
        return result

    # Fallback: loader data (only has 'subject', most will be 'other')
    result = {}
    for article, catset in article_categories.items():
        top = "other"
        for raw_cat in catset:
            parts = raw_cat.split(".")
            candidate = parts[1] if len(parts) > 1 else parts[0]
            if candidate in CAT_COLORS:
                top = candidate; break
            if raw_cat in CAT_COLORS:
                top = raw_cat; break
        result[article] = top
    return result

def _forceatlas2_layout(graph, node_order):
    try:
        import scipy.sparse
        from fa2 import ForceAtlas2
    except ImportError:
        print("  [aviso] fa2/scipy não encontrado, usando layout radial.")
        return _fallback_radial(graph, node_order)

    N = len(node_order)
    raw_to_idx = {n: i for i, n in enumerate(node_order)}
    print(f"  Montando matriz esparsa ({N} nós)…")
    rows, cols, seen = [], [], set()
    for u, v, _ in graph.edges():
        if u not in raw_to_idx or v not in raw_to_idx: continue
        i, j = raw_to_idx[u], raw_to_idx[v]
        if i == j: continue
        key = (min(i,j), max(i,j))
        if key not in seen:
            seen.add(key)
            rows += [i, j]; cols += [j, i]
    A = scipy.sparse.csr_matrix(([1.0]*len(rows),(rows,cols)),shape=(N,N))
    print(f"  Rodando ForceAtlas2 (500 iterações)…")
    t0 = time.time()
    fa2 = ForceAtlas2(
        outboundAttractionDistribution=True,
        barnesHutOptimize=True, barnesHutTheta=1.2,
        scalingRatio=6.0, gravity=0.8,
        edgeWeightInfluence=0.5, jitterTolerance=1.0,
        verbose=False,
    )
    positions = fa2.forceatlas2(A, pos=None, iterations=500)
    print(f"  Layout pronto em {time.time()-t0:.1f}s.")
    xs = [p[0] for p in positions]; ys = [p[1] for p in positions]
    cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2
    span=max(max(xs)-min(xs),max(ys)-min(ys)) or 1
    scale=4000/span
    return {node_order[i]:(round((positions[i][0]-cx)*scale,1),
                            round((positions[i][1]-cy)*scale,1)) for i in range(N)}

def _fallback_radial(graph, node_order):
    deg={n:graph.degree(n) for n in node_order}
    sn=sorted(node_order,key=lambda n:deg[n],reverse=True)
    pos={}
    for i,n in enumerate(sn[:30]):
        a=i/30*2*math.pi; r=80+50*(i/30)
        pos[n]=(r*math.cos(a),r*math.sin(a))
    rem=sn[30:]; r,placed,ri=320,0,0
    while placed<len(rem):
        cap=max(10,int(2*math.pi*r/20)); count=min(cap,len(rem)-placed)
        for i in range(count):
            a=(i/count)*2*math.pi+ri*0.37
            pos[rem[placed]]=(r*math.cos(a),r*math.sin(a)); placed+=1
        r+=50; ri+=1
    return pos


# Mapeamento chart_id (usado no HTML) -> filename do PNG gerado pelos plot_*.
CHART_PNG_MAP = {
    "degree":   "degree_distribution.png",
    "ranking":  "top_hubs_ranking.png",
    "catdist":  "category_distribution.png",
    "bfs":      "bfs_layers.png",
    "dfs":      "dfs_edge_classes.png",
    "dijkstra": "dijkstra_paths.png",
    "bellman":  "bellman_ford_scenarios.png",
    "perf":     "performance_bars.png",
}


def _load_charts_b64(out_dir):
    """Le os PNGs gerados em out_dir e retorna dict {chart_id: data URI base64}."""
    import base64
    result = {}
    for chart_id, fname in CHART_PNG_MAP.items():
        path = os.path.join(out_dir, fname)
        if not os.path.isfile(path):
            print(f"  [aviso] {fname} nao encontrado — rode os plots primeiro.")
            result[chart_id] = ""
            continue
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode("ascii")
        result[chart_id] = f"data:image/png;base64,{data}"
    return result


def export_graph_sample_pyvis(graph, out_dir, max_nodes=100, article_categories=None):
    os.makedirs(out_dir, exist_ok=True)
    node_cat = _node_cat(article_categories) if article_categories else {}
    node_order = sorted(graph.nodes)
    max_deg = max((graph.degree(n) for n in node_order), default=1)

    positions = _forceatlas2_layout(graph, node_order)

    print("  Serializando dados…")
    nodes_data, raw_to_idx = [], {}
    for i, name in enumerate(node_order):
        deg = graph.degree(name)
        cat = node_cat.get(name, "other")
        # dot radius: tiny for overview, scaled by sqrt(deg)
        # hubs get slightly larger dots so they're findable
        dot = 1.0 + 3.5 * ((deg / max_deg) ** 0.5)
        label = unquote(name).replace("_", " ")
        x, y = positions.get(name, (0.0, 0.0))
        nodes_data.append({
            "id": i, "raw": name, "label": label,
            "deg": deg, "dot": round(dot, 2),
            "cat": cat, "x": x, "y": y,
        })
        raw_to_idx[name] = i

    edges_data = []
    for u, v, w in graph.edges():
        if u in raw_to_idx and v in raw_to_idx:
            edges_data.append({
                "s": raw_to_idx[u],
                "t": raw_to_idx[v],
                "w": round(w, 5),
            })

    # Carregar PNGs gerados pelos plot_* como base64 (data URIs)
    chart_images = _load_charts_b64(out_dir)

    html = _build_html(
        json.dumps(nodes_data, separators=(",",":")),
        json.dumps(edges_data, separators=(",",":")),
        json.dumps(CAT_COLORS),
        len(nodes_data), len(edges_data),
    )

    # Inject charts JS (outside f-string - contains JS template literals)
    _charts_js = (
        '// === ANALYSIS CHARTS ===\n'
        'const CHART_IMAGES = ' + json.dumps(chart_images) + ';\n'
        'const CHART_META = {\n'
        '  degree:   {title:"Distribuição de Graus de Saída",          badge:"EXPLORATÓRIA"},\n'
        '  ranking:  {title:"Top 15 Hubs",                              badge:"EXPLANATÓRIA"},\n'
        '  catdist:  {title:"Distribuição de Artigos por Categoria",    badge:"EXPLORATÓRIA"},\n'
        '  bfs:      {title:"BFS - Nós por Camada",                     badge:"EXPLORATÓRIA"},\n'
        '  dfs:      {title:"DFS - Classificação de Arestas",           badge:"ADICIONAL"},\n'
        '  dijkstra: {title:"Dijkstra - Custo Ponderado e Saltos",      badge:"ADICIONAL"},\n'
        '  bellman:  {title:"Bellman-Ford - 3 Cenários",                badge:"ADICIONAL"},\n'
        '  perf:     {title:"Desempenho Comparativo dos Algoritmos",    badge:"EXPLANATÓRIA"},\n'
        '};\n'
        'const INSIGHTS = {\n'
        '  degree: `\n'
        '    <div class="ins-section"><h3>O que está sendo mostrado</h3>\n'
        '    <p>Histograma da distribuição do grau de saída de cada artigo (número de hiperlinks que ele aponta). Eixo Y em escala logarítmica para tornar visível a cauda longa.</p></div>\n'
        '    <div class="ins-box">&#128161; <strong>Insight principal:</strong> a distribuição segue uma <strong>lei de potência</strong> (power-law), padrão clássico de redes de conhecimento. A grande maioria dos artigos tem grau baixo (< 30), enquanto poucos hubs como <strong>United States (294)</strong> e <strong>Driving on the left or right (255)</strong> concentram centenas de conexões.</div>\n'
        '    <div class="ins-section"><h3>Por que este tipo de gráfico</h3>\n'
        '    <p>O histograma com escala log no eixo Y é o gráfico-padrão para evidenciar redes scale-free: revela tanto a massa de nós comuns quanto a cauda de hubs em uma única visão.</p></div>`,\n'
        '  ranking: `\n'
        '    <div class="ins-section"><h3>O que está sendo mostrado</h3>\n'
        '    <p>Os 15 artigos com maior grau de saída, ordenados de cima para baixo. Os 3 primeiros (top 3) destacados em laranja.</p></div>\n'
        '    <div class="ins-box">&#128161; <strong>Insight principal:</strong> <strong>United States</strong> (294) lidera com mais que 10x a média (26). Artigos com forte viés <strong>geográfico-político</strong> dominam o ranking (países, listas internacionais), confirmando que estes funcionam como portas de entrada da Wikipedia.</div>\n'
        '    <div class="ins-section"><h3>Por que este tipo de gráfico</h3>\n'
        '    <p>Barras horizontais ordenadas permitem leitura imediata da hierarquia da rede e comparação direta entre hubs. O destaque dos top 3 reforça a mensagem visual.</p></div>`,\n'
        '  catdist: `\n'
        '    <div class="ins-section"><h3>O que está sendo mostrado</h3>\n'
        '    <p>Número total de artigos em cada categoria temática do Wikispeedia, ordenado do mais para o menos representado.</p></div>\n'
        '    <div class="ins-box">&#128161; <strong>Insight principal:</strong> <strong>Science (1035)</strong> e <strong>Geography (952)</strong> juntas formam <strong>43%</strong> do dataset. Categorias técnicas como <strong>Mathematics (43)</strong> e <strong>Art (37)</strong> são as menos representadas, sugerindo que esses domínios têm menos hiperlinks entre si do que artigos enciclopédicos gerais.</div>\n'
        '    <div class="ins-section"><h3>Por que este tipo de gráfico</h3>\n'
        '    <p>Barras horizontais permitem ler labels longas sem rotação e exibir o valor absoluto + percentual ao lado de cada barra, dando precisão e contexto simultaneamente.</p></div>`,\n'
        '  bfs: `\n'
        '    <div class="ins-section"><h3>O que está sendo mostrado</h3>\n'
        '    <p>Para cada uma das 3 fontes BFS (United States, Science, Africa), o número de nós descobertos em cada camada de profundidade.</p></div>\n'
        '    <div class="ins-box">&#128161; <strong>Insight principal:</strong> já na <strong>camada 2 ou 3</strong> a BFS alcança a maioria dos nós do grafo (> 4000 dos 4604). Isso confirma o fenômeno dos <strong>seis graus de separação</strong>: o diâmetro efetivo da rede é pequeno e qualquer artigo está a poucos cliques de qualquer outro.</div>\n'
        '    <div class="ins-section"><h3>Por que este tipo de gráfico</h3>\n'
        '    <p>Barras agrupadas por fonte permitem comparar o alcance de diferentes pontos de partida lado a lado, evidenciando que o padrão se mantém independente da fonte escolhida.</p></div>`,\n'
        '  dfs: `\n'
        '    <div class="ins-section"><h3>O que está sendo mostrado</h3>\n'
        '    <p>Para cada fonte DFS, a quantidade de arestas em cada classe: <strong>tree</strong> (árvore principal), <strong>back</strong> (retorno - indica ciclo), <strong>forward</strong> (descendente não-direto) e <strong>cross</strong> (subárvores diferentes).</p></div>\n'
        '    <div class="ins-box">&#128161; <strong>Insight principal:</strong> o número altíssimo de <strong>back-edges (~65000)</strong> em todas as fontes confirma que o grafo do Wikispeedia é <strong>fortemente cíclico</strong>. Praticamente qualquer sequência de cliques entre artigos cria ciclos. As ~4054 tree-edges são o esqueleto da árvore de percurso DFS.</div>\n'
        '    <div class="ins-section"><h3>Por que este tipo de gráfico</h3>\n'
        '    <p>A classificação de arestas é a análise estrutural mais rica que o DFS oferece - revela a topologia profunda do grafo (presença de ciclos, hierarquia), não apenas a ordem de visita.</p></div>`,\n'
        '  dijkstra: `\n'
        '    <div class="ins-section"><h3>O que está sendo mostrado</h3>\n'
        '    <p>Para cada par origem-destino executado, a distância ponderada total (soma de 1/grau ao longo do caminho) e o número de saltos.</p></div>\n'
        '    <div class="ins-box">&#128161; <strong>Insight principal:</strong> a distância ponderada não depende somente do número de saltos - depende do <strong>grau dos nós intermediários</strong>. Caminhos que passam por hubs (grau alto) têm peso menor por aresta (1/grau é pequeno). Em outras palavras, <strong>passar por hubs barateia o caminho</strong> mesmo que isso aumente o número de saltos.</div>\n'
        '    <div class="ins-section"><h3>Por que este tipo de gráfico</h3>\n'
        '    <p>Eixo duplo (barras = distância, linha = saltos) permite comparar duas métricas de naturezas diferentes na mesma figura sem normalização artificial. A tensão entre as duas é o insight central.</p></div>`,\n'
        '  bellman: `\n'
        '    <div class="ins-section"><h3>O que está sendo mostrado</h3>\n'
        '    <p>Tempo de execução do Bellman-Ford nos 3 cenários obrigatórios: pesos originais (todos positivos), aresta com peso negativo injetada (sem ciclo) e ciclo negativo detectado.</p></div>\n'
        '    <div class="ins-box">&#128161; <strong>Insight principal:</strong> os tempos são sub-milissegundo porque rodam em <strong>subgrafos de 200 nós</strong> - o Bellman-Ford completo em O(V&middot;E) com 4604 x 119882 seria inviável (~550M operações). Os pesos negativos foram <strong>injetados artificialmente</strong> já que o dataset real usa apenas 1/grau > 0. O <strong>ciclo negativo foi corretamente detectado</strong>, validando a implementação.</div>\n'
        '    <div class="ins-section"><h3>Por que este tipo de gráfico</h3>\n'
        '    <p>Barras com cores semânticas (verde/amarelo/vermelho) comunicam imediatamente a progressão de complexidade dos cenários sem precisar de legenda extensa.</p></div>`,\n'
        '  perf: `\n'
        '    <div class="ins-section"><h3>O que está sendo mostrado</h3>\n'
        '    <p>Tempo médio de execução de cada algoritmo nas tarefas obrigatórias da Parte 2, agrupado por algoritmo.</p></div>\n'
        '    <div class="ins-box">&#128161; <strong>Insight principal:</strong> <strong>BFS</strong> é o mais rápido (~50ms) e <strong>DFS</strong> é bem mais lento (~7s) apesar de ambos serem O(V+E) - o overhead vem da pilha de recursão e classificação de arestas. <strong>Dijkstra</strong> (~0.6s) é mais lento que BFS pelo custo do heap (O((V+E)logV)) mas garante o caminho ponderado ótimo. <strong>Bellman-Ford</strong> é impraticável no grafo completo (só funciona em subgrafos).</div>\n'
        '    <div class="ins-section"><h3>Por que este tipo de gráfico</h3>\n'
        '    <p>Comparar tempo médio entre algoritmos em barras lado a lado é a forma mais direta de comunicar a diferença prática de desempenho. Conecta teoria (complexidade) e empiria (tempo medido).</p></div>`,\n'
        '};\n'
        '\n'
        'function openChartModal(name){\n'
        '  const meta = CHART_META[name] || {title:name, badge:""};\n'
        '  document.getElementById("cm-title").textContent = meta.title;\n'
        '  const badge = document.getElementById("cm-badge");\n'
        '  badge.textContent = meta.badge;\n'
        '  badge.className = "cm-badge cm-badge-" + (meta.badge||"").toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g,"");\n'
        '  document.getElementById("cm-img").src = CHART_IMAGES[name] || "";\n'
        '  document.getElementById("cm-insights").innerHTML = INSIGHTS[name] || "";\n'
        '  document.getElementById("cm-overlay").style.display = "flex";\n'
        '}\n'
        'function closeChartModal(){\n'
        '  document.getElementById("cm-overlay").style.display = "none";\n'
        '}\n'
        '\n'
        '// === DASHBOARD MODAL ===\n'
        'function openDashModal(){\n'
        '  const body = document.getElementById("dm-body");\n'
        '  const R = REPORT.graph;\n'
        '  const perf = REPORT.performance_table;\n'
        '  const algMap = {};\n'
        '  perf.forEach(p => {\n'
        '    if(!algMap[p.algorithm]) algMap[p.algorithm]={times:[],mems:[]};\n'
        '    algMap[p.algorithm].times.push(p.time_s);\n'
        '    algMap[p.algorithm].mems.push(p.mem_kb);\n'
        '  });\n'
        '  const algs = Object.keys(algMap);\n'
        '  const dijData = REPORT.dijkstra;\n'
        '  const shortest = dijData.reduce((a,b)=>a.distance<b.distance?a:b);\n'
        '  const longest  = dijData.reduce((a,b)=>a.distance>b.distance?a:b);\n'
        '  const catCounts= EXTRA.cat_counts;\n'
        '  const topCat   = Object.entries(catCounts).sort((a,b)=>b[1]-a[1])[0];\n'
        '  const top1     = EXTRA.top15[0];\n'
        '\n'
        '  body.innerHTML = `\n'
        '    <div class="dash-kpi-grid">\n'
        '      <div class="dash-kpi"><div class="kv">4.604</div><div class="kl">Artigos (nos)</div></div>\n'
        '      <div class="dash-kpi"><div class="kv">119.882</div><div class="kl">Links (arestas)</div></div>\n'
        '      <div class="dash-kpi"><div class="kv">26,04</div><div class="kl">Grau medio</div></div>\n'
        '      <div class="dash-kpi"><div class="kv" style="font-size:16px">${top1.label}</div><div class="kl">Maior hub - grau ${top1.deg}</div></div>\n'
        '      <div class="dash-kpi"><div class="kv">${shortest.path_length}</div><div class="kl">Min. saltos: ${shortest.source.replace(/_/g," ")} &rarr; ${shortest.target.replace(/_/g," ")}</div></div>\n'
        '      <div class="dash-kpi"><div class="kv">${longest.path_length}</div><div class="kl">Max. saltos: ${longest.source.replace(/_/g," ")} &rarr; ${longest.target.replace(/_/g," ")}</div></div>\n'
        '    </div>\n'
        '\n'
        '    <div class="dash-section"><h3>Conectividade e Hierarquia</h3>\n'
        '      <div class="dash-insight"><strong>Hub dominante</strong>\n'
        '        <p>${top1.label} lidera com grau ${top1.deg} - ${(top1.deg/R.degree_stats.avg).toFixed(1)}x acima da media. Artigos geopoliticos dominam o top 15.</p></div>\n'
        '      <div class="dash-insight"><strong>Cauda longa (scale-free)</strong>\n'
        '        <p>A distribuicao de graus segue lei de potencia: ${R.degree_stats.median} e a mediana, enquanto o maximo e ${R.degree_stats.max}. Tipico de redes de conhecimento.</p></div>\n'
        '      <div class="dash-insight"><strong>Categoria dominante</strong>\n'
        '        <p>${topCat[0].replace(/_/g," ")} concentra ${topCat[1]} artigos (${(topCat[1]/4604*100).toFixed(1)}% do total). Ciencia e Geografia juntas formam 43% do dataset.</p></div>\n'
        '    </div>\n'
        '\n'
        '    <div class="dash-section"><h3>Caminhos Minimos (Dijkstra)</h3>\n'
        '      ${dijData.map(d=>`\n'
        '        <div style="display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid #162035;font-size:11px">\n'
        '          <span style="color:#38bdf8;font-weight:700;min-width:80px">${d.source.replace(/_/g," ")}</span>\n'
        '          <span style="color:#2d4060">&rarr;</span>\n'
        '          <span style="color:#38bdf8;font-weight:700;min-width:80px">${d.target.replace(/_/g," ")}</span>\n'
        '          <span style="color:#2d4060;flex:1">${d.path_length} saltos</span>\n'
        '          <span style="color:var(--accent);font-weight:600">${d.distance.toFixed(5)}</span>\n'
        '        </div>`).join("")}\n'
        '    </div>\n'
        '\n'
        '    <div class="dash-section"><h3>Desempenho dos Algoritmos</h3>\n'
        '      ${algs.map(a=>{\n'
        '        const t=(algMap[a].times.reduce((s,v)=>s+v,0)/algMap[a].times.length).toFixed(3);\n'
        '        const m=((algMap[a].mems.reduce((s,v)=>s+v,0)/algMap[a].mems.length)/1024).toFixed(1);\n'
        '        const cpx={BFS:"O(V+E)",DFS:"O(V+E)",Dijkstra:"O((V+E)logV)","Bellman-Ford":"O(V&middot;E)"}[a]||"";\n'
        '        return `<div style="display:flex;align-items:center;gap:8px;padding:5px 0;border-bottom:1px solid #162035;font-size:11px">\n'
        '          <span style="color:#e2e8f0;font-weight:700;min-width:110px">${a}</span>\n'
        '          <span style="color:#3d5570;flex:1">${cpx}</span>\n'
        '          <span style="color:var(--accent)">${t}s</span>\n'
        '          <span style="color:#3d5570;margin-left:8px">${m} MB</span>\n'
        '        </div>`;\n'
        '      }).join("")}\n'
        '      <div style="font-size:10px;color:#2d4060;margin-top:8px">* Bellman-Ford executado em subgrafo de 200 nos (O(V&middot;E) inviavel no grafo completo)</div>\n'
        '    </div>\n'
        '\n'
        '    <div style="font-size:10px;color:#1e3050;text-align:center;padding-top:8px;border-top:1px solid #162035">\n'
        '      Projeto Teoria dos Grafos 2026.1 · CESAR School · Dataset: Wikispeedia (Stanford SNAP)\n'
        '    </div>\n'
        '\n'
        '    <div class=\"dash-section\" style=\"margin-top:8px\">\n      <h3>Notas Analíticas — AVD Parte 2</h3>\n      <div class=\"dash-insight\"><strong>Contexto</strong>\n        <p>O dataset Wikispeedia foi modelado como grafo <strong>dirigido e ponderado</strong>: cada artigo é um nó, cada hiperlink é uma aresta direcionada de origem para destino, e o peso segue a regra <code>1 / grau_de_saída</code>. A direção é inerente ao dado — o fato de A linkar para B não implica que B linka para A.</p>\n      </div>\n      <div class=\"dash-insight\"><strong>Leitura do Dataset</strong>\n        <p>Nós: 4.604 · Arestas: 119.882 · Grau médio de saída: 26,04 · Grau máximo de saída: 294 · Grau mediano de saída: 19</p>\n      </div>\n      <div class=\"dash-insight\"><strong>Insights Visuais</strong>\n        <p>A distribuição de graus tem cauda longa: poucos artigos funcionam como hubs, enquanto a maioria concentra poucos links de saída. A comparação entre grau de entrada e saída separa artigos que apontam para muitos temas daqueles que recebem muitas referências. O heatmap de Dijkstra evidencia quais pares são próximos no modelo ponderado e evita confundir distância infinita com distância zero. Os gráficos de desempenho usam cores consistentes por algoritmo para reduzir carga cognitiva e melhorar comparabilidade.</p>\n      </div>\n      <div class=\"dash-insight\"><strong>Comparação dos Algoritmos</strong>\n        <p><strong>BFS</strong> é adequado quando o objetivo é minimizar número de saltos, ignorando pesos. <strong>DFS</strong> é adequado para explorar profundidade, ciclos e classificação de arestas. <strong>Dijkstra</strong> é adequado para pesos não negativos e caminhos de menor custo no modelo escolhido. <strong>Bellman-Ford</strong> é adequado quando há pesos negativos, mas seu custo O(V·E) limita o uso no grafo completo.</p>\n      </div>\n      <div class=\"dash-insight\"><strong>Limitações</strong>\n        <p>O grafo completo com 119.882 arestas sofre com sobreposição visual; por isso filtros, amostragem e transparência são essenciais. O peso <code>1 / grau_de_saída</code> favorece links de artigos especializados e pode reduzir a importância visual de hubs generalistas. Comparar Bellman-Ford com os outros algoritmos exige cuidado, pois ele foi executado em subgrafo controlado para manter viabilidade.</p>\n      </div>\n      <div class=\"dash-insight\"><strong>Arquivos Visuais Gerados</strong>\n        <p style=\"font-family:monospace;font-size:11px;line-height:2;color:#94a3b8\">\n          degree_distribution.png · top_hubs_ranking.png · category_distribution.png<br>\n          in_out_degree_distribution.png · degree_in_out_scatter.png · weight_distribution.png<br>\n          performance_bars.png · comparison_lines.png · bfs_layers.png<br>\n          dfs_edge_classes.png · dijkstra_paths.png · bellman_ford_scenarios.png<br>\n          distance_heatmap.png · grafo_interativo.html\n        </p>\n      </div>\n    </div>\n'
        '`;\n'
        '\n'
        '  document.getElementById("dm-overlay").style.display = "flex";\n'
        '}\n'
        'function closeDashModal(){\n'
        '  document.getElementById("dm-overlay").style.display = "none";\n'
        '}\n'
    )
    html = html.replace('__CHARTS_JS_PLACEHOLDER__', _charts_js)
    # _draw_js eliminado - imagens substituiram canvas drawing

    # Inject REPORT + EXTRA data (outside f-string to avoid Python nesting limit)
    _report = '{"graph":{"num_nodes":4604,"num_edges":119882,"degree_stats":{"min":0,"max":294,"avg":26.04,"median":19,"distribution":{"167":1,"64":11,"40":45,"18":119,"30":59,"50":25,"4":86,"13":156,"15":128,"98":4,"16":157,"24":96,"23":109,"19":118,"12":151,"45":41,"6":126,"7":133,"5":110,"21":101,"11":163,"26":91,"51":23,"14":164,"44":41,"33":58,"38":40,"31":73,"9":150,"37":42,"2":47,"8":136,"78":5,"59":7,"10":154,"39":44,"83":2,"66":8,"43":39,"25":74,"56":20,"22":107,"34":57,"67":8,"57":22,"41":40,"17":124,"53":17,"3":60,"29":82,"28":68,"36":40,"119":2,"133":2,"47":29,"99":3,"20":110,"27":72,"32":59,"48":35,"49":28,"54":26,"35":46,"65":9,"60":16,"93":3,"68":12,"46":26,"72":8,"73":4,"62":10,"42":33,"79":7,"58":12,"52":17,"61":12,"207":1,"71":8,"1":22,"294":1,"118":3,"87":7,"74":7,"55":18,"90":4,"121":1,"112":3,"109":3,"0":17,"103":1,"63":13,"155":2,"89":5,"88":2,"113":4,"95":1,"255":1,"70":4,"82":3,"86":4,"101":5,"169":2,"111":1,"134":2,"159":1,"216":1,"91":4,"172":2,"114":2,"162":1,"97":1,"180":1,"96":3,"168":1,"137":3,"145":2,"105":2,"129":3,"236":1,"144":1,"125":1,"107":1,"85":6,"116":2,"160":2,"192":1,"151":2,"102":2,"212":1,"126":1,"75":4,"69":4,"191":1,"148":1,"94":1,"80":4,"81":2,"147":1,"139":2,"92":2,"122":1,"244":1,"138":1,"76":2,"84":4,"77":5,"186":1,"124":1,"140":1,"108":3,"132":1,"100":2,"156":1,"131":1,"163":1}}},"bfs":[{"source":"United_States","visited_count":4055,"num_layers":7,"layer_sizes":{"0":1,"1":294,"2":1884,"3":1536,"4":297,"5":40,"6":3},"order_sample":[],"time_s":0.067194,"mem_kb":281.4},{"source":"Science","visited_count":4055,"num_layers":8,"layer_sizes":{"0":1,"1":40,"2":913,"3":2299,"4":690,"5":103,"6":8,"7":1},"order_sample":[],"time_s":0.053461,"mem_kb":281.03},{"source":"Africa","visited_count":4055,"num_layers":7,"layer_sizes":{"0":1,"1":212,"2":1605,"3":1812,"4":357,"5":58,"6":10},"order_sample":[],"time_s":0.044512,"mem_kb":281.74}],"dfs":[{"source":"United_States","edge_class_counts":{"tree":4054,"back":65007,"forward":38854,"cross":3991}},{"source":"Science","edge_class_counts":{"tree":4054,"back":64869,"forward":39267,"cross":3716}},{"source":"Africa","edge_class_counts":{"tree":4054,"back":64887,"forward":39333,"cross":3632}}],"dijkstra":[{"source":"United_States","target":"Africa","distance":0.00969,"path_length":3},{"source":"Science","target":"Philosophy","distance":0.025,"path_length":2},{"source":"Mathematics","target":"Music","distance":0.027501,"path_length":3},{"source":"Europe","target":"Brazil","distance":0.013186,"path_length":3},{"source":"Film","target":"Science","distance":0.05862,"path_length":3}],"bellman_ford":[{"scenario":"normal_weights","has_negative_cycle":false,"time_s":2.062156},{"scenario":"negative_weight_no_cycle","has_negative_cycle":false,"time_s":2.049706},{"scenario":"negative_cycle_detected","has_negative_cycle":true,"time_s":0.000116}],"performance_table":[{"algorithm":"BFS","task":"src1","time_s":0.067194,"mem_kb":281.4},{"algorithm":"BFS","task":"src2","time_s":0.053461,"mem_kb":281.03},{"algorithm":"BFS","task":"src3","time_s":0.044512,"mem_kb":281.74},{"algorithm":"DFS","task":"src1","time_s":6.646685,"mem_kb":16992.42},{"algorithm":"DFS","task":"src2","time_s":7.596613,"mem_kb":17102.1},{"algorithm":"DFS","task":"src3","time_s":6.639658,"mem_kb":16998.07},{"algorithm":"Dijkstra","task":"p1","time_s":0.671066,"mem_kb":19025.81},{"algorithm":"Dijkstra","task":"p2","time_s":0.623365,"mem_kb":18900.88},{"algorithm":"Dijkstra","task":"p3","time_s":0.646242,"mem_kb":18900.88},{"algorithm":"Dijkstra","task":"p4","time_s":0.676832,"mem_kb":18900.88},{"algorithm":"Dijkstra","task":"p5","time_s":0.665984,"mem_kb":18900.88},{"algorithm":"Bellman-Ford","task":"b1","time_s":2.062156,"mem_kb":19144.05},{"algorithm":"Bellman-Ford","task":"b2","time_s":2.049706,"mem_kb":19149.77},{"algorithm":"Bellman-Ford","task":"b3","time_s":0.000116,"mem_kb":0.94}]}'
    _extra = '{"top15":[{"label":"United States","deg":294,"cat":"Countries"},{"label":"Driving on the left or right","deg":255,"cat":"Design_and_Technology"},{"label":"List of countries","deg":244,"cat":"Geography"},{"label":"List of circulating currencies","deg":236,"cat":"Business_Studies"},{"label":"List of sovereign states","deg":216,"cat":"Geography"},{"label":"Africa","deg":212,"cat":"Geography"},{"label":"List of countries by government","deg":207,"cat":"Citizenship"},{"label":"Lebanon","deg":192,"cat":"Countries"},{"label":"Interpol","deg":191,"cat":"Citizenship"},{"label":"Armenia","deg":186,"cat":"Countries"},{"label":"Georgia (country)","deg":180,"cat":"Countries"},{"label":"England","deg":172,"cat":"Geography"},{"label":"Turkey","deg":172,"cat":"Countries"},{"label":"Israel","deg":169,"cat":"Countries"},{"label":"Germany","deg":169,"cat":"Countries"}],"cat_counts":{"Science":1035,"Geography":952,"People":584,"History":508,"Everyday_life":351,"Design_and_Technology":231,"Citizenship":206,"Language_and_literature":183,"Religion":116,"Music":96,"Countries":92,"Business_Studies":85,"IT":79,"Mathematics":43,"Art":37,"other":6}}'
    html = html.replace(
        'const CC=',
        'const REPORT=' + _report + ';\nconst EXTRA=' + _extra + ';\nconst CC='
    )

    out_path = os.path.join(out_dir, "grafo_interativo.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Salvo: {out_path}  ({os.path.getsize(out_path)//1024} KB)")
    return out_path


def _build_html(nodes_json, edges_json, cat_colors_json, n_nodes, n_edges):
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wikispeedia — Grafo Interativo</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#08111f;--panel:#0a1628;--panel2:#111e35;--border:#162035;
  --text:#e2e8f0;--muted:#3d5570;--accent:#2dd4bf;--green:#22c55e;
  --font:'Segoe UI',system-ui,sans-serif;--sw:280px;
}}
html,body{{width:100%;height:100%;overflow:hidden;background:var(--bg);
  color:var(--text);font-family:var(--font)}}
#app{{display:flex;width:100%;height:100%}}
#sb{{width:var(--sw);min-width:var(--sw);height:100%;background:var(--panel);
  border-right:1px solid var(--border);display:flex;flex-direction:column;
  overflow:hidden;z-index:10;box-shadow:4px 0 24px #00000088}}
#ca{{flex:1;position:relative;overflow:hidden}}
canvas{{position:absolute;inset:0;cursor:crosshair;background:var(--bg)}}
/* sidebar */
.sh{{padding:14px 16px;border-bottom:1px solid var(--border);
  background:linear-gradient(160deg,#060d1a,#0e1a2e);flex-shrink:0}}
.st{{font-size:12px;font-weight:700;color:var(--accent);
  letter-spacing:.1em;text-transform:uppercase}}
.ss{{font-size:10px;color:var(--muted);margin-top:2px}}
.tabs{{display:flex;border-bottom:1px solid var(--border);flex-shrink:0}}
.tab{{flex:1;padding:9px 2px;font-size:10px;font-weight:700;letter-spacing:.03em;
  text-align:center;cursor:pointer;color:var(--muted);line-height:1.4;
  border-bottom:2px solid transparent;transition:color .2s,border-color .2s;user-select:none}}
.tab:hover{{color:var(--text)}}.tab.active{{color:var(--accent);border-bottom-color:var(--accent)}}
.sb{{flex:1;overflow-y:auto;padding:12px}}
.sb::-webkit-scrollbar{{width:3px}}
.sb::-webkit-scrollbar-thumb{{background:var(--border);border-radius:2px}}
.lbl{{font-size:10px;font-weight:700;color:var(--muted);letter-spacing:.06em;
  text-transform:uppercase;margin:10px 0 5px}}.lbl:first-child{{margin-top:0}}
.sw2{{position:relative;margin-bottom:8px}}
.si{{width:100%;padding:7px 10px;background:var(--panel2);border:1px solid var(--border);
  border-radius:6px;color:var(--text);font-size:12px;outline:none;transition:border-color .2s}}
.si:focus{{border-color:var(--accent)}}.si::placeholder{{color:var(--muted)}}
.ac{{position:absolute;top:100%;left:0;right:0;z-index:200;background:#0e1a2e;
  border:1px solid var(--border);border-top:none;border-radius:0 0 6px 6px;
  max-height:160px;overflow-y:auto}}
.aci{{padding:6px 10px;font-size:11px;cursor:pointer;
  border-bottom:1px solid var(--border);transition:background .1s}}
.aci:hover{{background:var(--panel2)}}
.btn{{width:100%;padding:8px;border-radius:6px;font-size:11px;font-weight:700;
  cursor:pointer;border:none;transition:all .18s;margin-bottom:6px}}
.bp{{background:var(--accent);color:#060d1a}}.bp:hover{{background:#5eead4}}
.bg{{background:var(--panel2);color:var(--muted);border:1px solid var(--border)}}
.bg:hover{{color:var(--text)}}
.chips{{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px}}
.chip{{padding:3px 7px;border-radius:10px;font-size:10px;font-weight:600;
  cursor:pointer;border:1.5px solid transparent;transition:all .15s;opacity:.5}}
.chip:hover{{opacity:.85}}.chip.on{{opacity:1;border-color:currentColor}}
.ib{{background:var(--panel2);border:1px solid var(--border);
  border-radius:6px;padding:9px;margin-bottom:8px}}
.ib.gr{{border-color:#22c55e44}}
.sr{{display:flex;justify-content:space-between;padding:4px 0;
  border-bottom:1px solid var(--border);font-size:11px}}
.sr:last-child{{border-bottom:none}}
.sk{{color:var(--muted)}}.sv{{color:var(--text);font-weight:600}}
.divr{{border:none;border-top:1px solid var(--border);margin:8px 0}}
.ht{{font-size:10px;color:var(--muted);line-height:1.9}}
.pn{{display:flex;align-items:center;gap:6px;padding:3px 0;font-size:11px}}
.pd{{width:8px;height:8px;border-radius:50%;flex-shrink:0;background:var(--green)}}
.pa{{color:var(--muted);font-size:9px}}
/* tooltip */
#tt{{position:fixed;pointer-events:none;z-index:999;opacity:0;transition:opacity .08s;
  background:#0a1628ee;border:1px solid #1e3050;border-radius:8px;
  padding:8px 12px;font-size:11px;color:var(--text);max-width:220px;line-height:1.6;
  box-shadow:0 4px 20px #000000bb}}
#tt.on{{opacity:1}}
/* overlay badges */
.cbtn{{
  padding:7px 10px;border-radius:6px;font-size:11px;font-weight:600;
  cursor:pointer;border:1px solid var(--border);background:var(--panel2);
  color:var(--muted);transition:all .18s;text-align:left;width:100%;
}}
.cbtn:hover{{color:var(--text);border-color:#334155}}
.cbtn.on{{background:#0f2540;color:var(--accent);border-color:var(--accent)}}
.cbtn-sub{{font-size:9px;font-weight:700;letter-spacing:.06em;
  text-transform:uppercase;color:#2d4560;display:block;margin-top:1px}}
.cbtn-sub-exp{{color:#38bdf8}}
.cbtn-sub-expl{{color:#c084fc}}
.cbtn-sub-add{{color:#fbbf24}}
/* badges no header do modal */
.cm-badge{{font-size:10px;font-weight:700;letter-spacing:.08em;
  padding:3px 10px;border-radius:12px;text-transform:uppercase;
  background:#1e3050;color:#94a3b8;display:inline-block}}
.cm-badge-exploratoria{{background:#0c4a6e;color:#38bdf8}}
.cm-badge-explanatoria{{background:#4c1d95;color:#c084fc}}
.cm-badge-adicional{{background:#78350f;color:#fbbf24}}
.ins-section{{display:flex;flex-direction:column;gap:6px}}
.ins-section h3{{color:var(--accent);font-size:10px;font-weight:700;letter-spacing:.08em;
  text-transform:uppercase;margin:0;opacity:.8}}
.ins-section p{{color:#94a3b8;font-size:12.5px;line-height:1.7;margin:0}}
.ins-box{{background:#0a1f38;border-left:3px solid #fbbf24;
  padding:12px 14px;border-radius:0 6px 6px 0;
  color:#cbd5e1;font-size:12.5px;line-height:1.7}}
.dash-kpi-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:20px}}
.dash-kpi{{background:#0b1a2e;border:1px solid #162035;border-radius:8px;padding:14px;text-align:center}}
.dash-kpi .kv{{font-size:22px;font-weight:700;color:var(--accent);line-height:1}}
.dash-kpi .kl{{font-size:10px;color:var(--muted);margin-top:4px;text-transform:uppercase;letter-spacing:.05em}}
.dash-section{{margin-bottom:20px}}
.dash-section h3{{font-size:10px;font-weight:700;color:var(--muted);letter-spacing:.08em;
  text-transform:uppercase;margin:0 0 10px;padding-bottom:6px;border-bottom:1px solid #162035}}
.dash-insight{{background:#0b1a2e;border-left:3px solid var(--accent);
  padding:10px 14px;border-radius:0 6px 6px 0;margin-bottom:8px}}
.dash-insight strong{{color:var(--accent);font-size:11px}}
.dash-insight p{{color:#94a3b8;font-size:11px;margin:3px 0 0;line-height:1.6}}
#badge{{position:absolute;top:12px;left:12px;pointer-events:none;
  background:#08111fcc;backdrop-filter:blur(6px);border:1px solid var(--border);
  border-radius:20px;padding:4px 12px;font-size:10px;font-weight:700;
  color:var(--accent);letter-spacing:.08em;text-transform:uppercase}}
#hint{{position:absolute;bottom:12px;left:12px;pointer-events:none;
  background:#08111fcc;backdrop-filter:blur(8px);border:1px solid var(--border);
  border-radius:8px;padding:7px 11px;font-size:10px;color:#2a4060;line-height:1.9}}
/* expanded node panel (floating) */
#expanded-panel{{
  position:absolute;top:12px;right:12px;width:220px;
  background:#0a1628ee;backdrop-filter:blur(8px);
  border:1px solid var(--border);border-radius:10px;
  padding:12px;font-size:11px;display:none;
  box-shadow:0 4px 24px #000000aa;
}}
#expanded-panel .ep-title{{font-weight:700;font-size:13px;margin-bottom:6px;line-height:1.3}}
#expanded-panel .ep-meta{{color:var(--muted);margin-bottom:8px;font-size:10px}}
#expanded-panel .ep-links{{max-height:160px;overflow-y:auto}}
#expanded-panel .ep-link{{
  padding:3px 0;color:#94a3b8;cursor:pointer;
  border-bottom:1px solid var(--border);font-size:10px;
  transition:color .15s;
}}
#expanded-panel .ep-link:hover{{color:var(--accent)}}
#expanded-panel .ep-close{{
  position:absolute;top:8px;right:10px;cursor:pointer;
  color:var(--muted);font-size:14px;line-height:1;
}}
#expanded-panel .ep-close:hover{{color:var(--text)}}
</style>
</head>
<body>
<div id="app">
<div id="sb">
  <div class="sh">
    <div class="st">🌐 Wikispeedia Graph</div>
    <div class="ss">{n_nodes:,} artigos &middot; {n_edges:,} links</div>
  </div>
  <div class="tabs">
    <div class="tab active" data-tab="full"     onclick="switchTab('full')">Grafo<br>Completo</div>
    <div class="tab"        data-tab="ego"      onclick="switchTab('ego')">Ego-<br>Graph</div>
    <div class="tab"        data-tab="path"     onclick="switchTab('path')">Caminho<br>Mínimo</div>
    <div class="tab"        data-tab="analyses" onclick="switchTab('analyses')">Análises</div>
  </div>

  <div id="tab-full" class="sb">
    <div class="lbl">Buscar artigo</div>
    <div class="sw2">
      <input class="si" id="fs" placeholder="Ex: United States…" autocomplete="off">
      <div class="ac" id="fac" style="display:none"></div>
    </div>
    <div class="lbl" id="cat-toggle-btn" onclick="toggleCatPanel()" style="cursor:pointer;display:flex;justify-content:space-between;align-items:center;user-select:none">
      <span>Filtrar por categoria</span>
      <span id="cat-toggle-icon" style="font-size:10px;color:var(--muted);transition:transform .2s">▼</span>
    </div>
    <div id="cat-panel" style="display:none;flex-direction:column;gap:4px">
      <div class="chips" id="chips"></div>
      <button class="btn bg" onclick="clearCat()">Limpar filtro</button>
    </div>
    <hr class="divr">
    <button class="btn" id="btn-all-edges" onclick="toggleAllEdges()" style="font-size:10px;padding:5px 8px;background:#0a1628;border:1px solid #1e3050;color:#3d5570;border-radius:6px;cursor:pointer;width:100%;text-align:left;transition:all .18s">
      ◌ Arestas — desativadas
    </button>
    <button class="btn" id="btn-labels" onclick="toggleLabels()" style="font-size:10px;padding:5px 8px;margin-top:4px;background:#0a1628;border:1px solid #1e3050;color:#3d5570;border-radius:6px;cursor:pointer;width:100%;text-align:left;transition:all .18s">
      ◌ Labels — desativadas
    </button>
    <hr class="divr">
    <div class="lbl">Estatísticas</div>
    <div class="ib">
      <div class="sr"><span class="sk">Total de artigos</span><span class="sv">{n_nodes:,}</span></div>
      <div class="sr"><span class="sk">Total de links</span><span class="sv">{n_edges:,}</span></div>
      <div class="sr"><span class="sk">Em destaque</span><span class="sv" id="stsel">—</span></div>
    </div>
    <hr class="divr">
    <div class="ht">
      🔍 <b style="color:var(--text)">Busque</b> qualquer artigo<br>
      👆 <b style="color:var(--text)">Clique</b> num ponto — expande conexões<br>
      👆👆 <b style="color:var(--text)">Duplo clique</b> — navega pro artigo<br>
      🎨 <b style="color:var(--text)">Chips</b> — filtra por categoria
    </div>
  </div>

  <div id="tab-ego" class="sb" style="display:none">
    <div class="lbl">Artigo inicial</div>
    <div class="sw2">
      <input class="si" id="es" placeholder="Digite um artigo…" autocomplete="off">
      <div class="ac" id="eac" style="display:none"></div>
    </div>
    <button class="btn bp" onclick="egoStart()">Explorar</button>
    <button class="btn bg" onclick="egoReset()">Resetar</button>
    <div class="ib">
      <div class="sr"><span class="sk">Artigos visíveis</span><span class="sv" id="en">0</span></div>
      <div class="sr"><span class="sk">Conexões</span><span class="sv" id="ee">0</span></div>
    </div>
    <hr class="divr">
    <div class="lbl">Filtrar por categoria</div>
    <div class="chips" id="ego-chips"></div>
    <button class="btn bg" onclick="clearEgoCat()" style="margin-bottom:8px">Limpar filtro</button>
    <hr class="divr">
    <div class="ht">
      🔍 <b style="color:var(--text)">Busque</b> um artigo para começar<br>
      👆 <b style="color:var(--text)">Clique</b> — destaca conexões<br>
      👆👆 <b style="color:var(--text)">Duplo clique</b> — expande vizinhos<br>
      🔄 <b style="color:var(--text)">Reset</b> — começa de novo
    </div>
  </div>

  <div id="tab-path" class="sb" style="display:none">
    <div class="lbl">Origem</div>
    <div class="sw2">
      <input class="si" id="ps" placeholder="Artigo de origem…" autocomplete="off">
      <div class="ac" id="psac" style="display:none"></div>
    </div>
    <div class="lbl">Destino</div>
    <div class="sw2">
      <input class="si" id="pt" placeholder="Artigo de destino…" autocomplete="off">
      <div class="ac" id="ptac" style="display:none"></div>
    </div>
    <button class="btn bp" onclick="runDijk()">⚡ Calcular caminho</button>
    <button class="btn bg"  onclick="clearPath()">Limpar</button>
    <div id="pres" style="display:none">
      <hr class="divr">
      <div class="ib gr" id="pmeta"></div>
      <div id="pnodes"></div>
    </div>
    <div id="perr" style="display:none;color:#f87171;font-size:11px;padding:4px 0"></div>
  </div>
  <!-- TAB: ANÁLISES -->
  <div id="tab-analyses" class="sb" style="display:none">
    <div class="lbl" style="margin-top:0">Dataset Wikispeedia</div>
    <div class="ib">
      <div class="sr"><span class="sk">Artigos</span><span class="sv">4.604</span></div>
      <div class="sr"><span class="sk">Links</span><span class="sv">119.882</span></div>
      <div class="sr"><span class="sk">Grau médio</span><span class="sv">26,04</span></div>
      <div class="sr"><span class="sk">Grau máx</span><span class="sv">294 (United States)</span></div>
    </div>
    <div class="lbl">Exploratórias</div>
    <div style="display:flex;flex-direction:column;gap:4px">
      <button class="cbtn" onclick="openChartModal('degree')"  >Distribuição de Graus<br><span class="cbtn-sub cbtn-sub-exp">EXPLORATÓRIA</span></button>
      <button class="cbtn" onclick="openChartModal('catdist')" >Artigos por Categoria<br><span class="cbtn-sub cbtn-sub-exp">EXPLORATÓRIA</span></button>
      <button class="cbtn" onclick="openChartModal('bfs')"     >BFS — Camadas por Fonte<br><span class="cbtn-sub cbtn-sub-exp">EXPLORATÓRIA</span></button>
    </div>
    <div class="lbl">Explanatórias</div>
    <div style="display:flex;flex-direction:column;gap:4px">
      <button class="cbtn" onclick="openChartModal('ranking')" >Top 15 Hubs<br><span class="cbtn-sub cbtn-sub-expl">EXPLANATÓRIA</span></button>
      <button class="cbtn" onclick="openChartModal('perf')"    >Desempenho Comparativo<br><span class="cbtn-sub cbtn-sub-expl">EXPLANATÓRIA</span></button>
    </div>
    <div class="lbl">Adicionais</div>
    <div style="display:flex;flex-direction:column;gap:4px">
      <button class="cbtn" onclick="openChartModal('dfs')"     >DFS — Classes de Arestas<br><span class="cbtn-sub cbtn-sub-add">ADICIONAL</span></button>
      <button class="cbtn" onclick="openChartModal('dijkstra')">Dijkstra — Custo e Saltos<br><span class="cbtn-sub cbtn-sub-add">ADICIONAL</span></button>
      <button class="cbtn" onclick="openChartModal('bellman')" >Bellman-Ford — Cenários<br><span class="cbtn-sub cbtn-sub-add">ADICIONAL</span></button>
    </div>
    <hr class="divr">
    <button class="cbtn" onclick="window.open('dashboard.html','_blank')" style="background:#0f2540;border-color:var(--accent);color:var(--accent)">
      📋 Abrir Dashboard Analítico<br><span class="cbtn-sub" style="color:#2dd4bf88">NOVA ABA · INTERATIVO</span>
    </button>
  </div>

</div><!-- /sidebar -->

<div id="ca">
  <canvas id="cv"></canvas>
  <div id="badge">Grafo Completo</div>
  <div id="hint">
    🖱 Scroll — zoom &nbsp;·&nbsp; Arrastar — mover<br>
    👆 Clique num ponto para explorar conexões
  </div>
  <!-- Expanded node floating panel -->
  <div id="expanded-panel">
    <span class="ep-close" onclick="closeExpanded()">✕</span>
    <div class="ep-title" id="ep-title"></div>
    <div class="ep-meta"  id="ep-meta"></div>
    <div style="font-size:10px;color:var(--muted);margin-bottom:4px">CONECTA A:</div>
    <div class="ep-links" id="ep-links"></div>
  </div>
  <!-- ANALYSIS: empty state shown when tab active, charts open as modals -->
  <div id="chart-panel" style="display:none;position:absolute;inset:0;background:#0b1120;
    overflow:hidden;flex-direction:column;align-items:center;justify-content:center;z-index:5">
    <div style="text-align:center;color:#2d4560">
      <div style="font-size:32px;margin-bottom:12px">📊</div>
      <div style="font-size:14px;font-weight:600;color:#3d5570;margin-bottom:6px">Selecione uma visualização</div>
      <div style="font-size:11px;color:#2d4060">Clique em qualquer item na barra lateral para abrir o gráfico</div>
    </div>
  </div>

  <!-- CHART MODAL OVERLAY (estilo amiga: overlay centra, modal rola) -->
  <div id="cm-overlay" onclick="if(event.target===this)closeChartModal()" style="display:none;position:fixed;inset:0;z-index:2000;background:rgba(0,0,0,.75);backdrop-filter:blur(4px);align-items:center;justify-content:center;padding:20px;box-sizing:border-box">
    <div id="cm" style="background:#0d1526;border:1px solid #1e3050;border-radius:14px;width:min(860px,95vw);max-height:90vh;overflow-y:auto;position:relative;box-shadow:0 12px 60px #000000bb;display:flex;flex-direction:column">
      <!-- header sticky -->
      <div style="display:flex;align-items:flex-start;justify-content:space-between;padding:18px 22px 14px;border-bottom:1px solid #162035;gap:12px;position:sticky;top:0;background:#0d1526;z-index:1;border-radius:14px 14px 0 0">
        <div style="display:flex;flex-direction:column;gap:6px;min-width:0">
          <div id="cm-title" style="font-size:17px;font-weight:700;color:var(--accent);line-height:1.3"></div>
          <span id="cm-badge" class="cm-badge cm-badge-exploratoria" style="align-self:flex-start"></span>
        </div>
        <button onclick="closeChartModal()" style="background:#1e3050;border:1px solid #2a4060;color:#94a3b8;width:30px;height:30px;border-radius:8px;cursor:pointer;font-size:15px;line-height:1;flex-shrink:0;display:flex;align-items:center;justify-content:center">✕</button>
      </div>
      <!-- modal body -->
      <div style="padding:18px 22px;display:flex;flex-direction:column;gap:16px">
        <div style="background:#f8fafc;border-radius:10px;padding:8px;border:1px solid #1e3050;display:flex;align-items:center;justify-content:center">
          <img id="cm-img" src="" alt="Visualização" style="max-width:100%;height:auto;border-radius:6px;display:block">
        </div>
        <div id="cm-insights" style="display:flex;flex-direction:column;gap:14px"></div>
      </div>
    </div>
  </div>

  <!-- DASHBOARD MODAL OVERLAY -->
  <div id="dm-overlay" onclick="if(event.target===this)closeDashModal()" style="display:none;position:fixed;inset:0;z-index:2000;background:rgba(0,0,0,.75);backdrop-filter:blur(4px);align-items:center;justify-content:center;padding:20px;box-sizing:border-box">
    <div id="dm" style="background:#0d1526;border:1px solid #1e3050;border-radius:14px;width:min(880px,95vw);max-height:90vh;overflow-y:auto;position:relative;box-shadow:0 12px 60px #000000bb">
      <div style="padding:20px 24px 14px;border-bottom:1px solid #162035;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;background:#0d1526;z-index:1;border-radius:14px 14px 0 0">
        <div>
          <div style="font-size:18px;font-weight:700;color:var(--accent)">📋 Dashboard Analítico — Wikispeedia</div>
          <div style="font-size:11px;color:var(--muted);margin-top:2px">Teoria dos Grafos 2026.1 · Dataset Stanford SNAP</div>
        </div>
        <button onclick="closeDashModal()" style="background:#1e3050;border:1px solid #2a4060;color:#94a3b8;width:30px;height:30px;border-radius:8px;cursor:pointer;font-size:15px;line-height:1;flex-shrink:0;display:flex;align-items:center;justify-content:center">✕</button>
      </div>
      <div id="dm-body" style="padding:24px"></div>
    </div>
  </div>
</div>
</div>
<div id="tt"></div>

<script>
const NODES={nodes_json};
const EDGES={edges_json};
const CC={cat_colors_json};
</script>
<script>
// ── indices ───────────────────────────────────────────────────────
const byId  = new Map(NODES.map(n=>[n.id,n]));
const byRaw = new Map(NODES.map(n=>[n.raw,n]));
const adjOut = new Map(NODES.map(n=>[n.id,[]]));
const adjAll = new Map(NODES.map(n=>[n.id,[]]));
for(const e of EDGES){{
  adjOut.get(e.s)?.push({{id:e.t,w:e.w}});
  adjAll.get(e.s)?.push({{id:e.t,w:e.w}});
  adjAll.get(e.t)?.push({{id:e.s,w:e.w}});
}}

// ── canvas ────────────────────────────────────────────────────────
const cv=document.getElementById('cv'), ctx=cv.getContext('2d');
let W=0,H=0;
function resize(){{
  W=cv.width=cv.parentElement.clientWidth;
  H=cv.height=cv.parentElement.clientHeight;
}}
window.addEventListener('resize',()=>{{resize();redraw();}});

// ── state ─────────────────────────────────────────────────────────
let tab='full', xf=d3.zoomIdentity, hov=null;
let activeCat=null;
let expandedId=null;
let showAllEdges=false;
let showLabels=false;   // node currently expanded (connections shown)
let expandFull=false;       // whether current expansion shows all neighbours
let highlightSet=new Set(); // neighbour ids of expanded node

// ego tab state
let egoNodes=[],egoEdges=[],egoCtr=new Set(),egoSim=null,egoSelId=null;
let egoCat=null;  // active category filter in ego tab
// path tab state
let pSrc=null,pTgt=null,pathIds=[];

// ── category chips ────────────────────────────────────────────────
const CAT_PT={{
  Science:'Ciência',Geography:'Geografia',People:'Pessoas',
  History:'História',Everyday_life:'Cotidiano',
  Design_and_Technology:'Design e Tecnologia',Countries:'Países',
  Citizenship:'Cidadania',Language_and_literature:'Língua e Literatura',
  Religion:'Religião',Music:'Música',Business_Studies:'Negócios',
  IT:'Tecnologia',Mathematics:'Matemática',Art:'Arte',other:'Outro'
}};
(()=>{{
  // Build both chip containers (full graph + ego graph)
  for(const gid of ['chips','ego-chips']){{
    const g=document.getElementById(gid);
    const isEgo=(gid==='ego-chips');
    for(const [cat,color] of Object.entries(CC)){{
      const c=document.createElement('div');
      c.className='chip';c.textContent=CAT_PT[cat]||cat.replace(/_/g,' ');
      c.style.color=color;c.style.background=color+'18';c.dataset.cat=cat;
      c.onclick=()=>isEgo?toggleEgoCat(cat):toggleCat(cat);
      g.appendChild(c);
    }}
  }}
}})();
function toggleCatPanel(){{
  const panel=document.getElementById('cat-panel');
  const icon=document.getElementById('cat-toggle-icon');
  const open=panel.style.display==='flex';
  panel.style.display=open?'none':'flex';
  icon.style.transform=open?'':'rotate(180deg)';
}}
function toggleAllEdges(){{
  showAllEdges=!showAllEdges;
  const btn=document.getElementById('btn-all-edges');
  if(showAllEdges){{
    btn.style.background='#0f2540';btn.style.borderColor='var(--accent)';btn.style.color='var(--accent)';
    btn.textContent='◉ Arestas — ativadas';
  }}else{{
    btn.style.background='#0a1628';btn.style.borderColor='#1e3050';btn.style.color='#3d5570';
    btn.textContent='◌ Arestas — desativadas';
  }}
  redraw();
}}
function toggleLabels(){{
  showLabels=!showLabels;
  const btn=document.getElementById('btn-labels');
  if(showLabels){{
    btn.style.background='#0f2540';btn.style.borderColor='var(--accent)';btn.style.color='var(--accent)';
    btn.textContent='◉ Labels — ativadas';
  }}else{{
    btn.style.background='#0a1628';btn.style.borderColor='#1e3050';btn.style.color='#3d5570';
    btn.textContent='◌ Labels — desativadas';
  }}
  redraw();
}}
function toggleCat(cat){{
  activeCat=activeCat===cat?null:cat;
  document.querySelectorAll('#chips .chip').forEach(c=>c.classList.toggle('on',c.dataset.cat===activeCat));
  redraw();
}}
function clearCat(){{
  activeCat=null;
  document.querySelectorAll('#chips .chip').forEach(c=>c.classList.remove('on'));
  document.getElementById('stv').textContent=NODES.length.toLocaleString();
  redraw();
}}
function toggleEgoCat(cat){{
  egoCat=egoCat===cat?null:cat;
  document.querySelectorAll('#ego-chips .chip').forEach(c=>c.classList.toggle('on',c.dataset.cat===egoCat));
  redraw();
}}
function clearEgoCat(){{
  egoCat=null;
  document.querySelectorAll('#ego-chips .chip').forEach(c=>c.classList.remove('on'));
  redraw();
}}

// ── zoom ──────────────────────────────────────────────────────────
const zoom=d3.zoom().scaleExtent([0.02,30])
  .on('zoom',e=>{{xf=e.transform;redraw();}});
d3.select(cv).call(zoom);

function fitView(){{
  const xs=NODES.map(n=>n.x),ys=NODES.map(n=>n.y);
  const x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);
  const s=Math.min(W/(x1-x0),H/(y1-y0))*4.5;
  d3.select(cv).call(zoom.transform,
    d3.zoomIdentity.translate(W/2-s*(x0+x1)/2,H/2-s*(y0+y1)/2).scale(s));
}}

// ── expanded node panel ───────────────────────────────────────────
function expandNode(node, full=false){{
  expandedId=node.id;
  expandFull=full;
  highlightSet=new Set([node.id]);
  const allNeighbors=adjAll.get(node.id)||[];
  // deduplicate by id (adjAll has both directions so same node can appear twice)
  const seenNbs=new Set();
  const uniqueNeighbors=allNeighbors.filter(nb=>{{
    if(seenNbs.has(nb.id)) return false;
    seenNbs.add(nb.id);
    return nb.id !== node.id;  // also exclude self
  }});
  // sort by neighbour degree descending, then slice if needed
  const sorted=[...uniqueNeighbors].sort((a,b)=>(byId.get(b.id)?.deg||0)-(byId.get(a.id)?.deg||0));
  const neighbors = (!full && sorted.length>30) ? sorted.slice(0,30) : sorted;
  neighbors.forEach(nb=>highlightSet.add(nb.id));

  const color=CC[node.cat]||'#94a3b8';
  document.getElementById('ep-title').innerHTML=
    `<span style="color:${{color}}">${{node.label}}</span>`;
  const totalNb=(adjAll.get(node.id)||[]).length;
  const truncated=!full&&totalNb>30;
  const epMetaEl=document.getElementById('ep-meta');
  epMetaEl.innerHTML=`${{CAT_PT[node.cat]||node.cat}} · grau ${{node.deg}}`
    +(truncated
      ? `<br><span style="color:var(--accent);font-size:10px;cursor:pointer"
           onclick="expandNode(byId.get(${{node.id}}),true)">
           ▸ mostrando 30 de ${{totalNb}} — clique aqui para ver todas</span>`
      : ``);

  const linksEl=document.getElementById('ep-links');
  linksEl.innerHTML='';
  // neighbors is already sorted by degree from expandNode
  for(const nb of neighbors.slice(0,40)){{
    const nd=byId.get(nb.id); if(!nd) continue;
    const c=CC[nd.cat]||'#94a3b8';
    const el=document.createElement('div');
    el.className='ep-link';
    el.innerHTML=`<span style="color:${{c}}">●</span> ${{nd.label}}`;
    el.onclick=()=>{{
      expandNode(nd);
      // pan to it
      const sc=Math.max(xf.k,2);
      d3.select(cv).transition().duration(400)
        .call(zoom.transform,d3.zoomIdentity
          .translate(W/2-nd.x*sc,H/2-nd.y*sc).scale(sc));
    }};
    linksEl.appendChild(el);
  }}
  if(sorted.length>40){{
    const more=document.createElement('div');
    more.style.cssText='color:#3d5570;font-size:10px;padding:4px 0';
    more.textContent=`+ ${{sorted.length-40}} mais conexões`;
    linksEl.appendChild(more);
  }}

  document.getElementById('expanded-panel').style.display='block';
  document.getElementById('stsel').textContent=node.label;
  redraw();
}}
function closeExpanded(){{
  expandedId=null;expandFull=false;highlightSet=new Set();
  document.getElementById('expanded-panel').style.display='none';
  document.getElementById('stsel').textContent='—';
  redraw();
}}

// ── interaction ───────────────────────────────────────────────────
cv.addEventListener('mousemove',e=>{{
  const [mx,my]=xf.invert([e.offsetX,e.offsetY]);
  hov=null;
  if(tab==='ego'){{
    for(const n of egoNodes){{
      const dx=n.x-mx,dy=n.y-my;
      if(dx*dx+dy*dy<(n.dot+6)*(n.dot+6)){{hov=n;break;}}
    }}
  }} else {{
    // Priority: check highlighted nodes first, then rest
    // This prevents dimmed nodes from stealing hover/click
    const priority = expandedId!==null
      ? [...highlightSet].map(id=>byId.get(id)).filter(Boolean)
      : NODES;
    const rest = expandedId!==null ? NODES : [];
    for(const pool of [priority, rest]){{
      for(const n of pool){{
        const dx=n.x-mx,dy=n.y-my;
        const r=Math.max(n.dot,3)+4;
        if(dx*dx+dy*dy<r*r){{hov=n;break;}}
      }}
      if(hov) break;
    }}
  }}
  tip(hov,e.clientX,e.clientY);
  redraw();
}});
cv.addEventListener('mouseleave',()=>{{hov=null;tipOff();redraw();}});

let ct=null;
cv.addEventListener('click',()=>{{
  if(!hov){{
    if(tab==='full') closeExpanded();
    return;
  }}
  if(ct){{
    // double-click
    clearTimeout(ct);ct=null;
    if(tab==='full'){{
      expandNode(hov, true);
    }} else if(tab==='ego'){{
      const sc=Math.max(xf.k,4);
      d3.select(cv).transition().duration(500)
        .call(zoom.transform,d3.zoomIdentity
          .translate(W/2-hov.x*sc,H/2-hov.y*sc).scale(sc));
      egoExpand(hov);
    }}
  }} else {{
    // single-click
    ct=setTimeout(()=>{{
      ct=null;
      if(tab==='full') expandNode(hov, false);
      else if(tab==='ego'){{
        egoSelId=egoSelId===hov.id?null:hov.id;
        redraw();
      }}
    }},220);
  }}
}});

// ── tooltip ───────────────────────────────────────────────────────
function tip(n,x,y){{
  const el=document.getElementById('tt');
  if(!n){{el.classList.remove('on');return;}}
  const c=CC[n.cat]||'#94a3b8';
  el.innerHTML=`<b style="color:${{c}}">${{n.label}}</b>
    <div style="color:#3d5570;margin-top:2px">${{CAT_PT[n.cat]||n.cat}} · grau ${{n.deg}}</div>`;
  const pw=el.offsetWidth,ph=el.offsetHeight;
  el.style.left=(x+14+pw>window.innerWidth?x-pw-10:x+14)+'px';
  el.style.top =(y+14+ph>window.innerHeight?y-ph-10:y+14)+'px';
  el.classList.add('on');
}}
function tipOff(){{document.getElementById('tt').classList.remove('on');}}
const nc=n=>CC[n.cat]||'#94a3b8';

// ── DRAW ──────────────────────────────────────────────────────────
function redraw(){{
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle='#08111f';ctx.fillRect(0,0,W,H);
  if(tab==='full') drawFull();
  else if(tab==='ego') drawEgo();
  else drawPathMode();
}}

// ── FULL: dot-map with on-click expansion ─────────────────────────
function drawFull(){{
  const k=xf.k;
  const hasExp=expandedId!==null;
  const hasCat=activeCat!==null;

  ctx.save();ctx.translate(xf.x,xf.y);ctx.scale(k,k);

  // ── Modo Apresentação: todas as arestas com baixíssima opacidade ──
  if(showAllEdges && !hasExp){{
    ctx.strokeStyle='rgba(255,255,255,0.04)';
    ctx.lineWidth=0.5/k;
    ctx.beginPath();
    for(const e of EDGES){{
      const s=byId.get(e.s),t=byId.get(e.t);
      if(!s||!t)continue;
      const sx=s.x*k+xf.x,sy=s.y*k+xf.y;
      const tx2=t.x*k+xf.x,ty2=t.y*k+xf.y;
      if(Math.max(sx,tx2)<-100||Math.min(sx,tx2)>W+100)continue;
      if(Math.max(sy,ty2)<-100||Math.min(sy,ty2)>H+100)continue;
      ctx.moveTo(s.x,s.y);ctx.lineTo(t.x,t.y);
    }}
    ctx.stroke();
  }}

  // ── Draw expansion edges (connections of expanded node) ──
  if(hasExp){{
    const center=byId.get(expandedId);
    if(center){{
      ctx.strokeStyle='#2dd4bf';ctx.lineWidth=1/k;ctx.globalAlpha=0.35;
      ctx.beginPath();
      for(const nb of (adjAll.get(expandedId)||[])){{
        if(!highlightSet.has(nb.id)) continue;  // only draw to visible neighbours
        const t=byId.get(nb.id);if(!t)continue;
        const sx=center.x*k+xf.x,sy=center.y*k+xf.y;
        const tx2=t.x*k+xf.x,ty2=t.y*k+xf.y;
        if(Math.max(sx,tx2)<-50||Math.min(sx,tx2)>W+50)continue;
        if(Math.max(sy,ty2)<-50||Math.min(sy,ty2)>H+50)continue;
        ctx.moveTo(center.x,center.y);ctx.lineTo(t.x,t.y);
      }}
      ctx.stroke();ctx.globalAlpha=1;
    }}
  }}

  // ── Draw all nodes as dots ──
  for(const n of NODES){{
    const sx=n.x*k+xf.x,sy=n.y*k+xf.y;
    if(sx<-10||sx>W+10||sy<-10||sy>H+10)continue;

    const isExp=n.id===expandedId;
    const isNb=hasExp&&highlightSet.has(n.id)&&!isExp;
    const isCatMatch=!hasCat||(n.cat===activeCat);
    const isHov=hov?.id===n.id;

    // opacity: dim everything not in highlight/cat
    let alpha=1;
    if(hasCat&&!isCatMatch&&!isExp) alpha=0.06;
    else if(hasExp&&!highlightSet.has(n.id)) alpha=0.08;

    ctx.globalAlpha=alpha;

    const c=nc(n);
    // radius: base dot + bigger if expanded/neighbour/hovered
    let r=n.dot*0.65;
    if(isExp) r=n.dot*1.4+3;
    else if(isNb) r=n.dot*1.0+1.5;
    else if(isHov) r=n.dot*0.65+2.5;

    // glow for expanded node and hovered
    if((isExp||isHov)&&alpha>0.5){{
      ctx.shadowColor=c;ctx.shadowBlur=(isExp?20:12)/k;
    }}

    // glow: always on, intensity by role
    if(alpha>0.2){{
      ctx.shadowColor=c;
      ctx.shadowBlur=isExp?20/k:isNb?8/k:(n.deg>60?4/k:2/k);
    }}
    ctx.beginPath();ctx.arc(n.x,n.y,r,0,Math.PI*2);
    ctx.fillStyle=c;ctx.fill();
    ctx.shadowBlur=0;

    // border
    ctx.beginPath();ctx.arc(n.x,n.y,r,0,Math.PI*2);
    if(isExp)      {{ctx.strokeStyle='rgba(255,255,255,0.95)';ctx.lineWidth=2.5/k;}}
    else if(isNb)  {{ctx.strokeStyle='rgba(255,255,255,0.75)';ctx.lineWidth=1.8/k;}}
    else if(isHov) {{ctx.strokeStyle='rgba(255,255,255,0.85)';ctx.lineWidth=2/k;}}
    else           {{ctx.strokeStyle='rgba(255,255,255,0.28)';ctx.lineWidth=0.9/k;}}
    ctx.stroke();

    // Labels: show for expanded+neighbours always,
    // for hubs at mid zoom, for all at close zoom
    const showLabel = isExp||isNb||isHov
      ||showLabels
      ||(k>1.5&&n.deg>200)
      ||(k>3.0&&n.deg>100)
      ||(k>6.0&&n.deg>40)
      ||(k>12.0&&n.deg>10)
      ||(k>20.0);

    if(showLabel&&alpha>0.1){{
      const fs=Math.max(11,Math.min(16,r*1.2+3))/k;
      ctx.font=`${{isExp?'bold ':isNb?'600 ':''}}${{fs}}px Segoe UI`;
      ctx.textAlign='center';ctx.textBaseline='top';
      const lbl=n.label.substring(0,22);
      const tw=ctx.measureText(lbl).width;
      const lx=n.x,ly=n.y+r+1.5/k,pad=2.5/k;
      ctx.fillStyle='rgba(6,11,22,0.65)';
      ctx.fillRect(lx-tw/2-pad,ly-pad,tw+pad*2,fs+pad*2);
      ctx.fillStyle='#ffffff';
      ctx.globalAlpha=Math.max(alpha,0.95);
      ctx.fillText(lbl,lx,ly);
      ctx.textBaseline='alphabetic';
    }}
    ctx.globalAlpha=1;
  }}
  ctx.restore();
}}

// ── EGO ──────────────────────────────────────────────────────────
function drawEgo(){{
  if(!egoNodes.length){{
    ctx.textAlign='center';
    ctx.font='bold 15px Segoe UI';ctx.fillStyle='#e2e8f0';
    ctx.fillText('Busque um artigo para começar',W/2,H/2-8);
    ctx.font='12px Segoe UI';ctx.fillStyle='#3d5570';
    ctx.fillText('Use a barra lateral',W/2,H/2+14);return;
  }}
  const k=xf.k;
  ctx.save();ctx.translate(xf.x,xf.y);ctx.scale(k,k);
  const ss=egoSelId!==null,snbs=new Set();
  if(ss){{
    snbs.add(egoSelId);
    for(const e of egoEdges){{
      const s=typeof e.source==='object'?e.source.id:e.source;
      const t=typeof e.target==='object'?e.target.id:e.target;
      if(s===egoSelId)snbs.add(t);if(t===egoSelId)snbs.add(s);
    }}
  }}
  // set of node ids currently in egoNodes (for edge filtering)
  const eids_draw=new Set(egoNodes.map(n=>n.id));

  for(const e of egoEdges){{
    const src=e.source,tgt=e.target;if(!src?.x||!tgt?.x)continue;
    const sid=typeof src==='object'?src.id:src;
    const tid=typeof tgt==='object'?tgt.id:tgt;
    // skip edges where either endpoint is no longer in egoNodes
    if(!eids_draw.has(sid)||!eids_draw.has(tid)) continue;
    const selDim=ss&&(!snbs.has(sid)||!snbs.has(tid));
    const catDimE=egoCat&&(byId.get(sid)?.cat!==egoCat&&byId.get(tid)?.cat!==egoCat);
    const dim=selDim||catDimE;
    ctx.beginPath();ctx.moveTo(src.x,src.y);ctx.lineTo(tgt.x,tgt.y);
    ctx.strokeStyle=dim?'#1a2a3a':'#2a4a6a';ctx.lineWidth=1/k;
    ctx.globalAlpha=dim?0.06:0.55;ctx.stroke();ctx.globalAlpha=1;
  }}
  for(const n of egoNodes){{
    if(!n.x)continue;
    const isc=egoCtr.has(n.id),h=hov?.id===n.id,issel=egoSelId===n.id;
    const catDim=egoCat&&n.cat!==egoCat&&!egoCtr.has(n.id);
    const dim=(ss&&!snbs.has(n.id))||catDim;
    const c=nc(n),r=isc?n.dot*1.5+4:n.dot;
    ctx.globalAlpha=dim?0.12:1;
    if((isc||h)&&!dim){{ctx.shadowColor=c;ctx.shadowBlur=12/k;}}
    ctx.beginPath();ctx.arc(n.x,n.y,h||issel?r+3:r,0,Math.PI*2);
    ctx.fillStyle=issel?'#fff':c;ctx.fill();ctx.shadowBlur=0;
    ctx.strokeStyle=h||issel?'#fff':'rgba(0,0,0,0.3)';
    ctx.lineWidth=(h||issel?2:0.5)/k;ctx.stroke();
    if(!dim){{
      const fs=Math.max(9,Math.min(13,r*0.9))/k;
      ctx.font=`${{isc?'bold ':''}}${{fs}}px Segoe UI`;
      ctx.textAlign='center';ctx.textBaseline='top';
      const lbl=n.label.substring(0,20),tw=ctx.measureText(lbl).width;
      const lx=n.x,ly=n.y+r+2/k,pad=2/k;
      ctx.fillStyle='rgba(6,11,22,0.52)';
      ctx.fillRect(lx-tw/2-pad,ly-pad,tw+pad*2,fs+pad*2);
      ctx.fillStyle=isc?'#fff':'#94a3b8';ctx.fillText(lbl,lx,ly);
      ctx.textBaseline='alphabetic';
    }}
    ctx.globalAlpha=1;
  }}
  ctx.restore();
}}

// ── PATH ─────────────────────────────────────────────────────────
function drawPathMode(){{
  if(!pathIds.length){{
    ctx.textAlign='center';ctx.font='bold 14px Segoe UI';ctx.fillStyle='#e2e8f0';
    ctx.fillText('Escolha origem e destino para calcular o caminho',W/2,H/2);return;
  }}
  const k=xf.k;
  ctx.save();ctx.translate(xf.x,xf.y);ctx.scale(k,k);
  const ps=new Set(pathIds);
  // Path edges FIRST (under nodes)
  ctx.strokeStyle='rgba(255,255,255,0.75)';ctx.lineWidth=1.8/k;
  ctx.shadowColor='rgba(255,255,255,0.9)';ctx.shadowBlur=10/k;ctx.globalAlpha=0.85;
  for(let i=0;i<pathIds.length-1;i++){{
    const s=byId.get(pathIds[i]),t=byId.get(pathIds[i+1]);
    if(!s||!t)continue;
    ctx.beginPath();ctx.moveTo(s.x,s.y);ctx.lineTo(t.x,t.y);ctx.stroke();
  }}
  ctx.shadowBlur=0;ctx.globalAlpha=1;

  // All nodes on top
  for(const n of NODES){{
    const sx=n.x*k+xf.x,sy=n.y*k+xf.y;
    if(sx<-10||sx>W+10||sy<-10||sy>H+10)continue;
    const on=ps.has(n.id);
    ctx.globalAlpha=on?1:0.05;
    if(on){{
      ctx.shadowColor='rgba(255,255,255,0.6)';
      ctx.shadowBlur=14/k;
    }}
    ctx.beginPath();ctx.arc(n.x,n.y,on?n.dot*1.8+3:n.dot,0,Math.PI*2);
    ctx.fillStyle=nc(n);ctx.fill();
    ctx.shadowBlur=0;
    if(on){{
      ctx.shadowColor='rgba(255,255,255,0.8)';ctx.shadowBlur=10/k;
      ctx.beginPath();ctx.arc(n.x,n.y,n.dot*1.8+3,0,Math.PI*2);
      ctx.strokeStyle='rgba(255,255,255,0.9)';ctx.lineWidth=2/k;ctx.stroke();
      ctx.shadowBlur=0;
    }}
    ctx.globalAlpha=1;
  }}
  // Path labels
  for(const id of pathIds){{
    const n=byId.get(id);if(!n)continue;
    const fs=Math.max(10,14)/k;
    ctx.font=`bold ${{fs}}px Segoe UI`;ctx.textAlign='center';ctx.textBaseline='top';
    const lbl=n.label.substring(0,24),tw=ctx.measureText(lbl).width;
    const lx=n.x,ly=n.y+n.dot*1.8+3+4/k,pad=3/k;
    ctx.fillStyle='rgba(6,11,22,0.9)';
    ctx.fillRect(lx-tw/2-pad,ly-pad,tw+pad*2,fs+pad*2);
    ctx.fillStyle='#4ade80';ctx.fillText(lbl,lx,ly);ctx.textBaseline='alphabetic';
  }}
  ctx.restore();
}}

// ── EGO EXPAND ───────────────────────────────────────────────────
function egoExpand(node){{
  const eids=new Set(egoNodes.map(n=>n.id));
  egoCtr.add(node.id);
  const pn=egoNodes.find(n=>n.id===node.id);
  const px=pn?.x??W/2,py=pn?.y??H/2;
  if(!eids.has(node.id)){{egoNodes.push({{...byId.get(node.id),x:px,y:py}});eids.add(node.id);}}
  const nbs=(adjAll.get(node.id)||[]).slice(0,30);
  const step=2*Math.PI/Math.max(nbs.length,1);
  nbs.forEach(({{id:nid}},i)=>{{
    const nd=byId.get(nid);if(!nd||eids.has(nid))return;
    egoNodes.push({{...nd,
      x:px+Math.cos(step*i)*(90+Math.random()*40),
      y:py+Math.sin(step*i)*(90+Math.random()*40)}});
    eids.add(nid);
  }});
  // Rebuild edges cleanly from scratch — no ghost edges
  const em=new Map();
  for(const n of egoNodes){{
    for(const {{id:nid,w}} of (adjAll.get(n.id)||[])){{
      if(eids.has(nid)){{
        const key=Math.min(n.id,nid)+'-'+Math.max(n.id,nid);
        if(!em.has(key)) em.set(key,{{source:n.id,target:nid,weight:w}});
      }}
    }}
  }}
  egoEdges=Array.from(em.values());
  if(egoSim)egoSim.stop();
  egoNodes=egoNodes.map(n=>{{return{{...n,fx:null,fy:null}}}});
  egoEdges=egoEdges.map(e=>{{return{{...e}}}});
  egoSim=d3.forceSimulation(egoNodes)
    .force('link',d3.forceLink(egoEdges).id(d=>d.id).distance(90).strength(0.4))
    .force('charge',d3.forceManyBody().strength(-200))
    .force('center',d3.forceCenter(W/2,H/2).strength(0.04))
    .force('collide',d3.forceCollide(d=>d.dot*1.5+8))
    .alphaDecay(0.03)
    .on('tick',()=>{{if(tab==='ego')redraw();}});
  document.getElementById('en').textContent=egoNodes.length;
  document.getElementById('ee').textContent=egoEdges.length;

  // Centralizar a view no ego após a simulação se acomodar
  let centered=false;
  egoSim.on('tick.center',()=>{{
    if(!centered && egoSim.alpha()<0.15){{
      centered=true;
      const xs=egoNodes.map(n=>n.x),ys=egoNodes.map(n=>n.y);
      const x0=Math.min(...xs),x1=Math.max(...xs);
      const y0=Math.min(...ys),y1=Math.max(...ys);
      const padded_w=x1-x0+120,padded_h=y1-y0+120;
      const s=Math.min(W/padded_w,H/padded_h,4);
      const cx=(x0+x1)/2,cy=(y0+y1)/2;
      d3.select(cv).transition().duration(600)
        .call(zoom.transform,d3.zoomIdentity
          .translate(W/2-cx*s,H/2-cy*s).scale(s));
    }}
  }});
}}
function egoStart(){{
  const raw=document.getElementById('es').dataset.selectedRaw;
  if(!raw)return;const node=byRaw.get(raw);if(!node)return;
  egoReset();
  setTimeout(()=>{{
    egoExpand(node);
    // pan to node position, keep current zoom or use minimum zoom
    const sc=Math.max(xf.k,1.5);
    d3.select(cv).transition().duration(500)
      .call(zoom.transform,d3.zoomIdentity
        .translate(W/2-node.x*sc,H/2-node.y*sc).scale(sc));
  }},30);
}}
function egoReset(){{
  if(egoSim){{egoSim.stop();egoSim=null;}}
  egoNodes=[];egoEdges=[];egoCtr=new Set();egoSelId=null;
  egoCat=null;
  document.querySelectorAll('#ego-chips .chip').forEach(c=>c.classList.remove('on'));
  document.getElementById('es').value='';
  document.getElementById('en').textContent='0';
  document.getElementById('ee').textContent='0';
  redraw();
}}

// ── DIJKSTRA ─────────────────────────────────────────────────────
function dijkJS(src,tgt){{
  const dist=new Map(NODES.map(n=>[n.id,Infinity]));
  const par=new Map();const vis=new Set();
  dist.set(src,0);par.set(src,null);
  const heap=[{{id:src,d:0}}];
  while(heap.length){{
    heap.sort((a,b)=>a.d-b.d);
    const {{id:u}}=heap.shift();
    if(vis.has(u))continue;vis.add(u);if(u===tgt)break;
    for(const {{id:v,w}} of (adjOut.get(u)||[])){{
      const nd=dist.get(u)+w;
      if(nd<dist.get(v)){{dist.set(v,nd);par.set(v,u);heap.push({{id:v,d:nd}});}}
    }}
  }}
  if(!isFinite(dist.get(tgt)))return null;
  const path=[];let cur=tgt;
  while(cur!==null&&cur!==undefined){{path.unshift(cur);cur=par.get(cur);}}
  return{{path,distance:dist.get(tgt)}};
}}
function runDijk(){{
  const err=document.getElementById('perr'),res=document.getElementById('pres');
  err.style.display='none';res.style.display='none';pathIds=[];
  if(!pSrc||!pTgt){{err.textContent='Selecione origem e destino.';err.style.display='block';return;}}
  if(pSrc.id===pTgt.id){{err.textContent='Origem e destino são iguais.';err.style.display='block';return;}}
  err.textContent='⏳ Calculando…';err.style.display='block';
  setTimeout(()=>{{
    const r=dijkJS(pSrc.id,pTgt.id);
    err.style.display='none';
    if(!r){{err.textContent='Nenhum caminho encontrado.';err.style.display='block';return;}}
    pathIds=r.path;
    document.getElementById('pmeta').innerHTML=`
      <div class="sr"><span class="sk">Artigos</span><span class="sv">${{r.path.length}}</span></div>
      <div class="sr"><span class="sk">Saltos</span><span class="sv">${{r.path.length-1}}</span></div>
      <div class="sr"><span class="sk">Distância</span><span class="sv">${{r.distance.toFixed(5)}}</span></div>`;
    const pn=document.getElementById('pnodes');pn.innerHTML='';
    r.path.forEach((id,i)=>{{
      const n=byId.get(id),row=document.createElement('div');row.className='pn';
      row.innerHTML=`<div class="pd"></div><span>${{n.label}}</span>
        ${{i<r.path.length-1?'<span class="pa">↓</span>':''}}`;
      pn.appendChild(row);
    }});
    res.style.display='block';
    const xs=r.path.map(id=>byId.get(id).x),ys=r.path.map(id=>byId.get(id).y);
    const cx=(Math.min(...xs)+Math.max(...xs))/2,cy=(Math.min(...ys)+Math.max(...ys))/2;
    const rx=Math.max(...xs)-Math.min(...xs)+200,ry=Math.max(...ys)-Math.min(...ys)+200;
    const sc=Math.min(W/rx,H/ry,5)*0.85;
    d3.select(cv).transition().duration(700)
      .call(zoom.transform,d3.zoomIdentity
        .translate(W/2-cx*sc,H/2-cy*sc).scale(sc));
    redraw();
  }},20);
}}
function clearPath(){{
  pathIds=[];pSrc=null;pTgt=null;
  document.getElementById('ps').value='';document.getElementById('pt').value='';
  document.getElementById('pres').style.display='none';
  document.getElementById('perr').style.display='none';redraw();
}}

// ── AUTOCOMPLETE ──────────────────────────────────────────────────
function mkAC(inp,ac,onSel){{
  inp.addEventListener('input',()=>{{
    const v=inp.value.trim().toLowerCase();
    if(!v||v.length<2){{ac.style.display='none';return;}}
    // collect all matches, then sort by relevance:
    // 1st: label starts with query, 2nd: word in label starts with query, 3rd: substring match
    const exact=[], wordStart=[], rest=[];
    for(const n of NODES){{
      const lbl=n.label.toLowerCase();
      if(lbl.includes(v)||n.raw.toLowerCase().includes(v)){{
        if(lbl.startsWith(v)) exact.push(n);
        else if(lbl.split(' ').some(w=>w.startsWith(v))) wordStart.push(n);
        else rest.push(n);
      }}
    }}
    const m=[...exact,...wordStart,...rest].slice(0,12);
    if(!m.length){{ac.style.display='none';return;}}
    ac.innerHTML='';
    m.forEach(n=>{{
      const it=document.createElement('div');it.className='aci';
      const c=CC[n.cat]||'#94a3b8';
      it.innerHTML=`<span style="color:${{c}};font-weight:600">${{n.label}}</span>
        <span style="color:#3d5570;font-size:10px;margin-left:4px">
          ${{(n.cat||'').replace(/_/g,' ')}}</span>`;
      it.addEventListener('mousedown',ev=>{{
        ev.preventDefault();
        inp.value=n.label;inp.dataset.selectedRaw=n.raw;
        ac.style.display='none';onSel(n);
      }});
      ac.appendChild(it);
    }});
    ac.style.display='block';
  }});
  document.addEventListener('click',e=>{{
    if(!ac.contains(e.target)&&e.target!==inp)ac.style.display='none';
  }});
}}

mkAC(document.getElementById('fs'),document.getElementById('fac'),n=>{{
  expandNode(n);
  const sc=Math.max(xf.k,3);
  d3.select(cv).transition().duration(600)
    .call(zoom.transform,d3.zoomIdentity
      .translate(W/2-n.x*sc,H/2-n.y*sc).scale(sc));
}});
mkAC(document.getElementById('es'),document.getElementById('eac'),()=>{{}});
mkAC(document.getElementById('ps'),document.getElementById('psac'),n=>{{pSrc=n;}});
mkAC(document.getElementById('pt'),document.getElementById('ptac'),n=>{{pTgt=n;}});

// ── TAB ───────────────────────────────────────────────────────────
const TB={{full:'Grafo Completo',ego:'Ego-Graph',path:'Caminho Mínimo',analyses:'Análises'}};
const TH={{
  full:'🖱 Scroll — zoom &nbsp;·&nbsp; Arrastar — mover<br>👆 Clique num ponto para ver conexões',
  ego: '🖱 Scroll — zoom<br>👆👆 Duplo clique para expandir vizinhos',
  path:'⚡ Todos os nós dimmed · caminho destacado em verde',
  analyses:'📊 Selecione uma visualização na barra lateral',
}};
function switchTab(t){{
  tab=t;
  document.querySelectorAll('.tab').forEach(c=>c.classList.toggle('active',c.dataset.tab===t));
  ['full','ego','path','analyses'].forEach(x=>{{
    const el=document.getElementById('tab-'+x);
    if(el) el.style.display=x===t?'':'none';
  }});
  document.getElementById('badge').textContent=TB[t]||t;
  document.getElementById('hint').innerHTML=TH[t]||'';
  const isA=t==='analyses';
  document.getElementById('chart-panel').style.display=isA?'flex':'none';
  document.getElementById('cv').style.display=isA?'none':'block';
  document.getElementById('badge').style.display=isA?'none':'block';
  document.getElementById('hint').style.display=isA?'none':'block';
  if(!isA){{ closeExpanded(); redraw(); }}
  // quando aba 'analyses' fica ativa, o painel mostra a tela "Selecione uma visualização"
  // o usuário clica nos botões da sidebar (openChartModal) para abrir cada gráfico.
}}

__CHARTS_JS_PLACEHOLDER__
// ── BOOT ─────────────────────────────────────────────────────────
resize();
// Escalar posições para mais espaçamento entre nós
(()=>{{ const s=1.9; NODES.forEach(n=>{{n.x*=s;n.y*=s;}}); }})();
fitView();
</script>
</body>
</html>"""


