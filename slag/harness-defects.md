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
