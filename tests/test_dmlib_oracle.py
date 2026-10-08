from itertools import combinations

import pytest

from delta_matroid import DeltaMatroid, MatchingGraph, det_mod_p
from delta_matroid.exchange import BitmaskExchangeEngine
from verification.dmlib import (
    antipode_strong,
    det_mod,
    hyperplane_delta,
    hyperplane_even,
    is_delta,
    is_even_sys,
    lift,
    neighbors as oracle_neighbors,
    pm_family_dp,
    weak_wenzel,
    wenzel,
)


def all_families(n):
    subsets = tuple(range(1 << n))
    for code in range(1, 1 << len(subsets)):
        yield {subsets[i] for i in range(len(subsets)) if (code >> i) & 1}


def test_constructor_acceptance_matches_independent_delta_oracle_n3():
    n = 3
    for family in all_families(n):
        expected_delta = is_delta(family)
        if expected_delta:
            D = DeltaMatroid(range(n), (
                {i for i in range(n) if mask >> i & 1}
                for mask in family
            ))
            assert D.verify_delta_axiom() is None
            assert D.is_even() == is_even_sys(family)
            if D.is_even():
                assert D.verify_wenzel() is None
                assert wenzel(family)
        else:
            with pytest.raises(ValueError, match="symmetric exchange"):
                DeltaMatroid(range(n), (
                    {i for i in range(n) if mask >> i & 1}
                    for mask in family
                ))


def test_theorem_a_strong_delta_characterizations_match_on_all_n3_families():
    n = 3
    for family in all_families(n):
        if not is_delta(family):
            continue
        lifted = lift(family, n)
        strong = hyperplane_delta(family)
        assert weak_wenzel(family) is strong
        assert is_delta(lifted) and is_even_sys(lifted) is strong
        assert antipode_strong(family) is strong


def test_theorem_2_3_even_characterizations_match_on_all_even_n3_delta_families():
    n = 3
    for family in all_families(n):
        if not (is_delta(family) and is_even_sys(family)):
            continue
        assert hyperplane_even(family)
        assert wenzel(family)


def test_historical_unordered_weak_verifier_has_known_n3_false_positive():
    family = {1, 2, 3, 4}
    assert turn1_weak_verifier(family)
    assert not is_delta(family)


def test_lazy_exchange_neighbors_match_independent_oracle():
    G = MatchingGraph.from_edges(
        range(7),
        [(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (4, 5), (5, 6), (3, 6)],
    )
    D = G.delta_matroid()
    masks = bytearray(1 << 7)
    for F in D.feasible_sets:
        masks[D.mask(F)] = 1

    engine = BitmaskExchangeEngine(7, masks, even=True)
    oracle_family = masks_to_family(masks)
    for X in range(1 << 7):
        if not masks[X]:
            continue
        expected = set(oracle_neighbors(oracle_family, X, 7, mode="both"))
        assert set(engine.neighbors(X)) == expected


def masks_to_family(masks):
    return {mask for mask, ok in enumerate(masks) if ok}


def test_matching_subset_dp_matches_independent_oracle_on_all_graphs_n5():
    n = 5
    pairs = list(combinations(range(n), 2))
    for code in range(1 << len(pairs)):
        edges = [pairs[i] for i in range(len(pairs)) if (code >> i) & 1]
        G = MatchingGraph.from_edges(range(n), edges)
        actual = G.feasible_masks()

        adj = [0] * n
        for u, v in edges:
            adj[u] |= 1 << v
            adj[v] |= 1 << u

        expected = pm_family_dp(n, adj)
        assert actual == expected


def test_modular_determinant_matches_independent_oracle():
    matrices = (
        ((1, 2), (3, 4)),
        ((0, 1, 2), (3, 4, 5), (6, 7, 8)),
        ((5, -2, 7, 11), (3, 4, -9, 2), (8, 1, 6, -4), (0, 3, 5, 7)),
    )
    p = 101
    for matrix in matrices:
        assert det_mod(matrix, p) == det_mod_p(matrix, p)
