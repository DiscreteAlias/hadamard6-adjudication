---
title: Where does the machine-checked part stop?
project: hadamard6
kind: result
published: 2026-08-29
workPeriod: 2026-08-22 to 2026-08-29
tier: 1
access: public
summary: A protocol for adjudicating partially formalized proofs, its output on a fifty-page unrefereed claim, and its own error rate.
repo: https://github.com/DiscreteAlias/hadamard6-adjudication
---

A solo operator with a protocol can establish, in a week, exactly where a
fifty-page unrefereed mathematical claim's machine-checked core stops. This is
that protocol, its output on a real paper, and its own error rate.

It is not a claim about whether the paper is correct. I did not check that, and
nothing below should be read as evidence either way. What I checked is the
*shape* of the argument: which results depend on which, which of them the
companion proof assistant covers, and which it does not.

Everything is in a public repository: **[github.com/DiscreteAlias/hadamard6-adjudication](https://github.com/DiscreteAlias/hadamard6-adjudication)**.
Commits are linked throughout, including the ones where this went wrong.

---

## The problem

Formal verification has stopped being all-or-nothing. The normal case now is a
paper with a companion Lean or Rocq artifact covering *part* of its argument,
with the rest in prose. That is a good development and an honest one — authors
formalize the spine and say so. But it leaves the reader with a question nobody
has a procedure for: which part?

The usual answer is a paragraph. "The classification chain is formalized; the
construction-level comparison is not." True, and insufficient — a paragraph
doesn't tell you whether the unformalized remainder is a footnote or a
load-bearing third of the argument.

The field knows this is the pressure point. The Leiden Declaration on Artificial
Intelligence and Mathematics, published in June 2026 and endorsed by the
International Mathematical Union, puts verification and disclosure at the front
of its list. Two independent public registries now index AI-produced
mathematical results and grade each one *by how it was verified* — from
machine-checked through to disputed. The grading axis exists because production
has outrun adjudication, and everyone can see it.

As generation gets cheaper, the scarce good is not another result. It is a
repeatable way to say what a result establishes.

---

## The subject

**arXiv:2608.18053**, "A Complete Classification of Complex Hadamard Matrices of
Order Six" (Cárdenes Wuttig & Tindall), v1 dated 18 August 2026. Fifty pages.
Unrefereed, no venue, no DOI. LLM-assisted, per its own disclosure on p13. It
ships a companion Lean 4 audit.

I picked it because it was live, checkable, and nobody had looked at it. It was
seven days old when I started.

Before doing any work I wrote into the repository README that the deliverable was
a structural map and a localization — not a verdict — specifically so it could
not be renegotiated on day five when the argumentative content turned out to
dominate ([`0aaa1eb`](https://github.com/DiscreteAlias/hadamard6-adjudication/commit/0aaa1eb)).
It did dominate. The commitment held.

---

## The protocol

### The claim DAG

One row per numbered result: id, short statement, dependencies, bucket, status,
notes. Four buckets:

| bucket | meaning |
|---|---|
| `MECH` | reduces to an exact finite computation |
| `IMPORT` | asserted from another paper |
| `ARG` | a genuine mathematical argument |
| `DEF` | a definition; no proof obligation |

The proportions tell you what kind of week you are having before you have had it.
Final counts: 12 MECH, 2 IMPORT, 29 ARG, 8 DEF across 51 rows. Roughly two-thirds
argument.

Extraction was done by an agent reading the full paper. That output is an
*unverified input*, and treating it as ground truth would be the same error the
whole exercise exists to avoid. the fidelity pass and the error log below are about what it takes to trust it.

### The structural auditor

[`dag_audit.py`](https://github.com/DiscreteAlias/hadamard6-adjudication/blob/main/checks/dag_audit.py)
is paper-agnostic: give it the DAG, a page count, the headline node, and the
formalized node. It checks cycles, dangling edges, duplicate ids and bucket
arithmetic — and two things that are less obvious.

**Dense-counter completeness.** If a paper numbers its results on a shared
counter, *numbered* completeness is self-certifying: a missing result shows as a
hole in the sequence. Here the counters ran 1–26 in the main text and S.1–S.20 in
the supplement, both dense. That is a real guarantee obtained without reading
anything.

**Page coverage as an omission detector.** Dense counters say nothing about
*unnumbered* load-bearing steps — those have no counter to be missing from. The
handle is page citations: collect every row's, then ask which pages nobody
claims.

First run: pages 1, 34, 41 and 50. One and 50 were title and back matter.
Thirty-four and 41 were inside the supplemental proofs, and both mattered (below).

This is a cheap trick and it is the only mechanical purchase I know of on the
omission problem.

### The dependency cone

Given the headline claim, compute its ancestor set. Everything outside is not
load-bearing for it.

Here: 37 of 51 nodes. Outside sat fourteen, including a numbered Theorem that
nothing depends on, together with its entire five-node subtree.

This reorders the work. Five of the twelve MECH nodes turned out to be outside
the cone — verifying them would have produced certificates proving nothing about
the headline. The auditor prints that list explicitly, because the temptation is
always to verify what is easy rather than what is load-bearing.

### The audit gap

This is the piece I have not seen done elsewhere, and it is the reusable idea.

Given a paper with a *partial* formalization, compute the set difference between
the headline claim's dependency cone and the formalized theorem's cone.

That set is the answer to "where does the machine-checked part stop" — a list of
nodes with buckets attached, rather than a paragraph of hedging. It is mechanical
once the DAG exists, it updates when the DAG is corrected, and it can be diffed
across paper revisions.

It is also the number to watch while making corrections. Three times I predicted
what an edit would do to the gap, ran the auditor, and got a different number.
Each time the prediction was wrong for an instructive reason (below).

### Adversarial fidelity

Structural consistency is not fidelity. A confabulated DAG passes every check in
the structural checks — the rows cohere with each other; nothing checks them against the paper.

Two rules did the work.

**The verifier is never the extractor.** A session auditing its own output will
confirm it. The fidelity pass ran in a fresh session on a different model.

**Adversarial framing.** Not "check these rows" but *"find me a wrong row; assume
it contains errors."* Confirmatory framing produces confirmation. That is not a
capability limitation — it is what the task rewards, and you have to structure
against it.

The pass checked existence, statement fidelity, edge fidelity in both directions,
and page references across all rows, starting at the audit-gap nodes rather than
the top of the table. It returned fourteen findings and moved the gap from eleven
nodes to fourteen
([`819b966`](https://github.com/DiscreteAlias/hadamard6-adjudication/commit/819b966)).
Three of the four additions were dependencies no structural check could have
found — two unnumbered, one hidden inside a prose equation range.

### The Lean boundary check

The mechanical layer is nearly foolproof and produces artifacts. `lake build`.
`#print axioms` on every public endpoint against the standard known-consistent
whitelist — `propext`, `Classical.choice`, `Quot.sound`. Greps for `sorry`,
`admit`, project-level `axiom`, `opaque`, `unsafe`, `native_decide`.

What it does not buy is stated plainly in Lean's own documentation: the check is
meaningful only if one believes the formal theorem statement corresponds to its
intended informal meaning. **The kernel is silent on whether the theorem is the
theorem.** That is the whole job and the only part that can go wrong.

Two moves for it.

**Read the definitions before the theorem.** If the formal `IsHadamard` does not
mean what the paper's "complex Hadamard matrix" means, everything above it is
decoration. Definitions are where fidelity dies, and they are less fun to read.

**Check vacuity.** A theorem whose hypotheses nothing satisfies is true, compiles
cleanly, and means nothing. Test whether the formalization exhibits a concrete
inhabitant.

---

## What it found

### The Lean artifact does what it claims

First, because it is the most important finding and because saying it first is
what earns the right to say the rest.

Repository `f9ff024`, Mathlib v4.33.0-rc2. `lake build Hadamard6.PaperTheorem`
completes in 3496 jobs, exit 0. All nine public endpoints report exactly
`[propext, Classical.choice, Quot.sound]`. No `sorry`, `admit`, project axiom,
`opaque`, `unsafe`, or `native_decide` anywhere in source. Build log in the
repository.

The definitions hold up:

- `IsHadamard H` is `EntrywiseUnit H ∧ H * conjTranspose H = 6 • 1`, with
  `EntrywiseUnit` being `normSq (A i j) = 1`. The real condition, not a
  weakening.
- `InFiniteCornerAtlas H` unfolds to genuine existential corner structure with no
  `IsHadamard` smuggled in, so the classification iff is substantive in both
  directions. The authors flag this themselves, noting their proof ordering
  "prevents the output definition from doing any logical work in the witness
  theorem." They are right.
- Vacuity is closed: the Tao matrix is written out entry by entry and proved to
  satisfy the definition, so the classified type is inhabited.

This is a real formalization. Anyone can now cite that without reading 107
modules.

### Fourteen nodes past the kernel

The formalized chain ends at one node; the headline claim sits in a cone of 37,
of which fourteen lie outside it:

| bucket | count |
|---|---|
| ARG (unmechanized argument) | 10 |
| IMPORT | 1 |
| MECH | 2 |
| DEF | 1 |

**The authors disclose this.** Their `LEAN_ASSUMES_AND_PROVES.md` has a "Does not
prove" section listing six categories. The table above is that list at node
granularity — a sharper version of their own disclosure, not something they
concealed.

That is a smaller claim than "nobody has stated the gap," and it is the true one.
What the protocol adds is precision: six categories becomes fourteen named nodes
with buckets, updating mechanically as the map is corrected.

### Five dependencies the numbering does not expose

The part that is unambiguously new. Each is checkable in minutes with the PDF.

**A four-sentence iff with no number (p43).** Between one proof and the next
lemma sits a paragraph defining a "good" row pair and a "directionally bad"
orientation, concluding: *at a finite corner, a product-regular frame exists
exactly when the actual horizontal side is row-good and the actual vertical side
is column-good.* The following lemma's statement is phrased entirely in these
terms and cannot be read without it. That lemma is inside the audit gap.

**A one-sentence well-definedness argument (p42).** *"Consequently the existence
of a product-regular frame is invariant under standard equivalence."* That
sentence licenses a class-level definition which three separate results in the
gap quantify over. Without it, the object is not well-defined on equivalence
classes.

**A dependency hidden in prose.** A definition named its dependency as "Sec II B
machinery (S.2.16–S.2.24)". A lemma's entire statement *is* equations
S.2.23–S.2.24. A dependency written as an equation range instead of a node
reference is invisible to any cone computation — which is exactly why it went
unnoticed until the fidelity pass
([`da92e7a`](https://github.com/DiscreteAlias/hadamard6-adjudication/commit/da92e7a)).

**A definition whose content lives on an uncited page.** The passage
distinguishing the published construction's output from the paper's own completed
output sits on p41. The definition cites p12 and p48. It is the IMPORT node whose
fidelity to the cited construction decides the headline claim.

**A cross-reference pointing at the wrong equation.** A definition cites (S.2.26)
on p35 for its eleven guards; the canonical list is (S.2.67) on p42.

The pattern underneath all five: **the extraction recorded where results were
*stated*, not where their content *lived*.** Page coverage caught only the
instances leaving a whole page unclaimed. Narrower off-by-ones were invisible and
had to be read for.

### The hypothesis that is not the one on the page

The formalization takes two literature-facing hypotheses. The second, printed
from the build:

```
KarlssonRawOrSeamCoverage : ∀ (H : Mat6),
  IsHadamard H → HasHadamardTwoByTwo H →
    Nonempty (CanonicalKarlssonRawPresentation H) ∨ IsAffineFourierSeam H
```

The corresponding published input, in the paper's main text, is an **iff**
concluding in membership of a named three-parameter family. The Lean hypothesis
is a forward implication concluding in a two-case concrete presentation. Weaker
in direction, different in form.

The paper says on p31 that the two arguments "are precisely the two published
inputs." The repository's own documentation is more careful — it notes that the
second "is the concrete coordinate form" and that "its conclusion is not an
abstract family name."

Consequence: residual trust splits into three checks rather than two — citation
fidelity for the first input, fidelity of the concrete form to the cited
literature, and fidelity of the Lean statement to the paper's conclusion. The
third is discharged. The first two are not.

### The blind track

Running alongside, in a separate session that never opened the paper, the
dependency graph, or the repository's own README: a search for a 6×6 complex
Hadamard matrix inequivalent to everything in the known catalogue.

Blindness was structural, not promised — verified afterwards by git audit, and
the only breach was four files *written* into a shared directory, which teaches
the blind track nothing. Exact arithmetic throughout, no floating point, and a
verdict discipline where "known" always means an explicit equivalence certificate
re-verified by matrix multiplication, never an invariant match.

Result: **exit 0, certified negative**
([`62591c4`](https://github.com/DiscreteAlias/hadamard6-adjudication/commit/62591c4)).
Butson matrices exhaustive through order 6; one ansatz stratum exhausted
completely — 1,488 consistent leaves, 1,536 solutions, every one certified
equivalent to the known Tao matrix. Zero open candidates.

But the reason it earns its place here is what it did *before* searching.
Verifying its own tooling against known values, it found three defects in the
shared library — including an invariant whose equality test compared symbolic
*spellings* rather than numbers, which could have manufactured a false discovery
in the direction that matters most. It found them because it was not taking the
tooling on authority, and it was not taking it on authority because it had been
built to be independent.

**A blind track that finds nothing has still done work if it audits the
instrument on the way.**

---

## What the protocol got wrong

This is the section that makes the piece worth reading. All of it happened; all
of it is in the repository's history.

**A fabricated page span, committed and pushed.** A manual read recorded a proof
as spanning two pages — my own eyes on a screen — without checking the page
boundary. The second page was the opening of a new section. The span went into
the map and a note asserting it went into the verification record
([`79588b5`](https://github.com/DiscreteAlias/hadamard6-adjudication/commit/79588b5)).
The adversarial pass caught it by extracting the page boundary directly
([`c4e2d91`](https://github.com/DiscreteAlias/hadamard6-adjudication/commit/c4e2d91)),
which is the entire argument for making that pass independent.

**A template committed with its placeholders intact**
([`96e4e8d`](https://github.com/DiscreteAlias/hadamard6-adjudication/commit/96e4e8d)),
under a message asserting a finding. Reverted
([`ab2176d`](https://github.com/DiscreteAlias/hadamard6-adjudication/commit/ab2176d)).
Both commits remain in history, because a verification record that quietly
overwrites its own contamination is not a verification record.

**A node silently absent from the graph for a week.** A table row wrapped across
two physical lines. The parser did not match the first fragment (no trailing
pipe) and ignored the second (wrong leading cell), so both were discarded with no
diagnostic. Every count published before the repair ran on 47 rows rather than
48. The gap list happened to be unaffected — luck, not design.

The fix is worth reporting because my first attempt failed. I added a
column-count check; the red test still passed. A wrapped row never *reaches* a
column count. The defect was not a wrong check but a missing one: **every silent
`continue` in a parser is an unstated assumption that the skipped line does not
matter.** There were three, and one was load-bearing
([`49b5c85`](https://github.com/DiscreteAlias/hadamard6-adjudication/commit/49b5c85)).

**Three commits to land one dependency edge**
([`fa7c29b`](https://github.com/DiscreteAlias/hadamard6-adjudication/commit/fa7c29b),
[`54ba4eb`](https://github.com/DiscreteAlias/hadamard6-adjudication/commit/54ba4eb),
[`da92e7a`](https://github.com/DiscreteAlias/hadamard6-adjudication/commit/da92e7a)),
each with a message asserting a change that had not occurred.

**Eleven defects in the instrumentation**, logged as found. The worst was a
self-test that printed `MISMATCH` on failure and exited 0 regardless — so for
five days the bootstrap gate that was supposed to abort on a broken harness could
not fire. Two others were unsound predicates that could have produced a *false
refutation of the paper*: a Hadamard test collapsing "cannot decide" into
"false," and a rank computation resting on heuristic zero-testing
([`a2e38a7`](https://github.com/DiscreteAlias/hadamard6-adjudication/commit/a2e38a7)).

**The through-line, and the transferable finding: every one of these was caught by
a check contradicting a number someone had predicted out loud.** Not one was
caught by reading carefully. Predict the output before running the command; the
disagreements are where the information is.

---

## Scope — what was not done

Prominent rather than buried, because a finding is only as good as its stated
boundary.

- **No computational claim in the paper was verified.** The harness was built,
  debugged and red-tested; it was never pointed at the paper.
- **Nine of ten literature imports remain unchecked**, including both halves of
  the structural proposition every route passes through. The cited papers were
  never opened. This is the largest unverified thing in the exercise.
- **The IMPORT node's fidelity to its cited construction was not checked**,
  though it decides the headline claim.
- **The companion certificate directory was never run.**
- **A blind re-extraction of the DAG was planned and not performed.** The
  adversarial pass found no edge errors among the original gap nodes, so a second
  independent extraction was judged not worth a full re-read. A judgment, not a
  verification.

---

## What transfers

`dag_audit.py` is paper-agnostic today. The DAG format and four-bucket taxonomy
are general. The audit-gap computation applies to any paper with a partial
formalization.

The decorrelation discipline generalizes further than the graph work does. It
shows up three times here and paid every time: the fidelity pass on a different
model from the extractor, the blind search that never read the paper, and the red
test that breaks an anchor deliberately to confirm a check can fail. In each case
the value came from an instrument that could not be talked into agreeing.

Honest limits. This is n=1. Dense-counter completeness needs a shared numbering
counter; a paper numbering per-section gives nothing. Page coverage assumes
citations you can trust to a page — and the systematic defect found here was
precisely that citations recorded statement sites rather than content sites,
which degrades the check.

Two things I would do differently from the start. Red-test every assertion before
trusting it, because a check that cannot fail is worse than no check — you
believe it. And commit predicted numbers *before* running the command that
produces them.

The claim I am willing to defend is narrow. Not that this paper is right or
wrong. That the boundary of its machine-checked core is now a list of fourteen
named nodes rather than a paragraph, that five load-bearing steps its numbering
does not expose are now identified, and that the procedure producing both is
reusable and has a measured error rate.

---

## Disclosure

The five findings in the section on hidden dependencies, the p31 wording note in
the hypothesis section, and a smaller
section-range slip were sent to the corresponding author on 29 August 2026, ahead
of this write-up. No claims about correctness were made, then or here. Any
response will be recorded in the repository
([`a1888e5`](https://github.com/DiscreteAlias/hadamard6-adjudication/commit/a1888e5)).

The sealed verdict is at
[`slag/verdict.md`](https://github.com/DiscreteAlias/hadamard6-adjudication/blob/main/slag/verdict.md);
the full defect log at
[`slag/harness-defects.md`](https://github.com/DiscreteAlias/hadamard6-adjudication/blob/main/slag/harness-defects.md).

This write-up was drafted with AI assistance, as was the adjudication itself. So
was the paper it examines. That symmetry is worth stating rather than eliding.

---

*Julian Miller · [discretealias.dev](https://discretealias.dev)*
