"""Equivalence invariants in canonical form. Track B.

All products are computed in (re, im) pairs over a common real field K
(numfield), so within-matrix equality is exact coordinate equality. Cross-matrix
objects (fingerprints, profiles) are expressed in algnum labels, which are
canonical across fields and spellings.

fingerprint(H): Counter {label: multiplicity} over all 6^4 Haagerup products.
row_profiles(H): {(j,l): Counter} over ordered row pairs -- pruning keys for the
equivalence decider (invariance: relabeling rows by p maps profile (j,l) to
(p(j), p(l)); columns permute inside the Counter; diagonals cancel).
h2_minors(H): all 2x2 submatrices with chirality product == -1, exactly.
zero3(expr): PROVED_ZERO / PROVED_NONZERO / UNDECIDED. Never guesses.
"""

from collections import Counter

import sympy as sp

from .algnum import label, label_sort_key
from .numfield import entry_pairs
from .qiv import certified_nonzero

ZERO, NONZERO, UNDECIDED = "ZERO", "NONZERO", "UNDECIDED"


def zero3(expr):
    """Three-valued exact zero test. UNDECIDED must be escalated by callers."""
    e = sp.expand(sp.sympify(expr))
    if e == 0:
        return ZERO
    if e.is_Rational:
        return NONZERO
    if certified_nonzero(e):
        return NONZERO
    try:
        mp = sp.minimal_polynomial(e, sp.Symbol("_z"))
    except Exception:
        return UNDECIDED
    return ZERO if mp == sp.Symbol("_z") else NONZERO


# ------------------------------------------------------------- pair utilities

def _pmul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def _pconj(a):
    return (a[0], -a[1])


def haagerup_products(H):
    """(K, {(i,j,k,l): pair}, pair->sympy reconstructor). All 6^4 products."""
    K, pairs = entry_pairs(H)

    def lam(i, j, k, l):
        return _pmul(_pmul(pairs[i][j], pairs[k][l]),
                     _pconj(_pmul(pairs[i][l], pairs[k][j])))

    n = sp.Matrix(H).rows
    prods = {}
    for i in range(n):
        for j in range(n):
            for k in range(n):
                for l in range(n):
                    prods[(i, j, k, l)] = lam(i, j, k, l)

    def to_expr(p):
        return K.to_sympy(p[0]) + sp.I * K.to_sympy(p[1])

    return K, prods, to_expr


def _label_map(prods, to_expr):
    """pair -> algnum label, one label call per distinct value."""
    distinct = {}
    for p in prods.values():
        distinct.setdefault(p, None)
    out = {}
    for p in distinct:
        out[p] = label(to_expr(p))
    return out


def fingerprint(H):
    """Canonical Haagerup multiset: sorted tuple of (label, multiplicity)."""
    _, prods, to_expr = haagerup_products(H)
    lm = _label_map(prods, to_expr)
    c = Counter(lm[p] for p in prods.values())
    return tuple(sorted(c.items(), key=lambda kv: label_sort_key(kv[0])))


def haagerup_set_labels(H):
    """Canonical Haagerup SET (labels only, no multiplicities)."""
    return tuple(sorted({lab for lab, _ in fingerprint(H)}, key=label_sort_key))


def invariants_bundle(H):
    """fingerprint + row profiles + h2 minors in one pass (shared products)."""
    n = sp.Matrix(H).rows
    _, prods, to_expr = haagerup_products(H)
    lm = _label_map(prods, to_expr)

    fp = Counter(lm[p] for p in prods.values())
    fp = tuple(sorted(fp.items(), key=lambda kv: label_sort_key(kv[0])))

    profiles = {}
    for j in range(n):
        for l in range(n):
            if j == l:
                continue
            c = Counter()
            for m in range(n):
                for m2 in range(n):
                    c[lm[prods[(j, m, l, m2)]]] += 1
            profiles[(j, l)] = tuple(sorted(c.items(), key=lambda kv: label_sort_key(kv[0])))

    minus_one = label(sp.Integer(-1))
    minors = []
    for i in range(n):
        for k in range(i + 1, n):
            for j in range(n):
                for l in range(j + 1, n):
                    if lm[prods[(i, j, k, l)]] == minus_one:
                        minors.append(((i, k), (j, l)))
    return {"fingerprint": fp, "profiles": profiles, "h2_minors": tuple(minors)}


def h2_minors(H):
    return invariants_bundle(H)["h2_minors"]


# --------------------------------------------------- sound Hadamard predicate

def is_hadamard_K(H):
    """Exact Hadamard check in field coordinates (no simplify anywhere).

    Returns (ok, why). Sound both ways: coordinate equality in K is exact.
    """
    H = sp.Matrix(H)
    n = H.rows
    K, pairs = entry_pairs(H)
    one, zero = K.one, K.zero
    for i in range(n):
        for j in range(n):
            x, y = pairs[i][j]
            if x * x + y * y != one:
                return False, f"entry ({i},{j}) not unimodular"
    for j in range(n):
        for l in range(j + 1, n):
            sx = zero
            sy = zero
            for k in range(n):
                a, b = pairs[j][k]
                c, d = pairs[l][k]
                sx += a * c + b * d
                sy += b * c - a * d
            if sx != zero or sy != zero:
                return False, f"rows {j},{l} not orthogonal"
    return True, "ok"
