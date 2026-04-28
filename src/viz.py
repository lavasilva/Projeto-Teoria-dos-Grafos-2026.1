from __future__ import annotations
import sys
from pathlib import Path
from collections import defaultdict, deque

sys.path.insert(0, str(Path(__file__).parent))

from graphs.io import load_graph
from graphs.graph import Graph
from graphs.algorithms import dijkstra_path, bfs

try:
    from pyvis.network import Network
except ImportError:
    raise ImportError("Instale pyvis: pip3 install pyvis --break-system-packages")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
except ImportError:
    raise ImportError("Instale matplotlib: pip3 install matplotlib --break-system-packages")

ROOT     = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
OUT_DIR  = ROOT / "out"

ROTAS_OBRIGATORIAS = [
    ("REC", "POA"),
    ("MAO", "GRU"),
]
ROUTE_COLORS  = ["#e74c3c", "#2980b9"]
NODE_DEFAULT  = "#95a5a6"
EDGE_DEFAULT  = "#dfe6e9"

REGIAO_CORES = {
    "Nordeste":     "#e67e22",
    "Sudeste":      "#2980b9",
    "Sul":          "#27ae60",
    "Centro-Oeste": "#8e44ad",
    "Norte":        "#c0392b",
}

HUBS = {"REC", "GRU", "POA", "BSB", "MAO"}


def build_viz(g: Graph, rotas: list[tuple[str, str]], out_path: Path) -> None:
    net = Network(
        height="750px", width="100%",
        bgcolor="#1e1e2e", font_color="white", directed=True,
    )
    net.set_options("""
    {
      "physics": { "enabled": true, "stabilization": { "iterations": 150 } },
      "edges":   { "smooth": { "type": "curvedCW", "roundness": 0.1 } }
    }
    """)

    for node in g.nodes:
        meta  = g.node_meta.get(node, {})
        label = f"{node}\n{meta.get('cidade','')}"
        net.add_node(node, label=label, color=NODE_DEFAULT, size=18,
                     font={"size": 11, "color": "white"},
                     title=f"{meta.get('cidade','')} ({meta.get('regiao','')})")

    added_edges: set[frozenset] = set()
    for edge in g.edges:
        key = frozenset([edge.origem, edge.destino])
        if key not in added_edges:
            net.add_edge(edge.origem, edge.destino, color=EDGE_DEFAULT,
                         width=1, title=f"peso={edge.peso}")
            added_edges.add(key)

    for (origem, destino), color in zip(rotas, ROUTE_COLORS):
        custo, caminho = dijkstra_path(g, origem, destino)
        if caminho is None:
            continue
        label_rota = f"{origem}→{destino} (custo={custo:.2f})"
        print(f"  {label_rota}: {' -> '.join(caminho)}")
        for node in caminho:
            net.get_node(node)["color"]      = color
            net.get_node(node)["size"]        = 28
            net.get_node(node)["borderWidth"] = 3
            net.get_node(node)["font"]        = {"size": 13, "color": "white", "bold": True}
        for i in range(len(caminho) - 1):
            net.add_edge(caminho[i], caminho[i + 1], color=color, width=5,
                         title=label_rota, label=str(i + 1),
                         font={"size": 10, "color": color, "strokeWidth": 0},
                         arrows="to")

    for i, ((orig, dest), color) in enumerate(zip(rotas, ROUTE_COLORS)):
        custo, caminho = dijkstra_path(g, orig, dest)
        custo_str = f"{custo:.2f}" if caminho else "N/A"
        net.add_node(f"__leg_{i}__",
                     label=f"● {orig}→{dest}\n  custo={custo_str}",
                     color=color, shape="box", x=-600, y=-300 + i * 80,
                     physics=False, font={"size": 12, "color": "white"}, size=20)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    net.save_graph(str(out_path))
    print(f"  ✔ {out_path}")


