"""Exact parametrizations of the known order-6 complex Hadamard catalogue.  [D]

Cached from pinned primary sources (fetched 2026-08-25 via arXiv e-print,
offline thereafter). Every constructor returns an exact sympy Matrix; the
__main__ verifier checks is_hadamard and the expected defect for sample points
of every family and exits nonzero on any failure.

Sources (arXiv id, version, what was taken):
  [TZ] quant-ph/0512154v2  Tadej-Zyczkowski, "A concise guide to complex
       Hadamard matrices": F6 and the phase pattern of F6(a,b) (eq. F6_maxAUF),
       D6 and D6(c) (eqs. U1par, U6_1par_orbits), the circulant C6 (x =
       [1, i/d, -1/d, -i, -d, i d], d = (1-sqrt3)/2 + i sqrt(sqrt3/2)), S6.
       Defect values stated there: d(F6)=4, d(C6)=4, d(S6)=0.
  [BN] math/0609076v1  Beauchamp-Nicoara, "Orthogonal maximal abelian
       *-subalgebras of the 6x6 matrices": B6(theta) self-adjoint family,
       y = exp(i theta), z = (1+2y-y^2)/(y(-1+2y+y^2)),
       x = (1+2y+y^2 - sqrt2 sqrt(1+2y+2y^3+y^4))/(1+2y-y^2),
       t = (same numerator)/(-1+2y+y^2). Anchors: B6(pi/2) ~ D6,
       B6(2 Arg d) ~ C6.
  [MS] math/0702043v1  Matolcsi-Szollosi, "Towards a classification of 6x6
       complex Hadamard matrices": symmetric family M6(x) (eq. fam) with
       a,d = (x^2-2x-1)/4 -/+ i (x^2-2x-1) sqrt(16-|x^2-2x-1|^2)/(4|x^2-2x-1|),
       b,c = -(1+x^2)/4 -/+ i(...), p,q = (x^2+2x-1)/4 +/- i(...), x != +-i.
       Anchors: M6(1) ~ F6, M6(x -> -i) ~ D6, M6(x1) = discrete M6 with
       x1 = (1-sqrt13)/3 + i sqrt(-5+2 sqrt13)/3.
  [K1] 1003.4133v1  Karlsson, "H2-reducible Hadamard matrices of order 6":
       H2-reducible <=> dephased form contains a -1 in the core; every such
       matrix has the F2/Z-block canonical form. All previously known families
       except S6 (F6(a,b), F6(a,b)^T, D6(c), B6, M6(x), X6^(2) hypocycloid,
       K6^(2)) are H2-reducible, hence inside K6^(3).
  [K2] 1003.4177v1  Karlsson, "Three-parameter complex Hadamard matrices of
       order 6": the K6^(3) family: H = [[F2,Z1,Z2],[Z3,Z3AZ1/2,Z3BZ2/2],
       [Z4,Z4BZ1/2,Z4AZ2/2]], A11 = -1/2 + i sqrt3/2 (cos t + e^{-i p} sin t),
       A12 = -1/2 + i sqrt3/2 (-cos t + e^{i p} sin t), B = -F2 - A, Mobius
       relations z3^2 = M_A(z1^2), z4^2 = M_B(z1^2), z2^2 = M_A^{-1}(M_B(z1^2))
       with M(z) = (alpha z - beta)/(conj(beta) z - conj(alpha)),
       alpha_A = A12^2, beta_A = A11^2 (and B likewise).
  [SZ] 1008.0632v1  Szollosi, "Complex Hadamard matrices of order 6: a
       four-parameter family": the Dilation Algorithm (Construction mC) and the
       explicit generic point of section "A generic matrix": input quadruple
       (a, 1/a, c, a), a a unimodular root of a^6+a^4+2a^3+a^2+1 = 0,
       c = (-a^3+a^2+a+1)/(a(a^3+a^2+a-1)), prescribed C-block g = 1/a, h = a,
       F(e) = U(e)/V(e) with the printed quintic-coefficient polynomials,
       (e,s1,s2) the roots of the printed cubic, t3+t4 = a^5+a^3+2a^2-a-1,
       t3 t4 = (11a^5+2a^4-13a^3+44a^2+19a+40)/67, D = -C E^* (B^{-1})^*.
       Conjecture there: CH(6) = K6^(3) u G6^(4) u {S6}.

Exact arithmetic only. No floating point, no simplify-based verdicts: the
verifier uses field arithmetic (QQ.algebraic_field + DomainMatrix) throughout,
with conjugation of unimodular generators implemented as inversion.
"""

