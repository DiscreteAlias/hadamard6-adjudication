"""Family membership closure. Track B.

The known order-6 landscape (source-cached in checks/lib/catalogue.py):
  K6^(3)  = ALL H2-reducible matrices (Karlsson 1003.4133/1003.4177: a 6x6 CHM
            with one 2x2 Hadamard submatrix is H2-reducible, and the
            H2-reducible matrices are exactly the three-parameter family).
            Every named 1-2 parameter family (F6(a,b), F6^T, D6(c), B6, M6(x),
            X6^(2), K6^(2)) lies inside it.
  G6^(4)  = Szollosi's generic four-parameter family (Dilation Algorithm).
  S6      = Tao's isolated matrix.

Closure cascade for a candidate H (exact at every step):
  1. chirality -1 minor present -> constructive H2-block certificate: exhibit
     the row/column pairing making all nine 2x2 blocks Hadamard. With
     Karlsson's classification, that certificate closes H as member-K6^(3).
     A minor WITHOUT a certificate goes to the monitored bucket
     "H2-signature, no K6 witness" (decoder bug or theorem issue; loud).
  2. no minor -> try exact equivalence to S6 (all four variants).
  3. remaining -> G6^(4) membership via the Dilation Algorithm (day-3 tool)
     or unresolved-G6.
Fast path before 1: equivalence against a quick reference list (exact certs).
"""

from itertools import combinations

import sympy as sp

from .equivalence import equivalent_any_variant
from .invariants import invariants_bundle
from .numfield import entry_pairs


def _pmul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def _pconj(a):
    return (a[0], -a[1])


_PAIRINGS = [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]


def h2_block_certificate(H, minor=None):
    """Constructive H2-reducibility certificate: a partition of rows and
    columns into pairs such that all nine 2x2 blocks have chirality -1
    (each block proportional to a 2x2 Hadamard). Exact arithmetic.

    Returns {"row_pairs": [...], "col_pairs": [...]} or None.
    """
    H = sp.Matrix(H)
    K, P = entry_pairs(H)
    mone = (K.from_sympy(sp.Integer(-1)), K.zero)

    def chirality_is_minus1(r0, r1, c0, c1):
        v = _pmul(_pmul(P[r0][c0], P[r1][c1]),
                  _pconj(_pmul(P[r0][c1], P[r1][c0])))
        return v == mone

    rows_all = list(range(6))
    cols_all = list(range(6))

    def pairings(items, first_pair=None):
        out = []
        if first_pair:
            rest = [x for x in items if x not in first_pair]
            for (a, b), (c, d) in [(( rest[p[0][0]], rest[p[0][1]]),
                                    (rest[p[1][0]], rest[p[1][1]]))
                                   for p in _PAIRINGS]:
                out.append([tuple(first_pair), (a, b), (c, d)])
        else:
            for i in range(1, 6):
                fp = (0, items[i])
                rest = [x for x in items if x not in fp]
                for p in _PAIRINGS:
                    out.append([fp, (rest[p[0][0]], rest[p[0][1]]),
                                (rest[p[1][0]], rest[p[1][1]])])
        return out

    row_first = tuple(minor[0]) if minor else None
    col_first = tuple(minor[1]) if minor else None
    for rp in pairings(rows_all, row_first):
        for cp in pairings(cols_all, col_first):
            if all(chirality_is_minus1(r[0], r[1], c[0], c[1])
                   for r in rp for c in cp):
                return {"row_pairs": [list(x) for x in rp],
                        "col_pairs": [list(x) for x in cp]}
    return None


def verify_h2_certificate(H, cert):
    """Re-verify a block certificate from scratch (exact)."""
    H = sp.Matrix(H)
    K, P = entry_pairs(H)
    mone = (K.from_sympy(sp.Integer(-1)), K.zero)
    for r in cert["row_pairs"]:
        for c in cert["col_pairs"]:
            v = _pmul(_pmul(P[r[0]][c[0]], P[r[1]][c[1]]),
                      _pconj(_pmul(P[r[0]][c[1]], P[r[1]][c[0]])))
            if v != mone:
                return False
    return True


def close_candidate(H, bundle=None, quick_refs=(), s6=None):
    """Closure cascade. Returns (verdict, detail dict).

    verdict in {"closed:equivalent", "closed:member-K6(3)",
                "closed:equivalent-S6", "bucket:h2-no-witness", "open"}.
    """
    H = sp.Matrix(H)
    bundle = bundle or invariants_bundle(H)

    for name, R in quick_refs:
        hit = equivalent_any_variant(H, R, bundle)
        if hit:
            return "closed:equivalent", {"ref": name, "variant": hit[0],
                                         "cert": hit[1]}

    if bundle["h2_minors"]:
        minor = bundle["h2_minors"][0]
        cert = h2_block_certificate(H, minor)
        if cert and verify_h2_certificate(H, cert):
            return "closed:member-K6(3)", {"block_cert": cert,
                                           "minor": [list(minor[0]), list(minor[1])],
                                           "basis": "Karlsson 1003.4133/1003.4177"}
        return "bucket:h2-no-witness", {"minor": [list(minor[0]), list(minor[1])]}

    if s6 is not None:
        hit = equivalent_any_variant(H, s6, bundle)
        if hit:
            return "closed:equivalent-S6", {"variant": hit[0], "cert": hit[1]}

    return "open", {}
