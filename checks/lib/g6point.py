"""Szollosi's explicit generic G6^(4) point, exactly verified.  [SZ 1008.0632v1]

Construction (section "A generic matrix" of the paper): input quadruple
(a, 1/a, c, a) with a a unimodular root of  a^6 + a^4 + 2a^3 + a^2 + 1 = 0,
c = (-a^3+a^2+a+1)/(a(a^3+a^2+a-1)); prescribed C-block g = 1/a, h = a;
(e, s1, s2) the roots of the printed cubic over Q(a); f = U(e)/V(e),
s3 = U(s1)/V(s1), s4 = U(s2)/V(s2); (t1, t2) the unimodular pair with
t1 + t2 = -(1+a+c+g) via the sum-product formula; (t3, t4) the roots of
z^2 - st z + pt with st = a^5+a^3+2a^2-a-1, pt = (11a^5+2a^4-13a^3+44a^2
+19a+40)/67; finally D = -C E^* (B^{-1})^*.

Verification strategy (exact, no floating point, no simplify verdicts):
the five atoms (a, e, s1, t1, t3) satisfy five explicit polynomial RELATIONS
(each a true statement about the chosen roots). Any matrix identity that
reduces to 0 modulo the relation cascade holds for the actual numbers -- a
sound ZERO certificate by pure polynomial arithmetic. Nonzero facts
(denominators, pivots) are certified by exact rational interval boxes around
the chosen roots. Conjugation is substitution atom -> 1/atom, sound because
each atom is separately certified unimodular (its conjugate and reciprocal
boxes isolate the same root of its rational minimal polynomial).

Rank of the defect system is bracketed: pivots box-certified nonzero give
rank >= r; remaining rows reduced to 0 by the cascade give rank <= r.
"""

import sys
from fractions import Fraction
from itertools import combinations
from pathlib import Path

import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qivmini import Box, EncloseError, enclose  # noqa: E402

A, E, S1, T1, T3 = sp.symbols("_g6A _g6E _g6S1 _g6T1 _g6T3")
_VARS = (A, E, S1, T1, T3)
_x = sp.Symbol("_g6x")

_CACHE = {}


# --------------------------------------------------------------- construction

def _coeffs():
    c3 = (-145823 * A ** 5 + 177379 * A ** 4 + 335906 * A ** 3
          + 107524 * A ** 2 + 34729 * A + 182739)
    c2 = (-151183 * A ** 5 + 513285 * A ** 4 + 729716 * A ** 3
          + 258504 * A ** 2 + 142253 * A + 363291)
    c1 = (52821 * A ** 5 + 421725 * A ** 4 + 441134 * A ** 3
          + 177978 * A ** 2 + 144177 * A + 190285)
    c0 = (-21839 * A ** 5 + 186361 * A ** 4 + 235364 * A ** 3
          + 87432 * A ** 2 + 56745 * A + 111701)
    return c3, c2, c1, c0


def _U(t):
    return ((-1 + 23 * A + 12 * A ** 2 + 16 * A ** 3 + 49 * A ** 4 + 45 * A ** 5) * t
            + (-4 + 37 * A + 19 * A ** 2 + 21 * A ** 3 + 79 * A ** 4 + 76 * A ** 5) * t ** 2
            + (-1 + 23 * A + 12 * A ** 2 + 16 * A ** 3 + 49 * A ** 4 + 45 * A ** 5) * t ** 3)


def _V(t):
    return (-21 - 14 * A - 18 * A ** 2 - 48 * A ** 3 - 43 * A ** 4
            + (-59 - 31 * A - 48 * A ** 2 - 128 * A ** 3 - 105 * A ** 4 + 5 * A ** 5) * t
            + (-82 - 23 * A - 52 * A ** 2 - 160 * A ** 3 - 102 * A ** 4 + 47 * A ** 5) * t ** 2
            + (-22 - 5 * A - 13 * A ** 2 - 41 * A ** 3 - 25 * A ** 4 + 16 * A ** 5) * t ** 3)


def _uconj(v):
    """Conjugate of a real-rational-coefficient rational function of the
    unimodular atoms: substitute every atom by its reciprocal."""
    return sp.sympify(v).subs({t: 1 / t for t in _VARS}, simultaneous=True)


