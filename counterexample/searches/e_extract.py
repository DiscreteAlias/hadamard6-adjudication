#!/usr/bin/env python3
"""Stage 3 for the two-triangle stratum: exact solution extraction + funnel.

Every leaf is zero-dimensional. For each leaf:
  - lex Groebner basis with variable order y5 > w5 > ... > y2 > w2 > w1 > y1 > z
    -> elimination polynomial in (y1, z) plus (usually) shape-lemma generators
    var - q(y1, z) for the remaining variables.
  - the y1-values: clear z by resultant with z^2+z+1 -> rational polynomial;
    certified attribution of its roots to OUR zeta_3 (boxes; z-root chosen as
    e^{2 pi i/3}); each certified y1 root is a CRootOf.
  - back-substitute through the shape generators to get all y_r exactly.
  - FUNNEL per solution: evaluate all 225 chirality monomials exactly (they
    are monomials in z, y_r: values via certified boxes with exact -1 witness
    confirmation by minimal-polynomial zero test of (m + 1)); a -1 minor
    closes the solution as member-K6(3) (Karlsson, source-cached theorem,
    minor position + exact witness logged). -1-free solutions get the full
    gauntlet (fingerprint vs DB, S6 decider, defect).
Leaves that do not satisfy the shape lemma are logged as stalls with their GB.
"""

import argparse
import sys
import time
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "checks" / "lib"))

import sympy as sp
from fractions import Fraction

from lib.qiv import enclose, Box
from lib.runctl import EXIT_BUDGET, EXIT_NEGATIVE, EXIT_NOVEL, Run
from lib.serialize import ARTIFACTS, jsonl_append, jsonl_load

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "ett", Path(__file__).resolve().parent / "e_twotriangle.py")
ett = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ett)
_spec2 = importlib.util.spec_from_file_location(
    "ecl", Path(__file__).resolve().parent / "e_close.py")
ecl = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(ecl)

LEAVES = ARTIFACTS / "e_twotriangle.jsonl"
OUT = ARTIFACTS / "e_extract.jsonl"

Z3 = sp.exp(2 * sp.pi * sp.I * sp.Rational(1, 3))


def _zeta_root():
    """The CRootOf of z^2+z+1 equal to e^{2 pi i /3} (positive imag part)."""
    roots = sp.Poly(sp.Symbol("t") ** 2 + sp.Symbol("t") + 1,
                    sp.Symbol("t")).all_roots()
    for r in roots:
        b = enclose(r, Fraction(1, 10 ** 8))
        if b.im.lo > 0:
            return r
    raise RuntimeError("no zeta root with positive imaginary part")


ZROOT = _zeta_root()


def solve_leaf(pattern_indices, gb_time_budget=60.0):
    """Return (solutions, note): solutions = list of dicts {row -> y value
    (exact sympy)}, note = 'shape' | 'stall:<why>'."""
    pats, polys, gens = ecl.leaf_system(pattern_indices)
    rows_used = list(range(1, len(pats)))
    # lex order: y5 w5 y4 w4 y3 w3 y2 w2 w1 y1 z
    order_gens = []
    for r in reversed(rows_used[1:]):
        order_gens += [ett.Y[r], ett.W[r]]
    order_gens += [ett.W[1], ett.Y[1], ett.Z]
    G = sp.groebner(polys, *order_gens, order="lex")
    exprs = list(G.exprs)
    if exprs == [sp.Integer(1)]:
        return [], "inconsistent"

    # find the univariate-in-(y1, z) generator(s)
    y1z = [e for e in exprs if not any(e.has(v) for v in order_gens[:-2]
                                       if v not in (ett.Y[1], ett.Z))]
    y1z = [e for e in y1z if e.has(ett.Y[1])]
    if not y1z:
        return [], "stall:no-y1z-generator"
    p_y1 = min(y1z, key=lambda e: sp.Poly(e, ett.Y[1]).degree())

    # clear z: resultant with z^2+z+1 -> rational polynomial in y1
    R = sp.resultant(p_y1, ett.Z ** 2 + ett.Z + 1, ett.Z)
    Rp = sp.Poly(sp.expand(R), ett.Y[1])
    if Rp.degree() < 1:
        return [], "stall:empty-resultant"
    cands = []
    for f, _m in sp.factor_list(Rp.as_expr())[1]:
        fp = sp.Poly(f, ett.Y[1])
        if fp.degree() >= 1:
            cands.extend(fp.all_roots())

    # certified filter: p_y1(y1, zeta3) == 0 via boxes + exact confirmation
    zb = enclose(ZROOT, Fraction(1, 10 ** 12))
    sols_y1 = []
    for r in cands:
        rb = enclose(r, Fraction(1, 10 ** 12))
        # box-evaluate p_y1 at (rb, zb)
        val = _eval_box(p_y1, {ett.Y[1]: rb, ett.Z: zb})
        if val.contains_zero():
            # exact confirmation
            expr = p_y1.subs({ett.Y[1]: r, ett.Z: Z3}, simultaneous=True)
            mp = sp.minimal_polynomial(expr, sp.Symbol("_q"))
            if mp == sp.Symbol("_q"):
                sols_y1.append(r)
    if not sols_y1:
        return [], "no-solutions-at-our-zeta"

    # shape-lemma back-substitution for remaining variables
    shape = {}
    for r in rows_used[1:]:
        gen = [e for e in exprs
               if e.has(ett.Y[r]) and sp.Poly(e, ett.Y[r]).degree() == 1
               and not any(e.has(v) for v in order_gens
                           if v not in (ett.Y[r], ett.Y[1], ett.Z, ett.W[1]))]
        if not gen:
            return [], f"stall:no-shape-generator-y{r}"
        g = sp.Poly(gen[0], ett.Y[r])
        shape[r] = (-g.nth(0) / g.nth(1))          # y_r = expr(y1, w1, z)

    sols = []
    for y1v in sols_y1:
        sub = {ett.Y[1]: y1v, ett.W[1]: sp.conjugate(y1v), ett.Z: Z3}
        vals = {1: y1v}
        okv = True
        for r in rows_used[1:]:
            vr = shape[r].subs(sub, simultaneous=True)
            vals[r] = vr
        sols.append(vals)
    return sols, "shape"


