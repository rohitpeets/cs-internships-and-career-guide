"""One function per source: fetch(board, http) -> list of {title, url, location, text}.

Each raises ShapeError when the response doesn't look like that source's format,
so a changed API fails loudly instead of silently returning zero jobs.
"""


import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from classify import keep_title, strip_html  # noqa: E402


class ShapeError(Exception):
    pass


class BoardGone(Exception):
    """404/410 for the whole board: a renamed or deleted board, never "zero open jobs"."""


class Jobs(list):
    """A board's jobs. complete=False when a cap was hit, so missing jobs must not count as closed."""

    def __init__(self, items=(), complete=True):
        super().__init__(items)
        self.complete = complete


def posted_date(v):
    """The company's own posting date as YYYY-MM-DD, from whatever the source gives:
    ISO strings, epoch seconds/milliseconds, or "November 3, 2026". None if missing or unreadable."""
    from datetime import date, datetime, timezone
    if v in (None, ""):
        return None
    try:
        if isinstance(v, (int, float)):
            d = datetime.fromtimestamp(v / 1000 if v > 1e11 else v, tz=timezone.utc).date()
        elif re.match(r"\d{4}-\d{2}-\d{2}", str(v)):
            d = date.fromisoformat(str(v)[:10])
        else:
            d = datetime.strptime(str(v).strip(), "%B %d, %Y").date()
    except (ValueError, OverflowError, OSError):
        return None
    return min(d, date.today()).isoformat()  # a future date is a data error; never show it


def paginate(call, step, cap=1000):
    """call(offset) -> (items, total). Pages until a short/empty page or `total`; stops at `cap` and reports it,
    so a capped board is treated as incomplete (missing jobs aren't counted as closed)."""
    out, offset = [], 0
    while True:
        items, total = call(offset)
        out += items
        offset += step
        if not items or offset >= total:
            return out, True
        if offset >= cap:
            return out, False


def gone(r, board):
    if r.status_code in (404, 410):
        raise BoardGone(f"{board}: HTTP {r.status_code}")


def need(cond, msg):
    if not cond:
        raise ShapeError(msg)


