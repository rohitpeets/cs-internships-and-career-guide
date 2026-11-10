"""Write README.md (front page) and one table file per section from postings.json.

Everything in the tables comes from company feeds, so it's treated as untrusted: text is HTML- and markdown-escaped,
and a link is used only if it's a plain http(s) URL (otherwise the row is left out and counted).
"""
import html
import json
import re
import sys
from collections import Counter
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib.parse import quote, urlsplit

sys.path.insert(0, str(Path(__file__).parent))
from common import COMPANIES, DATA, POSTINGS, ROOT, load_json, load_yaml  # noqa: E402


def today() -> str:
    """Dates on the page are U.S. Central time, not the server's UTC."""
    return datetime.now(ZoneInfo("America/Chicago")).date().isoformat()

SECTIONS = [("internship", "Internships", "INTERNSHIPS.md"),
            ("new_grad", "New Grad", "NEW_GRAD.md"),
            ("early", "Early Programs (freshmen & sophomores)", "EARLY.md")]
LEGEND = """**Tags.** Each tag comes from a sentence in the posting, shown in grey under the job title. A blank tag means the posting doesn't say.

- 🛂✅ **sponsors**: the posting says it sponsors visas
- 🛂❌ **no sponsor**: it says it doesn't sponsor visas
- 🚫 **no CPT/OPT**: it says it won't take CPT or OPT
- 🇺🇸 **citizens**: limited to U.S. citizens, green-card holders or U.S. persons
- 📜 **ITAR**: mentions ITAR export rules, often limited to U.S. persons (check)
- 🔒 **clearance**: needs a security clearance
- 🏛 **gov**: government or national-lab role, often U.S.-only (check)
- 🌐 **remote** · ⚠ **unverified**: link couldn't be verified recently · ⏳ **60+ days**: listed for 60+ days

**Posted** is the date the company posted the job. A date with * is when this board first saw it, because that company's job site doesn't give one. Companies sometimes re-post a job, which resets its date.

> 🛂❌ usually means no visa sponsorship later (for example H-1B). Unless the row also shows 🚫, CPT or OPT may still work. Check with the recruiter and your DSO.

> **Disclaimer:** listings and tags are generated automatically from employers' public job postings and can be wrong, incomplete or out of date. Always read the full posting on the employer's site. Visa, CPT, OPT and citizenship notes are general information, not legal or immigration advice; confirm your situation with your school's DSO or an immigration attorney. This board is not affiliated with or endorsed by any employer listed."""
GOV = re.compile(r"\b(u\.?s\.? government|government|federal|national lab\w*|laborator(y|ies)|jpl|jet propulsion|nasa|dod|department of (defense|energy)|"
                 r"navy|naval|army|air force|space force|missile|defense)\b", re.I)


def text(s: str) -> str:
    """Escape untrusted text for a markdown table cell: no HTML, no links or emphasis, no new rows or columns."""
    s = " ".join((s or "").split())  # \r, \n and tabs can't start a new line or heading
    s = html.escape(s, quote=False)
    s = re.sub(r"([\\`*_\[\]()#!~])", r"\\\1", s)
    return s.replace("|", "/")


def safe_url(u: str) -> str | None:
    """Only plain http(s) links with a host; characters that could break out of markdown are percent-encoded."""
    u = (u or "").strip()
    if not u or any(c.isspace() for c in u):
        return None
    parts = urlsplit(u)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return None
    return quote(u, safe=":/?#@!$&'*+,;=%~.-_")  # ( ) < > | " ` and spaces get encoded


def tag_str(r) -> str:
    """Each tag is an emoji plus a short word, so it reads the same to a screen reader as it looks."""
    t, out = r.get("tags") or {}, []
    if t.get("sponsor") is True:
        out.append("🛂✅ sponsors")
    elif t.get("sponsor") is False:
        out.append("🛂❌ no sponsor")
    if t.get("no_cpt"):
        out.append("🚫 no CPT/OPT")
    if t.get("citizen"):
        out.append("🇺🇸 citizens")
    elif t.get("itar"):
        out.append("📜 ITAR")
    if t.get("clearance"):
        out.append("🔒 clearance")
    if GOV.search(r.get("title", "")) and not (t.get("citizen") or t.get("clearance") or t.get("itar")):
        out.append("🏛 gov")
    if t.get("remote"):
        out.append("🌐 remote")
    if r.get("status") == "uncertain" or r.get("misses", 0) > 0:  # missed its company's feed at least once
        out.append("⚠ unverified")
    if date.fromisoformat(when(r)) < date.today() - timedelta(days=60):
        out.append("⏳ 60+ days")
    return "<br>".join(out)


