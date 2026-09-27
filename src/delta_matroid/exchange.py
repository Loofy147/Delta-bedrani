from __future__ import annotations

from array import array
from collections import deque
from typing import Iterable, Sequence


class BitmaskExchangeEngine:
    """Lazy exchange-graph engine over feasible subset masks.

    A vertex is a feasible mask in {0,...,n-1}. Two feasible masks are adjacent
    when their symmetric difference has size <= 2. For even families only
    two-bit moves can occur.
    """

    def __init__(
        self,
        n: int,
        feasible_masks: Sequence[int] | bytes | bytearray,
        *,
        even: bool = True,
    ):
        if n < 0:
            raise ValueError("n must be nonnegative")
        expected = 1 << n
        if len(feasible_masks) != expected:
            raise ValueError(f"feasible mask table must have length {expected}")
        if not any(feasible_masks):
            raise ValueError("the feasible mask table must contain at least one vertex")
        if even:
            parities = {i.bit_count() & 1 for i, ok in enumerate(feasible_masks) if ok}
            if len(parities) != 1:
                raise ValueError("even=True requires a parity-uniform feasible family")
        self.n = n
        self.size = expected
        self.feasible = feasible_masks
        self.even = even
        self._bits = tuple(1 << i for i in range(n))
        self._feasible_vertices: int | None = None

    @classmethod
    def from_feasible_iterable(
        cls,
        n: int,
        feasible: Iterable[int],
        *,
        even: bool = True,
    ) -> "BitmaskExchangeEngine":
        table = bytearray(1 << n)
        for mask in feasible:
            if not 0 <= mask < (1 << n):
                raise ValueError("feasible mask outside groundset")
            table[mask] = 1
        return cls(n, table, even=even)

    def __contains__(self, mask: int) -> bool:
        return 0 <= mask < self.size and bool(self.feasible[mask])

    def feasible_count(self) -> int:
        if self._feasible_vertices is None:
            self._feasible_vertices = sum(self.feasible)
        return self._feasible_vertices

    def iter_vertices(self):
        return (mask for mask, ok in enumerate(self.feasible) if ok)

    def neighbors(self, mask: int):
        if mask not in self:
            raise ValueError("mask must be feasible")

        if not self.even:
            for bit in self._bits:
                candidate = mask ^ bit
                if self.feasible[candidate]:
                    yield candidate

        for i in range(self.n):
            bit_i = self._bits[i]
            for j in range(i + 1, self.n):
                candidate = mask ^ bit_i ^ self._bits[j]
                if self.feasible[candidate]:
                    yield candidate

    def degree(self, mask: int) -> int:
        return sum(1 for _ in self.neighbors(mask))

    def component_size(self, source: int | None = None) -> int:
        if source is None:
            source = next(self.iter_vertices(), None)
        if source is None or source not in self:
            raise ValueError("source must be feasible")

        seen = bytearray(self.size)
        seen[source] = 1
        q = deque([source])
        reached = 1

        while q:
            u = q.popleft()
            for v in self.neighbors(u):
                if not seen[v]:
                    seen[v] = 1
                    reached += 1
                    q.append(v)
        return reached

    def is_connected(self, source: int | None = None) -> bool:
        return self.component_size(source) == self.feasible_count()

    def shortest_path(self, source: int, target: int) -> tuple[int, ...]:
        if source not in self or target not in self:
            raise ValueError("both endpoints must be feasible")
        if source == target:
            return (source,)

        parent: dict[int, int] = {source: -1}
        q = deque([source])

        while q:
            u = q.popleft()
            for v in self.neighbors(u):
                if v in parent:
                    continue
                parent[v] = u
                if v == target:
                    path = [v]
                    while path[-1] != source:
                        path.append(parent[path[-1]])
                    path.reverse()
                    return tuple(path)
                q.append(v)

        raise ValueError("exchange graph is disconnected")

    def diameter(self, *, max_vertices: int = 1024) -> int:
        """Exact diameter by all-pairs BFS with an explicit size guard."""
        vertices = tuple(self.iter_vertices())
        count = len(vertices)

        if count > max_vertices:
            raise ValueError(
                f"exact diameter disabled for {count} feasible vertices; "
                f"max_vertices={max_vertices}"
            )

        best = 0
        distances = array("i", [-1]) * self.size
        seen_stamp = array("I", [0]) * self.size
        stamp = 0

        for source in vertices:
            stamp += 1
            reached = 1
            seen_stamp[source] = stamp
            distances[source] = 0
            q = deque([source])
            eccentricity = 0

            while q:
                u = q.popleft()
                du = distances[u]
                for v in self.neighbors(u):
                    if seen_stamp[v] == stamp:
                        continue
                    seen_stamp[v] = stamp
                    distances[v] = du + 1
                    reached += 1
                    eccentricity = max(eccentricity, du + 1)
                    q.append(v)

            if reached != count:
                raise ValueError("exchange graph is disconnected")
            best = max(best, eccentricity)

        return best
