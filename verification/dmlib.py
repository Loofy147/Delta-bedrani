"""
dmlib.py -- shared utilities for the delta-matroid research suite.

Conventions
-----------
* Ground set [n] = {0..n-1}; a subset is an int bitmask; a "family" (set system)
  is a Python set of ints.  Nothing here depends on the uploaded package, so the
  package can be tested *against* these independent implementations.
* "even" follows the literature (Bouchet; Calvert-Dermenjian-Fink-Smith 2026):
  all members have the SAME PARITY of cardinality (not: all cardinalities even).
"""
from __future__ import annotations
import itertools, json, hashlib, sys, time, platform
from fractions import Fraction
from collections import deque

def pc(x: int) -> int:
    return x.bit_count()

def bits(x: int):
    out = []
    while x:
        b = x & -x
        out.append(b)
        x ^= b
    return out

def is_delta(F) -> bool:
    if not F:
        return False
    for A in F:
        for B in F:
            if A == B:
                continue
            bl = bits(A ^ B)
            for x in bl:
                for y in bl:
                    if (A ^ (x | y)) in F:
                        break
                else:
                    return False
    return True

def single_strong(F) -> bool:
    for A in F:
        for B in F:
            if A == B:
                continue
            bl = bits(A ^ B)
            for x in bl:
                if not any(y != x and (A ^ (x | y)) in F for y in bl):
                    return False
    return True

def wenzel(F) -> bool:
    for A in F:
        for B in F:
            if A == B:
                continue
            bl = bits(A ^ B)
            for x in bl:
                if not any(y != x and (A ^ (x | y)) in F and (B ^ (x | y)) in F for y in bl):
                    return False
    return True

def weak_wenzel(F) -> bool:
    for A in F:
        for B in F:
            if A == B:
                continue
            bl = bits(A ^ B)
            for x in bl:
                if not any((A ^ (x | y)) in F and (B ^ (x | y)) in F for y in bl):
                    return False
    return True

def hyperplane_even(F) -> bool:
    for A in F:
        for B in F:
            if A == B:
                continue
            bl = bits(A ^ B)
            if not any((A ^ (x | y)) in F and (B ^ (x | y)) in F
                       for x, y in itertools.combinations(bl, 2)):
                return False
    return True

def hyperplane_delta(F) -> bool:
    for A in F:
        for B in F:
            if A == B:
                continue
            bl = bits(A ^ B)
            if not any((A ^ (x | y)) in F and (B ^ (x | y)) in F
                       for x in bl for y in bl):
                return False
    return True

def basis_exchange(F) -> bool:
    for A in F:
        for B in F:
            for a in bits(A & ~B):
                if not any(((A ^ a) | b) in F for b in bits(B & ~A)):
                    return False
    return True

def parities(F):
    return {pc(s) & 1 for s in F}

def is_even_sys(F) -> bool:
    return len(parities(F)) <= 1

def all_card_even(F) -> bool:
    return all(pc(s) % 2 == 0 for s in F)

def equicardinal(F) -> bool:
    return len({pc(s) for s in F}) <= 1

def lift(F, n):
    star = 1 << n
    return {(s | star) if (pc(s) & 1) else s for s in F}

def antipode_strong(F) -> bool:
    groups = {}
    Fl = list(F)
    for i in range(len(Fl)):
        for j in range(i + 1, len(Fl)):
            I, J = Fl[i], Fl[j]
            if pc(I ^ J) >= 3:
                groups.setdefault((I & J, I | J), 0)
                groups[(I & J, I | J)] += 1
    return all(c >= 2 for c in groups.values())

def twist(F, X):
    return {s ^ X for s in F}

def parity_split(F):
    return ({s for s in F if pc(s) % 2 == 0}, {s for s in F if pc(s) % 2 == 1})

def turn1_weak_verifier(F) -> bool:
    order = sorted(F, key=lambda s: (pc(s), s))
    for i in range(len(order)):
        for j in range(i + 1, len(order)):
            A, B = order[i], order[j]
            bl = bits(A ^ B)
            for x in bl:
                if not any((A ^ (x | y)) in F for y in bl):
                    return False
    return True

def loops_of(F):
    u = 0
    for s in F:
        u |= s
    return None if not F else u