def evidence(r, early=False) -> str:
    ev = r.get("tag_evidence") or {}
    keys = ("early",) if early else ("no_cpt", "sponsor", "citizen", "itar", "clearance")
    s = next((ev[k] for k in keys if ev.get(k)), "")
    return f"<br><sub>“{text(s[:140])}{'…' if len(s) > 140 else ''}”</sub>" if s else ""


def dedupe(rows):
    """Same company + title + location shown once (companies often post one job under several links)."""
    best = {}
    for r in rows:
        k = (r["company"].lower().strip(), r["title"].lower().strip(), (r.get("location") or "").lower().strip())
        if k not in best or r["first_seen"] < best[k]["first_seen"]:
            best[k] = r
    return list(best.values())


def when(r) -> str:
    """The company's posting date when the feed gives one, else the day this board first saw the job."""
    return r.get("posted") or r["first_seen"]


def added(d: str) -> str:
    x = date.fromisoformat(d)
    return f"{x:%b} {x.day}"


def table(rows, early=False) -> tuple[str, int]:
    """Newest first by posting date. The date column is left out while every row has the same date."""
    show_added = len({when(r) for r in rows}) > 1
    lines = ["| Company | Role | Location | Tags |" + (" Posted |" if show_added else ""),
             "|---|---|---|---|" + ("---|" if show_added else "")]
    skipped = 0
    for r in sorted(rows, key=lambda r: (-date.fromisoformat(when(r)).toordinal(), r["company"].lower(), r["title"].lower())):
        url = safe_url(r.get("url"))
        if not url:
            skipped += 1
            continue
        loc = r.get("location") or ""
        line = (f"| {text(r['company'])} | [{text(r['title'])}]({url}){evidence(r, early)} | "
                f"{text(loc[:45])}{'…' if len(loc) > 45 else ''} | {tag_str(r)} |")
        lines.append(line + (f" {added(when(r))}{'' if r.get('posted') else '*'} |" if show_added else ""))
    return "\n".join(lines), skipped


def new_section(new) -> str:
    if not new:
        return "_Nothing new this week yet._"
    if len(new) > 150:  # a big new source was added this week
        return f"_{len(new)} postings were added this week (a new source was connected). Browse the sections above._"
    per, capped = Counter(), []
    for r in sorted(new, key=lambda r: when(r), reverse=True):  # at most 3 per company, so one big poster can't fill the list
        per[r["company"]] += 1
        if per[r["company"]] <= 3:
            capped.append(r)
    shown, _ = table(capped[:75])
    return shown + f"\n\n_{len(new)} postings were posted this week. This list shows up to 3 per company; the rest are in the section pages above._"


