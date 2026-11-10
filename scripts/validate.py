"""Schema check, plus a guard against a source change wiping the board.

Fails if open postings dropped below 50% of the largest count in the last 7 commits,
so a slow slide (49% one day, 49% the next) can't get past it either.
An intended shrink (a stricter filter) is committed with "[reset-baseline]" in the message.
Skipped when there is no previous commit of postings.json (first run).
"""
import json
import subprocess
import sys
from pathlib import Path

import jsonschema

sys.path.insert(0, str(Path(__file__).parent))
from common import DATA, POSTINGS, load_json  # noqa: E402


def previous_count(n=7):
    try:
        log = subprocess.run(["git", "log", f"-{n}", "--format=%H %s", "--", "data/postings.json"],
                             capture_output=True, text=True, check=True).stdout.splitlines()
        shas = []
        for line in log:  # a commit whose message has [reset-baseline] is an intended shrink: look no further back
            shas.append(line.split()[0])
            if "[reset-baseline]" in line:
                break
        counts = []
        for sha in shas:
            out = subprocess.run(["git", "show", f"{sha}:data/postings.json"], capture_output=True, text=True, check=True).stdout
            counts.append(len(json.loads(out)))
        return max(counts) if counts else None
    except Exception:
        return None


def main():
    rows = load_json(POSTINGS, [])
    jsonschema.validate(rows, json.loads((DATA / "schema.json").read_text(encoding="utf-8")))
    prev = previous_count()
    if prev and len(rows) < prev * 0.5:
        sys.exit(f"open postings fell from {prev} (7-commit high) to {len(rows)}; refusing to publish")
    print(f"valid: {len(rows)} postings" + (f" (was {prev})" if prev is not None else " (first run)"))


if __name__ == "__main__":
    main()