def greenhouse(board, http):
    r = http.get(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs", params={"content": "true"})
    gone(r, board)
    r.raise_for_status()
    d = r.json()
    need(isinstance(d, dict) and isinstance(d.get("jobs"), list), "greenhouse: no jobs list")
    return [{"title": j["title"], "url": j["absolute_url"], "location": (j.get("location") or {}).get("name") or "",
             "text": strip_html(j.get("content", "")), "posted": posted_date(j.get("first_published"))}  # updated_at is an edit date, not a posting date
            for j in d["jobs"]]


def lever(board, http):
    r = http.get(f"https://api.lever.co/v0/postings/{board}", params={"mode": "json"})
    gone(r, board)
    r.raise_for_status()
    d = r.json()
    need(isinstance(d, list), "lever: not a list")
    out = []
    for j in d:
        lists = " ".join(f"{x.get('text', '')}: {x.get('content', '')}" for x in j.get("lists", []))
        text = (j.get("descriptionPlain") or "") + "\n" + strip_html(lists) + "\n" + (j.get("additionalPlain") or "")
        out.append({"title": j["text"], "url": j["hostedUrl"], "location": (j.get("categories") or {}).get("location", "") or "", "text": text,
                    "posted": posted_date(j.get("createdAt"))})
    return out


def ashby(board, http):
    r = http.get(f"https://api.ashbyhq.com/posting-api/job-board/{board}")
    gone(r, board)
    r.raise_for_status()
    d = r.json()
    need(isinstance(d, dict) and isinstance(d.get("jobs"), list), "ashby: no jobs list")
    return [{"title": j["title"], "url": j["jobUrl"], "location": j.get("location", "") or "", "text": j.get("descriptionPlain", "") or "",
             "posted": posted_date(j.get("publishedAt"))}
            for j in d["jobs"] if j.get("isListed", True)]


SEARCHES = ("intern", "co-op", "new grad", "graduate", "entry level")


def workday(board, http):
    """board = "tenant.wdN/site". Uses the JSON search behind every Workday career site."""
    host_part, site = board.split("/", 1)
    tenant = host_part.split(".")[0]
    base = f"https://{host_part}.myworkdayjobs.com"
    api = f"{base}/wday/cxs/{tenant}/{site}"
    def page(q):
        def call(offset):
            r = http.post(f"{api}/jobs", json={"appliedFacets": {}, "limit": 20, "offset": offset, "searchText": q})
            gone(r, board)
            r.raise_for_status()
            d = r.json()
            need(isinstance(d, dict) and isinstance(d.get("jobPostings"), list), "workday: no jobPostings")
            return d["jobPostings"], d.get("total", 0)
        return call

    paths, complete = {}, True
    for q in SEARCHES:
        items, ok = paginate(page(q), 20)
        complete &= ok
        paths.update((j["externalPath"], j) for j in items if j.get("externalPath") and keep_title(j.get("title", "")))
    out = []
    for path, j in paths.items():
        r = http.get(f"{api}{path}")
        info = ((r.json() or {}).get("jobPostingInfo") or {}) if r.ok else {}  # a failed detail call keeps the row, without tags
        out.append({"title": j["title"], "url": info.get("externalUrl") or f"{base}/{site}{path}",
                    "location": info.get("location") or j.get("locationsText", ""), "text": strip_html(info.get("jobDescription", "")),
                    "posted": posted_date(info.get("startDate"))})
    return Jobs(out, complete)


def oracle(board, http):
    """board = "prefix.fa.region/site". Uses Oracle Recruiting Cloud's public candidate-experience API."""
    from urllib.parse import quote
    host_part, site = board.split("/", 1)
    base = f"https://{host_part}.oraclecloud.com"
    def page(q):
        def call(offset):
            finder = quote(f'findReqs;siteNumber={site},facetsList=NONE,limit=100,offset={offset},keyword="{q}",sortBy=POSTING_DATES_DESC', safe=";=,")
            r = http.get(f"{base}/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList&finder={finder}")
            gone(r, board)
            r.raise_for_status()
            d = r.json()
            need(isinstance(d, dict) and isinstance(d.get("items"), list), "oracle: no items")
            batch = [j for item in d["items"] for j in (item.get("requisitionList") or [])]
            total = (d["items"][0].get("TotalJobsCount") if d["items"] else 0) or 0
            return batch, (total if len(batch) == 100 else 0)  # a short page is the last one
        return call

    seen, out, complete = {}, [], True
    for q in ("intern", "co-op", "graduate", "entry level"):
        items, ok = paginate(page(q), 100)
        complete &= ok
        seen.update((j["Id"], j) for j in items if keep_title(j.get("Title", "")))
    for rid, j in seen.items():
        finder = quote(f'ById;Id="{rid}",siteNumber={site}', safe=";=,")
        r = http.get(f"{base}/hcmRestApi/resources/latest/recruitingCEJobRequisitionDetails?expand=all&onlyData=true&finder={finder}")
        text = ""
        if r.ok:
            items = (r.json() or {}).get("items") or [{}]
            text = strip_html((items[0].get("ExternalDescriptionStr") or "") + "\n" + (items[0].get("ExternalQualificationsStr") or ""))
        out.append({"title": j["Title"], "url": f"{base}/hcmUI/CandidateExperience/en/sites/{site}/job/{rid}",
                    "location": j.get("PrimaryLocation", "") or "", "text": text, "posted": posted_date(j.get("PostedDate"))})
    return Jobs(out, complete)


def smartrecruiters(board, http):
    """board = company identifier. Public Posting API: list with keyword search, then one detail call per kept job."""
    api = f"https://api.smartrecruiters.com/v1/companies/{board}/postings"
    def page(q):
        def call(offset):
            r = http.get(api, params={"q": q, "limit": 100, "offset": offset})
            gone(r, board)
            r.raise_for_status()
            d = r.json()
            need(isinstance(d, dict) and isinstance(d.get("content"), list), "smartrecruiters: no content list")
            return d["content"], d.get("totalFound", 0)
        return call

    seen, complete = {}, True
    for q in ("intern", "co-op", "graduate", "entry level"):
        items, ok = paginate(page(q), 100)
        complete &= ok
        seen.update((j["id"], j) for j in items if keep_title(j.get("name", "")))
    out = []
    for pid, j in seen.items():
        r = http.get(f"{api}/{pid}")
        det = r.json() if r.ok else {}
        secs = ((det.get("jobAd") or {}).get("sections") or {})
        text = strip_html("\n".join((v or {}).get("text", "") for v in secs.values() if isinstance(v, dict)))
        loc = j.get("location") or {}
        where = ", ".join(x for x in (loc.get("city"), loc.get("region"), loc.get("country", "").upper()) if x)
        if loc.get("remote"):
            where = (where + " (Remote)").strip()
        out.append({"title": j["name"], "url": det.get("postingUrl") or f"https://jobs.smartrecruiters.com/{board}/{pid}",
                    "location": where, "text": text, "posted": posted_date(j.get("releasedDate"))})
    return Jobs(out, complete)


def amazon(board, http):
    """amazon.jobs public search JSON (board is unused; kept for the companies.yaml format)."""
    def page(q):
        def call(offset):
            r = http.get("https://www.amazon.jobs/en/search.json",
                         params={"base_query": q, "loc_query": "United States", "result_limit": 100, "offset": offset})
            gone(r, board)
            r.raise_for_status()
            d = r.json()
            need(isinstance(d, dict) and isinstance(d.get("jobs"), list), "amazon: no jobs list")
            return d["jobs"], d.get("hits", 0)
        return call

    seen, complete = {}, True
    for q in ("intern", "co-op", "new grad", "university graduate"):
        items, ok = paginate(page(q), 100)
        complete &= ok
        seen.update((j["id"], j) for j in items if keep_title(j.get("title", "")) and j.get("country_code") in ("USA", None))
    return Jobs([{"title": j["title"], "url": "https://www.amazon.jobs" + j["job_path"],
                  "location": j.get("normalized_location") or j.get("location", ""),
                  "text": strip_html("\n".join(j.get(k) or "" for k in ("description", "basic_qualifications", "preferred_qualifications"))),
                  "posted": posted_date(j.get("posted_date"))}
                 for j in seen.values()], complete)


def eightfold(board, http):
    """board = "host|domain", e.g. "explore.jobs.netflix.net|netflix.com". Eightfold's public careers API."""
    host, domain = board.split("|", 1)
    api = f"https://{host}/api/apply/v2/jobs"
    def page(q):
        def call(start):
            r = http.get(api, params={"domain": domain, "query": q, "location": "United States", "start": start, "num": 100})
            gone(r, board)
            r.raise_for_status()
            d = r.json()
            need(isinstance(d, dict) and isinstance(d.get("positions"), list), "eightfold: no positions list")
            return d["positions"], d.get("count", 0)
        return call

    seen, complete = {}, True
    for q in ("intern", "co-op", "new grad", "university"):
        items, ok = paginate(page(q), 100)
        complete &= ok
        seen.update((j["id"], j) for j in items if keep_title(j.get("name", "")))
    out = []
    for pid, j in seen.items():
        r = http.get(f"{api}/{pid}", params={"domain": domain})
        det = r.json() if r.ok else {}
        out.append({"title": j["name"], "url": j.get("canonicalPositionUrl") or f"https://{host}/careers/job/{pid}",
                    "location": j.get("location") or "; ".join(j.get("locations") or []),
                    "text": strip_html(det.get("job_description", "") or ""), "posted": posted_date(j.get("t_create"))})
    return Jobs(out, complete)


CLOUD = {"greenhouse": greenhouse, "lever": lever, "ashby": ashby, "smartrecruiters": smartrecruiters, "amazon": amazon, "eightfold": eightfold}
LOCAL = {"workday": workday, "oracle": oracle}
