"""Schema check, plus a guard against a source change wiping the board.

Fails if open postings dropped more than 50% versus the last commit.
Skipped when there is no previous commit of postings.json (first run).
"""
import json
import subprocess
import sys
from pathlib import Path

import jsonschema

sys.path.insert(0, str(Path(__file__).parent))
from common import DATA, POSTINGS, load_json  # noqa: E402


def previous_count():
    try:
        out = subprocess.run(["git", "show", "HEAD:data/postings.json"], capture_output=True, text=True, check=True).stdout
        return len(json.loads(out))
    except Exception:
        return None


def main():
    rows = load_json(POSTINGS, [])
    jsonschema.validate(rows, json.loads((DATA / "schema.json").read_text(encoding="utf-8")))
    prev = previous_count()
    if prev and len(rows) < prev * 0.5:
        sys.exit(f"open postings fell from {prev} to {len(rows)}; refusing to publish")
    print(f"valid: {len(rows)} postings" + (f" (was {prev})" if prev is not None else " (first run)"))


if __name__ == "__main__":
    main()
