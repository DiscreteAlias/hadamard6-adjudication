"""Canonical labels for algebraic numbers. Track B.

label(expr) = (minpoly_coeffs, root_index): the normalized integer minimal
polynomial over Q together with the index of the value among that polynomial's
roots in sympy's canonical CRootOf ordering. Two constant expressions denote the
same algebraic number iff their labels are equal -- across any surface spelling
(radicals, exp form, RootOf). Labels are hashable and totally ordered, so
multisets of algebraic numbers become comparable exact objects.

Index determination is certified: qiv boxes for the expression vs eval_rational
boxes for each candidate root, refined until exactly one candidate intersects.
No floating point; failures raise (escalate), never guess.
"""

from fractions import Fraction

import sympy as sp

from .qiv import Box, EncloseError, enclose

_X = sp.Symbol("_algnum_x")

_minpoly_cache = {}
_label_cache = {}
_roots_cache = {}


class LabelError(Exception):
    pass


def minpoly_coeffs(expr):
    """Normalized integer coefficient tuple (leading first) of the minimal
    polynomial over Q. Primitive, positive leading coefficient."""
    key = sp.srepr(expr)
    if key in _minpoly_cache:
        return _minpoly_cache[key]
    p = sp.Poly(sp.minimal_polynomial(expr, _X), _X)
    coeffs = tuple(int(c) for c in p.all_coeffs())
    g = 0
    for c in coeffs:
        g = sp.igcd(g, c)
    if g > 1:
        coeffs = tuple(c // g for c in coeffs)
    if coeffs[0] < 0:
        coeffs = tuple(-c for c in coeffs)
    _minpoly_cache[key] = coeffs
    return coeffs


def _poly_roots(coeffs):
    """CRootOf list (canonical sympy order) for an integer coefficient tuple."""
    if coeffs in _roots_cache:
        return _roots_cache[coeffs]
    p = sp.Poly(list(coeffs), _X)
    roots = [sp.CRootOf(p, k) for k in range(p.degree())]
    _roots_cache[coeffs] = roots
    return roots


def _root_box(root, eps):
    e = sp.Rational(Fraction(eps).numerator, Fraction(eps).denominator) / 2
    v = root.eval_rational(dx=e, dy=e)
    re, im = v.as_real_imag()
    re, im = Fraction(re.p, re.q), Fraction(im.p, im.q)
    h = Fraction(eps) / 2
    from .qiv import Iv
    return Box(Iv(re - h, re + h), Iv(im - h, im + h))


def label(expr):
    """(minpoly_coeffs, root_index) for a constant algebraic sympy expression."""
    expr = sp.sympify(expr)
    key = sp.srepr(expr)
    if key in _label_cache:
        return _label_cache[key]
    if expr.free_symbols:
        raise LabelError(f"free symbols in {expr}")

    coeffs = minpoly_coeffs(expr)
    deg = len(coeffs) - 1
    if deg == 1:
        # rational: unique root of a x + b
        out = (coeffs, 0)
        _label_cache[key] = out
        return out

    roots = _poly_roots(coeffs)
    eps = Fraction(1, 10**8)
    for _ in range(24):
        try:
            ebox = enclose(expr, eps)
        except EncloseError as exc:
            raise LabelError(f"cannot enclose {expr}: {exc}") from exc
        hits = [k for k, r in enumerate(roots) if _root_box(r, eps).intersects(ebox)]
        if len(hits) == 1:
            out = (coeffs, hits[0])
            _label_cache[key] = out
            return out
        if len(hits) == 0:
            raise LabelError(
                f"box of {expr} meets no root of its own minpoly {coeffs} "
                f"at eps={eps} -- minpoly/enclosure inconsistency")
        eps /= 10**4
    raise LabelError(f"root separation did not resolve for {expr}")


def eq_algebraic(a, b):
    """Exact equality of two constant algebraic expressions."""
    return label(a) == label(b)


def label_sort_key(lab):
    coeffs, idx = lab
    return (len(coeffs), coeffs, idx)


def canonical_multiset(exprs):
    """Sorted tuple of (label, multiplicity) -- a canonical, comparable object."""
    from collections import Counter
    c = Counter(label(e) for e in exprs)
    return tuple(sorted(c.items(), key=lambda kv: label_sort_key(kv[0])))
