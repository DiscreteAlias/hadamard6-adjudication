# Harness defects — hadamard6-adjudication `[D]`

Append-only. Defects in *our* instrumentation, not in the paper under
adjudication. Those go in `ledger.md`.

**Namespace:** `H6-H<n>`. Deliberately not bare `H<n>` — the Cupel slag ledger
already carries H1–H10 from dgg-2026-001, a different harness. Collision on
aggregation would be silent and unrecoverable.

**Schema** (carried from the Cupel slag entries): what / evidence / blast radius
/ `caught_by` / `should_have_been_caught_by` / status.

---

## H6-H1 — `haagerup()` set equality compares spellings, not numbers

**Found:** 2026-08-25, Track B planning.

**What:** `haagerup()` returns a Python `set` of sympy expressions. Equality
between two matrices' sets is therefore syntactic. The same algebraic number
reached by different routes (`exp(2*pi*I/3)` vs `(-1+I*sqrt(3))/2`;
`sqrt(sqrt(3)/2)` vs `3**(1/4)/sqrt(2)`) compares unequal.

**Evidence:** `haagerup(C6)` returns 16 values with mixed radical spellings
(16.4s, lib path). `nsimplify` wraps rather than normalizes.

**Blast radius:** `inequivalent()` is unsound in the direction that matters —
it can report two equivalent matrices as inequivalent, i.e. **manufacture a
false NOVEL**. This was specified in `counterexample/README.md` as the
discriminator for the whole track and described in conversation as "the only
tool here that can actually kill the paper." Any prior reasoning resting on raw
set comparison across matrices is void.

**caught_by:** Track B planning, by direct measurement before use.
**should_have_been_caught_by:** the lib self-test. It only ever checked that
`haagerup` *distinguishes* F6 from S6 — two matrices whose spellings happen to
differ anyway. It never checked that it *matches* two spellings of the same
matrix. The missing anchor is an **identity** test (monomial-scramble a matrix,
confirm the invariant is unchanged), not a distinctness test.

**Status:** OPEN in `checks/lib/hadamard.py`. Fix belongs in Track B's
`invariants.py` as canonical labels — content/sign-normalized minimal polynomial
plus isolating box, validated at 0.4s on the 16 C6 values. **Do not change
shared-lib behavior while a track is running against it**; the docstring is
patched to warn, the function is left alone.

---

## H6-H2 — Haagerup is blind to transpose and conjugation

**Found:** 2026-08-25, Track B planning.

**What:** The Haagerup set is invariant under H → Hᵀ and H → conj(H) by index
bijection on its defining quadruple. It cannot separate F6 from F6ᵀ.

**Blast radius:** any four-variant equivalence check resting on the raw set is
inert. Separation must come from fingerprint multiplicities, defect, and the
equivalence decider.

**caught_by:** Track B planning, from the definition.
**should_have_been_caught_by:** the docstring, which states the converse
correctly ("equal sets do NOT imply equivalence") but omits the specific
symmetries that make equality *guaranteed* — the operationally relevant fact.

**Status:** OPEN. Docstring patched; no behavior change.

---

## H6-H3 — `defect()` docstring overclaims the converse

**Found:** 2026-08-25, Track B planning.

**What:** `defect(H) == 0 ⟹ H isolated` is a theorem. The converse is not.
"Generic 6x6 families sit at d = 4" reads as though defect 4 certifies a
continuum through the point. It does not.

**Blast radius:** cosmetic in code, real in report language. Any sentence of the
form "defect 4, therefore a family passes through here" is unsupported.

**caught_by:** Track B planning.
**should_have_been_caught_by:** review at authoring time.

**Status:** OPEN. Docstring patched; no behavior change.

---

## Pattern

All three are in the same file, all three were introduced by the same author in
one sitting, and all three survived a self-test that checked only that two known
matrices came out different. **A self-test built from distinctness anchors
cannot catch a soundness bug in an equality predicate.** Add identity anchors —
scramble round-trips — before trusting any invariant.

---

## H6-H4 — `defect()` rank rests on sympy's heuristic zero testing

**Found:** 2026-08-25, Track B day 1 (logged on user instruction).

