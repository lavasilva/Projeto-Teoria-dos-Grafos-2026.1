from __future__ import annotations
import csv
from pathlib import Path

from graphs.graph import Graph


def load_graph(
    airports_csv: str | Path,
    adjacencias_csv: str | Path,
) -> Graph:
    airports_csv    = Path(airports_csv)
    adjacencias_csv = Path(adjacencias_csv)

    for p in (airports_csv, adjacencias_csv):
        if not p.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {p}")

    g = Graph()

    required_node_cols = {"iata", "cidade", "regiao"}
    with airports_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = required_node_cols - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{airports_csv.name}: colunas faltando: {missing}")
        for row in reader:
            iata = row["iata"].strip()
            if not iata:
                continue
            g.add_node(iata, cidade=row["cidade"].strip(),
                       regiao=row["regiao"].strip())

    required_edge_cols = {"origem", "destino", "tipo_conexao", "justificativa", "peso"}
    with adjacencias_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = required_edge_cols - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{adjacencias_csv.name}: colunas faltando: {missing}")
        for i, row in enumerate(reader, start=2):
            origem  = row["origem"].strip()
            destino = row["destino"].strip()
            try:
                peso = float(row["peso"])
            except ValueError:
                raise ValueError(
                    f"{adjacencias_csv.name} linha {i}: peso inválido: {row['peso']!r}"
                )
            g.add_edge(
                origem=origem,
                destino=destino,
                peso=peso,
                tipo_conexao=row["tipo_conexao"].strip(),
                justificativa=row["justificativa"].strip(),
            )

    _validate(g, airports_csv.name)
    return g


def _validate(g: Graph, source: str) -> None:
    """Verifica que o grafo tem nós e é conectado (BFS)."""
    if g.order == 0:
        raise ValueError(f"{source}: grafo sem nós.")

    start   = g.nodes[0]
    visited = {start}
    queue   = [start]
    while queue:
        node = queue.pop(0)
        for nb in g.neighbors(node):
            if nb not in visited:
                visited.add(nb)
                queue.append(nb)

    isolated = set(g.nodes) - visited
    if isolated:
        raise ValueError(
            f"Grafo desconectado! Nós não alcançáveis a partir de {start!r}: {isolated}"
        )