from delta_matroid import MatchingGraph, complete_graph


def test_k4_matching_family():
    D = complete_graph(4).delta_matroid()
    assert len(D.feasible_sets) == 8
    assert D.is_even()
    assert D.verify_wenzel() is None


def test_k3_disjoint_k3_has_no_full_feasible_set():
    edges = [(0,1),(0,2),(1,2),(3,4),(3,5),(4,5)]
    G = MatchingGraph.from_edges(range(6), edges)
    D = G.delta_matroid()
    assert len(D.feasible_sets) == 16
    assert frozenset(range(6)) not in D.feasible_sets
    assert D.verify_wenzel() is None


def test_c6():
    D = MatchingGraph.from_edges(
        range(6),
        [(i,(i+1)%6) for i in range(6)]
    ).delta_matroid()
    assert D.is_even()
    assert D.verify_wenzel() is None
