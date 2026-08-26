"""Artifact serialization. Track B.

Matrices round-trip through sympy srepr strings. Artifacts are append-only
JSONL files under artifacts/; the README ledger is regenerated from them.
"""

import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
CANDIDATES = ARTIFACTS / "candidates.jsonl"
RUNS = ARTIFACTS / "runs.jsonl"


def matrix_srepr(H):
    return sp.srepr(sp.Matrix(H))


def matrix_from_srepr(s):
    return sp.sympify(s)


def jsonl_append(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(obj, sort_keys=True) + "\n")


def jsonl_load(path):
    if not Path(path).exists():
        return []
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out
