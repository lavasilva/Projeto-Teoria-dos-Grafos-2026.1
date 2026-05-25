import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from graphs.graph import Graph
from graphs.algorithms import bellman_ford, bellman_ford_path


def make_graph():
    g = Graph()
    for n in ["A", "B", "C", "D", "E"]:
        g.add_node(n)
    g.add_edge("A", "B", peso=1.0)
    g.add_edge("B", "C", peso=2.0)
    g.add_edge("A", "C", peso=5.0)
    g.add_edge("C", "D", peso=1.0)
    g.add_edge("D", "E", peso=3.0)
    return g


def make_real_graph():
    from graphs.io import load_graph
    root = Path(__file__).parent.parent
    return load_graph(
        root / "data" / "aeroportos_data.csv",
        root / "data" / "adjacencias_aeroportos.csv",
    )



def test_bf_custo_minimo():
    g = make_graph()
    dist, _, _ = bellman_ford(g, "A")
    assert dist["C"] == pytest.approx(3.0)


def test_bf_origem_custo_zero():
    g = make_graph()
    dist, _, _ = bellman_ford(g, "A")
    assert dist["A"] == pytest.approx(0.0)


def test_bf_caminho_otimo_a_d():
    g = make_graph()
    custo, path, neg = bellman_ford_path(g, "A", "D")
    assert custo == pytest.approx(4.0)
    assert path == ["A", "B", "C", "D"]
    assert neg is False


def test_bf_mesmo_no():
    g = make_graph()
    custo, path, neg = bellman_ford_path(g, "A", "A")
    assert custo == pytest.approx(0.0)
    assert path == ["A"]
    assert neg is False


def test_bf_no_inexistente_levanta_erro():
    g = make_graph()
    with pytest.raises(ValueError):
        bellman_ford(g, "Z")


def test_bf_sem_caminho_retorna_inf():
    g = Graph()
    for n in ["X", "Y", "Z"]:
        g.add_node(n)
    g.add_edge("X", "Y", peso=1.0)
    custo, path, neg = bellman_ford_path(g, "X", "Z")
    assert custo == float("inf")
    assert path is None


def test_bf_sem_ciclo_negativo_no_grafo_principal():
    g = make_graph()
    _, _, neg = bellman_ford(g, "A")
    assert neg is False


def test_bf_concorda_com_dijkstra():
    from graphs.algorithms import dijkstra_path
    g = make_graph()
    for origem in ["A", "B", "C"]:
        for destino in ["D", "E"]:
            custo_bf, _, _ = bellman_ford_path(g, origem, destino)
            custo_dj, _   = dijkstra_path(g, origem, destino)
            assert custo_bf == pytest.approx(custo_dj), \
                f"Divergência em {origem}->{destino}: BF={custo_bf}, Dijkstra={custo_dj}"



def test_bf_real_mao_gru():
    g = make_real_graph()
    custo, path, neg = bellman_ford_path(g, "MAO", "GRU")
    assert custo == pytest.approx(3.0)
    assert path == ["MAO", "BSB", "GRU"]
    assert neg is False


def test_bf_real_rec_poa():
    g = make_real_graph()
    custo, path, neg = bellman_ford_path(g, "REC", "POA")
    assert custo == pytest.approx(1.5)
    assert path == ["REC", "POA"]
    assert neg is False


def test_bf_real_sem_ciclo_negativo():
    g = make_real_graph()
    _, _, neg = bellman_ford(g, "GRU")
    assert neg is False


def test_bf_real_concorda_dijkstra_todas_rotas():
    from graphs.algorithms import dijkstra_path
    import csv
    g = make_real_graph()
    root = Path(__file__).parent.parent
    with open(root / "data" / "rotas.csv") as f:
        for row in csv.DictReader(f):
            orig, dest = row["origem"].strip(), row["destino"].strip()
            custo_bf, _, _ = bellman_ford_path(g, orig, dest)
            custo_dj, _   = dijkstra_path(g, orig, dest)
            assert custo_bf == pytest.approx(custo_dj), \
                f"{orig}->{dest}: BF={custo_bf}, Dijkstra={custo_dj}"