def _relations():
    """The five relation polynomials (integer coefficients; each vanishes at
    the chosen atom values) plus auxiliary polynomial data."""
    if "rel" in _CACHE:
        return _CACHE["rel"]
    c3, c2, c1, c0 = _coeffs()
    pa = A ** 6 + A ** 4 + 2 * A ** 3 + A ** 2 + 1
    st = A ** 5 + A ** 3 + 2 * A ** 2 - A - 1
    # sigma = -(1 + a + c + 1/a) with c = cN/cD
    cN = -A ** 3 + A ** 2 + A + 1
    cD = sp.expand(A * (A ** 3 + A ** 2 + A - 1))
    sigN = sp.expand(-((1 + A) * A * cD + A * cN + cD))   # over common den A*cD
    sigD = sp.expand(A * cD)
    # conj(sigma): sigma has real rational coefficients in the unimodular a,
    # so conj(sigma) = sigma(1/a). With degN = deg(sigN), degD = deg(sigD):
    #   conj(sigma) = revN / (A^{degN-degD} revD)   (degN >= degD here),
    # hence sigma/conj(sigma) = A^{degN-degD} sigN revD / (sigD revN).
    def _rev1(p):
        pp = sp.Poly(p, A)
        return sp.expand(A ** pp.degree() * pp.as_expr().subs(A, 1 / A)), pp.degree()
    sigbN, degN = _rev1(sigN)
    sigbD, degD = _rev1(sigD)
    if degN < degD:
        raise RuntimeError("unexpected sigma degree ordering")
    apow = A ** (degN - degD)
    R1 = sp.expand(pa)
    R2 = sp.expand(c3 * E ** 3 + c2 * E ** 2 + c1 * E + c0)
    R3 = sp.expand(c3 * E * S1 ** 2 + E * (c2 + c3 * E) * S1 - c0)
    R4 = sp.expand(sigD * sigbN * T1 ** 2 - sigN * sigbN * T1
                   + apow * sigN * sigbD)
    R5 = sp.expand(67 * T3 ** 2 - 67 * st * T3
                   + (11 * A ** 5 + 2 * A ** 4 - 13 * A ** 3 + 44 * A ** 2
                      + 19 * A + 40))

    # Monicize in each lead variable so the triangular set is a lex Groebner
    # basis and plain-division NF is COMPLETE (pa is irreducible, so every
    # nonzero polynomial in A is invertible mod pa).
    def inv_mod_pa(p):
        return sp.expand(sp.invert(sp.Poly(p, A), sp.Poly(pa, A)).as_expr())

    def red_pa(p):
        return sp.expand(sp.rem(sp.expand(p), pa, A))

    ic3 = inv_mod_pa(c3)
    R2m = sp.expand(E ** 3 + red_pa(ic3 * c2) * E ** 2
                    + red_pa(ic3 * c1) * E + red_pa(ic3 * c0))
    # Vieta form: S1^2 - (s1+s2) S1 + s1 s2, with s1+s2 = -c2/c3 - E and
    # s1 s2 = -c0/(c3 E) = E^2 + (c2/c3) E + c1/c3  (using R2).
    R3m = sp.expand(S1 ** 2 + (red_pa(ic3 * c2) + E) * S1
                    + E ** 2 + red_pa(ic3 * c2) * E + red_pa(ic3 * c1))
    lc4 = sp.expand(sigD * sigbN)
    ilc4 = inv_mod_pa(lc4)
    R4m = sp.expand(T1 ** 2 + red_pa(-ilc4 * sigN * sigbN) * T1
                    + red_pa(ilc4 * apow * sigN * sigbD))
    R5m = sp.expand(T3 ** 2 - st * T3
                    + sp.Rational(1, 67) * (11 * A ** 5 + 2 * A ** 4
                                            - 13 * A ** 3 + 44 * A ** 2
                                            + 19 * A + 40))
    # Pairing coupler: column-2 . conj(column-3) orthogonality
    #   1 + a^2 + c/a + a^-2 + t1/t3 + (sigma - t1)/(st - t3) = 0
    # is LINEAR in t1 after clearing denominators; on the correct pairing
    # component it expresses t1 rationally in (a, t3). Without it the relation
    # ideal contains all four (t1, t3) pairing components and true identities
    # of the matrix are not ideal members (observed at entry (4,3)).
    coupler = (1 + A ** 2 + cN / (cD * A) + A ** (-2)
               + T1 / T3 + (sigN / sigD - T1) / (st - T3))
    cnum, _cden = sp.fraction(sp.together(coupler))
    cpoly = sp.Poly(sp.expand(cnum), T1)
    if cpoly.degree() != 1:
        raise RuntimeError("coupler not linear in T1")
    t1lin = (sp.expand(cpoly.nth(1)), sp.expand(cpoly.nth(0)))   # lc*T1 + c0 = 0

    # Monic elimination of T1: T1SUB = -c0 * lc^{-1} in Q[A,T3]/(R1, R5m),
    # inverse via the quadratic norm: for lc = alpha + beta*T3 (mod R5m),
    # (alpha + beta*T3)(alpha + beta*(st - T3)) = alpha^2 + alpha beta st
    # + beta^2 * ptbar =: N in Q[A]/(R1), so lc^{-1} = conj_elt * N^{-1}.
    def red_R1(p):
        return sp.expand(sp.rem(sp.expand(p), R1, A))

    ptbar = sp.Rational(1, 67) * (11 * A ** 5 + 2 * A ** 4 - 13 * A ** 3
                                  + 44 * A ** 2 + 19 * A + 40)
    lcr = sp.expand(sp.rem(sp.expand(t1lin[0]), R5m, T3))
    lp = sp.Poly(lcr, T3)
    if lp.degree() > 1:
        raise RuntimeError("lc not reduced to T3-degree <= 1")
    beta = red_R1(lp.nth(1))
    alpha = red_R1(lp.nth(0))
    Nrm = red_R1(alpha ** 2 + alpha * beta * st + beta ** 2 * ptbar)
    Ninv = sp.expand(sp.invert(sp.Poly(Nrm, A), sp.Poly(R1, A)).as_expr())
    conj_elt = sp.expand(alpha + beta * st - beta * T3)
    lcinv = sp.expand(conj_elt * Ninv)
    t1sub_raw = sp.expand(-t1lin[1] * lcinv)
    t1sub = sp.expand(sp.rem(sp.expand(sp.rem(t1sub_raw, R5m, T3)), R1, A))

    out = {
        "relations": (R1, R2m, R3m, R4m, R5m),
        "raw_relations": (R1, R2, R3, R4, R5),
        "t1lin": t1lin,
        "t1sub": t1sub,
        "pa": pa, "cubic_coeffs": (c3, c2, c1, c0),
        "cN": cN, "cD": cD, "sigN": sigN, "sigD": sigD, "st": st,
        "t1_poly": (sp.expand(sigD * sigbN), sp.expand(-sigN * sigbN),
                    sp.expand(apow * sigN * sigbD)),
    }
    _CACHE["rel"] = out
    return out