from itertools import combinations

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from hadamard import fourier, tao_S6


def _w(k, n):
    return sp.exp(2 * sp.pi * sp.I * sp.Rational(k, n))


# --------------------------------------------------------------- [TZ] F6(a,b)

def F6_phases(a, b):
    """F6(a,b) = F6 o EXP(i R), R[j,k] = a for odd j, k=1,4; b for odd j, k=2,5.
    a, b are sympy phase EXPRESSIONS (radians)."""
    F = fourier(6)
    out = sp.zeros(6, 6)
    for j in range(6):
        for k in range(6):
            ph = sp.Integer(0)
            if j % 2 == 1 and k % 3 == 1:
                ph = a
            elif j % 2 == 1 and k % 3 == 2:
                ph = b
            out[j, k] = F[j, k] * sp.exp(sp.I * ph)
    return out


def F6_point(p1, q1, p2, q2):
    """F6(2 pi p1/q1, 2 pi p2/q2) -- an exact root-of-unity parameter point."""
    return F6_phases(2 * sp.pi * sp.Rational(p1, q1), 2 * sp.pi * sp.Rational(p2, q2))


# ---------------------------------------------------------------- [TZ] D6(c)

D6_BASE = sp.Matrix([
    [1,  1,  1,  1,  1,  1],
    [1, -1,  sp.I, -sp.I, -sp.I,  sp.I],
    [1,  sp.I, -1,  sp.I, -sp.I, -sp.I],
    [1, -sp.I,  sp.I, -1,  sp.I, -sp.I],
    [1, -sp.I, -sp.I,  sp.I, -1,  sp.I],
    [1,  sp.I, -sp.I, -sp.I,  sp.I, -1],
])

_D6_PHASE_PATTERN = [
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 0],
    [0, 0, -1, 0, 0, -1],
    [0, 0, -1, 0, 0, -1],
    [0, 0, 0, 1, 1, 0],
]


def D6_c(c):
    """D6(c), c a sympy phase expression: D6 o EXP(i R(c)) per [TZ]."""
    out = sp.zeros(6, 6)
    for j in range(6):
        for k in range(6):
            out[j, k] = D6_BASE[j, k] * sp.exp(sp.I * _D6_PHASE_PATTERN[j][k] * c)
    return out


def D6_point(p, q):
    return D6_c(2 * sp.pi * sp.Rational(p, q))


# ------------------------------------------------------------------- [TZ] C6

def bjorck_d():
    return (1 - sp.sqrt(3)) / 2 + sp.I * sp.sqrt(sp.sqrt(3) / 2)


def C6():
    """Bjorck's circulant cyclic 6-roots matrix, [TZ] convention:
    row = [1, i/d, -1/d, -i, -d, i d], C[j,k] = row[(k-j) mod 6]."""
    d = bjorck_d()
    row = [sp.Integer(1), sp.I / d, -1 / d, -sp.I, -d, sp.I * d]
    return sp.Matrix(6, 6, lambda j, k: row[(k - j) % 6])


def S6():
    return tao_S6()


# ------------------------------------------------------------- [BN] B6(theta)

