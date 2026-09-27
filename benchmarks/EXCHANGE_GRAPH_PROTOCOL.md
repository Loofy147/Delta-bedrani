# Exchange-graph benchmark protocol

## Purpose

Measure the lazy bitmask exchange engine without conflating graph enumeration,
connectivity, and all-pairs diameter cost.

## Adjacency

Two feasible masks A and B are adjacent exactly when

|A Delta B| <= 2.

For even delta-matroids, only the |A Delta B| = 2 case can occur.

## Metrics

For each graph record:

- feasible-set count
- connected component size from the selected source (the empty set for normal matching delta-matroids)
- connectivity
- feasible-mask construction time
- component traversal time
- exact diameter time when below the configured guard

## Guard

Exact diameter is deliberately disabled once the number of feasible vertices
exceeds the configured limit (default: 512). This is a complexity boundary,
not an approximation.

## Reproducibility

Run from repository root:

    PYTHONPATH=src python bench_exchange.py --diameter-limit 512

The program emits JSON containing the Python/platform runtime and measurements.

No percentage of pruning and no portable wall-clock claim is inferred from
these measurements.
