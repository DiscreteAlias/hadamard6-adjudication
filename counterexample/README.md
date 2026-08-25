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

| candidate | hadamard? | defect | haagerup novel? | disposition |
|---|---|---|---|---|
| | | | | |
