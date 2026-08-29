# Verdict — arXiv:2608.18053 `[D]`

**Sealed 2026-08-29.** Kept regardless of outcome, per the day-one commitment in
`README.md`.

Subject: *A Complete Classification of Complex Hadamard Matrices of Order Six*,
Cárdenes Wuttig & Tindall, arXiv:2608.18053v1, 18 Aug 2026, 50 pp. Unrefereed,
no venue, no DOI, LLM-assisted per its own disclosure on p13. At intake it was
seven days old.

---

## Verdict

**LOCALIZED.** Not refuted, not confirmed. The deliverable is a structural map of
the paper with a verified boundary around its machine-checked core, plus five
dependencies the paper's own numbering does not expose.

Correctness of the classification was never in scope and is not claimed either
way. The pre-commitment written into `README.md` before any work began — that
the DAG plus a localization *is* the full deliverable — was honoured without
renegotiation.

---

## The finding

The paper ships a companion Lean 4 audit. That audit covers the classification
chain ending at C19. The headline claim C26 — Szöllősi's conjecture, that
𝒦₆⁽³⁾ ∪ 𝒯₆ ∪ G₆⁽⁴⁾ exhausts ℋ₆ — sits in a dependency cone of 37 nodes, of which
**14 are outside the Lean-audited chain**:

| bucket | count | nodes |
|---|---|---|
| ARG (unmechanized argument) | 10 | C26, P24, P25, S15, S16, S18, S19, T22, U4, U5 |
| IMPORT | 1 | D23 |
| MECH | 2 | S7, S17 |
| DEF | 1 | D20 |

The authors disclose this in categories. `LEAN_ASSUMES_AND_PROVES.md` lists six
things Lean does not prove — the Construction 3.1 comparison, the generic
quadratic–cubic reconstruction geometry, nonsplitting of the product cover, the
physical seed-domain theorem, global product-regular reach, the ramification
seed. **This is that list enumerated at node granularity.** It is a sharper
version of the authors' own disclosure, not a discovery they concealed.

### Five dependencies the numbering does not expose

Independently checkable in minutes by anyone with the PDF:

- **U4** (p43, unnumbered) — the directional-badness characterization: at a
  finite corner a product-regular frame exists *exactly when* the horizontal
  side is row-good and the vertical side is column-good. Four-sentence
  justification of an iff. **Lemma S.18's statement is phrased entirely in these
  terms and has no meaning without it.** S18 is in the gap.
- **U5** (p42, unnumbered) — equivalence-invariance of product-regularity, which
  licenses the class-level definition 𝒫₆ at (S.2.68). One sentence. S16, S17 and
  T22 all quantify over 𝒫₆.
- **S7 via D20** — D20 named "Sec II B machinery (S.2.16–S.2.24)" as prose. S7's
  entire statement *is* S.2.23–S.2.24. A dependency expressed as an equation
  range is invisible to any cone computation.
- **D23 / p41** — the definitional passage for G₆⁽⁴⁾ distinguishing it from the
  paper's own completed output lives on p41; D23 cited only p12 and p48. D23 is
  the IMPORT node whose fidelity to Construction 3.1 decides the headline.
- **D20 / p42** — the canonical eleven-guard form is (S.2.67) on p42; the row
  cited (S.2.26) on p35.

Underlying pattern: **the extractor recorded where results were *stated*, not
where their content *lived*.** Page-coverage analysis caught only the instances
that left a whole page unclaimed.

### The Lean artifact does what it claims

Verified directly, not taken from p31. Repo `f9ff024`, Mathlib v4.33.0-rc2,
`lake build Hadamard6.PaperTheorem` — 3496 jobs, exit 0. All nine public
endpoints report exactly `[propext, Classical.choice, Quot.sound]`. Source
carries no `sorry`, `admit`, project `axiom`/`constant`, `opaque`, `unsafe`, or
`native_decide`.

Definitions read in full and faithful: `IsHadamard` is `EntrywiseUnit ∧ H H† =
6•1`; `InFiniteCornerAtlas` is genuine existential corner structure with no
smuggled Hadamardness, so `paper_total_output_corollary` is substantive in both
directions. Non-vacuous — `taoMatrix` is written out entry by entry and
`taoMatrix_isHadamard` proves it satisfies the definition.

