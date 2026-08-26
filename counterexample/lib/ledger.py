"""README ledger regeneration. Track B.

The README's Log table and Runs section are regenerated between HTML-comment
markers from the append-only artifacts (candidates.jsonl / runs.jsonl), so a
crash can never corrupt history: re-running the regeneration is idempotent.
Existing prose outside the markers is preserved.
"""

from pathlib import Path

from .serialize import CANDIDATES, RUNS, ROOT, jsonl_load

README = ROOT / "README.md"

LB, LE = "<!-- ledger:begin -->", "<!-- ledger:end -->"
RB, RE = "<!-- runs:begin -->", "<!-- runs:end -->"

_HEADER = "| candidate | hadamard? | defect | haagerup novel? | disposition |"
_SEP = "|---|---|---|---|---|"


def _candidate_rows():
    # last artifact wins per candidate id (later gauntlet stages refine verdicts)
    latest = {}
    for c in jsonl_load(CANDIDATES):
        latest[c["id"]] = c
    rows = []
    for cid in sorted(latest):
        c = latest[cid]
        rows.append("| {id} | {had} | {defect} | {novel} | {disp} |".format(
            id=cid, had=c.get("hadamard", "?"), defect=c.get("defect", "?"),
            novel=c.get("haagerup_novel", "?"), disp=c.get("disposition", "open")))
    return rows


def _run_rows():
    rows = []
    for r in jsonl_load(RUNS):
        rows.append("- `{ts}` `{script}` {args} — {summary} (exit {exit}, {wall}s)".format(
            ts=r.get("ts", "?"), script=r.get("script", "?"),
            args=r.get("args", ""), summary=r.get("summary", ""),
            exit=r.get("exit", "?"), wall=r.get("wall_s", "?")))
    return rows


def _replace_block(text, begin, end, payload):
    if begin in text and end in text:
        pre, rest = text.split(begin, 1)
        _, post = rest.split(end, 1)
        return pre + begin + "\n" + payload + "\n" + end + post
    return text + f"\n{begin}\n{payload}\n{end}\n"


def regenerate():
    text = README.read_text()

    table = "\n".join([_HEADER, _SEP] + _candidate_rows())
    if LB not in text:
        # replace the scaffold's empty table in section "## Log" with markers
        scaffold = _HEADER + "\n" + _SEP + "\n| | | | | |"
        if scaffold in text:
            text = text.replace(scaffold, LB + "\n" + LE)
        elif "## Log" in text:
            text = text.replace("## Log", "## Log\n\n" + LB + "\n" + LE, 1)
    text = _replace_block(text, LB, LE, table)

    if RB not in text:
        text += "\n## Runs\n\n" + RB + "\n" + RE + "\n"
    text = _replace_block(text, RB, RE, "\n".join(_run_rows()) or "(none yet)")

    README.write_text(text)