def B6_y(y):
    """Beauchamp-Nicoara self-adjoint family at y = exp(i theta), exact y.

    Valid for theta in [-pi, -arccos((-1+sqrt3)/2)] u [arccos((-1+sqrt3)/2), pi].
    sqrt(1+2y+2y^3+y^4) is rewritten as y*sqrt(y^-2+2/y+2y+y^2) — the inner
    argument is real for |y| = 1 (sum of conjugate pairs), which keeps all
    entries in a radical REAL/imag-splittable field. The global branch choice
    selects one of the two BN solution branches; both are family members.
    """
    r = sp.expand(y ** -2 + 2 / y + 2 * y + y ** 2)
    num = 1 + 2 * y + y ** 2 - sp.sqrt(2) * y * sp.sqrt(r)
    x = num / (1 + 2 * y - y ** 2)
    t = num / (-1 + 2 * y + y ** 2)
    z = (1 + 2 * y - y ** 2) / (y * (-1 + 2 * y + y ** 2))
    xb, yb, zb, tb = (sp.conjugate(v) for v in (x, y, z, t))
    return sp.Matrix([
        [1,  1,   1,   1,   1,   1],
        [1, -1,  xb, -y, -xb,   y],
        [1,  x,  -1,   t,  -t,  -x],
        [1, -yb, tb,  -1,  yb, -tb],
        [1, -x, -tb,   y,   1,  zb],
        [1,  yb, -xb, -t,   z,   1],
    ])


def B6_point(p, q):
    """B6 at theta = 2 pi p / q (must lie in the valid range)."""
    return B6_y(_w(p, q))


# --------------------------------------------------------------- [MS] M6(x)

def M6_x(x):
    """Matolcsi-Szollosi symmetric family at exact unimodular x != +-i.

    abs2(v) is computed as v * (v with x -> 1/x), valid because the arguments
    are polynomials in x with real (integer) coefficients and |x| = 1.
    """
    def abs2(poly):
        return sp.expand(poly * poly.subs(x_, 1 / x_))

    x_ = sp.Symbol("x_")
    A_ = x_ ** 2 - 2 * x_ - 1
    B_ = 1 + x_ ** 2
    C_ = x_ ** 2 + 2 * x_ - 1

    def pair(P, sign_first):
        """(P/4 +- i P sqrt(16-|P|^2)/(4|P|)) evaluated exactly at x."""
        Pv = P.subs(x_, x)
        a2 = abs2(P).subs(x_, x)
        root = sp.sqrt(16 - a2)
        absP = sp.sqrt(a2)
        main = Pv / 4
        dev = sp.I * Pv * root / (4 * absP)
        return (main + sign_first * dev, main - sign_first * dev)

    d, a = pair(A_, sp.Integer(1))       # d gets +, a gets -   [MS eq. auj1/duj]
    b, c = pair(-B_, sp.Integer(1))      # b = -(1+x^2)/4 - i(1+x^2)(...): use
    p, q = pair(C_, sp.Integer(1))       # P = -(1+x^2)          [MS eq. buj/cuj]
    # p gets +, q gets -                                        [MS eq. puj/quj]
    return sp.Matrix([
        [1,  1, 1, 1, 1, 1],
        [1, -1, x, x, -x, -x],
        [1,  x, d, a,  b,  c],
        [1,  x, a, d,  c,  b],
        [1, -x, b, c,  p,  q],
        [1, -x, c, b,  q,  p],
    ])


def M6_point(p, q):
    return M6_x(_w(p, q))


# ------------------------------------------------- [K2] K6^(3) three-parameter