def viz_histograma_graus(g: Graph, out_path: Path) -> None:
    graus = [g.degree(n) for n in g.nodes]

    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#ffffff")

    counts = defaultdict(int)
    for gr in graus:
        counts[gr] += 1

    xs = sorted(counts.keys())
    ys = [counts[x] for x in xs]

    bars = ax.bar(xs, ys, color="#2980b9", edgecolor="#1a5276",
                  linewidth=0.8, width=0.6, zorder=3)

    for bar, y in zip(bars, ys):
        ax.text(bar.get_x() + bar.get_width() / 2, y + 0.05,
                str(y), ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.set_title("Distribuição de Graus dos Aeroportos", fontsize=14,
                 fontweight="bold", pad=12)
    ax.set_xlabel("Grau (número de conexões)", fontsize=11)
    ax.set_ylabel("Quantidade de aeroportos", fontsize=11)
    ax.set_xticks(xs)
    ax.yaxis.grid(True, linestyle="--", alpha=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)

    nota = ("A maioria dos aeroportos tem grau 1–2 (periféricos).\n"
            "Poucos hubs (GRU, MAO, REC) concentram muitas conexões.")
    ax.text(0.98, 0.97, nota, transform=ax.transAxes, fontsize=8,
            va="top", ha="right", color="#555",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#eaf2ff", alpha=0.8))

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✔ {out_path}")


def viz_ranking_aeroportos(g: Graph, out_path: Path) -> None:
    dados = sorted(
        [(n, g.degree(n), g.node_meta[n].get("regiao","")) for n in g.nodes],
        key=lambda x: x[1], reverse=True
    )
    aeroportos = [f"{d[0]} ({g.node_meta[d[0]].get('cidade','')})" for d in dados]
    graus      = [d[1] for d in dados]
    regioes    = [d[2] for d in dados]
    cores      = [REGIAO_CORES.get(r, "#bdc3c7") for r in regioes]

    fig, ax = plt.subplots(figsize=(9, 7))
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#ffffff")

    bars = ax.barh(aeroportos, graus, color=cores, edgecolor="#555",
                   linewidth=0.5, zorder=3)

    for bar, grau in zip(bars, graus):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                str(grau), va="center", fontsize=10, fontweight="bold")

    ax.set_title("Ranking de Aeroportos por Número de Conexões",
                 fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Grau (número de conexões)", fontsize=11)
    ax.set_ylabel("Aeroporto", fontsize=11)
    ax.xaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.invert_yaxis()
    ax.spines[["top", "right"]].set_visible(False)

    legendas = [mpatches.Patch(color=c, label=r)
                for r, c in REGIAO_CORES.items()]
    ax.legend(handles=legendas, title="Região", loc="lower right",
              fontsize=8, title_fontsize=9)

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✔ {out_path}")


def viz_regioes(g: Graph, out_path: Path) -> None:
    regioes_nos: dict[str, set[str]] = defaultdict(set)
    for node in g.nodes:
        regioes_nos[g.node_meta[node].get("regiao","?")].add(node)

    regioes    = sorted(regioes_nos.keys())
    ordens     = []
    tamanhos   = []
    densidades = []

    for reg in regioes:
        sub = g.induced_subgraph(regioes_nos[reg])
        ordens.append(sub.order)
        tamanhos.append(sub.size)
        densidades.append(round(sub.density(), 3))

    x     = range(len(regioes))
    width = 0.25

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#ffffff")

    b1 = ax.bar([i - width for i in x], ordens,     width, label="Ordem |V|",
                color="#2980b9", edgecolor="#1a5276", linewidth=0.6, zorder=3)
    b2 = ax.bar([i          for i in x], tamanhos,  width, label="Tamanho |E|",
                color="#27ae60", edgecolor="#1e8449", linewidth=0.6, zorder=3)
    b3 = ax.bar([i + width  for i in x], densidades, width, label="Densidade",
                color="#e67e22", edgecolor="#d35400", linewidth=0.6, zorder=3)

    for bars in (b1, b2, b3):
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.02,
                    f"{h:.2f}" if h < 1.5 else str(int(h)),
                    ha="center", va="bottom", fontsize=8)

    ax.set_title("Comparação de Métricas por Região", fontsize=14,
                 fontweight="bold", pad=12)
    ax.set_xlabel("Região", fontsize=11)
    ax.set_ylabel("Valor", fontsize=11)
    ax.set_xticks(list(x))
    ax.set_xticklabels(regioes, fontsize=10)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✔ {out_path}")


def viz_bfs_camadas(g: Graph, start: str, out_path: Path) -> None:
    dist_bfs: dict[str, int] = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for nb in g.neighbors(node):
            if nb not in dist_bfs:
                dist_bfs[nb] = dist_bfs[node] + 1
                queue.append(nb)

    camadas: dict[int, list[str]] = defaultdict(list)
    for node, d in dist_bfs.items():
        camadas[d].append(node)

    nos_ord    = []
    camada_cor = []
    camada_val = []
    palette    = ["#2980b9", "#27ae60", "#e67e22", "#8e44ad", "#c0392b"]

    for camada in sorted(camadas.keys()):
        for node in sorted(camadas[camada]):
            cidade = g.node_meta[node].get("cidade", node)
            nos_ord.append(f"{node} – {cidade}")
            camada_cor.append(palette[camada % len(palette)])
            camada_val.append(dist_bfs[node])

    fig, ax = plt.subplots(figsize=(9, 8))
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#ffffff")

    bars = ax.barh(nos_ord, camada_val, color=camada_cor,
                   edgecolor="#555", linewidth=0.5, zorder=3)

    for bar, val in zip(bars, camada_val):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                f"nível {val}", va="center", fontsize=9)

    ax.set_title(f"Camadas BFS a partir de {start} (São Paulo/GRU)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Distância em saltos (nº de escalas)", fontsize=11)
    ax.set_ylabel("Aeroporto", fontsize=11)
    ax.set_xticks(range(max(camada_val) + 1))
    ax.xaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.invert_yaxis()
    ax.spines[["top", "right"]].set_visible(False)

    legendas = [mpatches.Patch(color=palette[i],
                label=f"Nível {i} ({len(camadas[i])} aeroportos)")
                for i in sorted(camadas.keys())]
    ax.legend(handles=legendas, title="Camada BFS", loc="lower right",
              fontsize=8, title_fontsize=9)

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✔ {out_path}")

