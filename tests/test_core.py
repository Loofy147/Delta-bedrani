import pytest

from delta_matroid import DeltaMatroid


def test_non_even_weak_but_not_even_wenzel():
    D = DeltaMatroid({1, 2, 3}, [set(), {1}, {2}, {3}, {1, 2, 3}])
    assert D.verify_delta_axiom() is None
    assert not D.is_even()
    try:
        D.verify_wenzel()
    except ValueError:
        pass
    else:
        raise AssertionError("non-even family must not use the even Wenzel form")


def test_even_wenzel_family():
    D = DeltaMatroid(range(4), [
        set(), {0,1}, {0,2}, {0,3},
        {1,2}, {1,3}, {2,3}, {0,1,2,3}
    ])
    assert D.is_even()
    assert D.verify_delta_axiom() is None
    assert D.verify_wenzel() is None


def test_twist_and_minor_identities():
    D = DeltaMatroid({1, 2}, [set(), {1, 2}])
    assert D.twist({1}).twist({1}) == D
    assert D.twist({1}).delete(1).feasible_sets == D.contract(1).feasible_sets
    assert D.twist({1}).contract(1).feasible_sets == D.delete(1).feasible_sets


def test_exchange_graph():
    D = DeltaMatroid(range(4), [
        set(), {0,1}, {0,2}, {0,3},
        {1,2}, {1,3}, {2,3}, {0,1,2,3}
    ])
    assert D.is_exchange_connected()
    path = D.shortest_path(set(), {0,1,2,3})
    assert len(path) == 3
    assert D.diameter() == 2


def test_odd_parity_family_is_even_delta_matroid():
    D = DeltaMatroid({1, 2}, [{1}, {2}])
    assert D.is_even()
    assert D.verify_delta_axiom() is None
    assert D.verify_wenzel() is None


def test_invalid_family_is_rejected_at_construction():
    with pytest.raises(ValueError, match="symmetric exchange"):
        DeltaMatroid({0, 1, 2}, [set(), {0, 1}, {2}])

def test_explicit_diameter_guard():
    D = DeltaMatroid({0, 1, 2, 3}, [
        set(), {0,1}, {0,2}, {0,3},
        {1,2}, {1,3}, {2,3}, {0,1,2,3}
    ])
    try:
        D.diameter(max_vertices=4)
    except ValueError as exc:
        assert "exact diameter disabled" in str(exc)
    else:
        raise AssertionError("explicit diameter guard must reject oversized families")




def test_small_delta_matroid_twist_and_minor_closure():
    subsets = [
        frozenset(i for i in range(3) if mask >> i & 1)
        for mask in range(1 << 3)
    ]

    for family_mask in range(1, 1 << len(subsets)):
        family = [
            subsets[i]
            for i in range(len(subsets))
            if family_mask >> i & 1
        ]
        try:
            D = DeltaMatroid(range(3), family)
        except ValueError:
            continue

        for mask in range(1 << 3):
            X = {i for i in range(3) if mask >> i & 1}
            assert D.twist(X).twist(X) == D

        for e in range(3):
            assert D.delete(e).verify_delta_axiom() is None
            assert D.contract(e).verify_delta_axiom() is None


def test_direct_sum_preserves_delta_matroid_laws():
    left = DeltaMatroid({0, 1}, [set(), {0, 1}])
    right = DeltaMatroid({2, 3}, [set(), {2, 3}])
    D = left.direct_sum(right)

    assert D.groundset == frozenset({0, 1, 2, 3})
    assert D.feasible_sets == frozenset({
        frozenset(),
        frozenset({0, 1}),
        frozenset({2, 3}),
        frozenset({0, 1, 2, 3}),
    })
    assert D.is_even()
    assert D.verify_delta_axiom() is None
    assert D.verify_wenzel() is None

    with pytest.raises(ValueError, match="disjoint"):
        left.direct_sum(DeltaMatroid({1, 2}, [set(), {1, 2}]))
