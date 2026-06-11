import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Grafos - CLI Parte 2")
    parser.add_argument("--dataset", required=True, help="Caminho para o diretório do dataset")
    parser.add_argument("--alg", default=None, choices=["BFS", "DFS", "DIJKSTRA", "BF", "ALL"], help="Algoritmo a executar")
    parser.add_argument("--source", default=None, help="Nó de origem")
    parser.add_argument("--target", default=None, help="Nó de destino")
    parser.add_argument("--out", default="./out", help="Diretório de saída")
    args = parser.parse_args()

    if not os.path.isdir(args.dataset):
        print(f"Erro: --dataset '{args.dataset}' não é um diretório válido.")
        sys.exit(1)

    os.makedirs(args.out, exist_ok=True)

    if "parte2" in args.dataset.lower() or args.dataset.endswith("dataset_parte2") or args.dataset.endswith("dataset_parte2/"):
        from src.runner_parte2 import run_parte2
        run_parte2(args.dataset, args.out, alg=args.alg, source=args.source, target=args.target)
    else:
        print("Detectado dataset da Parte 1. Use o runner da Parte 1.")
        sys.exit(1)


if __name__ == "__main__":
    main()
