import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from graphs.graph import Graph
from graphs.algorithms import bfs, bfs_path


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


def test_bfs_visita_todos_nos():
    g = make_graph()
    parent = bfs(g, "A")
    assert set(parent.keys()) == {"A", "B", "C", "D", "E"}


def test_bfs_raiz_sem_pai():
    g = make_graph()
    parent = bfs(g, "A")
    assert parent["A"] is None


def test_bfs_caminho_mais_curto_em_arestas():
    """BFS minimiza número de arestas, não custo."""
    g = make_graph()
    assert bfs_path(g, "A", "C") == ["A", "C"]


def test_bfs_caminho_simples():
    g = make_graph()
    assert bfs_path(g, "A", "D") == ["A", "C", "D"]


def test_bfs_mesmo_no():
    g = make_graph()
    assert bfs_path(g, "A", "A") == ["A"]


def test_bfs_no_inexistente_levanta_erro():
    g = make_graph()
    with pytest.raises(ValueError):
        bfs(g, "Z")


def test_bfs_sem_caminho_retorna_none():
    g = Graph()
    g.add_node("X")
    g.add_node("Y")
    g.add_node("Z")
    g.add_edge("X", "Y", peso=1.0)
    assert bfs_path(g, "X", "Z") is None



def test_bfs_real_gru_mao():
    g = make_real_graph()
    path = bfs_path(g, "GRU", "MAO")
    assert path is not None
    assert path[0] == "GRU"
    assert path[-1] == "MAO"
    assert len(path) == 3        


def test_bfs_real_rec_poa_direto():
    g = make_real_graph()
    path = bfs_path(g, "REC", "POA")
    assert path == ["REC", "POA"] 