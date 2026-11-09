"""Fetch every company board in companies.yaml and merge into postings.json.

    python scripts/fetch_ats.py --cloud        Greenhouse, Lever, Ashby (the GitHub Action)
    python scripts/fetch_ats.py --cloud --only greenhouse --limit 5   quick local test

A posting missing from its company's feed on two consecutive successful fetches is closed
and moved to removed.json. Companies whose fetch failed are left untouched.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import adapters  # noqa: E402
from classify import keep_title, section, tags  # noqa: E402
from common import COMPANIES, POSTINGS, REMOVED, Http, load_json, load_yaml, now_iso, save_json, today, url_key  # noqa: E402

MAX_FAIL_SHARE = 0.3  # more failing boards than this means something is wrong on our side


def to_row(company, ats, j):
    sec = section(j["title"], j["text"])
    t, ev = tags(j["text"], j["location"])
    return {"id": url_key(j["url"]), "company": company, "title": j["title"].strip(), "url": j["url"],
            "location": j["location"], "source": ats, "section": sec, "tags": t, "tag_evidence": ev,
            "status": "open", "misses": 0, "first_seen": today(), "last_seen": today()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cloud", action="store_true", help="only the sources that run in the GitHub Action")
    ap.add_argument("--only", help="one ats name")
    ap.add_argument("--limit", type=int, help="first N boards (testing)")
    a = ap.parse_args()

    boards = [c for c in load_yaml(COMPANIES, {"companies": []})["companies"]
              if c["ats"] in adapters.CLOUD and (not a.only or c["ats"] == a.only)]
    if a.limit:
        boards = boards[: a.limit]

    rows = {r["id"]: r for r in load_json(POSTINGS, [])}
    removed = load_json(REMOVED, [])
    removed_ids = {r["id"] for r in removed}
    http, failed, seen_by_company = Http(gap=1.0), [], {}

    for i, c in enumerate(boards, 1):
        try:
            jobs = adapters.CLOUD[c["ats"]](c["board"], http)
        except Exception as e:  # network error, HTTP error or ShapeError
            failed.append(f'{c["name"]} ({c["ats"]}/{c["board"]}): {e}')
            continue
        ids = set()
        for j in jobs:
            if not keep_title(j["title"]):
                continue
            new = to_row(c["name"], c["ats"], j)
            if not new["section"]:
                continue
            ids.add(new["id"])
            if new["id"] in rows:
                old = rows[new["id"]]
                new.update(first_seen=old["first_seen"])
            elif new["id"] in removed_ids:  # reopened
                removed[:] = [r for r in removed if r["id"] != new["id"]]
            rows[new["id"]] = new
        seen_by_company[(c["name"], c["ats"])] = ids
        if i % 25 == 0:
            print(f"  {i}/{len(boards)} boards")

    # two consecutive misses in a successfully fetched feed = closed
    closed = 0
    for rid, r in list(rows.items()):
        key = (r["company"], r["source"])
        if key in seen_by_company and rid not in seen_by_company[key]:
            r["misses"] = r.get("misses", 0) + 1
            if r["misses"] >= 2:
                removed.append({**r, "removed_on": today(), "reason": "no longer in company feed"})
                del rows[rid]
                closed += 1

    save_json(POSTINGS, sorted(rows.values(), key=lambda r: (r["company"].lower(), r["title"].lower())))
    save_json(REMOVED, removed)
    print(f"{now_iso()} boards={len(boards)} failed={len(failed)} open={len(rows)} closed_now={closed}")
    for f in failed[:20]:
        print("  FAILED", f)
    if boards and len(failed) / len(boards) > MAX_FAIL_SHARE:
        sys.exit(f"{len(failed)}/{len(boards)} boards failed; not trusting this run")


if __name__ == "__main__":
    main()
