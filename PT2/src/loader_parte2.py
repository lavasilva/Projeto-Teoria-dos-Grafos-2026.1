import os
import csv
import json
from collections import defaultdict
from src.graph import Graph


def load_wikispeedia_dataset(data_dir):
    articles_path = os.path.join(data_dir, "articles.tsv")
    links_path = os.path.join(data_dir, "links.tsv")
    categories_path = os.path.join(data_dir, "categories.tsv")

    print("[1/3] Carregando artigos...")
    articles = set()
    if os.path.exists(articles_path):
        with open(articles_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    articles.add(line)
    print(f"       {len(articles)} artigos carregados.")

    print("[2/3] Carregando categorias...")
    article_categories = defaultdict(set)
    if os.path.exists(categories_path):
        with open(categories_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split("\t")
                    if len(parts) == 2:
                        article, category = parts
                        article_categories[article].add(category.split(".")[0])
    print(f"       {len(article_categories)} artigos com categoria.")

    print("[3/3] Carregando links...")
    raw_edges = []
    if os.path.exists(links_path):
        with open(links_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split("\t")
                    if len(parts) == 2:
                        src, tgt = parts
                        if src in articles and tgt in articles:
                            raw_edges.append((src, tgt))
    print(f"       {len(raw_edges)} links carregados.")

    return articles, raw_edges, article_categories


def build_graph(data_dir, **kwargs):
    articles, raw_edges, article_categories = load_wikispeedia_dataset(data_dir)

    print("Construindo grafo Wikispeedia...")
    g = Graph(directed=True)

    out_degree = defaultdict(int)
    in_degree = defaultdict(int)
    for src, tgt in raw_edges:
        out_degree[src] += 1
        in_degree[tgt] += 1

    for article in articles:
        g.add_node(article)

    for src, tgt in raw_edges:
        out_d = max(out_degree[src], 1)
        weight = round(1.0 / out_d, 6)
        g.add_edge(src, tgt, weight)

    print(f"Grafo: {g.num_nodes()} nós, {g.num_edges()} arestas.")
    return g, {}, {}, article_categories


def inject_negative_weights(graph, pairs, bonus=-2.0):
    modified = []
    for u, v in pairs:
        if graph.has_edge(u, v):
            old_w = graph.adj[u][v]
            graph.adj[u][v] = bonus
            if not graph.directed:
                graph.adj[v][u] = bonus
            modified.append((u, v, old_w, bonus))
    return modified


def save_report(data, out_dir, filename="parte2_report.json"):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"Relatório salvo em {path}")
