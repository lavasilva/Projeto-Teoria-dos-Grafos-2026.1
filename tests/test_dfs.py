import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from graphs.graph import Graph
from graphs.algorithms import dfs, dfs_path


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



def test_dfs_visita_todos_nos():
    g = make_graph()
    parent = dfs(g, "A")
    assert set(parent.keys()) == {"A", "B", "C", "D", "E"}


def test_dfs_raiz_sem_pai():
    g = make_graph()
    parent = dfs(g, "A")
    assert parent["A"] is None


def test_dfs_caminho_valido():
    g = make_graph()
    path = dfs_path(g, "A", "D")
    assert path is not None
    assert path[0] == "A"
    assert path[-1] == "D"
    for i in range(len(path) - 1):
        assert g.has_edge(path[i], path[i + 1])


def test_dfs_mesmo_no():
    g = make_graph()
    assert dfs_path(g, "A", "A") == ["A"]


def test_dfs_no_inexistente_levanta_erro():
    g = make_graph()
    with pytest.raises(ValueError):
        dfs(g, "Z")


def test_dfs_sem_caminho_retorna_none():
    g = Graph()
    g.add_node("X")
    g.add_node("Y")
    g.add_node("Z")
    g.add_edge("X", "Y", peso=1.0)
    assert dfs_path(g, "X", "Z") is None


def test_dfs_caminho_a_d_contem_intermediarios():
    g = make_graph()
    path = dfs_path(g, "A", "D")
    assert path == ["A", "B", "C", "D"]


def test_dfs_real_gru_mao_conectados():
    g = make_real_graph()
    path = dfs_path(g, "GRU", "MAO")
    assert path is not None
    assert path[0] == "GRU"
    assert path[-1] == "MAO"


def test_dfs_real_caminho_valido_arestas():
    g = make_real_graph()
    path = dfs_path(g, "REC", "BEL")
    assert path is not None
    for i in range(len(path) - 1):
        assert g.has_edge(path[i], path[i + 1]), \
            f"Aresta inválida no caminho: {path[i]} -> {path[i+1]}"

def _tem_ciclo(g, parent):
    visited = set()
    for node, par in parent.items():
        visited.add(node)
        for nb in g.neighbors(node):
            if nb in visited and nb != par:
                return True
    return False


def test_dfs_detecta_ciclo():
    g = Graph()
    for n in ["A", "B", "C"]:
        g.add_node(n)
    g.add_edge("A", "B", peso=1.0)
    g.add_edge("B", "C", peso=1.0)
    g.add_edge("A", "C", peso=1.0)

    parent = dfs(g, "A")
    assert _tem_ciclo(g, parent) is True


def test_dfs_sem_ciclo_em_arvore():
    g = Graph()
    for n in ["A", "B", "C", "D"]:
        g.add_node(n)
    g.add_edge("A", "B", peso=1.0)
    g.add_edge("B", "C", peso=1.0)
    g.add_edge("C", "D", peso=1.0)

    parent = dfs(g, "A")
    assert _tem_ciclo(g, parent) is False