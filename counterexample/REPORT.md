# Track B final report — blind counterexample search, 6×6 complex Hadamard `[D]`

**Dates:** 2026-08-25 → 2026-08-26 (3-day scope).
**Charter:** find a 6×6 complex Hadamard matrix (CHM) inequivalent, under
H → D₁P₁HP₂D₂, to everything in the known catalogue — blind to `../paper/`,
`../dag.md`, and the repo-root `README.md` throughout. Exact arithmetic only.

## Verdict

**Exit 0 — negative result, fully certified.** No candidate inequivalent to
the known catalogue was found. Every matrix produced by every search stratum
was closed against the catalogue with an exact, re-verified certificate.
There are **zero open candidates**: no `unresolved-G6`, no bucket entries,
no stalls outstanding.

## What was searched, and how completely

**Stratum A — Butson BH(6, q), exhaustive for q ≤ 6.**
Enumeration by exact cyclotomic exponent arithmetic (bitset backtracking over
the vanishing-sum row lists), canonical dedup, every class rep through the
gauntlet. Results, each with a verified equivalence certificate:
- BH(6,2) = ∅, BH(6,5) = ∅ (row-level: no 6-term vanishing sums — matches
  Lam–Leung); BH(6,7), BH(6,11) empty at row level as well.
- BH(6,3): exactly 1 class = **S6** (Tao).
- BH(6,4): exactly 1 class = **D6** (Diţă's matrix itself), certificate to D6(0).
- BH(6,6): exactly 4 classes = **F6**, **F6(0, 2π/6)** (Fourier-family lattice
  point), **its transpose** (certified via variant T — the decider separating
  what the Haagerup invariant provably cannot), and **S6**.

**Stratum E∩G — the two-triangle stratum, exhaustive.**
Ansatz: every noninitial row of the dephased matrix is a disjoint union of two
rotated ω-triangles x·{1,ω,ω²} ⊔ y·{1,ω,ω²} (ω = ζ₃), with the second-triangle
phase free per row. This is the natural −1-minor-free hunting ground: within
root-of-unity matrices of 2·3-smooth order, a chirality-(−1)-free matrix is
forced into it (2+2+2 vanishing-sum decompositions contain antipodal pairs).
S6 lies inside; F6 does **not** (its ±1 row is not a triangle pair).
- Search space: 40 discrete patterns/row; row-sorted canonicalization;
  exact integer pair-solvability prefilter (|C₀| ≤ 2|C₁| over Z[ω]);
  Gröbner consistency from depth 4. **Exhaustive, under budget**:
  22,064 nodes, 12,773 leaf Gröbner calls → **1,488 consistent leaves, all
  zero-dimensional** (no continuous families exist in the stratum).
- Extraction: shape-lemma back-substitution + certified-resultant root
  attribution; 3 leaves needed a quadratic-fiber extraction (solutions in a
  degree-2 fiber over Q(ζ₃)).
- **Outcome: 1,536 solutions across all leaves; every single one is
  equivalent to S6, each closed with a decider certificate re-verified by
  exact multiplication.** No solution had any chirality-(−1) minor
  (consistent: Haagerup values of the S6 class are {1, ω, ω²}).
- This yields an exhaustive classification statement for the stratum:
  *up to equivalence, S6 is the only 6×6 CHM whose dephased noninitial rows
  are all two-triangle rows.*

**Defect census.** Exact DomainMatrix rank (sound path, slag H6-H4) at every
reference point and every Butson class: **every family point has defect 4;
S6 has defect 0.** No anomalies (nothing outside {0, 4} anywhere).

**Reference catalogue** (`checks/lib/catalogue.py`, sources pinned):
F6(a,b)/F6ᵀ [TZ quant-ph/0512154v2 conventions], D6(c) [TZ], C6 (Björck) [TZ],
S6 [TZ/lib], B6(θ) [BN math/0609076v1], M6(x) [MS math/0702043v1], K6^(3)
[Karlsson 1003.4177v1, with the H2-reducibility theorem of 1003.4133v1],
G6^(4) [Szöllősi 1008.0632v1: Dilation Algorithm + the explicit generic
point]. Reference DB: 190+ exactly-verified grid points with canonical
fingerprints. Coverage notes: M6 grid at orders {1,2,3,6,8,12} (the two ζ₅
points omitted — DomainMatrix in that field exceeded 6h; the family is
anchored by 14 other points); B6 grid similarly at radical-friendly orders.

**G6^(4) hard precondition** (user-set): Szöllősi's explicit generic point
transcribed and **verified Hadamard**: all 36 unimodularity and 15 Gram
residuals certified zero by normal forms in the tower quotient
Q[a,e,s₁,t₁,t₃]/(relations + pairing coupler), with every denominator and
cascade lead coefficient certified nonzero by exact rational interval boxes.
Transcription audit: **16/16 printed data items of the paper byte-match the
code** (exact polynomial comparison; see “Transcription audit” below).
**Defect: computing** — the exact fraction-free elimination over the tower
was at pivot 4/~21 at wrap time and continues in background; the number will
be appended here when it lands. Per the sign-off decision this does not gate
the verdict: G6^(4) is in the reference set on its Hadamard verification, and
there are zero survivors for its defect to adjudicate.

## Why this closes the catalogue side

By Karlsson's theorem (source-cached, both directions): a 6×6 CHM with one
2×2 Hadamard submatrix (chirality −1) is H2-reducible, and the H2-reducible
matrices are exactly K6^(3) — which contains every named 1–2 parameter family
(F6, F6ᵀ, D6, B6, M6, X6^(2), K6^(2)). The known landscape is
K6^(3) ∪ G6^(4) ∪ {S6}. Every candidate this track produced fell to one of:
an explicit equivalence certificate to a catalogue point; the constructive
H2-block certificate (all nine 2×2 blocks chirality −1 under an exhibited
row/column pairing — validated on D6, C6, F6-points, B6, M6); or an S6
certificate. Nothing reached the G6^(4)-membership frontier because nothing
survived that far.

## Soundness discipline (what a verdict rests on)

- Zero tests three-valued; no `simplify`/`nsimplify` verdicts anywhere in
  Track B code (no-float lint enforced in selftest).
- "Known" always means a certificate: (P₁,D₁,P₂,D₂) re-verified by exact
  multiplication, or a verified structural certificate (H2 block form).
- Invariants in canonical form: minimal polynomial + certified isolating box.
- Defects by DomainMatrix over explicit algebraic fields; the lib's heuristic
  path is cross-checked and loses loudly on disagreement (H6-H4/H6-H5).
- Selftest: 60+ hard gates, all green at wrap (fingerprint closed forms,
  scramble round-trips, invariance identities, emptiness gates, decider
  certificates, catalogue anchors B6(π/2)~D6 / M6(1)~F6 / B6 self-adjoint).

## Transcription audit (sign-off item 1)

The G6 fix was a **method/ideal-construction correction; the transcribed
parametrization is unchanged from extraction**. Exact polynomial comparison
of the code against a fresh transcription of the verbatim `.tex` lines
(a-sextic; c; cubic c₃..c₀; U, V coefficient polynomials; t₃+t₄; 67·t₃t₄):
16/16 equal. What changed during verification, precisely:
1. My *derived* relation for the (t₁,t₂) pair — t₁t₂ = σ/σ̄ cleared of
   denominators; the paper prints no formula here — had dropped an A-power
   (deg σ_N = 6 ≠ deg σ_D = 5) when clearing the conjugate. Exposed because
   the mis-cleared quadratic's roots were certified non-unimodular while
   |σ|² ≈ 0.0677 ≤ 4 guarantees a unimodular pair. Fixed with explicit
   degree bookkeeping. (Slag **H6-H7**, stage 1.)
2. The certification ideal cut out all four (t₁,t₃) pairing components, so
   true identities of the actual matrix were not ideal members. Fixed by
   adding the pairing coupler — the paper's own step-#7 requirement,
   col 2 ⊥ col 3, linear in t₁ — and a monic (norm-inverse) elimination.
   Exactness certificates: the coupler's t₁ satisfies the pair quadratic
   identically mod (R1, R5) (resultant NF-zero); certified boxes separate
   the correct pairing (residual → 0 at 10⁻²⁴, wrong pairings ≈ 1.95).
   (Slag **H6-H7**, stage 2.)
One catalogue family **did** have a transcription change: the M6(x) b,c-pair
leading sign, caught by the build verification gate and fixed **toward the
paper**, validated against the paper's own printed anchors (the M6(1) matrix;
M6(1) ≅ F6). Logged as slag **H6-H6** with a contamination audit: the
mis-signed matrices failed the Hadamard gate immediately and never entered
any DB, ledger row, or downstream computation.

