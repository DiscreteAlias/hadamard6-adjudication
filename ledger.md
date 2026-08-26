# Ledger `[D]`

Schema carried over from the research brief. One row per claim.

---

**claim:** Up to standard equivalence, every 6×6 complex Hadamard class outside
Karlsson's three-parameter family and Tao's isolated matrix is recovered
algebraically from a suitable corner; the classification is complete.

- **status:** CLAIMED
- **primary:** arXiv:2608.18053, Aug 2026. No venue, no DOI.
- **certificate:** none possible — quantified over everything. Falsifiable by a
  single inequivalent exact matrix; not verifiable by any finite object.
- **load:** 0 at intake.
- **last_touched:** Aug 2026.
- **decision:** D1 — tooling for MUB-6 if it holds. The Hadamard→MUB reduction
  is FOLKLORE, not proven sufficient, so this does not close MUB-6 either way.

---

**Status taxonomy:** PROVEN / CLAIMED / NUMERICAL *(dead reckoning)* / FOLKLORE / REFUTED

---

**Note — harness dependency (not a claim about the paper):** every MECH
verdict here that calls `is_hadamard`/`defect` from `checks/lib/hadamard.py`
relies on the H6-H4/H6-H5 sound-path fix landed in commit `a2e38a7` (see
`slag/harness-defects.md`). Verdicts computed before that commit against the
unfixed heuristic-only path are covered by the H6-H5 addendum's
contamination audit, not restated here.