**One naming caveat.** `IsKarlssonConcrete H := IsHadamard H ∧
HasHadamardTwoByTwo H` — Hadamard with a 2×2 Hadamard submatrix. Nothing about
Karlsson's three-parameter family. The identification lives in prose in
`PUBLIC_THEOREM_AUDIT.md` and is not formalized. That identification is P7(1).

### The second hypothesis differs from P7(1) as printed

Verbatim from the build:

```
KarlssonRawOrSeamCoverage : ∀ (H : Mat6),
  IsHadamard H → HasHadamardTwoByTwo H →
    Nonempty (CanonicalKarlssonRawPresentation H) ∨ IsAffineFourierSeam H
```

P7(1) on p4 is an **iff** concluding in family membership. The Lean hypothesis is
forward-only and concludes in a two-case concrete presentation. p31 asserts these
"are precisely the two published inputs of Proposition 7"; that is the paper's
claim, not reader-verifiable. The repo's own docs state the difference more
carefully than the paper does.

Consequence: residual trust is **three** checks, not two — P7(2) citation
fidelity, the raw-or-seam form's fidelity to Karlsson [26,27], and Lean statement
fidelity to C19. The third is now discharged. The first two are not.

---

## Scope — what was NOT done

Stated plainly because the finding is only as good as its boundary.

- **No MECH node was verified.** `checks/` contains only `check_template.py`. The
  harness was built and fixed; it was never pointed at the paper.
- **Nine of ten imports remain unchecked**, including both halves of P7. Karlsson
  [26,27] and Szöllősi [24] were never opened. **P7(1) is the single largest
  unverified thing in this adjudication** — every route to the classification
  passes through it.
- **D23's fidelity to Construction 3.1 was not checked**, though it decides the
  headline claim.
- **The certificate directory was not run.** `certificates/verify.py` with its
  SHA-256 manifest covers P17, T22, S16, S17 and was never executed.
- **V2 (blind re-extraction) was not run.** V1 found no edge errors among the
  original eleven gap nodes, so the second opinion was judged not worth a full
  re-read. That is a judgment, not a verification.

---

## Counterexample search (Track B)

Blind throughout — never read `paper/`, `dag.md`, or the root `README.md`.
Verified post-hoc by git audit; the only allowlist breach was four files written
into `checks/lib/` (H6-H9), which are writes, not reads, leaving decorrelation
intact.

**Exit 0, certified negative.** Butson BH(6,q) exhaustive for q ≤ 6: BH(6,3) = S6,
BH(6,4) = D6, BH(6,6) = four classes. The two-triangle stratum exhausted — 1,488
consistent leaves, 1,536/1,536 solutions certified equivalent to S6 with decider
certificates re-verified by exact multiplication. Defect census uniform at {0,4}.
Zero open candidates.

Side result: *up to equivalence, S6 is the only 6×6 CHM whose dephased noninitial
rows are all two-triangle rows.*

---

## Bucket counts

| | intake (day one) | sealed |
|---|---|---|
| rows | 48 | 51 |
| claim nodes | 40 | 43 |
| MECH | 11 | 12 |
| IMPORT | 2 | 2 |
| ARG | 27 (≈68 %) | 29 (≈67 %) |
| C26 cone | 34 | 37 |
| **audit gap** | **11** | **14** |

V1 moved the gap from 11 to 14. Three of the four additions were dependencies no
structural check could have found.

---

## Harness defects

Eleven, all in our own instrumentation. Full entries in
`slag/harness-defects.md`.

- **H6-H1/H6-H2/H6-H3** — `haagerup()` compares spellings not numbers; blind to
  transpose/conjugation; `defect()` docstring overclaims the converse. OPEN in
  the shared lib with warning docstrings; sound versions live in Track B.
- **H6-H4/H6-H5** — heuristic zero-testing in `defect()` and `is_hadamard()`.
  **FIXED** (`a2e38a7`): dual-path with a falsy UNDECIDED singleton; UNDECIDED
  never collapses to False. B6(2π/3), a true Hadamard the old predicate rejected,
  now certifies TRUE and is a self-test anchor.
- **H6-H6/H6-H7** — M6 transcription sign; G6 certification ideal. FIXED, caught
  by designed verification gates.
- **H6-H8** — the lib self-test never failed the process. It printed "MISMATCH"
  and exited 0 regardless, meaning the bootstrap's harness gate was decorative
  from day one. FIXED, red-tested.
- **H6-H9** — Track B allowlist breach. OPEN, logged not acted on.
- **H6-H10** — the field-construction guard is a wall-clock timeout, hence
  nondeterministic. Safe direction; recorded as a tradeoff, not a defect.
