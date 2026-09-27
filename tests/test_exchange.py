from __future__ import annotations

import pytest

from delta_matroid import MatchingGraph
from delta_matroid.exchange import BitmaskExchangeEngine


def test_even_neighbor_definition():
    feasible = bytearray(1 << 4)
    feasible[0] = 1
    feasible[0b0011] = 1
    feasible[0b0101] = 1
    engine = BitmaskExchangeEngine(4, feasible, even=True)

    assert set(engine.neighbors(0)) == {0b0011, 0b0101}
    assert engine.degree(0) == 2


def test_generic_one_and_two_element_exchanges():
    feasible = bytearray(1 << 3)
    feasible[0b001] = 1
    feasible[0b010] = 1
    feasible[0b111] = 1
    engine = BitmaskExchangeEngine(3, feasible, even=False)

    assert set(engine.neighbors(0b001)) == {0b010, 0b111}
    assert engine.component_size(0b001) == 3


def test_shortest_path_and_diameter():
    D = MatchingGraph.from_edges(
        range(6),
        [(i, (i + 1) % 6) for i in range(6)],
    ).delta_matroid()
    engine = D.graph.exchange_engine()

    path = engine.shortest_path(0, 0b111111)
    assert path[0] == 0
    assert path[-1] == 0b111111
    assert len(path) == 4
    assert engine.diameter(max_vertices=64) == 3


def test_petersen_connected_diameter():
    edges = (
        [(i, (i + 1) % 5) for i in range(5)]
        + [(5 + i, 5 + ((i + 2) % 5)) for i in range(5)]
        + [(i, 5 + i) for i in range(5)]
    )
    D = MatchingGraph.from_edges(range(10), edges).delta_matroid()
    engine = D.graph.exchange_engine()

    assert engine.feasible_count() == 272
    assert engine.is_connected()
    assert engine.diameter(max_vertices=512) == 5


def test_diameter_guard():
    D = MatchingGraph.from_edges(
        range(12),
        ((i, j) for i in range(12) for j in range(i + 1, 12)),
    ).delta_matroid()
    engine = D.graph.exchange_engine()

    assert engine.feasible_count() == 2048
    with pytest.raises(ValueError, match="exact diameter disabled"):
        engine.diameter(max_vertices=512)


def test_even_flag_accepts_odd_parity_uniform_family():
    feasible = bytearray(1 << 2)
    feasible[0b01] = 1
    feasible[0b10] = 1
    engine = BitmaskExchangeEngine(2, feasible, even=True)
    assert set(engine.neighbors(0b01)) == {0b10}
