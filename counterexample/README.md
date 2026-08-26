# Track B — counterexample search `[D]`

**Do not open `../paper/`.** Not a formality. Proof-checking rewards agreement;
an agent that has read the argument will find it convincing. Track B's ignorance
is the instrument.

## The one job

Produce a 6×6 complex Hadamard matrix, exactly verified, whose Haagerup set does
not appear in the claimed list.

That is a finite certificate. A hit is self-verifying and settles the question.
A miss is informative too — record *where* the search stalled.

## Discriminator

`haagerup(H)` from `../checks/lib/hadamard.py`. Different Haagerup sets ⟹
inequivalent. The converse fails: equal sets do **not** imply equivalence.

Cross-check survivors against the Tadej–Życzkowski catalogue and the defect
stratification (generic families at defect 4; isolated points at 0).

## Log

<!-- ledger:begin -->
| candidate | hadamard? | defect | haagerup novel? | disposition |
|---|---|---|---|---|
| A.q3.c0 | True | 0 | no (== S6) | closed:equivalent-S6 (variant id, cert verified) |
| A.q4.c0 | True | 4 | no (== D6(0/4)) | closed:member-D6(0/4) (variant id, cert verified) |
| A.q6.c0 | True | 4 | no (== F6) | closed:equivalent-F6 (variant id, cert verified) |
| A.q6.c1 | True | 4 | no (== F6(0/6,1/6)) | closed:member-F6(0/6,1/6) (variant T, cert verified) |
| A.q6.c2 | True | 4 | no (== F6(0/6,1/6)) | closed:member-F6(0/6,1/6) (variant id, cert verified) |
| A.q6.c3 | True | 0 | no (== S6) | closed:equivalent-S6 (variant id, cert verified) |
| E.twotriangle.stratum | 1536/1536 | 0 (S6 class) | no — every solution's set is {1, ω, ω²} | closed: stratum exhausted (1488 leaves, all 0-dim; 1536 solutions, every one certified equivalent-S6; 3 stalled leaves resolved via quadratic-fiber extraction) |
| G6.generic-point | True | computing (exact bracket) | n/a (reference point, not a candidate) | reference: Szollosi 1008.0632v1 explicit generic point, Hadamard fully certified (36+15 NF-zero residuals); transcription audit 16/16 |
<!-- ledger:end -->

## Runs

<!-- runs:begin -->
- `2026-08-26T01:02:09Z` `searches/a_butson.py` q=2..6 — q=2: raw 0, classes 0; q=3: raw 12, classes 1; q=4: raw 72, classes 1; q=5: raw 0, classes 0; q=6: raw 312, classes 4 (exit 0, 59s)
- `2026-08-26T02:43:47Z` `searches/e_twotriangle.py` budget=12.0m — nodes 743, pruned 289, leaves 705 (0-dim 342, pos-dim 74) — exhaustive (exit 0, 183s)
- `2026-08-26T06:16:33Z` `searches/e_twotriangle.py` budget=600.0m — nodes 22064, pruned 18398, leaves 12773 (0-dim 1488, pos-dim 0) — exhaustive (exit 0, 12746s)
- `2026-08-26T06:57:15Z` `searches/e_close.py` budget=240.0m — 0 leaves closed wholesale (K6), 1488 survivors (exit 0, 2410s)
- `2026-08-26T06:59:00Z` `searches/e_extract.py` budget=30.0m — leaves 12, solutions 12, K6-closed 0, -1-free 12, stalls 0, BUDGET STOP (exit 3, 12s)
- `2026-08-26T07:02:35Z` `searches/e_extract.py` budget=30.0m — leaves 15, solutions 15, K6-closed 0, RU-free 15, open/noncyclotomic 0, stalls 0, BUDGET STOP (exit 3, 63s)
- `2026-08-26T07:26:15Z` `searches/e_extract.py` budget=480.0m — leaves 1488, solutions 1530, K6-closed 0, RU-free 1530, open/noncyclotomic 0, stalls 3 — complete (exit 0, 1402s)
<!-- runs:end -->
