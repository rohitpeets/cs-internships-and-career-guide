"""Find working job feeds for companies the board doesn't cover yet. Run on the laptop (needs internet):
    python scripts/probe_sources.py
Prints companies.yaml lines for every source that answers, with how many CS/CE postings it has right now.
Nothing is written to data/; paste the lines you want into companies.yaml.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import adapters  # noqa: E402
from classify import keep_title, us_job  # noqa: E402
from common import Http  # noqa: E402

# (company, ats, board) guesses. Workday entries are tenant names: the probe finds the wdN host and site itself.
GUESSES = [
    ("Amazon", "amazon", "amazon"),
    ("Microsoft", "eightfold", "apply.careers.microsoft.com|microsoft.com"),
    ("Microsoft", "eightfold", "jobs.careers.microsoft.com|microsoft.com"),
    ("Netflix", "eightfold", "explore.jobs.netflix.net|netflix.com"),
    ("Qualcomm", "eightfold", "careers.qualcomm.com|qualcomm.com"),
    ("AMD", "eightfold", "careers.amd.com|amd.com"),
    ("Cisco", "eightfold", "jobs.cisco.com|cisco.com"),
    ("SpaceX", "greenhouse", "spacex"), ("Stripe", "greenhouse", "stripe"), ("Databricks", "greenhouse", "databricks"),
    ("Airbnb", "greenhouse", "airbnb"), ("Snowflake", "ashby", "snowflake"), ("Uber", "greenhouse", "uber"),
    ("Bloomberg", "greenhouse", "bloomberg"), ("Venture Global", "greenhouse", "ventureglobal"),
    ("Venture Global LNG", "greenhouse", "venturegloballng"), ("Lamar Advertising", "greenhouse", "lamar"),
    ("ServiceNow", "smartrecruiters", "ServiceNow"), ("Visa", "smartrecruiters", "Visa"), ("Bosch", "smartrecruiters", "BoschGroup"),
    ("JPMorgan Chase", "oracle", "jpmc.fa/CX_1001"), ("Oracle", "oracle", "eeho.fa.us2/CX_45001"),
    ("Capital One", "workday", "capitalone"), ("PayPal", "workday", "paypal"), ("Mastercard", "workday", "mastercard"),
    ("Target", "workday", "target"), ("Chevron", "workday", "chevron"), ("Shell", "workday", "shell"),
    ("ExxonMobil", "workday", "exxonmobil"), ("Phillips 66", "workday", "phillips66"), ("Lockheed Martin", "workday", "lmco"),
    ("Intuit", "workday", "intuit"), ("Goldman Sachs", "workday", "gs"), ("Tesla", "workday", "tesla"),
    # Louisiana and Gulf Coast
    ("Entergy", "workday", "entergy"), ("Ochsner Health", "workday", "ochsner"), ("Lumen", "workday", "lumen"),
    ("Hancock Whitney", "workday", "hancockwhitney"), ("Westlake", "workday", "westlake"), ("Sasol", "workday", "sasol"),
    ("CITGO", "workday", "citgo"), ("Cleco", "workday", "cleco"), ("Amedisys", "workday", "amedisys"),
    ("Pool Corporation", "workday", "poolcorp"), ("Globalstar", "workday", "globalstar"), ("DXC Technology", "workday", "dxctechnology"),
    ("Huntington Ingalls", "workday", "hii"), ("Turner Industries", "workday", "turner"), ("Sempra", "workday", "sempra"),
    ("Halliburton", "workday", "halliburton"), ("Baker Hughes", "workday", "bakerhughes"), ("Origin Bank", "workday", "origin"),
    ("Blue Cross Blue Shield of Louisiana", "workday", "bcbsla"), ("Lamar Advertising", "workday", "lamar"),
    ("Cameron LNG", "workday", "cameronlng"), ("Motiva", "workday", "motiva"), ("LyondellBasell", "workday", "lyondellbasell"),
    ("Dow", "workday", "dow"), ("Kinder Morgan", "workday", "kindermorgan"), ("Cheniere", "workday", "cheniere"),
]
WD_HOSTS = ("wd1", "wd5", "wd3", "wd12", "wd10", "wd103", "wd108", "wd501", "wd2", "wd101")


def find_workday(tenant, http):
    for n in WD_HOSTS:
        try:
            r = http.get(f"https://{tenant}.{n}.myworkdayjobs.com/", allow_redirects=True)
        except Exception:
            continue
        m = re.search(r"myworkdayjobs\.com/(?:[a-z]{2}-[A-Z]{2}/)?([A-Za-z0-9_\-]+)", r.url)
        if r.ok and m and m.group(1).lower() not in ("wday", "en-us"):
            return f"{tenant}.{n}/{m.group(1)}"
    return None


def main():
    http = Http(gap=0.5, timeout=15, retries=1)
    fns = {**adapters.CLOUD, **adapters.LOCAL}
    found, missing = [], []
    for name, ats, board in GUESSES:
        if ats == "workday":
            board = find_workday(board, http)
            if not board:
                missing.append(f"{name} (workday: no tenant found)")
                continue
        try:
            jobs = fns[ats](board, http)
        except Exception as e:
            missing.append(f"{name} ({ats}/{board}): {type(e).__name__} {str(e)[:80]}")
            continue
        cs = [j for j in jobs if keep_title(j["title"]) and us_job(j["location"])]
        found.append((name, ats, board, len(jobs), len(cs)))
        print(f"  ok  {name:28} {ats:15} {board:45} all={len(jobs):4} cs_us={len(cs)}", flush=True)
    print("\n# paste into data/companies.yaml (working sources):")
    for name, ats, board, _, cs in found:
        print(f'  - {{name: "{name}", ats: {ats}, board: "{board}"}}   # {cs} CS/CE postings now')
    print("\n# not found (needs a manual check):")
    for m in missing:
        print("  -", m)


if __name__ == "__main__":
    main()
