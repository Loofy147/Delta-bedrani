# Research status — Delta-bedrani v0.1.0

Date: 2026-09-27

## Repository state

- `main` contains the exact research kernel and CI workflow.
- `feature/exchange-engine-v0` contains the lazy bitmask exchange engine and benchmark protocol.
- Pull request: #1.
- Feature branch is intentionally kept separate from `main` until review and CI evidence are available.
- The previous branch-history construction briefly dropped CI and benchmark documentation; this was detected by compare-diff audit and is being repaired explicitly.

## Established by theory

- A matching delta-matroid of a simple graph is defined by the vertex subsets inducing subgraphs with perfect matchings; the construction is due to Bouchet. 
- Matching delta-matroids are even and normal.
- Wenzel (1993) characterizes even delta-matroids by strong symmetric exchange conditions.
- Exact finite-field Tutte arithmetic gives a one-sided feasibility certificate: a nonzero evaluated determinant implies existence of a perfect matching.

## Experimentally supported

- All 1088 labeled simple graphs for n=4 and n=5 were checked by deterministic matching-DP.
- Those 1088 exact families passed weak symmetric exchange and Wenzel strong exchange verification.
- K3 disjoint-union K3 remains singular in 100 finite-field Tutte samples.
- Exact PPT identities are covered by tests when the pivot block is invertible.
- K_n counts agree with 2^(n-1) through n=24 in the bitmask backend.
- The lazy exchange engine has targeted tests for one-/two-bit exchange generation, shortest paths, connectivity, and guarded exact diameter.
- Observed exchange-graph results for C6, K8, Petersen, K10, and K12 are recorded in `benchmarks/OBSERVED_2026-09-27.md`.

## Unknown / deliberately unclaimed

- A randomized Tutte zero is not an infeasibility certificate.
- No percentage is claimed for PPT pruning.
- No portable hardware-independent runtime is claimed.
- Exact all-pairs diameter is guarded by a feasible-vertex limit.
- Large explicit exchange-graph materialization is unsupported by design.
- GitHub Actions workflow run 36331349628 completed successfully for all four Python matrix jobs.
- The ecosystem scan found active third-party implementation work (for example, an open 2026 Jacobian issue); novelty claims are therefore scoped to this repository's exact architecture and evidence workflow.
