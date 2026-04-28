from __future__ import annotations
import json
import csv
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from graphs.io import load_graph
from graphs.graph import Graph
from graphs.algorithms import dijkstra_path

ROOT     = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
OUT_DIR  = ROOT / "out"


def compute_global(g: Graph) -> dict:
    return {
        "ordem":     g.order,
        "tamanho":   g.size,
        "densidade": round(g.density(), 6),
    }


def compute_regioes(g: Graph) -> list[dict]:
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
    resultado = []
    for node in sorted(g.nodes):
        ego = g.ego_network(node)
        resultado.append({
            "aeroporto":     node,
            "cidade":        g.node_meta[node].get("cidade", ""),
            "regiao":        g.node_meta[node].get("regiao", ""),
            "grau":          g.degree(node),
            "ordem_ego":     ego.order,
            "tamanho_ego":   ego.size,
            "densidade_ego": round(ego.density(), 6),
        })
    return resultado


def compute_graus(g: Graph) -> list[dict]:
    resultado = [
        {"aeroporto": node, "grau": g.degree(node)}
        for node in g.nodes
    ]
    return sorted(resultado, key=lambda x: x["grau"], reverse=True)


def compute_rotas(g: Graph, rotas_csv: Path) -> list[dict]:
    if not rotas_csv.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {rotas_csv}")

    resultado = []
    with rotas_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            origem  = row["origem"].strip()
            destino = row["destino"].strip()
            custo, caminho = dijkstra_path(g, origem, destino)
            caminho_str = " -> ".join(caminho) if caminho else "sem rota"
            resultado.append({
                "origem":  origem,
                "destino": destino,
                "custo":   round(custo, 4) if custo != float("inf") else "inf",
                "caminho": caminho_str,
            })
            print(f"  {origem} → {destino}: custo={custo:.2f}, "
                  f"caminho={caminho_str}")
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


def save_graus(data: list[dict], out_dir: Path) -> None:
    path = out_dir / "graus.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["aeroporto", "grau"])
        writer.writeheader()
        writer.writerows(data)
    print(f"  ✔ {path}")


def save_rotas(data: list[dict], out_dir: Path) -> None:
    path = out_dir / "distancias_rotas.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["origem", "destino", "custo", "caminho"])
        writer.writeheader()
        writer.writerows(data)
    print(f"  ✔ {path}")


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

    print("\nCalculando graus e rankings...")
    graus_data = compute_graus(g)
    mais_conectado = graus_data[0]
    print(f"  Aeroporto mais conectado: {mais_conectado['aeroporto']} "
          f"(grau={mais_conectado['grau']})")
    maior_densidade_ego = max(ego_data, key=lambda x: x["densidade_ego"])
    print(f"  Maior densidade local:    {maior_densidade_ego['aeroporto']} "
          f"(densidade_ego={maior_densidade_ego['densidade_ego']})")

    print("\nCalculando rotas (Dijkstra)...")
    rotas_data = compute_rotas(g, rotas_csv)

    print("\nSalvando arquivos de saída...")
    save_global(global_data, out_dir)
    save_regioes(regioes_data, out_dir)
    save_ego(ego_data, out_dir)
    save_graus(graus_data, out_dir)
    save_rotas(rotas_data, out_dir)
    print("\nConcluído!")


if __name__ == "__main__":
    run()