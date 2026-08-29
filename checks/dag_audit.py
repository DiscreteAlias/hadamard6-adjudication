#!/usr/bin/env python3
"""
dag_audit.py — structural audit of a claim DAG.  [D]

Paper-agnostic. Checks what can be checked without reading the paper, and
emits a coverage map showing where omissions could hide.

    python3 checks/dag_audit.py dag.md --pages 50 --target C26 --audited C19

Exit 0 if every structural check passes, 1 otherwise. Prints a record intended
to be pasted into the ledger, not just eyeballed.

What this CANNOT tell you: whether any row faithfully describes the paper.
Internal consistency is not fidelity. See VERIFY.md.
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict

ROW = re.compile(r"^\|\s*(?P<cells>.+?)\s*\|\s*$")
NODE = re.compile(r"^(?:[A-Z]\d{1,2}|U\d+)$")
TOKEN = re.compile(r"\b(?:[DPTLCSU]\d{1,2})\b")
PAGES = re.compile(r"pp?\s*(\d{1,3})\s*(?:[–\-]\s*(\d{1,3}))?")


# A line that opens like a claim row: "| <node-id> |". Anything matching this
# MUST parse as a full six-column row.
ROW_OPENER = re.compile(r"^\|\s*(?P<id>[A-Z]\d{1,2}|U\d+)\s*\|")


def parse(path):
    """
    Parse claim rows, and fail loudly on anything that opens like one but isn't.

    H6-H11: the original dropped any line that didn't match ROW cleanly, and any
    row whose column count wasn't six. A line-wrapped row fails BOTH -- its first
    fragment has no trailing pipe so ROW never matches, and its tail starts with
    a non-id cell so it is ignored. The node vanished from the graph with no
    diagnostic. U2 was absent for a week that way, along with its edges.

    The fix keys on ROW_OPENER instead: if a line starts "| <node-id> |" it is a
    claim row and must yield six columns, or it is a structural failure. Lines
    whose first cell is not a node id belong to other tables (the imports table
    is five columns by design) and are ignored as before.
    """
    rows, malformed = [], []
    for lineno, line in enumerate(open(path, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        opener = ROW_OPENER.match(line)
        m = ROW.match(line)

        if not opener:
            if not m:
                continue
            cells = [c.strip() for c in m.group("cells").split("|")]
            if not cells or cells[0] in ("id",) or set(cells[0]) <= set("-:"):
                continue
            if not NODE.match(cells[0]):
                continue  # another table's row; not ours to police

        nid = opener.group("id") if opener else "?"

        if not m:
            malformed.append((lineno, nid, "no trailing pipe -- line-wrapped row"))
            continue

        cells = [c.strip() for c in m.group("cells").split("|")]
        if len(cells) != 6:
            malformed.append((lineno, nid, f"{len(cells)} columns, expected 6"))
            continue

        rows.append(dict(zip(("id", "stmt", "deps", "bucket", "status", "notes"), cells)))
    return rows, malformed


def build(rows):
    ids = [r["id"] for r in rows]
    idset = set(ids)
    edges, dangling = {}, defaultdict(list)
    for r in rows:
        deps = []
        for t in TOKEN.findall(r["deps"]):
            if t in idset:
                deps.append(t)
            else:
                dangling[r["id"]].append(t)
        edges[r["id"]] = deps
    return ids, idset, edges, dict(dangling)


def find_cycles(ids, edges):
    WHITE, GREY = 0, 1
    color = {i: WHITE for i in ids}
    found = []

    def walk(u, stack):
        color[u] = GREY
        stack.append(u)
        for v in edges.get(u, []):
            if color[v] == GREY:
                found.append(stack[stack.index(v):] + [v])
            elif color[v] == WHITE:
                walk(v, stack)
        stack.pop()
        color[u] = 2

    for i in ids:
        if color[i] == WHITE:
            walk(i, [])
    return found


def ancestors(node, edges):
    seen, stack = set(), [node]
    while stack:
        for v in edges.get(stack.pop(), []):
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen


def counters(ids):
    """Dense-counter completeness. A shared numbering makes omission detectable."""
    out = {}
    main = sorted(int(i[1:]) for i in ids if re.match(r"^[DPTLC]\d+$", i))
    supp = sorted(int(i[1:]) for i in ids if re.match(r"^S\d+$", i))
    for name, seq in (("main", main), ("supplement", supp)):
        if not seq:
            continue
        out[name] = {
            "range": [seq[0], seq[-1]],
            "gaps": [n for n in range(seq[0], seq[-1] + 1) if n not in seq],
            "duplicates": [k for k, v in Counter(seq).items() if v > 1],
        }
    return out


def page_coverage(rows, total):
    """
    Which pages of the paper does some node claim to describe?

    Uncovered pages are where unmodeled content hides. This is the only
    mechanical handle on omission -- the failure that dense counters cannot
    catch, because an unnumbered load-bearing step has no counter.
    """
    covered = set()
    for r in rows:
        for a, b in PAGES.findall(r["stmt"] + " " + r["notes"]):
            lo = int(a)
            hi = int(b) if b else lo
            if 1 <= lo <= total and lo <= hi <= total:
                covered.update(range(lo, hi + 1))
    gaps, run = [], []
    for p in range(1, total + 1):
        if p in covered:
            if run:
                gaps.append((run[0], run[-1]))
                run = []
        else:
            run.append(p)
    if run:
        gaps.append((run[0], run[-1]))
    return sorted(covered), gaps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dag", nargs="?", default="dag.md")
    ap.add_argument("--pages", type=int, required=True, help="page count of the paper")
    ap.add_argument("--target", required=True, help="headline claim node, e.g. C26")
    ap.add_argument("--audited", help="node whose cone an external audit covers, e.g. C19")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    rows, malformed = parse(a.dag)
    ids, idset, edges, dangling = build(rows)
    bucket = {r["id"]: r["bucket"] for r in rows}
    bad = []

    dupes = [k for k, v in Counter(ids).items() if v > 1]
    cycles = find_cycles(ids, edges)
    ctr = counters(ids)
    covered, page_gaps = page_coverage(rows, a.pages)

    for ln, nid, why in malformed:
        bad.append(
            f"malformed claim row, line {ln} (id {nid}): {why} "
            f"-- this node is NOT in the graph (H6-H11)"
        )
    if dupes:
        bad.append(f"duplicate ids: {dupes}")
    if dangling:
        bad.append(f"dangling dependency refs: {dangling}")
    if cycles:
        bad.append(f"cycles: {cycles}")
    for name, c in ctr.items():
        if c["gaps"]:
            bad.append(f"{name} counter has gaps {c['gaps']} -- missing numbered results")
        if c["duplicates"]:
            bad.append(f"{name} counter duplicates {c['duplicates']}")
    if a.target not in idset:
        bad.append(f"target {a.target} not in DAG")

    cone = ancestors(a.target, edges) | {a.target} if a.target in idset else set()
    outside = sorted(set(ids) - cone)
    orphans = sorted(i for i in ids if not any(i in d for d in edges.values()) and i != a.target)

    gap_nodes = []
    if a.audited and a.audited in idset:
        aud = ancestors(a.audited, edges) | {a.audited}
        gap_nodes = sorted(cone - aud)

    misdirected = sorted(i for i in ids if bucket.get(i) == "MECH" and i not in cone)

    rec = {
        "dag": a.dag,
        "rows": len(rows),
        "malformed_rows": malformed,
        "buckets": dict(Counter(bucket.values())),
        "counters": ctr,
        "cycles": cycles,
        "dangling": dangling,
        "cone_target": a.target,
        "cone_size": len(cone),
        "outside_cone": outside,
        "orphans": orphans,
        "audit_gap": {"audited": a.audited, "nodes": gap_nodes},
        "mech_outside_cone": misdirected,
        "page_coverage": {"total": a.pages, "covered": len(covered), "gaps": page_gaps},
        "structural_pass": not bad,
        "failures": bad,
    }

    if a.json:
        print(json.dumps(rec, indent=2))
        return 0 if not bad else 1

    print(f"# DAG audit — {a.dag}\n")
    print(f"rows: {len(rows)}   malformed: {len(malformed)}   buckets: {dict(Counter(bucket.values()))}")
    for name, c in ctr.items():
        state = "dense, no gaps" if not c["gaps"] else f"GAPS {c['gaps']}"
        print(f"counter[{name}]: {c['range'][0]}..{c['range'][1]} — {state}")
    print(f"cycles: {len(cycles)}   dangling refs: {len(dangling)}   duplicate ids: {len(dupes)}")
    print()
    print(f"{a.target} cone: {len(cone)} of {len(rows)} nodes")
    print(f"  outside the cone ({len(outside)}): {' '.join(outside)}")
    print(f"  orphans (nothing depends on them): {' '.join(orphans)}")
    if gap_nodes:
        print(f"\naudit gap — in {a.target} cone but not under {a.audited} ({len(gap_nodes)}):")
        print("  " + "  ".join(f"{g}[{bucket[g]}]" for g in gap_nodes))
    if misdirected:
        print(f"\nMECH nodes outside the cone (verifying these proves nothing about "
              f"{a.target}): {' '.join(misdirected)}")
    print(f"\npage coverage: {len(covered)}/{a.pages} pages claimed by some node")
    if page_gaps:
        print("  UNCOVERED (omission risk — nothing in the DAG describes these):")
        for lo, hi in page_gaps:
            print(f"    pp {lo}–{hi}" if hi > lo else f"    p {lo}")
    print()
    if bad:
        print("STRUCTURAL FAIL")
        for b in bad:
            print("  - " + b)
        return 1
    print("STRUCTURAL PASS")
    print("NOT CHECKED: fidelity of any row to the paper. See VERIFY.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
