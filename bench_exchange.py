from __future__ import annotations

import argparse
import json
import platform
import sys
from itertools import combinations
from time import perf_counter

from delta_matroid import MatchingGraph


def petersen_edges():
    outer = [(i, (i + 1) % 5) for i in range(5)]
    inner = [(5 + i, 5 + ((i + 2) % 5)) for i in range(5)]
    spokes = [(i, 5 + i) for i in range(5)]
    return outer + inner + spokes


def complete_edges(n: int):
    return combinations(range(n), 2)


def cycle_edges(n: int):
    return ((i, (i + 1) % n) for i in range(n))


def cases():
    return (
        ("C6", 6, cycle_edges(6)),
        ("K8", 8, complete_edges(8)),
        ("Petersen", 10, petersen_edges()),
        ("K10", 10, complete_edges(10)),
        ("K12", 12, complete_edges(12)),
    )


def run_case(name, n, edges, diameter_limit):
    graph = MatchingGraph.from_edges(range(n), edges)

    t0 = perf_counter()
    masks = graph.feasible_masks()
    build_s = perf_counter() - t0

    engine = graph.exchange_engine(feasible_masks=masks)

    t1 = perf_counter()
    count = engine.feasible_count()
    component = engine.component_size()
    connectivity_s = perf_counter() - t1

    feasible_vertices = tuple(engine.iter_vertices())
    endpoints = (feasible_vertices[0], feasible_vertices[-1])

    t2 = perf_counter()
    theorem_path = engine.even_exchange_shortest_path(*endpoints)
    theorem_path_s = perf_counter() - t2

    t3 = perf_counter()
    bfs_path = engine.shortest_path(*endpoints)
    bfs_path_s = perf_counter() - t3

    row = {
        "graph": name,
        "n": n,
        "feasible_sets": count,
        "component_size": component,
        "connected": component == count,
        "feasible_table_build_s": build_s,
        "connectivity_s": connectivity_s,
        "theorem_path_length": len(theorem_path) - 1,
        "bfs_path_length": len(bfs_path) - 1,
        "theorem_path_s": theorem_path_s,
        "bfs_path_s": bfs_path_s,
        "diameter": None,
        "diameter_s": None,
        "diameter_status": "SKIPPED",
    }

    if count <= diameter_limit:
        t2 = perf_counter()
        row["diameter"] = engine.diameter(max_vertices=diameter_limit)
        row["diameter_s"] = perf_counter() - t2
        row["diameter_status"] = "EXACT"

    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--diameter-limit",
        type=int,
        default=512,
        help="maximum number of feasible vertices for exact all-pairs diameter",
    )
    args = parser.parse_args()

    results = {
        "python": sys.version,
        "platform": platform.platform(),
        "python_implementation": platform.python_implementation(),
        "diameter_limit": args.diameter_limit,
        "cases": [],
    }

    for name, n, edges in cases():
        results["cases"].append(run_case(name, n, edges, args.diameter_limit))

    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
