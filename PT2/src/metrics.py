import time
import tracemalloc
import json
import os
from collections import Counter


def run_timed(fn, *args, track_memory=False, **kwargs):
    if track_memory:
        tracemalloc.start()
    t0 = time.perf_counter()
    result = fn(*args, **kwargs)
    elapsed = time.perf_counter() - t0
    mem_kb = None
    if track_memory:
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        mem_kb = round(peak / 1024, 2)
    return result, round(elapsed, 6), mem_kb


def degree_stats(graph):
    degrees = [graph.degree(u) for u in graph.nodes]
    n = len(degrees)
    if n == 0:
        return {}
    avg = sum(degrees) / n
    sorted_d = sorted(degrees)
    median = sorted_d[n // 2]
    return {
        "min": min(degrees),
        "max": max(degrees),
        "avg": round(avg, 2),
        "median": median,
        "distribution": dict(Counter(degrees)),
    }


def describe_graph(graph):
    return {
        "num_nodes": graph.num_nodes(),
        "num_edges": graph.num_edges(),
        "directed": graph.directed,
        "degree_stats": degree_stats(graph),
    }


def format_bfs_result(result, source):
    return {
        "source": source,
        "visited_count": result["visited_count"],
        "num_layers": len(result["layers"]),
        "layer_sizes": {k: len(v) for k, v in result["layers"].items()},
        "order_sample": result["order"][:20],
    }


def format_dfs_result(result, source):
    return {
        "source": source,
        "visited_count": result["visited_count"],
        "has_cycle": result["has_cycle"],
        "cycles_sample": result["cycles"][:5],
        "edge_class_counts": {
            cls: sum(1 for v in result["edge_classes"].values() if v == cls)
            for cls in ("tree", "back", "forward", "cross")
        },
        "order_sample": result["order"][:20],
    }


def format_dijkstra_result(dist, parent, source, target, path):
    return {
        "source": source,
        "target": target,
        "distance": dist.get(target, float("inf")),
        "path": path,
        "path_length": len(path) if path else None,
    }


def format_bf_result(result, source, target, path):
    return {
        "source": source,
        "target": target,
        "has_negative_cycle": result["has_negative_cycle"],
        "distance": result["dist"].get(target, float("inf")),
        "path": path,
    }


def build_performance_table(entries):
    return entries


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
