# Delta-bedrani Research Operating Contract v0.1

**Status:** RESEARCH-OPERATING-CONTRACT
**Updated:** 2026-10-08

## Purpose

Keep mathematical claims, experiments, implementations, and evidence in separate provenance-bearing states.

Delta-bedrani is an exact research kernel. Its repository state must therefore distinguish:

1. mathematical authority;
2. independent oracle/evaluator;
3. implementation behavior;
4. experiment result;
5. scientific interpretation.

## 1. Claim identity

Every material claim is identified by:

```text
repository + branch + commit + path
```

Repository name alone is insufficient when the repository contains active feature/research branches.

For Delta-bedrani, the current active research implementation is:

```text
repo   = Loofy147/Delta-bedrani
branch = feature/exchange-engine-v0
head   = c9301959469ddcb70afde3011764737c468c028e
```

This does not imply that the feature branch is the canonical `main` state.

## 2. Evidence classes

Use the following distinctions:

- **THEORETICAL:** established by a proof or authoritative mathematical source.
- **DIFFERENTIAL:** agreement between independently implemented evaluators.
- **EXHAUSTIVE-FINITE:** exhaustive verification over an explicitly bounded finite domain.
- **REGRESSION:** a previously identified failure or boundary protected by a test.
- **BENCHMARK:** environment-specific measurement.
- **UNKNOWN:** not decided by the current evaluator/protocol.

A test passing is evidence about the tested behavior. It is not automatically evidence for a stronger theorem.

## 3. Result versus conclusion

```text
execution result != scientific conclusion
```

Before promoting a result, record:

- evaluator validity;
- exact scope;
- reproducibility;
- independence;
- possible contradiction;
- interpretation boundary;
- next discriminating test.

An evaluator failure is first an **INVALID_RESULT** until the evaluator or protocol is repaired.

## 4. Disposition vocabulary

Material results terminate in one of:

```text
CONFIRMED
PARTIALLY_CONFIRMED
CONTRADICTED
REFINED
INCONCLUSIVE
INVALID_RESULT
CONTEXT_BOUND
REGRESSION
NOVEL_SIGNAL
OPEN
```

`OPEN` must carry a concrete next discriminating test.

## 5. Independent oracle rule

`verification/dmlib.py` is an independent evaluator.

It must not import `delta_matroid` implementation modules.

When an oracle and implementation disagree:

1. preserve the exact input;
2. preserve both outputs;
3. identify the first semantic divergence;
4. determine whether the oracle, implementation, or protocol is wrong;
5. only then change the scientific disposition.

Do not repair an implementation merely to make an oracle comparison green.

## 6. Finite closure boundary

Exhaustive agreement on a finite domain is recorded as:

```text
EXHAUSTIVE-FINITE
```

It must not silently become:

```text
GENERAL
```

For example, all labeled simple graphs on n=5 establish an exact finite check, not an asymptotic theorem about all graphs.

## 7. Branch drift

A result on `feature/exchange-engine-v0` is not automatically a result on `main`.

When a claim is copied into documentation, retain:

```text
source branch
source commit
evidence path
test/run identifier
scope
status
```

A later commit invalidates "current" wording unless it has received fresh verification where the changed surface matters.

## 8. Evidence regression gate

The preferred progression is:

```text
source
  -> deterministic evaluator
  -> normalized result
  -> claim binding
  -> disposition
  -> regression protection
```

The repository currently has the evaluator and regression tests, but does not yet have an automated machine-readable evidence-integrity gate for the claim registry itself.

That is explicit specification debt.

## 9. Machine-derived boundary

The following research-discipline rules are adopted from the audited Machine protocol:

- branch identity is part of provenance;
- suggestions are not evidence;
- similarity is not lineage;
- finite experimental closure is not a general closure theorem;
- implementation behavior, mechanism interpretation, and architectural implication remain separate;
- unverified README or benchmark prose does not promote a claim.

These are methodological controls only. No Machine mechanism is imported into Delta-bedrani as a mathematical or computational capability.

## 10. Current project frontier

The current strongest verified frontier is:

```text
explicit feasible-set kernel
+ deterministic matching subset-DP
+ independent exchange oracle
+ theorem-aware even exchange path
+ exact modular algebra checks
+ provenance-bearing research status
```

The next frontier is not "more features".

It is stronger independent verification and sharper characterization of:

- representability;
- local cone generation;
- optimization behavior;
- minor/twist closure;
- counterexample families;
- finite versus family-level closure.

## 11. Governing invariant

> No material claim may rely only on repository prose. It must retain its source location, scope, evidence class, disposition, and next discriminating test.

