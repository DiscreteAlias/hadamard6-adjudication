"""Butson-mode exponent arithmetic in Z[x]/Phi_q(x). Track B.

A BH(6, q) candidate is a 6x6 integer matrix of exponents over Z_q; the actual
matrix is zeta_q**E. Everything here is pure integer arithmetic -- sympy appears
only to fetch cyclotomic polynomial coefficients and to lift survivors.

Vanishing test: sum of zeta^{e_i} == 0 iff the coefficient polynomial reduces to
zero mod Phi_q. Rows orthogonal iff the entrywise exponent difference vanishes.
"""

from functools import lru_cache
from itertools import product

import sympy as sp


@lru_cache(maxsize=None)
def phi_coeffs(q):
    """Integer coefficients of Phi_q, leading first."""
    x = sp.Symbol("x")
    p = sp.Poly(sp.cyclotomic_poly(q, x), x)
    return tuple(int(c) for c in p.all_coeffs())


def vanishes(exponents, q):
    """Does sum_i zeta_q^{e_i} == 0? Exact, integers only."""
    phi = phi_coeffs(q)
    deg = len(phi) - 1
    c = [0] * q
    for e in exponents:
        c[e % q] += 1
    for k in range(q - 1, deg - 1, -1):
        f = c[k]
        if f:
            c[k] = 0
            for j in range(1, deg + 1):
                c[k - j] -= f * phi[j]
    return all(v == 0 for v in c[:deg])


@lru_cache(maxsize=None)
def vanishing_rows(q):
    """All dephased rows (0, e2..e6) with 1 + sum zeta^{e_i} == 0, lex order."""
    out = []
    for es in product(range(q), repeat=5):
        if vanishes((0,) + es, q):
            out.append((0,) + es)
    return tuple(out)


def rows_orthogonal(a, b, q):
    """<zeta^a, zeta^b> == 0, i.e. the difference row vanishes."""
    return vanishes(tuple((x - y) % q for x, y in zip(a, b)), q)


def enumerate_bh6(q):
    """All dephased BH(6, q) exponent matrices with lex-increasing rows 2..6.

    Row 1 is all zeros; rows 2..6 come from vanishing_rows(q), strictly
    increasing lexicographically (quotients row permutations), pairwise
    orthogonal. Bitset candidate propagation; exact integer arithmetic only.
    Returns list of 6-tuples of 6-tuples.
    """
    rows = vanishing_rows(q)
    n = len(rows)
    # orthogonality adjacency as bitmasks over row indices
    adj = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if rows_orthogonal(rows[i], rows[j], q):
                adj[i] |= 1 << j
                adj[j] |= 1 << i

    zero = (0,) * 6
    full = (1 << n) - 1
    out = []

    def extend(chosen, cand):
        depth = len(chosen)
        if depth == 5:
            out.append((zero,) + tuple(rows[i] for i in chosen))
            return
        # only rows with index above the last chosen (lex-increasing rows)
        c = cand
        while c:
            k = (c & -c).bit_length() - 1
            c &= c - 1
            chosen.append(k)
            # candidates above k, orthogonal to everything chosen
            extend(chosen, cand & adj[k] & (full << (k + 1)))
            chosen.pop()

    extend([], full)
    return out


def canonical_exp(mat, q):
    """Canonical form under the q-th-root monomial equivalence group:
    row/col permutations and row/col exponent shifts.

    min over (column permutation tau, pivot row r) of:
      dephase columns by row r, dephase rows by column 0, sort rows.
    """
    from itertools import permutations

    best = None
    rows6 = range(6)
    for tau in permutations(range(6)):
        m = [[mat[i][tau[j]] for j in range(6)] for i in rows6]
        for r in rows6:
            piv = m[r]
            d = [[(m[i][j] - piv[j]) % q for j in range(6)] for i in rows6]
            d = [tuple((row[j] - row[0]) % q for j in range(6)) for row in d]
            d = tuple(sorted(d))
            if best is None or d < best:
                best = d
    return best


def to_sympy(mat, q):
    """Lift an exponent matrix to the exact sympy matrix zeta_q**E."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "checks" / "lib"))
    from hadamard import butson
    return butson([list(r) for r in mat], q)
