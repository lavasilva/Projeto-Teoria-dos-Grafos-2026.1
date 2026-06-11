from collections import defaultdict


class Graph:
    def __init__(self, directed=False):
        self.directed = directed
        self.adj = defaultdict(dict)
        self.nodes = set()

    def add_node(self, u):
        self.nodes.add(u)
        if u not in self.adj:
            self.adj[u] = {}

    def add_edge(self, u, v, weight=1.0):
        self.nodes.add(u)
        self.nodes.add(v)
        self.adj[u][v] = weight
        if not self.directed:
            self.adj[v][u] = weight

    def get_neighbors(self, u):
        return self.adj[u].items()

    def num_nodes(self):
        return len(self.nodes)

    def num_edges(self):
        total = sum(len(nbrs) for nbrs in self.adj.values())
        return total if self.directed else total // 2

    def degree(self, u):
        return len(self.adj[u])

    def degree_distribution(self):
        return {u: self.degree(u) for u in self.nodes}

    def edges(self):
        seen = set()
        result = []
        for u, nbrs in self.adj.items():
            for v, w in nbrs.items():
                key = (min(u, v), max(u, v)) if not self.directed else (u, v)
                if key not in seen:
                    seen.add(key)
                    result.append((u, v, w))
        return result

    def has_edge(self, u, v):
        return v in self.adj.get(u, {})
