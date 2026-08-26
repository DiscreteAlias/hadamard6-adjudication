#!/usr/bin/env python3
"""Track B selftest: known-fact anchors that keep every fast path honest.

Exit 0 = all hard gates green. Exit 4 = a hard gate failed (stop and fix).
Soft-gate mismatches print loudly but do not fail the run.
"""

import re
import subprocess
import sys
import time
from itertools import combinations_with_replacement
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks" / "lib"))

import sympy as sp

from hadamard import defect as lib_defect
from hadamard import dephase, fourier, is_hadamard, tao_S6
from lib.algnum import eq_algebraic, label
from lib.cyclo import canonical_exp, enumerate_bh6, to_sympy, vanishing_rows
from lib.equivalence import equivalent, equivalent_any_variant, verify_cert
from lib.invariants import (NONZERO, ZERO, fingerprint, invariants_bundle,
                            is_hadamard_K, zero3)
from lib.numfield import fast_defect

FAILURES = []


def gate(name, ok, detail=""):
    status = "OK  " if ok else "FAIL"
    print(f"{status} {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def soft(name, ok, detail=""):
    status = "ok  " if ok else "SOFT-MISMATCH"
    print(f"{status} {name}" + (f" — {detail}" if detail else ""))


def bjorck_c6():
    s3 = sp.sqrt(3)
    d = (1 - s3) / 2 + sp.I * sp.sqrt(s3 / 2)
    db = sp.conjugate(d)
    row = [1, sp.I * d, -d, -sp.I, -db, sp.I * db]
    return sp.Matrix(6, 6, lambda i, j: row[(j - i) % 6])


def scramble(H, rp, cp, dph, eph, q=12):
    z = lambda k: sp.exp(2 * sp.pi * sp.I * sp.Rational(k, q))
    n = H.rows
    D1 = sp.diag(*[z(k) for k in dph])
    D2 = sp.diag(*[z(k) for k in eph])
    P1 = sp.zeros(n, n)
    P2 = sp.zeros(n, n)
    for i, r in enumerate(rp):
        P1[i, r] = 1
    for j, c in enumerate(cp):
        P2[c, j] = 1
    return D1 * P1 * H * P2 * D2


def main():
    t_all = time.time()
    here = Path(__file__).resolve().parent

    # 1. shared lib self-test
    r = subprocess.run([sys.executable, str(here.parents[0] / "checks" / "lib" / "hadamard.py")],
                       capture_output=True, text=True)
    gate("lib self-test subprocess", r.returncode == 0)

    F6, S6, C6 = fourier(6), tao_S6(), bjorck_c6()

    # 2. canonicalizer adversarial pairs
    pairs = [
        (sp.exp(2 * sp.pi * sp.I / 3), (-1 + sp.I * sp.sqrt(3)) / 2),
        (sp.sqrt(sp.sqrt(3) / 2), 3 ** sp.Rational(1, 4) / sp.sqrt(2)),
        (sp.exp(2 * sp.pi * sp.I * sp.Rational(1, 12)), (sp.sqrt(3) + sp.I) / 2),
        (sp.exp(2 * sp.pi * sp.I * sp.Rational(3, 4)), -sp.I),
    ]
    gate("canonicalizer adversarial pairs", all(eq_algebraic(a, b) for a, b in pairs))
    d_expr = (1 - sp.sqrt(3)) / 2 + sp.I * sp.sqrt(sp.sqrt(3) / 2)
    mp = sp.minimal_polynomial(d_expr, sp.Symbol("z"))
    roots = sp.Poly(mp, sp.Symbol("z")).all_roots()
    gate("radical vs CRootOf spelling", sum(1 for r_ in roots if eq_algebraic(r_, d_expr)) == 1)
    gate("Bjorck d minpoly", label(d_expr)[0] == (1, -2, 0, -2, 1))

    # 3. F6 fingerprint closed form
    fpF6 = dict(fingerprint(F6))
    pred = {}
    for u in range(6):
        for v in range(6):
            pred[(u * v) % 6] = pred.get((u * v) % 6, 0) + 36
    ok = all(fpF6.get(label(sp.exp(2 * sp.pi * sp.I * sp.Rational(m, 6))), 0) == pred[m]
             for m in range(6))
    gate("F6 fingerprint == closed-form prediction", ok)
    gate("F6 fingerprint total 1296", sum(fpF6.values()) == 1296)

    bS6 = invariants_bundle(S6)
    fpS6 = dict(bS6["fingerprint"])
    gate("S6 fingerprint total 1296, mult(1) >= 396",
         sum(fpS6.values()) == 1296 and fpS6.get(label(sp.Integer(1)), 0) >= 396)

    # 4. defect anchors, both paths
    gate("lib defect F6=4, S6=0", lib_defect(F6) == 4 and lib_defect(S6) == 0)
    dF, rF = fast_defect(F6, return_rank=True)
    dS, rS = fast_defect(S6, return_rank=True)
    dC, rC = fast_defect(C6, return_rank=True)
    gate("fast defect ranks F6:21 S6:25 C6:21", (dF, rF, dS, rS, dC, rC) == (4, 21, 0, 25, 4, 21))
    gate("lib defect C6=4 (agrees with fast)", lib_defect(C6) == 4)

    # 5. C6 anchors
    gate("Bjorck relation d^2-(1-sqrt3)d+1=0",
         zero3(d_expr ** 2 - (1 - sp.sqrt(3)) * d_expr + 1) == ZERO)
    gate("|d| = 1", zero3(sp.Abs(d_expr) ** 2 - 1) == ZERO)
    okH, _ = is_hadamard(C6)
    okK, whyK = is_hadamard_K(C6)
    gate("C6 is_hadamard (lib) and is_hadamard_K", okH and okK, whyK)

    # 6. H2 scanner
    bF6 = invariants_bundle(F6)
    gate("S6 has zero chirality -1 minors", len(bS6["h2_minors"]) == 0)
    need = {((j, j + 3), (k, k + 3)) for j in range(3) for k in range(3)}
    gate("F6 has the (j,j+3)x(k,k+3) -1 minors", need <= set(bF6["h2_minors"]))

    # 7. scramble round-trips (fixed, no RNG)
    for name, H, args in [
        ("F6", F6, ([3, 0, 5, 1, 4, 2], [2, 4, 0, 5, 3, 1], [1, 7, 2, 11, 5, 0], [3, 0, 9, 4, 8, 6])),
        ("S6", S6, ([2, 5, 1, 0, 3, 4], [4, 1, 3, 2, 0, 5], [0, 2, 4, 6, 8, 10], [5, 3, 1, 11, 9, 7])),
        ("C6", C6, ([1, 4, 2, 0, 5, 3], [3, 5, 0, 2, 1, 4], [2, 0, 7, 5, 3, 1], [0, 6, 2, 10, 4, 8])),
    ]:
        M = scramble(H, *args)
        gate(f"{name} scramble: fingerprint invariant", fingerprint(M) == fingerprint(H))
        gate(f"{name} scramble: defect invariant", fast_defect(M) == fast_defect(H))
        cert = equivalent(H, M)
        gate(f"{name} scramble: decider certificate", cert is not None and verify_cert(H, M, cert))

    # 8. invariance identities
    for name, H in [("F6", F6), ("S6", S6), ("C6", C6)]:
        fp = fingerprint(H)
        gate(f"{name}: Haagerup(H) == Haagerup(H^T)", fp == fingerprint(H.T))
        gate(f"{name}: Haagerup(H) == Haagerup(conj H)", fp == fingerprint(H.conjugate()))
        gate(f"{name}: Haagerup(dephase(H)) == Haagerup(H)", fp == fingerprint(dephase(H)))
        gate(f"{name}: conjugation-closure of fingerprint",
             all(dict(fp).get(lab_c, 0) == m for (lab_c, m) in _conj_pairs(fp)))

    # 9. structural equivalences
    F2, F3 = fourier(2), fourier(3)
    K23 = sp.Matrix(6, 6, lambda i, j: F2[i // 3, j // 3] * F3[i % 3, j % 3])
    cert = equivalent(F6, K23)
    gate("F2 (x) F3 ~ F6 with certificate", cert is not None and verify_cert(F6, K23, cert))
    gate("C6 ~ C6^T", equivalent_any_variant(C6, C6.T) is not None)

    # 10. Butson gates
    gate("BH(6,2) empty", len(enumerate_bh6(2)) == 0)
    gate("BH(6,5) empty", len(enumerate_bh6(5)) == 0)
    gate("BH(6,7) empty at row level", len(vanishing_rows(7)) == 0)
    gate("BH(6,11) empty at row level", len(vanishing_rows(11)) == 0)
    m3 = enumerate_bh6(3)
    classes3 = {}
    for m in m3:
        classes3.setdefault(canonical_exp(m, 3), m)
    hit = None
    if len(classes3) == 1:
        rep = to_sympy(next(iter(classes3.values())), 3)
        hit = equivalent_any_variant(rep, S6)
    gate("BH(6,3): one class, decider-equivalent to S6 (some variant)",
         len(classes3) == 1 and hit is not None, f"variant {hit[0] if hit else '-'}")

    # 11. independent q=6 vanishing count (Lam-Leung decomposition)
    msets = set()
    from collections import Counter as C_
    for combo in combinations_with_replacement(range(3), 3):   # three antipodal pairs
        c = C_()
        for e in combo:
            c[e] += 1
            c[e + 3] += 1
        msets.add(tuple(sorted(c.elements())))
    for t1 in range(2):                                        # two triangles
        for t2 in range(2):
            c = C_()
            for e in (t1, t1 + 2, t1 + 4):
                c[e] += 1
            for e in (t2, t2 + 2, t2 + 4):
                c[e] += 1
            msets.add(tuple(sorted(c.elements())))
    from math import factorial
    total = 0
    for ms in msets:
        c = C_(ms)
        if c[0] == 0:
            continue
        perms = factorial(6)
        for m in c.values():
            perms //= factorial(m)
        total += perms * c[0] // 6
    gate("q=6 vanishing rows == 340 (independent derivation)",
         total == len(vanishing_rows(6)) == 340, f"derived {total}")

    # 12. zero3
    gate("zero3 proves sqrt2*sqrt3 - sqrt6 == 0", zero3(sp.sqrt(2) * sp.sqrt(3) - sp.sqrt(6)) == ZERO)
    gate("zero3 proves sqrt2 - 1 != 0", zero3(sp.sqrt(2) - 1) == NONZERO)

    # 12b. day-2 catalogue anchors
    import catalogue as cat
    from lib.families import h2_block_certificate, verify_h2_certificate
    from lib.numfield import entry_pairs, real_field_for

    B6h = cat.B6_point(1, 4)
    Kf = real_field_for(list(B6h) + list(B6h.conjugate().T))
    _, p1 = entry_pairs(B6h, Kf)
    _, p2 = entry_pairs(B6h.conjugate().T, Kf)
    gate("B6(pi/2) is self-adjoint (exact field pairs)", p1 == p2)

    hitD = equivalent_any_variant(B6h, cat.D6_point(0, 1))
    gate("B6(pi/2) ~ D6 (BN observation, cert)", hitD is not None,
         f"variant {hitD[0] if hitD else '-'}")

    hitF = equivalent_any_variant(cat.M6_x(sp.Integer(1)), F6)
    gate("M6(1) ~ F6 (MS observation, cert)", hitF is not None,
         f"variant {hitF[0] if hitF else '-'}")

    for nm, Hh in [("D6(0)", cat.D6_point(0, 1)), ("F6(1/12,5/12)", cat.F6_point(1, 12, 5, 12))]:
        from lib.invariants import invariants_bundle as _ib
        bb = _ib(Hh)
        cert = h2_block_certificate(Hh, bb["h2_minors"][0])
        gate(f"K6 block certificate for {nm}", cert is not None
             and verify_h2_certificate(Hh, cert))

    g6rec = Path(__file__).resolve().parents[1] / "checks" / "lib" / "g6_verification.json"
    soft("G6 generic point verification record present", g6rec.exists(),
         str(g6rec))

    # 13. no-float lint over counterexample/
    bad = []
    pat = re.compile(r"\bevalf\b|\bnsimplify\b|\bfloat\(|math\.sqrt|\bnumpy\b|\brandom\b|\.n\(\)")
    for p in sorted(here.rglob("*.py")):
        if "artifacts" in p.parts:
            continue
        for ln, line in enumerate(p.read_text().splitlines(), 1):
            if pat.search(line) and "no-float lint" not in line:
                bad.append(f"{p.name}:{ln}: {line.strip()}")
    gate("no-float lint", not bad, "; ".join(bad[:5]))

    print(f"\n{'ALL HARD GATES GREEN' if not FAILURES else 'FAILURES: ' + ', '.join(FAILURES)}"
          f"  ({time.time() - t_all:.0f}s)")
    return 4 if FAILURES else 0


def _conj_pairs(fp):
    """(conjugate-label, multiplicity) pairs for a fingerprint: the label of the
    conjugate of each fingerprint value, paired with that value's multiplicity."""
    from lib.algnum import _poly_roots  # canonical root order
    out = []
    for (coeffs, idx), m in fp:
        if len(coeffs) == 2:            # rational: self-conjugate
            out.append(((coeffs, idx), m))
            continue
        roots = _poly_roots(coeffs)
        target = sp.conjugate(roots[idx])
        cidx = next(k for k, r_ in enumerate(roots) if eq_algebraic(r_, target))
        out.append(((coeffs, cidx), m))
    return out


if __name__ == "__main__":
    sys.exit(main())
