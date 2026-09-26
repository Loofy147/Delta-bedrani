from delta_matroid import GlobalTutteMatrix, SingularMatrixError, det_mod_p

P = 1_000_000_007


def k3_union_k3_adjacency():
    A = [[0]*6 for _ in range(6)]
    for u,v in [(0,1),(0,2),(1,2),(3,4),(3,5),(4,5)]:
        A[u][v] = A[v][u] = 1
    return A


def test_exact_zero_for_k3_union_k3():
    A = k3_union_k3_adjacency()
    for seed in range(100):
        T = GlobalTutteMatrix.sample(A, P, seed=seed)
        assert det_mod_p(T.matrix, P) == 0
        assert not T.certify_feasible(range(6))


def test_ppt_pair_identity():
    A = [[0]*4 for _ in range(4)]
    for u,v in [(0,1),(0,2),(1,2),(2,3),(1,3)]:
        A[u][v] = A[v][u] = 1
    T = GlobalTutteMatrix.sample(A, P, seed=7)
    subset = (0,1)
    try:
        det_A, S = T.ppt(subset)
    except SingularMatrixError:
        return
    lhs = det_mod_p(T.principal((0,1,2,3)), P)
    rhs = (det_A * (S[0][0]*S[1][1] - S[0][1]*S[1][0])) % P
    assert lhs == rhs
    assert T.pair_extension_certificate(subset, 2, 3) == (S[0][1] % P != 0)
