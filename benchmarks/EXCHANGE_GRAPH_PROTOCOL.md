# Exchange-graph benchmark protocol

## Purpose

Measure the lazy bitmask exchange engine without conflating graph enumeration,
connectivity, shortest-path construction, and all-pairs diameter cost.

## Adjacency

Two feasible masks A and B are adjacent exactly when

|A Delta B| <= 2.

For parity-uniform delta-matroids, all feasible sets have the same parity, so
distinct adjacent feasible masks differ by exactly two elements.

## Metrics

For each graph record:

- feasible-set count
- connected component size from the selected source
- connectivity
- feasible-mask construction time
- component traversal time
- theorem-aware shortest-path length and construction time
- independent BFS shortest-path length and construction time
- exact diameter time when below the configured guard

The theorem-aware and BFS path lengths must agree. The theorem-aware path length
should also equal |A Delta B|/2 for the selected endpoints.

## Guard

Exact diameter is deliberately disabled once the number of feasible vertices
exceeds the configured limit (default: 512). This is a complexity boundary,
not an approximation.

## Reproducibility

Run from repository root:

    PYTHONPATH=src python bench_exchange.py --diameter-limit 512

The program emits JSON containing the Python/platform runtime and measurements.

## Evidence rules

Record the exact commit/ref used for the run and preserve the emitted JSON or a
derived observation table. Environment-specific wall-clock measurements are
observations, not portable performance claims.

No percentage of pruning and no asymptotic speedup is inferred from these
measurements.
