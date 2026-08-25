# Hadamard-6 Adjudication `[D]`

Adjudication of **arXiv:2608.18053**, "A Complete Classification of Complex
Hadamard Matrices of Order Six" (Aug 2026, unrefereed, <90 days at intake).

Not a Cupel program. No gate ladder, no phases, no kill conditions. One claim,
one week, one sealed verdict. If a gate definition appears in this directory,
the task has been left.

---

## What counts as success

**A localization, not a verdict.**

"Complete classification up to equivalence" is quantified over everything. There
is no certificate that establishes it, and no week of work will produce one. The
deliverable is:

- the claim DAG,
- the set of nodes mechanically verified in exact arithmetic,
- the single step everything rests on, named,
- the residual risk, stated.

Decided in advance, on the record: **if the argumentative bucket turns out to be
most of the paper, the DAG plus a localization is the full deliverable and the
week succeeded.** This line exists so it cannot be renegotiated on day five.

## What would falsify the paper

One 6×6 complex Hadamard matrix, exactly verified, whose Haagerup set does not
appear in the claimed list. That is a finite certificate and it is
self-verifying. It is the only outcome here that is cheap to check.

---

## Two tracks

**Track A — read the paper.** Extract the DAG, classify every node, verify what
is mechanical, check what is imported.

**Track B — never read the paper.** Search for a counterexample. Track B does
not open `paper/`. This is not a formality: proof-checking rewards agreement,
and a model that has read the argument will find it convincing. Track B's
ignorance is the point.

Run Track B as a **separate session with cwd = `counterexample/`**. A note in a
README does not isolate an agent that has been handed the repo root.

---

## Three buckets

| bucket | meaning | who checks |
|---|---|---|
| `MECH` | reduces to exact finite computation | scripted, `checks/` |
| `IMPORT` | asserted from another paper | citation fidelity check |
| `ARG` | genuine mathematical argument | you, unaided |

Record the proportions on day one. `IMPORT` is where errors hide and is the
cheapest bucket to clear.

---

## Rules

1. **No floating point.** Ever.
2. **One script per node.** Exit code is the verdict.
3. **Ground truth first.** F₆ defect 4, S₆ defect 0, before anything else.
4. **Seal either way.** A negative week produces a ledger entry, not silence.

## Running

```bash
python3 checks/lib/hadamard.py     # exits nonzero if the harness is broken
```
