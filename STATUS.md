# Research status — Delta-bedrani v0.1.0

Date: 2026-10-08

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
- The lazy exchange engine has targeted tests for one-/two-bit exchange generation, connectivity, guarded exact diameter, plus exhaustive theorem-path checks for every feasible C6 endpoint pair; BFS remains an independent path oracle. Small-system twist/minor closure and direct-sum laws are also covered.
- Observed exchange-graph results for C6, K8, Petersen, K10, and K12 are recorded in `benchmarks/OBSERVED_2026-09-27.md`.

## Independent oracle verification — 2026-10-08

- `verification/dmlib.py` provides an implementation-independent reference layer for symmetric exchange, strong/weak Wenzel exchange, hyperplane exchange, lifting, antipode conditions, exchange graphs, matching subset-DP, modular determinants, GF(2) principal-minor families, GF(3) Pfaffian families, and small exact optimization.
- Differential tests were added in `tests/test_dmlib_oracle.py`; the oracle imports no `delta_matroid` package code.
- Exhaustive n=3 set-system checks compare constructor acceptance against the independent symmetric-exchange oracle.
- All n=5 labeled simple graphs (1024 graphs) compare `MatchingGraph.feasible_masks()` against the independent matching DP.
- Theorem A characterisation equivalences are checked on all nonempty n=3 delta-matroid families: hyperplane exchange, weak Wenzel, parity-completed lift, and peerless-antipode condition.
- Theorem 2.3 equivalences are checked on all n=3 even delta-matroids.
- A known historical unordered-pair weak-verifier false positive is preserved as a regression: feasible masks `{1, 2, 3, 4}` pass the old verifier but fail full symmetric exchange.
- Modular determinant results are cross-checked against an independent implementation on fixed integer matrices over `F_101`.
- TDD evidence: commit `fe48901...` intentionally produced a RED collection failure because the oracle was absent; the oracle and tests were then added and the corrected sequence culminated in workflow `37832187993`.
- Current verification: workflow `37836842551` completed successfully on Python 3.10, 3.11, 3.12, and 3.13; each job reported 43 passed, and the claim-registry integrity gate also passed.

## Oracle hardening — 2026-10-08

- The `ternary_representable()` cap path was reproduced as a real oracle bug: an early `return None` could suppress a later twist that was exactly representable.
- The regression first failed on Python 3.13 with `None is True`; the implementation was then changed to accumulate an `undecided` flag and continue scanning twists.
- The corrected oracle passes the controlled n=5 regression and the full test suite.
- `binary_representable()` and `ternary_representable()` were cross-checked against exhaustive finite-field matrix enumeration for every parity-uniform family on n=4.
- The n=4 representability suite remains fast enough for the normal matrix CI: all four Python jobs passed with 38 tests.
## Theorem A item 5 — isolated antipodes — 2026-10-09

- Added the independent predicate `has_isolated_antipode(F, min_dimension=5)`, defined directly from the paper's interval criterion: for a feasible antipodal pair (A, B), the interval `A & B <= S <= A | B` contains no other feasible set.
- Added `theorem_a_local_antipode_condition(F)`: no peerless antipodes in 3- or 4-cubes and no isolated antipodes in cubes of dimension at least 5.
- Targeted n=5 regressions cover an isolated opposite pair, an added in-interval feasible set that destroys isolation, and the full 5-cube.
- Exhaustive n=4 check: the fifth characterization agrees with the independent strong-delta-matroid reference on all 65,535 nonempty set systems. The dimension-5+ clause is necessarily vacuous at n=4.
- Exhaustive restricted n=5 check: `has_isolated_antipode` agrees with the interval definition on all 5,488 nonempty set systems with at most three feasible masks, plus the full 5-cube boundary fixture. This does not exhaust all n=5 set systems.
- Current CI run `37985896369` passed all 45 tests under Python 3.10, 3.11, 3.12, and 3.13, with the claim-registry integrity gate passing in every matrix job.

## Current implementation hardening

- Exact exchange distance for parity-uniform delta-matroids is derived from symmetric exchange plus parity: `d(A,B) = |A Delta B|/2`.
- A theorem-aware shortest-path backend constructs such paths without BFS; BFS remains the independent oracle.

- `DeltaMatroid` now rejects a family that fails symmetric exchange at construction; theorem-backed internal constructors are used for known-valid closure paths.
- Exact diameter uses O(|F|) distance state per source rather than arrays of size 2^n.

## Research-state controls

- Research claims now follow `docs/RESEARCH-OPERATING-CONTRACT-v0.1.md`.
- The machine-readable claim registry is `evidence/claims-v0.1.json`.
- Claims retain source branch/commit, evidence class, scope, disposition, limitations, and verification run.
- `verification/dmlib.py` is an independent oracle; its agreement with the package is differential evidence, not a mathematical proof.
- Methodological provenance controls were adapted from the audited `Loofy147/Machine` research protocol. No Machine mechanism is treated as a Delta-bedrani computational primitive.

## Unknown / deliberately unclaimed

- A randomized Tutte zero is not an infeasibility certificate.
- No percentage is claimed for PPT pruning.
- No portable hardware-independent runtime is claimed.
- Exact all-pairs diameter is guarded by a feasible-vertex limit.
- Large explicit exchange-graph materialization is unsupported by design.
- GitHub Actions workflow run `37836842551` is the current verified branch-head CI evidence for the feature branch.
- The ecosystem scan found active third-party implementation work (for example, an open 2026 Jacobian issue); novelty claims are therefore scoped to this repository's exact architecture and evidence workflow.
