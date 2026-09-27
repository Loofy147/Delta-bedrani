# Research status — Delta-bedrani v0.1.0

Date: 2026-09-27

## Repository state

- `main` contains the exact research kernel and CI workflow.
- `feature/exchange-engine-v0` contains the lazy bitmask exchange engine and benchmark protocol.
- Pull request: #1.
- Feature head has additional documentation/measurement commits after the initial feature commit.
- The compare against `main` remains clean: the feature branch does not delete CI or unrelated files.

## Established by theory

- Matching feasible-set systems form even delta-matroids.
- Wenzel (1993) gives the strong exchange characterization for even delta-matroids.
- Exact finite-field Tutte arithmetic gives a one-sided feasibility certificate: nonzero determinant implies existence of a perfect matching.

## Experimentally supported

- All 1088 labeled simple graphs for n=4 and n=5 were checked by deterministic matching-DP.
- Those 1088 exact families passed weak symmetric exchange and Wenzel strong exchange verification.
- K3 disjoint-union K3 remains singular in 100 finite-field Tutte samples.
- Exact PPT identities are covered by tests when the pivot block is invertible.
- K_n counts agree with 2^(n-1) through n=24 in the bitmask backend.
- The lazy exchange engine was independently smoke-tested against direct symmetric-difference neighbor enumeration for n=1..7.
- Observed exchange-graph results for C6, K8, Petersen, K10, and K12 are recorded in `benchmarks/OBSERVED_2026-09-27.md`.

## Unknown / deliberately unclaimed

- A randomized Tutte zero is not an infeasibility certificate.
- No percentage is claimed for PPT pruning.
- No portable hardware-independent runtime claim is made.
- Exact all-pairs diameter is guarded by a feasible-vertex limit.
- Large explicit exchange-graph materialization is unsupported by design.
- The GitHub Actions workflow has not produced a readable status through the current connector, so CI is not marked PASS here.
- No absolute claim is made that no third-party delta-matroid implementation exists.
