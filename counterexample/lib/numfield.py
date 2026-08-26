"""Common-number-field embedding and exact linear algebra. Track B.

Entries of a candidate matrix are algebraic; their real/imaginary parts live in
a real number field Q(theta). We embed them there and do all linear algebra as
DomainMatrix over QQ.algebraic_field -- sound exact rank, no heuristic zero
tests. This is the defect path that wins on disagreement (slag H6-H4).
"""

from itertools import combinations

import sympy as sp
from sympy.polys.matrices import DomainMatrix

DEGREE_BUDGET = 64

_field_cache = {}


class EscalateError(Exception):
    """Field too large or conversion failed; caller must escalate, not guess."""


def _re_im(e):
    x, y = sp.expand_complex(e).as_real_imag()
    return sp.expand(x), sp.expand(y)


def real_field_for(entries):
    """QQ.algebraic_field containing re/im of every entry. Degree-budgeted."""
    gens = []
    seen = set()
    for e in entries:
        for part in _re_im(e):
            if part.is_Rational:
                continue
            key = sp.srepr(part)
            if key not in seen:
                seen.add(key)
                gens.append(part)
    if not gens:
        return sp.QQ
    gkey = tuple(sorted(sp.srepr(g) for g in gens))
    if gkey in _field_cache:
        return _field_cache[gkey]
    est = 1
    for g in gens:
        est *= sp.minimal_polynomial(g, sp.Symbol("_x")).as_poly().degree()
        if est > DEGREE_BUDGET ** 2:
            break
    # est is only an upper-bound estimate; the real guard is the built field's degree
    K = sp.QQ.algebraic_field(*gens)
    if K.mod.degree() > DEGREE_BUDGET:
        raise EscalateError(f"field degree {K.mod.degree()} exceeds budget {DEGREE_BUDGET}")
    _field_cache[gkey] = K
    return K


def to_K(K, expr):
    try:
        return K.from_sympy(expr)
    except Exception as exc:  # CoercionFailed and friends
        raise EscalateError(f"cannot embed {expr} in field: {exc}") from exc


def entry_pairs(H, K=None):
    """(K, 6x6 list of (x, y) K-element pairs) for a sympy matrix."""
    H = sp.Matrix(H)
    if K is None:
        K = real_field_for(list(H))
    pairs = []
    for i in range(H.rows):
        row = []
        for j in range(H.cols):
            x, y = _re_im(H[i, j])
            row.append((to_K(K, x), to_K(K, y)))
        pairs.append(row)
    return K, pairs


def rank_K(K, rows):
    """Exact rank of a matrix given as list of lists of K elements."""
    m, n = len(rows), len(rows[0])
    dm = DomainMatrix(rows, (m, n), K)
    return dm.rank()


def nullspace_K(K, rows):
    """Exact nullspace basis (list of row vectors of K elements)."""
    m, n = len(rows), len(rows[0])
    dm = DomainMatrix(rows, (m, n), K)
    ns = dm.nullspace()
    return [[ns[i, j] for j in range(ns.shape[1])] for i in range(ns.shape[0])]


def defect_system(K, pairs, n=6):
    """The Tadej-Zyczkowski 30x36 real system, entries in K.

    Same construction as checks/lib/hadamard.py defect(): for each row pair
    j < l, the real and imaginary parts of H[j,k] * conj(H[l,k]) enter columns
    j*n+k (+) and l*n+k (-).
    """
    zero = K.zero
    rows = []
    for j, l in combinations(range(n), 2):
        re_row = [zero] * (n * n)
        im_row = [zero] * (n * n)
        for k in range(n):
            a, b = pairs[j][k]
            c, d = pairs[l][k]
            cr = a * c + b * d          # Re((a+bi)(c-di))
            ci = b * c - a * d          # Im((a+bi)(c-di))
            re_row[j * n + k] += cr
            re_row[l * n + k] -= cr
            im_row[j * n + k] += ci
            im_row[l * n + k] -= ci
        rows.append(re_row)
        rows.append(im_row)
    return rows


def fast_defect(H, return_rank=False):
    """Exact defect via DomainMatrix over an explicit real algebraic field."""
    H = sp.Matrix(H)
    n = H.rows
    K, pairs = entry_pairs(H)
    rows = defect_system(K, pairs, n)
    r = rank_K(K, rows)
    d = (n * n - r) - (2 * n - 1)
    return (d, r) if return_rank else d
