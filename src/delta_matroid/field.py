from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import random
from typing import Sequence


@lru_cache(maxsize=32)
def _is_prime(p: int) -> bool:
    """Deterministic trial-division primality test for the configured modulus."""
    if not isinstance(p, int) or p <= 1:
        return False
    if p <= 3:
        return True
    if p % 2 == 0:
        return False
    d = 3
    while d * d <= p:
        if p % d == 0:
            return False
        d += 2
    return True


def _require_prime(p: int) -> None:
    if not _is_prime(p):
        raise ValueError("p must be prime")
    if p == 2:
        raise ValueError("p must be an odd prime")


class SingularMatrixError(ValueError):
    pass


def det_mod_p(matrix: Sequence[Sequence[int]], p: int) -> int:
    """Exact determinant over the odd prime field F_p."""
    _require_prime(p)
    n = len(matrix)
    if any(not isinstance(x, int) for row in matrix for x in row):
        raise TypeError("matrix entries must be integers")
    if n == 0:
        return 1
    if any(len(row) != n for row in matrix):
        raise ValueError("Matrix must be square.")
    A = [[x % p for x in row] for row in matrix]
    det = 1
    for col in range(n):
        pivot = next((r for r in range(col, n) if A[r][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            A[col], A[pivot] = A[pivot], A[col]
            det = (-det) % p
        pivot_value = A[col][col]
        det = (det * pivot_value) % p
        inv = pow(pivot_value, p - 2, p)
        for r in range(col + 1, n):
            if A[r][col] == 0:
                continue
            factor = A[r][col] * inv % p
            for c in range(col, n):
                A[r][c] = (A[r][c] - factor * A[col][c]) % p
    return det


def inverse_mod_p(matrix: Sequence[Sequence[int]], p: int) -> list[list[int]]:
    """Exact matrix inverse over the odd prime field F_p."""
    _require_prime(p)
    n = len(matrix)
    if any(not isinstance(x, int) for row in matrix for x in row):
        raise TypeError("matrix entries must be integers")
    if n == 0:
        return []
    if any(len(row) != n for row in matrix):
        raise ValueError("Matrix must be square.")
    A = [
        [x % p for x in row] + [1 if i == j else 0 for j in range(n)]
        for i, row in enumerate(matrix)
    ]
    for col in range(n):
        pivot = next((r for r in range(col, n) if A[r][col]), None)
        if pivot is None:
            raise SingularMatrixError("Matrix is singular over F_p.")
        if pivot != col:
            A[col], A[pivot] = A[pivot], A[col]
        inv = pow(A[col][col], p - 2, p)
        A[col] = [(x * inv) % p for x in A[col]]
        for r in range(n):
            if r == col or A[r][col] == 0:
                continue
            factor = A[r][col]
            A[r] = [(x - factor * y) % p for x, y in zip(A[r], A[col])]
    return [row[n:] for row in A]


def matmul_mod(A: Sequence[Sequence[int]], B: Sequence[Sequence[int]], p: int) -> list[list[int]]:
    _require_prime(p)
    if any(not isinstance(x, int) for row in A for x in row) or any(not isinstance(x, int) for row in B for x in row):
        raise TypeError("matrix entries must be integers")
    if not A or not B:
        return []
    n, k, m = len(A), len(B), len(B[0])
    if len(A[0]) != k or any(len(row) != m for row in B):
        raise ValueError("Incompatible matrix shapes.")
    return [[sum(A[i][t] * B[t][j] for t in range(k)) % p for j in range(m)] for i in range(n)]


@dataclass(frozen=True)
class GlobalTutteMatrix:
    vertices: tuple[int, ...]
    matrix: tuple[tuple[int, ...], ...]
    prime: int

    def __post_init__(self):
        _require_prime(self.prime)
        n = len(self.vertices)
        if self.vertices != tuple(range(n)):
            raise ValueError("GlobalTutteMatrix vertices must be canonical indices 0..n-1")
        if len(self.matrix) != n or any(len(row) != n for row in self.matrix):
            raise ValueError("GlobalTutteMatrix.matrix must be square")
        if any(not isinstance(x, int) for row in self.matrix for x in row):
            raise TypeError("GlobalTutteMatrix entries must be integers")
        for i in range(n):
            if self.matrix[i][i] % self.prime != 0:
                raise ValueError("Tutte matrix diagonal must be zero")
            for j in range(i + 1, n):
                if (self.matrix[i][j] + self.matrix[j][i]) % self.prime != 0:
                    raise ValueError("Tutte matrix must be skew-symmetric")

    @classmethod
    def sample(
        cls,
        adjacency: Sequence[Sequence[int]],
        prime: int = 1_000_000_007,
        seed: int | None = None,
    ) -> "GlobalTutteMatrix":
        n = len(adjacency)
        if any(len(row) != n for row in adjacency):
            raise ValueError("Adjacency matrix must be square.")
        _require_prime(prime)
        rng = random.Random(seed)
        T = [[0] * n for _ in range(n)]
        for i in range(n):
            if adjacency[i][i]:
                raise ValueError("Simple graph expected: adjacency diagonal must be zero.")
            for j in range(i + 1, n):
                if adjacency[i][j] != adjacency[j][i]:
                    raise ValueError("Adjacency matrix must be symmetric.")
                if adjacency[i][j]:
                    x = rng.randrange(1, prime)
                    T[i][j] = x
                    T[j][i] = (-x) % prime
        return cls(tuple(range(n)), tuple(tuple(row) for row in T), prime)

    def principal(self, subset: Sequence[int]) -> list[list[int]]:
        subset = tuple(subset)
        if any(i < 0 or i >= len(self.vertices) for i in subset):
            raise ValueError("subset contains a vertex outside the matrix")
        if len(set(subset)) != len(subset):
            raise ValueError("subset must not contain duplicate vertices")
        return [[self.matrix[i][j] for j in subset] for i in subset]

    def certify_feasible(self, subset: Sequence[int]) -> bool:
        return det_mod_p(self.principal(subset), self.prime) != 0

    def ppt(self, subset: Sequence[int]) -> tuple[int, list[list[int]]]:
        A = tuple(subset)
        rest = tuple(v for v in self.vertices if v not in A)
        TAA = self.principal(A)
        det_A = det_mod_p(TAA, self.prime)
        if det_A == 0:
            raise SingularMatrixError("T[A] is singular; PPT is undefined for this sampled matrix.")
        inv_A = inverse_mod_p(TAA, self.prime)
        TBB = [[self.matrix[i][j] for j in rest] for i in rest]
        TBA = [[self.matrix[i][j] for j in A] for i in rest]
        TAB = [[self.matrix[i][j] for j in rest] for i in A]
        left = [
            [sum(TBA[i][t] * inv_A[t][j] for t in range(len(A))) % self.prime for j in range(len(A))]
            for i in range(len(rest))
        ]
        correction = [
            [sum(left[i][t] * TAB[t][j] for t in range(len(A))) % self.prime for j in range(len(rest))]
            for i in range(len(rest))
        ]
        S = [
            [(TBB[i][j] - correction[i][j]) % self.prime for j in range(len(rest))]
            for i in range(len(rest))
        ]
        return det_A, S

    def pair_extension_certificate(self, subset: Sequence[int], u: int, v: int) -> bool:
        A = tuple(subset)
        if u in A or v in A or u == v:
            raise ValueError("u and v must be distinct vertices outside A.")
        _, S = self.ppt(A)
        rest = [x for x in self.vertices if x not in A]
        iu, iv = rest.index(u), rest.index(v)
        return S[iu][iv] % self.prime != 0