- **H6-H11** — `dag_audit.py` silently discarded unparseable rows. **U2 was
  absent from the graph for a week**, with its edges. Every count before the
  repair ran on 47 rows. FIXED, red-tested.

---

## The verification record's own failures

Kept because an adjudication that documents catching its own errors is worth more
than one reporting a clean run.

- **A fabricated page span was committed.** V3 recorded S.6's proof as spanning
  pp33–34 on the basis of a manual read, without checking the page boundary. p34
  is Section II B's opening. V1 caught it; the correction is appended to
  `verification/v0-structural.txt` rather than replacing the original.
- **A template was committed and pushed with placeholders unfilled**, under a
  message asserting a finding. Reverted; both commits remain in history.
- **Three commits to land one edge** (D20 → S7), each asserting a gap change that
  had not occurred.
- **U2 unparsed for a week** (H6-H11).

Every one of these was caught the same way: **a check contradicting a number
someone had predicted out loud.** Not by careful reading. That is the transferable
finding, and it is larger than any individual defect.

---

## Effect on the MUB-6 decision (D1)

**None, directly.** The Hadamard → MUB reduction is FOLKLORE — motivational in
the literature, not a proven sufficiency. Szöllősi (2010) writes that
classification "might finally lead to the solution of the famous MUB-6 problem";
McNulty–Weigert note the MOLS/Hadamard–MUB analogy "fades a little if one looks
carefully into the details." A complete 6×6 classification is tooling for MUB-6,
not a closure of it.

Indirectly, substantial: the exact-arithmetic harness built during this
engagement — sound `is_hadamard`, exact DomainMatrix rank, canonical algebraic
labels, interval arithmetic, an equivalence decider emitting certificates, and a
catalogue of 6×6 complex Hadamards pinned to pre-2013 primary sources — operates
on precisely the objects MUB-6 requires. That harness was validated against known
answers by Track B's validation tier, not by this adjudication.

---

## Repository state at seal

`dag.md` 51 nodes · `verification/` V0, V1, V3 and the Lean build log ·
`slag/harness-defects.md` H6-H1..H6-H11 · `counterexample/` Track B complete ·
`checks/` harness fixed and red-tested, no node scripts written.

Reproduce:

```bash
python3 checks/lib/hadamard.py
python3 checks/dag_audit.py dag.md --pages 50 --target C26 --audited C19
```

---
## Disclosure and response

**Sent 2026-08-29, 04:49 UTC.** The five findings in "Five dependencies the
numbering does not expose", the p31 wording note, and a smaller section-range
slip were sent to the corresponding author ahead of any public write-up. No
claims about correctness were made.

**Response 2026-08-29, 13:23 UTC**, from Cárdenes Wuttig, with Tindall copied.
All findings accepted; none was a misreading. The outcome splits, and the split
matters:

**Already addressed before the note was sent — not attributable to this work.**
The reply states that revisions to the paper and repository were already made
and would appear the following Monday, and attaches a revised manuscript dated
**28 August** — the day *before* the note. In that revision: the unnumbered
Karlsson-intersection claim (U3) is removed; Definition 20 gives the full guard
list directly; Definition 23 explicitly defines G₆⁽⁴⁾ and distinguishes it from
the authors' own completed output; and the Section I A omission is gone with a
reorganisation. Three of the five findings, plus the section-range slip,
converged independently.

**Changed as a result of the note.** Two findings remained open in the revision,
and the authors state they will promote both to numbered statements:

- **U4** — the p43 admissibility/directional-badness characterisation. The reply
  notes the discussion is now supported by a numbered lemma, but that the
  definition and its equivalence with the existence of a product-regular frame
  remain unnumbered.
- **U5** — the p42 invariance of product-regular-frame existence under standard
  equivalence, still stated only in prose.

**Editorial note accepted.** On the p31 Lean scope wording, the reply agrees the
remaining wording should refer to the concrete structural reductions derived
within Lean, rather than saying that Lean proves the two published results
themselves.

**Scope of this verdict is unchanged.** Everything sealed above is computed
against **v1** (arXiv stamp 18 Aug 2026). A revised manuscript exists
(`hadamard_classification_Aug_28.pdf`, received 29 Aug) and a revised repository
was announced. Node numbering, the dependency cone, and the fourteen-node audit
gap all refer to v1 and are **not** amended here. A revision is a new
adjudication, not a patch to a closed one.
