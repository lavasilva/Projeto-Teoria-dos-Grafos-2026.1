import heapq


def dijkstra(graph, source, target=None):
    for u, v, w in graph.edges():
        if w < 0:
            raise ValueError(
                f"Dijkstra requer pesos >= 0. Aresta ({u}, {v}) tem peso {w}."
            )

    dist = {node: float("inf") for node in graph.nodes}
    dist[source] = 0
    parent = {source: None}
    heap = [(0, source)]
    visited = set()

    while heap:
        d, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        if target and u == target:
            break
        for v, w in graph.get_neighbors(u):
            if v not in visited and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                heapq.heappush(heap, (dist[v], v))

    return {"dist": dist, "parent": parent}


def reconstruct_path(parent, source, target):
    if target not in parent:
        return None
    path = []
    cur = target
    while cur is not None:
        path.append(cur)
        cur = parent.get(cur)
    path.reverse()
    if path[0] != source:
        return None
    return path
