# checks/ `[D]`

One script per MECH node. Named for the node: `t3_2.py` checks Theorem 3.2.

**Contract**
- exit 0 — verified exactly
- exit 1 — refuted, with the residual printed
- exit 2 — could not be reduced to exact computation; reclassify the node as ARG

**Before pointing any script at the paper**, run it against ground truth:
F₆ has defect 4, Tao's S₆ has defect 0, and the two are inequivalent. A script
that cannot reproduce those is not evidence about anything.

No floating point. If a computation seems to need it, the node is ARG.
