"""Merge data/manual.yaml (postings added by maintainers) into postings.json.

manual.yaml:
  postings:
    - company: Example Corp
      title: Software Engineering Intern
      url: https://example.com/jobs/123
      location: Houston, TX          # optional
      section: internship            # optional: internship | new_grad | early
      notes: sponsors F-1 per recruiter   # optional, shown nowhere, for maintainers
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from classify import section, tags  # noqa: E402
from common import MANUAL, POSTINGS, load_json, load_yaml, save_json, today, url_key  # noqa: E402


def main():
    items = load_yaml(MANUAL, {"postings": []}).get("postings") or []
    rows = {r["id"]: r for r in load_json(POSTINGS, [])}
    live = set()
    for m in items:
        rid = url_key(m["url"])
        live.add(rid)
        t, ev = tags(m.get("notes", ""), m.get("location", ""))
        old = rows.get(rid, {})
        rows[rid] = {**old, "id": rid, "company": m["company"], "title": m["title"], "url": m["url"],
                     "location": m.get("location", ""), "source": "manual",
                     "section": m.get("section") or section(m["title"]) or "internship",
                     "tags": old.get("tags") or t, "tag_evidence": old.get("tag_evidence") or ev,
                     "status": old.get("status", "open"), "misses": old.get("misses", 0),
                     "first_seen": old.get("first_seen", today()), "last_seen": today()}
    # a row deleted from manual.yaml leaves the board
    for rid in [k for k, r in rows.items() if r.get("source") == "manual" and k not in live]:
        del rows[rid]
    save_json(POSTINGS, sorted(rows.values(), key=lambda r: (r["company"].lower(), r["title"].lower())))
    print(f"manual postings: {len(live)}")


if __name__ == "__main__":
    main()
