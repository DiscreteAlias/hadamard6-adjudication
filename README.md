# hadamard6-adjudication

A structural adjudication of **arXiv:2608.18053**, *"A Complete Classification of
Complex Hadamard Matrices of Order Six"* (Cárdenes Wuttig & Tindall, v1, 18 Aug
2026) — a fifty-page unrefereed preprint shipping a companion Lean 4 audit.

**This repository does not claim the paper is right or wrong.** It answers a
narrower question: *where does the machine-checked part stop?*

Run over five days, 25–29 August 2026.

---

## Verdict

**LOCALIZED.** The companion Lean artifact was verified and does what it claims.
The headline classification claim sits in a dependency cone of 37 nodes, of which
**14 lie outside the Lean-audited chain** — ten unmechanized arguments, one
literature import, two mechanical, one definitional.

The authors disclose this themselves, in six categories, in their repository's
`LEAN_ASSUMES_AND_PROVES.md`. What is added here is precision: those six
categories enumerated as fourteen named nodes, computed mechanically from a
dependency graph, updating automatically as the graph is corrected.

Additionally, **five load-bearing steps the paper's own numbering does not
expose** were identified — two unnumbered claims, one dependency written as a
prose equation range, one definition whose content sits on an uncited page, and
one cross-reference pointing at the wrong equation. These were sent to the
corresponding author on 29 August 2026, before publication.

Full verdict: [`slag/verdict.md`](slag/verdict.md).

---

## What was checked

- The Lean artifact (`f9ff024`, Mathlib v4.33.0-rc2) built from source: 3496
  jobs, exit 0; all nine public endpoints report only `propext`,
  `Classical.choice`, `Quot.sound`; no `sorry`, `admit`, project axiom,
  `opaque`, `unsafe`, or `native_decide`. Definitions read in full and confirmed
  faithful; vacuity closed by an explicit inhabitant.
- Every numbered result in the paper (26 main + 20 supplemental) mapped into a
  dependency graph, audited structurally, then audited again for fidelity
  against the paper by an independent session on a different model.
- A blind counterexample search, run without access to the paper, returning a
  certified negative.

## What was **not** checked

Stated up front, because a finding is only as good as its boundary.

- **No individual computational claim in the paper was verified.** The harness
  exists and is tested; it was never pointed at the paper.
- **Nine of ten literature imports are unchecked**, including both halves of the
  structural proposition every route passes through. The cited papers were never
  opened. This is the largest unverified thing here.
- The IMPORT node's fidelity to its cited construction — which decides the
  headline claim — was not checked.
- The companion certificate directory was never run.
- A blind re-extraction of the dependency graph was planned and not performed.

---

## Where to start

| file | what it is |
|---|---|
| [`slag/verdict.md`](slag/verdict.md) | the sealed verdict — read this first |
| [`dag.md`](dag.md) | the claim graph: 51 nodes, dependencies, buckets |
| [`checks/dag_audit.py`](checks/dag_audit.py) | the structural auditor (paper-agnostic) |
| [`VERIFY.md`](VERIFY.md) | the verification protocol (V0–V4) |
| [`verification/`](verification/) | audit outputs, the fidelity pass, and its corrections |
| [`slag/harness-defects.md`](slag/harness-defects.md) | eleven defects found in **our own** instrumentation |
| [`counterexample/REPORT.md`](counterexample/REPORT.md) | the blind search, certified negative |

Reproduce the two gates:

```bash
python3 checks/lib/hadamard.py
python3 checks/dag_audit.py dag.md --pages 50 --target C26 --audited C19
```

Both must exit 0. The auditor reads 51 rows, reports a 14-node audit gap, and
states plainly that it has checked no row's fidelity to the paper.

---

## The protocol, in brief

**Claim DAG.** One row per numbered result: dependencies, plus a bucket —
`MECH` (exact finite computation), `IMPORT` (asserted from elsewhere), `ARG`
(genuine argument), `DEF` (no proof obligation).

**Structural audit.** Cycles, dangling edges, bucket arithmetic — and two
sharper checks. *Dense-counter completeness*: a shared numbering counter makes
missing numbered results self-certifying. *Page coverage*: collect every row's
page citations and ask which pages nobody claims — the only mechanical handle on
**un**numbered load-bearing steps, which have no counter to be missing from.

**Dependency cone.** Compute the headline claim's ancestor set. Everything
outside is not load-bearing for it. Here that excluded a numbered Theorem nothing
depends on, and five of twelve mechanical nodes whose verification would have
proved nothing about the headline.

**Audit gap.** Set difference between the headline's cone and the formalized
theorem's cone. This is the reusable idea: *where the machine-checked part stops*
becomes a list of nodes rather than a paragraph.

**Adversarial fidelity.** Structural consistency is not fidelity — a confabulated
graph can be perfectly consistent. So: the verifier is never the extractor, it
runs on a different model, and it is framed *"find me a wrong row"* rather than
*"check these rows."*

**Lean boundary.** The kernel is silent on whether the theorem is the theorem.
Read the definitions before the theorem; check that the hypotheses can be
instantiated.

---

## On the defect log

[`slag/harness-defects.md`](slag/harness-defects.md) records eleven defects — all
in *this* instrumentation, not the paper's. Among them: a self-test that printed
`MISMATCH` and exited 0 regardless, leaving this repository's own bootstrap gate
inert for five days; a parser that silently discarded a line-wrapped row, so one
node was absent from the graph for a week; and a verification pass that
fabricated a page span and committed it, caught only because the fidelity pass
was independent.

It is public deliberately. Every one of these was caught the same way — **a check
contradicting a number someone had predicted out loud**, never by reading
carefully. That is the transferable finding, and it is worth more than any
individual defect.

---

## Reading the internal vocabulary

`slag/` is the kill log — findings kept regardless of outcome. **Track A** read
the paper; **Track B** never did, by construction, so that its counterexample
search would be an independent check rather than a correlated one. **V0–V4** are
the stages of [`VERIFY.md`](VERIFY.md). **`[D]`** marks a document drafted with
AI assistance.

---

*Julian Miller · [discretealias.dev](https://discretealias.dev)*
