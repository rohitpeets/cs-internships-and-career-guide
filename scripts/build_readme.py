"""Write README.md (front page) and one table file per section from postings.json.

Everything in the tables comes from company feeds, so it's treated as untrusted: text is HTML- and markdown-escaped,
and a link is used only if it's a plain http(s) URL (otherwise the row is left out and counted).
"""
import html
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
LEGEND = """**Tags.** 🛂✅ the posting says it sponsors visas · 🛂❌ it says it doesn't · 🚫 it says it won't take CPT/OPT · 🇺🇸 limited to U.S. citizens, green-card holders or U.S. persons (often ITAR) · 🔒 security clearance · 🏛 government or national-lab role, often U.S.-only (check) · 🌐 remote · ⚠ link couldn't be verified recently · ⏳ listed for 60+ days.
A blank tag means the posting doesn't say. The grey line under a title is the sentence a tag came from.
**Posted** is the date the company posted the job. A date with * is when this board first saw it, because that company's job site doesn't give one. Companies sometimes re-post a job, which resets its date.

> 🛂❌ usually means no visa sponsorship later (for example H-1B). Unless the row also shows 🚫, CPT or OPT may still work. Check with the recruiter and your DSO."""
START_HERE = """## New to internships? Start here

**📘 [Student guides](guides/README.md):** short how-tos for CS and CE students on GitHub, LinkedIn, your first resume, projects, networking, applying and interviews, and a 4-year timeline. **[Resources](guides/resources.md):** communities, programs, free courses, hackathons, and tools.

- **Apply early.** Most summer internships open between August and October of the year before, and many fill by winter.
- **Freshmen and sophomores:** start with 🌱 Early Programs. In the other lists, open the posting and check the qualifications for class year and GPA.
- **Internship vs. co-op:** an internship is usually a summer. A co-op is usually a full semester or more of full-time work, often with a break from classes.
- **Don't wait to meet every bullet.** If you meet most of the qualifications, apply.
- **Get your resume checked** by your career center or an upperclassman who has had an internship before you send it out."""
GOV = re.compile(r"\b(u\.?s\.? government|government|federal|national lab\w*|laborator(y|ies)|jpl|jet propulsion|nasa|dod|department of (defense|energy)|"
                 r"navy|naval|army|air force|space force|missile|defense)\b", re.I)


GUIDES = [("resume.md", "📝 Your first resume"), ("projects.md", "🛠️ Your first projects"),
          ("applying.md", "📨 Applying and interviews"), ("networking.md", "🤝 Networking, clubs, and programs"),
          ("timeline.md", "🗓️ 4-year timeline (and F-1 rules)"), ("github.md", "🐙 GitHub setup"),
          ("linkedin.md", "💼 LinkedIn setup")]


def guides_section() -> str:
    """Embed each guide in the README as a click-to-open section, so nobody has to leave the page."""
    gdir = ROOT / "guides"
    if not gdir.is_dir():
        return ""
    start = (gdir / "README.md").read_text(encoding="utf-8") if (gdir / "README.md").exists() else ""
    m = re.search(r"## Year 1: start here\n(.*?)\n## All guides", start, re.S)
    out = ["## 📘 Guides: things I wish I knew", "",
           "Click a guide to open it right here. Each one ends with its own list of free resources.", ""]
    if m:
        out += ["### Start here (year 1)", "", re.sub(r"^## ", "### ", re.sub(r"\]\((?!https?:|#)([^)]+)\)", r"](guides/\1)", re.sub(r"\n+Looking for clubs.*$", "", m.group(1).strip())), flags=re.M), ""]
    for fname, label in GUIDES:
        f = gdir / fname
        if not f.exists():
            continue
        body = f.read_text(encoding="utf-8")
        body = re.sub(r"^# .*\n", "", body, count=1)                      # its title becomes the summary
        body = re.sub(r"^(#{2,5}) ", lambda h: "#" + h.group(1) + " ", body, flags=re.M)   # nest headings
        body = re.sub(r"\]\((?!https?:|#)([^)]+)\)", r"](guides/\1)", body)          # links work from the repo root
        body = re.sub(r"\n+Next: .*$", "", body.rstrip(), flags=re.S)
        out += ["<details>", f"<summary><b>{label}</b></summary>", "", body.strip(), "", "</details>", ""]
    return "\n".join(out)


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
    t, out = r.get("tags") or {}, []
    if t.get("sponsor") is True:
        out.append("🛂✅")
    elif t.get("sponsor") is False:
        out.append("🛂❌")
    if t.get("no_cpt"):
        out.append("🚫")
    if t.get("citizen"):
        out.append("🇺🇸")
    if t.get("clearance"):
        out.append("🔒")
    if GOV.search(r.get("title", "")) and not (t.get("citizen") or t.get("clearance")):
        out.append("🏛")
    if t.get("remote"):
        out.append("🌐")
    if r.get("status") == "uncertain" or r.get("misses", 0) > 0:  # missed its company's feed at least once
        out.append("⚠")
    if date.fromisoformat(when(r)) < date.today() - timedelta(days=60):
        out.append("⏳")
    return " ".join(out)


