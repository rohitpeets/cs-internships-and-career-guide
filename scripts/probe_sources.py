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
from common import Blocked, Http  # noqa: E402

# (company, ats, board) guesses. A Workday board is either a tenant name (the probe finds the wdN host and site)
# or an exact "tenant.wdN/site" taken from the company's own apply links. Several guesses per company are fine:
# the first one that answers wins.
GUESSES = [
    # Exact Workday sites (from the companies' own apply links); checked first
    ("Chevron", "workday", "chevron.wd5/jobs"), ("Mastercard", "workday", "mastercard.wd1/CorporateCareers"),
    ("Capital One", "workday", "capitalone.wd12/Capital_One"), ("Target", "workday", "target.wd5/targetcareers"),
    ("PayPal", "workday", "paypal.wd1/jobs"), ("Northrop Grumman", "workday", "ngc.wd1/Northrop_Grumman_External_Site"),
    ("RTX", "workday", "globalhr.wd5/REC_RTX_Ext_Gateway"), ("SAIC", "workday", "saic.wd1/SAIC"),
    ("MITRE", "workday", "mitre.wd5/MITRE"), ("BAE Systems", "workday", "baesystems.wd3/BAE_Systems_External"),
    ("General Dynamics Information Technology", "workday", "gdit.wd5/External_Career_Site"),
    ("General Dynamics Electric Boat", "workday", "gdeb.wd1/EB_Careers"),
    ("Leidos", "workday", "leidos.wd5/External"), ("Booz Allen", "workday", "bah.wd1/BAH_Jobs"),
    ("Cisco", "workday", "cisco.wd5/Cisco_Careers"), ("AMD", "workday", "amd.wd1/External"),
    ("Shell", "workday", "shell.wd3/ShellCareers"), ("Phillips 66", "workday", "phillips66.wd5/Phillips66"),
    ("Lumen", "workday", "lumen.wd5/External"), ("Westlake", "workday", "westlake.wd5/Westlake_Careers"),
    ("Cheniere", "workday", "cheniere.wd1/Cheniere"), ("Ochsner Health", "workday", "ochsner.wd1/Ochsner"),
    ("Entergy", "workday", "entergy.wd1/Entergy"), ("Intuit", "workday", "intuit.wd1/Intuit"),
    ("Visa", "workday", "visa.wd5/Visa"), ("Lockheed Martin", "workday", "lmco.wd1/LMCareers"),
    ("L3Harris", "workday", "l3harris.wd1/L3HarrisCareers"), ("Huntington Ingalls", "workday", "hii.wd1/External"),
    ("Sandia National Laboratories", "workday", "sandia.wd1/External"),
    ("Oak Ridge National Laboratory", "workday", "ornl.wd1/ORNL_Careers"),
    # Name-only guesses
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
    if "/" in tenant:  # already an exact tenant.wdN/site
        return tenant
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
    http = Http(gap=1.0, timeout=15, retries=1, check_robots=True)  # same manners as the nightly job
    fns = {**adapters.CLOUD, **adapters.LOCAL}
    found, missing, done = [], [], set()
    for name, ats, board in GUESSES:
        if name in done:  # an earlier guess for this company already worked
            continue
        if ats == "workday":
            board = find_workday(board, http)
            if not board:
                missing.append(f"{name} (workday: no tenant found)")
                continue
        try:
            jobs = fns[ats](board, http)
        except Blocked as e:
            missing.append(f"{name} ({ats}/{board}): blocked by the site ({str(e)[:60]}); leave it out")
            continue
        except Exception as e:
            missing.append(f"{name} ({ats}/{board}): {type(e).__name__} {str(e)[:80]}")
            continue
        done.add(name)
        cs = [j for j in jobs if keep_title(j["title"]) and us_job(j["location"])]
        found.append((name, ats, board, len(jobs), len(cs)))
        print(f"  ok  {name:28} {ats:15} {board:45} all={len(jobs):4} cs_us={len(cs)}", flush=True)
    print("\n# paste into data/companies.yaml (working sources):")
    for name, ats, board, _, cs in found:
        print(f'  - {{name: "{name}", ats: {ats}, board: "{board}"}}   # {cs} CS/CE postings now')
    print("\n# not found (needs a manual check):")
    for m in missing:
        if m.split(" (")[0] in done:  # another guess for the same company worked
            continue
        print("  -", m)


if __name__ == "__main__":
    main()
