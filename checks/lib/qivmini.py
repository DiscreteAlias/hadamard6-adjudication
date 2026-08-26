"""Minimal exact rational interval/box arithmetic for catalogue verification.

Subset copy of counterexample/lib/qiv.py (kept dependency-free so Track A
never imports Track B internals). Exact arithmetic only; math.isqrt is the
only integer primitive beyond ring ops.
"""


from fractions import Fraction
from math import isqrt

import sympy as sp


class EncloseError(Exception):
    """Expression contains a node qiv cannot certify."""


# ------------------------------------------------------------------- intervals

class Iv:
    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi=None):
        lo = Fraction(lo)
        hi = lo if hi is None else Fraction(hi)
        if lo > hi:
            raise ValueError(f"inverted interval [{lo}, {hi}]")
        self.lo, self.hi = lo, hi

    def __repr__(self):
        return f"Iv({self.lo}, {self.hi})"

    def __neg__(self):
        return Iv(-self.hi, -self.lo)

    def __add__(self, o):
        return Iv(self.lo + o.lo, self.hi + o.hi)

    def __sub__(self, o):
        return Iv(self.lo - o.hi, self.hi - o.lo)

    def __mul__(self, o):
        c = (self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi)
        return Iv(min(c), max(c))

    def scaled(self, q):
        q = Fraction(q)
        return Iv(self.lo * q, self.hi * q) if q >= 0 else Iv(self.hi * q, self.lo * q)

    def width(self):
        return self.hi - self.lo

    def contains_zero(self):
        return self.lo <= 0 <= self.hi

    def strictly_positive(self):
        return self.lo > 0

    def strictly_negative(self):
        return self.hi < 0

    def intersects(self, o):
        return not (self.hi < o.lo or o.hi < self.lo)


