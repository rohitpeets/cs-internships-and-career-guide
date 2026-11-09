"""Link checks for rows that no company feed vouches for (v1: manual.yaml rows).

Feed rows close when they drop out of their feed, so they aren't checked here.
    open      -> misses reset
    closed    -> one strike; two in a row moves the row to removed.json
    uncertain -> 403/429/timeouts: status "uncertain" (shown with ⚠); removed after 7 days
"""
import argparse
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import POSTINGS, REMOVED, Http, load_json, save_json, today  # noqa: E402

CLOSED_TEXT = re.compile(r"no longer (accepting applications|available|open)|position has been filled|job (posting )?(is |has )?(closed|expired)|page (you are|you're) looking for (doesn't|does not) exist", re.I)


def check(http, url):
    try:
        r = http.get(url, allow_redirects=True)
    except Exception:
        return "uncertain"
    if r.status_code in (404, 410):
        return "closed"
    if r.status_code in (401, 403, 429) or r.status_code >= 500:
        return "uncertain"
    return "closed" if CLOSED_TEXT.search(r.text[:200000]) else "open"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stale-only", action="store_true", help="only rows not covered by a company feed")
    a = ap.parse_args()
    rows, removed, http = load_json(POSTINGS, []), load_json(REMOVED, []), Http(gap=1.0)
    keep = []
    for r in rows:
        if a.stale_only and r.get("source") != "manual":
            keep.append(r)
            continue
        state = check(http, r["url"])
        if state == "open":
            r.update(status="open", misses=0, uncertain_since=None)
        elif state == "closed":
            r["misses"] = r.get("misses", 0) + 1
            if r["misses"] >= 2:
                removed.append({**r, "removed_on": today(), "reason": "link closed twice"})
                continue
        else:
            r["status"] = "uncertain"
            r["uncertain_since"] = r.get("uncertain_since") or today()
            if (date.today() - date.fromisoformat(r["uncertain_since"])).days >= 7:
                removed.append({**r, "removed_on": today(), "reason": "unverifiable for 7 days"})
                continue
        r["last_checked"] = today()
        keep.append(r)
    save_json(POSTINGS, keep)
    save_json(REMOVED, removed)
    print(f"checked; open rows now {len(keep)}")


if __name__ == "__main__":
    main()
