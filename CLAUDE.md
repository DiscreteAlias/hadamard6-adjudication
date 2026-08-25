# Track A — adjudication

Adjudicating arXiv:2608.18053 (6×6 complex Hadamard classification).
Read `README.md` first.

## Do

- Build `dag.md` before verifying anything.
- Classify every node MECH / IMPORT / ARG.
- Exact arithmetic only. sympy, symbolic roots of unity, exact ranks.
- Run `python3 checks/lib/hadamard.py` before trusting any check.
- One script per node in `checks/`, exit code as verdict.

## Do not

- Do not assess whether the proof is "convincing." Localize what it rests on.
- Do not use floating point. If a step seems to need it, it is ARG.
- Do not add gates, phases, or kill conditions. This is one claim, one week.
- Do not touch `counterexample/`. That track must stay blind.