def _iroot_floor(t, r):
    """floor(t**(1/r)) for nonnegative integer t, by exact binary search."""
    if t < 0:
        raise ValueError("negative radicand")
    if r == 2:
        return isqrt(t)
    if t in (0, 1):
        return t
    hi = 1 << (t.bit_length() // r + 2)
    lo = 0
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid ** r <= t:
            lo = mid
        else:
            hi = mid
    return lo


def _nthroot_lower(x, r):
    """Largest m/s <= x**(1/r), s = 2**64 granularity. x: Fraction >= 0."""
    s = 1 << 64
    t = (x.numerator * s ** r) // x.denominator          # floor(x s^r)
    return Fraction(_iroot_floor(t, r), s)


def _nthroot_upper(x, r):
    s = 1 << 64
    t = -((-x.numerator * s ** r) // x.denominator)      # ceil(x s^r)
    m = _iroot_floor(t, r)
    if m ** r < t:
        m += 1
    return Fraction(m, s)


def iv_nthroot(iv, r):
    """Certified enclosure of the real r-th root over a nonnegative interval."""
    if iv.lo < 0:
        raise EncloseError(f"nth root of interval reaching below zero: {iv}")
    return Iv(_nthroot_lower(iv.lo, r), _nthroot_upper(iv.hi, r))


def iv_sqrt(iv):
    return iv_nthroot(iv, 2)


def iv_recip(iv):
    """Certified reciprocal of an interval excluding zero."""
    if iv.contains_zero():
        raise EncloseError(f"reciprocal of interval containing zero: {iv}")
    return Iv(1 / iv.hi, 1 / iv.lo)


# ------------------------------------------------------------------------ boxes

class Box:
    __slots__ = ("re", "im")

    def __init__(self, re, im=None):
        self.re = re if isinstance(re, Iv) else Iv(re)
        self.im = (im if isinstance(im, Iv) else Iv(im)) if im is not None else Iv(0)

    def __repr__(self):
        return f"Box(re={self.re}, im={self.im})"

    def __neg__(self):
        return Box(-self.re, -self.im)

    def __add__(self, o):
        return Box(self.re + o.re, self.im + o.im)

    def __sub__(self, o):
        return Box(self.re - o.re, self.im - o.im)

    def __mul__(self, o):
        return Box(self.re * o.re - self.im * o.im,
                   self.re * o.im + self.im * o.re)

    def conj(self):
        return Box(self.re, -self.im)

    def recip(self):
        """Certified 1/z via conj(z) / |z|^2."""
        norm2 = self.re * self.re + self.im * self.im
        inv = iv_recip(norm2)
        c = self.conj()
        return Box(c.re * inv, c.im * inv)

    def width(self):
        return max(self.re.width(), self.im.width())

    def contains_zero(self):
        return self.re.contains_zero() and self.im.contains_zero()

    def intersects(self, o):
        return self.re.intersects(o.re) and self.im.intersects(o.im)


BOX_ZERO = Box(0)
BOX_ONE = Box(1)
BOX_I = Box(Iv(0), Iv(1))


def box_sqrt(b):
    """Principal-branch complex sqrt of a box (sympy convention: Re >= 0,
    sign(Im result) = sign(Im argument); negative reals map to +i sqrt(-x)).
    Escalates when the branch cut cannot be resolved."""
    m = iv_sqrt(b.re * b.re + b.im * b.im)
    half = Fraction(1, 2)
    re2 = (m + b.re).scaled(half)
    im2 = (m - b.re).scaled(half)
    re2 = Iv(max(Fraction(0), re2.lo), max(Fraction(0), re2.hi))
    im2 = Iv(max(Fraction(0), im2.lo), max(Fraction(0), im2.hi))
    re_s = iv_sqrt(re2)
    im_mag = iv_sqrt(im2)
    if b.im.lo > 0:
        return Box(re_s, im_mag)
    if b.im.hi < 0:
        return Box(re_s, -im_mag)
    if b.im.lo == 0 == b.im.hi:
        if b.re.lo >= 0:
            return Box(re_s)
        if b.re.hi <= 0:
            return Box(Iv(0), im_mag)
    raise EncloseError("complex sqrt across branch cut: refine the argument")


# ------------------------------------------------------------ tree evaluation

def _crootof_box(r, eps):
    """Certified box for a CRootOf via eval_rational (exact rational output)."""
    e = sp.Rational(eps.numerator, eps.denominator) / 2
    v = r.eval_rational(dx=e, dy=e)
    re, im = v.as_real_imag()
    re, im = Fraction(re.p, re.q), Fraction(im.p, im.q)
    h = Fraction(eps) / 2
    return Box(Iv(re - h, re + h), Iv(im - h, im + h))


def _eval(expr, eps):
    if expr.is_Rational:
        return Box(Fraction(expr.p, expr.q))
    if expr is sp.I:
        return BOX_I
    if isinstance(expr, sp.conjugate):
        return _eval(expr.args[0], eps).conj()
    if expr.is_Add:
        acc = BOX_ZERO
        for a in expr.args:
            acc = acc + _eval(a, eps)
        return acc
    if expr.is_Mul:
        acc = BOX_ONE
        for a in expr.args:
            acc = acc * _eval(a, eps)
        return acc
    if expr.is_Pow:
        base, ex = expr.args
        if ex.is_Integer:
            n = int(ex)
            b = _eval(base, eps)
            if n < 0:
                b = b.recip()
                n = -n
            acc = BOX_ONE
            for _ in range(n):
                acc = acc * b
            return acc
        if ex.is_Rational:
            p, r = int(ex.p), int(ex.q)
            b = _eval(base, eps)
            neg = p < 0
            p = abs(p)
            if (b.im.lo == 0 == b.im.hi) and b.re.lo >= 0:
                acc = b.re
                pw = Iv(1)
                for _ in range(p):
                    pw = pw * acc
                out = Box(iv_nthroot(pw, r))
                return out.recip() if neg else out
            if r == 2 and p == 1:
                out = box_sqrt(b)
                return out.recip() if neg else out
            raise EncloseError(f"rational power of general complex: {expr}")
        raise EncloseError(f"unsupported power: {expr}")
    if isinstance(expr, sp.exp):
        # exp(I*pi*r) -> cos(pi r) + I sin(pi r), then radical rewrite
        arg = expr.args[0]
        c = arg / (sp.I * sp.pi)
        if c.is_Rational:
            return _eval(sp.cos(sp.pi * c), eps) + BOX_I * _eval(sp.sin(sp.pi * c), eps)
        raise EncloseError(f"unsupported exp: {expr}")
    if isinstance(expr, (sp.cos, sp.sin)):
        r = expr.rewrite(sp.sqrt)
        if r.has(sp.cos, sp.sin):
            raise EncloseError(f"no radical form: {expr}")
        return _eval(r, eps)
    if isinstance(expr, sp.CRootOf):
        return _crootof_box(expr, eps)
    raise EncloseError(f"unsupported node {type(expr).__name__}: {expr}")


def enclose(expr, eps=Fraction(1, 10**12)):
    """Certified Box for a constant sympy expression, half-width <= eps."""
    expr = sp.sympify(expr)
    if expr.free_symbols:
        raise EncloseError(f"free symbols in {expr}")
    leaf = Fraction(eps)
    for _ in range(64):
        box = _eval(expr, leaf)
        if box.width() <= 2 * Fraction(eps):
            return box
        leaf /= 16
    raise EncloseError(f"enclosure did not converge for {expr}")


def certified_nonzero(expr, max_depth=8):
    """True iff a certified box excludes zero. False means UNDECIDED, not zero."""
    eps = Fraction(1, 10**6)
    for _ in range(max_depth):
        try:
            box = enclose(expr, eps)
        except EncloseError:
            return False
        if not box.contains_zero():
            return True
        eps /= 10**6
    return False
