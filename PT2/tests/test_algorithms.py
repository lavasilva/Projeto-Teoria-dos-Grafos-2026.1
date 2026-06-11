import pytest
from src.graph import Graph
from src.bfs_dfs import bfs, dfs
from src.dijkstra import dijkstra, reconstruct_path
from src.bellman_ford import bellman_ford, reconstruct_path_bf


def make_simple_graph():
    g = Graph(directed=False)
    for u, v, w in [("A", "B", 1), ("A", "C", 4), ("B", "C", 2), ("B", "D", 5), ("C", "D", 1)]:
        g.add_edge(u, v, w)
    return g


def make_cyclic_graph():
    g = Graph(directed=True)
    for u, v, w in [("A", "B", 1), ("B", "C", 1), ("C", "A", 1), ("C", "D", 2)]:
        g.add_edge(u, v, w)
    return g


def make_negative_graph():
    g = Graph(directed=True)
    for u, v, w in [("A", "B", 4), ("A", "C", 2), ("B", "D", 3), ("C", "B", -1), ("C", "D", 5)]:
        g.add_edge(u, v, w)
    return g


def make_negative_cycle_graph():
    g = Graph(directed=True)
    for u, v, w in [("A", "B", 1), ("B", "C", -3), ("C", "A", 1), ("A", "D", 10)]:
        g.add_edge(u, v, w)
    return g


class TestBFS:
    def test_layers_correct(self):
        g = make_simple_graph()
        result = bfs(g, "A")
        assert result["layers"][0] == ["A"]
        assert set(result["layers"][1]) == {"B", "C"}

    def test_visited_all_connected(self):
        g = make_simple_graph()
        result = bfs(g, "A")
        assert result["visited_count"] == 4

    def test_disconnected_graph(self):
        g = Graph(directed=False)
        g.add_edge("A", "B", 1)
        g.add_edge("C", "D", 1)
        result = bfs(g, "A")
        assert result["visited_count"] == 2

    def test_single_node(self):
        g = Graph(directed=False)
        g.add_node("X")
        result = bfs(g, "X")
        assert result["visited_count"] == 1
        assert result["layers"][0] == ["X"]


class TestDFS:
    def test_detects_cycle(self):
        g = make_cyclic_graph()
        result = dfs(g, "A")
        assert result["has_cycle"] is True

    def test_no_cycle_in_dag(self):
        g = Graph(directed=True)
        g.add_edge("A", "B", 1)
        g.add_edge("B", "C", 1)
        g.add_edge("A", "C", 1)
        result = dfs(g, "A")
        assert result["has_cycle"] is False

    def test_back_edges_present_in_cycle(self):
        g = make_cyclic_graph()
        result = dfs(g, "A")
        assert "back" in result["edge_classes"].values()

    def test_all_nodes_visited_connected(self):
        g = make_simple_graph()
        result = dfs(g, "A")
        assert result["visited_count"] == 4

    def test_tree_edges_exist(self):
        g = make_simple_graph()
        result = dfs(g, "A")
        assert "tree" in result["edge_classes"].values()


class TestDijkstra:
    def test_shortest_path_correct(self):
        g = make_simple_graph()
        result = dijkstra(g, "A")
        assert result["dist"]["D"] == pytest.approx(4.0)

    def test_path_reconstruction(self):
        g = make_simple_graph()
        result = dijkstra(g, "A")
        path = reconstruct_path(result["parent"], "A", "D")
        assert path is not None
        assert path[0] == "A"
        assert path[-1] == "D"

    def test_rejects_negative_weights(self):
        g = Graph(directed=True)
        g.add_edge("A", "B", -1)
        with pytest.raises(ValueError):
            dijkstra(g, "A")

    def test_zero_weight_accepted(self):
        g = Graph(directed=True)
        g.add_edge("A", "B", 0)
        result = dijkstra(g, "A")
        assert result["dist"]["B"] == pytest.approx(0.0)

    def test_unreachable_node(self):
        g = Graph(directed=True)
        g.add_edge("A", "B", 1)
        g.add_node("C")
        result = dijkstra(g, "A")
        assert result["dist"]["C"] == float("inf")


class TestBellmanFord:
    def test_negative_weights_no_cycle(self):
        g = make_negative_graph()
        result = bellman_ford(g, "A")
        assert result["has_negative_cycle"] is False
        assert result["dist"]["B"] == pytest.approx(1.0)
        assert result["dist"]["D"] == pytest.approx(4.0)

    def test_detects_negative_cycle(self):
        g = make_negative_cycle_graph()
        result = bellman_ford(g, "A")
        assert result["has_negative_cycle"] is True

    def test_path_reconstruction_negative_weights(self):
        g = make_negative_graph()
        result = bellman_ford(g, "A")
        path = reconstruct_path_bf(result["parent"], "A", "D")
        assert path is not None
        assert path[0] == "A"
        assert path[-1] == "D"

    def test_normal_weights_correct(self):
        g = make_simple_graph()
        result = bellman_ford(g, "A")
        assert result["has_negative_cycle"] is False
        assert result["dist"]["D"] == pytest.approx(4.0)

    def test_unreachable_node(self):
        g = Graph(directed=True)
        g.add_edge("A", "B", 1)
        g.add_node("Z")
        result = bellman_ford(g, "A")
        assert result["dist"]["Z"] == float("inf")
