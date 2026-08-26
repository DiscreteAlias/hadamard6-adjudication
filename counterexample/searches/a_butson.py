#!/usr/bin/env python3
"""Stratum A: exhaustive Butson BH(6,q) classification, q in {2,3,4,5,6}.

q in {5,7,11} are empty by Lam-Leung (5,7 verified at row level here; the
enumerator must agree). Entries stay cyclotomic, so nothing here is expected to
be new -- this stratum validates the pipeline and contributes exact reference
points. Every class rep goes through: is_hadamard (both paths) -> invariants ->
defect (both paths, DomainMatrix wins loudly per slag H6-H4) -> equivalence
attempts vs day-1 references (F6, S6, C6, all four variants).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "checks" / "lib"))

import sympy as sp

from hadamard import defect as lib_defect
from hadamard import fourier, is_hadamard, tao_S6
from lib.cyclo import canonical_exp, enumerate_bh6, to_sympy
from lib.equivalence import equivalent_any_variant
from lib.invariants import invariants_bundle, is_hadamard_K
from lib.numfield import fast_defect
from lib.runctl import EXIT_INTERNAL, EXIT_NEGATIVE, Run
from lib.serialize import CANDIDATES, jsonl_append, matrix_srepr


def bjorck_c6():
    s3 = sp.sqrt(3)
    d = (1 - s3) / 2 + sp.I * sp.sqrt(s3 / 2)
    db = sp.conjugate(d)
    row = [1, sp.I * d, -d, -sp.I, -db, sp.I * db]
    return sp.Matrix(6, 6, lambda i, j: row[(j - i) % 6])


REFS = [("F6", fourier(6)), ("S6", tao_S6()), ("C6", bjorck_c6())]


def main():
    run = Run("searches/a_butson.py", "q=2..6")
    problems = []
    summary_bits = []

    ref_bundles = {name: invariants_bundle(H) for name, H in REFS}

    for q in (2, 3, 4, 5, 6):
        raw = enumerate_bh6(q)
        classes = {}
        for m in raw:
            classes.setdefault(canonical_exp(m, q), m)
        summary_bits.append(f"q={q}: raw {len(raw)}, classes {len(classes)}")
        print(f"BH(6,{q}): raw {len(raw)}, canonical classes {len(classes)}")

        for ci, (cf, m) in enumerate(sorted(classes.items())):
            cid = f"A.q{q}.c{ci}"
            H = to_sympy(m, q)

            okK, whyK = is_hadamard_K(H)
            okL, _ = is_hadamard(H)
            if not (okK and okL):
                problems.append(f"{cid}: hadamard check failed K={okK} lib={okL} ({whyK})")
                continue

            bundle = invariants_bundle(H)
            dF = fast_defect(H)
            dL = lib_defect(H)
            defect_note = str(dF)
            if dF != dL:
                # slag H6-H4: DomainMatrix wins; loud event
                problems.append(f"{cid}: DEFECT DISAGREEMENT fast={dF} lib={dL} (DomainMatrix wins)")
                defect_note = f"{dF} (LIB DISAGREED: {dL})"

            match = None
            for name, R in REFS:
                hit = equivalent_any_variant(H, R, bundle)
                if hit:
                    match = (name, hit[0])
                    break

            fp_match = [name for name, b in ref_bundles.items()
                        if b["fingerprint"] == bundle["fingerprint"]]

            if match:
                disp = f"closed:equivalent-{match[0]} (variant {match[1]}, cert verified)"
                novel = f"no (== {match[0]})"
            else:
                disp = "open: awaiting day-2 family solvers"
                novel = (f"fp matches {','.join(fp_match)} but no cert yet" if fp_match
                         else "fp differs from day-1 refs; family grids pending")

            jsonl_append(CANDIDATES, {
                "id": cid,
                "stratum": "A",
                "q": q,
                "exponents": [list(r) for r in m],
                "matrix_srepr": matrix_srepr(H),
                "hadamard": True,
                "defect": defect_note,
                "h2_minors": len(bundle["h2_minors"]),
                "haagerup_novel": novel,
                "disposition": disp,
            })
            print(f"  {cid}: defect {defect_note}, h2-minors {len(bundle['h2_minors'])}, {disp}")

    if problems:
        for p in problems:
            print("PROBLEM:", p)
        return run.finish("; ".join(summary_bits) + " — PROBLEMS: " + "; ".join(problems),
                          EXIT_INTERNAL)
    return run.finish("; ".join(summary_bits), EXIT_NEGATIVE)


if __name__ == "__main__":
    sys.exit(main())
