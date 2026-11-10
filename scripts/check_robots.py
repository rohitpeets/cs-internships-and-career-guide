"""One-off check: does each robots.txt-checked source allow the URLs this board reads?

    python scripts/check_robots.py            # every Workday/Oracle/Amazon/Eightfold board
    python scripts/check_robots.py --limit 5  # quick look

Only reads robots.txt files (one per site). Boards listed as BLOCKED will be skipped by fetch_ats.py.
"""
import argparse
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import COMPANIES, Http, load_yaml  # noqa: E402
from fetch_ats import ROBOTS_ATS  # noqa: E402


def api_url(c):
    ats, board = c["ats"], c["board"]
    if ats == "workday":
        host_part, site = board.split("/", 1)
        return f"https://{host_part}.myworkdayjobs.com/wday/cxs/{host_part.split('.')[0]}/{site}/jobs"
    if ats == "oracle":
        host_part, _ = board.split("/", 1)
        return f"https://{host_part}.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
    if ats == "amazon":
        return "https://www.amazon.jobs/en/search.json"
    if ats == "eightfold":
        return f"https://{board.split('|', 1)[0]}/api/apply/v2/jobs"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    boards = [c for c in load_yaml(COMPANIES, {"companies": []})["companies"] if c["ats"] in ROBOTS_ATS]
    if a.limit:
        boards = boards[: a.limit]
    print(f"checking robots.txt for {len(boards)} boards (8 at a time)...", flush=True)
    tally = Counter()

    def check(c):
        return c, Http(gap=1.0, timeout=10).robots_allow(api_url(c))

    with ThreadPoolExecutor(max_workers=8) as pool:
        for i, f in enumerate(as_completed([pool.submit(check, c) for c in boards]), 1):
            c, ok = f.result()
            tally[(c["ats"], ok)] += 1
            if not ok:
                print(f"BLOCKED  {c['ats']:<10} {c['name']}", flush=True)
            if i % 50 == 0:
                print(f"  {i}/{len(boards)} checked", flush=True)
    for (ats, ok), n in sorted(tally.items()):
        print(f"{ats:<10} {'allowed' if ok else 'blocked'}: {n}")


if __name__ == "__main__":
    main()
