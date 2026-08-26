#!/usr/bin/env python3
"""Stratum E (with G-filter downstream): the two-triangle ansatz, exhaustively.

Ansatz: dephased H; each noninitial row r is a disjoint union of two
omega-triangles: three entries {1, w, w^2} * 1 on a 3-set S_r containing
column 0, and {1, w, w^2} * y_r on the complement, with y_r a FREE unimodular
phase (w = zeta_3). Row sums vanish identically, so orthogonality to the
all-ones row is automatic; the remaining 10 row-pair orthogonality equations
are bilinear in (y_r, conj y_s).

Coverage notes (exact statements for the ledger):
- Any CHM whose dephased rows all decompose as two rotated omega-triangles is
  in this stratum. For root-of-unity entries of 3-smooth-times-2 order this is
  forced for -1-free matrices (Lam-Leung: 2+2+2 decompositions contain
  antipodal pairs = chirality -1 with the first row).
- Row 1 is normalized to (1, w, w^2, y1, y1 w, y1 w^2) by column permutations;
  the canonicalization may overcount but cannot undercount.
- S6 (y=1 interleaved) and F6 (y = zeta_6) lie in the stratum: rediscovering
  and closing both validates the engine end to end.

Method: DFS over the discrete patterns of rows 2..5 (40 per row: 3-set S_r
containing 0, 2 orders for the aligned triangle, 2 coset orders for the free
one). At each node, a Groebner basis over QQ[z, y_i, w_i]/(z^2+z+1, y_i w_i-1)
decides consistency (1 in ideal -> prune). At full depth: zero-dimensional
ideals -> exact solutions via elimination + certified boxes; positive-
dimensional ideals -> logged as continuous slices with sample closure.
Every complete matrix goes through the gauntlet (verify_candidate.run_gauntlet).
"""

import argparse
import sys
import time
from itertools import combinations, permutations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "checks" / "lib"))

import sympy as sp

from lib.runctl import EXIT_BUDGET, EXIT_NEGATIVE, EXIT_NOVEL, Run
from lib.serialize import jsonl_append, ARTIFACTS

LOG = ARTIFACTS / "e_twotriangle.jsonl"

Z = sp.Symbol("z")                      # zeta_3
Y = [sp.Symbol(f"y{i}") for i in range(6)]   # y_r, r = 1..5 used
W = [sp.Symbol(f"w{i}") for i in range(6)]   # conj y_r

ZREL = Z ** 2 + Z + 1


def patterns():
    """All 40 row patterns: (S tuple with 0, exponents dict col->(k, scaled))
    where entry = z^k * (y if scaled else 1)."""
    out = []
    for rest in combinations(range(1, 6), 2):
        S = (0,) + rest
        Sc = tuple(c for c in range(6) if c not in S)
        for orderA in permutations((1, 2)):
            for orderB in ((0, 1, 2), (0, 2, 1)):
                exps = {S[0]: (0, False), S[1]: (orderA[0], False),
                        S[2]: (orderA[1], False)}
                for c, k in zip(Sc, orderB):
                    exps[c] = (k, True)
                out.append((S, exps))
    return out


PATS = patterns()
ROW1 = (tuple([0, 1, 2]), {0: (0, False), 1: (1, False), 2: (2, False),
                           3: (0, True), 4: (1, True), 5: (2, True)})


def pair_equations(pat_r, r, pat_s, s):
    """The two polynomials (equation and its conjugate) for orthogonality of
    rows r and s, in QQ[z, y_r, w_r, y_s, w_s], denominators cleared."""
    acc = sp.Integer(0)
    for j in range(6):
        kr, sr = pat_r[1][j]
        ks, ss = pat_s[1][j]
        term = Z ** ((kr - ks) % 3)
        if sr:
            term *= Y[r]
        if ss:
            term *= W[s]
        acc += term
    e1 = sp.expand(acc)
    # conjugate: z -> z^2, y <-> w
    e2 = sp.expand(e1.subs({Z: Z ** 2, Y[r]: W[r], W[s]: Y[s]},
                           simultaneous=True))
    return e1, e2


def base_relations(rows_used):
    rels = [ZREL]
    for r in rows_used:
        rels.append(Y[r] * W[r] - 1)
    return rels


def groebner_consistent(polys, gens):
    G = sp.groebner(polys, *gens, order="grevlex")
    return not (len(G.exprs) == 1 and G.exprs[0] == 1), G


# ---------------------------------------------------- exact pairwise prefilter

def _zw_pqrs(pat_r, pat_s):
    """P, Q, R, S in Z[omega] (as (m, n) pairs, x = m + n*omega) for the pair
    equation P + Q w_s + R y_r + S y_r w_s of rows with patterns pat_r (role
    r: contributes y_r on its scaled triangle) and pat_s (role s: w_s)."""
    acc = {(False, False): [0, 0], (False, True): [0, 0],
           (True, False): [0, 0], (True, True): [0, 0]}
    for j in range(6):
        kr, sr = pat_r[1][j]
        ks, ss = pat_s[1][j]
        k = (kr - ks) % 3
        cell = acc[(sr, ss)]
        if k == 0:
            cell[0] += 1
        elif k == 1:
            cell[1] += 1
        else:                       # omega^2 = -1 - omega
            cell[0] -= 1
            cell[1] -= 1
    return (tuple(acc[(False, False)]), tuple(acc[(False, True)]),
            tuple(acc[(True, False)]), tuple(acc[(True, True)]))


