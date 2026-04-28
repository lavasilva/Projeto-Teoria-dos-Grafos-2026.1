"""
solve.py – Métricas globais, por região e ego-networks.

Saídas geradas
--------------
out/global.json         – ordem, tamanho, densidade do grafo completo
out/regioes.json        – métricas por região (subgrafo induzido)
out/ego_aeroportos.csv  – grau, ordem_ego, tamanho_ego, densidade_ego por aeroporto
"""

from __future__ import annotations
import json
import csv
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from graphs.io import load_graph
from graphs.graph import Graph

ROOT    = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
OUT_DIR  = ROOT / "out"


def compute_global(g: Graph) -> dict:
    """Métricas do grafo completo."""
    return {
        "ordem":     g.order,
        "tamanho":   g.size,
        "densidade": round(g.density(), 6),
    }


def compute_regioes(g: Graph) -> list[dict]:
    """Subgrafo induzido por região → ordem, tamanho, densidade."""
    regioes: dict[str, set[str]] = defaultdict(set)
    for node in g.nodes:
        regiao = g.node_meta[node].get("regiao", "Desconhecida")
        regioes[regiao].add(node)

    resultado = []
    for regiao, nos in sorted(regioes.items()):
        sub = g.induced_subgraph(nos)
        resultado.append({
            "regiao":     regiao,
            "aeroportos": sorted(nos),
            "ordem":      sub.order,
            "tamanho":    sub.size,
            "densidade":  round(sub.density(), 6),
        })
    return resultado


def compute_ego(g: Graph) -> list[dict]:
    """Ego-network {v} ∪ N(v) para cada aeroporto."""
    resultado = []
    for node in sorted(g.nodes):
        ego = g.ego_network(node)
        resultado.append({
            "aeroporto":    node,
            "cidade":       g.node_meta[node].get("cidade", ""),
            "regiao":       g.node_meta[node].get("regiao", ""),
            "grau":         g.degree(node),
            "ordem_ego":    ego.order,
            "tamanho_ego":  ego.size,
            "densidade_ego": round(ego.density(), 6),
        })
    return resultado


def save_global(data: dict, out_dir: Path) -> None:
    path = out_dir / "global.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✔ {path}")


def save_regioes(data: list[dict], out_dir: Path) -> None:
    path = out_dir / "regioes.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✔ {path}")


def save_ego(data: list[dict], out_dir: Path) -> None:
    path = out_dir / "ego_aeroportos.csv"
    fieldnames = ["aeroporto", "cidade", "regiao",
                  "grau", "ordem_ego", "tamanho_ego", "densidade_ego"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"  ✔ {path}")


def run(
    airports_csv:    Path | None = None,
    adjacencias_csv: Path | None = None,
    out_dir:         Path | None = None,
) -> None:
    airports_csv    = airports_csv    or DATA_DIR / "aeroportos_data.csv"
    adjacencias_csv = adjacencias_csv or DATA_DIR / "adjacencias_aeroportos.csv"
    out_dir         = out_dir         or OUT_DIR

    out_dir.mkdir(parents=True, exist_ok=True)

    print("Carregando grafo...")
    g = load_graph(airports_csv, adjacencias_csv)
    print(f"  {g}")

    print("\nCalculando métricas globais...")
    global_data = compute_global(g)
    print(f"  ordem={global_data['ordem']}, tamanho={global_data['tamanho']}, "
          f"densidade={global_data['densidade']:.4f}")

    print("\nCalculando métricas por região...")
    regioes_data = compute_regioes(g)
    for r in regioes_data:
        print(f"  {r['regiao']}: |V|={r['ordem']}, |E|={r['tamanho']}, "
              f"d={r['densidade']:.4f}")

    print("\nCalculando ego-networks...")
    ego_data = compute_ego(g)
    for e in ego_data:
        print(f"  {e['aeroporto']}: grau={e['grau']}, "
              f"|V|_ego={e['ordem_ego']}, |E|_ego={e['tamanho_ego']}, "
              f"d_ego={e['densidade_ego']:.4f}")

    print("\nSalvando arquivos de saída...")
    save_global(global_data, out_dir)
    save_regioes(regioes_data, out_dir)
    save_ego(ego_data, out_dir)
    print("\nConcluído!")


if __name__ == "__main__":
    run()