**What:** `defect()` builds its 30×36 system with `sp.simplify(sp.re/im(...))`
entries and calls symbolic `Matrix.rank()`. Pivot-zero decisions inside that
rank are heuristic: an unrecognized zero pivot inflates rank and **deflates
defect**. On radical-field points (Björck C6, B6(θ), K6^(3) samples) an
unsimplified true zero is plausible.

**Evidence:** No disagreement observed yet — lib and sound path agree on all
anchors (F6 rank 21 / defect 4, S6 rank 25 / defect 0, C6 rank 21 / defect 4).
The defect is architectural: correctness depends on `simplify` succeeding,
which is not a contract. The sound path — DomainMatrix rank over an explicit
`QQ.algebraic_field` on (re, im) coordinates — reproduces all anchors in
0.1–4.6s (sympy 1.14.0) and is decided by exact field arithmetic.

**Blast radius:** a deflated defect can turn "generic family point, defect 4"
into "defect < 4" (phantom rigidity signal), or mask a genuinely anomalous
defect. Any defect-based claim produced solely by the lib path on non-cyclotomic
entries is unattested.

**caught_by:** Track B day-1 implementation, by construction of the parallel
sound path (`counterexample/lib/numfield.py::fast_defect`).
**should_have_been_caught_by:** the lib self-test — its anchors (F6, S6) live
in Q(ζ6), where `simplify` is reliable; no anchor exercises a radical field.

**Status:** OPEN in `checks/lib/hadamard.py`; no shared-lib behavior change
while tracks are running. **Protocol (user-set):** both paths run on catalogue
anchors and must agree there; on any disagreement elsewhere, **DomainMatrix
wins and the event is loud** (logged as a problem, never silently resolved) —
the lib is never used as a tiebreak against the field-arithmetic path.

---

## H6-H5 — `is_hadamard()` treats unproven-zero as nonzero (false dismissal)

**Found:** 2026-08-25, Track B day 2, catalogue verification.

**What:** `is_hadamard()` decides each Gram residual by structural comparison
after `sp.simplify(sp.expand_complex(...))`. A true zero that `simplify` fails
to normalize reads as nonzero, so a genuine Hadamard matrix is reported as
**not Hadamard**. The predicate is effectively two-valued with UNDECIDED
collapsed onto False — the unsound direction for a search whose candidates
die at this gate.

**Evidence:** B6(2π/3) (Beauchamp–Nicoara point, y = ζ3; the sqrt argument
1+2y+2y³+y⁴ is complex there). Lib verdict: False. Two independent sound
methods disagree with it: (i) field-coordinate check — exact (re,im) pairs
over `QQ.algebraic_field`, Gram sums identically zero, defect 4; (ii)
minimal-polynomial zero certification of individual Gram sums (ZERO on all
sampled row pairs, 24s). The matrix is Hadamard.

**Blast radius:** any candidate whose entries stress `simplify` (nested
radicals over complex arguments, RootOf towers) can be silently destroyed at
gate 1 and logged "not Hadamard". This is the false-dismissal path flagged in
Track B's plan review (risk: "the single most likely way a real discovery gets
destroyed").

**caught_by:** catalogue build — every family point runs both the lib path and
the field path, and the disagreement was loud by protocol (H6-H4).
**should_have_been_caught_by:** lib self-test — no anchor leaves Q(ζ6).

**Status:** OPEN in `checks/lib/hadamard.py`; no shared-lib change while
tracks run. Track B protocol: `is_hadamard` disagreements escalate to
per-residual minimal-polynomial certification; the field/minpoly verdict wins;
every occurrence is logged. Track A should treat lib `is_hadamard == False` on
radical-entry matrices as UNDECIDED, not as a refutation.

---

## H6-H5 addendum — contamination audit (requested at sign-off)

**When found:** day 2, during catalogue verification — after the lib self-test
(day 1 start), all planning probes (day 1), and the complete stratum-A run
(day 1) had already executed.

**Everything that ran under the defective behavior, checked item by item:**
- Planning probes (C6, Diţă block form): lib `is_hadamard` returned True on
  both; later cross-confirmed by the field path. Not contaminated.
- Lib self-test (F6, S6): entries in Q(ζ6), the domain where `simplify` is
  reliable; verdicts True, cross-confirmed. Not contaminated.
- Stratum A gauntlet (all BH(6,q≤6) class reps): every rep ran BOTH
  `is_hadamard_K` (field path, primary) and lib `is_hadamard` (cross-check);
  both returned True on all six class representatives — agreement recorded in
  the run log. Not contaminated.
