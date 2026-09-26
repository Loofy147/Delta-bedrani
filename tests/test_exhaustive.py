from itertools import combinations
from delta_matroid import MatchingGraph


def all_graphs(n):
    pairs = list(combinations(range(n), 2))
    for code in range(1 << len(pairs)):
        edges = [pairs[i] for i in range(len(pairs)) if (code >> i) & 1]
        yield edges


def test_all_labeled_graphs_n4_n5():
    total = 0
    for n in (4, 5):
        for edges in all_graphs(n):
            D = MatchingGraph.from_edges(range(n), edges).delta_matroid()
            assert D.is_even()
            assert D.verify_delta_axiom() is None
            assert D.verify_wenzel() is None
            total += 1
    assert total == 1088