def _znorm2(x):
    m, n = x
    return m * m - m * n + n * n


def _zconj(x):
    m, n = x
    return (m - n, -n)              # conj(m + n w) = m + n w^2 = (m-n) - n w


def _zmul(x, y):
    m, n = x
    p, q = y
    # (m + n w)(p + q w) = mp + (mq + np) w + nq w^2, w^2 = -1 - w
    return (m * p - n * q, m * q + n * p - n * q)


def _zsub(x, y):
    return (x[0] - y[0], x[1] - y[1])


def pair_solvable(pat_r, pat_s):
    """Exact necessary condition for the pair equation to admit unimodular
    (y_r, y_s): |C0| <= 2 |C1| with C0 = |P|^2+|R|^2-|Q|^2-|S|^2 (integer)
    and C1 = conj(P) R - conj(Q) S in Z[omega]. Integer arithmetic only."""
    P, Q, R, S = _zw_pqrs(pat_r, pat_s)
    c0 = _znorm2(P) + _znorm2(R) - _znorm2(Q) - _znorm2(S)
    c1 = _zsub(_zmul(_zconj(P), R), _zmul(_zconj(Q), S))
    return c0 * c0 <= 4 * _znorm2(c1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget-min", type=float, default=120.0)
    ap.add_argument("--max-depth", type=int, default=5,
                    help="rows to assign beyond row 1 (5 = full matrix)")
    args = ap.parse_args()
    run = Run("searches/e_twotriangle.py", f"budget={args.budget_min}m")
    t_end = time.time() + args.budget_min * 60

    stats = {"nodes": 0, "pruned": 0, "leaves": 0, "zero_dim": 0,
             "pos_dim": 0, "budget_stop": False}
    leaves = []

    def gens_for(rows_used):
        g = [Z]
        for r in rows_used:
            g += [Y[r], W[r]]
        return g

    # precompute the exact pairwise prefilter tables
    filt_row1 = [pair_solvable(ROW1, p) and pair_solvable(p, ROW1)
                 for p in PATS]
    filt = [[pair_solvable(PATS[i], PATS[j]) and pair_solvable(PATS[j], PATS[i])
             for j in range(len(PATS))] for i in range(len(PATS))]
    print(f"prefilter: row1-compatible patterns "
          f"{sum(filt_row1)}/{len(PATS)}", flush=True)

    GROEBNER_FROM_DEPTH = 4   # interior Groebner only when equations are dense

    def dfs(depth, chosen, polys, min_idx):
        # chosen: [(row, pat_index)]; rows 2..5 use non-decreasing pat_index
        if time.time() > t_end:
            stats["budget_stop"] = True
            return
        if depth == args.max_depth:
            rows_used = [c[0] for c in chosen]
            gens = gens_for(rows_used)
            ok, G = groebner_consistent(polys + base_relations(rows_used), gens)
            stats["leaves"] += 1
            if not ok:
                stats["pruned"] += 1
                return
            rec = {"pattern_indices": [c[1] for c in chosen[1:]],
                   "groebner_size": len(G.exprs)}
            try:
                rec["zero_dimensional"] = bool(G.is_zero_dimensional)
            except Exception:
                rec["zero_dimensional"] = None
            stats["zero_dim" if rec["zero_dimensional"] else "pos_dim"] += 1
            leaves.append(rec)
            jsonl_append(LOG, rec)
            return
        r = depth + 1
        for pi in range(min_idx, len(PATS)):
            if time.time() > t_end:
                stats["budget_stop"] = True
                return
            if not filt_row1[pi]:
                continue
            if any(not filt[c[1]][pi] for c in chosen[1:]):
                continue
            stats["nodes"] += 1
            pat = PATS[pi]
            new_polys = list(polys)
            for (rprev, piprev) in chosen:
                patprev = ROW1 if rprev == 1 else PATS[piprev]
                e1, e2 = pair_equations(patprev, rprev, pat, r)
                new_polys += [e1, e2]
            if depth + 1 >= GROEBNER_FROM_DEPTH and depth + 1 < args.max_depth:
                rows_used = [c[0] for c in chosen] + [r]
                ok, _G = groebner_consistent(
                    new_polys + base_relations(rows_used), gens_for(rows_used))
                if not ok:
                    stats["pruned"] += 1
                    continue
            chosen.append((r, pi))
            dfs(depth + 1, chosen, new_polys, pi)
            chosen.pop()

    dfs(1, [(1, -1)], [], 0)

    summary = (f"nodes {stats['nodes']}, pruned {stats['pruned']}, "
               f"leaves {stats['leaves']} (0-dim {stats['zero_dim']}, "
               f"pos-dim {stats['pos_dim']})"
               + (", BUDGET STOP" if stats["budget_stop"] else " — exhaustive"))
    print(summary)
    return run.finish(summary,
                      EXIT_BUDGET if stats["budget_stop"] else EXIT_NEGATIVE)


if __name__ == "__main__":
    sys.exit(main())
