"""
graph.py – Estrutura de grafo não-direcionado com lista de adjacência.
Proibido usar networkx/igraph/graph-tool para algoritmos.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class Edge:
    """Representa uma aresta com metadados."""
    origem: str
    destino: str
    peso: float
    tipo_conexao: str
    justificativa: str

    def other(self, node: str) -> str:
        return self.destino if node == self.origem else self.origem


@dataclass
class Graph:
    """
    Grafo não-direcionado rotulado com lista de adjacência.

    Atributos
    ---------
    adj : dict[str, list[Edge]]
        Mapa nó -> lista de arestas incidentes.
    node_meta : dict[str, dict]
        Metadados dos nós (cidade, regiao, ...).
    _edges : list[Edge]
        Lista canônica de arestas (sem duplicatas/espelhamento).
    """

    adj: Dict[str, List[Edge]] = field(default_factory=dict)
    node_meta: Dict[str, dict] = field(default_factory=dict)
    _edges: List[Edge] = field(default_factory=list)

    def add_node(self, iata: str, **meta) -> None:
        """Adiciona um nó (aeroporto). Idempotente."""
        if iata not in self.adj:
            self.adj[iata] = []
            self.node_meta[iata] = meta

    def add_edge(self, origem: str, destino: str, peso: float = 1.0,
                 tipo_conexao: str = "", justificativa: str = "") -> None:
        """Adiciona aresta não-direcionada (espelhada na lista de adj)."""
        for n, label in [(origem, "origem"), (destino, "destino")]:
            if n not in self.adj:
                raise ValueError(f"Nó desconhecido ({label}): {n!r}")
        edge = Edge(origem=origem, destino=destino, peso=peso,
                    tipo_conexao=tipo_conexao, justificativa=justificativa)
        self.adj[origem].append(edge)
        self.adj[destino].append(edge)
        self._edges.append(edge)

    @property
    def nodes(self) -> List[str]:
        return list(self.adj.keys())

    @property
    def edges(self) -> List[Edge]:
        return list(self._edges)

    @property
    def order(self) -> int:
        """Ordem |V|."""
        return len(self.adj)

    @property
    def size(self) -> int:
        """Tamanho |E|."""
        return len(self._edges)

    def degree(self, node: str) -> int:
        return len(self.adj[node])

    def neighbors(self, node: str) -> List[str]:
        return [e.other(node) for e in self.adj[node]]

    def has_edge(self, u: str, v: str) -> bool:
        return any(e.other(u) == v for e in self.adj.get(u, []))

    def density(self) -> float:
        """
        Densidade do grafo não-direcionado:
            2|E| / (|V| * (|V| - 1))
        Retorna 0.0 se |V| < 2.
        """
        v = self.order
        if v < 2:
            return 0.0
        return (2 * self.size) / (v * (v - 1))

    def induced_subgraph(self, nodes: Set[str]) -> "Graph":
        """Subgrafo induzido pelo conjunto nodes."""
        sub = Graph()
        for n in nodes:
            if n in self.adj:
                sub.add_node(n, **self.node_meta.get(n, {}))
        for edge in self._edges:
            if edge.origem in nodes and edge.destino in nodes:
                sub.add_edge(edge.origem, edge.destino,
                             peso=edge.peso,
                             tipo_conexao=edge.tipo_conexao,
                             justificativa=edge.justificativa)
        return sub

    def ego_network(self, node: str) -> "Graph":
        """Ego-network de node: subgrafo induzido por {node} ∪ N(node)."""
        ego_nodes = {node} | set(self.neighbors(node))
        return self.induced_subgraph(ego_nodes)

    def __repr__(self) -> str:
        return f"Graph(|V|={self.order}, |E|={self.size})"