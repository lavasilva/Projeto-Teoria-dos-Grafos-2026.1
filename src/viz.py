from __future__ import annotations
import sys
import csv
import base64
from pathlib import Path
from collections import defaultdict, deque

sys.path.insert(0, str(Path(__file__).parent))

from graphs.io import load_graph
from graphs.graph import Graph
from graphs.algorithms import dijkstra_path

try:
    from pyvis.network import Network
except ImportError:
    raise ImportError("Instale pyvis: pip3 install pyvis --break-system-packages")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
except ImportError:
    raise ImportError("Instale matplotlib: pip3 install matplotlib --break-system-packages")

ROOT     = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
OUT_DIR  = ROOT / "out"

ROTAS_OBRIGATORIAS = [
    ("REC", "POA"),
    ("MAO", "GRU"),
]
ROUTE_COLORS  = ["#e74c3c", "#00b894"]
NODE_DEFAULT  = "#95a5a6"
EDGE_DEFAULT  = "#dfe6e9"

REGIAO_CORES = {
    "Nordeste":     "#e67e22",
    "Sudeste":      "#1a6fa8",
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
      "edges":   { "smooth": { "type": "curvedCW", "roundness": 0.1 } },
                    "interaction": { "navigationButtons": true, "keyboard": true }
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
    ax.legend(handles=legendas, title="Camada BFS", loc="upper right",
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
        radius=0.75,
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



VIZ_DESCRIPTIONS = [
    {
        "key":    "viz_graus_hist",
        "titulo": "Histograma de Graus",
        "tipo":   "Exploratória",
        "cor":    "#3b82f6",
        "o_que":  (
            "O histograma mostra a frequência de ocorrência de cada valor de grau na rede, "
            "ou seja, quantos aeroportos possuem cada número de conexões diretas. O eixo "
            "horizontal representa o grau e o eixo vertical a quantidade de aeroportos com "
            "aquele grau. Cada barra corresponde a um valor de grau observado na rede: 1, 2, 3, 4, 5 e 7."
        ),
        "insight": (
            "A distribuição é fortemente assimétrica à direita: 13 dos 20 aeroportos possuem "
            "grau 1 ou 2, enquanto apenas três aeroportos (GRU com grau 7, MAO e REC com grau 5) "
            "concentram a maior parte das conexões da rede. Esse padrão é característico de redes "
            "hub-and-spoke, onde poucos nós centralizam a conectividade e a maioria dos nós são "
            "periféricos, dependentes desses hubs para alcançar o restante da rede."
        ),
        "por_que": (
            "O histograma é o tipo canônico para distribuições de frequência de variáveis discretas. "
            "A escolha de uma única cor para todas as barras aplica o princípio de pregnância: o dado "
            "relevante é a altura de cada barra, não a distinção entre elas. A escala do eixo vertical "
            "começa em zero, boa prática obrigatória em histogramas de frequência para evitar distorção visual."
        ),
    },
    {
        "key":    "viz_bfs_camadas",
        "titulo": "Camadas BFS a partir de GRU",
        "tipo":   "Exploratória",
        "cor":    "#3b82f6",
        "o_que":  (
            "O gráfico de barras horizontais mostra a distância em número de saltos de cada aeroporto "
            "até GRU (São Paulo/Guarulhos), calculada pelo algoritmo de Busca em Largura (BFS). "
            "As barras são coloridas por nível: azul (nível 0), verde (nível 1), laranja (nível 2) e roxo (nível 3)."
        ),
        "insight": (
            "Sete aeroportos estão a apenas 1 salto de GRU (BSB, CNF, GIG, GYN, POA, REC e SSA). "
            "Nove aeroportos estão a 2 saltos, e três (PVH, RBR e VIX) estão a 3 saltos, sendo os "
            "mais periféricos da rede. A partir do maior hub, qualquer aeroporto pode ser alcançado "
            "em no máximo 3 escalas. PVH e RBR dependem de MAO como hub intermediário, configurando "
            "uma cadeia de dependência característica de aeroportos em regiões geograficamente distantes."
        ),
        "por_que": (
            "Barras horizontais foram escolhidas porque os rótulos dos aeroportos são longos e "
            "ficariam ilegíveis em barras verticais. A lei da proximidade é aplicada pelo agrupamento "
            "natural por nível, e a lei da similaridade pela cor — a mesma cor significa o mesmo nível de distância."
        ),
    },
    {
        "key":    "viz_ranking_barras",
        "titulo": "Ranking por Número de Conexões",
        "tipo":   "Explanatória",
        "cor":    "#f59e0b",
        "o_que":  (
            "O gráfico de barras horizontais mostra todos os 20 aeroportos ordenados do mais ao menos "
            "conectado, em ordem decrescente de grau. A cor de cada barra indica a região geográfica "
            "a que pertence. Os valores de grau são anotados ao final de cada barra para leitura direta."
        ),
        "insight": (
            "GRU domina isoladamente com grau 7, um valor 40% superior ao segundo colocado (REC e MAO, grau 5). "
            "As três primeiras posições pertencem a regiões diferentes (Sudeste, Nordeste e Norte), revelando "
            "que a rede não concentra sua hierarquia em uma única região. Os seis aeroportos com grau 1 formam "
            "um cluster periférico claramente identificável, evidenciando que mais de 30% dos aeroportos são nós folha."
        ),
        "por_que": (
            "O ranking em barras horizontais é uma visualização explanatória por excelência: comunica "
            "hierarquia de forma imediata. A lei da continuidade é aplicada pela ordenação decrescente; "
            "a lei da similaridade pela cor regional. O uso de cor como segunda dimensão informacional "
            "comunica duas variáveis (grau e região) em uma única visualização."
        ),
    },
    {
        "key":    "viz_hubs_vs_comuns",
        "titulo": "Hubs vs Aeroportos Comuns",
        "tipo":   "Explanatória",
        "cor":    "#f59e0b",
        "o_que":  (
            "O gráfico de barras agrupadas compara os 5 hubs regionais (REC, GRU, POA, BSB e MAO) "
            "com os 15 aeroportos comuns em duas métricas: grau médio e densidade ego média."
        ),
        "insight": (
            "Hubs e aeroportos comuns diferem em ambas as métricas, mas em sentidos opostos. "
            "Os hubs têm grau médio de 5,0 contra 1,8 dos comuns. O dado contraintuitivo é a "
            "densidade ego: hubs (0,43) têm densidade local menor do que os comuns (0,80). "
            "Isso significa que os hubs conectam aeroportos que não se ligam diretamente entre si — "
            "eles funcionam como pontes estruturais, não como membros de grupos coesos."
        ),
        "por_que": (
            "Barras agrupadas permitem comparar duas métricas entre duas categorias em uma única figura, "
            "aplicando a lei da proximidade. A lei da similaridade é aplicada pela cor: azul representa "
            "sempre grau médio e laranja representa sempre densidade ego, criando uma codificação visual consistente."
        ),
    },
    {
        "key":    "viz_custo_rotas",
        "titulo": "Custo das Rotas (Dijkstra)",
        "tipo":   "Adicional",
        "cor":    "#6b7280",
        "o_que":  (
            "O gráfico de barras verticais mostra o custo total acumulado de cada par origem-destino "
            "calculado pelo algoritmo de caminho mínimo. As barras estão ordenadas crescentemente pelo "
            "custo, com gradiente de amarelo (menor custo) a vermelho-escuro (maior custo). "
            "O número de escalas é anotado sobre cada barra."
        ),
        "insight": (
            "REC → POA é a rota de menor custo (1,5, sem escalas) por ser uma conexão direta entre dois "
            "hubs regionais. BEL → CGH é a rota de maior custo (6,5, 4 escalas), exigindo passagem por "
            "MAO, BSB, GRU e CNF, evidenciando a posição periférica de Belém. O custo não depende apenas "
            "da distância geográfica, mas da posição do aeroporto na hierarquia da rede."
        ),
        "por_que": (
            "Barras verticais com gradiente de cor aplicam o princípio de pregnância: a associação de "
            "amarelo com barato e vermelho com caro é culturalmente consolidada. A anotação do número de "
            "escalas sobre cada barra adiciona uma segunda variável informacional sem introduzir um eixo extra."
        ),
    },
    {
        "key":    "viz_densidade_ego",
        "titulo": "Densidade da Ego-Network",
        "tipo":   "Adicional",
        "cor":    "#6b7280",
        "o_que":  (
            "O gráfico de barras horizontais mostra a densidade ego-network de cada aeroporto, "
            "calculada sobre o subgrafo induzido por v ∪ vizinhança de v, ordenada de forma decrescente. "
            "A densidade ego mede a proporção de conexões existentes entre o aeroporto e seus vizinhos "
            "em relação ao máximo possível."
        ),
        "insight": (
            "Aeroportos com grau 1 possuem densidade ego igual a 1,0, formando trivialmente um subgrafo "
            "completo com seu único vizinho. O padrão mais rico está na faixa intermediária: hubs como "
            "GRU (0,36) e MAO (0,33) têm as menores densidades ego da rede, confirmando que eles conectam "
            "aeroportos que não se conectam entre si — seu papel estrutural é de ponte, não de núcleo coeso."
        ),
        "por_que": (
            "Barras horizontais permitem rótulos legíveis com os 20 aeroportos simultaneamente. "
            "A lei da continuidade é aplicada pela ordenação decrescente, criando uma narrativa visual "
            "dos aeroportos de maior densidade local (periféricos) aos de menor densidade (hubs). "
            "O eixo horizontal vai de 0 a 1, a escala natural da densidade."
        ),
    },
    {
        "key":    "viz_regioes_barras",
        "titulo": "Métricas Comparadas por Região",
        "tipo":   "Adicional",
        "cor":    "#6b7280",
        "o_que":  (
            "O gráfico de barras agrupadas compara três métricas do subgrafo induzido de cada região: "
            "ordem (número de aeroportos), tamanho (número de conexões internas) e densidade "
            "(proporção de conexões existentes sobre o máximo possível)."
        ),
        "insight": (
            "O Centro-Oeste apresenta o caso extremo positivo: com apenas 2 aeroportos diretamente "
            "conectados, o subgrafo tem densidade máxima de 1,0. O Nordeste apresenta o caso oposto: "
            "maior número de aeroportos (6) mas menor densidade (0,27), pois as conexões internas são "
            "escassas e concentradas no hub REC. A relação inversa entre ordem e densidade aparece em quase todas as regiões."
        ),
        "por_que": (
            "Barras agrupadas são o tipo adequado para comparar múltiplas métricas entre categorias discretas. "
            "A lei da proximidade agrupa as três barras de cada região. A lei da similaridade mantém cores "
            "consistentes entre as séries: azul (ordem), verde (tamanho) e laranja (densidade)."
        ),
    },
    {
        "key":    "viz_pizza_regioes",
        "titulo": "Proporção de Aeroportos por Região",
        "tipo":   "Adicional",
        "cor":    "#6b7280",
        "o_que":  (
            "O gráfico de pizza mostra a distribuição percentual dos 20 aeroportos da rede entre as "
            "5 regiões geográficas do Brasil. Cada fatia representa uma região, com percentual e nome "
            "anotados diretamente sobre o gráfico."
        ),
        "insight": (
            "O Nordeste concentra 30% dos aeroportos da rede (6 de 20), seguido pelo Sudeste com 25% "
            "(5 aeroportos) e Norte com 20% (4 aeroportos). O Centro-Oeste é a região menos representada "
            "com 10% (2 aeroportos). Apesar de ser a região mais representada, o Nordeste apresenta a "
            "menor densidade interna (0,27), enquanto o Centro-Oeste, com menos aeroportos, tem densidade máxima."
        ),
        "por_que": (
            "O gráfico de pizza é adequado quando o número de categorias é pequeno e o objetivo é mostrar "
            "a proporção de cada categoria em relação ao todo. A consistência de cores com todas as outras "
            "visualizações cria um código visual persistente que permite ao leitor identificar regiões instantaneamente."
        ),
    },
]


def _encode_img(path: Path) -> str:
    """Retorna string data URI base64 de um PNG, ou string vazia se não existir."""
    if not path.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def _build_viz_data_js(out_dir: Path) -> str:
    """Monta o array JS VIZ_DATA com imagens embutidas e descrições."""
    parts = ["const VIZ_DATA = ["]
    for d in VIZ_DESCRIPTIONS:
        img = _encode_img(out_dir / f"{d['key']}.png")
        # Escapa aspas simples nos textos para não quebrar a string JS
        def esc(s: str) -> str:
            return s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ")
        parts.append(
            f"  {{titulo:'{esc(d['titulo'])}',tipo:'{esc(d['tipo'])}',tipoCor:'{d['cor']}',"
            f"img:'{img}',"
            f"oQue:'{esc(d['o_que'])}',"
            f"insight:'{esc(d['insight'])}',"
            f"porQue:'{esc(d['por_que'])}'"
            f"}},"
        )
    parts.append("];")
    return "\n".join(parts)


def viz_grafo_interativo(g: Graph, out_path: Path) -> None:
    from collections import deque

    rotas_info = {}
    for (orig, dest), color in zip(ROTAS_OBRIGATORIAS, ROUTE_COLORS):
        custo, caminho = dijkstra_path(g, orig, dest)
        rotas_info[(orig, dest)] = {"custo": custo, "caminho": caminho, "color": color}

    nos_em_rota: dict[str, str] = {}
    arestas_em_rota: dict[frozenset, str] = {}
    for info in rotas_info.values():
        if info["caminho"]:
            for node in info["caminho"]:
                nos_em_rota[node] = info["color"]
            for i in range(len(info["caminho"]) - 1):
                key = frozenset([info["caminho"][i], info["caminho"][i+1]])
                arestas_em_rota[key] = info["color"]

    REGIAO_CORES_VIZ = {
        "Nordeste":     "#e67e22",
        "Sudeste":      "#1a6fa8",
        "Sul":          "#27ae60",
        "Centro-Oeste": "#8e44ad",
        "Norte":        "#c0392b",
    }

    bfs_start = "GRU"
    bfs_layer: dict[str, int] = {}
    visited_bfs = {bfs_start}
    q = deque([(bfs_start, 0)])
    while q:
        node, layer = q.popleft()
        bfs_layer[node] = layer
        for nb in g.neighbors(node):
            if nb not in visited_bfs:
                visited_bfs.add(nb)
                q.append((nb, layer + 1))

    global_ordem   = g.order
    global_tamanho = g.size
    global_density = round(g.density(), 4)
    grau_medio     = round(sum(g.degree(n) for n in g.nodes) / g.order, 2)

    from collections import defaultdict
    regioes_nos: dict[str, list] = defaultdict(list)
    for node in g.nodes:
        r = g.node_meta[node].get("regiao", "?")
        regioes_nos[r].append(node)

    regioes_metricas = {}
    for r, nos in sorted(regioes_nos.items()):
        sub = g.induced_subgraph(set(nos))
        regioes_metricas[r] = {"ordem": sub.order, "tamanho": sub.size, "densidade": round(sub.density(), 4)}

    nodes_js = []
    for node in g.nodes:
        meta   = g.node_meta.get(node, {})
        regiao = meta.get("regiao", "")
        cidade = meta.get("cidade", "")
        grau   = g.degree(node)
        d_ego  = round(g.ego_network(node).density(), 4)
        is_hub = node in HUBS
        color  = nos_em_rota.get(node, REGIAO_CORES_VIZ.get(regiao, "#95a5a6"))
        size   = 30 if is_hub else 18
        star   = "⭐" if is_hub else ""
        label  = f"{star}{node}\\n{cidade}"
        layer  = bfs_layer.get(node, "?")
        title  = (f"<b>{node} — {cidade}</b><br>"
                  f"Região: {regiao}<br>Grau: {grau}<br>"
                  f"Densidade ego: {d_ego}<br>"
                  f"Camada BFS (GRU): {layer}<br>"
                  f"{'⭐ Hub regional' if is_hub else 'Aeroporto comum'}")
        border = "white" if node in nos_em_rota else "#888"
        nodes_js.append(
            f'{{id:"{node}",label:"{label}",title:"{title}",'
            f'regiao:"{regiao}",isHub:{"true" if is_hub else "false"},'
            f'bfsLayer:{bfs_layer.get(node, 99)},'
            f'color:{{background:"{color}",border:"{border}"}},'
            f'size:{size},font:{{size:{13 if is_hub else 10},color:"white",bold:{"true" if is_hub else "false"}}}}}'
        )

    edges_js = []
    added: set[frozenset] = set()
    eid = 0
    for edge in g.edges:
        key = frozenset([edge.origem, edge.destino])
        if key in added:
            continue
        added.add(key)
        in_rota = key in arestas_em_rota
        color   = arestas_em_rota[key] if in_rota else "#555577"
        width   = 4 if in_rota else 1.5
        title   = f"peso={edge.peso} | {edge.tipo_conexao}"
        edges_js.append(
            f'{{id:{eid},from:"{edge.origem}",to:"{edge.destino}",'
            f'color:{{color:"{color}"}},width:{width},'
            f'title:"{title}",dashes:{"false" if in_rota else "true"}}}'
        )
        eid += 1

    nodes_str = "[" + ",\n".join(nodes_js) + "]"
    edges_str = "[" + ",\n".join(edges_js) + "]"

    original_nodes = []
    for node in g.nodes:
        meta   = g.node_meta.get(node, {})
        regiao = meta.get("regiao", "")
        color  = nos_em_rota.get(node, REGIAO_CORES_VIZ.get(regiao, "#95a5a6"))
        border = "white" if node in nos_em_rota else "#888"
        original_nodes.append(f'"{node}":{{background:"{color}",border:"{border}"}}')
    original_nodes_str = "{" + ",".join(original_nodes) + "}"

    original_edges = []
    added2: set[frozenset] = set()
    eid2 = 0
    for edge in g.edges:
        key = frozenset([edge.origem, edge.destino])
        if key in added2:
            eid2 += 1
            continue
        added2.add(key)
        in_rota = key in arestas_em_rota
        color   = arestas_em_rota[key] if in_rota else "#555577"
        width   = 4 if in_rota else 1.5
        original_edges.append(f'{eid2}:{{color:"{color}",width:{width}}}')
        eid2 += 1
    original_edges_str = "{" + ",".join(original_edges) + "}"

    regioes_js_parts = []
    for r, m in regioes_metricas.items():
        cor = REGIAO_CORES_VIZ.get(r, "#95a5a6")
        regioes_js_parts.append(
            f'"{r}":{{cor:"{cor}",ordem:{m["ordem"]},tamanho:{m["tamanho"]},densidade:{m["densidade"]}}}'
        )
    regioes_js_str = "{" + ",".join(regioes_js_parts) + "}"

    viz_data_js = _build_viz_data_js(out_path.parent)

    # Gera itens HTML da sidebar dinamicamente
    sidebar_items = ""
    for d in VIZ_DESCRIPTIONS:
        sidebar_items += (
            f'<div class="viz-item" onclick="abrirViz({VIZ_DESCRIPTIONS.index(d)})">'
            f'<div class="viz-item-titulo">{d["titulo"]}</div>'
            f'<span class="viz-badge" style="background:{d["cor"]}">{d["tipo"]}</span>'
            f'</div>\n  '
        )

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Rede de Aeroportos do Brasil</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#1a1a2e; font-family:'Segoe UI',sans-serif; overflow:hidden; display:flex; }}

  /* ── Grafo ocupa o espaço central ── */
  #grafo {{ flex:1; height:100vh; min-width:0; }}

  /* ── Painel esquerdo (controles) ── */
  #painel {{
    position:fixed; top:12px; left:12px; z-index:999;
    background:rgba(15,15,35,0.97); border-radius:12px;
    padding:14px 16px; color:white; width:250px;
    border:1px solid #333; max-height:calc(100vh - 24px);
    overflow-y:auto;
  }}
  #painel h3 {{ margin:0 0 10px; font-size:14px; color:#f1c40f; }}
  .rota-btn {{
    display:block; width:100%; margin:3px 0;
    padding:7px 10px; border:none; border-radius:6px;
    cursor:pointer; font-size:11px; font-weight:bold; color:white; text-align:left;
  }}
  .rota-btn:hover {{ opacity:0.85; }}
  .regiao-btn {{
    display:inline-flex; align-items:center; gap:5px;
    padding:4px 8px; border:none; border-radius:5px;
    cursor:pointer; font-size:11px; color:white;
    margin:2px; font-weight:bold;
  }}
  .regiao-btn.inactive {{ opacity:0.35; }}
  .legenda-item {{ display:flex; align-items:center; gap:8px; font-size:11px; margin:2px 0; }}
  .dot {{ width:11px; height:11px; border-radius:50%; flex-shrink:0; }}
  .sep {{ border-top:1px solid #333; margin:8px 0; }}
  #busca {{
    width:100%; padding:6px 8px; border-radius:6px;
    border:1px solid #555; background:#2a2a4a;
    color:white; font-size:12px; margin-bottom:6px;
  }}
  #busca::placeholder {{ color:#888; }}
  .metrica-box {{
    background:#1e1e3a; border-radius:7px; padding:8px 10px; margin:4px 0;
    font-size:11px;
  }}
  .metrica-box b {{ color:#f1c40f; font-size:12px; }}
  .metrica-row {{ display:flex; justify-content:space-between; margin:2px 0; }}
  .metrica-val {{ color:#7ec8e3; font-weight:bold; }}
  #info-regiao {{ display:none; }}
  .section-title {{ font-size:11px; font-weight:bold; color:#aaa; margin:6px 0 4px; text-transform:uppercase; letter-spacing:0.5px; }}
  #bfs-slider-wrap {{ margin:4px 0; }}
  #bfs-slider {{ width:100%; accent-color:#f1c40f; }}
  #bfs-label {{ font-size:11px; color:#aaa; }}

  /* ── Coluna direita: visualizações ── */
  #viz-sidebar {{
    width:210px;
    flex-shrink:0;
    background:rgba(15,15,35,0.97);
    border-left:1px solid #2a2a4a;
    height:100vh;
    overflow-y:auto;
    padding:14px 12px;
    display:flex;
    flex-direction:column;
    gap:6px;
    z-index:998;
  }}
  #viz-sidebar h3 {{
    font-size:13px; color:#f1c40f; margin:0 0 10px;
  }}
  .viz-item {{
    background:#1e1e3a;
    border:1px solid #2d2d50;
    border-radius:8px;
    padding:10px 10px 8px;
    cursor:pointer;
    transition:all .18s;
    display:flex;
    flex-direction:column;
    gap:5px;
  }}
  .viz-item:hover {{
    background:#2a2a50;
    border-color:#f1c40f55;
    transform:translateX(-2px);
    box-shadow:2px 0 12px rgba(241,196,15,.12);
  }}
  .viz-item-titulo {{
    font-size:11px;
    font-weight:600;
    color:#e2e8f0;
    line-height:1.35;
  }}
  .viz-badge {{
    font-size:9px;
    font-weight:700;
    padding:2px 6px;
    border-radius:20px;
    color:white;
    align-self:flex-start;
    letter-spacing:.3px;
    text-transform:uppercase;
  }}

  /* ── Overlay / popup ── */
  #viz-overlay {{
    display:none;
    position:fixed; inset:0; z-index:2000;
    background:rgba(0,0,0,.75);
    backdrop-filter:blur(4px);
    align-items:center;
    justify-content:center;
    padding:20px;
  }}
  #viz-overlay.open {{ display:flex; }}
  #viz-modal {{
    background:#12122a;
    border:1px solid #333;
    border-radius:14px;
    width:min(860px, 95vw);
    max-height:90vh;
    overflow-y:auto;
    display:flex;
    flex-direction:column;
    position:relative;
  }}
  #viz-modal-header {{
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    padding:18px 20px 14px;
    border-bottom:1px solid #2a2a4a;
    gap:12px;
    position:sticky; top:0; background:#12122a; z-index:1;
    border-radius:14px 14px 0 0;
  }}
  #viz-modal-header-left {{
    display:flex;
    flex-direction:column;
    gap:6px;
  }}
  #viz-modal-titulo {{
    font-size:17px;
    font-weight:700;
    color:#f1f5f9;
  }}
  #viz-modal-tipo-badge {{
    font-size:10px;
    font-weight:700;
    padding:3px 9px;
    border-radius:20px;
    color:white;
    align-self:flex-start;
    text-transform:uppercase;
    letter-spacing:.4px;
  }}
  #viz-close {{
    background:#2a2a4a;
    border:1px solid #444;
    color:#aaa;
    width:32px; height:32px;
    border-radius:8px;
    cursor:pointer;
    font-size:18px;
    line-height:1;
    flex-shrink:0;
    display:flex; align-items:center; justify-content:center;
    transition:all .15s;
    margin-top:2px;
  }}
  #viz-close:hover {{ background:#e74c3c; color:white; border-color:#e74c3c; }}
  #viz-modal-body {{
    padding:20px;
    display:flex;
    flex-direction:column;
    gap:18px;
  }}
  #viz-img-wrap {{
    background:#0d0d20;
    border-radius:10px;
    padding:12px;
    border:1px solid #2a2a4a;
    display:flex;
    align-items:center;
    justify-content:center;
  }}
  #viz-img {{
    max-width:100%;
    height:auto;
    border-radius:6px;
    display:block;
  }}
  .viz-section {{
    display:flex;
    flex-direction:column;
    gap:6px;
  }}
  .viz-section-label {{
    font-size:10px;
    font-weight:700;
    text-transform:uppercase;
    letter-spacing:.6px;
    color:#64748b;
  }}
  .viz-section-text {{
    font-size:12.5px;
    color:#cbd5e1;
    line-height:1.65;
  }}
  .viz-insight-box {{
    background:#1e1e3a;
    border-left:3px solid #f1c40f;
    border-radius:0 8px 8px 0;
    padding:12px 14px;
  }}
  .viz-insight-box .viz-section-text {{ color:#e2e8f0; }}

  /* scrollbars */
  #viz-sidebar::-webkit-scrollbar,
  #viz-modal::-webkit-scrollbar,
  #painel::-webkit-scrollbar {{ width:5px; }}
  #viz-sidebar::-webkit-scrollbar-track,
  #viz-modal::-webkit-scrollbar-track,
  #painel::-webkit-scrollbar-track {{ background:transparent; }}
  #viz-sidebar::-webkit-scrollbar-thumb,
  #viz-modal::-webkit-scrollbar-thumb,
  #painel::-webkit-scrollbar-thumb {{ background:#333; border-radius:10px; }}
</style>
</head>
<body>

<!-- Painel de controles (esquerda, fixo) -->
<div id="painel">
  <h3>🛫 Rede de Aeroportos</h3>

  <input id="busca" type="text" placeholder="🔍 Buscar aeroporto (ex: GRU)..." oninput="buscar(this.value)">

  <div class="sep"></div>
  <div class="section-title">Métricas Globais</div>
  <div class="metrica-box">
    <div class="metrica-row"><span>Aeroportos (|V|)</span><span class="metrica-val">{global_ordem}</span></div>
    <div class="metrica-row"><span>Rotas (|E|)</span><span class="metrica-val">{global_tamanho}</span></div>
    <div class="metrica-row"><span>Densidade</span><span class="metrica-val">{global_density}</span></div>
    <div class="metrica-row"><span>Grau médio</span><span class="metrica-val">{grau_medio}</span></div>
  </div>

  <div class="sep"></div>
  <div class="section-title">Filtrar por Região</div>
  <div id="filtro-regioes"></div>
  <div id="info-regiao" class="metrica-box" style="margin-top:6px"></div>
  <button class="rota-btn" style="background:#333;margin-top:4px" onclick="limparFiltroRegiao()">✕ Limpar filtro</button>

  <div class="sep"></div>
  <div class="section-title">Camadas BFS a partir de GRU</div>
  <div id="bfs-slider-wrap">
    <input type="range" id="bfs-slider" min="0" max="3" value="3" oninput="filtrarBFS(this.value)">
    <div id="bfs-label">Mostrando todas as camadas</div>
  </div>
  <button class="rota-btn" style="background:#333;margin-top:2px" onclick="resetarBFS()">✕ Resetar BFS</button>

  <div class="sep"></div>
  <div class="section-title">Caminhos Obrigatórios</div>
  <button class="rota-btn" style="background:#e74c3c" onclick="realcarRota('REC','POA','#e74c3c')">🔴 REC → POA (custo 1.50)</button>
  <button class="rota-btn" style="background:#00b894" onclick="realcarRota('MAO','GRU','#00b894')">🟢 MAO → GRU (custo 3.00)</button>
  <button class="rota-btn" style="background:#444" onclick="resetar()">⚪ Resetar destaque</button>
  <a href="arvore_percurso.html" target="_blank" class="rota-btn" style="background:#2d2d50;border:1px solid #555;margin-top:6px;text-decoration:none;display:block;text-align:left;">🌳 Ver árvore de percurso</a>

  <div class="sep"></div>
  <div class="section-title">Legenda de Regiões</div>
  <div class="legenda-item"><div class="dot" style="background:#e67e22"></div>Nordeste</div>
  <div class="legenda-item"><div class="dot" style="background:#1a6fa8"></div>Sudeste</div>
  <div class="legenda-item"><div class="dot" style="background:#27ae60"></div>Sul</div>
  <div class="legenda-item"><div class="dot" style="background:#8e44ad"></div>Centro-Oeste</div>
  <div class="legenda-item"><div class="dot" style="background:#c0392b"></div>Norte</div>
  <div style="font-size:10px;color:#666;margin-top:6px">⭐ Nós maiores = hubs regionais<br>Hover nos nós para ver detalhes</div>
</div>

<!-- Grafo (centro) -->
<div id="grafo"></div>

<!-- Coluna direita: visualizações -->
<div id="viz-sidebar">
  <h3>📊 Visualizações</h3>
  {sidebar_items}
</div>

<!-- Popup overlay -->
<div id="viz-overlay" onclick="fecharVizOverlay(event)">
  <div id="viz-modal">
    <div id="viz-modal-header">
      <div id="viz-modal-header-left">
        <div id="viz-modal-titulo"></div>
        <span id="viz-modal-tipo-badge"></span>
      </div>
      <button id="viz-close" onclick="fecharViz()">✕</button>
    </div>
    <div id="viz-modal-body">
      <div id="viz-img-wrap">
        <img id="viz-img" src="" alt="Visualização">
      </div>
      <div class="viz-section">
        <div class="viz-section-label">O que está sendo mostrado</div>
        <div class="viz-section-text" id="viz-o-que"></div>
      </div>
      <div class="viz-section viz-insight-box">
        <div class="viz-section-label" style="color:#f1c40faa">💡 Insight</div>
        <div class="viz-section-text" id="viz-insight"></div>
      </div>
      <div class="viz-section">
        <div class="viz-section-label">Por que este tipo de gráfico</div>
        <div class="viz-section-text" id="viz-por-que"></div>
      </div>
    </div>
  </div>
</div>

<script>
{viz_data_js}

function abrirViz(i) {{
  const d = VIZ_DATA[i];
  document.getElementById('viz-modal-titulo').textContent = d.titulo;
  const badge = document.getElementById('viz-modal-tipo-badge');
  badge.textContent = d.tipo;
  badge.style.background = d.tipoCor;
  document.getElementById('viz-img').src = d.img;
  document.getElementById('viz-o-que').textContent = d.oQue;
  document.getElementById('viz-insight').textContent = d.insight;
  document.getElementById('viz-por-que').textContent = d.porQue;
  document.getElementById('viz-overlay').classList.add('open');
  document.getElementById('viz-modal').scrollTop = 0;
}}

function fecharViz() {{
  document.getElementById('viz-overlay').classList.remove('open');
}}

function fecharVizOverlay(e) {{
  if (e.target === document.getElementById('viz-overlay')) fecharViz();
}}

document.addEventListener('keydown', function(e) {{
  if (e.key === 'Escape') fecharViz();
}});
</script>

<script>
const nodesData = {nodes_str};
const edgesData = {edges_str};
const origNodes = {original_nodes_str};
const origEdges = {original_edges_str};
const regioesMeta = {regioes_js_str};

const nodes = new vis.DataSet(nodesData);
const edges = new vis.DataSet(edgesData);
const container = document.getElementById("grafo");
const network = new vis.Network(container, {{nodes, edges}}, {{
  physics: {{
    enabled: true,
    forceAtlas2Based: {{ gravitationalConstant: -50, springLength: 120 }},
    solver: "forceAtlas2Based",
    stabilization: {{ iterations: 200 }}
  }},
  edges: {{ smooth: {{ type: "continuous" }} }},
  interaction: {{ hover: true, navigationButtons: true, keyboard: true }}
}});

const rotas = {{
  "REC-POA": ["REC","POA"],
  "MAO-GRU": ["MAO","BSB","GRU"]
}};

let regiaoAtiva = null;
let bfsModo = false;

// Monta botões de região
const filtroDiv = document.getElementById("filtro-regioes");
Object.entries(regioesMeta).forEach(([r, m]) => {{
  const btn = document.createElement("button");
  btn.className = "regiao-btn";
  btn.id = "btn-regiao-" + r;
  btn.style.background = m.cor;
  btn.textContent = r;
  btn.onclick = () => filtrarRegiao(r);
  filtroDiv.appendChild(btn);
}});

function filtrarRegiao(regiao) {{
  bfsModo = false;
  document.getElementById("busca").value = "";

  if (regiaoAtiva === regiao) {{
    limparFiltroRegiao();
    return;
  }}
  regiaoAtiva = regiao;

  // Atualiza botões
  Object.keys(regioesMeta).forEach(r => {{
    const btn = document.getElementById("btn-regiao-" + r);
    if (btn) btn.className = "regiao-btn" + (r === regiao ? "" : " inactive");
  }});

  // Destaca nós da região
  const nodeUpdates = [];
  nodes.forEach(n => {{
    const match = n.regiao === regiao;
    nodeUpdates.push({{
      id: n.id,
      color: match
        ? {{ background: origNodes[n.id].background, border: "white" }}
        : {{ background: "#1e1e2e", border: "#222" }},
      font: {{ color: match ? "white" : "#333" }}
    }});
  }});
  nodes.update(nodeUpdates);

  // Escurece arestas fora da região
  const edgeUpdates = [];
  edges.forEach(e => {{
    const fromRegiao = nodesData.find(n => n.id === e.from)?.regiao;
    const toRegiao   = nodesData.find(n => n.id === e.to)?.regiao;
    const inRegiao   = fromRegiao === regiao && toRegiao === regiao;
    edgeUpdates.push({{
      id: e.id,
      color: {{ color: inRegiao ? origEdges[e.id].color : "#1e1e2e" }},
      width: inRegiao ? origEdges[e.id].width * 1.5 : 0.3
    }});
  }});
  edges.update(edgeUpdates);

  // Mostra métricas da região
  const m = regioesMeta[regiao];
  const infoDiv = document.getElementById("info-regiao");
  infoDiv.style.display = "block";
  infoDiv.innerHTML = `<b style="color:${{m.cor}}">${{regiao}}</b><br>
    <div class="metrica-row"><span>Aeroportos</span><span class="metrica-val">${{m.ordem}}</span></div>
    <div class="metrica-row"><span>Rotas internas</span><span class="metrica-val">${{m.tamanho}}</span></div>
    <div class="metrica-row"><span>Densidade</span><span class="metrica-val">${{m.densidade}}</span></div>`;
}}

function limparFiltroRegiao() {{
  regiaoAtiva = null;
  Object.keys(regioesMeta).forEach(r => {{
    const btn = document.getElementById("btn-regiao-" + r);
    if (btn) btn.className = "regiao-btn";
  }});
  document.getElementById("info-regiao").style.display = "none";
  resetar();
}}

function filtrarBFS(val) {{
  val = parseInt(val);
  bfsModo = true;
  regiaoAtiva = null;
  document.getElementById("busca").value = "";
  const label = document.getElementById("bfs-label");
  label.textContent = val === 3 ? "Mostrando todas as camadas" : `Camadas 0 a ${{val}} a partir de GRU`;

  const nodeUpdates = [];
  nodes.forEach(n => {{
    const inLayer = n.bfsLayer <= val;
    nodeUpdates.push({{
      id: n.id,
      color: inLayer
        ? {{ background: origNodes[n.id].background, border: "white" }}
        : {{ background: "#1e1e2e", border: "#222" }},
      font: {{ color: inLayer ? "white" : "#333" }}
    }});
  }});
  nodes.update(nodeUpdates);

  const edgeUpdates = [];
  edges.forEach(e => {{
    const fromLayer = nodesData.find(n => n.id === e.from)?.bfsLayer ?? 99;
    const toLayer   = nodesData.find(n => n.id === e.to)?.bfsLayer ?? 99;
    const inLayer   = fromLayer <= val && toLayer <= val;
    edgeUpdates.push({{
      id: e.id,
      color: {{ color: inLayer ? origEdges[e.id].color : "#1e1e2e" }},
      width: inLayer ? origEdges[e.id].width : 0.3
    }});
  }});
  edges.update(edgeUpdates);
}}

function resetarBFS() {{
  bfsModo = false;
  document.getElementById("bfs-slider").value = 3;
  document.getElementById("bfs-label").textContent = "Mostrando todas as camadas";
  resetar();
}}

function buscar(val) {{
  val = val.trim().toUpperCase();
  if (!val) {{ resetar(); return; }}
  bfsModo = false;
  regiaoAtiva = null;
  const updates = [];
  nodes.forEach(n => {{
    const match = n.id.toUpperCase().includes(val) ||
                  n.label.toUpperCase().includes(val);
    updates.push({{
      id: n.id,
      color: match
        ? {{ background: origNodes[n.id].background, border: "white" }}
        : {{ background: "#1e1e2e", border: "#222" }},
      font: {{ color: match ? "white" : "#333" }}
    }});
  }});
  nodes.update(updates);
}}

function realcarRota(orig, dest, cor) {{
  resetar();
  const caminho = rotas[orig + "-" + dest];
  if (!caminho) return;

  const nodeUpdates = [];
  nodes.forEach(n => {{
    const inPath = caminho.includes(n.id);
    nodeUpdates.push({{
      id: n.id,
      color: inPath
        ? {{ background: cor, border: "white" }}
        : {{ background: "#1e1e2e", border: "#222" }},
      font: {{ color: inPath ? "white" : "#333" }}
    }});
  }});
  nodes.update(nodeUpdates);

  const edgeUpdates = [];
  edges.forEach(e => {{
    let inRota = false;
    for (let i = 0; i < caminho.length - 1; i++) {{
      if ((e.from===caminho[i]&&e.to===caminho[i+1]) ||
          (e.to===caminho[i]&&e.from===caminho[i+1])) inRota = true;
    }}
    edgeUpdates.push({{
      id: e.id,
      color: {{ color: inRota ? cor : "#1e1e2e" }},
      width: inRota ? 5 : 0.3
    }});
  }});
  edges.update(edgeUpdates);
}}

function resetar() {{
  document.getElementById("busca").value = "";
  bfsModo = false;
  regiaoAtiva = null;
  document.getElementById("bfs-slider").value = 3;
  document.getElementById("bfs-label").textContent = "Mostrando todas as camadas";
  document.getElementById("info-regiao").style.display = "none";
  Object.keys(regioesMeta).forEach(r => {{
    const btn = document.getElementById("btn-regiao-" + r);
    if (btn) btn.className = "regiao-btn";
  }});

  const nodeUpdates = [];
  nodes.forEach(n => {{
    nodeUpdates.push({{
      id: n.id,
      color: {{ background: origNodes[n.id].background, border: origNodes[n.id].border }},
      font: {{ color: "white" }}
    }});
  }});
  nodes.update(nodeUpdates);

  const edgeUpdates = [];
  edges.forEach(e => {{
    edgeUpdates.push({{
      id: e.id,
      color: {{ color: origEdges[e.id].color }},
      width: origEdges[e.id].width
    }});
  }});
  edges.update(edgeUpdates);
}}
</script>
</body>
</html>"""

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
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

    print("\n[1/9] Grafo interativo com rotas...")
    build_viz(g, ROTAS_OBRIGATORIAS, out_dir / "arvore_percurso.html")

    print("\n[2/9] Histograma de distribuição de graus...")
    viz_histograma_graus(g, out_dir / "viz_graus_hist.png")

    print("\n[3/9] Ranking de aeroportos por grau...")
    viz_ranking_aeroportos(g, out_dir / "viz_ranking_barras.png")

    print("\n[4/9] Comparação de métricas por região...")
    viz_regioes(g, out_dir / "viz_regioes_barras.png")

    print("\n[5/9] Camadas BFS a partir de GRU...")
    viz_bfs_camadas(g, "GRU", out_dir / "viz_bfs_camadas.png")

    print("\n[6/9] Densidade ego-network por aeroporto...")
    viz_densidade_ego(g, out_dir / "viz_densidade_ego.png")

    print("\n[7/9] Custo das rotas (Dijkstra)...")
    viz_custo_rotas(g, rotas_csv, out_dir / "viz_custo_rotas.png")

    print("\n[8/9] Proporção de aeroportos por região...")
    viz_pizza_regioes(g, out_dir / "viz_pizza_regioes.png")

    print("\n[9/9] Hubs vs aeroportos comuns...")
    viz_hubs_vs_comuns(g, out_dir / "viz_hubs_vs_comuns.png")

    print("\n[+] Grafo interativo completo...")
    viz_grafo_interativo(g, out_dir / "grafo_interativo.html")

    print("\nConcluído! Arquivos gerados em out/")


if __name__ == "__main__":
    run()