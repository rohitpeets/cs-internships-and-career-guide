"""Merge the laptop's data/local.json (Workday, Oracle) into postings.json. Run by the GitHub Action.

Laptop rows replace the previous laptop rows. If the laptop hasn't run for 3+ days,
its rows stay but show ⚠ (status "uncertain"), so the board degrades instead of breaking.
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import adapters  # noqa: E402
from common import LOCAL, POSTINGS, load_json, save_json  # noqa: E402

STALE_DAYS = 3


def main():
    local = load_json(LOCAL, None)
    if not local:
        print("no laptop data yet")
        return
    rows = [r for r in load_json(POSTINGS, []) if r.get("source") not in adapters.LOCAL]
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(local["fetched_at"])).days
    for r in local["rows"]:
        rows.append({**r, "status": "uncertain" if age >= STALE_DAYS else r.get("status", "open")})
    save_json(POSTINGS, sorted(rows, key=lambda r: (r["company"].lower(), r["title"].lower())))
    print(f"merged {len(local['rows'])} laptop rows (fetched {age} day(s) ago)")


if __name__ == "__main__":
    main()
