from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import heapq

from graphs.graph import Graph


def bfs(g: Graph, start: str) -> Dict[str, Optional[str]]:
    if start not in g.adj:
        raise ValueError(f"Nó desconhecido: {start!r}")

    parent: Dict[str, Optional[str]] = {start: None}
    queue = [start]

    while queue:
        node = queue.pop(0)
        for nb in g.neighbors(node):
            if nb not in parent:
                parent[nb] = node
                queue.append(nb)

    return parent


def bfs_path(g: Graph, start: str, end: str) -> Optional[List[str]]:
    parent = bfs(g, start)
    if end not in parent:
        return None
    path = []
    node: Optional[str] = end
    while node is not None:
        path.append(node)
        node = parent[node]
    return list(reversed(path))


def dfs(g: Graph, start: str) -> Dict[str, Optional[str]]:
    if start not in g.adj:
        raise ValueError(f"Nó desconhecido: {start!r}")

    parent: Dict[str, Optional[str]] = {}
    stack = [(start, None)]

    while stack:
        node, par = stack.pop()
        if node in parent:
            continue
        parent[node] = par
        for nb in reversed(g.neighbors(node)):
            if nb not in parent:
                stack.append((nb, node))

    return parent


def dfs_path(g: Graph, start: str, end: str) -> Optional[List[str]]:
    parent = dfs(g, start)
    if end not in parent:
        return None
    path = []
    node: Optional[str] = end
    while node is not None:
        path.append(node)
        node = parent[node]
    return list(reversed(path))

def dijkstra(
    g: Graph, start: str
) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
    if start not in g.adj:
        raise ValueError(f"Nó desconhecido: {start!r}")

    for edge in g.edges:
        if edge.peso < 0:
            raise ValueError(
                f"Dijkstra não suporta pesos negativos: "
                f"aresta {edge.origem!r}↔{edge.destino!r} tem peso {edge.peso}"
            )

    dist:   Dict[str, float]          = {n: float("inf") for n in g.nodes}
    parent: Dict[str, Optional[str]]  = {n: None for n in g.nodes}
    dist[start] = 0.0

    heap = [(0.0, start)]

    while heap:
        cost, node = heapq.heappop(heap)
        if cost > dist[node]:
            continue 
        for edge in g.adj[node]:
            nb      = edge.other(node)
            new_cost = dist[node] + edge.peso
            if new_cost < dist[nb]:
                dist[nb]   = new_cost
                parent[nb] = node
                heapq.heappush(heap, (new_cost, nb))

    return dist, parent


def dijkstra_path(
    g: Graph, start: str, end: str
) -> Tuple[float, Optional[List[str]]]:
    dist, parent = dijkstra(g, start)
    if dist[end] == float("inf"):
        return float("inf"), None

    path = []
    node: Optional[str] = end
    while node is not None:
        path.append(node)
        node = parent[node]
    return dist[end], list(reversed(path))


def bellman_ford(
    g: Graph, start: str
) -> Tuple[Dict[str, float], Dict[str, Optional[str]], bool]:
    if start not in g.adj:
        raise ValueError(f"Nó desconhecido: {start!r}")

    dist:   Dict[str, float]         = {n: float("inf") for n in g.nodes}
    parent: Dict[str, Optional[str]] = {n: None for n in g.nodes}
    dist[start] = 0.0

    nodes = g.nodes
    edges = g.edges
    n     = len(nodes)

    for _ in range(n - 1):
        updated = False
        for edge in edges:
            if dist[edge.origem] + edge.peso < dist[edge.destino]:
                dist[edge.destino]   = dist[edge.origem] + edge.peso
                parent[edge.destino] = edge.origem
                updated = True
            if dist[edge.destino] + edge.peso < dist[edge.origem]:
                dist[edge.origem]   = dist[edge.destino] + edge.peso
                parent[edge.origem] = edge.destino
                updated = True
        if not updated:
            break 

    negative_cycle = False
    for edge in edges:
        if dist[edge.origem] + edge.peso < dist[edge.destino]:
            negative_cycle = True
            break
        if dist[edge.destino] + edge.peso < dist[edge.origem]:
            negative_cycle = True
            break

    return dist, parent, negative_cycle


def bellman_ford_path(
    g: Graph, start: str, end: str
) -> Tuple[float, Optional[List[str]], bool]:
    dist, parent, neg_cycle = bellman_ford(g, start)
    if neg_cycle or dist[end] == float("inf"):
        return dist[end], None, neg_cycle

    path = []
    node: Optional[str] = end
    while node is not None:
        path.append(node)
        node = parent[node]
    return dist[end], list(reversed(path)), neg_cycle