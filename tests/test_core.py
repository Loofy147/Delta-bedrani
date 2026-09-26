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