def neighbors(F, X, n, mode="both"):
    out = []
    for i in range(n):
        b = 1 << i
        if mode in ("both", "single"):
            Y = X ^ b
            if Y in F:
                out.append(Y)
        if mode in ("both", "pair"):
            for j in range(i + 1, n):
                Y2 = X ^ (b | (1 << j))
                if Y2 in F:
                    out.append(Y2)
    return out

def all_pairs_dist(F, n):
    Fl = list(F)
    adj = {X: neighbors(F, X, n) for X in Fl}
    dist = {}
    for s in Fl:
        d = {s: 0}
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in d:
                    d[v] = d[u] + 1
                    q.append(v)
        dist[s] = d
    return dist, adj

def monotone_dist(F, adj, B):
    order = sorted(F, key=lambda X: pc(X ^ B))
    INF = 10**9
    dm = {}
    for X in order:
        if X == B:
            dm[X] = 0
            continue
        best = INF
        for Y in adj[X]:
            if pc(Y ^ B) < pc(X ^ B) and dm.get(Y, INF) + 1 < best:
                best = dm[Y] + 1
        dm[X] = best
    return dm

def _rref_solve(cols, v):
    d, k = len(v), len(cols)
    M = [[Fraction(cols[j][i]) for j in range(k)] + [Fraction(v[i])] for i in range(d)]
    r = 0
    for c in range(k):
        p = None
        for i in range(r, d):
            if M[i][c] != 0:
                p = i
                break
        if p is None:
            return None
        M[r], M[p] = M[p], M[r]
        inv = 1 / M[r][c]
        M[r] = [x * inv for x in M[r]]
        for i in range(d):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        r += 1
    for i in range(r, d):
        if M[i][k] != 0:
            return None
    return [M[i][k] for i in range(k)]

def in_cone(v, gens):
    if not any(v):
        return True
    gens = list(set(gens))
    for k in range(1, min(len(v), len(gens)) + 1):
        for sub in itertools.combinations(gens, k):
            sol = _rref_solve(sub, v)
            if sol is not None and all(x >= 0 for x in sol):
                return True
    return False

def vdiff(X, Y, n):
    return tuple(((Y >> i) & 1) - ((X >> i) & 1) for i in range(n))

def locally_exact(F, n) -> bool:
    for X in F:
        near = [vdiff(X, Y, n) for Y in F if 1 <= pc(X ^ Y) <= 2]
        for Y in F:
            if pc(X ^ Y) > 2 and not in_cone(vdiff(X, Y, n), near):
                return False
    return True

def score(X, w):
    return sum(w[i] for i in range(len(w)) if (X >> i) & 1)

def local_search(F, n, w, start, mode="both"):
    cur, sc = start, score(start, w)
    while True:
        best, bs = None, sc
        for Y in neighbors(F, cur, n, mode):
            s = score(Y, w)
            if s > bs:
                best, bs = Y, s
        if best is None:
            return cur, sc
        cur, sc = best, bs

def brute_opt(F, w):
    return max(score(X, w) for X in F)

def signed_greedy(F, n, w, tie_order=None):
    N = sum(1 << i for i in range(n) if w[i] < 0)
    FT = [X ^ N for X in F]
    idx = list(range(n)) if tie_order is None else list(tie_order)
    idx.sort(key=lambda i: -abs(w[i]))
    S = T = 0
    def sep(S, T):
        return any((X & S) == S and (X & T) == 0 for X in FT)
    for i in idx:
        b = 1 << i
        if sep(S | b, T):
            S |= b
        else:
            T |= b
    return S ^ N

def det_mod(M, p):
    n = len(M)
    A = [[x % p for x in row] for row in M]
    det = 1
    for c in range(n):
        piv = None
        for r in range(c, n):
            if A[r][c] % p:
                piv = r
                break
        if piv is None:
            return 0
        if piv != c:
            A[c], A[piv] = A[piv], A[c]
            det = -det
        det = det * A[c][c] % p
        inv = pow(A[c][c], p - 2, p)
        for r in range(c + 1, n):
            f = A[r][c] * inv % p
            if f:
                for k in range(c, n):
                    A[r][k] = (A[r][k] - f * A[c][k]) % p
    return det % p

def pf_mod(A, idx, p):
    if not idx:
        return 1
    i0 = idx[0]
    tot = 0
    for k in range(1, len(idx)):
        j = idx[k]
        rest = idx[1:k] + idx[k + 1:]
        t = A[i0][j] * pf_mod(A, rest, p)
        tot += t if (k % 2 == 1) else -t
    return tot % p

