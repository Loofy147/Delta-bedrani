# Verified Tutte-Schur Library v1.0 — Roadmap and Integration Contract

Status: ROADMAP / ACTIVE RESEARCH PLAN
Recorded: 2026-09-30
Repository: Loofy147/Delta-bedrani
Branch: research/verified-tutte-schur-v1-roadmap
Base: feature/exchange-engine-v0 at 9d43885eb449d2506b2b139205259d176980f315

## 1. Objective

Build a reusable research library for matching-pattern / matching-delta-matroid computation with:

- exact finite-field algebra;
- an independent deterministic combinatorial authority;
- incremental Tutte-PPT / Schur search;
- exact structural verification;
- reproducible certificates and benchmark evidence.

The v1.0 target is a verified research library. It is not a claim of polynomial-time enumeration, and one randomized Tutte run is not treated as an exact-completeness authority.

## 2. Architecture

Five contracts are separated:

1. ExactKernel — modular arithmetic, determinant, inverse, Schur complement, Rank-2 update.
2. GroundTruth — deterministic matching-pattern enumeration.
3. Search — global Tutte sampling, single-seed DFS, incremental Schur state, multi-seed union.
4. Verifier — FP/FN, algebraic differential tests, parity/exchange tests, metamorphic tests.
5. Certification/Benchmarking — provenance, probability bound, counters, memory/RSS telemetry, reproducible artifacts.

No layer may promote a claim merely because another layer produced a consistent result.

## 3. Epistemic contract

Use:

ESTABLISHED
EXPERIMENTALLY_SUPPORTED
USER_REPORTED
INFERENCE
HYPOTHESIS
CONTRADICTED
UNKNOWN
OPEN

A nonzero evaluated Tutte determinant is a one-sided feasibility certificate.
A randomized zero is UNKNOWN for feasibility.
Exact family equality against the deterministic oracle is an exact result for that tested instance, not a universal proof of randomized completeness.

## 4. Release gates

### v0.5 — Mathematical kernel freeze

Implement and differentially test:

- prime-field validation;
- exact determinant;
- exact inverse;
- Schur complement;
- Rank-2 quotient update;
- determinant/pair-extension identity.

Required invariant:

Rank2(A,u,v) == DirectSchur(A union {u,v})

over multiple graphs, primes, seeds, and valid pivot states.

Any mismatch blocks progression.

### v0.6 — GroundTruth freeze

The deterministic matching oracle becomes the small/medium-case authority.

Required:

- all labeled simple graphs for n <= 6;
- independent recursive and bitmask-DP cross-checks;
- K_n;
- K_a disjoint-union K_b;
- empty/sparse graphs;
- adversarial small graphs.

Expose compact bitset plus exact family digest.

### v0.7 — Single-seed search

Implement true single-path DFS with incremental Schur state.

Invariants:

- local state alone controls expansion;
- every discovered set has a valid algebraic witness;
- global output state cannot influence expansion;
- active Schur states are bounded by recursive path depth.

### v0.8 — Independent multi-seed certification

For seeds s_1,...,s_r:

F_union = union_i F_i

Each run has independent local visitation state.
The union accumulator is output-only.

Kill tests:

1. pre-filling or clearing the global union must not change local nodes, pair tests, or updates;
2. permuting seed order must not change the union;
3. repeating an identical seed/graph/prime must reproduce the same run.

The probability bound is conditional on the declared independent-uniform sampling model over F_p^*.

### v0.9 — Performance and telemetry freeze

Introduce packed skew-symmetric storage and upper-triangle updates after correctness is frozen.

Measure:

- nodes;
- pair tests;
- Rank-2 updates;
- scalar arithmetic operations;
- runtime;
- peak traced Python allocation;
- isolated-process peak RSS;
- bitset bytes;
- active-state depth.

Do not infer portable runtime from one host.

### v0.95 — Certification freeze

Every certificate binds:

graph digest, code repository/branch/commit, prime, sampling model, RNG, seeds, per-seed counts, union count/digest, oracle count where available, FP/FN, algebraic status, exchange status, counters, memory telemetry, probability formula/value, and interpretation boundary.

Any provenance or result drift invalidates the certificate.

### v1.0 — Stable research library

All of the following are required:

- complete unit suite;
- exhaustive n <= 6 graph suite;
- Rank-2 differential suite;
- exact FP/FN comparison where oracle is enabled;
- multi-seed noninterference;
- small-prime fault injection;
- metamorphic relabeling;
- clean-install/package tests;
- CI on the supported Python matrix;
- reproducible benchmark artifacts;
- explicit UNKNOWN handling;
- probability assumptions retained in every probabilistic claim;
- clean-environment certificate replay.

## 5. Required regression families

K_n:
|F(K_n)| = 2^(n-1)

K_a disjoint-union K_b:
|F| = 2^(a-1) 2^(b-1)

K3 disjoint-union K3:
|F| = 16 and the full six-vertex set is infeasible.

Petersen:
|F| = 272 for the tested labeled instance.

Adversarial small-p fixtures:
retain the p=101 multi-seed truncation counterexample permanently.

Metamorphic relabeling:
F(pi(G)) = { pi(A) : A in F(G) }.

## 6. Complexity contract

The current architecture solves search-state breadth memory but remains exponential in worst-case output/search size.

For K_24:

|F| = 2^23 = 8,388,608

Pair-test workload:

sum_{A in F} C(24-|A|,2) = 578,813,952

For the current full-matrix Rank-2 update implementation, the scalar-entry work is:

sum_{s even, 0 <= s <= 22} C(24,s) (22-s)^2
= 73,219,964,928

