#!/usr/bin/env python3
"""Stage 2 for the two-triangle stratum: wholesale closure of leaves.

For each consistent leaf (pattern assignment with nonempty solution set), every
chirality value H[r][j] H[s][l] conj(H[r][l]) conj(H[s][j]) is a MONOMIAL in
(z, y_i, w_i). If for some (rows, cols) the ideal proves chirality == -1
(NF(m + 1) == 0 modulo the leaf's Groebner basis), then EVERY matrix in the
leaf has a 2x2 Hadamard submatrix, hence is H2-reducible, hence lies in
K6^(3) (Karlsson) — the whole leaf closes at once.

Leaves with no identically-(-1) chirality are the survivors: their solutions
could contain -1-free matrices. They go to exact extraction (stage 3).
"""

import argparse
import sys
import time
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "checks" / "lib"))

import sympy as sp

from lib.runctl import EXIT_BUDGET, EXIT_NEGATIVE, Run
from lib.serialize import ARTIFACTS, jsonl_append, jsonl_load

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "ett", Path(__file__).resolve().parent / "e_twotriangle.py")
ett = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ett)

LEAVES = ARTIFACTS / "e_twotriangle.jsonl"
OUT = ARTIFACTS / "e_close.jsonl"

ROW0 = (None, {j: (0, False) for j in range(6)})   # the all-ones row


def leaf_system(pattern_indices):
    pats = [ROW0, ett.ROW1] + [ett.PATS[i] for i in pattern_indices]
    rows_used = list(range(1, len(pats)))          # y-variables for rows 1..5
    polys = []
    for a in range(1, len(pats)):
        for b in range(a + 1, len(pats)):
            e1, e2 = ett.pair_equations(pats[a], a, pats[b], b)
            polys += [e1, e2]
    gens = [ett.Z]
    for r in rows_used:
        gens += [ett.Y[r], ett.W[r]]
    rels = [ett.ZREL] + [ett.Y[r] * ett.W[r] - 1 for r in rows_used]
    return pats, polys + rels, gens


def chirality_monomial(pats, r, s, j, l):
    """H[r][j] H[s][l] conj(H[r][l]) conj(H[s][j]) as a sympy monomial."""
    def ent(rr, jj, conj):
        k, scaled = pats[rr][1][jj]
        zpow = (-k) % 3 if conj else k
        m = ett.Z ** zpow
        if scaled and rr >= 1:
            m *= (ett.W[rr] if conj else ett.Y[rr])
        return m
    return sp.expand(ent(r, j, False) * ent(s, l, False)
                     * ent(r, l, True) * ent(s, j, True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget-min", type=float, default=240.0)
    args = ap.parse_args()
    run = Run("searches/e_close.py", f"budget={args.budget_min}m")
    t_end = time.time() + args.budget_min * 60

    done = {tuple(r["pattern_indices"]) for r in jsonl_load(OUT)}
    leaves = jsonl_load(LEAVES)
    n_closed = n_surv = 0
    budget_stop = False
    for leaf in leaves:
        key = tuple(leaf["pattern_indices"])
        if key in done:
            continue
        if time.time() > t_end:
            budget_stop = True
            break
        pats, polys, gens = leaf_system(leaf["pattern_indices"])
        G = sp.groebner(polys, *gens, order="grevlex")
        if len(G.exprs) == 1 and G.exprs[0] == 1:
            jsonl_append(OUT, {"pattern_indices": list(key),
                               "closure": "inconsistent"})
            continue
        witness = None
        for r, s in combinations(range(6), 2):
            for j, l in combinations(range(6), 2):
                m = chirality_monomial(pats, r, s, j, l)
                if G.reduce(sp.expand(m + 1))[1] == 0:
                    witness = (r, s, j, l)
                    break
            if witness:
                break
        if witness:
            n_closed += 1
            jsonl_append(OUT, {"pattern_indices": list(key),
                               "closure": "K6-wholesale",
                               "minor": list(witness),
                               "zero_dimensional": leaf.get("zero_dimensional")})
        else:
            n_surv += 1
            jsonl_append(OUT, {"pattern_indices": list(key),
                               "closure": "SURVIVOR",
                               "zero_dimensional": leaf.get("zero_dimensional")})
            print(f"SURVIVOR leaf {key} (0-dim={leaf.get('zero_dimensional')})",
                  flush=True)
    summary = (f"{n_closed} leaves closed wholesale (K6), {n_surv} survivors"
               + (", BUDGET STOP" if budget_stop else ""))
    print(summary)
    return run.finish(summary, EXIT_BUDGET if budget_stop else EXIT_NEGATIVE)


if __name__ == "__main__":
    sys.exit(main())
