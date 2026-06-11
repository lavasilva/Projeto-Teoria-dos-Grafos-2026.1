def bellman_ford(graph, source):
    dist = {node: float("inf") for node in graph.nodes}
    dist[source] = 0
    parent = {source: None}
    nodes = list(graph.nodes)
    n = len(nodes)
    edge_list = graph.edges()

    for _ in range(n - 1):
        updated = False
        for u, v, w in edge_list:
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                updated = True
            if not graph.directed:
                if dist[v] != float("inf") and dist[v] + w < dist[u]:
                    dist[u] = dist[v] + w
                    parent[u] = v
                    updated = True
        if not updated:
            break

    negative_cycle_nodes = set()
    for u, v, w in edge_list:
        if dist[u] != float("inf") and dist[u] + w < dist[v]:
            negative_cycle_nodes.add(v)
        if not graph.directed:
            if dist[v] != float("inf") and dist[v] + w < dist[u]:
                negative_cycle_nodes.add(u)

    has_negative_cycle = len(negative_cycle_nodes) > 0

    return {
        "dist": dist,
        "parent": parent,
        "has_negative_cycle": has_negative_cycle,
        "negative_cycle_nodes": negative_cycle_nodes,
    }


def reconstruct_path_bf(parent, source, target):
    if target not in parent:
        return None
    path = []
    cur = target
    visited_in_path = set()
    while cur is not None:
        if cur in visited_in_path:
            return None
        visited_in_path.add(cur)
        path.append(cur)
        cur = parent.get(cur)
    path.reverse()
    if not path or path[0] != source:
        return None
    return path
