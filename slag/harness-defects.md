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

**Status:** FIXED in `checks/lib/hadamard.py` (commit a2e38a7). `defect()` now
runs a sound DomainMatrix path over an explicit algebraic field alongside the
heuristic; sound wins whenever it decides, disagreement prints loudly to stderr,
and field-construction failure degrades to the falsy UNDECIDED singleton rather
than to a number. Both paths' ranks are self-test anchors (F6 21, S6 25).

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

**Status:** FIXED in `checks/lib/hadamard.py` (commit a2e38a7). `is_hadamard()`
is now three-valued; UNDECIDED never collapses to False. B6(2pi/3) — the witness
— certifies TRUE and is a self-test anchor. `checks/README.md` records that an
UNDECIDED verdict is exit 2 (reclassify the node ARG), never exit 1 (refuted).

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

---

## H6-H8 — lib self-test never fails the process

**Found:** 2026-08-26, Track A, during the H6-H5/H6-H4 harness fix.

**What:** `checks/lib/hadamard.py`'s `if __name__ == "__main__":` block
decided pass/fail by building a string ("OK" / "MISMATCH (expected ...)")
and printing it. No `assert`, no `sys.exit`, no exception on a failed
comparison — the script always returned exit code 0, regardless of whether
any anchor actually held.

**Evidence:** read directly, not inferred: the block's only failure signal
was an f-string ternary assigned to a `flag` variable and printed; nothing
in the file called `sys.exit` or raised on a mismatch.