def K6_point(ct, st, cp, sp_, z1):
    """Karlsson K6^(3) at exact (cos t, sin t) and (cos p, sin p) pairs and
    exact unimodular z1. Caller must supply ct^2+st^2 = 1 and cp^2+sp_^2 = 1
    exactly (e.g. from root-of-unity half-angle data).

    Requires the Mobius transformations to be nondegenerate at this point
    (|alpha|^2 != |beta|^2 for both A and B); raises ValueError otherwise.
    """
    I = sp.I
    s3 = sp.sqrt(3)
    eip = cp + I * sp_                      # e^{i p}
    eim = cp - I * sp_                      # e^{-i p}
    A11 = sp.Rational(-1, 2) + I * s3 / 2 * (ct + eim * st)
    A12 = sp.Rational(-1, 2) + I * s3 / 2 * (-ct + eip * st)
    B11 = -1 - A11                          # B = -F2 - A elementwise on this form
    B12 = -1 - A12

    def uconj(v):
        return sp.expand_complex(sp.conjugate(v))

    def mob(al, be, z):
        return (al * z - be) / (uconj(be) * z - uconj(al))

    def mob_inv(al, be, w):
        return (uconj(al) * w - be) / (uconj(be) * w - al)

    alA, beA = A12 ** 2, A11 ** 2
    alB, beB = B12 ** 2, B11 ** 2
    for al, be in ((alA, beA), (alB, beB)):
        gap = sp.simplify(sp.expand_complex(al * uconj(al) - be * uconj(be)))
        if gap == 0:
            raise ValueError("degenerate Mobius point")

    z1sq = z1 ** 2
    z3 = sp.sqrt(mob(alA, beA, z1sq))
    z4 = sp.sqrt(mob(alB, beB, z1sq))
    z2 = sp.sqrt(mob_inv(alA, beA, mob(alB, beB, z1sq)))

    A = sp.Matrix([[A11, A12], [uconj(A12), -uconj(A11)]])
    B = sp.Matrix([[B11, B12], [uconj(B12), -uconj(B11)]])
    F2 = sp.Matrix([[1, 1], [1, -1]])
    Z1 = sp.Matrix([[1, 1], [z1, -z1]])
    Z2 = sp.Matrix([[1, 1], [z2, -z2]])
    Z3 = sp.Matrix([[1, z3], [1, -z3]])
    Z4 = sp.Matrix([[1, z4], [1, -z4]])

    top = F2.row_join(Z1).row_join(Z2)
    mid = Z3.row_join(Z3 * A * Z1 / 2).row_join(Z3 * B * Z2 / 2)
    bot = Z4.row_join(Z4 * B * Z1 / 2).row_join(Z4 * A * Z2 / 2)
    return top.col_join(mid).col_join(bot)


# ----------------------------------------------------- [SZ] G6^(4) generic pt

def _boxes_of(values, eps_pow=15):
    from fractions import Fraction
    from qivmini import enclose
    return [enclose(v, Fraction(1, 10 ** eps_pow)) for v in values]


def certify_unimodular_root(roots, idx, eps_pow=15):
    """Exact |r| = 1 for r = roots[idx] of a REAL-coefficient rational
    polynomial whose root list is `roots`: conj(r) is then a root, and if the
    box of conj(r) and the box of 1/r isolate the SAME single root, then
    conj(r) == 1/r exactly, i.e. |r| = 1. Returns True/False; raises on
    ambiguous isolation (refine eps_pow)."""
    bx = _boxes_of(roots, eps_pow)
    cb = bx[idx].conj()
    rb = bx[idx].recip()
    conj_hits = [j for j, b in enumerate(bx) if b.intersects(cb)]
    recip_hits = [j for j, b in enumerate(bx) if b.intersects(rb)]
    if len(conj_hits) != 1 or len(recip_hits) != 1:
        raise RuntimeError(f"ambiguous isolation {conj_hits} {recip_hits}")
    return conj_hits == recip_hits


def _szollosi_a():
    """The unimodular root (canonical: lowest CRootOf index certified
    unimodular) of a^6 + a^4 + 2a^3 + a^2 + 1 = 0."""
    z = sp.Symbol("z")
    poly = sp.Poly(z ** 6 + z ** 4 + 2 * z ** 3 + z ** 2 + 1, z)
    roots = poly.all_roots()
    for k in range(len(roots)):
        if certify_unimodular_root(roots, k):
            return roots[k], roots
    raise RuntimeError("no unimodular root certified")


def _poly_box(coeff_exprs_in_a, abox):
    """Box of a polynomial-in-a value: coeff exprs are integer polynomials in
    the symbol; evaluated at the box of a via exact interval Horner."""
    from qivmini import Box
    from fractions import Fraction
    out = Box(0)
    for c in coeff_exprs_in_a:
        out = out * abox + Box(Fraction(int(c)))
    return out