- The defect's failure direction is false DISMISSAL (True→False). No candidate
  anywhere in the run was dismissed by a lib `is_hadamard` False: the only
  False verdicts it ever produced were B6(2π/3) (the finding itself, refuted
  by two independent sound methods) and deliberately corrupted test matrices.
**Conclusion: no accepted result predates the finding under the defective
predicate alone; every pre-finding use was independently confirmed.**

---

## H6-H6 — M6(x) transcription slip (sign of the b,c pair), caught by verify

**Found:** 2026-08-25, day 2, first catalogue verification of M6.

**What:** the first transcription of [MS math/0702043v1] eq. (buj)/(cuj)
encoded b, c with main term +(1+x²)/4; the paper has −(1+x²)/4. A
parametrization-data error in `checks/lib/catalogue.py` (M6 only).

**Evidence:** M6(1) and M6(ζ12) failed `is_hadamard_field` (rows 0,2 not
orthogonal) on first build. After the sign fix, the corrected formula
reproduces the paper's own printed anchor M6(1) (entries b=ω², c=ω) and the
decider certifies M6(1) ~ F6 — the paper's stated observation — plus all 16
M6 grid points verify Hadamard with defect 4.

**Blast radius / contamination:** none. The mis-signed matrices failed the
Hadamard gate immediately, were never written to the reference DB, never
appeared in a ledger row, and no downstream computation consumed them. The
fix direction was toward the paper, validated against in-paper anchors
(printed M6(1) matrix; M6(1) ≅ F6), not against the verifier alone.

**caught_by:** catalogue build verification (every family point must pass
`is_hadamard` at build).
**should_have_been_caught_by:** transcription review; the build gate exists
precisely for this.

**Status:** FIXED in `checks/lib/catalogue.py` before any artifact was
produced from the family.

---

## H6-H7 — G6 certification: wrong derived relation, then too-coarse ideal

**Found:** 2026-08-25/26, day 2–3, G6^(4) generic-point verification.

**What (two stages, both in Track B instrumentation, neither in the paper's
printed data — all 16 printed data items byte-match the source, verified by
exact polynomial comparison):**
1. My DERIVED relation for the (t1,t2) pair (t1·t2 = σ/σ̄, cleared of
   denominators — the paper prints no formula here; it says the values
   "follow from the Decomposition formula") dropped an A-power when clearing
   conj(σ) because deg(sigN) = 6 ≠ deg(sigD) = 5. Signature that exposed it:
   the certified roots of the mis-cleared quadratic were NOT unimodular
   (|t1|² ≈ 1.29, 0.78) although |σ|² ≈ 0.0677 ≤ 4 guarantees a unimodular
   pair. Fixed by explicit degree bookkeeping.
2. The relation ideal {pa, cubic, s1-quadratic, t1-quadratic, t3-quadratic}
   cuts out all four (t1,t3) PAIRING components; the true matrix identities
   hold only on the correct one, so NF certification failed on a true
   Hadamard (entry (4,3)). Fixed by adding the pairing coupler — the paper's
   own step-#7 requirement, column-2 ⊥ column-3, which is linear in t1 — and
   eliminating t1 by a monic (norm-inverse) substitution. Certificates: the
   coupler's T1-root satisfies the t1-quadratic identically mod (R1, R5m)
   (resultant NF-zero), and the certified boxes separate the correct pairing
   (residual → 0 at 10⁻²⁴; wrong pairings ≈ 1.95).

**Blast radius / contamination:** none. Stage-1's wrong roots existed only
inside failed verification runs; the persisted construction state was built
AFTER the stage-1 fix. Stage-2 changed only the certification ideal, not the
matrix. No DB entry, ledger row, or search result consumed any G6 quantity
before the full Hadamard verification passed (36 unimodularity + 15 Gram
certificates green).

**caught_by:** the verification gate itself — it was designed to be able to
fail, it failed, and the failures were diagnosed to instrumentation with the
paper data proven untouched.
**should_have_been_caught_by:** stage 1: a unit test on conj-clearing of
unequal-degree fractions; stage 2: recognizing from the start that quadratic
relations for paired roots encode all pairings.

**Status:** FIXED in `checks/lib/g6point.py`; transcription audit (code vs
.tex, 16/16 exact matches) recorded in the final report.
