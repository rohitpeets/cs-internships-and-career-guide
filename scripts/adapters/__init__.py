"""One function per source: fetch(board, http) -> list of {title, url, location, text}.

Each raises ShapeError when the response doesn't look like that source's format,
so a changed API fails loudly instead of silently returning zero jobs.
"""


class ShapeError(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise ShapeError(msg)


def greenhouse(board, http):
    r = http.get(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs", params={"content": "true"})
    if r.status_code == 404:
        return []
    r.raise_for_status()
    d = r.json()
    need(isinstance(d, dict) and isinstance(d.get("jobs"), list), "greenhouse: no jobs list")
    from classify import strip_html
    return [{"title": j["title"], "url": j["absolute_url"], "location": (j.get("location") or {}).get("name", ""),
             "text": strip_html(j.get("content", ""))} for j in d["jobs"]]


def lever(board, http):
    r = http.get(f"https://api.lever.co/v0/postings/{board}", params={"mode": "json"})
    if r.status_code == 404:
        return []
    r.raise_for_status()
    d = r.json()
    need(isinstance(d, list), "lever: not a list")
    out = []
    for j in d:
        lists = " ".join(f"{x.get('text', '')}: {x.get('content', '')}" for x in j.get("lists", []))
        from classify import strip_html
        text = (j.get("descriptionPlain") or "") + "\n" + strip_html(lists) + "\n" + (j.get("additionalPlain") or "")
        out.append({"title": j["text"], "url": j["hostedUrl"], "location": (j.get("categories") or {}).get("location", "") or "", "text": text})
    return out


def ashby(board, http):
    r = http.get(f"https://api.ashbyhq.com/posting-api/job-board/{board}")
    if r.status_code == 404:
        return []
    r.raise_for_status()
    d = r.json()
    need(isinstance(d, dict) and isinstance(d.get("jobs"), list), "ashby: no jobs list")
    return [{"title": j["title"], "url": j["jobUrl"], "location": j.get("location", "") or "", "text": j.get("descriptionPlain", "") or ""}
            for j in d["jobs"] if j.get("isListed", True)]


SEARCHES = ("intern", "co-op", "new grad", "graduate", "entry level")


def workday(board, http):
    """board = "tenant.wdN/site". Uses the JSON search behind every Workday career site."""
    from classify import keep_title, strip_html
    host_part, site = board.split("/", 1)
    tenant = host_part.split(".")[0]
    base = f"https://{host_part}.myworkdayjobs.com"
    api = f"{base}/wday/cxs/{tenant}/{site}"
    paths = {}
    for q in SEARCHES:
        offset = 0
        while True:
            r = http.post(f"{api}/jobs", json={"appliedFacets": {}, "limit": 20, "offset": offset, "searchText": q})
            if r.status_code in (404, 410):
                return []
            r.raise_for_status()
            d = r.json()
            need(isinstance(d, dict) and isinstance(d.get("jobPostings"), list), "workday: no jobPostings")
            for j in d["jobPostings"]:
                if j.get("externalPath") and keep_title(j.get("title", "")):
                    paths[j["externalPath"]] = j
            offset += 20
            if offset >= min(d.get("total", 0), 200) or not d["jobPostings"]:
                break
    out = []
    for path, j in paths.items():
        r = http.get(f"{api}{path}")
        if not r.ok:
            continue
        info = (r.json() or {}).get("jobPostingInfo") or {}
        out.append({"title": j["title"], "url": info.get("externalUrl") or f"{base}/{site}{path}",
                    "location": info.get("location") or j.get("locationsText", ""), "text": strip_html(info.get("jobDescription", ""))})
    return out


def oracle(board, http):
    """board = "prefix.fa.region/site". Uses Oracle Recruiting Cloud's public candidate-experience API."""
    from urllib.parse import quote
    from classify import keep_title, strip_html
    host_part, site = board.split("/", 1)
    base = f"https://{host_part}.oraclecloud.com"
    seen, out = {}, []
    for q in ("intern", "co-op", "graduate", "entry level"):
        finder = quote(f'findReqs;siteNumber={site},facetsList=NONE,limit=100,keyword="{q}",sortBy=POSTING_DATES_DESC', safe=";=,")
        r = http.get(f"{base}/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList&finder={finder}")
        if r.status_code in (404, 410):
            return []
        r.raise_for_status()
        d = r.json()
        need(isinstance(d, dict) and isinstance(d.get("items"), list), "oracle: no items")
        for item in d["items"]:
            for j in item.get("requisitionList") or []:
                if keep_title(j.get("Title", "")):
                    seen[j["Id"]] = j
    for rid, j in seen.items():
        finder = quote(f'ById;Id="{rid}",siteNumber={site}', safe=";=,")
        r = http.get(f"{base}/hcmRestApi/resources/latest/recruitingCEJobRequisitionDetails?expand=all&onlyData=true&finder={finder}")
        text = ""
        if r.ok:
            items = (r.json() or {}).get("items") or [{}]
            text = strip_html((items[0].get("ExternalDescriptionStr") or "") + "\n" + (items[0].get("ExternalQualificationsStr") or ""))
        out.append({"title": j["Title"], "url": f"{base}/hcmUI/CandidateExperience/en/sites/{site}/job/{rid}",
                    "location": j.get("PrimaryLocation", "") or "", "text": text})
    return out


CLOUD = {"greenhouse": greenhouse, "lever": lever, "ashby": ashby}
LOCAL = {"workday": workday, "oracle": oracle}