def _roots_over_Qa(coeffs_in_a, a, aroots, a_index=0, eps_pow=15):
    """Exact roots of sum_k coeffs_in_a[k](a) * x^k (highest degree first),
    coefficients integer polynomials in the CRootOf a.

    Method: eliminate a by resultant with a's minimal polynomial -> rational
    polynomial R(x) whose roots include every root of every conjugate's
    polynomial. A candidate root x0 of R is certified as a root of OUR
    polynomial when the interval evaluation of the polynomial at (box a_i,
    box x0) contains 0 for i = a_index and excludes 0 for every other
    conjugate i (x0 is exactly a root of one of the factors; all other factors
    are certified nonvanishing at x0). Raises on ambiguity.
    """
    from fractions import Fraction
    from qivmini import enclose

    z = sp.Symbol("z")
    x = sp.Symbol("x")
    pa_expr = a.poly.as_expr(z) if hasattr(a, "poly") else None
    if pa_expr is None:
        raise RuntimeError("a must be a CRootOf")
    poly_x = sum(c.subs(_SZ_A, z) * x ** k
                 for k, c in enumerate(reversed(coeffs_in_a)))
    R = sp.resultant(pa_expr, poly_x, z)
    Rp = sp.Poly(sp.expand(R), x)
    cands = []
    for f, _m in sp.factor_list(Rp.as_expr())[1]:
        fp = sp.Poly(f, x)
        if fp.degree() >= 1:
            cands.extend(fp.all_roots())

    aboxes = _boxes_of(aroots, eps_pow)
    out = []
    for r in cands:
        rb = enclose(r, Fraction(1, 10 ** eps_pow))
        hits = []
        for i, ab in enumerate(aboxes):
            val = None
            for c in coeffs_in_a:
                cb = _poly_box(sp.Poly(c.subs(_SZ_A, z), z).all_coeffs(), ab)
                val = cb if val is None else val * rb + cb
            if val.contains_zero():
                hits.append(i)
        if hits == [a_index]:
            out.append(r)
        elif a_index in hits:
            raise RuntimeError(f"ambiguous conjugate attribution: {hits}")
    return out


_SZ_A = sp.Symbol("_sz_a")


def G6_generic():
    """Szollosi's explicit generic G6^(4) point ([SZ] section 'A generic
    matrix'). Returns the exact 6x6 sympy matrix. Entries live in the tower
    Q(a)(e)(s1)(t1)(t3)."""
    a = _szollosi_a()
    z = sp.Symbol("z")

    b = 1 / a
    c = (-a ** 3 + a ** 2 + a + 1) / (a * (a ** 3 + a ** 2 + a - 1))
    d = a
    g = 1 / a
    h = a

    # cubic for (e, s1, s2), coefficients in Z[a]  [SZ eq. after (FE2)]
    c3 = (-145823 * a ** 5 + 177379 * a ** 4 + 335906 * a ** 3
          + 107524 * a ** 2 + 34729 * a + 182739)
    c2 = (-151183 * a ** 5 + 513285 * a ** 4 + 729716 * a ** 3
          + 258504 * a ** 2 + 142253 * a + 363291)
    c1 = (52821 * a ** 5 + 421725 * a ** 4 + 441134 * a ** 3
          + 177978 * a ** 2 + 144177 * a + 190285)
    c0 = (-21839 * a ** 5 + 186361 * a ** 4 + 235364 * a ** 3
          + 87432 * a ** 2 + 56745 * a + 111701)

    e, s1, s2 = _roots_of_cubic_over_Qa(c3, c2, c1, c0, a)

    # F(e) = U(e)/V(e)  [SZ eq. FE2]
    def U(t):
        return ((-1 + 23 * a + 12 * a ** 2 + 16 * a ** 3 + 49 * a ** 4 + 45 * a ** 5) * t
                + (-4 + 37 * a + 19 * a ** 2 + 21 * a ** 3 + 79 * a ** 4 + 76 * a ** 5) * t ** 2
                + (-1 + 23 * a + 12 * a ** 2 + 16 * a ** 3 + 49 * a ** 4 + 45 * a ** 5) * t ** 3)

    def V(t):
        return (-21 - 14 * a - 18 * a ** 2 - 48 * a ** 3 - 43 * a ** 4
                + (-59 - 31 * a - 48 * a ** 2 - 128 * a ** 3 - 105 * a ** 4 + 5 * a ** 5) * t
                + (-82 - 23 * a - 52 * a ** 2 - 160 * a ** 3 - 102 * a ** 4 + 47 * a ** 5) * t ** 2
                + (-22 - 5 * a - 13 * a ** 2 - 41 * a ** 3 - 25 * a ** 4 + 16 * a ** 5) * t ** 3)

    f = U(e) / V(e)
    s3 = U(s1) / V(s1)
    s4 = U(s2) / V(s2)

    # (t1, t2): column-2 orthogonality pair via sum-product formula [SZ sump]
    sig = -(1 + a + c + g)
    t1, t2 = _unimodular_pair(sig, a)

    # (t3, t4): the printed symmetric functions [SZ]
    st = a ** 5 + a ** 3 + 2 * a ** 2 - a - 1
    pt = (11 * a ** 5 + 2 * a ** 4 - 13 * a ** 3 + 44 * a ** 2 + 19 * a + 40) / 67
    t3, t4 = _roots_of_quadratic_over_Qa(1, -st, pt, a)

    E = sp.Matrix([[1, 1, 1], [1, a, b], [1, c, d]])
    B = sp.Matrix([[1, 1, 1], [e, s1, s2], [f, s3, s4]])
    C = sp.Matrix([[1, g, h], [1, t1, t3], [1, t2, t4]])
    atoms = (a, e, s1, t1, t3)
    Estar = E.T.applyfunc(lambda v: _uconj_tower(v, atoms))
    Binv = B.inv()
    Binvstar = Binv.T.applyfunc(lambda v: _uconj_tower(v, atoms))
    D = -C * Estar * Binvstar

    top = E.row_join(B)
    bot = C.row_join(D)
    return top.col_join(bot), atoms


