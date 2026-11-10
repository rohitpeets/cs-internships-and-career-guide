"""Fetch company boards from companies.yaml and merge them into a postings file.

    python scripts/fetch_ats.py --cloud     Greenhouse, Lever, Ashby -> data/postings.json   (GitHub Action)
    python scripts/fetch_ats.py --local     Workday, Oracle         -> data/local.json      (laptop, nightly)
    add --only workday --limit 5 for a quick test

A posting missing from its company's feed on two consecutive successful fetches is closed
and moved to removed.json. Companies whose fetch failed are left untouched.
"""
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import adapters  # noqa: E402
from classify import early_evidence, keep_title, section, tags, us_job  # noqa: E402
from common import COMPANIES, LOCAL, POSTINGS, REMOVED, Http, load_json, load_yaml, now_iso, save_json, today, url_key  # noqa: E402

MAX_FAIL_SHARE = 0.3  # more failing boards than this means something is wrong on our side


def to_row(company, ats, board, j):
    t, ev = tags(j["text"], j["location"])
    sec = section(j["title"], j["text"])
    if sec == "early":
        why = early_evidence(j["title"], j["text"])
        if why:
            ev["early"] = why
    return {"id": url_key(j["url"]), "company": company, "board": board, "title": j["title"].strip(), "url": j["url"],
            "location": j["location"], "source": ats, "section": sec, "tags": t, "tag_evidence": ev, "posted": j.get("posted"),
            "status": "open", "misses": 0, "first_seen": today(), "last_seen": today()}


def fetch_one(c, fns):
    return c, fns[c["ats"]](c["board"], Http(gap=1.0))  # pacing is shared per host across all Http objects


def board_of(r, by_name):
    """Rows are matched to their board by (ats, board); rows from before the board field existed fall back to company name."""
    return (r["source"], r.get("board") or by_name.get((r["company"], r["source"])))


def main():
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--cloud", action="store_true")
    mode.add_argument("--local", action="store_true")
    ap.add_argument("--only", help="one ats name")
    ap.add_argument("--limit", type=int, help="first N boards (testing)")
    ap.add_argument("--workers", type=int, default=8, help="boards fetched in parallel (local mode)")
    a = ap.parse_args()

    fns = adapters.LOCAL if a.local else adapters.CLOUD
    target = LOCAL if a.local else POSTINGS
    every = load_yaml(COMPANIES, {"companies": []})["companies"]
    skipped = sorted({c["ats"] for c in every} - set(adapters.CLOUD) - set(adapters.LOCAL))
    if skipped:
        print(f"no reader yet for: {', '.join(skipped)} ({sum(c['ats'] in skipped for c in every)} boards skipped)")
    boards = [c for c in every if c["ats"] in fns and (not a.only or c["ats"] == a.only)]
    if a.limit:
        boards = boards[: a.limit]

    state = load_json(target, {"rows": []} if a.local else [])
    rows = {r["id"]: r for r in (state["rows"] if a.local else state)}
    # the laptop keeps its own closed list inside local.json, so it never edits a file the Action also writes
    removed = state.get("removed", []) if a.local else load_json(REMOVED, [])
    removed_ids = {r["id"] for r in removed}
    failed, gone, unsure, seen = [], [], set(), {}
    by_name = {(c["name"], c["ats"]): c["board"] for c in boards}

    with ThreadPoolExecutor(max_workers=a.workers if a.local else 1) as pool:
        futures = [pool.submit(fetch_one, c, fns) for c in boards]
        for i, f in enumerate(as_completed(futures), 1):
            c = boards[futures.index(f)]
            key = (c["ats"], c["board"])
            try:
                _, jobs = f.result()
            except adapters.BoardGone as e:  # renamed/deleted board: flag its rows, never treat as "zero jobs"
                gone.append(f'{c["name"]} ({c["ats"]}/{c["board"]}): {e}')
                unsure.add(key)
                continue
            except Exception as e:  # network error, HTTP error or ShapeError
                failed.append(f'{c["name"]} ({c["ats"]}/{c["board"]}): {str(e)[:150]}')
                continue
            if not getattr(jobs, "complete", True) or (not jobs and any(board_of(r, by_name) == key for r in rows.values())):
                unsure.add(key)  # capped or suddenly empty: don't count its missing rows as closed
            ids = set()
            for j in jobs:
                try:  # one odd posting (missing field, null location) must not stop the run
                    j = {**j, "title": j.get("title") or "", "location": j.get("location") or "", "text": j.get("text") or ""}
                    if not keep_title(j["title"]) or not us_job(j["location"]):
                        continue
                    new = to_row(c["name"], c["ats"], c["board"], j)
                except Exception as e:
                    print(f"  skipped one posting from {c['name']}: {type(e).__name__} {str(e)[:80]}")
                    continue
                if not new["section"]:
                    continue
                ids.add(new["id"])
                if new["id"] in rows:
                    new["first_seen"] = rows[new["id"]]["first_seen"]
                elif new["id"] in removed_ids:  # reopened
                    removed[:] = [r for r in removed if r["id"] != new["id"]]
                rows[new["id"]] = new
            seen[key] = ids
            if i % 25 == 0:
                print(f"  {i}/{len(boards)} boards", flush=True)

    if boards and len(failed) / len(boards) > MAX_FAIL_SHARE:  # checked before anything is written
        for f in failed[:20]:
            print("  FAILED", f)
        sys.exit(f"{len(failed)}/{len(boards)} boards failed; not trusting this run, nothing saved")

    closed = 0
    for rid, r in list(rows.items()):
        key = board_of(r, by_name)
        if key in unsure:
            r["status"] = "uncertain"
            r["uncertain_since"] = r.get("uncertain_since") or today()
            continue
        if key in seen and rid not in seen[key]:
            if r.get("last_miss") == today():  # strikes count days, not runs: two runs on one day are one strike
                continue
            r["misses"], r["last_miss"] = r.get("misses", 0) + 1, today()
            if r["misses"] >= 2:
                removed.append({**r, "removed_on": today(), "reason": "no longer in company feed"})
                del rows[rid]
                closed += 1

    out = sorted(rows.values(), key=lambda r: (r["company"].lower(), r["title"].lower()))
    if a.local:
        save_json(target, {"fetched_at": now_iso(), "rows": out, "removed": removed[-2000:]})
    else:
        save_json(REMOVED, removed[-5000:])  # first: a crash before the next line leaves a closed row in both files, never in neither
        save_json(target, out)
    print(f"{now_iso()} boards={len(boards)} failed={len(failed)} gone={len(gone)} unsure={len(unsure)} open={len(rows)} closed_now={closed}")
    for f in failed[:20]:
        print("  FAILED", f)
    for g in gone[:40]:
        print("  GONE (fix the slug in companies.yaml)", g)


if __name__ == "__main__":
    main()
