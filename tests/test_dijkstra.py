import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from graphs.graph import Graph
from graphs.algorithms import dijkstra, dijkstra_path


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



def test_dijkstra_custo_minimo():
    g = make_graph()
    dist, _ = dijkstra(g, "A")
    assert dist["C"] == pytest.approx(3.0)


def test_dijkstra_origem_custo_zero():
    g = make_graph()
    dist, _ = dijkstra(g, "A")
    assert dist["A"] == pytest.approx(0.0)


def test_dijkstra_caminho_otimo_a_d():
    g = make_graph()
    custo, path = dijkstra_path(g, "A", "D")
    assert custo == pytest.approx(4.0)
    assert path == ["A", "B", "C", "D"]


def test_dijkstra_caminho_a_e():
    g = make_graph()
    custo, path = dijkstra_path(g, "A", "E")
    assert custo == pytest.approx(7.0)
    assert path == ["A", "B", "C", "D", "E"]


def test_dijkstra_mesmo_no():
    g = make_graph()
    custo, path = dijkstra_path(g, "A", "A")
    assert custo == pytest.approx(0.0)
    assert path == ["A"]


def test_dijkstra_no_inexistente_levanta_erro():
    g = make_graph()
    with pytest.raises(ValueError):
        dijkstra(g, "Z")


def test_dijkstra_sem_caminho_retorna_inf():
    g = Graph()
    for n in ["X", "Y", "Z"]:
        g.add_node(n)
    g.add_edge("X", "Y", peso=1.0)
    custo, path = dijkstra_path(g, "X", "Z")
    assert custo == float("inf")
    assert path is None


def test_dijkstra_prefere_custo_menor_que_bfs():
    g = make_graph()
    custo, path = dijkstra_path(g, "A", "C")
    assert custo == pytest.approx(3.0)
    assert path == ["A", "B", "C"]



def test_dijkstra_real_mao_gru():
    g = make_real_graph()
    custo, path = dijkstra_path(g, "MAO", "GRU")
    assert custo == pytest.approx(3.0)
    assert path == ["MAO", "BSB", "GRU"]


def test_dijkstra_real_rec_poa():
    g = make_real_graph()
    custo, path = dijkstra_path(g, "REC", "POA")
    assert custo == pytest.approx(1.5)
    assert path == ["REC", "POA"]


def test_dijkstra_real_bel_cgh():
    g = make_real_graph()
    custo, path = dijkstra_path(g, "BEL", "CGH")
    assert custo == pytest.approx(6.5)
    assert path == ["BEL", "MAO", "BSB", "GRU", "CNF", "CGH"]


def test_dijkstra_real_caminho_valido_arestas():
    g = make_real_graph()
    _, path = dijkstra_path(g, "FOR", "BSB")
    assert path is not None
    for i in range(len(path) - 1):
        assert g.has_edge(path[i], path[i + 1]), \
            f"Aresta inválida: {path[i]} -> {path[i+1]}"

def test_dijkstra_recusa_peso_negativo():
    g = Graph()
    for n in ["A", "B", "C"]:
        g.add_node(n)
    g.add_edge("A", "B", peso=-1.0)
    g.add_edge("B", "C", peso=2.0)
    g.add_edge("A", "C", peso=5.0)

    with pytest.raises(ValueError, match="pesos negativos"):
        dijkstra(g, "A")