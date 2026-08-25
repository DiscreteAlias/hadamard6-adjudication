# Track B — blind counterexample search

You are searching for a 6×6 complex Hadamard matrix that is inequivalent to
everything in the known catalogue.

## Hard constraint

**Do not read `../paper/`, `../dag.md`, or `../README.md`.** You are deliberately
ignorant of the argument you are trying to break. If you find yourself reasoning
about what a paper claims, you have left your task.

## Method

- Exact arithmetic only (`../checks/lib/hadamard.py`).
- Verify `is_hadamard` before anything else about a candidate.
- Discriminate with `haagerup()`. Different set ⟹ inequivalent.
- Log every candidate in `README.md`, including misses and where they stalled.