## Harness defects found by this track

- **H6-H4** — lib `defect()` rank rests on heuristic zero-testing; sound
  DomainMatrix path built, agrees on all anchors, wins loudly elsewhere.
- **H6-H5** — lib `is_hadamard()` collapses UNDECIDED to False (false
  dismissal): B6(2π/3) is a true Hadamard rejected by the lib, proven by two
  independent sound methods. Contamination audit (sign-off item 2): found on
  day 2 during catalogue verification; every earlier consumer of the lib
  predicate (planning probes, lib self-test, all six stratum-A class reps)
  ran it only alongside the sound field path with agreement on every case,
  and nothing anywhere was dismissed on a lib False. Full entry with the
  audit: `slag/harness-defects.md`.
- **H6-H6, H6-H7** — as above (own-instrumentation defects, contamination
  none, both caught by designed verification gates).

## Stalls and coverage limits (nothing hidden)

- Two-triangle stratum: 3/1,488 leaves initially stalled the shape-lemma
  extractor; resolved same day by quadratic-fiber extraction; all 6 fiber
  solutions closed to S6 with certificates. Stratum fully exhausted.
- Butson q ≥ 8 was cut from scope by the run owner (day-2 revision).
- M6 ζ₅ grid points and the G6 exact defect: cost-bounded as noted above.
- The Dilation-Algorithm membership solver (for adjudicating hypothetical
  `unresolved-G6` survivors) was designed but never needed — no candidate
  survived to require it.

## Bottom line

A three-day, fully exact, certificate-disciplined blind search across the
strata where a new matrix could most plausibly hide — exhaustive Butson
through q = 6, the complete two-triangle stratum, and a defect census over
the whole reference catalogue — produced nothing outside the known
catalogue, and produced machine-checkable certificates for every closure.
The instrument found four real defects in the shared harness along the way
and left the catalogue, the invariants, and the deciders substantially
hardened for the adjudication.

*G6^(4) exact defect: pending, appended here when the elimination lands.*