# fraction-pair algebra over the tower quotient (num, den) with NF'd parts

def _fnorm(x):
    """Strip the common rational content of (num, den) — value-preserving."""
    n, d = x
    if n == 0:
        return (sp.Integer(0), sp.Integer(1))
    def cont(p):
        if p.is_Rational:
            return abs(p)
        c = sp.Integer(0)
        for cf in sp.Poly(p, *_VARS).coeffs():
            c = sp.gcd(c, cf)
        return c
    g = sp.gcd(cont(n), cont(d))
    if g not in (0, 1):
        return (sp.expand(n / g), sp.expand(d / g))
    return x


def _fmul(x, y):
    return _fnorm((_mulnf(x[0], y[0]), _mulnf(x[1], y[1])))


def _fadd(x, y):
    return _fnorm((_nf(sp.expand(_mulnf(x[0], y[1]) + _mulnf(y[0], x[1]))),
                   _mulnf(x[1], y[1])))


def _fsub(x, y):
    return _fnorm((_nf(sp.expand(_mulnf(x[0], y[1]) - _mulnf(y[0], x[1]))),
                   _mulnf(x[1], y[1])))


def _fneg(x):
    return (sp.expand(-x[0]), x[1])


def _fconj(x):
    return _urev_frac(x[0], x[1])


def _polyfrac_eval(coeffs_highest_first, t):
    """Evaluate a polynomial with coefficients (exprs in A) at a fraction t."""
    out = (sp.Integer(0), sp.Integer(1))
    for c in coeffs_highest_first:
        out = _fadd(_fmul(out, t), (sp.expand(c), sp.Integer(1)))
    return out