def viz_densidade_ego(g: Graph, out_path: Path) -> None:
    dados = []
    for node in g.nodes:
        ego = g.ego_network(node)
        regiao = g.node_meta[node].get("regiao", "")
        cidade = g.node_meta[node].get("cidade", "")
        dados.append((f"{node} – {cidade}", ego.density(), regiao))

    dados.sort(key=lambda x: x[1], reverse=True)
    labels = [d[0] for d in dados]
    vals   = [d[1] for d in dados]
    cores  = [REGIAO_CORES.get(d[2], "#bdc3c7") for d in dados]

    fig, ax = plt.subplots(figsize=(9, 7))
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#ffffff")

    bars = ax.barh(labels, vals, color=cores, edgecolor="#555",
                   linewidth=0.5, zorder=3)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}", va="center", fontsize=9, fontweight="bold")

    ax.set_title("Densidade da Ego-Network por Aeroporto", fontsize=14,
                 fontweight="bold", pad=12)
    ax.set_xlabel("Densidade ego-network", fontsize=11)
    ax.set_ylabel("Aeroporto", fontsize=11)
    ax.set_xlim(0, 1.15)
    ax.xaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.invert_yaxis()
    ax.spines[["top", "right"]].set_visible(False)

    legendas = [mpatches.Patch(color=c, label=r) for r, c in REGIAO_CORES.items()]
    ax.legend(handles=legendas, title="Região", loc="lower right",
              fontsize=8, title_fontsize=9)

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✔ {out_path}")


def viz_custo_rotas(g: Graph, rotas_csv: Path, out_path: Path) -> None:
    import csv
    pares = []
    with rotas_csv.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            orig  = row["origem"].strip()
            dest  = row["destino"].strip()
            custo, caminho = dijkstra_path(g, orig, dest)
            n_escalas = len(caminho) - 2 if caminho else 0
            pares.append((f"{orig}→{dest}", custo, n_escalas))

    pares.sort(key=lambda x: x[1])
    labels  = [p[0] for p in pares]
    custos  = [p[1] for p in pares]
    escalas = [p[2] for p in pares]

    cmap = plt.cm.YlOrRd
    norm_vals = [(c - min(custos)) / (max(custos) - min(custos) + 1e-9) for c in custos]
    cores = [cmap(v) for v in norm_vals]

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#ffffff")

    bars = ax.bar(labels, custos, color=cores, edgecolor="#555",
                  linewidth=0.6, zorder=3)

    for bar, custo, esc in zip(bars, custos, escalas):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                f"{custo:.1f}\n({esc} escala{'s' if esc != 1 else ''})",
                ha="center", va="bottom", fontsize=8, fontweight="bold")

    ax.set_title("Custo das Rotas Calculadas pelo Dijkstra", fontsize=14,
                 fontweight="bold", pad=12)
    ax.set_xlabel("Par origem → destino", fontsize=11)
    ax.set_ylabel("Custo total (peso acumulado)", fontsize=11)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)

    sm = plt.cm.ScalarMappable(cmap=cmap,
         norm=plt.Normalize(vmin=min(custos), vmax=max(custos)))
    sm.set_array([])
    plt.colorbar(sm, ax=ax, label="Custo (menor → maior)", shrink=0.7)

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✔ {out_path}")