Therefore n=24 runtime is UNKNOWN until directly measured.

Bitset storage remains O(2^n). A one-bit-per-subset bitset requires 2^(n-3) bytes; two local/global bitsets require 2^(n-2) bytes.

## 7. Repository placement and lineage

Implementation home:
Loofy147/Delta-bedrani

The current main branch contains the exact delta-matroid kernel. The feature branch feature/exchange-engine-v0 contains the lazy bitmask exchange layer, guarded diameter, theorem-aware paths, finite-field contracts, and related tests.

Current feature head:
9d43885eb449d2506b2b139205259d176980f315

Current base main:
a58e14b176b7013fc7147f322d3613a261b9aaa9

Pull request #1 is open and not merged. The recorded green CI run is for an older head; the current head requires fresh CI evidence before merge.

Important: the full v0.3/v0.4 Tutte-Schur DFS, independent multi-seed union, compact subset bitset, global probability certificate, and telemetry implementation discussed in the conversation are not currently present in feature/exchange-engine-v0. They must be added as new provenance-bearing code.

## 8. Machine relationship

Loofy147/Machine is not currently the implementation home.

Search of Machine did not identify the delta-matroid/Tutte/Schur library there. Machine instead provides a reusable research-governance and evidence discipline:

repository + branch + commit as minimum claim provenance;
Specification -> Claims -> Verification obligation -> Evidence -> Disposition -> Regression protection;
explicit OPEN/UNKNOWN/CONTRADICTED states;
evidence manifests and integrity verification;
resource-contract and benchmark provenance;
branch/specification canonicalization.

Therefore:

Delta-bedrani = domain implementation.
Machine = provenance/evidence/contract reference.

Direct Machine-to-Delta-bedrani code lineage is UNKNOWN and must not be invented.

## 9. Machine material that should be reused by analogy

Relevant Machine documents/lines already establish patterns suitable for this library:

- BRANCH-EVIDENCE-AND-RESEARCH-HANDLING: branch/ref is part of claim identity and similarity is not lineage.
- EVIDENCE-SPECIFICATION-DISPOSITION-CONTRACT: every specification maps to claims, verification obligations, evidence, disposition, and regression protection.
- EVIDENCE-COVERAGE-AUDIT: reproducible execution artifacts and result records must remain mutually consistent.
- RESEARCH-STATE-CANONICALIZATION: main is integration authority; research branches remain scope-bound until reconciled.
- MACHINE-SUBSTRATE-RESOURCE-CONTRACT-v0.2: use explicit resource vectors, common traces, and exact provenance rather than scalar performance scores.
- MACHINE-SUBSTRATE-CONTRACT-CROSSWALK: classify representation/access changes only after normalizing information, timing, storage, access semantics, and resource cost.

These are process precedents, not evidence about the mathematical library.

## 10. Existing Delta-bedrani work to reuse

The main and feature branch already provide:

- exact matching subset-DP;
- matching delta-matroid construction;
- parity-uniform evenness;
- symmetric-exchange and Wenzel verification;
- exact twist/delete/contract/restrict/direct-sum operations;
- exact finite-field determinant/inverse;
- global Tutte matrix and PPT;
- lazy bitmask exchange engine;
- guarded exact diameter;
- theorem-aware exchange paths;
- exhaustive n=4/n=5 graph verification;
- K3 disjoint-union K3 regression at 16 feasible sets;
- reproducible exchange benchmark protocol.

Feature branch status is experimental and branch-scoped. Its current field implementation still recomputes PPT from scratch; Rank-2 incremental Schur belongs in the next library layer.

## 11. v1.0 target layout

src/delta_matroid/
  core.py
  matching.py
  field.py
  schur.py
  search.py
  verify.py
  certificate.py
  telemetry.py

tests/
  test_core.py
  test_matching.py
  test_field.py
  test_schur.py
  test_search.py
  test_certificate.py
  test_metamorphic.py
  test_exhaustive.py

benchmarks/
  protocols/
  runners/
  observed/

evidence/
  claims/
  runs/
  certificates/
  manifests/

docs/
  ROADMAP_V1.md
  MATHEMATICAL_CONTRACT.md
  ALGORITHM_CONTRACT.md
  EVIDENCE_CONTRACT.md
  BENCHMARK_CONTRACT.md
  STATUS.md

## 12. Immediate implementation frontier

1. Add Schur direct and Rank-2 kernels.
2. Differential-test Rank-2 against the existing GlobalTutteMatrix.ppt implementation.
3. Preserve the deterministic oracle as an explicit certificate authority.
4. Implement true single-path DFS.
5. Separate per-seed local state from global union output.
6. Add exact FP/FN bitset certificates.
7. Add adversarial small-prime fixtures.
8. Add isolated-process memory/RSS telemetry.
9. Add packed skew storage after correctness freeze.
10. Run n=8..20 calibration and a direct n=24 measurement on declared graph families.

## 13. Blocking conditions

Progress stops on:

- algebraic differential mismatch;
- nonzero algebraic witness contradicted by the oracle;
- identical seed/run reproducibility failure;
- global state influencing local search;
- provenance mismatch;
- evidence/result drift;
- probability bound without explicit assumptions;
- performance extrapolation presented as measurement;
- universal theorem claim derived only from finite tests.

## 14. Definition of done

The library is complete when:

correctness is separated from completeness;
completeness is separated from probability;
probability is separated from reproducibility;
performance is separated from correctness;
evidence is separated from interpretation;
repository state is separated from conversation state.

The release artifact is:

executable library + independent oracle + differential/regression suite + reproducible certificates + explicit probabilistic contract + benchmark corpus + provenance ledger.