def evidence(r, early=False) -> str:
    ev = r.get("tag_evidence") or {}
    keys = ("early",) if early else ("no_cpt", "sponsor", "citizen", "clearance")
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
    skipped = 0
    for key, name, fname in SECTIONS:
        part = [r for r in rows if r["section"] == key]
        body, n = table(part, early=(key == "early"))
        skipped += n
        (ROOT / fname).write_text(f"# {name}\n\n[⬅ Back to the main page](README.md) · {len(part)} open · updated {today()}\n\n"
                                  f"{intro.get(key, '')}**Click a job title to open the company's application page.**\n\n{LEGEND}\n\n{body}\n", encoding="utf-8")

    must = (load_yaml(DATA / "must_have.yaml", {}) or {}).get("companies") or []
    names = " ".join(r["company"].lower() for r in rows)
    missing = [m for m in must if m.lower() not in names]
    not_yet = (f"**Not on this board yet:** {', '.join(missing)}. These companies hire CS interns, but their job sites aren't read here yet. "
               f"Check their careers pages directly.") if missing else ""

    icons = {"internship": "💼", "new_grad": "🎓", "early": "🌱"}
    links = "\n".join(f"| {icons[key]} **{name}** | {counts.get(key, 0)} | **[👉 Open the list]({fname})** |" for key, name, fname in SECTIONS)
    boards = len((load_yaml(COMPANIES, {}) or {}).get("companies") or [])
    readme = f"""# Things I Wish I Knew: CS Edition

[![Daily refresh](https://github.com/rohitpeets/mcneese-jobs/actions/workflows/daily.yml/badge.svg)](https://github.com/rohitpeets/mcneese-jobs/actions/workflows/daily.yml)

Internships, new-grad roles and early programs in the **United States** for computer science and computer engineering students, plus the guides and resources I wish I'd had as a freshman.
Pulled straight from companies' own job boards and refreshed daily. **Last updated {today()}.**

> **📘 New to internships? [Open the guides below](#-guides-things-i-wish-i-knew)** (resume, projects, applying, interviews, 4-year plan) **and [resources](guides/resources.md)** ([ColorStack](https://www.colorstack.org), [NSBE](https://www.nsbe.org), [SHPE](https://www.shpe.org), [CodePath](https://www.codepath.org), [hackathons](https://mlh.com), [free courses](guides/projects.md#resources), [project ideas](https://github.com/codecrafters-io/build-your-own-x), and [more](guides/resources.md)).

## Find jobs

**Click "👉 Open the list"** next to a section to see its jobs. Each job title in a list is a link to the company's application page.

| Section | Open roles | Link |
|---|---|---|
{links}

Each list shows the newest postings first. Tags come only from a sentence in the posting itself. A blank tag means the posting doesn't say, not "no".

**{len(rows):,} open roles** from **{boards} company job boards**, checked every day, with automated tests on every run. How it works and how accurate it is: [docs/WRITEUP.md](docs/WRITEUP.md).

This board doesn't cover everything. It reads about half of what paid job aggregators list. For more, also check Handshake, LinkedIn, and the community internship lists on GitHub.

{guides_section()}

{not_yet}

{LEGEND}

{START_HERE}

## 🆕 New this week

{new_section(new)}

---
Found a posting that should be here, or a mistake? [Open an issue](https://github.com/rohitpeets/mcneese-jobs/issues).
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    print(f"built: {dict(counts)}, new this week {len(new)}, rows left out for unsafe links {skipped}")


if __name__ == "__main__":
    main()