def symbolic_matrix():
    """The 6x6 matrix as a dict (i,j) -> (num, den) of NF'd polynomials in
    the tower variables, plus relations and auxiliary data."""
    if "sym" in _CACHE:
        return _CACHE["sym"]
    rel = _relations()
    c3, c2, c1, c0 = rel["cubic_coeffs"]
    cN, cD = rel["cN"], rel["cD"]
    sigN, sigD = rel["sigN"], rel["sigD"]
    st = rel["st"]

    one = (sp.Integer(1), sp.Integer(1))
    aF = (A, sp.Integer(1))
    ainvF = (sp.Integer(1), A)
    ccF = (cN, cD)
    eF = (E, sp.Integer(1))
    s1F = (S1, sp.Integer(1))
    s2F = (sp.expand(-c2 - c3 * E - c3 * S1), c3)
    # U, V coefficient lists (highest first) as polynomials in A
    u3 = -1 + 23 * A + 12 * A ** 2 + 16 * A ** 3 + 49 * A ** 4 + 45 * A ** 5
    u2 = -4 + 37 * A + 19 * A ** 2 + 21 * A ** 3 + 79 * A ** 4 + 76 * A ** 5
    u1 = u3
    v3 = -22 - 5 * A - 13 * A ** 2 - 41 * A ** 3 - 25 * A ** 4 + 16 * A ** 5
    v2 = -82 - 23 * A - 52 * A ** 2 - 160 * A ** 3 - 102 * A ** 4 + 47 * A ** 5
    v1 = -59 - 31 * A - 48 * A ** 2 - 128 * A ** 3 - 105 * A ** 4 + 5 * A ** 5
    v0 = -21 - 14 * A - 18 * A ** 2 - 48 * A ** 3 - 43 * A ** 4

    def F_of(t):
        Ut = _polyfrac_eval([u3, u2, u1, sp.Integer(0)], t)
        Vt = _polyfrac_eval([v3, v2, v1, v0], t)
        return (_mulnf(Ut[0], Vt[1]), _mulnf(Ut[1], Vt[0]))

    fF = F_of(eF)
    s3F = F_of(s1F)
    s4F = F_of(s2F)
    sigF = (sigN, sigD)
    t1F = (T1, sp.Integer(1))
    t2F = _fsub(sigF, t1F)
    t3F = (T3, sp.Integer(1))
    t4F = _fsub((st, sp.Integer(1)), t3F)

    Eb = [[one, one, one], [one, aF, ainvF], [one, ccF, aF]]
    Bb = [[one, one, one], [eF, s1F, s2F], [fF, s3F, s4F]]
    Cb = [[one, ainvF, aF], [one, t1F, t3F], [one, t2F, t4F]]

    # det(B) and adjugate by explicit cofactors (fraction arithmetic, NF'd)
    def det2(p, q, r, s):
        return _fsub(_fmul(p, s), _fmul(q, r))

    def det3(M):
        return _fadd(
            _fsub(_fmul(M[0][0], det2(M[1][1], M[1][2], M[2][1], M[2][2])),
                  _fmul(M[0][1], det2(M[1][0], M[1][2], M[2][0], M[2][2]))),
            _fmul(M[0][2], det2(M[1][0], M[1][1], M[2][0], M[2][1])))

    detB = det3(Bb)
    # adjugate: adj[i][j] = (-1)^{i+j} * minor(j, i)
    def minor(M, r, c):
        rs = [x for x in range(3) if x != r]
        cs = [x for x in range(3) if x != c]
        return det2(M[rs[0]][cs[0]], M[rs[0]][cs[1]],
                    M[rs[1]][cs[0]], M[rs[1]][cs[1]])

    adjB = [[None] * 3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            m = minor(Bb, j, i)
            adjB[i][j] = m if (i + j) % 2 == 0 else _fneg(m)

    # Binv = adjB / detB ; Binv* = conj entrywise; D = -C E* Binv*^T? no:
    # D = -C E* (B^{-1})*, with (B^{-1})* = conjugate transpose of B^{-1}.
    EstarT = [[_fconj(Eb[j][i]) for j in range(3)] for i in range(3)]
    BinvstarT = [[_fconj(adjB[j][i]) for j in range(3)] for i in range(3)]
    detBconj = _fconj(detB)

    def matmul(X, Y):
        out = [[None] * 3 for _ in range(3)]
        for i in range(3):
            for j in range(3):
                acc = (sp.Integer(0), sp.Integer(1))
                for k in range(3):
                    acc = _fadd(acc, _fmul(X[i][k], Y[k][j]))
                out[i][j] = acc
        return out

    CE = matmul(Cb, EstarT)
    Draw = matmul(CE, BinvstarT)
    Db = [[_fneg(_fmul(Draw[i][j], (detBconj[1], detBconj[0])))
           for j in range(3)] for i in range(3)]

    Hfr = {}
    for i in range(3):
        for j in range(3):
            Hfr[(i, j)] = Eb[i][j]
            Hfr[(i, j + 3)] = Bb[i][j]
            Hfr[(i + 3, j)] = Cb[i][j]
            Hfr[(i + 3, j + 3)] = Db[i][j]

    out = dict(rel)
    out["Hfr"] = Hfr
    _CACHE["sym"] = out
    return out


# --------------------------------------------------- atom roots + certificates

def _poly_box_in(poly, var, box):
    """Box of an integer/rational-coefficient univariate polynomial at a box."""
    out = Box(0)
    for cf in sp.Poly(poly, var).all_coeffs():
        out = out * box + Box(Fraction(sp.Rational(cf).p, sp.Rational(cf).q))
    return out


def _multi_box(poly, boxes, eps_pow):
    """Box of a multivariate polynomial with rational coefficients at atom
    boxes (dict var -> Box)."""
    p = sp.Poly(sp.expand(poly), *_VARS)
    out = Box(0)
    for monom, coeff in p.terms():
        term = Box(Fraction(sp.Rational(coeff).p, sp.Rational(coeff).q))
        for v, m in zip(_VARS, monom):
            for _ in range(m):
                term = term * boxes[v]
        out = out + term
    return out


def _root_boxes(roots, eps_pow):
    return [enclose(r, Fraction(1, 10 ** eps_pow)) for r in roots]


def _certify_unimodular(roots, idx, eps_pow=15):
    bx = _root_boxes(roots, eps_pow)
    ch = [j for j, b in enumerate(bx) if b.intersects(bx[idx].conj())]
    rh = [j for j, b in enumerate(bx) if b.intersects(bx[idx].recip())]
    if len(ch) != 1 or len(rh) != 1:
        raise RuntimeError("ambiguous isolation; raise eps_pow")
    return ch == rh


def _roots_over_Qa(coeff_polys_in_A, aroots, a_index, eps_pow=12):
    """Certified roots (as CRootOf of a rational polynomial) of
    sum_k coeff_polys_in_A[k] * x^k (highest first) at a = aroots[a_index].
    Elimination by resultant; attribution by interval exclusion among the
    conjugates of a."""
    pa = sp.Poly([1, 0, 1, 2, 1, 0, 1], A).as_expr()   # a^6+a^4+2a^3+a^2+1
    poly_x = sum(c * _x ** k for k, c in enumerate(reversed(coeff_polys_in_A)))
    R = sp.resultant(pa, poly_x, A)
    cands = []
    for fct, _m in sp.factor_list(sp.expand(R))[1]:
        fp = sp.Poly(fct, _x)
        if fp.degree() >= 1:
            cands.extend(fp.all_roots())

    for attempt in range(3):
        ep = eps_pow + 6 * attempt
        aboxes = _root_boxes(aroots, ep)
        out, ambiguous = [], False
        for r in cands:
            rb = enclose(r, Fraction(1, 10 ** ep))
            hits = []
            for i, ab in enumerate(aboxes):
                val = None
                for c in coeff_polys_in_A:
                    cb = _poly_box_in(c, A, ab)
                    val = cb if val is None else val * rb + cb
                if val.contains_zero():
                    hits.append(i)
            if hits == [a_index]:
                out.append(r)
            elif a_index in hits:
                ambiguous = True
        if not ambiguous:
            return out
    raise RuntimeError("conjugate attribution stayed ambiguous")


def atoms():
    """Chosen CRootOf values and certified boxes for (a, e, s1, t1, t3),
    with unimodularity certificates for all five and the derived s2, t2, t4
    consistency checks."""
    if "atoms" in _CACHE:
        return _CACHE["atoms"]
    sym = _relations()
    z = _x
    pa_poly = sp.Poly(A ** 6 + A ** 4 + 2 * A ** 3 + A ** 2 + 1, A)
    aroots = sp.Poly(pa_poly.as_expr().subs(A, z), z).all_roots()
    a_idx = None
    for k in range(len(aroots)):
        if _certify_unimodular(aroots, k):
            a_idx = k
            break
    if a_idx is None:
        raise RuntimeError("no unimodular a-root")
    a_val = aroots[a_idx]

    c3, c2, c1, c0 = sym["cubic_coeffs"]
    eroots = _roots_over_Qa([c3, c2, c1, c0], aroots, a_idx)
    if len(eroots) != 3:
        raise RuntimeError(f"expected 3 cubic roots, got {len(eroots)}")
    for r in eroots:
        family = r.poly.all_roots()
        if not _certify_unimodular(family, r.index):
            raise RuntimeError("cubic root not unimodular")

    q2, q1, q0 = sym["t1_poly"]
    t1roots = _roots_over_Qa([sp.expand(q2), sp.expand(q1), sp.expand(q0)],
                             aroots, a_idx)
    if len(t1roots) != 2:
        raise RuntimeError(f"expected 2 t1 roots, got {len(t1roots)}")
    for r in t1roots:
        if not _certify_unimodular(r.poly.all_roots(), r.index):
            raise RuntimeError("t1 root not unimodular")

    st = sym["st"]
    r5c = [sp.Integer(67), sp.expand(-67 * st),
           11 * A ** 5 + 2 * A ** 4 - 13 * A ** 3 + 44 * A ** 2 + 19 * A + 40]
    t3roots = _roots_over_Qa(r5c, aroots, a_idx)
    if len(t3roots) != 2:
        raise RuntimeError(f"expected 2 t3 roots, got {len(t3roots)}")
    for r in t3roots:
        if not _certify_unimodular(r.poly.all_roots(), r.index):
            raise RuntimeError("t3 root not unimodular")

    vals = {A: a_val, E: eroots[0], S1: eroots[1], T1: t1roots[0], T3: t3roots[0]}
    out = {"values": vals, "eroots": eroots, "t1roots": t1roots,
           "t3roots": t3roots, "a_index": a_idx, "aroots": aroots}
    _CACHE["atoms"] = out
    return out


_BOX_CACHE = {}


def boxes(eps_pow=12):
    if eps_pow in _BOX_CACHE:
        return _BOX_CACHE[eps_pow]
    at = atoms()
    out = {v: enclose(r, Fraction(1, 10 ** eps_pow))
           for v, r in at["values"].items()}
    _BOX_CACHE[eps_pow] = out
    return out


_STATE = Path(__file__).resolve().parent / "g6_state.json"


def save_state():
    """Persist atoms + fraction matrix as srepr strings (expensive to build)."""
    import json
    at = atoms()
    sym = symbolic_matrix()
    data = {
        "values": {str(v): sp.srepr(r) for v, r in at["values"].items()},
        "Hfr": {f"{i},{j}": [sp.srepr(n), sp.srepr(d)]
                for (i, j), (n, d) in sym["Hfr"].items()},
    }
    _STATE.write_text(json.dumps(data))


def load_state():
    """Load persisted atoms + matrix if present. Returns True on success."""
    import json
    if not _STATE.exists():
        return False
    data = json.loads(_STATE.read_text())
    names = {str(v): v for v in _VARS}
    vals = {names[k]: sp.sympify(s) for k, s in data["values"].items()}
    _CACHE["atoms"] = {"values": vals}
    sym = dict(_relations())
    sym["Hfr"] = {tuple(int(x) for x in k.split(",")):
                  (sp.sympify(n), sp.sympify(d))
                  for k, (n, d) in data["Hfr"].items()}
    _CACHE["sym"] = sym
    return True


# ------------------------------------------------------- normal-form cascade

def _nf(expr):
    """Reduce a polynomial in the tower variables by the relation cascade
    (T3, T1, S1, E, A). Result 0 is a sound ZERO certificate for the actual
    numbers, provided the recorded leading coefficients are nonzero (they are
    box-certified in verify())."""
    relmap = _relations()
    R1, R2, R3, R4, R5 = relmap["relations"]
    t1sub = relmap["t1sub"]
    e = sp.expand(expr)
    # eliminate T1 FIRST by the MONIC substitution T1 -> t1sub (a polynomial
    # in A, T3; a ring homomorphism, so addition-safe); then the monic cascade.
    if e.has(T1):
        e = sp.expand(e.subs(T1, t1sub))
    for rel, var in ((R5, T3), (R3, S1), (R2, E), (R1, A)):
        if e == 0:
            return sp.Integer(0)
        if e.has(var):
            e = sp.expand(sp.rem(e, rel, var))
    return e


def _nf_zero(expr):
    return _nf(expr) == 0


def is_zero_certified(expr, eps_pow=12):
    """Three-stage exact zero decision for a rational function of the atoms:
    NF of the numerator (ZERO certificate); certified box excluding 0
    (NONZERO certificate); escalation with refined boxes. The denominator is
    box-certified nonzero (the expression must be well-defined)."""
    num, den = sp.fraction(sp.cancel(sp.together(sp.expand(expr))))
    _certify_nonzero_poly(den, eps_pow)
    if _nf_zero(num):
        return True, "nf-zero"
    for ep in (eps_pow, eps_pow + 8, eps_pow + 20):
        bx = boxes(ep)
        nb = _multi_box(num, bx, ep)
        if not nb.contains_zero():
            return False, "box-nonzero"
    raise RuntimeError(f"UNDECIDED zero test (possible tower collapse): {expr}")


def _strip_content(p):
    """Primitive part: divide out the rational content (sign-preserving)."""
    p = sp.expand(p)
    if p == 0 or p.is_Rational:
        return p
    pl = sp.Poly(p, *_VARS)
    cont = sp.Integer(0)
    for c in pl.coeffs():
        cont = sp.gcd(cont, c)
    if cont not in (0, 1):
        return sp.expand(p / cont)
    return p


def _certify_nonzero_poly(p, eps_pow=12):
    p = _strip_content(p)
    if p.is_Rational:
        if p == 0:
            raise RuntimeError("zero where nonzero required")
        return
    # precision must exceed the coefficient magnitude scale
    digits = max(len(str(abs(sp.Rational(c).p)))
                 for c in sp.Poly(p, *_VARS).coeffs())
    base = max(eps_pow, digits + 12)
    for ep in (base, base + 20, base + 60):
        b = _multi_box(p, boxes(ep), ep)
        if not b.contains_zero():
            return
    raise RuntimeError(f"could not certify nonzero: {p}")


# ---------------------------------------------------------- fraction algebra

def _frac(expr):
    """(num, den) as expanded polynomials, cancel()'d once."""
    n, d = sp.fraction(sp.cancel(sp.together(sp.expand(expr))))
    return sp.expand(n), sp.expand(d)


def _urev_frac(num, den):
    """Fraction form of the conjugate: substitute vars by reciprocals and
    clear monomials. Returns polynomial (num', den')."""
    def rev(p):
        p = sp.Poly(sp.expand(p), *_VARS)
        monom = sp.Integer(1)
        for v, dg in zip(_VARS, p.degree_list()):
            monom *= v ** max(dg, 0)
        return sp.expand(monom * p.as_expr().subs(
            {v: 1 / v for v in _VARS}, simultaneous=True)), monom
    rn, mn = rev(num)
    rd, md = rev(den)
    return sp.expand(rn * md), sp.expand(rd * mn)


def _mulnf(p, q):
    return _nf(sp.expand(p * q))


def _sum_fracs_nf(fracs):
    """NF'd numerator and (unreduced) denominator-product of a sum of
    fractions, via prefix/suffix denominator products (all NF'd)."""
    nums = [f[0] for f in fracs]
    dens = [f[1] for f in fracs]
    k = len(fracs)
    pre = [sp.Integer(1)] * (k + 1)
    suf = [sp.Integer(1)] * (k + 1)
    for i in range(k):
        pre[i + 1] = _mulnf(pre[i], dens[i])
    for i in range(k - 1, -1, -1):
        suf[i] = _mulnf(suf[i + 1], dens[i])
    total = sp.Integer(0)
    for i in range(k):
        total = sp.expand(total + _mulnf(_mulnf(nums[i], pre[i]), suf[i + 1]))
    return _nf(total), pre[k]


# ------------------------------------------------------------- verification

def matrix_with_values():
    """H with the certified CRootOf atoms substituted (exact sympy Matrix)."""
    sym, at = symbolic_matrix(), atoms()
    vals = at["values"]
    out = sp.zeros(6, 6)
    for (i, j), (n, d) in sym["Hfr"].items():
        out[i, j] = (n.subs(vals, simultaneous=True)
                     / d.subs(vals, simultaneous=True))
    return out


def verify_hadamard(eps_pow=12, verbose=True):
    """Exact is_hadamard for the G6 point. Zero facts by NF cascade; nonzero
    facts (denominators, cascade lead coefficients) by certified boxes."""
    sym = symbolic_matrix()
    fr = [[sym["Hfr"][(i, j)] for j in range(6)] for i in range(6)]
    # soundness of the cascade: lead coefficients of each relation nonzero
    R1, R2, R3, R4, R5 = sym["relations"]
    for rel, var in ((R5, T3), (R4, T1), (R3, S1), (R2, E)):
        _certify_nonzero_poly(sp.Poly(rel, var).LC(), eps_pow)

    for i in range(6):
        for j in range(6):
            n, d = fr[i][j]
            _certify_nonzero_poly(d, eps_pow)
            rn, rd = _urev_frac(n, d)
            # |x|^2 = 1  <=>  n*rn - d*rd == 0 (both denominators certified)
            _certify_nonzero_poly(rd, eps_pow)
            if not _nf_zero(sp.expand(_mulnf(n, rn) - _mulnf(d, rd))):
                return False, f"entry ({i},{j}) unimodularity not NF-zero"
        if verbose:
            print(f"  unimodular row {i} ok", flush=True)
    for j in range(6):
        for l in range(j + 1, 6):
            terms = []
            for k in range(6):
                n1, d1 = fr[j][k]
                rn, rd = _urev_frac(*fr[l][k])
                terms.append((_mulnf(n1, rn), _mulnf(d1, rd)))
            total, _dens = _sum_fracs_nf(terms)
            if total != 0:
                return False, f"rows {j},{l} Gram sum not NF-zero"
            if verbose:
                print(f"  gram ({j},{l}) ok", flush=True)
    return True, "ok"


def _rows_boxes(eps_pow=30):
    """Certified interval boxes of the 30x36 defect system entries."""
    sym = symbolic_matrix()
    fr = [[sym["Hfr"][(i, j)] for j in range(6)] for i in range(6)]
    bx = boxes(eps_pow)

    def fbox(f):
        return _multi_box(f[0], bx, eps_pow) * _multi_box(f[1], bx, eps_pow).recip()

    ent = [[fbox(fr[i][j]) for j in range(6)] for i in range(6)]
    rows = []
    for j, l in combinations(range(6), 2):
        re_row = [Box(0)] * 36
        im_row = [Box(0)] * 36
        for k in range(6):
            u = ent[j][k] * ent[l][k].conj()
            re_row[j * 6 + k] = re_row[j * 6 + k] + Box(u.re)
            re_row[l * 6 + k] = re_row[l * 6 + k] + (-Box(u.re))
            im_row[j * 6 + k] = im_row[j * 6 + k] + Box(u.im)
            im_row[l * 6 + k] = im_row[l * 6 + k] + (-Box(u.im))
        rows.append(re_row)
        rows.append(im_row)
    return rows


def rank_lower_bound(eps_pow=30, verbose=True):
    """Certified rank lower bound of the defect system by interval Gaussian
    elimination (pivots must exclude zero). rank >= result ==> defect <=
    36 - result - 11. Sound; not necessarily tight."""
    rows = _rows_boxes(eps_pow)
    m, n = len(rows), 36
    used = [False] * m
    rank = 0
    for col in range(n):
        piv = None
        best = None
        for i in range(m):
            if used[i]:
                continue
            b = rows[i][col].re * rows[i][col].re + rows[i][col].im * rows[i][col].im
            if not b.contains_zero():
                if best is None or b.lo > best:
                    best = b.lo
                    piv = i
        if piv is None:
            continue
        used[piv] = True
        rank += 1
        pv = rows[piv][col]
        pvr = pv.recip()
        for i in range(m):
            if used[i]:
                continue
            f = rows[i][col] * pvr
            rows[i] = [rows[i][c] + (-(f * rows[piv][c])) for c in range(n)]
        if verbose:
            print(f"  interval pivot {rank} at col {col}", flush=True)
    return rank


def defect(eps_pow=12, verbose=True):
    """Exact defect via fraction-free Gauss over the tower quotient with a
    bracketed rank: pivots box-certified nonzero (rank lower bound), remaining
    rows NF-zero (rank upper bound)."""
    sym = symbolic_matrix()
    fr = [[sym["Hfr"][(i, j)] for j in range(6)] for i in range(6)]

    rows = []
    for j, l in combinations(range(6), 2):
        u = []
        for k in range(6):
            n1, d1 = fr[j][k]
            rn, rd = _urev_frac(*fr[l][k])
            u.append((_mulnf(n1, rn), _mulnf(d1, rd)))
        ubar = [_urev_frac(*x) for x in u]
        for sign in (1, -1):
            # sign=+1: u + conj(u) (2 Re); sign=-1: u - conj(u) (2i Im)
            row = [sp.Integer(0)] * 36
            entries = []
            for k in range(6):
                n1, d1 = u[k]
                n2, d2 = ubar[k]
                num = sp.expand(_mulnf(n1, d2) + sign * _mulnf(n2, d1))
                den = _mulnf(d1, d2)
                entries.append((_nf(num), den))
            # clear the row denominator by prefix/suffix products
            k6 = 6
            pre = [sp.Integer(1)] * (k6 + 1)
            suf = [sp.Integer(1)] * (k6 + 1)
            for i in range(k6):
                pre[i + 1] = _mulnf(pre[i], entries[i][1])
            for i in range(k6 - 1, -1, -1):
                suf[i] = _mulnf(suf[i + 1], entries[i][1])
            for k in range(6):
                val = _mulnf(_mulnf(entries[k][0], pre[k]), suf[k + 1])
                row[j * 6 + k] = sp.expand(row[j * 6 + k] + val)
                row[l * 6 + k] = sp.expand(row[l * 6 + k] - val)
            rows.append([_nf(v) for v in row])
        if verbose:
            print(f"  defect rows for pair ({j},{l}) built", flush=True)

    def strip(row):
        cont = sp.Integer(0)
        for v in row:
            for c in sp.Poly(v, *_VARS).coeffs() if v != 0 else []:
                cont = sp.gcd(cont, c)
        if cont not in (0, 1):
            return [sp.expand(v / cont) for v in row]
        return row

    rows = [strip(r) for r in rows]
    m, n = len(rows), 36
    rank = 0
    used = [False] * m
    for col in range(n):
        piv = None
        for i in range(m):
            if used[i]:
                continue
            v = rows[i][col]
            if v == 0:
                continue
            try:
                _certify_nonzero_poly(v, eps_pow)
                piv = i
                break
            except RuntimeError:
                if not _nf_zero(v):
                    raise RuntimeError(
                        f"entry neither certified nonzero nor NF-zero at "
                        f"row {i} col {col} -- escalate")
                rows[i][col] = sp.Integer(0)
        if piv is None:
            continue
        used[piv] = True
        rank += 1
        pv = rows[piv][col]
        for i in range(m):
            if used[i] or rows[i][col] == 0:
                continue
            f = rows[i][col]
            rows[i] = strip([
                _nf(sp.expand(_mulnf(rows[i][c], pv) - _mulnf(rows[piv][c], f)))
                for c in range(n)])
        if verbose:
            print(f"  pivot {rank} at col {col}", flush=True)
    # upper bound: every unused row must be NF-zero entirely
    for i in range(m):
        if not used[i]:
            for c in range(n):
                if rows[i][c] != 0 and not _nf_zero(rows[i][c]):
                    raise RuntimeError(
                        f"leftover row {i} col {c} not NF-zero -- rank bracket "
                        f"failed, escalate")
    return (36 - rank) - 11
