# Research status — Delta-bedrani v0.1.0

Date: 2026-09-26

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

## Unknown / deliberately unclaimed

- A randomized Tutte zero is not used as an infeasibility certificate.
- No percentage is claimed for PPT pruning.
- No generic hardware benchmark is claimed.
- No absolute claim is made that no third-party delta-matroid implementation exists.
- Large explicit exchange-graph materialization is unsupported by design.
