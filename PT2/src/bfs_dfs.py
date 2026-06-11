from collections import deque


def bfs(graph, source):
    visited = {source: None}
    layers = {source: 0}
    queue = deque([source])
    order = []
    layer_map = defaultdict_compat()

    while queue:
        node = queue.popleft()
        order.append(node)
        layer = layers[node]
        layer_map.setdefault(layer, []).append(node)
        for neighbor, _ in graph.get_neighbors(node):
            if neighbor not in visited:
                visited[neighbor] = node
                layers[neighbor] = layer + 1
                queue.append(neighbor)

    return {
        "order": order,
        "layers": layer_map,
        "parent": visited,
        "visited_count": len(visited),
    }


def defaultdict_compat():
    return {}


def dfs(graph, source):
    visited = set()
    parent = {source: None}
    discovery = {}
    finish = {}
    edge_classes = {}
    cycles_found = []
    timer = [0]
    order = []

    def _dfs_visit(u):
        visited.add(u)
        timer[0] += 1
        discovery[u] = timer[0]
        order.append(u)
        for v, _ in graph.get_neighbors(u):
            if v not in visited:
                parent[v] = u
                edge_classes[(u, v)] = "tree"
                _dfs_visit(v)
            else:
                if v not in finish:
                    edge_classes[(u, v)] = "back"
                    cycles_found.append((u, v))
                elif discovery[u] < discovery[v]:
                    edge_classes[(u, v)] = "forward"
                else:
                    edge_classes[(u, v)] = "cross"
        timer[0] += 1
        finish[u] = timer[0]

    import sys
    sys.setrecursionlimit(100000)
    _dfs_visit(source)

    return {
        "order": order,
        "parent": parent,
        "discovery": discovery,
        "finish": finish,
        "edge_classes": edge_classes,
        "has_cycle": len(cycles_found) > 0,
        "cycles": cycles_found,
        "visited_count": len(visited),
    }
