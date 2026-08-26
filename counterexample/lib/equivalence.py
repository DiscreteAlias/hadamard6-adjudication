"""Exact equivalence decider with certificates. Track B.

Equivalence: H2 = D1 P1 H1 P2 D2 (row/col permutations, unimodular diagonals).
Decision by backtracking over the row bijection (pruned by row-pair profile
invariants) then constructive column/diagonal solving. All arithmetic is (re,im)
pairs over one common real field; division by unimodular entries is
multiplication by the conjugate pair, so everything stays in ring ops.

A returned certificate is ALWAYS re-verified from scratch by exact
re-multiplication before being handed out. None means: no equivalence exists
(the search is exhaustive over the finite group), never "gave up".
"""

from collections import Counter
from itertools import permutations

import sympy as sp

from .invariants import invariants_bundle
from .numfield import entry_pairs, real_field_for


def _pmul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def _pconj(a):
    return (a[0], -a[1])


def four_variants(H):
    H = sp.Matrix(H)
    yield "id", H
    yield "T", H.T
    yield "C", H.conjugate()
    yield "CT", H.conjugate().T


def _common_pairs(H1, H2):
    K = real_field_for(list(sp.Matrix(H1)) + list(sp.Matrix(H2)))
    _, A = entry_pairs(H1, K)
    _, B = entry_pairs(H2, K)
    return K, A, B


def equivalent(H1, H2, b1=None, b2=None):
    """Certificate dict or None. Exhaustive, exact."""
    H1, H2 = sp.Matrix(H1), sp.Matrix(H2)
    n = H1.rows
    b1 = b1 or invariants_bundle(H1)
    b2 = b2 or invariants_bundle(H2)
    if b1["fingerprint"] != b2["fingerprint"]:
        return None

    prof1, prof2 = b1["profiles"], b2["profiles"]
    sig1 = {r: Counter(prof1[(r, k)] for k in range(n) if k != r) for r in range(n)}
    sig2 = {r: Counter(prof2[(r, k)] for k in range(n) if k != r) for r in range(n)}

    K, A, B = _common_pairs(H1, H2)
    one = (K.one, K.zero)

    # row backtracking: p[i] = row of H1 matched to row i of H2
    def try_columns(p):
        # solve H2[i,j] = d_i e_j A[p[i], tau[j]]
        for c0 in range(n):
            # q_i = H2[i,0] / A[p[i], c0] = d_i * e_0
            q = [_pmul(B[i][0], _pconj(A[p[i]][c0])) for i in range(n)]
            tau = [None] * n
            tau[0] = c0
            used = {c0}
            w = [None] * n          # w[j] = e_j / e_0
            w[0] = one

            def place(j):
                if j == n:
                    return True
                for c in range(n):
                    if c in used:
                        continue
                    # candidate w_j from row 0, verify rows 1..n-1
                    wj = _pmul(_pmul(B[0][j], _pconj(A[p[0]][c])), _pconj(q[0]))
                    okc = True
                    for i in range(1, n):
                        lhs = B[i][j]
                        rhs = _pmul(_pmul(q[i], wj), A[p[i]][c])
                        if lhs != rhs:
                            okc = False
                            break
                    if okc:
                        tau[j] = c
                        used.add(c)
                        w[j] = wj
                        if place(j + 1):
                            return True
                        used.remove(c)
                        tau[j] = None
                return False

            if place(1):
                d = q                        # with e_0 = 1
                e = w
                return tau, d, e
        return None

    rows_h1 = list(range(n))

    def assign(i, p, used):
        if i == n:
            got = try_columns(p)
            if got:
                tau, d, e = got
                return p[:], tau, d, e
            return None
        for r in rows_h1:
            if r in used:
                continue
            if sig2[i] != sig1[r]:
                continue
            ok = True
            for i2 in range(i):
                if prof2[(i, i2)] != prof1[(r, p[i2])] or prof2[(i2, i)] != prof1[(p[i2], r)]:
                    ok = False
                    break
            if not ok:
                continue
            p.append(r)
            used.add(r)
            got = assign(i + 1, p, used)
            if got:
                return got
            p.pop()
            used.remove(r)
        return None

    got = assign(0, [], set())
    if not got:
        return None

    p, tau, d, e = got

    def to_expr(pair):
        return K.to_sympy(pair[0]) + sp.I * K.to_sympy(pair[1])

    cert = {
        "row_map": list(p),        # H2 row i uses H1 row p[i]
        "col_map": list(tau),      # H2 col j uses H1 col tau[j]
        "d": [to_expr(x) for x in d],
        "e": [to_expr(x) for x in e],
    }
    assert verify_cert(H1, H2, cert), "internal: certificate failed re-verification"
    return cert


def verify_cert(H1, H2, cert):
    """Exact from-scratch check: H2[i,j] == d_i e_j H1[p[i], tau[j]]."""
    H1, H2 = sp.Matrix(H1), sp.Matrix(H2)
    n = H1.rows
    p, tau = cert["row_map"], cert["col_map"]
    d, e = cert["d"], cert["e"]
    entries = list(H1) + list(H2) + list(d) + list(e)
    K = real_field_for(entries)
    _, A = entry_pairs(H1, K)
    _, B = entry_pairs(H2, K)

    def emb(x):
        xr, xi = sp.expand_complex(sp.sympify(x)).as_real_imag()
        return (K.from_sympy(sp.expand(xr)), K.from_sympy(sp.expand(xi)))

    dd = [emb(x) for x in d]
    ee = [emb(x) for x in e]
    for i in range(n):
        for j in range(n):
            lhs = B[i][j]
            rhs = _pmul(_pmul(dd[i], ee[j]), A[p[i]][tau[j]])
            if lhs != rhs:
                return False
    return True


def equivalent_any_variant(Hcand, Href, bcand=None):
    """Try cand against all four variants of ref. Returns (tag, cert) or None."""
    for tag, V in four_variants(Href):
        cert = equivalent(Hcand, V, bcand, None)
        if cert:
            return tag, cert
    return None
