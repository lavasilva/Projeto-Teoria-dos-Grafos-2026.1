from __future__ import annotations
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent))

from graphs.io import load_graph
from graphs.graph import Graph
from graphs.algorithms import dijkstra_path

try:
    from pyvis.network import Network
except ImportError:
    raise ImportError("Instale pyvis: pip3 install pyvis")

ROOT     = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
OUT_DIR  = ROOT / "out"

ROTAS_OBRIGATORIAS = [
    ("REC", "POA"),  
    ("MAO", "GRU"),  
]

ROUTE_COLORS = ["#e74c3c", "#2980b9"]  
NODE_DEFAULT  = "#95a5a6"              
EDGE_DEFAULT  = "#dfe6e9"             


def build_viz(g: Graph, rotas: list[tuple[str, str]], out_path: Path) -> None:
    net = Network(
        height="750px",
        width="100%",
        bgcolor="#1e1e2e",
        font_color="white",
        directed=True,
    )
    net.set_options("""
    {
      "physics": {
        "enabled": true,
        "stabilization": { "iterations": 150 }
      },
      "edges": {
        "smooth": { "type": "curvedCW", "roundness": 0.1 }
      }
    }
    """)

    for node in g.nodes:
        meta  = g.node_meta.get(node, {})
        label = f"{node}\n{meta.get('cidade','')}"
        net.add_node(
            node,
            label=label,
            color=NODE_DEFAULT,
            size=18,
            font={"size": 11, "color": "white"},
            title=f"{meta.get('cidade','')} ({meta.get('regiao','')})",
        )

    added_edges: set[frozenset] = set()
    for edge in g.edges:
        key = frozenset([edge.origem, edge.destino])
        if key not in added_edges:
            net.add_edge(
                edge.origem, edge.destino,
                color=EDGE_DEFAULT,
                width=1,
                title=f"peso={edge.peso}",
            )
            added_edges.add(key)

    for (origem, destino), color in zip(rotas, ROUTE_COLORS):
        custo, caminho = dijkstra_path(g, origem, destino)
        if caminho is None:
            print(f"  ⚠ Sem rota: {origem} → {destino}")
            continue

        label_rota = f"{origem}→{destino} (custo={custo:.2f})"
        print(f"  {label_rota}: {' -> '.join(caminho)}")

        for node in caminho:
            net.get_node(node)["color"]      = color
            net.get_node(node)["size"]        = 28
            net.get_node(node)["borderWidth"] = 3
            net.get_node(node)["font"]        = {"size": 13, "color": "white", "bold": True}

        for i in range(len(caminho) - 1):
            u, v = caminho[i], caminho[i + 1]
            net.add_edge(
                u, v,
                color=color,
                width=5,
                title=label_rota,
                label=str(i + 1),
                font={"size": 10, "color": color, "strokeWidth": 0},
                arrows="to",
            )

    for i, ((orig, dest), color) in enumerate(zip(rotas, ROUTE_COLORS)):
        custo, caminho = dijkstra_path(g, orig, dest)
        custo_str = f"{custo:.2f}" if caminho else "N/A"
        net.add_node(
            f"__leg_{i}__",
            label=f"● {orig}→{dest}\n  custo={custo_str}",
            color=color,
            shape="box",
            x=-600,
            y=-300 + i * 80,
            physics=False,
            font={"size": 12, "color": "white"},
            size=20,
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    net.save_graph(str(out_path))
    print(f"  ✔ {out_path}")


def run(
    airports_csv:    Path | None = None,
    adjacencias_csv: Path | None = None,
    out_dir:         Path | None = None,
) -> None:
    airports_csv    = airports_csv    or DATA_DIR / "aeroportos_data.csv"
    adjacencias_csv = adjacencias_csv or DATA_DIR / "adjacencias_aeroportos.csv"
    out_dir         = out_dir         or OUT_DIR

    print("Carregando grafo...")
    g = load_graph(airports_csv, adjacencias_csv)
    print(f"  {g}")

    print("\nGerando visualização dos caminhos...")
    build_viz(g, ROTAS_OBRIGATORIAS, out_dir / "arvore_percurso.html")
    print("\nConcluído!")


if __name__ == "__main__":
    run()