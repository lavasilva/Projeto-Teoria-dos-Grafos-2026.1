from __future__ import annotations

import argparse
import sys
from pathlib import Path

SRC = Path(__file__).parent
sys.path.insert(0, str(SRC))

ROOT     = SRC.parent
DATA_DIR = ROOT / "data"
OUT_DIR  = ROOT / "out"


def _load(args) -> "graphs.graph.Graph":
    from graphs.io import load_graph
    return load_graph(
        args.airports or DATA_DIR / "aeroportos_data.csv",
        args.adj      or DATA_DIR / "adjacencias_aeroportos.csv",
    )


def _paths(args):
    return dict(
        airports_csv    = Path(args.airports)  if args.airports else None,
        adjacencias_csv = Path(args.adj)       if args.adj      else None,
        rotas_csv       = Path(args.rotas)     if args.rotas    else None,
        out_dir         = Path(args.out)       if args.out      else None,
    )


def cmd_solve(args):
    import solve
    solve.run(**_paths(args))


def cmd_viz(args):
    import viz
    viz.run(**_paths(args))


def cmd_all(args):
    cmd_solve(args)
    cmd_viz(args)


def cmd_rota(args):
    from graphs.algorithms import dijkstra_path

    g = _load(args)

    origem  = args.origem.strip().upper()
    destino = args.destino.strip().upper()

    if origem not in g.adj:
        print(f"Erro: aeroporto '{origem}' não encontrado no grafo.", file=sys.stderr)
        sys.exit(1)
    if destino not in g.adj:
        print(f"Erro: aeroporto '{destino}' não encontrado no grafo.", file=sys.stderr)
        sys.exit(1)

    custo, caminho = dijkstra_path(g, origem, destino)

    if caminho is None:
        print(f"Sem rota entre {origem} e {destino}.")
    else:
        print(f"Rota:  {' -> '.join(caminho)}")
        print(f"Custo: {custo:.2f}")
        print(f"Saltos: {len(caminho) - 1}")


def cmd_info(args):
    g = _load(args)

    iata = args.iata.strip().upper()

    if iata not in g.adj:
        print(f"Erro: aeroporto '{iata}' não encontrado no grafo.", file=sys.stderr)
        sys.exit(1)

    meta  = g.node_meta.get(iata, {})
    grau  = g.degree(iata)
    vizinhos = g.neighbors(iata)
    ego   = g.ego_network(iata)

    print(f"Aeroporto : {iata}")
    print(f"Cidade    : {meta.get('cidade', '—')}")
    print(f"Região    : {meta.get('regiao', '—')}")
    print(f"Grau      : {grau}")
    print(f"Vizinhos  : {', '.join(sorted(vizinhos))}")
    print(f"Ego-rede  : |V|={ego.order}, |E|={ego.size}, "
          f"densidade={ego.density():.4f}")

    print("\nArestas:")
    for edge in sorted(g.adj[iata], key=lambda e: e.other(iata)):
        nb = edge.other(iata)
        print(f"  {iata} <-> {nb}  peso={edge.peso:.1f}  [{edge.tipo_conexao}]"
              f"  {edge.justificativa}")



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="Rede de Aeroportos do Brasil — Teoria dos Grafos 2026.1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--airports", metavar="CSV",
                        help="aeroportos_data.csv (padrão: data/aeroportos_data.csv)")
    parser.add_argument("--adj",      metavar="CSV",
                        help="adjacencias_aeroportos.csv (padrão: data/adjacencias_aeroportos.csv)")
    parser.add_argument("--rotas",    metavar="CSV",
                        help="rotas.csv (padrão: data/rotas.csv)")
    parser.add_argument("--out",      metavar="DIR",
                        help="diretório de saída (padrão: out/)")

    sub = parser.add_subparsers(dest="cmd", metavar="COMANDO")
    sub.required = True

    sub.add_parser("solve", help="calcula métricas e rotas → out/")

    sub.add_parser("viz", help="gera visualizações → out/")

    sub.add_parser("all", help="solve + viz em sequência")

    p_rota = sub.add_parser("rota", help="rota mínima entre dois aeroportos (Dijkstra)")
    p_rota.add_argument("origem",  help="código IATA de origem  (ex.: MAO)")
    p_rota.add_argument("destino", help="código IATA de destino (ex.: GRU)")

    p_info = sub.add_parser("info", help="informações de um aeroporto")
    p_info.add_argument("iata", help="código IATA (ex.: GRU)")

    return parser


def main():
    parser = build_parser()
    args   = parser.parse_args()

    dispatch = {
        "solve": cmd_solve,
        "viz":   cmd_viz,
        "all":   cmd_all,
        "rota":  cmd_rota,
        "info":  cmd_info,
    }
    dispatch[args.cmd](args)


if __name__ == "__main__":
    main()