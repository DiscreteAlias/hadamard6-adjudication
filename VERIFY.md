# VERIFY.md — DAG verification protocol `[D]`

The DAG is now the schedule for the rest of the week. Everything downstream
allocates against it. This is what it takes to trust it.

**Governing principle: the verifier is never the extractor.** A session that
built the DAG will confirm the DAG. Every fidelity pass below runs in a fresh
session, and V2 runs on a different model. This is the same decorrelation
argument that makes Track B blind, applied to Track A's own output.

**Evidence standard: every pass emits an artifact.** "I checked, it's fine" is
worth nothing. Each pass appends to `verification/` and the result is committed
whether it passes or fails.

---

## V0 — Structural (scripted, no paper)

```bash
python3 checks/dag_audit.py dag.md --pages 50 --target C26 --audited C19
```

Covers: duplicate ids, dangling edges, cycles, bucket arithmetic, dense-counter
completeness, dependency cone, orphans, audit gap, page coverage.

Dense counters make **numbered** completeness self-certifying — a missing Prop
would show as a hole in 1–26. Nothing else here needs a human.

Run it on every commit touching `dag.md`. Never transcribe the cone by hand.

---

## V1 — Fidelity audit (fresh session, adversarial framing)

Not "check these rows." **"Find me a wrong row."** Confirmatory framing produces
confirmation; that is the whole lesson of Track B.

> You are auditing `dag.md`, extracted from `paper/2608.18053v1.pdf` by a
> different session. Assume it contains errors. Your job is to find them.
>
> For every node in the C26 dependency cone (34 of 48 — `dag_audit.py` prints
> the list), open the cited pages and check three things independently:
> (a) the numbered result exists where claimed;
> (b) the short statement is a faithful compression, not a plausible-sounding
>     paraphrase that shifts a quantifier or drops a hypothesis;
> (c) the proof invokes **exactly** the listed dependencies — flag both edges
>     that aren't used and dependencies used but not listed.
>
> Missing edges matter more than spurious ones. Report every discrepancy to
> `verification/v1-fidelity.md` with page and quote. Do not edit `dag.md`.

Then, unassisted and by eye, confirm Fig. 1 (p3) shows T6 resting on exactly
{P16, P17, P18}, and that p31's dependency summary matches the extracted chain.
The paper's own architecture claims are an independent source; use them.

---

## V2 — Blind re-extraction (different model, never sees dag.md)

The strongest evidence available. Two independent extractions agreeing is real
evidence. One extraction plus a self-check is not.

```bash
mkdir -p verification/blind && cp paper/*.pdf verification/blind/
cd verification/blind && claude --model opus     # extraction was fable
```

> Read this paper and build a claim DAG: one row per numbered result, its
> dependencies, and a MECH / IMPORT / ARG classification. Write `dag-blind.md`.
> Do not look outside this directory.

Then diff:

```bash
python3 checks/dag_audit.py verification/blind/dag-blind.md --pages 50 --target C26
diff <(cut -d'|' -f2,4,5 dag.md) <(cut -d'|' -f2,4,5 verification/blind/dag-blind.md)
```

Disagreements localize exactly where extraction is unreliable. Expect bucket
disagreements on hybrid nodes — those are informative, not failures. Edge
disagreements inside the C26 cone are serious.

Cost is a full re-read. That is the price of "must be correct."

---

## V3 — Omission sweep (the failure nothing else catches)

Dense counters certify that no *numbered* result is missing. They say nothing
about unnumbered load-bearing steps. The DAG currently has two (U1, U2); a third
would be invisible to V0 and easy to miss in V1.

Two handles:

**Page gaps.** `dag_audit.py` reports pages no node claims. Current output:
**pp 1, 34, 41, 50.** Pages 34 and 41 sit inside the supplemental proofs —
between S6 (p33) and S7 (p35), and between S14 (p40) and S15 (p42). Read both.
Either the DAG's page citations are imprecise (a proof spanning pp33–35 cited
as p33), or there is unmodeled content there. Resolve which.

**Targeted proof reading.** For P13, S18 and T22 — the three genuinely
argumentative nodes in the cone — read the proofs hunting only for steps that
carry weight and have no number. Anything found becomes U3, U4, … and V0 reruns.

---

## V4 — Downstream cross-check

The Lean audit is claimed to mechanize the C19 chain. If it does, and its
theorem statement is faithful, that independently corroborates the DAG's account
of what C19 depends on. Disagreement between the Lean dependency structure and
`dag.md` is evidence about both.

This overlaps the real adjudication; do it once V1–V3 are clean.

---

## Sign-off

The DAG is trusted when: V0 passes, V1 finds no unexplained discrepancy inside
the cone, V2 agrees on cone membership and on every edge among the load-bearing
nodes, and V3's page gaps are resolved.

Record the verdict in `verification/README.md` and commit. If V2 disagrees
materially, **both** DAGs are suspect and the disagreement is the finding —
do not adopt one and discard the other.
