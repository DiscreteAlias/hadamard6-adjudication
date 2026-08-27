# V1 — Fidelity audit of `dag.md` against `paper/2608.18053v1.pdf`

Run 2026-08-26. Fresh session, adversarial framing per `VERIFY.md` §V1.
Extraction: `pdftotext -layout`, all 50 pages, read directly. No subagents, no
paraphrase chains — every quote below is from the extracted page named.

`dag.md` was not edited. Every correction here is a recommendation.

**Scope actually covered.** All 49 rows were checked for (a) existence, (b) statement
fidelity, (c) edge fidelity both directions, (d) page-reference coverage. Depth is
not uniform and is stated per node in §3.

- **Full-proof read** (every page of the proof read end to end, both directions of (c)):
  L8, P13, P14, P15, P16, P12, S3, S4, P17, P18, C19, T6, S15, S16, S17, S18, S19,
  T22, P24, P25, C26, D23, D20, S5, S6, S7, S8, S9, S10, S11, S12, S13, S14, S20,
  U1, U2, U3.
- **Definition rows read in place**: D1, D2, D3, D4, D5, D9, D10, D11, S2.
- **Import row**: P7 checked against its printed statement, footnote 1, and both
  restatements (p4, p15); the *cited sources* [24][26][27] were not opened (that is
  the separate citation-fidelity task, still ☐ in `dag.md`'s import table).

---

## 1. The paper's own dependency claims (independent source)

### 1.1 Figure 1, p3 — **agrees with `dag.md`**

The flow diagram reads, top to bottom:

> "For arbitrary [H] ∈ H₆, does one of the 400 positional corners give a finite-corner
> witness?" → *no* → "Failure-of-search routing / **Proposition 16**" → "[H] ∈ K₆⁽³⁾
> finite witness: **Proposition 17**" ∥ "H ∼ S₆⁽⁰⁾ finite witness: **Proposition 18**"
> → "Every [H] ∈ H₆ has a finite-corner witness" → "The actual B, C occur in the finite
> candidate lists; orthogonality forces the actual unimodular block D" → "H₆ ⊆ A₆^fc;
> soundness (**Proposition 12**) gives H₆ = A₆^fc"

T6 rests on exactly {P16, P17, P18}. **Matches `dag.md` T6 row exactly.**

The two printed proofs of Theorem 6 confirm it independently:

> p8: "Proposition 16 then gives [H] ∈ K₆⁽³⁾ or [H] ∈ T₆. In the first case,
> Proposition 17 supplies a finite-corner witness, and in the second, Proposition 18
> supplies one."

> p31: "Proposition 16 gives a finite-corner witness when the matrix is neither
> Karlsson nor Tao; Proposition 18 gives one for Tao; and Proposition 17 gives one for
> every Karlsson matrix."

The figure's lower half also confirms C19 ← {T6, P12, S3}: the "actual B, C occur in
the finite candidate lists" box is Proposition S.3, and the caption names Proposition 12
for soundness. The p31 proof of C19 names all three explicitly:

> p31: "Theorem 6 supplies a finite-corner witness for every class. At that corner the
> actual adjacent blocks occur in the complete finite candidate lists, and
> **Proposition S.3** recovers the actual fourth block. Thus H₆ ⊆ A₆^fc.
> **Proposition 12** gives the reverse inclusion."

**Verdict: no discrepancy.** `dag.md`'s two most load-bearing edge sets are corroborated
by an independent source in the paper.

### 1.2 §"Proof dependencies and formal audit", p31 — **agrees on scope, one caveat**

Point 3 is the scoping sentence the deliverable rests on:

> p31: "The four-phase reconstruction, its intersection geometry, and the ramification
> patch are proved in the remaining sections but are **not part of the Lean
> formalization**. They are consequences of the classification, not inputs to it."

"The remaining sections" = Supplement Section II, which begins on p31 and contains
D20 (recalled p35), T21, T22, D23 (recalled p48), P24, P25, C26 and S5–S20. This
reproduces `dag.md`'s 11-node audit gap: everything in the C26 cone that is not under
C19 is Section II material. **No disagreement.**

What Lean actually proves, per p31:

> "From these arguments Lean derives, in the same order as the paper,
> IsHadamard(H) ⟹ HasFiniteCorner(H) ⟹ H ∈ A₆^fc, proves the converse implication by
> direct-completion soundness, and hence proves IsHadamard(H) ⟺ H ∈ A₆^fc both for
> matrices and on equivalence classes."

`IsHadamard(H) ⟺ H ∈ A₆^fc` is Corollary 19 (Eq. 46 / S.1.137) at matrix and class
level. So the audited statement is exactly C19. **`dag.md`'s "inside Lean-audit scope"
tags on T6 and C19 are correct.**

**Caveat — see finding V1-8.** The paper's claim that the two Lean hypotheses are
"precisely the two published inputs of Proposition 7" does not survive a literal
reading, and `dag.md`'s load-bearing section repeats it without qualification.

---

## 2. Findings

Severity codes: **[CONE]** changes cone membership or the gap list · **[BUCKET]**
changes a bucket assignment · **[STMT]** statement fidelity · **[EDGE]** edge fidelity
without cone consequence · **[PAGE]** page-reference coverage · **[INTERNAL]** provable
without the paper.

---

### V1-1 — D20 depends on Lemma S.7 without naming it **[CONE]**

**Row says** (`dag.md:42`):

| id | statement | depends |
|---|---|---|
| D20 | Def 20: product-regular lift (11 guards, Eq 63 / S.2.26) (p9; recalled p35) | `Sec II B machinery (S.2.16–S.2.24)` |

**Paper says.** S.2.23 and S.2.24 are not "machinery" — they are the statement of
Lemma S.7, a node the DAG already carries (row S7):

> p35: "**Lemma S.7 (Product-factor identities).** Equations (S.2.23) and (S.2.24) are
> polynomial identities on the regular fixed-Gram locus. In particular,
> u + v = −c₃/((1+ss^#)c₆), uv = c₀/c₆."

And in the main text, D20 is introduced on p9 immediately after S.7 is invoked to
license the very objects D20 quantifies over:

> p9: "For either choice u = u±, the corresponding coordinates x₁, x₂, x₃ are the roots
> of q_{s_h,u}(x) = x³ − s_h x² + u s_h^# x − u. (58) **Supplemental Lemma S.7 proves the
> exact factorization**, also recorded in Supplemental Eq. (S.2.23):
> Φ_h(x) = c_{6,h} q_{s_h,u₊}(x) q_{s_h,u₋}(x). (59)
> **Definition 20 (Product-regular lift).** …"

The p35 recall of D20 sits directly under Lemma S.7's proof and reads:

> p35: "The lift is product regular when **the product quadratics have their expected
> degree**, the coordinate cubics have simple roots, all companion denominators are
> nonzero, and [S.2.26]."

"The product quadratic" is Eq. (S.2.24); that its two roots are the two coordinate-cubic
products is precisely S.7.

**Severity.** `dag.md` names S.7's content as an equation range instead of an edge.
S7 is currently **outside** the C26 cone. Adding `D20 → S7`:

- C26 cone: 34 → 35 nodes
- audit gap: 11 → 12 nodes (S7 joins; it is not under C19)
- `MECH nodes outside the cone` loses S7
- **the headline is unaffected**: S7 is MECH, so the claim "eight unmechanized ARG
  nodes plus D23's definitional fidelity" is unchanged.

**Counter-argument, stated fairly.** D20 is a `DEF` row with no proof obligation, and
Eq. 54 defines u = x₁x₂x₃ directly, so `q_h` can be *formed* without the factorization
theorem. One can defend the current row on that basis. But the row cannot both name
S.2.23–S.2.24 as its dependency and deny an edge to the node whose entire statement is
S.2.23–S.2.24.

**Recommended correction.** Add `S7` to D20's `depends`, and trim the prose string to
`Sec II B setup (S.2.16–S.2.22)`. Rerun `dag_audit.py`; expect gap 12, cone 35. If you
prefer to keep D20 edge-free as a pure DEF, then the prose string must be narrowed so
it no longer swallows a node.

**This is the only finding among the eleven that changes the published gap list.**

---

### V1-2 — Unnumbered load-bearing claim on p43, no DAG node (**candidate U4**) **[CONE-adjacent, omission]**

**Row says.** Nothing. No row covers this claim. `dag.md`'s U-series stops at U3.

**Paper says.** Standalone paragraph on p43, between the end of Prop S.17's proof
("Hence every Tao frame fails at least one product-regularity guard.") and Lemma S.18:

> p43: "For a phase block X, write γ_ij = Σ_k X_ik X̄_jk. An unordered row pair {i, j}
> is **good** if its three entrywise row ratios are distinct and, for the remaining row
> ℓ, |γ_iℓ| ≠ |γ_jℓ|. Let Good_r(X) mean that some row pair is good, and put
> Good_c(X) = Good_r(Xᵀ). Call the corresponding orientation **directionally bad** when
> its goodness condition fails. **At a finite corner, a product-regular frame exists
> exactly when the actual horizontal side is row-good and the actual vertical side is
> column-good.** Indeed, distinct ratios give a simple coordinate cubic and a nonzero
> leading coefficient, while unequal correlation magnitudes are exactly the nonzero δ
> guard. The uncancelled common-root identity then makes the companion resultant
> nonzero outside the H₂ locus. Reversing the chosen pair conjugates the leading
> coefficient and changes only the sign of δ, so the three unordered pairs exhaust all
> frame orientations."

**Why it is load-bearing.** It is an **iff** with a four-sentence proof, not a
definition. It is the *only* bridge between the "directionally bad" language of S18/S19
and product regularity. T22's proof consumes it directly:

> p45: "Suppose now that no frame is product regular. **At every finite corner at least
> one adjacent side is directionally bad.** Lemma S.18 excludes simultaneous badness
> outside Karlsson and Tao."

That sentence is the contrapositive of the ⟸ direction. Without this claim, S18 and S19
say nothing about 𝒫₆ and T22's counting argument does not start.

**Severity.** This is exactly the V3 omission class — an unnumbered load-bearing step
invisible to dense counters — and it sits **inside the C26 cone on the T22 path**, i.e.
in the deliverable. It is materially more consequential than either page gap V3 found.

**Recommended correction.** Add a row:

```
| U4 | (unnumbered, p43) directional-goodness dictionary: at a finite corner, a
       product-regular frame exists ⟺ actual horizontal side row-good ∧ actual vertical
       side column-good | D20 | ARG | unverified | three guard identifications
       (simple cubic + nonzero leading coeff ← distinct ratios; nonzero δ ← unequal
       correlation moduli; nonzero companion resultant ← uncancelled common-root
       identity, outside the H₂ locus) each MECH-checkable; the "three unordered pairs
       exhaust all frame orientations" step is the ARG risk |
```

and edges `T22 → U4`, `S18 → U4`, `S19 → U4`. Cone unchanged (U4's only dependency,
D20, is already in the cone); the gap list gains U4 and becomes 12 (or 13 with V1-1).

---

### V1-3 — S6's proof does **not** span pp33–34; V3's "p34 resolved" note is wrong **[PAGE]**

**Row says** (`dag.md:59`):

> S6 | Prop S.6: physical soundness and completeness at one corner … (statement p33,
> **proof p33-34**)

That page span was introduced by the V3 pass, per `verification/v0-structural.txt`:

> "p 34 — RESOLVED, citation imprecision only. S.6 is stated at the end of p33; its
> proof runs pp33-34. The paper omits the closing box, which made the proof appear to
> continue onto p35. S.7 starts clean on p35 and ends there. No unmodeled content."

**Paper says.** S.6's proof is five sentences, entirely on p33, and p34 opens with a new
section header. Raw (non-`-layout`) extraction of the p33/p34 boundary:

> **p33, last lines:** "Proof. The two physical incidence systems are exactly the
> complete physical candidate sets by Lemma S.5. The intrinsic finite-fiber condition
> is therefore exactly the guard in Definition 10. The determinant conditions select
> exactly the permitted candidate pairs. Proposition S.3 then states that Eq. (S.2.15)
> is the unique possible completion and that Eq. (S.2.14) is equivalent to the Hadamard
> entrywise condition. These are precisely the five steps of our completed procedure."
>
> **p34, first lines:** "34 / B. / Generic quadratic–cubic algebraic cover / The global
> incidence equations are simplest conceptually. …"

**What is actually on p34.** The opening of Supplement Sec. II B — and it is
definitional/derivational content that three rows depend on but none cites:

- (S.2.16) the self-inversive cubic q_{s,u}(z) = z³ − sz² + us^#z − u
- (S.2.17) the uncancelled linear relation A(z) + B(z)y = 0
- (S.2.18)–(S.2.19) explicit A(z) and B(z) = b₀ + b₁z + b₂z² + b₃z³
- (S.2.20) the reciprocal fundamental sextic Φ_fund(z) = z³A(z)A(z)^# − B(z)B(z)^#
- (S.2.21) the leading coefficient c₆
- (S.2.22) the coefficient identities
- (S.2.23) the factorization Φ_fund = c₆ q_{s,u} q_{s,v}
- (S.2.24) the product quadratic (1+ss^#)c₆U² + c₃U + (1+ss^#)c₀ = 0

S7's `depends` string is "S.2.16–S.2.24"; S4's is "sextic definition (Eq 53 /
S.2.18–S.2.20)"; D20's is "Sec II B machinery (S.2.16–S.2.24)". All three point at p34.
**No row's page field claims p34.**

**Severity.** Two things at once: a fabricated page span now sits in `dag.md`, and the
p34 gap V3 believed it had closed is still open. Both are the systematic defect the
brief named — *where a result is stated vs. where its content lives*.

**Provenance — recorded explicitly, because it is the point of the finding.** V3 was a
**manual read by the run owner**, not an extraction error by the session that built the
DAG. The false span `proof p33-34` was written into `dag.md` on the strength of that
read without checking the page boundary, and the "missing closing box" explanation in
`verification/v0-structural.txt` was invented to rationalize it. So the defect entered
the artifact through a *verification* pass, not through extraction — which is the
argument for V1 running as an independent, adversarially framed session on a different
model rather than as a self-check. This finding is the case that argument was written
for. Independently reproduced by the run owner via
`pdftotext -f 33 -l 34 paper/2608.18053v1.pdf - | tail -40`.

**Recommended correction.**
- S6 page ref → `(statement p33, proof p33)`.
- S7 page ref → `(statement and proof p35; defining machinery S.2.16–S.2.24 p34)`.
- Amend `verification/v0-structural.txt`'s V3 note: p34 is **not** S.6's proof
  continuation; it is Sec. II B's definitional block, and it was uncovered for a
  different reason than V3 recorded. *(Done — append-only correction block added
  2026-08-26; the original note is retained verbatim above it.)*
- After the S6 fix, page coverage will report p34 uncovered again unless S7 (or D20)
  claims it. That is the correct outcome, not a regression.

---

### V1-4 — D20's "11 guards" are Eq. (S.2.67) on p42, not Eq. (S.2.26) on p35 **[PAGE]**

**Row says** (`dag.md:42`): `Def 20: product-regular lift (11 guards, Eq 63 / S.2.26) (p9; recalled p35)`

**Paper says.** Three different guard formulations exist, and the row conflates them.

*Eq. 63, p9* — thirteen written factors (eleven after grouping the two star-conjugate
determinant pairs):

> "det(E) det(B)(det B)^# det(C)(det C)^# × c_{6,h} c_{6,v} δ_h δ_v × Disc(q_h) Disc(q_v)
> R_h R_v ≠ 0."

*Eq. (S.2.26), p35* — **nine** factors, with the discriminant and resultant guards in
prose rather than in the equation:

> "The lift is product regular when the product quadratics have their expected degree,
> the coordinate cubics have simple roots, all companion denominators are nonzero, and
> c_{6,h} c_{6,v} δ_h δ_v det(E) det(B)(det B)^# det(C)(det C)^# ≠ 0"

*Eq. (S.2.67), p42* — the canonical eleven-item list, and the only place in the paper
where the phrase "eleven guards" appears:

> p42: "A frame over a retained finite corner is product regular precisely when the
> **eleven guards** det E, det B(det B)^#, det C(det C)^#, c_{6,h}, c_{6,v}, δ_h, δ_v,
> Disc q_h, Disc q_v, R_h, R_v are nonzero. Here R_h, R_v are the cleared resultants of
> the actual candidate cubic and its companion denominator."

**Severity.** The count "11" is correct but is sourced to two equations that do not
state it, one of which (S.2.26) enumerates only nine. More importantly, p42's S.2.67 is
the form that S16, S17 and T22 actually use ("every frame fails a resultant guard",
"fails at least one product-regularity guard"), and D20 does not cite p42.

**Recommended correction.** D20 page ref →
`(p9, Eq 63; recalled p35, S.2.26; eleven-guard canonical form S.2.67 p42)`.

---

### V1-5 — S18's short statement drops the "invertible blocks" hypothesis **[STMT]**

**Row says** (`dag.md:71`): `Lemma S.18: two-sided badness dispatcher: both actual sides directionally bad ⇒ H₂-reducible or order-3 Hadamard block (pp43–44)`

**Paper says** (p43):

> "**Lemma S.18 (Two-sided badness dispatcher).** Let a **finite-corner presentation
> have invertible blocks** and suppose that its horizontal and vertical actual sides are
> both directionally bad. Then the completed Hadamard matrix is H₂-reducible or contains
> an order-three Hadamard block. In particular, outside the Karlsson and Tao sectors,
> the two actual sides of a finite corner cannot both be directionally bad."

Two hypotheses are dropped: *finite-corner presentation* and *invertible blocks*. The
second is used in the proof:

> p43: "The only divisions below are by phase monomials and **block determinants; these
> are nonzero by hypothesis**."

The second sentence ("In particular, outside the Karlsson and Tao sectors …") is also
dropped, and it is the form T22 actually consumes (p45: "Lemma S.18 excludes
simultaneous badness outside Karlsson and Tao").

**Severity.** Statement fidelity on one of the eight deliverable ARG nodes. No cone or
bucket change. It matters because a hypothesis-free reading of S18 is materially
stronger than what the paper proves.

**Recommended correction.** Statement →
`Lemma S.18: two-sided badness dispatcher: finite-corner presentation with invertible
blocks, both actual sides directionally bad ⇒ H₂-reducible ∨ order-3 Hadamard block;
hence outside K₆⁽³⁾ ∪ T₆ the two sides cannot both be bad (pp43–44)`.

---

### V1-6 — `P13 → S1` is a spurious edge **[EDGE]**

**Row says** (`dag.md:35`): `P13 | … | depends: S1, S2`

**Paper says.** Proposition 13's proof runs pp17–23 and **never invokes Lemma S.1**. I
read all seven pages; Lemma S.1 appears nowhere in that range. The first citation of
Lemma S.1 anywhere in the supplement is on **p24**, inside Proposition 14's proof:

> p24: "**Lemma S.1** and Eq. (S.1.84) give Re τ_c(B) < 0."

What P13 actually uses from Sec. I B is the *unnumbered* normalization identity
Eq. (S.1.14), τ_r(X) = S·R·T, on p17 — a different object from Lemma S.1's
Re τ_r = Re τ_c:

> p20: "If ζ = −1, Eq. (S.1.38) excludes s = 0, and **Eq. (S.1.14)** gives
> Re τ_r(X) = −st² < 0."
> p22: "In either case, **Eq. (S.1.14)** yields Re τ_r(X) < 0."

**Severity.** Spurious edge = noise, and the cone is unaffected: S1 stays in the C26
cone via P14, where `dag.md` already lists it correctly. Worth fixing anyway because
`dag.md` names S1 as one of P13's only two dependencies, which overstates what P13
inherits.

**Recommended correction.** P13 `depends` → `S2` (plus, if you want the identity
represented, the Sec. I B normalization Eq. S.1.12–S.1.14 as a prose string). Note in
the row that Re τ_r = Re τ_c (S1) enters at P14, not P13.

---

### V1-7 — Main-text proofs are treated as absent for eight nodes **[PAGE]**

**Rows say.** The page fields use the form `(statement page; proof supplement-page)`,
implying the proof lives only in the supplement:

| row | `dag.md` page field | proof also printed in full at |
|---|---|---|
| **P24** | `(p12; proof p48)` | **p12** |
| **P25** | `(p12; proof pp48–49)` | **p12** |
| **C26** | `(p12; proof p49)` | **p12** |
| T6 | `(p3; proof p8, p31)` | p8 ✓ (p31 is a restated proof, not the audit note) |
| P12 | `(p6; proof p27)` | **p6** |
| P16 | `(p8; proof p26)` | **p8** |
| C19 | `(p8; proof p31)` | **p8** |
| P18 | `(p8; proof p30)` | **p8** |

**Paper says**, e.g.:

> p12: "**Proof of Corollary 26.** By Corollary 19, A₆^fc = H₆. Substituting this
> equality into Proposition 25 gives G₆⁽⁴⁾ = H₆ \ (K₆⁽³⁾ ∪ T₆). Tao and Karlsson are
> disjoint because every cross ratio of Tao is a cubic root of unity, whereas
> H₂-reducibility requires a cross ratio equal to −1."

> p12: "**Proof.** Product regularity (Definition 20) asserts that the relevant leading
> coefficients and companion denominators are nonzero and that the coordinate roots are
> simple. Every elimination step … is therefore reversible. Both procedures then use the
> same forced block and the same nine unimodularity tests…" *(Prop 24, complete)*

**Severity.** Page coverage is not violated (the statement page is cited), so V0 could
never see this. It matters for two reasons:

1. It is the same systematic defect as V1-3 — the extractor recorded one location per
   proof.
2. **For P25 the two proofs have different edge sets.** The p12 proof derives the
   forward inclusion directly from Definition 23 and does *not* route through S15:

   > p12: "Let [H] ∈ G₆⁽⁴⁾. **By Definition 23**, a representative is produced by
   > Construction 3.1 from finite normalized candidate sets. … Hence the branch-complete
   > atlas retains H, proving the forward inclusion."

   The p49 proof does:

   > p49: "**Proposition S.15** gives the forward inclusion. Conversely, Theorem 22
   > supplies every class on the right with a product-regular frame. At that frame,
   > Proposition 24 shows that Construction 3.1 recovers the matrix."

   `dag.md`'s `S15, T22, P24` matches the supplement route and is the **more
   conservative** choice — it does not lose an edge. No correction needed to the edge
   set; the finding is that the S15 edge exists only on one of two printed routes, and
   that should be on the record.

**Recommended correction.** Change the page-field convention to name every proof
location, e.g. `P24 (p12; proof p12, restated + reproved p48)`. At minimum do this for
P24, P25, C26 — the three deliverable nodes.

---

### V1-8 — the Lean audit's second hypothesis is not literally P7(1) **[framing; deliverable-relevant]**

**`dag.md` says** (`dag.md:87–91`, "Load-bearing step"):

> "The paper ships a companion Lean 4 audit claimed (p31) to mechanize the entire
> T6/C19 chain with **exactly P7's two published inputs as explicit hypotheses**. If
> that artifact checks out …, the classification's residual trust collapses to: **P7
> citation fidelity + Lean statement fidelity**."

**Paper says** (p31):

> "Its public theorem keeps two arguments visible. The first is the cubic-root
> criterion. The second is the **concrete raw-or-seam form** of Karlsson's complete
> parametrization: **every H₂-reducible Hadamard has either a canonical
> Karlsson-coordinate presentation or an affine-Fourier seam presentation.** These are
> precisely the two published inputs of Proposition 7, not additional classification
> hypotheses."

Compare P7(1) as printed (p4, restated p15):

> "H is H₂-reducible **if and only if** it is equivalent to a member of Karlsson's
> complete three-real-parameter family."

The Lean hypothesis differs from P7(1) in two ways:

- **direction**: P7(1) is an iff; the Lean argument is the forward direction only
  (H₂-reducible ⟹ has a presentation). Weaker, which is fine — but it means the Lean
  theorem does not carry P7(1)'s converse.
- **form**: "canonical Karlsson-coordinate presentation **or** affine-Fourier seam
  presentation" is a specific two-case concrete normal form, not "member of Karlsson's
  three-real-parameter family". The seam split is exactly the case division that P17's
  proof organizes itself around (pp28–30: simultaneous-degeneracy boundary vs.
  nondegenerate chart).

The sentence "These are precisely the two published inputs of Proposition 7" is the
**paper's own assertion**, not something the reader can verify from p31.

**Severity.** Does not change the cone. It changes the accuracy of the deliverable's
residual-risk sentence: "Lean statement fidelity" is not a single check but *two* —
(i) does the Lean theorem statement match C19, and (ii) is the second Lean hypothesis
actually implied by the cited Karlsson theorems, given it is a concrete presentation
claim rather than a family-membership claim. The second is genuinely a citation-fidelity
question about [26][27], not a Lean question.

**Recommended correction.** Rewrite the load-bearing paragraph to state the Lean
hypotheses as the paper actually gives them, and split the residual-trust claim:
`P7(2) citation fidelity + the raw-or-seam form's fidelity to [26,27] + Lean statement
fidelity to C19`. Do **not** adopt the paper's "precisely" claim.

**Minor, same section.** p31 point 1 reads "**Sections I B–I G** prove the new
fixed-Gram, routing, completion, and Karlsson-witness steps" — omitting Section I A,
which is Lemma 8's proof (pp15–16) and is load-bearing for P14 and P16. The Lean chain
as stated (IsHadamard ⟺ A₆^fc) plainly includes it; the section range on p31 is a paper
slip. Worth one line in the ledger, since the deliverable quotes p31 for scope.

---

### V1-9 — `dag.md`'s own bucket counts are stale (U3 never folded in) **[INTERNAL]**

Provable from `dag.md` and `verification/v0-structural.txt` alone; no paper needed.

**Row/header says:**

- `dag.md:5–7`: "Rows: all 26 main-text numbered items + all 20 supplement-only
  S-numbered results + **2 unnumbered load-bearing claims (U1, U2)**."
- `dag.md:101–102`: "**48 rows** = **40 claim nodes** + 8 DEF rows"
- `dag.md:104`: "MECH: **11** — D3, D5, P18, S1, S3, S5, S7, S10, S13, S17, U1"
- `dag.md:108`: "ARG ≈ **68 %** of claim nodes"

**Actual** (`verification/v0-structural.txt`, same file):

> "rows: **49**   buckets: {'DEF': 8, 'MECH': **12**, 'ARG': 27, 'IMPORT': 2}"

U3 was added by V3 with bucket MECH (`dag.md:76`) and never entered the counts block.
Correct figures: 49 rows = 41 claim nodes + 8 DEF; MECH 12 (add **U3**); ARG 27/41 ≈ **66 %**;
unnumbered claims = 3 (U1, U2, U3) — 4 if U4 (V1-2) is adopted, 5 with U5 (V1-13).

**Severity.** No cone or edge consequence, but the counts block carries a
"do not revise silently" instruction, so a stale count is exactly the kind of thing
that gets quoted downstream.

**Recommended correction.** Update lines 5–7, 101–102, 104, 108. Verify with:

```bash
python3 checks/dag_audit.py dag.md --pages 50 --target C26 --audited C19
```

---

### V1-10 — `S11 → classification` edge missing **[EDGE, outside cone]**

**Row says** (`dag.md:64`): `S11 | … | depends: S10, Bondal–Zhdanovskiy (import), Hardt triviality (import)`

**Paper says** (p38, inside S.11's proof):

> "Removing the at-most-three-dimensional Karlsson sector and the Tao point leaves a
> real four-dimensional locus. **The finite-corner classification covers it by finitely
> many corner loci.**"

and flags the direction explicitly on p37:

> "This proposition is a post-classification geometric consequence. It is not used in
> the finite-corner selection theorem or in the proof of Theorem 6; its proof may
> therefore invoke that classification without circularity."

`dag.md`'s note-field records the fact ("Authors state it is post-classification — not
used by T6 (p37); used by T21") but no edge exists.

**Severity.** S11 is outside the C26 cone and only feeds T21 (an orphan). Adding
`S11 → C19` does **not** change the C26 cone. It does make T21's inherited burden honest.

**Recommended correction.** Add `C19` to S11's `depends`.

---

### V1-11 — U2's proof is on p47, row cites only p46 **[PAGE, outside cone]**

**Row says** (`dag.md:75`): `U2 | (unnumbered, p46) intrinsic Karlsson characterization …`

**Paper says.** The statement (S.2.101) closes p46; the proof opens p47:

> p47: "**Proof.** The cross ratio equals −1 exactly when the corresponding 2 × 2
> submatrix becomes F₂ after row and column phasing. Karlsson's completeness theorem for
> H₂-reducible order-six Hadamards therefore gives the equivalence. The finite-corner
> classification gives the containment. It is strict because Tao belongs to A₆^fc, while
> every Tao cross ratio is a cubic root of unity and hence is not −1."

Textbook off-by-one of the class V1-3 describes. Edges (P7(1), C19) are both confirmed
by that quote. p47 is covered by S20, so page coverage never flagged it.

**Recommended correction.** U2 page ref → `(unnumbered, p46; proof p47)`.

---

### V1-12 — `U3 → S4` edge missing **[EDGE, outside cone]**

**Row says** (`dag.md:76`): `U3 | … | depends: S.2.60–S.2.64`

**Paper says** (p41):

> "The three blocks are invertible, and the leading fundamental coefficient is nonzero
> for both row orientations of B and Cᵀ. **Lemma S.4** therefore makes both complete
> candidate fibers finite, and the forced completion reproduces Eq. (S.1.115)."

**Recommended correction.** Add `S4` to U3's `depends`. U3 stays outside the C26 cone
(S4 is already inside it, via P17).

---

### V1-13 — second omission candidate: equivalence-invariance of 𝒫₆, p42 (**candidate U5**) **[omission, lower weight]**

**Paper says** (p42, unnumbered, one sentence of argument):

> "Row and column permutations act bijectively on the 400 corners and the 14,400 frames,
> transporting the normalized fibres, actual blocks, guards, and product equations.
> **Consequently the existence of a product-regular frame is invariant under standard
> equivalence**, although an individual preferred frame is not intrinsic. The full zero
> support is retained when several guards vanish simultaneously; no arbitrary 'first
> failed guard' convention is used."

**Why it matters.** Eq. (S.2.68) defines 𝒫₆ at *class* level
(`𝒫₆ := {[H] ∈ ℋ₆ : [H] admits a product-regular frame}`). T22, S16 and S17 are all
statements about 𝒫₆. Without equivalence-invariance, 𝒫₆ is not well-defined and none of
the three is well-posed.

**Severity.** Lower than V1-2: the argument is short, near-mechanical, and the paper
gives the reason in the same sentence. But it is an unnumbered well-definedness claim
underneath three of the eleven deliverable nodes, so V3's standard says it should be
visible. Flagged at lower confidence than U4 — this is a judgment call, U4 is not.

**Recommended correction.** Either add `U5 (unnumbered, p42) 𝒫₆ well-defined:
product-regular-frame existence is standard-equivalence invariant | D20 | MECH |
bijective transport of 400 corners / 14,400 frames`, or add one line to D20's note
recording it. Adding it does not change the cone (D20 is in it) but does grow the gap
list.

---

### V1-14 — nits (no correction required, recorded for completeness)

- **D23 page field has a typo** (`dag.md:45`): `defnitional passage 41` — misspelled and
  missing the `p`. Should be `definitional passage p41`. The page itself is correct: the
  third statement of Def 23 is on p41 ("Following Szöllősi, let G₆⁽⁴⁾ denote the
  non-Karlsson, non-Tao classes actually returned by Steps 1–8 of his Construction 3.1.
  His detailed Case 2 retains finite common-root solutions, and his Theorem 4.1 proves
  fixed-corner exhaustion whenever the normalized invertible candidate sets are finite."),
  and the p48 recall is confirmed.
- **P7(1) wording** (`dag.md:29`): row says `H₂-reducible ⟺ member of Karlsson's complete
  three-real-parameter family`; paper says "**equivalent to a** member". Harmless
  (H₂-reducibility is equivalence-invariant) but this is the import node, so exactness is
  cheap.
- **T22 note** (`dag.md:44`): "4×4 Gram positivity". Paper (p46) says "all eight remaining
  phase choices give a **nonzero** 4 × 4 Gram determinant … contradicting rank three" —
  nonvanishing, not positivity. Affects how the MECH check is written.
- **D10 statement** (`dag.md:32`) covers only the finite-dilation-corner half of Def 10.
  The second half, on p5, is the definition of *finite-corner witness* — the central term
  of T6/C19: "A displayed Hadamard matrix has a finite-corner witness when its upper-left
  block is a finite-dilation corner and its actual adjacent blocks belong to B_E^× and
  C_E^×." The `pp4–5` span is right; the statement should mention it.
- **P13 statement** (`dag.md:35`) drops "physical" from "normalized **physical** row-Gram
  fiber" (p17). Immaterial given X ∈ 𝕋³ˣ³, noted only for the record.
- **Paper-side citation defect** (not `dag.md`'s): p2 and p31 cite the Lean formalization
  as **[35]**, but reference [35] is "A. Platzer and G. Sutcliffe, eds., *Automated
  Deduction – CADE 28*" — the proceedings volume, not the artifact. The artifact is [36]
  (the GitHub repo), which p31 also names for the entry point. Ledger material.
- **P24's `depends`** lists `D20, D23`. Both proofs (p12, p48) invoke Definition 20
  explicitly and neither names Definition 23; routing "Construction 3.1" through D23 is
  consistent with `dag.md`'s own convention (D23's stated content *is* fidelity to
  Construction 3.1), so I am not flagging it. `D11` (the branch-complete procedure, the
  other half of P24's comparison) is arguably missing but is already in the cone.

---

## 3. Rows attacked and **not** broken

Recorded because a clean node is a result. Each of these had (a)–(d) checked against
the cited pages; where I say "edges exact" I mean I read the proof and found the listed
dependencies used and no unlisted named result used.

### The eleven (deliverable nodes)

| node | existence | statement | edges | pages | verdict |
|---|---|---|---|---|---|
| **C26** | Cor 26, p12; restated + reproved p49 | exact — "H₆ = G₆⁽⁴⁾ ∪ K₆⁽³⁾ ∪ T₆, where each sector is disjoint from the other two" (p12) | **exact**: C19, P25 — both proofs name exactly these | p49 ✓, p12 proof uncited → V1-7 | **clean but for V1-7** |
| **T22** | Thm 22, p11; restated p44, proof pp45–46 | exact — "H₆ \ 𝒫₆ = T₆ ∪̇ {[H×]}" (Eq 74 / S.2.86) | **exact, all six confirmed used**: P13 (p45 "the fixed-Gram trichotomy"), S18 (p45), S19 (p45), P7 (p46), S16 (p46), S17 (p46). **No T21 edge** — I checked specifically; T21 appears only in the trailing cross-reference sentence of the *statement*, never in the proof. Had it been used, T21+S7+S8+S9+S10+S11 would enter the cone and the gap would be ~17. It is not. | p44 is the restatement, proof is pp45–46; `pp44–46` acceptable | **clean** (U4 edge to add per V1-2) |
| **P25** | Prop 25, p12; restated p48, proof p49 | exact — "G₆⁽⁴⁾ = A₆^fc \ (K₆⁽³⁾ ∪ T₆)" | **exact**: p49 names S.15, Thm 22, Prop 24 in that order | see V1-7 (two routes) | **clean** |
| **P24** | Prop 24, p12; restated + reproved p48 | exact — "produce exactly the same candidate blocks and Hadamard completions" | D20 confirmed (named in the p12 proof); D23 defensible by convention; D11 arguably missing but in-cone | p12 proof uncited → V1-7 | **clean but for V1-7** |
| **S15** | Prop S.15, p42 | exact — "G₆⁽⁴⁾ ⊆ A₆^fc \ (K₆⁽³⁾ ∪ T₆)" (S.2.66) | **exact**: D23 ("Construction 3.1", "the sector restriction in the definition"), D11 ("retained by the branch-complete procedure") | p42 ✓ | **clean** |
| **S16** | Prop S.16, p42 | exact — "K₆⁽³⁾ \ 𝒫₆ = {[H×]}" (S.2.70) | P7(1) genuinely used (the reverse inclusion needs "apply Karlsson's standard parametrization", i.e. the passage from intrinsic H₂-reducibility to the family); [31] and the Karlsson parametrization confirmed; D20 definitional and in-cone | p42 ✓ | **clean**. Counts all verified: census (120,120,80,80) sums to 400; 49 = 40 empty + 1 imbalance + 6 mixed + 1 reciprocal + 1 remaining |
| **S17** | Prop S.17, p43 | exact — "T₆ ∩ 𝒫₆ = ∅" (S.2.71) | **exact**: D5, D20 (the three guard families named in the proof are exactly D20's: leading coefficients, imbalance factors, simple coordinate cubic) | p43 ✓ | **clean**. Counts verified: 120² = 14,400; 12,960; 5,760 |
| **S18** | Lemma S.18, p43, proof pp43–44 | **hypotheses dropped → V1-5** | **exact**: p44 "Proposition 7(1) sends the H₂ leaves to Karlsson, while Proposition 15 sends the order-three-Hadamard leaves to Karlsson or Tao" | pp43–44 ✓ | **V1-5 only** |
| **S19** | Cor S.19, p44 | exact — E_M(a,b) normal form, 2θ = q(3−q) > 0 (S.2.82–S.2.83) | **exact**: S18 ("The repeated-ratio and circulant leaves in the proof of Lemma S.18 … The remaining factor ad = b in Eq. (S.2.76)") | p44 ✓ | **clean** |
| **D23** | Def 23, p12; passage p41; recalled p48 | faithful; the "Equivalently, by his Theorem 4.1 …" clause is compressed away in the statement but preserved in the note | `[24]` — correct as an IMPORT leaf | all three locations confirmed present | **clean** (typo per V1-14) |
| **D20** | Def 20, p9; recalled p35 | see **V1-1** and **V1-4** | see **V1-1** | see **V1-3**, **V1-4** | **V1-1, V1-4** |

### The C19 chain (the audited half)

| node | verdict |
|---|---|
| **T6** | Statement exact (p3, restated p15). Edges {P16, P17, P18} confirmed three times over: Fig. 1 (p3), proof p8, proof p31. **Clean.** |
| **P7** | Statement exact both printings (p4, p15). Footnote 1's numbering drift (journal Thm 2.11 / Lemma 2.14 vs. arXiv-v1 Thm 2.12 / Lemma 2.15, conjecture 4.4) transcribed correctly. `external` as the dependency is right. **Clean** (nit V1-14). |
| **L8** | Statement exact (p4, p15). Proof pp15–16, page span exact. Edges {D1, D4} exact — and the paper explicitly closes the door on a P7 edge: p4 "We present a self-contained proof that stops at the 2 × 2 submatrix, **so that Karlsson's theorem is not used here** and the two structural inputs remain confined to Proposition 7." **Clean.** |
| **P12** | Statement exact. Edges {S3, D11} exact (p27 proof names Proposition S.3 and Definition 11). **Clean but for V1-7** (proof also on p6). |
| **P13** | Statement exact (p7, p17). Proof pp17–23, page span exact. Note-field verified in detail: branch structure "dependent branch" (p19) / "nondependent branch" (p20) / "first s = 0, then 0 < s < 1, and finally 1 ≤ s ≤ 3, where common unit-circle roots require separate care" (p20, S.1.55) — matches the row verbatim. Cited identity ranges S.1.20, S.1.26–S.1.31, S.1.37–S.1.45, S.1.58–S.1.69, S.1.75–S.1.80 all land inside pp18–23. No import edge needed: p18 says Haagerup's trick (S.1.21) "has been **derived directly** from the two residual coordinate pairs". **V1-6 only.** |
| **P14** | Statement exact. Proof pp23–24, page span exact. **All four edges confirmed used**: L8 + P7(1) (p23 "Lemma 8 and Proposition 7(1) then imply that every 3 × 3 submatrix of H is invertible"), P13 (p23, p24, three applications), S1 (p24 "Lemma S.1 and Eq. (S.1.84) give Re τ_c(B) < 0"). **Clean — the tightest row in the DAG.** |
| **P15** | Statement exact (p7 form and p24 form agree, since T₆ = {[S₆⁽⁰⁾]}). Proof pp24–26, page span exact. Edges {U1, P7(2), D4} exact — U1 at p24, P7(2) at p26 ("Proposition 7(2) therefore gives Eq. (S.1.90)"), D4 at p26 (the two "place [H] in K₆⁽³⁾" leaves). Note range S.1.91–S.1.108 correct. **Clean.** |
| **P16** | Statement exact. Proof p26, page exact. Edges {P14, P15, L8, P7(1)} all named in the p26 proof; **P13 is justified by the paper's own preamble**: p26 "Proposition 13 controls infinite side fibers, Proposition 14 selects a finite corner …, and Proposition 15 identifies the remaining case …. **These results prove Proposition 16.**" **Clean but for V1-7.** |
| **P17** | Statement exact. Proof pp28–30, page span **exact** (ends p30, "this proves K₆⁽³⁾ ⊂ A₆^fc"). Every number in the note verified against p28/p30: 245 pairwise resultants, 25 first-phase conditions, 18 residual second-phase branches (S.1.119); Karlsson chart + Möbius relations S.1.117–S.1.128; Bernstein dyadic subdivision terminating in **ten** rational boxes on p30; Lean module names match p49. Edges {P7(1), S4, Karlsson import} correct. **Clean.** |
| **P18** | Statement exact. Proof p30, page **exact**. Note verified verbatim against p30: det E = 3ω, (BB†)₁₂ = ω − 1 ≠ 0, (BB†)₂₃ = 0, cross ratios cubic ⇒ no H₂. Edges {P13, D5} exact. **Clean but for V1-7** (proof also on p8). |
| **C19** | Statement exact. Edges {T6, P12, S3} exact — see §1.1. **Clean but for V1-7.** |
| **S1** | Lemma S.1, p16, statement and proof both on p16. Statement exact. Note range S.1.8–S.1.11 correct. **Clean.** |
| **S2** | Def S.2, p17 (S.1.15). **Clean.** |
| **S3** | Prop S.3, p27. Statement exact including both directions. Note range S.1.110–S.1.114 correct. The "reproves, import avoided" note is the paper's own: p27 "This is Szöllősi's fixed-corner embedding criterion … **We restate and reprove it here** because the completed procedure of Definition 11 requires both directions". Edge {D9} correct. **Clean.** |
| **S4** | Lemma S.4, statement p27, proof p28. Span `pp27–28` exact. Statement exact including the "Consequently …" clause. The note's flag about Sec. II B formalism used inside Sec. I is correct and the non-circularity reasoning holds. **Clean.** |
| **D1, D2, D3, D4, D5, D9, D10, D11** | All exist on the cited pages (D1–D5 p2–p3, D9–D10 pp4–5, D11 p6). Statements faithful. D10 nit at V1-14. **Clean.** |
| **U1** | p24, exactly as described: "Three unit numbers sum to zero only when, after a common phase and a permutation, they are 1, ω, ω²; orthogonality of the two noninitial rows fixes their relative order." **Clean.** |

### Out-of-cone rows

| node | verdict |
|---|---|
| **S5** | Lemma S.5, p32, statement + proof. Statement exact (S.2.7 Gram form, S₃-relabelling clause). **Clean.** |
| **S6** | Prop S.6, p33. Statement faithful. Edges {S5, S3, D10} **exact** — all three named in the five-sentence p33 proof. **Page ref wrong → V1-3.** |
| **S7** | Lemma S.7, p35, statement + proof. Statement exact. **Machinery page p34 uncited → V1-3; owns S.2.23–S.2.24 that D20 claims as a prose dependency → V1-1.** |
| **S8** | Lemma S.8, pp35–36, span exact. Statement faithful; short statement omits "Let E be an invertible 3 × 3 phase matrix" (same class as V1-5, lower stakes). Note's identity ranges S.2.28–S.2.31 and "det G = 27 − 3p + J" verified verbatim on p35. Zariski-density + continuity + Sylvester steps present on p36 as the note says. **Clean modulo the dropped hypothesis.** |
| **S9** | Lemma S.9, p36, statement + proof. Statement faithful; short statement omits the "Consequently, every rational identity … specializes" clause, which is the part T21 uses. Edge to D20 correct; the S7 edge is not visibly exercised in the p36 proof. **Clean, minor.** |
| **S10** | Prop S.10, p37. Statement exact. Note verified verbatim: specialization (b,c,d) = (2,3,5), degree-8 P(a), gcd(P,P′) = 1, unique-factorization glue. **Clean.** |
| **S11** | Prop S.11, statement p37, proof p38, span exact. Statement exact. Specialization (a,b,c,d) = (2,3,5,7) confirmed. **V1-10** (missing classification edge). |
| **S12** | Cor S.12, statement p39, proof p40, span exact. Statement faithful. Edges {P13, P14, P15, P7(1)} **all four named in the p40 proof**. Note range S.2.47–S.2.53 correct (p39). **Clean.** |
| **S13** | Lemma S.13, p40, statement + proof. Statement exact. **Clean.** |
| **S14** | Thm S.14, p40. Statement faithful (400-corner union S.2.56, Laurent-rational transitions). Edges {S6, T6, S13} **exact** — the p40 proof names Proposition S.6, Theorem 6, and Eq. (S.2.54) which is S13's expression. **Clean.** |
| **S20** | Lemma S.20, p47, statement + proof. Statement exact. **Clean.** |
| **T21** | Thm 21, p10; restated + proved p36. Statement faithful. p36 proof names S8, S9, S11 and the Haagerup–Szöllősi decomposition — four of the five listed edges confirmed; **S7 is listed but not visibly used** in the p36 proof (same class as V1-6, outside the cone, not separately numbered). **Clean modulo that.** |
| **U2** | p46 statement, p47 proof. Edges {P7(1), C19} confirmed by the p47 quote. **V1-11** (page ref). |
| **U3** | p41 (S.2.65). Statement exact including the witness z₁ = (3+4i)/5, z₂ = (5+12i)/13 and the S.2.60–S.2.64 certificate. **V1-12** (missing S4 edge). |

### "Outside the DAG" section — spot-checked, clean

Table I on p48 ✓ (seven diagnostic rows, 256-bit Arb, Cayley seed over the degree-7
P(ξ) = Eq. S.2.108); the disclaimer is quoted correctly ("No classification or
product-coverage result depends on these numerical comparisons", p48); the 1600
automorphism witnesses trace to Lemma S.20 via p50 ("all 40² = 1600 permutation pairs
allowed by Lemma S.20") ✓; Farouki [45] is background as claimed ✓; the open question
on p11 ("Its possible intersection with the remaining Karlsson classes is not determined
here and remains an open problem") ✓; Sec. II K's scope remarks on p50 ✓; the LLM
disclosure on p13 ✓.

### External imports table — bibliographic check

Every entry in `dag.md`'s import table matches the reference list on pp13–14:
[23] Haagerup 1997 pp296–322 ✓ · [24] JLMS **85**, 616 (2012) ✓ · [26] LAA **434**, 239
(2011) ✓ · [27] LAA **434**, 247 (2011) ✓ · [28] MRL **11**, 251 (2004) ✓ ·
[29] J. Math. Sci. **216**, 23 (2016) ✓ · [31] Des. Codes Cryptogr. **92**, 4313 (2024) ✓ ·
[41] Basu–Pollack–Roy ✓ · [45] Farouki ✓ · [36] the GitHub repo ✓.
Only defect is the paper's own [35] mis-citation (V1-14).

---

## 4. Summary

**Findings by severity**

| id | node(s) | class | changes |
|---|---|---|---|
| V1-1 | D20 (→ S7) | **CONE** | gap 11 → 12; cone 34 → 35 |
| V1-2 | new U4 (p43) | **omission, in-cone** | gap +1 |
| V1-3 | S6, S7 | PAGE | reopens p34; removes a fabricated span |
| V1-4 | D20 | PAGE | adds p42 to D20 |
| V1-5 | S18 | STMT | dropped hypotheses |
| V1-6 | P13 | EDGE | spurious `P13 → S1`; cone unchanged |
| V1-7 | P24, P25, C26, +5 | PAGE | main-text proofs uncited |
| V1-8 | load-bearing § | framing | splits the residual-trust claim |
| V1-9 | counts block | INTERNAL | 48→49 rows, MECH 11→12, 68%→66% |
| V1-10 | S11 | EDGE | outside C26 cone |
| V1-11 | U2 | PAGE | outside cone |
| V1-12 | U3 | EDGE | outside cone |
| V1-13 | new U5 (p42) | omission, low weight | gap +1 if adopted |
| V1-14 | seven nits | — | none |

**What survives.** The claim the repo intends to publish is intact. C26's cone contains
the eleven, C19's Lean-audited chain does not, and Fig. 1 and p31 corroborate the DAG
rather than contradict it. The eight ARG nodes and D23 are unchanged. Every edge among
the eleven that I attacked held, including the one whose failure would have been most
expensive — **T22 does not depend on Theorem 21**, so the Section II B/T21 machinery
(S7–S11 and the Haagerup, Bondal–Zhdanovskiy, Hardt imports) stays out of the cone.

**What changes.** The gap list is 11 today; adopting V1-1 makes it 12 (adds S7, MECH),
adopting V1-2 makes it 13 (adds U4, ARG), adopting V1-13 makes it 14 (adds U5, MECH).
None of these disturbs the headline, because the added nodes are one ARG bridge and two
mechanical/definitional nodes — the eight unmechanized ARG nodes plus D23 remain the
finding. **If U4 is adopted, the deliverable's ARG count in the gap goes from eight to
nine**, and that sentence needs rewriting.

**Systematic defect, restated.** The brief's hypothesis is confirmed and is broader than
V3 found. The extractor recorded **one location per result**, chosen as the *statement*
site. This produced: a whole uncovered page (p34, V1-3), an uncited canonical definition
form (p42/S.2.67, V1-4), eight uncited main-text proofs (V1-7), and an off-by-one
(p47, V1-11). Page coverage caught none of these except the one that left a full page
blank — and V3's attempt to close that one closed it wrongly, in a manual pass, and
wrote a fabricated span into `dag.md` doing so.

**Recommended next step.** Apply V1-9 first (free, no paper needed), then V1-3 and V1-6
(unambiguous), then decide V1-1 and V1-2 — those two are the ones that move the
published number. Rerun `dag_audit.py` after each and diff the gap list.

---

## 5. Reproduction

```bash
# full-text extraction, layout-preserving, all 50 pages
pdftotext -layout paper/2608.18053v1.pdf /tmp/paper-layout.txt

# per-page extraction (the working set for every quote above)
for p in $(seq 1 50); do
  pdftotext -f "$p" -l "$p" -layout paper/2608.18053v1.pdf "/tmp/p$(printf %02d "$p").txt"
done

# V1-3: the p33/p34 boundary, raw (no -layout) so column order cannot mislead
pdftotext -f 33 -l 34 paper/2608.18053v1.pdf - | tail -40

# supplement section map — which section header lands on which page
for p in $(seq 14 50); do
  f="/tmp/p$(printf %02d "$p").txt"
  hits=$(grep -nE "^\s{20,}([A-Z]|I{1,3}V?)\.\s+[A-Za-z]" "$f")
  [ -n "$hits" ] && { echo "--- p$p"; echo "$hits"; }
done

# V1-6: confirm Lemma S.1 is absent from P13's proof (pp17-23) and present at p24
grep -l "Lemma S.1" /tmp/p1[7-9].txt /tmp/p2[0-3].txt   # expect: no matches
grep -n  "Lemma S.1" /tmp/p24.txt                        # expect: one match

# structural audit, unchanged by this pass (dag.md not edited)
python3 checks/dag_audit.py dag.md --pages 50 --target C26 --audited C19
```
