#!/usr/bin/env python3
"""The gauntlet: exact verdict for one candidate matrix. Track B.

Stages (cheap -> expensive), per the verdict discipline:
  1. sound Hadamard check (field coordinates); lib is_hadamard cross-checked,
     disagreement logged loudly (slag H6-H5) and the field verdict wins.
  2. canonical invariants (fingerprint, row profiles, H2 minors, defect via
     DomainMatrix; lib defect cross-checked on request only).
  3. fingerprint join against the reference DB -> exact equivalence attempts
     (all four variants) with re-verified certificates.
  4. closure cascade: K6^(3) via constructive H2-block certificate
     (Karlsson), S6 via decider; else open -> G6 membership is day-3 work.
Verdicts: closed:equivalent-<ref> / closed:member-K6(3) / closed:equivalent-S6
/ bucket:h2-no-witness (LOUD) / unresolved-G6.

Usage: verify_candidate.py --srepr FILE --id ID  (or import run_gauntlet).
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks" / "lib"))

import sympy as sp

import catalogue as cat
from hadamard import is_hadamard as lib_is_hadamard
from lib.equivalence import equivalent_any_variant
from lib.families import close_candidate
from lib.invariants import invariants_bundle, is_hadamard_K
from lib.ledger import regenerate
from lib.numfield import fast_defect
from lib.runctl import (EXIT_INTERNAL, EXIT_NEGATIVE, EXIT_NOVEL,
                        EXIT_UNRESOLVED_G6)
from lib.serialize import (CANDIDATES, ROOT, jsonl_append, jsonl_load,
                           matrix_from_srepr, matrix_srepr)

DB = ROOT / "catalogue" / "db" / "points.jsonl"


def _fp_key(fp):
    return tuple((tuple(lab[0]), lab[1], m) for lab, m in fp)


def run_gauntlet(H, cid, log=print):
    H = sp.Matrix(H)
    rec = {"id": cid, "matrix_srepr": matrix_srepr(H)}

    okK, whyK = is_hadamard_K(H)
    okL, _ = lib_is_hadamard(H)
    if okK != okL:
        log(f"{cid}: LOUD: lib is_hadamard={okL} vs field={okK} — field wins "
            f"(slag H6-H5)")
    if not okK:
        rec.update({"hadamard": False, "defect": "-",
                    "haagerup_novel": "-", "disposition": f"rejected: {whyK}"})
        jsonl_append(CANDIDATES, rec)
        return "rejected", rec

    bundle = invariants_bundle(H)
    d = fast_defect(H)
    rec.update({"hadamard": True, "defect": d,
                "h2_minors": len(bundle["h2_minors"])})
    if d not in (0, 4):
        log(f"{cid}: *** DEFECT {d} outside {{0,4}} — census anomaly ***")

    # DB fingerprint join
    fp = _fp_key(bundle["fingerprint"])
    db = jsonl_load(DB)
    matches = [r for r in db
               if tuple((tuple(x[0]), x[1], x[2]) for x in r["fingerprint"]) == fp]
    for r in matches[:8]:
        R = matrix_from_srepr(r["matrix_srepr"])
        hit = equivalent_any_variant(H, R, bundle)
        if hit:
            rec.update({
                "haagerup_novel": f"no (== {r['id']})",
                "disposition": f"closed:equivalent-{r['id']} (variant {hit[0]}, cert verified)",
            })
            jsonl_append(CANDIDATES, rec)
            return "closed", rec

    quick = [("F6", cat.F6_point(0, 1, 0, 1)),
             ("D6(0)", cat.D6_point(0, 1)), ("C6", cat.C6())]
    verdict, detail = close_candidate(H, bundle, quick_refs=quick, s6=cat.S6())

    fp_note = (f"fp matches {len(matches)} DB point(s), no cert" if matches
               else "fp not in DB")
    if verdict == "closed:equivalent":
        rec.update({"haagerup_novel": f"no (== {detail['ref']})",
                    "disposition": f"closed:equivalent-{detail['ref']} "
                                   f"(variant {detail['variant']}, cert verified)"})
        code = "closed"
    elif verdict == "closed:member-K6(3)":
        rec.update({"haagerup_novel": fp_note,
                    "disposition": "closed:member-K6(3) (H2-block cert verified; "
                                   "Karlsson 1003.4133/4177)"})
        code = "closed"
    elif verdict == "closed:equivalent-S6":
        rec.update({"haagerup_novel": "no (== S6)",
                    "disposition": f"closed:equivalent-S6 (variant {detail['variant']})"})
        code = "closed"
    elif verdict == "bucket:h2-no-witness":
        rec.update({"haagerup_novel": fp_note,
                    "disposition": "LOUD bucket: H2-signature but no K6 block "
                                   "certificate — decoder bug or theorem issue"})
        code = "bucket"
        log(f"{cid}: *** {rec['disposition']} ***")
    else:
        rec.update({"haagerup_novel": fp_note,
                    "disposition": "unresolved-G6: no minor, not S6 — needs "
                                   "Dilation membership run (day 3)"})
        code = "unresolved-G6"
    jsonl_append(CANDIDATES, rec)
    return code, rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--srepr", type=str, help="file containing sympy srepr of the matrix")
    ap.add_argument("--id", type=str, required=True)
    args = ap.parse_args()
    H = matrix_from_srepr(Path(args.srepr).read_text())
    t0 = time.time()
    code, rec = run_gauntlet(H, args.id)
    regenerate()
    print(f"{args.id}: {rec['disposition']} ({time.time()-t0:.1f}s)")
    return {"closed": EXIT_NEGATIVE, "rejected": EXIT_NEGATIVE,
            "unresolved-G6": EXIT_UNRESOLVED_G6,
            "bucket": EXIT_INTERNAL}.get(code, EXIT_NOVEL)


if __name__ == "__main__":
    sys.exit(main())
