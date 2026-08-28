# Claim DAG `[D]`

Built **before** any verification. Everything downstream schedules against this.

Extracted 2026-08-25 from a full read of arXiv:2608.18053v1 (50 pp.). Rows: all 26
main-text numbered items + all 20 supplement-only S-numbered results + 2
unnumbered load-bearing claims (U1, U2). Page references are to the PDF.

**Conventions.**
- `bucket` classifies the node's *own* marginal verification burden, given its
  dependency edges; what a node inherits is carried by `depends`. Hybrid nodes
  get a primary bucket and the split is stated in `notes`.
- Pure-notation definitions carry `DEF` (no proof obligation; row kept for
  dependency wiring) and are excluded from bucket counts. Definitions that embed
  a checkable claim get a real bucket (D3, D5 → MECH; D23 → IMPORT, since its
  entire content is fidelity to Szöllősi's Construction 3.1).
- `status` is `unverified` everywhere: building this DAG involved no checking.

## Main-text nodes (shared counter 1–26)

| id | statement (short) | depends | bucket | status | notes |
|---|---|---|---|---|---|
| D1 | Def 1: complex Hadamard: H ∈ 𝕋^{n×n}, HH† = nIₙ (p2) | — | DEF | — | |
| D2 | Def 2: standard equivalence H′ = D_r P_r H P_c D_c; class space ℋ₆ (p2) | D1 | DEF | — | |
| D3 | Def 3: Fourier matrix Fₙ; is CHM for every n (p2) | D1 | MECH | unverified | F₆ check = ground-truth script |
| D4 | Def 4: 2×2 Hadamard submatrix; H₂-reducible; 𝒦₆⁽³⁾ ≔ H₂-reducible classes (p2) | D1, D2 | DEF | — | K-sector defined *intrinsically*; identification with Karlsson's family is P7(1), not this def. Embedded mini-claim (F₂ exposure equivalence) trivial-MECH |
| D5 | Def 5: Tao's dephased S₆⁽⁰⁾ over ω = e^{2πi/3}; 𝒯₆ = {[S₆⁽⁰⁾]} (p3) | D1, D2 | MECH | unverified | S₆⁽⁰⁾ Hadamard = ground-truth script |
| T6 | Thm 6: every order-6 CHM is equivalent to a dephased matrix having a finite-corner witness (p3; proof p8, p31) | P16, P17, P18 | ARG | unverified | pure assembly; Fig. 1 (p3) is its architecture; inside Lean-audit scope (p31) |
| P7 | Prop 7: published inputs: (1) H₂-reducible ⟺ member of Karlsson's complete three-real-parameter family; (2) dephased with noninitial cubic-root row AND column ⇒ [H] ∈ 𝒯₆ or [H] ∈ 𝒦₆⁽³⁾ (p4) | external | IMPORT | unverified | **the** import node. (1): [26,27], cross-cited [24, p.623, Thm 2.11]. (2): [24, p.624, Lemma 2.14]. Authors' footnote 1: arXiv-v1 numbering of [24] is Thm 2.12 / Lemma 2.15 (and conjecture 4.4) — numbering drift to check both ways |
| L8 | Lemma 8: singular 3×3 submatrix of an order-6 CHM ⇒ 2×2 Hadamard submatrix (p4; proof pp15–16) | D1, D4 | ARG | unverified | short, self-contained; identities S.1.1–S.1.5 MECH-checkable; case logic human |
| D9 | Def 9: normalized candidate sets ℬ_E, 𝒞_E; invertible subsets ℬ_E^×, 𝒞_E^× (p4) | D1, block form Eq 12–14 | DEF | — | block-Gram derivation Eq 13 from HH† = H†H = 6I₆ is MECH-checkable |
| D10 | Def 10: finite-dilation corner: ℬ_E^× and 𝒞_E^× nonempty and finite (pp4–5) | D9 | DEF | — | |
| D11 | Def 11: total finite-corner atlas 𝒜₆^fc = classes of all retained outputs over all seeds (p6) | D10, branch-complete procedure (Sec III C, Eqs 17–19) | DEF | — | the five-step procedure is definitional; division-free claim is a property argued at P24/S3 |
| P12 | Prop 12: every matrix retained by the procedure is CHM (p6; proof p27) | S3, D11 | ARG | unverified | one-paragraph glue; all substance in S3 (MECH) |
| P13 | Prop 13: infinite-fiber trichotomy: invertible X ∈ 𝕋^{3×3} with infinite normalized row-Gram fiber ⇒ XX† = 3I₃ ∨ Re τ_r(X) < 0 ∨ X has 2×2 Hadamard submatrix (p7; proof pp17–23) | S2 | ARG | unverified | **largest unaided argument in the paper** (~7 pp: dependent branch; nondependent s=0, 0<s<1, 1≤s≤3 common-root repair). Embedded polynomial identities (S.1.20, S.1.26–S.1.31, S.1.37–S.1.45, S.1.58–S.1.69, S.1.75–S.1.80) MECH-checkable; branch-exhaustiveness is the risk |
| P14 | Prop 14: [H] ∉ 𝒦₆⁽³⁾ ⇒ all four blocks order-3 Hadamard, or some permutation+dephasing produces a finite-corner witness (p7; proof pp23–24) | P13, S1, L8, P7(1) | ARG | unverified | three-minus-sign identities S.1.86–S.1.88 MECH-checkable |
| P15 | Prop 15: one order-3 Hadamard block ⇒ H ∼ S₆⁽⁰⁾ or [H] ∈ 𝒦₆⁽³⁾ (p7; proof pp24–26) | U1, P7(2), D4 | ARG | unverified | Fourier-autocorrelation algebra S.1.91–S.1.108 MECH-checkable |
| P16 | Prop 16: no finite-corner witness ⇒ [H] ∈ 𝒦₆⁽³⁾ ∪ 𝒯₆ (p8; proof p26) | P13, P14, P15, L8, P7(1) | ARG | unverified | assembly; the routing funnel of the whole classification |
| P17 | Prop 17: every class in 𝒦₆⁽³⁾ has a finite-corner witness; 𝒦₆⁽³⁾ ⊂ 𝒜₆^fc (p8; proof pp28–30) | P7(1), S4, Karlsson parametrization (import), exact certificates | ARG | unverified | IMPORT edge: Karlsson chart + Möbius relations S.1.117–S.1.128 [26,27]. MECH core: 245 pairwise resultants → 25 first-phase conditions → 18 branches (S.1.119); Bernstein 10-box dyadic positivity for R (p30, Sec II J b). Kernel-checked per p49 in repo Lean modules (KarlssonResidualCertificate / KarlssonWitnessResultants / FourierSeamCertificate) |
| P18 | Prop 18: leading corner of S₆⁽⁰⁾ is a finite-corner witness; 𝒯₆ ⊂ 𝒜₆^fc (p8; proof p30) | P13, D5 | MECH | unverified | exact ℤ[ω] arithmetic given P13: det E = 3ω, (BB†)₁₂ = ω−1 ≠ 0, (BB†)₂₃ = 0, cross ratios cubic ⇒ no 2×2 submatrix |
| C19 | Cor 19: 𝒜₆^fc = ℋ₆ — the procedure is sound and exhaustive (p8; proof p31) | T6, P12, S3 | ARG | unverified | assembly; inside Lean-audit scope; this + C26 is the claim being adjudicated |
| D20 | Def 20: product-regular lift (11 guards, canonical form Eq. S.2.67 p42; Eq 63 / S.2.26 p35) (p9; recalled p35, p42) | Sec II B machinery (S.2.16–S.2.24) | DEF | — | eleven guards: det E, det B(det B)#, det C(det C)#, c₆h, c₆v, δh, δv, Disc qh, Disc qv, Rh, Rv |
| T21 | Thm 21: product-regular lift physical ⟺ ω_n ≤ 0; two sheets for ω_n < 0 coalescing at 0; forced block unimodular (p10; proof p36) | S7, S8, S9, S11, Haagerup decomposition (import) | ARG | unverified | IMPORT edge: Haagerup–Szöllősi two-phase decomposition [23, pp296–322; 24]; outside Lean audit |
| T22 | Thm 22: exact product-regular reach: ℋ₆ \ 𝒫₆ = 𝒯₆ ∪̇ {[H_×]} (p11; proof pp44–46) | P13, P7, S16, S17, S18, S19, U5 | ARG | unverified | counting argument N_dep ≥ 100 (S.2.95) vs ≤ 80 (S.2.100). MECH cores: 12² = 144 pairings at zero endpoint, 24 S₆-orbits, exact rational elimination (20 force q = 9/5), 4×4 Gram positivity; six exact checkers in repo (Sec II J c). Outside Lean audit. Feeds C26 via P25 |
| D23 | Def 23: G₆⁽⁴⁾ ≔ non-Karlsson, non-Tao classes returned by Steps 1–8 of Szöllősi's Construction 3.1, incl. Case 2 common-root branch, excl. identically-vanishing failure case (p12; defnitional passage 41; recalled p48) | [24] | IMPORT | unverified | fidelity to Construction 3.1 / Thm 4.1 / Remarks 4.2–4.3 of [24] is the entire check; definition drift here would hollow out C26 |
| P24 | Prop 24: at every product-regular corner, Construction 3.1 and the branch-complete procedure produce the same candidates and completions (p12; proof p48) | D20, D23 | ARG | unverified | reversibility-of-elimination argument, short |
| P25 | Prop 25: G₆⁽⁴⁾ = 𝒜₆^fc \ (𝒦₆⁽³⁾ ∪ 𝒯₆) (p12; proof pp48–49) | S15, T22, P24 | ARG | unverified | forward = S15; reverse = T22 + P24 |
| C26 | Cor 26: ℋ₆ = G₆⁽⁴⁾ ∪ 𝒦₆⁽³⁾ ∪ 𝒯₆, pairwise disjoint — Szöllősi's Conjecture 4.2 (journal; v1: 4.4) (p12; proof p49) | C19, P25 | ARG | unverified | disjointness via cross-ratio check (trivial-MECH: Tao cross ratios cubic, H₂ needs −1) |

## Supplement-only nodes (prefix S) and unnumbered claims (U)

| id | statement (short) | depends | bucket | status | notes |
|---|---|---|---|---|---|
| S1 | Lemma S.1: Re τ_r(X) = Re τ_c(X) for all X ∈ 𝕋^{3×3} (p16) | — | MECH | unverified | trace/determinant identity (S.1.8–S.1.11), sympy-checkable |
| S2 | Def S.2: normalized fixed-Gram fiber ℱ(S,T,R) (p17) | — | DEF | — | |
| S3 | Prop S.3: direct finite completion: invertible-block completions = ℬ_E × 𝒞_E pairs with forced D = −CE†(B⁻¹)†; Hadamard ⟺ D entrywise unimodular (p27) | D9 | MECH | unverified | identity chain S.1.110–S.1.114; deliberately *reproves* Szöllősi's fixed-corner criterion — import avoided |
| S4 | Lemma S.4: nonzero oriented leading coefficients of both fundamental sextics ⇒ side fiber finite; + invertible actual blocks ⇒ finite-corner witness (pp27–28) | D9, sextic definition (Eq 53 / S.2.18–S.2.20) | ARG | unverified | short finiteness logic. Uses Sec II B formalism inside Sec I — not circular (II B is definitional/identity-level, independent of T6), but the cross-reference is worth flagging |
| S5 | Lemma S.5: exact fixed-Gram presentation: the six incidence equations ⟺ Gram form S.2.7; S₃-action only relabels (p32) | S.2.3 definitions | MECH | unverified | identity + trivial division-legitimacy glue |
| S6 | Prop S.6: physical soundness and completeness at one corner: 𝒴_E reconstructions = completed-procedure outputs at E (statement p33, proof) | S5, S3, D10 | ARG | unverified | assembly |
| S7 | Lemma S.7: product-factor identities: Φ_fund = c₆ q_{s,u} q_{s,v}; u+v = −c₃/((1+ss^#)c₆), uv = c₀/c₆ (statement and proof p35; defining machinery S.2.16-S.2.24 p34) | S.2.16–S.2.24 | MECH | unverified | exact polynomial expansion both directions |
| S8 | Lemma S.8: complement positivity: regularity guards + ω_n(G) ≤ 0 ⇒ G = 6I₃ − EE† > 0 (pp35–36) | exact reduction S.2.28–S.2.31 | ARG | unverified | the ω_n(G) reduction and det G = 27 − 3p + J identities MECH-checkable; Zariski-density + continuity + Sylvester steps are ARG |
| S9 | Lemma S.9: the product-regular guards cover every denominator used in reconstruction/matching/flatness (p36) | D20, S7 | ARG | unverified | |
| S10 | Prop S.10: generic cover nonsplit: discriminant of S.2.24 not a square in ℚ(a,b,c,d) (p37) | S.2.24 | MECH | unverified | exact specialization (b,c,d) = (2,3,5); degree-8 integer P(a); gcd(P,P′) = 1 scriptable; one-line unique-factorization glue |
| S11 | Prop S.11: generic lower-block flatness: with sheet matching S.2.41, the formal block satisfies all nine flatness equations identically in the function field (pp37–38) | S10, Bondal–Zhdanovskiy (import), Hardt triviality (import) | ARG | unverified | IMPORTS [29] Thms 17 & 22 and [41]; exact specialization (a,b,c,d) = (2,3,5,7) MECH-checkable. Authors state it is post-classification — not used by T6 (p37); used by T21 |
| S12 | Cor S.12: boundary routing: positive-dimensional physical fiber with invertible candidate ⇒ complementary finite corner ∨ H₂-reducible ∨ Tao (pp39–40) | P13, P14, P15, P7(1) | ARG | unverified | boundary identities S.2.47–S.2.53 MECH-checkable; downstream of classification (feeds S14 context, not T6) |
| S13 | Lemma S.13: cross-ratio pivot normalization 𝒟 invariant under diagonal scalings (p40) | — | MECH | unverified | trivial |
| S14 | Thm S.14: global physical incidence cover: 𝒜₆^fc = union over 400 (I,J) of tagged presentations; transitions Laurent-rational (p40) | S6, T6, S13 | ARG | unverified | assembly |
| S15 | Prop S.15: published output retained: G₆⁽⁴⁾ ⊆ 𝒜₆^fc \ (𝒦₆⁽³⁾ ∪ 𝒯₆) (p42) | D23, D11 | ARG | unverified | procedure-comparison argument |
| S16 | Prop S.16: product-exceptional Karlsson class: 𝒦₆⁽³⁾ \ 𝒫₆ = {[H_×]} (p42) | P7(1), Karlsson parametrization (import), Matszangosz–Szöllősi (import), exact certificates, U5 | ARG | unverified | MECH core: H_× H_×† = 6I₆; 400-corner determinant-norm census (120,120,80,80); all 14,400 frames fail a resultant guard; repo checker `karlsson_product_exceptional_theorem_check.py`. Reverse: 49-case pair analysis + IMPORT [31] + exact divisor calculation |
| S17 | Prop S.17: Tao is product exceptional: 𝒯₆ ∩ 𝒫₆ = ∅ (p43) | D5, D20, U5| MECH | unverified | exact all-frame enumeration in ℤ[ω]/(ω²+ω+1): 14,400 frames; 12,960 / 5,760 counts; repeated coordinate ⇒ cubic not simple |
| S18 | Lemma S.18: two-sided badness dispatcher: both actual sides directionally bad ⇒ H₂-reducible or order-3 Hadamard block (pp43–44) | P7(1), P15, U4 | ARG | unverified | complete case split; exact certificate leaves S.2.72–S.2.81 (Cayley substitution, discriminants) MECH-checkable |
| S19 | Cor S.19: surviving block-polarized normal form E_M(a,b); 2θ = q(3−q) > 0 (p44) | S18 | ARG | unverified | substitution identities S.2.84–S.2.85 MECH-checkable |
| S20 | Lemma S.20: four-circulant-block matrices have a monomial automorphism with (3,3)-cycle row/column parts (p47) | — | ARG | unverified | short conjugation argument; used only by the numerical sidebar (Table I witnesses) |
| U1 | (unnumbered, p24) every order-3 CHM ∼ F₃ | — | MECH | unverified | 1 + x + y = 0 on 𝕋 forces {1, ω, ω²} up to phase/permutation; used by P15 |
| U2 | (unnumbered, p46) intrinsic Karlsson characterization: [H] ∈ 𝒦₆⁽³⁾ ⟺ −1 ∈ Λ(H); 𝒦₆⁽³⁾ ⊊ 𝒜₆^fc | P7(1), C19 | ARG | unverified | downstream only; nothing depends on it |
| U3 | (unnumbered, p41) dim_ℝ(𝒦₆⁽³⁾ ∩ 𝒜₆,reg^fc) ≥ 2 via exact nonvanishing witness at z₁=(3+4i)/5, z₂=(5+12i)/13 | S.2.60–S.2.64 | MECH | unverified | authors note Prop 17 proves the full three-parameter containment — illustrative, downstream only |
| U4 | (unnumbered, p43) directional-badness characterization: at a finite corner a product-regular frame exists exactly when the actual horizontal side is row-good and the actual vertical side is column-good; defines γ_ij, Good_r, Good_c, "directionally bad" | D20, D10 | ARG | unverified | four-sentence justification for an iff; S18's statement is phrased entirely in these terms and has no meaning without it. Unnumbered, and outside the Lean audit along with S18 |
| U5 | (unnumbered, p42) equivalence-invariance of product-regularity: row/column permutations act bijectively on the 400 corners and 14,400 frames, so existence of a product-regular frame is invariant under standard equivalence — licensing the class-level definition 𝒫₆ (S.2.68) | — | ARG | unverified | one-sentence justification; well-definedness of 𝒫₆, which S16, S17 and T22 all quantify over |

## Load-bearing step

> **Provisional — from DAG extraction only; no verification performed.**
For the classification claim (T6 + C19): every route passes through the funnel
P16 = {P13, P14, P15}, and both halves of P7 sit under it (P7(1) under P14/P16/P17,
P7(2) under P15). The largest unaided argument is **P13, the infinite-fiber
trichotomy (pp17–23)** — seven pages of branch analysis whose risk is
case-exhaustiveness, not any single identity.

The paper ships a companion Lean 4 audit claimed (p31) to mechanize the entire
T6/C19 chain. Note (V1-8): p31 states the public theorem keeps two arguments
visible — the cubic-root criterion, and the *concrete raw-or-seam form* of
Karlsson's parametrization ("every H₂-reducible Hadamard has either a canonical
Karlsson-coordinate presentation or an affine-Fourier seam presentation"). The
paper asserts these "are precisely the two published inputs of Proposition 7";
that is the paper's claim, not a reader-verifiable one. The second hypothesis is
weaker than P7(1) in direction (forward only, not the iff) and different in form
(a two-case concrete normal form, not family membership). So if the artifact
checks out (exists, compiles, no sorry/admit, axioms as claimed), the
classification's residual trust collapses to **three** checks, not two:
**P7(2) citation fidelity + the raw-or-seam form's fidelity to [26,27] +
Lean statement fidelity to C19**. The third is a Lean question; the second is a
citation-fidelity question about Karlsson.
The headline claim as usually quoted (C26, Szöllősi's conjecture / "the three
sectors exhaust ℋ₆") additionally rests on **D23's fidelity to Szöllősi's
Construction 3.1**, on **T22 ← {S16, S17, S18}** including the N_dep ≥ 100
vs ≤ 80 counting argument, and on **U4** (p43, unnumbered) — the
directional-badness iff that S18's statement is phrased entirely in terms of —
all **outside** the Lean audit(repo Python certificates only).

## Bucket counts
Recorded on day one; revised 2026-08-26 per V1-9, V1-2, V1-13 (day-one figures: 48 rows = 40 claim nodes, MECH 11, ARG 27, ARG ≈ 68 %). Current: 51 rows = 43 claim nodes + 8 DEF
rows (D1, D2, D4, D9, D10, D11, D20, S2; excluded from counts).
- MECH: **12** — D3, D5, P18, S1, S3, S5, S7, S10, S13, S17, U1, U3
- IMPORT: **2** — P7, D23 (import *edges* additionally enter P17, T21, T22-via-S16, S11, S16)
- ARG: **29** — T6, L8, P12, P13, P14, P15, P16, P17, C19, T21, T22, P24, P25, C26, S4, S6, S8, S9, S11, S12, S14, S15, S16, S18, S19, S20, U2, U4, U5
ARG ≈ 67 % of claim nodes. Per README pre-commitment: this does not renegotiate
the deliverable — the DAG plus a localization is the full deliverable. Note the
asymmetry: many ARG nodes are thin assembly shells (T6, P12, P16, C19, S6, S14)
whose substance is MECH-checkable identity work; the *genuinely* argumentative
mass is concentrated in P13, S8, S11, S18, U4, and the T22 counting argument.

## External imports to verify
| cited as | source | used by | says what is attributed? | checked |
|---|---|---|---|---|
| Karlsson complete 3-param family = H₂-reducible classification (P7(1)) | [26] LAA 434:239 (2011); [27] LAA 434:247 (2011); cross-cited [24] Thm 2.11 (journal) / Thm 2.12 (arXiv v1) | P7(1) → P14, P16, P17, S12, S16, S18, U2 | | ☐ |
| Szöllősi cubic-root row+column criterion (P7(2)) | [24] JLMS 85:616 (2012), p.624 Lemma 2.14 (journal) / Lemma 2.15 (arXiv:1008.0632 v1) | P7(2) → P15, T22 | | ☐ |
| Karlsson explicit parametrization + Möbius relations | [26, 27] (as transcribed in S.1.117–S.1.128) | P17, S16 | | ☐ |
| Szöllősi Construction 3.1, Thm 4.1, Remarks 4.2–4.3, Conjecture 4.2 (v1: 4.4) | [24] | D23, P24, S15, C26 | | ☐ |
| Haagerup two-phase decomposition | [23] Haagerup 1997, pp296–322 (also [24]) | T21 | | ☐ |
| Bondal–Zhdanovskiy Thms 17 & 22 | [29] J. Math. Sci. 216:23 (2016) | S11 → T21 | | ☐ |
| Semialgebraic Hardt triviality | [41] Basu–Pollack–Roy, Algorithms in Real Algebraic Geometry | S11 | | ☐ |
| Matszangosz–Szöllősi routing theorem | [31] Des. Codes Cryptogr. 92:4313 (2024) | S16 → T22 | | ☐ |
| Tao's matrix S₆⁽⁰⁾ | [28] MRL 11:251 (2004) | D5 | | ☐ |
| Companion artifacts: Lean 4 audit (`Hadamard6/PaperTheorem.lean`; claimed: no sorry/admit/project axiom, only propext + Classical.choice + Quot.sound) + certificate directory (`certificates/PAPER_CLAIM_AUDIT.md`, `certificates/verify.py` SHA-256-manifested, Karlsson/Fourier Lean certificate modules, `karlsson_product_exceptional_theorem_check.py`) | [36] github.com/mateocardeneswuttig/all_hadamard_matrices_in_dimension_six | Lean side: T6/C19 chain; certificate side: P17, T22, S16, S17 | | ☐ |

Notes:
- The scaffold's "Tao S₆ isolated" import row is retired: **isolation is never
  used anywhere in the proof** — only the matrix itself (Hadamardness is MECH).
  [28] remains listed for provenance of the matrix.
- Farouki [45] (Bernstein basis) is background only: the dyadic de Casteljau
  subdivision actually used is exact-rational and self-contained.
- Szöllősi's fixed-corner completeness criterion is deliberately **not**
  imported — the paper reproves it as S3.

## Outside the DAG

- **Table I (p48)**: 256-bit Arb interval numerics for one representative
  ramification seed (Cayley seed over the degree-7 P(ξ), Eq S.2.108). The
  paper's only numerics. Authors state: "No classification or product-coverage
  result depends on these numerical comparisons." The DAG confirms: no node
  cites it. Status NUMERICAL, non-load-bearing; uses S20 for the 1600
  automorphism witnesses.
- Fig. 1 (p3) = T6 proof architecture (matches the edges extracted here);
  Fig. 2 (p10) illustrative; Sec II H a (ramification seed), Sec II K (scope
  remarks: nonsplit ≠ nonrational, product-regular theorem one-sided), Sec VI
  (outlook, MUB-6 remarks — ledger territory): no proof obligations.
- p13 discloses LLM-assisted development (ChatGPT Sol 5.6 Pro, Codex 5.6 Sol,
  Claude Opus 5.0) with author verification claims; p31 scopes the Lean audit.
  Ledger facts, not DAG nodes.
- Open per the paper itself (p11): whether ℛ_{6,prod} intersects the remaining
  Karlsson classes — explicitly left undetermined; not part of the claim.
