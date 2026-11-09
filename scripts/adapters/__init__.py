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


CLOUD = {"greenhouse": greenhouse, "lever": lever, "ashby": ashby}
