#!/usr/bin/env python3
"""Build the reference DB: exact catalogue points + invariants + defect census.

Every point: is_hadamard (sound field path) -> invariants bundle -> defect
(DomainMatrix path; lib path cross-checked on cyclotomic points only, per
slag H6-H4/H6-H5). Census rule: any defect outside {0, 4} is flagged loudly —
it would be the most interesting object in the run.

Output: catalogue/db/points.jsonl (append-only; idempotent by id).
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "checks" / "lib"))

import sympy as sp

import catalogue as cat
from lib.invariants import invariants_bundle, is_hadamard_K
from lib.numfield import fast_defect
from lib.runctl import EXIT_INTERNAL, EXIT_NEGATIVE, Run
from lib.serialize import ROOT, jsonl_append, jsonl_load, matrix_srepr

DB = ROOT / "catalogue" / "db" / "points.jsonl"


def points():
    w = lambda p, q: sp.exp(2 * sp.pi * sp.I * sp.Rational(p, q))
    # F6(a,b) at 12th-root parameters
    for p1 in range(12):
        for p2 in range(12):
            yield f"F6.{p1}_12.{p2}_12", cat.F6_point(p1, 12, p2, 12), 4
    # D6(c) at 12th- and 8th-root parameters
    for p in range(12):
        yield f"D6.{p}_12", cat.D6_point(p, 12), 4
    for p in (1, 3, 5, 7):
        yield f"D6.{p}_8", cat.D6_point(p, 8), 4
    # C6 and S6
    yield "C6", cat.C6(), 4
    yield "S6", cat.S6(), 0
    # B6(theta): y = e^{i theta} in the valid range (|theta| >= arccos((sqrt3-1)/2) ~ 68.53deg)
    for name, y in [("B6.1_4", w(1, 4)), ("B6.1_3", w(1, 3)), ("B6.1_2", w(1, 2)),
                    ("B6.5_12", w(5, 12)), ("B6.7_12", w(7, 12)),
                    ("B6.3_8", w(3, 8)), ("B6.5_8", w(5, 8)), ("B6.2_5", w(2, 5))]:
        yield name, cat.B6_y(y), 4
    # M6(x): x a root of unity, x != +-i. The zeta_5 points (1/5, 2/5) are
    # deliberately omitted: their real fields make DomainMatrix defect
    # computations pathologically slow (>6h observed) and the 12th/8th/6th-root
    # grid already anchors the family (coverage note in the final report).
    for p, q in [(0, 1), (1, 12), (5, 12), (7, 12), (11, 12), (1, 8), (3, 8),
                 (5, 8), (7, 8), (1, 6), (5, 6), (1, 3), (2, 3), (1, 2)]:
        yield f"M6.{p}_{q}", cat.M6_x(w(p, q)), 4


def main():
    run = Run("catalogue/build_db.py")
    have = {r["id"] for r in jsonl_load(DB)}
    n_ok = n_flag = 0
    problems = []
    for pid, H, expd in points():
        if pid in have:
            continue
        t0 = time.time()
        try:
            ok, why = cat.is_hadamard_field(H)
            if not ok:
                problems.append(f"{pid}: not hadamard ({why})")
                continue
            bundle = invariants_bundle(H)
            d = fast_defect(H)
            rec = {
                "id": pid,
                "matrix_srepr": matrix_srepr(H),
                "defect": d,
                "expected_defect": expd,
                "fingerprint": [[list(lab[0]), lab[1], m] for lab, m in bundle["fingerprint"]],
                "h2_minors": len(bundle["h2_minors"]),
                "wall_s": round(time.time() - t0, 1),
            }
            jsonl_append(DB, rec)
            n_ok += 1
            flag = ""
            if d != expd:
                n_flag += 1
                flag = f"  *** DEFECT {d} != expected {expd} — CENSUS FLAG ***"
                problems.append(f"{pid}: defect {d} != {expd}")
            print(f"{pid}: defect {d}, h2 {len(bundle['h2_minors'])}, "
                  f"{rec['wall_s']}s{flag}", flush=True)
        except Exception as ex:
            problems.append(f"{pid}: {type(ex).__name__}: {ex}")
            print(f"{pid}: ERROR {type(ex).__name__}: {ex}", flush=True)
    summary = f"{n_ok} points built, {n_flag} census flags, {len(problems)} problems"
    if problems:
        for p in problems:
            print("PROBLEM:", p)
        return run.finish(summary, EXIT_INTERNAL)
    return run.finish(summary, EXIT_NEGATIVE)


if __name__ == "__main__":
    sys.exit(main())