def _uconj_tower(v, atoms):
    """Complex conjugate of a rational function (real rational coefficients) of
    unimodular atoms: substitute every atom by its reciprocal. Sound only for
    atoms individually certified unimodular."""
    return sp.sympify(v).subs({t: 1 / t for t in atoms}, simultaneous=True)


# --------------------------------------------- exact verification primitives

def _re_im(e):
    x, y = sp.expand_complex(e).as_real_imag()
    return sp.expand(x), sp.expand(y)


def real_field_for(entries, budget=64):
    gens, seen = [], set()
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
    K = sp.QQ.algebraic_field(*gens)
    if K.mod.degree() > budget:
        raise RuntimeError(f"field degree {K.mod.degree()} exceeds budget {budget}")
    return K


def is_hadamard_field(H):
    """Exact Hadamard predicate via (re, im) pairs over a real algebraic field.
    For radical-entry matrices (no CRootOf). Returns (ok, why)."""
    H = sp.Matrix(H)
    n = H.rows
    K = real_field_for(list(H))
    pairs = [[tuple(K.from_sympy(p) for p in _re_im(H[i, j])) for j in range(n)]
             for i in range(n)]
    one, zero = K.one, K.zero
    for i in range(n):
        for j in range(n):
            xx, yy = pairs[i][j]
            if xx * xx + yy * yy != one:
                return False, f"entry ({i},{j}) not unimodular"
    for j in range(n):
        for l in range(j + 1, n):
            sx = zero
            sy = zero
            for k in range(n):
                aa, bb = pairs[j][k]
                cc, dd = pairs[l][k]
                sx += aa * cc + bb * dd
                sy += bb * cc - aa * dd
            if sx != zero or sy != zero:
                return False, f"rows {j},{l} not orthogonal"
    return True, "ok"


def defect_field(H):
    """Tadej-Zyczkowski defect via DomainMatrix rank over an explicit real
    algebraic field (sound path; see slag/harness-defects.md H6-H4)."""
    from sympy.polys.matrices import DomainMatrix as _DM
    H = sp.Matrix(H)
    n = H.rows
    K = real_field_for(list(H))
    pairs = [[tuple(K.from_sympy(p) for p in _re_im(H[i, j])) for j in range(n)]
             for i in range(n)]
    zero = K.zero
    rows = []
    for j, l in combinations(range(n), 2):
        re_row = [zero] * (n * n)
        im_row = [zero] * (n * n)
        for k in range(n):
            aa, bb = pairs[j][k]
            cc, dd = pairs[l][k]
            cr = aa * cc + bb * dd
            ci = bb * cc - aa * dd
            re_row[j * n + k] += cr
            re_row[l * n + k] -= cr
            im_row[j * n + k] += ci
            im_row[l * n + k] -= ci
        rows.append(re_row)
        rows.append(im_row)
    dm = _DM(rows, (len(rows), n * n), K)
    return (n * n - dm.rank()) - (2 * n - 1)
