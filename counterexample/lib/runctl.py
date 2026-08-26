"""Run recording and exit-code convention. Track B.

Exit codes (uniform across search scripts):
  0  stratum exhausted, negative result (nothing new)
 10  NOVEL-pending-review candidate emitted -- halt and review
 20  exhausted, but unresolved-G6 survivors remain
  3  budget stop (frontier logged; incomplete)
  4  internal error / selftest failure
  5  precondition failure (e.g. G6^(4) transcription gate)

Timestamps are for provenance only; no timing value ever feeds a verdict.
"""

import subprocess
import time
from datetime import datetime, timezone

from .ledger import regenerate
from .serialize import RUNS, jsonl_append

EXIT_NEGATIVE = 0
EXIT_NOVEL = 10
EXIT_UNRESOLVED_G6 = 20
EXIT_BUDGET = 3
EXIT_INTERNAL = 4
EXIT_PRECONDITION = 5


def code_hash():
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or "nogit"
    except Exception:
        return "nogit"


class Run:
    def __init__(self, script, args=""):
        self.script = script
        self.args = args
        self.t0 = time.monotonic()

    def finish(self, summary, exit_code):
        rec = {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "script": self.script,
            "args": self.args,
            "code": code_hash(),
            "summary": summary,
            "exit": exit_code,
            "wall_s": int(time.monotonic() - self.t0),
        }
        jsonl_append(RUNS, rec)
        regenerate()
        return exit_code