def gf2_nonsingular_sub(rows, idxs):
    k = len(idxs)
    if k == 0:
        return True
    sub = []
    for i in idxs:
        r = rows[i]
        b = 0
        for pos, j in enumerate(idxs):
            if (r >> j) & 1:
                b |= 1 << pos
        sub.append(b)
    rank = 0
    for col in range(k):
        bit = 1 << col
        piv = None
        for i in range(rank, k):
            if sub[i] & bit:
                piv = i
                break
        if piv is None:
            return False
        sub[rank], sub[piv] = sub[piv], sub[rank]
        for i in range(k):
            if i != rank and sub[i] & bit:
                sub[i] ^= sub[rank]
        rank += 1
    return True

def subset_indices(n):
    return [[i for i in range(n) if (S >> i) & 1] for S in range(1 << n)]

def family_gf2(rows, n, SI=None):
    SI = SI or subset_indices(n)
    return {S for S in range(1 << n) if gf2_nonsingular_sub(rows, SI[S])}

def binary_representable(F, n):
    SI = subset_indices(n)
    for X in F:
        G = twist(F, X)
        rows = [0] * n
        d = [1 if (1 << i) in G else 0 for i in range(n)]
        for i in range(n):
            if d[i]:
                rows[i] |= 1 << i
        for i in range(n):
            for j in range(i + 1, n):
                both = 1 if ((1 << i) | (1 << j)) in G else 0
                aij = both ^ (d[i] & d[j])
                if aij:
                    rows[i] |= 1 << j
                    rows[j] |= 1 << i
        if family_gf2(rows, n, SI) == G:
            return True
    return False

def skew_family_modp(A, n, p):
    return {S for S in range(1 << n)
            if pc(S) % 2 == 0 and pf_mod(A, tuple(i for i in range(n) if (S >> i) & 1), p) != 0}

def ternary_representable(F, n, p=3, cap=1 << 14):
    if p != 3:
        raise ValueError("only GF(3) implemented")
    for X in F:
        G = twist(F, X)
        if not all(pc(s) % 2 == 0 for s in G):
            continue
        edges = [(i, j) for i in range(n) for j in range(i + 1, n) if ((1 << i) | (1 << j)) in G]
        parent = list(range(n))
        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        tree, other = [], []
        for (i, j) in edges:
            ri, rj = find(i), find(j)
            if ri != rj:
                parent[ri] = rj
                tree.append((i, j))
            else:
                other.append((i, j))
        if (1 << len(other)) > cap:
            return None
        for signs in itertools.product((1, 2), repeat=len(other)):
            A = [[0] * n for _ in range(n)]
            for (i, j) in tree:
                A[i][j], A[j][i] = 1, 2
            for (i, j), s in zip(other, signs):
                A[i][j], A[j][i] = s, (-s) % 3
            if skew_family_modp(A, n, 3) == G:
                return True
    return False

def pm_family_dp(n, adjmask):
    N = 1 << n
    feas = bytearray(N)
    feas[0] = 1
    for mask in range(1, N):
        if mask.bit_count() & 1:
            continue
        low = mask & -mask
        v = low.bit_length() - 1
        rest = mask ^ low
        nb = adjmask[v] & rest
        while nb:
            b = nb & -nb
            if feas[rest ^ b]:
                feas[mask] = 1
                break
            nb ^= b
    return feas

def count_pm(n, adjmask):
    from functools import lru_cache
    @lru_cache(maxsize=None)
    def c(mask):
        if mask == 0:
            return 1
        low = mask & -mask
        v = low.bit_length() - 1
        rest = mask ^ low
        nb = adjmask[v] & rest
        tot = 0
        while nb:
            b = nb & -nb
            tot += c(rest ^ b)
            nb ^= b
        return tot
    return c

def graph_adjmask(G):
    n = G.number_of_nodes()
    adj = [0] * n
    for u, v in G.edges():
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj

def provenance(script_path):
    import numpy, networkx
    h = hashlib.sha256(open(script_path, "rb").read()).hexdigest()[:16]
    return {"script": script_path.split("/")[-1], "sha256_16": h,
            "python": sys.version.split()[0], "platform": platform.platform(),
            "numpy": numpy.__version__, "networkx": networkx.__version__,
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

def save(name, obj):
    with open(f"/home/claude/research/results/{name}.json", "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