**Blast radius:** root `README.md`'s documented contract (`python3
checks/lib/hadamard.py` "exits nonzero if the harness is broken") and
`CLAUDE.md`'s "Run `python3 checks/lib/hadamard.py` before trusting any
check" were both false from the moment the file was created. Any gate —
bootstrap, pre-commit, or otherwise — that aborted on this script's exit
code before proceeding could never have fired; that gate has been
decorative since the repo was created. Second-order cause of H6-H1..H6-H3:
even had the original self-test carried identity anchors instead of only
distinctness anchors, a failing one would still have printed "MISMATCH" and
exited 0.

**caught_by:** this session, reading the block directly rather than
trusting the documented contract.
**should_have_been_caught_by:** a deliberate red test — break an anchor on
purpose, confirm the script's exit code actually goes nonzero.

**Status:** FIXED in `checks/lib/hadamard.py`, same commit as H6-H4/H6-H5 —
the self-test now accumulates failures and calls `sys.exit(1)` when any
anchor fails, `sys.exit(0)` otherwise. Verified directly before that commit:
deliberately broke the F6-defect anchor, confirmed the process exited 1
with the broken anchor named in the output, restored it, confirmed a clean
exit 0.

---

## H6-H9 — Track B wrote four files into `checks/lib/` outside its approved allowlist

**Found:** 2026-08-26, Track A, post-hoc audit during the H6-H5/H6-H4
harness fix.

**What:** `checks/lib/` contains four files attributable to Track B that sit
outside its approved shared path: `g6point.py`, `qivmini.py`,
`g6_state.json`, `g6_verification.json`. The approved shared path into
`checks/lib/` was `catalogue.py` only.

**Evidence:** neither `.py` file imports from or is imported by
`checks/lib/hadamard.py` — no coupling exists in either direction, checked
directly by grepping both files' import statements and every caller of
`is_hadamard`/`defect` repo-wide.

**Blast radius:** namespace pollution in the shared `checks/lib/` directory,
plus a duplicate exact-interval-arithmetic implementation (`qivmini.py`)
alongside `counterexample/lib/qiv.py`, with no stated authority for which is
canonical. Classification: an instrumentation-scope breach, not a blindness
violation — these are writes, not reads, so Track B's decorrelation claim
(never reading `paper/`, `dag.md`, or root `README.md`) is unaffected.

**caught_by:** post-hoc git audit.
**should_have_been_caught_by:** a pre-commit path check that does not exist.

**Status:** OPEN. Disposition pending triage. Do not move, delete, or
import these four files — a background G6 defect elimination may still
hold `g6_state.json` open. Logged only; not acted on by the H6-H4/H6-H5 fix.

---

## H6-H10 — `_real_field_for`'s escalation guard is nondeterministic by construction

**Found:** 2026-08-26, during implementation of the H6-H4/H6-H5 fix.

**What:** The ported field-construction helper originally escalated on a
degree-budget estimate computed before calling `sp.QQ.algebraic_field`. That was
the planned fix and it was wrong in both directions: measured directly, the
estimate is unreliable — B6(2pi/3)'s twelve generators produce a naive
product-of-degrees estimate of 65536 while the actual field has degree 4 and
builds in under a second. Estimate-based rejection would have escalated the
exact witness the commit exists to certify. The guard is therefore a **20-second
wall-clock timeout around the actual construction**, confirmed against both
B6(2pi/3) (0.5s, succeeds) and an adversarial case of 20 independent quadratic
surds (correctly escalates at the 20s mark instead of hanging).

**Not a defect — a recorded tradeoff.** This is logged because it changes the
character of the guarantee, and the change is easy to miss. A degree budget is
deterministic: same input, same verdict, forever. A wall-clock timeout is not.
The same matrix can certify TRUE on an idle machine and escalate to UNDECIDED
under load, on slower hardware, or after a sympy upgrade.

**Blast radius.** The failure direction is safe — nothing unsound gets through,
since the degraded verdict is UNDECIDED rather than TRUE or FALSE. But
"exact arithmetic, reproducible verdicts" now carries an asterisk, and Track B's
discipline was built on not having asterisks. **An UNDECIDED originating in this
path means "too slow here, now" — not "not decidable."** Anyone reading a future
UNDECIDED without that context will misread it as a mathematical fact about the
matrix. `checks/README.md` should carry the same distinction alongside its exit-2
contract: a MECH node reclassified ARG on a timeout is not the same thing as one
reclassified on genuine undecidability.

**caught_by:** the implementing session, by measuring the estimate against a real
case rather than reasoning about it.
**should_have_been_caught_by:** nothing — the planned design was wrong and only
execution revealed it. This is the fourth defect this week found by running
something rather than reading it.

**Status:** ACCEPTED as designed. Revisit if a deterministic bound on field
degree becomes available.

---

## H6-H11 — `dag_audit.py` silently discarded any line it could not parse

**Found:** 2026-08-26, by manual `sed` inspection while inserting U3.

**What:** The auditor dropped any line that did not match its `ROW` regex, and
any parsed row whose column count was not six. A line-wrapped table row fails
**both**: its first fragment has no trailing pipe so `ROW` never matches, and its
tail begins with a non-id cell so it is ignored as another table's row. The node
vanished from the graph with no diagnostic of any kind.

**Blast radius.** U2 was absent from the DAG for the entire week, together with
its edges to P7(1) and C19. Every cone computation and bucket count produced
before the repair ran on 47 rows, not 48 — including the committed
`verification/v0-structural.txt` of 2026-08-25 and the eleven-node audit gap that
was, at the time, the deliverable. The gap list happened to be unaffected (U2 is
downstream-only), but that was luck, not design.

**caught_by:** manual inspection, incidentally, while doing something else.
**should_have_been_caught_by:** an assertion in the auditor.

**Status:** FIXED in `checks/dag_audit.py`. The parser now keys on a **row
opener** — any line beginning `| <node-id> |` is a claim row and must yield
exactly six columns, or it is a structural failure with the line number and node
id named. Rows whose first cell is not a node id (the five-column imports table)
are ignored as before. Verified by red test: wrapping U2 across two lines yields
`STRUCTURAL FAIL`, `malformed: 1`, exit 1, naming U2 at line 75; a stray pipe
inside a cell is caught as 7 columns; the well-formed file reports `malformed: 0`
and exit 0.

**Note on the fix.** The first attempt added a column-count check and the red
test still passed — a wrapped row never reaches a column count. The defect was
not a wrong check but a **missing** one. Every silent `continue` in a parser is
an unstated assumption that the skipped line does not matter; `dag_audit.py` had
three, and one was load-bearing. This is the general lesson, larger than the
specific bug.