def main():
    rows = dedupe(load_json(POSTINGS, []))
    for r in rows:  # an early-program row has to show the sentence that makes it one; otherwise it's listed as a normal internship
        if r["section"] == "early" and not (r.get("tag_evidence") or {}).get("early"):
            r["section"] = "internship"
    counts = Counter(r["section"] for r in rows)
    week_ago = (date.today() - timedelta(days=7)).isoformat()
    # "new" means the company posted it this week; a row without a posting date counts from when the board first saw it,
    # but only after the board's first week (otherwise every launch-week row would be "new")
    launched = min((r["first_seen"] for r in rows), default=today())
    new = [r for r in rows if (r.get("posted") or (r["first_seen"] if r["first_seen"] > launched else "")) >= week_ago]

    intro = {"early": "Postings that say freshmen or sophomores can apply, or programs built for them. "
                      "The grey line under each title is the sentence from the posting, so you can check it.\n\n"
                      "Big-company programs like Google STEP, Microsoft Explore and Meta University aren't read by this board yet. "
                      "Check their student career pages directly in the fall.\n\n"}
    must = (load_yaml(DATA / "must_have.yaml", {}) or {}).get("companies") or []
    names = " ".join(r["company"].lower() for r in rows)
    missing = [m for m in must if m.lower() not in names]
    not_yet = (f"**Not on this board yet:** {', '.join(missing)}. These companies hire CS interns, but their job sites aren't read here yet. "
               f"Check their careers pages directly.") if missing else ""

    skipped = 0
    for key, name, fname in SECTIONS:
        part = [r for r in rows if r["section"] == key]
        body, n = table(part, early=(key == "early"))
        skipped += n
        (ROOT / fname).write_text(f"# {name}\n\n[⬅ Back to the main page](README.md) · {len(part)} open · updated {today()}\n\n"
                                  f"{intro.get(key, '')}**Click a job title to open the company's application page.**\n\n{LEGEND}\n\n{body}\n"
                                  + (f"\n{not_yet}\n" if key != "early" and not_yet else ""), encoding="utf-8")


    # postings from this week get their own page, so the landing page stays short
    (ROOT / "NEW_THIS_WEEK.md").write_text(
        f"# 🆕 New this week\n\n[⬅ Back to the main page](README.md) · {len(new)} posted in the last 7 days · updated {today()}\n\n"
        f"**Click a job title to open the company's application page.**\n\n{LEGEND}\n\n{new_section(new)}\n", encoding="utf-8")

    boards = len((load_yaml(COMPANIES, {}) or {}).get("companies") or [])
    early = counts.get("early", 0)
    early_note = f"{early} open right now" if early else "None listed right now, check back soon"
    readme = f"""# Things I Wish I Knew: CS Edition

[![Daily refresh](https://github.com/rohitpeets/cs-internships-and-career-guide/actions/workflows/daily.yml/badge.svg)](https://github.com/rohitpeets/cs-internships-and-career-guide/actions/workflows/daily.yml)

A free starter kit for computer science and computer engineering students in the U.S.: **a job board refreshed every day** from companies' own career sites, plus **plain-English guides** on everything I wish someone had told me as a freshman.

Last updated **{today()}**.

## 💼 Find jobs

| List | What's inside |
|---|---|
| 💼 **[Internships](INTERNSHIPS.md)** | {counts.get("internship", 0):,} open roles, newest first |
| 🎓 **[New grad](NEW_GRAD.md)** | {counts.get("new_grad", 0):,} full-time roles for graduating students |
| 🌱 **[Early programs](EARLY.md)** | For freshmen and sophomores. {early_note} |
| 🆕 **[New this week](NEW_THIS_WEEK.md)** | {len(new):,} roles posted in the last 7 days |

Every row links straight to the company's application page. International students: each posting is tagged for visa sponsorship, CPT/OPT and citizenship rules, with the sentence from the posting that the tag came from.

## 📘 Guides

| Guide | Read it if... |
|---|---|
| 🧭 **[Start here](guides/README.md)** | You're a freshman or sophomore and don't know where to begin |
| 📝 **[Your first resume](guides/resume.md)** | You need a resume, or yours isn't getting replies |
| 🛠️ **[Your first projects](guides/projects.md)** | You don't know what to build or how to finish it |
| 📨 **[Applying and interviews](guides/applying.md)** | You're about to apply: timing, referrals, coding tests, interviews |
| 🤝 **[Networking and getting involved](guides/networking.md)** | You want clubs, research, hackathons, contests, programs |
| 🗓️ **[4-year timeline](guides/timeline.md)** | You want to know what to do each semester (and F-1 rules) |
| 🐙 **[GitHub](guides/github.md)** | You need to set up GitHub or make your repos look good |
| 💼 **[LinkedIn](guides/linkedin.md)** | You need a LinkedIn profile or want to reach alumni |
| 🧰 **[Resources](guides/resources.md)** | You want free courses, communities, scholarships, and tools |

## 🚀 New here? Do these 3 things

1. **Read [Start here](guides/README.md).** Five steps for your first year, nothing more.
2. **Make a one-page resume** with the [resume guide](guides/resume.md).
3. **Apply early.** Big-company summer internships open about **July to September of the year before**. Open the [internships list](INTERNSHIPS.md) and apply in the first two weeks.

## ℹ️ About

- **{len(rows):,} open roles** from **{boards} company job boards**, checked every day with automated tests on every run. How it works and how accurate it is: [docs/WRITEUP.md](docs/WRITEUP.md).
- It doesn't catch everything. Also check Handshake, LinkedIn, and [Simplify's internship list](https://github.com/SimplifyJobs/Summer2027-Internships).
- Found a missing posting, a broken link, or a mistake? [Open an issue](https://github.com/rohitpeets/cs-internships-and-career-guide/issues).

## ⚖️ Disclaimer

This board is provided as is, without warranty of any kind. Listings and tags are generated automatically from employers' public job postings and can be wrong, incomplete or out of date. Always read the full posting on the employer's site. Visa, CPT, OPT and citizenship notes are general information, not legal or immigration advice; confirm your situation with your school's DSO or an immigration attorney. This project is free, non-commercial, and not affiliated with or endorsed by any employer listed or any university.

## License

- **Code:** [MIT](LICENSE).
- **Guides** (`guides/`): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Share and adapt them with credit.
- **Job listings:** titles, links and short quotes come from employers' public postings. They belong to those employers and aren't covered by either license.
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    # numbers for the GitHub Pages home page (index.html reads them as site.data.stats)
    (ROOT / "_data").mkdir(exist_ok=True)
    (ROOT / "_data" / "stats.json").write_text(json.dumps({"updated": today(), "internships": counts.get("internship", 0),
        "new_grad": counts.get("new_grad", 0), "early": counts.get("early", 0), "new_week": len(new), "total": len(rows),
        "boards": boards}, indent=2) + "\n", encoding="utf-8")
    print(f"built: {dict(counts)}, new this week {len(new)}, rows left out for unsafe links {skipped}")


if __name__ == "__main__":
    main()
