from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Iterable

from .core import DeltaMatroid
from .exchange import BitmaskExchangeEngine

Vertex = Hashable


@dataclass(frozen=True)
class MatchingGraph:
    vertices: tuple[Vertex, ...]
    edges: frozenset[frozenset[Vertex]]

    @classmethod
    def from_edges(
        cls,
        vertices: Iterable[Vertex],
        edges: Iterable[tuple[Vertex, Vertex]],
    ) -> "MatchingGraph":
        V = tuple(dict.fromkeys(vertices))
        E: set[frozenset[Vertex]] = set()
        allowed = set(V)
        for u, v in edges:
            if u == v:
                raise ValueError("Loops are not supported for simple graphs.")
            if u not in allowed or v not in allowed:
                raise ValueError("Edge endpoint is outside the vertex set.")
            E.add(frozenset((u, v)))
        return cls(V, frozenset(E))

    def _adj_masks(self) -> list[int]:
        index = {v: i for i, v in enumerate(self.vertices)}
        adj = [0] * len(self.vertices)
        for edge in self.edges:
            u, v = tuple(edge)
            i, j = index[u], index[v]
            adj[i] |= 1 << j
            adj[j] |= 1 << i
        return adj

    def feasible_masks(self) -> bytearray:
        """Exact deterministic matching-pattern table."""
        n = len(self.vertices)
        adj = self._adj_masks()
        feasible = bytearray(1 << n)
        feasible[0] = 1

        for mask in range(1, 1 << n):
            if mask.bit_count() & 1:
                continue

            lsb = mask & -mask
            v = lsb.bit_length() - 1
            rest = mask ^ lsb
            nbrs = adj[v] & rest

            while nbrs:
                bit = nbrs & -nbrs
                if feasible[rest ^ bit]:
                    feasible[mask] = 1
                    break
                nbrs ^= bit

        return feasible

    def feasible_count(self) -> int:
        return sum(self.feasible_masks())

    def feasible_family(self) -> list[frozenset[Vertex]]:
        feasible = self.feasible_masks()
        n = len(self.vertices)
        return [
            frozenset(self.vertices[i] for i in range(n) if mask >> i & 1)
            for mask, ok in enumerate(feasible) if ok
        ]

    def exchange_engine(
        self,
        *,
        feasible_masks: bytearray | bytes | None = None,
    ) -> BitmaskExchangeEngine:
        """Create a lazy exchange engine without materializing graph edges."""
        masks = self.feasible_masks() if feasible_masks is None else feasible_masks
        return BitmaskExchangeEngine(len(self.vertices), masks, even=True)

    def delta_matroid(self) -> "MatchingDeltaMatroid":
        return MatchingDeltaMatroid(self)


class MatchingDeltaMatroid(DeltaMatroid):
    def __init__(self, graph: MatchingGraph):
        self.graph = graph
        super().__init__(graph.vertices, graph.feasible_family(), _validated=True)

    def exchange_engine(self) -> BitmaskExchangeEngine:
        return self.graph.exchange_engine()


def complete_graph(n: int) -> MatchingGraph:
    if n < 0:
        raise ValueError("n must be nonnegative.")
    vertices = tuple(range(n))
    return MatchingGraph.from_edges(
        vertices,
        ((i, j) for i in range(n) for j in range(i + 1, n)),
    )


def cycle_graph(n: int) -> MatchingGraph:
    if n < 3:
        raise ValueError("A simple cycle requires n >= 3.")
    return MatchingGraph.from_edges(
        range(n),
        ((i, (i + 1) % n) for i in range(n)),
    )