def viz_pizza_regioes(g: Graph, out_path: Path) -> None:
    contagem: dict[str, int] = defaultdict(int)
    for node in g.nodes:
        regiao = g.node_meta[node].get("regiao", "?")
        contagem[regiao] += 1

    regioes = sorted(contagem.keys())
    valores = [contagem[r] for r in regioes]
    cores   = [REGIAO_CORES.get(r, "#bdc3c7") for r in regioes]

    fig, ax = plt.subplots(figsize=(7, 7))
    fig.patch.set_facecolor("#f8f9fa")

    wedges, texts, autotexts = ax.pie(
        valores, labels=regioes, colors=cores,
        autopct="%1.0f%%", startangle=140,
        pctdistance=0.75,
        wedgeprops=dict(edgecolor="white", linewidth=2),
    )
    for t in texts:
        t.set_fontsize(11)
        t.set_fontweight("bold")
    for at in autotexts:
        at.set_fontsize(10)
        at.set_color("white")
        at.set_fontweight("bold")

    ax.set_title("Proporção de Aeroportos por Região", fontsize=14,
                 fontweight="bold", pad=16)

    legendas = [mpatches.Patch(color=cores[i], label=f"{regioes[i]} ({valores[i]})")
                for i in range(len(regioes))]
    ax.legend(handles=legendas, title="Região (qtd)", loc="lower right",
              fontsize=9, title_fontsize=10)

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✔ {out_path}")


def viz_hubs_vs_comuns(g: Graph, out_path: Path) -> None:
    graus_hub, egos_hub = [], []
    graus_com, egos_com = [], []

    for node in g.nodes:
        grau = g.degree(node)
        ego  = g.ego_network(node).density()
        if node in HUBS:
            graus_hub.append(grau)
            egos_hub.append(ego)
        else:
            graus_com.append(grau)
            egos_com.append(ego)

    categorias  = ["Hubs regionais", "Aeroportos comuns"]
    grau_medio  = [sum(graus_hub)/len(graus_hub), sum(graus_com)/len(graus_com)]
    ego_media   = [sum(egos_hub)/len(egos_hub),   sum(egos_com)/len(egos_com)]

    x     = [0, 1]
    width = 0.3

    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#ffffff")

    b1 = ax.bar([i - width/2 for i in x], grau_medio, width,
                label="Grau médio", color="#2980b9", edgecolor="#1a5276",
                linewidth=0.6, zorder=3)
    b2 = ax.bar([i + width/2 for i in x], ego_media,  width,
                label="Densidade ego média", color="#e67e22", edgecolor="#d35400",
                linewidth=0.6, zorder=3)

    for bar in list(b1) + list(b2):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.03,
                f"{h:.2f}", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_title("Hubs Regionais vs Aeroportos Comuns", fontsize=14,
                 fontweight="bold", pad=12)
    ax.set_ylabel("Valor médio", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(categorias, fontsize=11)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✔ {out_path}")


def run(
    airports_csv:    Path | None = None,
    adjacencias_csv: Path | None = None,
    rotas_csv:       Path | None = None,
    out_dir:         Path | None = None,
) -> None:
    airports_csv    = airports_csv    or DATA_DIR / "aeroportos_data.csv"
    adjacencias_csv = adjacencias_csv or DATA_DIR / "adjacencias_aeroportos.csv"
    rotas_csv       = rotas_csv       or DATA_DIR / "rotas.csv"
    out_dir         = out_dir         or OUT_DIR

    out_dir.mkdir(parents=True, exist_ok=True)

    print("Carregando grafo...")
    g = load_graph(airports_csv, adjacencias_csv)
    print(f"  {g}")

    print("\n[1/8] Grafo interativo com rotas...")
    build_viz(g, ROTAS_OBRIGATORIAS, out_dir / "arvore_percurso.html")

    print("\n[2/8] Histograma de distribuição de graus...")
    viz_histograma_graus(g, out_dir / "viz_graus_hist.png")

    print("\n[3/8] Ranking de aeroportos por grau...")
    viz_ranking_aeroportos(g, out_dir / "viz_ranking_barras.png")

    print("\n[4/8] Comparação de métricas por região...")
    viz_regioes(g, out_dir / "viz_regioes_barras.png")

    print("\n[5/8] Camadas BFS a partir de GRU...")
    viz_bfs_camadas(g, "GRU", out_dir / "viz_bfs_camadas.png")

    print("\n[6/8] Densidade ego-network por aeroporto...")
    viz_densidade_ego(g, out_dir / "viz_densidade_ego.png")

    print("\n[7/8] Custo das rotas (Dijkstra)...")
    viz_custo_rotas(g, rotas_csv, out_dir / "viz_custo_rotas.png")

    print("\n[8/8] Proporção de aeroportos por região...")
    viz_pizza_regioes(g, out_dir / "viz_pizza_regioes.png")

    print("\n[+] Hubs vs aeroportos comuns...")
    viz_hubs_vs_comuns(g, out_dir / "viz_hubs_vs_comuns.png")

    print("\nConcluído! Arquivos gerados em out/")


if __name__ == "__main__":
    run()