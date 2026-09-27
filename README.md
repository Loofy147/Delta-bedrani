# Delta-bedrani

Exact research micro-framework for finite delta-matroids, matching delta-matroids, and exchange-graph experiments.

## Design boundary

The package deliberately separates three layers:

1. **Exact combinatorial authority** — deterministic matching subset-DP and explicit feasible sets.
2. **Exact algebraic certificate** — one global randomized Tutte matrix over a finite field, modular determinant, and PPT certificates.
3. **Structural experiments** — Bouchet symmetric exchange, Wenzel strong simultaneous exchange, and lazy basis/exchange-graph analysis.

A nonzero finite-field Tutte determinant is a certificate of feasibility. A zero randomized determinant is **UNKNOWN**, not an infeasibility certificate.

## Current API

```python
from delta_matroid import MatchingDeltaMatroid, complete_graph

D = complete_graph(6).delta_matroid()
print(D.summary())
print(D.verify_delta_axiom())
print(D.verify_wenzel())
```

The matching layer uses the deterministic recurrence:

`S feasible iff a fixed v in S has a neighbor u in S with S-{u,v} feasible.`

`DeltaMatroid(...)` validates symmetric exchange by default; theorem-backed constructors use an internal validated path only where the mathematical construction already establishes the invariant.

For an explicit family, `delete`, `contract`, `restrict`, `twist`, and `direct_sum` are exact set-system operations.

`is_even()` means parity-uniform: all feasible sets have the same cardinality parity. Matching delta-matroids are the normal/even subclass with even-sized feasible sets.

For a parity-uniform delta-matroid, symmetric exchange alone gives an exact basis-graph metric: `d(A, B) = |A Delta B| / 2`. The implementation exposes `even_exchange_distance()` and `even_exchange_shortest_path()` for this theorem-backed case; BFS is retained as an independent oracle.

## Benchmarking

```bash
PYTHONPATH=src python bench_exchange.py --diameter-limit 512
```

The benchmark records feasible-set count, connectivity, feasible-table construction time, component traversal time, and exact diameter when the configured vertex guard permits it. Measurements are environment-specific.

## Deliberate non-goals in v0.1

- No claim that randomized Tutte enumeration is exact-complete.
- No heuristic pruning based on a zero PPT entry.
- No generic large-scale explicit exchange graph materialization.
- No claim to implement every representation class of linear delta-matroids.
