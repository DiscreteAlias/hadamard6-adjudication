#!/usr/bin/env python3
"""Check for node <ID>: <statement>.  [D]

Bucket: MECH
Depends: <node ids>
"""
import sys
sys.path.insert(0, "lib")

from hadamard import is_hadamard, defect, haagerup, fourier, tao_S6  # noqa: E402


def ground_truth():
    """Refuse to run unless the harness reproduces known values."""
    assert defect(fourier(6)) == 4, "harness broken: F6 defect != 4"
    assert defect(tao_S6()) == 0, "harness broken: S6 defect != 0"


def check():
    """Return (verdict, evidence). Exact arithmetic only."""
    raise NotImplementedError


if __name__ == "__main__":
    ground_truth()
    try:
        ok, evidence = check()
    except NotImplementedError:
        sys.exit(2)
    print(evidence)
    sys.exit(0 if ok else 1)
