from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from itertools import combinations
from typing import Hashable, Iterable, Mapping

Element = Hashable
SetLike = Iterable[Element]


@dataclass(frozen=True)
class ExchangeViolation:
    A: frozenset[Element]
    B: frozenset[Element]
    x: Element
    condition: str


class DeltaMatroid:
    """Finite set-system representation of a delta-matroid."""

    def __init__(self, groundset: Iterable[Element], feasible_sets: Iterable[SetLike], *, _validated: bool = False):
        E = frozenset(groundset)
        F = frozenset(frozenset(S) for S in feasible_sets)
        if not F:
            raise ValueError("A delta-matroid must have a nonempty feasible family.")
        outside = [S for S in F if not S <= E]
        if outside:
            raise ValueError(f"Feasible set outside groundset: {outside[0]!r}")
        self._groundset = E
        self._feasible = F
        self._index = {e: i for i, e in enumerate(sorted(E, key=repr))}
        self._ordered_groundset = tuple(sorted(E, key=repr))

        if not _validated:
            violation = self.verify_delta_axiom()
            if violation is not None:
                raise ValueError(
                    f"feasible family violates symmetric exchange: {violation}"
                )

    @classmethod
    def from_feasible_sets(cls, groundset: Iterable[Element], feasible_sets: Iterable[SetLike]):
        return cls(groundset, feasible_sets, _validated=False)

    @classmethod
    def _from_validated(cls, groundset: Iterable[Element], feasible_sets: Iterable[SetLike]):
        return cls(groundset, feasible_sets, _validated=True)

    @property
    def groundset(self) -> frozenset[Element]:
        return self._groundset

    @property
    def feasible_sets(self) -> frozenset[frozenset[Element]]:
        return self._feasible

    @property
    def size(self) -> int:
        return len(self._feasible)

    def __contains__(self, subset: SetLike) -> bool:
        return frozenset(subset) in self._feasible

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DeltaMatroid):
            return NotImplemented
        return self._groundset == other._groundset and self._feasible == other._feasible

    def __hash__(self) -> int:
        return hash((self._groundset, self._feasible))

    def is_even(self) -> bool:
        """Return True when all feasible sets have the same parity."""
        parities = {len(F) % 2 for F in self._feasible}
        return len(parities) == 1

    def is_normal(self) -> bool:
        return frozenset() in self._feasible

    def loops(self) -> frozenset[Element]:
        return frozenset(e for e in self._groundset if all(e not in F for F in self._feasible))

    def coloops(self) -> frozenset[Element]:
        return frozenset(e for e in self._groundset if all(e in F for F in self._feasible))

    def verify_delta_axiom(self) -> ExchangeViolation | None:
        F = self._feasible
        for A in F:
            for B in F:
                diff = A ^ B
                for x in diff:
                    if not any(A ^ {x, y} in F for y in diff):
                        return ExchangeViolation(A, B, x, "weak_symmetric_exchange_failed")
        return None

    def verify_wenzel(self) -> ExchangeViolation | None:
        if not self.is_even():
            raise ValueError("Wenzel strong exchange here is the even-delta-matroid form.")
        F = self._feasible
        for A in F:
            for B in F:
                diff = A ^ B
                for x in diff:
                    for y in diff:
                        if y != x and (A ^ {x, y} in F) and (B ^ {x, y} in F):
                            break
                    else:
                        return ExchangeViolation(A, B, x, "wenzel_strong_exchange_failed")
        return None

    def twist(self, subset: SetLike) -> "DeltaMatroid":
        A = frozenset(subset)
        if not A <= self._groundset:
            raise ValueError("Twist set must be contained in the groundset.")
        return DeltaMatroid._from_validated(self._groundset, (F ^ A for F in self._feasible))

    def _delete_feasible(self, e: Element) -> frozenset[frozenset[Element]]:
        if e in self.coloops():
            return frozenset(F - {e} for F in self._feasible)
        return frozenset(F for F in self._feasible if e not in F)

    @staticmethod
    def _normalize_elements(value: Element | Iterable[Element], groundset: frozenset[Element]) -> list[Element]:
        try:
            if value in groundset:  # type: ignore[operator]
                return [value]  # type: ignore[list-item]
        except TypeError:
            pass
        return list(value)  # type: ignore[arg-type]

    def delete(self, element: Element | Iterable[Element]) -> "DeltaMatroid":
        elements = self._normalize_elements(element, self._groundset)
        if not set(elements) <= self._groundset:
            raise ValueError("Deletion set must be contained in the groundset.")
        D = self
        for e in elements:
            D = DeltaMatroid._from_validated(D._groundset - {e}, D._delete_feasible(e))
        return D

    def _contract_one(self, e: Element) -> "DeltaMatroid":
        loops = self.loops()
        if e in loops:
            newF = frozenset(self._feasible)
        else:
            newF = frozenset(F - {e} for F in self._feasible if e in F)
        return DeltaMatroid._from_validated(self._groundset - {e}, newF)

    def contract(self, element: Element | Iterable[Element]) -> "DeltaMatroid":
        elements = self._normalize_elements(element, self._groundset)
        if not set(elements) <= self._groundset:
            raise ValueError("Contraction set must be contained in the groundset.")
        D = self
        for e in elements:
            D = D._contract_one(e)
        return D

    def restrict(self, subset: SetLike) -> "DeltaMatroid":
        A = frozenset(subset)
        if not A <= self._groundset:
            raise ValueError("Restriction set must be contained in the groundset.")
        return self.delete(self._groundset - A)

    def direct_sum(self, other: "DeltaMatroid") -> "DeltaMatroid":
        if self._groundset & other._groundset:
            raise ValueError("Direct sum requires disjoint groundsets.")
        return DeltaMatroid._from_validated(
            self._groundset | other._groundset,
            (A | B for A in self._feasible for B in other._feasible),
        )

    def mask(self, subset: SetLike) -> int:
        S = frozenset(subset)
        if not S <= self._groundset:
            raise ValueError("Subset outside groundset.")
        return sum(1 << self._index[e] for e in S)

    def set_from_mask(self, mask: int) -> frozenset[Element]:
        if not 0 <= mask < (1 << len(self._ordered_groundset)):
            raise ValueError("mask outside groundset")
        return frozenset(
              self._ordered_groundset[i]
            for i in range(len(self._ordered_groundset))
            if mask >> i & 1
        )

    def exchange_neighbors(self, F: SetLike) -> frozenset[frozenset[Element]]:
        A = frozenset(F)
        if A not in self._feasible:
            raise ValueError("Input set is not feasible.")
        result: set[frozenset[Element]] = set()
        for e in self._groundset:
            B = A ^ {e}
            if B in self._feasible:
                result.add(B)
        for e, f in combinations(self._groundset, 2):
            B = A ^ {e, f}
            if B in self._feasible:
                result.add(B)
        return frozenset(result)

    def exchange_graph(self) -> Mapping[frozenset[Element], frozenset[frozenset[Element]]]:
        return {F: self.exchange_neighbors(F) for F in self._feasible}

    def is_exchange_connected(self) -> bool:
        start = next(iter(self._feasible))
        seen = {start}
        q = deque([start])
        while q:
            F = q.popleft()
            for G in self.exchange_neighbors(F):
                if G not in seen:
                    seen.add(G)
                    q.append(G)
        return len(seen) == len(self._feasible)

    def shortest_path(self, source: SetLike, target: SetLike) -> tuple[frozenset[Element], ...]:
        s, t = frozenset(source), frozenset(target)
        if s not in self._feasible or t not in self._feasible:
            raise ValueError("Both endpoints must be feasible.")
        if s == t:
            return (s,)
        parent: dict[frozenset[Element], frozenset[Element] | None] = {s: None}
        q = deque([s])
        while q:
            F = q.popleft()
            for G in self.exchange_neighbors(F):
                if G in parent:
                    continue
                parent[G] = F
                if G == t:
                    path = [G]
                    while parent[path[-1]] is not None:
                        path.append(parent[path[-1]])  # type: ignore[arg-type]
                    path.reverse()
                    return tuple(path)
                q.append(G)
        raise ValueError("Exchange graph is disconnected.")

    def diameter(self) -> int:
        max_distance = 0
        for source in self._feasible:
            dist = {source: 0}
            q = deque([source])
            while q:
                F = q.popleft()
                for G in self.exchange_neighbors(F):
                    if G not in dist:
                        dist[G] = dist[F] + 1
                        q.append(G)
            if len(dist) != len(self._feasible):
                raise ValueError("Exchange graph is disconnected.")
            max_distance = max(max_distance, max(dist.values()))
        return max_distance

    def summary(self) -> dict[str, object]:
        sizes = [len(F) for F in self._feasible]
        return {
            "groundset_size": len(self._groundset),
            "feasible_count": len(self._feasible),
            "min_feasible_size": min(sizes),
            "max_feasible_size": max(sizes),
            "even": self.is_even(),
            "normal": self.is_normal(),
            "loops": tuple(sorted(self.loops(), key=repr)),
            "coloops": tuple(sorted(self.coloops(), key=repr)),
        }