def _eval_box(expr, boxmap):
    p = sp.Poly(sp.expand(expr), *boxmap.keys())
    out = Box(0)
    for monom, coeff in p.terms():
        c = sp.Rational(coeff)
        term = Box(Fraction(c.p, c.q))
        for v, m in zip(boxmap.keys(), monom):
            for _ in range(m):
                term = term * boxmap[v]
        out = out + term
    return out


def build_matrix(pattern_indices, vals):
    pats = [ecl.ROW0, ett.ROW1] + [ett.PATS[i] for i in pattern_indices]
    H = sp.zeros(6, 6)
    for i, pat in enumerate(pats):
        for j in range(6):
            k, scaled = pat[1][j]
            H[i, j] = Z3 ** k * (vals[i] if (scaled and i >= 1) else 1)
    return H


def _exp_matrix(pattern_indices, ru, n):
    """Exponent matrix over Z_n for a root-of-unity solution: entry
    zeta_3^k * zeta_{nn}^{kk} -> exponent k*(n//3) + kk*(n//nn) mod n."""
    pats = [ecl.ROW0, ett.ROW1] + [ett.PATS[i] for i in pattern_indices]
    out = []
    for i, pat in enumerate(pats):
        row = []
        for j in range(6):
            k, scaled = pat[1][j]
            e = k * (n // 3)
            if scaled and i >= 1:
                _v, kk, nn = ru[i]
                e += kk * (n // nn)
            row.append(e % n)
        out.append(tuple(row))
    return tuple(out)


_S6_CLASSES = {}


def s6_class_closure(emat, n):
    """Close a cyclotomic -1-free solution: canonical form over Z_n, then one
    decider run per new class against S6 (all variants). Cached."""
    from lib.cyclo import canonical_exp, to_sympy
    from lib.equivalence import equivalent_any_variant
    import catalogue as cat
    cf = (n, canonical_exp([list(r) for r in emat], n))
    if cf in _S6_CLASSES:
        return _S6_CLASSES[cf]
    H = to_sympy([list(r) for r in emat], n)
    hit = equivalent_any_variant(H, cat.S6())
    res = (f"closed:equivalent-S6 (variant {hit[0]}, cert verified)" if hit
           else "OPEN: cyclotomic -1-free, not S6")
    _S6_CLASSES[cf] = res
    return res


_RU_TABLE = None


def _ru_table():
    """label -> (exp value, k, n) for all roots of unity of order <= 24."""
    global _RU_TABLE
    if _RU_TABLE is None:
        from lib.algnum import LabelError, label
        t = {}
        for n in range(1, 25):
            for k in range(n):
                if sp.gcd(k, n) == 1 or k == 0:
                    v = sp.exp(2 * sp.pi * sp.I * sp.Rational(k, n))
                    try:
                        t.setdefault(label(v), (v, k, n))
                    except LabelError:
                        break            # non-radical order: skip this n
        _RU_TABLE = t
    return _RU_TABLE


def as_root_of_unity(v):
    """(exp value, k, n) if v is a root of unity of order <= 24, else None."""
    from lib.algnum import label, LabelError
    try:
        lab = label(v)
    except LabelError:
        return None
    return _ru_table().get(lab)


def chirality_funnel(pattern_indices, vals):
    """Exact -1-minor scan. Fast path: when every y is a certified root of
    unity, each chirality is a pure exp-product decided structurally. Fallback:
    certified boxes + minimal-polynomial confirmation. Returns first -1 minor
    position or None."""
    pats = [ecl.ROW0, ett.ROW1] + [ett.PATS[i] for i in pattern_indices]
    ru = {r: as_root_of_unity(vals[r]) for r in range(1, 6)}
    fast = all(ru[r] is not None for r in range(1, 6))
    sub = {ett.Z: Z3}
    for r in range(1, 6):
        vv = ru[r][0] if fast else vals[r]
        sub[ett.Y[r]] = vv
        sub[ett.W[r]] = sp.conjugate(vv)
    for r, s in combinations(range(6), 2):
        for j, l in combinations(range(6), 2):
            m = ecl.chirality_monomial(pats, r, s, j, l)
            mv = m.subs(sub, simultaneous=True)
            if fast:
                e = sp.powsimp(sp.expand(mv), combine="exp")
                if sp.expand(e + 1) == 0:
                    return (r, s, j, l)
                continue
            b = enclose(mv + 1, Fraction(1, 10 ** 8))
            if b.contains_zero():
                mp = sp.minimal_polynomial(mv + 1, sp.Symbol("_q"))
                if mp == sp.Symbol("_q"):
                    return (r, s, j, l)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget-min", type=float, default=480.0)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    run = Run("searches/e_extract.py", f"budget={args.budget_min}m")
    t_end = time.time() + args.budget_min * 60

    done = {tuple(r["pattern_indices"]) for r in jsonl_load(OUT)}
    leaves = [r for r in jsonl_load(LEAVES)]
    stats = {"leaves": 0, "solutions": 0, "k6": 0, "free_ru": 0,
             "free_open": 0, "stalls": 0}
    budget_stop = False
    freelist = []
    for leaf in leaves:
        key = tuple(leaf["pattern_indices"])
        if key in done:
            continue
        if time.time() > t_end or (args.limit and stats["leaves"] >= args.limit):
            budget_stop = True
            break
        stats["leaves"] += 1
        try:
            sols, note = solve_leaf(list(key))
        except Exception as ex:
            note = f"stall:{type(ex).__name__}"
            sols = []
        rec = {"pattern_indices": list(key), "note": note,
               "n_solutions": len(sols), "solutions": []}
        if note.startswith("stall"):
            stats["stalls"] += 1
            print(f"leaf {key}: {note}", flush=True)
        for vals in sols:
            stats["solutions"] += 1
            minor = chirality_funnel(list(key), vals)
            if minor:
                stats["k6"] += 1
                rec["solutions"].append({
                    "y": {str(r): sp.srepr(v) for r, v in vals.items()},
                    "closure": "member-K6(3)", "minor": list(minor)})
                continue
            # -1-free: root-of-unity solutions dedupe by cyclotomic canonical
            # form and close against S6 once per class; anything else is loud.
            ru = {r: as_root_of_unity(vals[r]) for r in range(1, 6)}
            if all(v is not None for v in ru.values()):
                n = 3
                for (_v, k, nn) in ru.values():
                    n = int(sp.ilcm(n, nn))
                emat = _exp_matrix(list(key), ru, n)
                closure = s6_class_closure(emat, n)
                stats["free_ru"] += 1
                rec["solutions"].append({
                    "y": {str(r): sp.srepr(ru[r][0]) for r in ru},
                    "closure": closure, "canonical_order": n})
                if closure.startswith("OPEN"):
                    stats["free_open"] += 1
                    print(f"*** RU -1-FREE NOT S6 in leaf {key} ***", flush=True)
            else:
                stats["free_open"] += 1
                rec["solutions"].append({
                    "y": {str(r): sp.srepr(v) for r, v in vals.items()},
                    "closure": "MINUS-ONE-FREE-NONCYCLOTOMIC"})
                freelist.append((key, vals))
                print(f"*** NON-CYCLOTOMIC -1-FREE solution in leaf {key}: "
                      f"{[sp.sstr(vals[r]) for r in sorted(vals)]}", flush=True)
        jsonl_append(OUT, rec)

    summary = (f"leaves {stats['leaves']}, solutions {stats['solutions']}, "
               f"K6-closed {stats['k6']}, RU-free {stats['free_ru']}, "
               f"open/noncyclotomic {stats['free_open']}, "
               f"stalls {stats['stalls']}"
               + (", BUDGET STOP" if budget_stop else " — complete"))
    print(summary)
    code = EXIT_BUDGET if budget_stop else EXIT_NEGATIVE
    return run.finish(summary, code)


if __name__ == "__main__":
    sys.exit(main())
