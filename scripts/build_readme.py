"""Write README.md (front page) and one table file per section from postings.json.

Everything in the tables comes from company feeds, so it's treated as untrusted: text is HTML- and markdown-escaped,
and a link is used only if it's a plain http(s) URL (otherwise the row is left out and counted).
"""
import html
import json
import re
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote, urlsplit

sys.path.insert(0, str(Path(__file__).parent))
from common import COMPANIES, DATA, POSTINGS, ROOT, dedupe_rows, load_json, load_yaml, today, today_date  # noqa: E402
from classify import TRACKS, clearance_level, is_gov, terms, track  # noqa: E402



SECTIONS = [("internship", "Internships", "INTERNSHIPS.md"),
            ("new_grad", "New Grad", "NEW_GRAD.md"),
            ("early", "Early Programs (freshmen & sophomores)", "EARLY.md")]
# Empty, fixed-size spot the site's filter bar fills in, so adding it never shifts the long table (GitHub shows nothing).
FILTER_SLOT = '<div class="job-filter" id="job-filter"></div>'
LEGEND = """<details markdown="1" open>
<summary>What the tags and dates mean</summary>

**Tags.** Each tag comes from a sentence in the posting, shown in grey under the job title. A blank tag means the posting doesn't say.

- 🛂✅ **sponsors**: the posting says it sponsors visas
- 🛂❌ **no sponsor**: it says it doesn't sponsor visas
- 🚫 **no CPT/OPT**: it says it won't take CPT or OPT
- 🗽 **citizens**: limited to U.S. citizens, green-card holders or U.S. persons
- 📜 **ITAR**: mentions ITAR export rules, often limited to U.S. persons (check)
- 🔒 **clearance**: needs a security clearance (🔒 secret, 🔒 top secret, 🔒 ts/sci and 🔒 public trust show the level when the posting names it)
- 🏛 **gov**: government or national-lab role, often U.S.-only (check)
- 🧪 **OA**: the posting mentions an online coding test (HackerRank, CodeSignal, Codility or an "online assessment")
- 🎓 **3.0+ GPA**: the posting asks for a minimum GPA (the number shown is the minimum it states)
- 🔄 **co-op** · 🍂 **fall** · 🌱 **spring** · ⏱ **part-time**: the term or schedule named in the job title. No tag means summer or not stated
- 🌐 **remote** · ⏳ **60+ days**: the company posted it more than 60 days ago. Some big companies keep one posting open all year, so it may still be hiring
- ⚠ **unverified**: the company's job feed left it out at least once, or its link couldn't be checked recently. It may have closed

**Posted** is the date the company posted the job. A dash (—) means the company's job site doesn't publish one. Companies sometimes re-post a job, which resets its date.

> 🛂❌ usually means no visa sponsorship later (for example H-1B). Unless the row also shows 🚫, CPT or OPT may still work. Check with the recruiter. None of this is legal or immigration advice.

</details>"""
DISCLAIMER = "_Listings and tags are generated automatically from employers' postings and can be wrong or out of date. Always read the full posting._"

def text(s: str) -> str:
    """Escape untrusted text for a markdown table cell: no HTML, no links or emphasis, no new rows or columns,
    and no Liquid or kramdown syntax ({{ }}, {% %}, {: }), which the GitHub Pages build would otherwise run."""
    s = html.unescape(html.unescape(s or ""))  # feeds sometimes double-encode ("&amp;nbsp;"); show the character, not the entity
    s = " ".join(s.replace("\xa0", " ").split())  # \r, \n, tabs and non-breaking spaces can't start a new line or heading
    s = html.escape(s, quote=False)
    s = re.sub(r"([\\`*_\[\]()#!~])", r"\\\1", s)
    return s.replace("|", "/").replace("{", "&#123;").replace("}", "&#125;")


def safe_url(u: str) -> str | None:
    """Only plain http(s) links with a host; characters that could break out of markdown are percent-encoded."""
    u = (u or "").strip()
    if not u or any(c.isspace() for c in u):
        return None
    parts = urlsplit(u)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return None
    return quote(u, safe=":/?#@!$&'*+,;=%~.-_")  # ( ) < > | " ` and spaces get encoded


MAX_PAGE_BYTES = 480_000  # GitHub renders markdown files up to 512 KiB; leave headroom
MAX_ROWS_PER_PAGE = 120  # a list page shows at most this many postings, then continues on the next page
EMDASH = "\u2014"  # shown in the Posted column when the company site gives no date

TERM_TAGS = {"co_op": "🔄 co-op", "fall": "🍂 fall", "spring": "🌱 spring", "part_time": "⏱ part-time"}


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
        out.append("🗽 citizens")
    elif t.get("itar"):
        out.append("📜 ITAR")
    if t.get("clearance"):
        lvl = t.get("clearance_level") or clearance_level((r.get("tag_evidence") or {}).get("clearance", ""))
        out.append(f"🔒 {lvl}" if lvl else "🔒 clearance")
    if is_gov({"title": r.get("title", ""), "tags": {}}) and not (t.get("citizen") or t.get("clearance") or t.get("itar")):
        out.append("🏛 gov")
    if t.get("oa"):
        out.append("🧪 OA")
    if t.get("min_gpa"):
        out.append(f"🎓 {t['min_gpa']:.1f}+ GPA")
    out += [TERM_TAGS[k] for k in terms(r.get("title", ""))]
    if t.get("remote"):
        out.append("🌐 remote")
    if r.get("status") == "uncertain" or r.get("misses", 0) > 0:  # missed its company's feed at least once
        out.append("⚠ unverified")
    if date.fromisoformat(when(r)) < today_date() - timedelta(days=60):
        out.append("⏳ 60+ days")
    return "<br>".join(out)


def evidence(r, early=False) -> str:
    ev = r.get("tag_evidence") or {}
    keys = ("early",) if early else ("no_cpt", "sponsor", "citizen", "itar", "clearance")
    s = next((ev[k] for k in keys if ev.get(k)), "")
    return f"<br><sub>“{text(s[:140])}{'…' if len(s) > 140 else ''}”</sub>" if s else ""


dedupe = dedupe_rows  # postings.json is deduped at ingest (merge_local.py); this catches hand-added duplicates


SUFFIXES = {"inc", "incorporated", "corp", "corporation", "co", "company", "llc", "ltd", "plc", "group", "holdings", "the", "and",
            "technologies", "technology"}  # "Palantir Technologies" is Palantir, "Micron Technology" is Micron


def company_key(name: str) -> str:
    """ "Intel Corporation" and "Intel" match; "Apple Bank" isn't Apple and "Intuitive Surgical" isn't Intuit,
    so names are compared whole (minus legal suffixes), never as substrings."""
    words = re.sub(r"[^a-z0-9& ]", " ", (name or "").lower()).replace("&", " and ").split()
    while words and words[-1] in SUFFIXES:
        words.pop()
    while words and words[0] == "the":
        words.pop(0)
    return " ".join(words)


def career_links(missing, pages) -> str:
    """Names of companies the board can't read, each linked to its own careers page when we have one."""
    return ", ".join(f"[{m}]({pages[m]})" if pages.get(m) else m for m in missing)


def when(r) -> str:
    """The company's posting date when the feed gives one, else the day this board first saw the job."""
    return r.get("posted") or r["first_seen"]


_STATE_ABBREV = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
    "colorado": "CO", "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA",
    "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV", "new hampshire": "NH",
    "new jersey": "NJ", "new mexico": "NM", "new york": "NY", "north carolina": "NC",
    "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode island": "RI", "south carolina": "SC", "south dakota": "SD", "tennessee": "TN",
    "texas": "TX", "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC",
}
_US_SUFFIX = re.compile(r",?\s*(?:United States(?: of America)?|USA?)\s*$", re.I)
_STATE_RE = re.compile(
    r"\b(" + "|".join(re.escape(s) for s in sorted(_STATE_ABBREV, key=len, reverse=True)) + r")\s*$", re.I
)
_MULTI_SPACE = re.compile(r"\s{2,}")

def norm_location(loc: str) -> str:
    """Normalize a location string: drop US suffix, shorten full state names to abbreviations."""
    loc = _US_SUFFIX.sub("", loc).strip().rstrip(",").strip()
    m = _STATE_RE.search(loc)
    if m:
        loc = loc[:m.start()] + _STATE_ABBREV[m.group(1).lower()]
    return _MULTI_SPACE.sub(" ", loc).strip()


def added(d: str) -> str:
    x = date.fromisoformat(d)
    return f"{x:%b} {x.day}"


def paginate(items, size=MAX_ROWS_PER_PAGE):
    """Split a list into pages of at most `size` items. The internships list is long, so it is shown as
    numbered pages; an empty list still yields one (empty) page so the section file always exists."""
    return [items[i:i + size] for i in range(0, len(items), size)] or [items]


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
        loc = norm_location(r.get("location") or "")
        line = (f"| {text(r['company'])} | [{text(r['title'])}]({url}){evidence(r, early)} | "
                f"{text(loc[:45])}{'…' if len(loc) > 45 else ''} | {tag_str(r)} |")
        lines.append(line + (f" {added(r['posted']) if r.get('posted') else EMDASH} |" if show_added else ""))
    return "\n".join(lines), skipped


TRACK_GUIDE = {"software": "guides/tracks.md#software", "embedded": "guides/tracks.md#embedded-and-firmware",
               "hardware": "guides/tracks.md#hardware-and-chips", "security": "guides/tracks.md#security",
               "it": "guides/tracks.md#it-and-networking", "data": "guides/tracks.md#data-and-ml", "gov": "guides/tracks.md#government-and-defense"}
TRACK_BLURB = {"software": "Web, mobile, backend, full-stack and general software roles.",
               "embedded": "Firmware, microcontroller and real-time software that runs on devices.",
               "hardware": "Chip design, FPGA and ASIC work, and design verification.",
               "security": "Cybersecurity, security analyst and penetration testing roles.",
               "it": "IT support, networking, systems administration and cloud operations.",
               "data": "Data analysis, data engineering, machine learning and AI roles.",
               "gov": "Government, national-lab and defense roles, plus any posting that asks for a clearance or U.S. citizenship."}


def track_rows(rows, slug):
    if slug == "gov":
        return [r for r in rows if is_gov(r)]
    return [r for r in rows if track(r["title"]) == slug]


def write_track_pages(rows) -> int:
    """One page per track: internships and new-grad roles, newest first. Early programs are listed with the internships.
    A government/defense row also stays on its main track's page; the gov page is the second way in."""
    skipped = 0
    for slug, name in TRACKS:
        part = track_rows(rows, slug)
        interns = [r for r in part if r["section"] in ("internship", "early")]
        grads = [r for r in part if r["section"] == "new_grad"]
        blocks = []
        for title, group in (("Internships", interns), ("New grad", grads)):
            body, n = table(group)
            skipped += n
            blocks.append(f"## {title} ({len(group)})\n\n" + (body if group else "_Nothing open in this track right now._"))
        why = ("A posting is on this page if its title names government, a national lab or defense, or the posting asks for a clearance or U.S. citizenship. "
               "The same job can also appear on its main track's page.\n\n" if slug == "gov" else
               "The track comes from the words in the job title, so a few jobs may land in the wrong one. If a title doesn't say, it goes under Software.\n\n")
        (ROOT / f"track-{slug}.md").write_text(
            f"# {name}\n\n[⬅ Back to the main page](./) · {len(part)} open · updated {today()}\n\n"
            f"{TRACK_BLURB[slug]} New to this track? Read the [{name} section of the Career tracks guide]({TRACK_GUIDE[slug]}).\n\n{why}"
            f"**Click a job title to open the company's application page.**\n\n{LEGEND}\n\n{FILTER_SLOT}\n\n" + "\n\n".join(blocks) + f"\n\n{DISCLAIMER}\n", encoding="utf-8")
    return skipped


def new_section(new) -> str:
    if not new:
        return "_Nothing new this week yet._"
    per, capped = Counter(), []
    for r in sorted(new, key=lambda r: when(r), reverse=True):  # at most 3 per company, so one big poster can't fill the list
        per[r["company"]] += 1
        if per[r["company"]] <= 3:
            capped.append(r)
    shown, _ = table(capped[:75])
    return shown + f"\n\n_{len(new)} postings were posted this week. This list shows up to 3 per company; the rest are in the [internships](INTERNSHIPS.md) and [new grad](NEW_GRAD.md) lists._"


def unverified_count(rows):
    """Rows the last run couldn't re-check (shown with the totals, so a reader isn't handed a
    headline count that quietly includes postings which may already have closed)."""
    return sum(1 for r in rows if r.get("status") == "uncertain")


def main():
    rows = dedupe(load_json(POSTINGS, []))
    for r in rows:  # an early-program row has to show the sentence that makes it one; otherwise it's listed as a normal internship
        if r["section"] == "early" and not (r.get("tag_evidence") or {}).get("early"):
            r["section"] = "internship"
    counts = Counter(r["section"] for r in rows)
    week_ago = (today_date() - timedelta(days=7)).isoformat()
    # "new" means the company posted it this week; a row without a posting date counts from when the board first saw it,
    # but only after the board's first week (otherwise every launch-week row would be "new")
    launched = min((r["first_seen"] for r in rows), default=today())
    new = [r for r in rows if (r.get("posted") or (r["first_seen"] if r["first_seen"] > launched else "")) >= week_ago]

    early_watchlist = ("\n\n<details markdown=\"1\" open>\n<summary><strong>Well-known programs to watch for</strong></summary>\n\n"
                       "These programs are built for freshmen and sophomores and open once a year. "
                       "They're added here only while applications are open.\n\n"
                       "| Program | Typical window | Where to check |\n"
                       "|---|---|---|\n"
                       "| Microsoft Explore | Aug–Oct | [careers.microsoft.com](https://careers.microsoft.com/students/us/en/us-ur-swe-702) |\n"
                       "| Google STEP | Sep–Oct | [google.com/students](https://www.google.com/about/careers/applications/students/) |\n"
                       "| NVIDIA Ignite | Sep–Oct | [nvidia.com/careers](https://www.nvidia.com/en-us/about-nvidia/careers/university/) |\n"
                       "| Meta University | Sep–Nov | [metacareers.com/students](https://www.metacareers.com/students-and-grads/) |\n"
                       "| Amazon Propel | Aug–Oct | [amazon.jobs/students](https://www.amazon.jobs/en/landing_pages/campus) |\n"
                       "| UberSTAR | Varies | [uber.com/careers](https://www.uber.com/us/en/careers/) |\n"
                       "| Bank of America Global Technology Freshman Analyst | Aug–Oct | [bankofamerica.com/campus](https://campus.bankofamerica.com/) |\n"
                       "\nThis list is maintained by hand. If a program is missing, [open an issue](https://github.com/rohitpeets/cs-internships-and-career-guide/issues).\n\n"
                       "</details>\n")
    intro = {"early": "Postings that say freshmen or sophomores can apply, or programs built for them. "
                      "The grey line under each title is the sentence from the posting, so you can check it.\n\n"
                      "Big tech programs for first- and second-years, like Microsoft Explore and NVIDIA Ignite, usually open in September "
                      "and close in October, so check their student pages in late summer. Programs are added here only while they're open.\n\n"
                      "Only a few programs are open at a time. Freshmen and sophomores should also check the full [internships list](INTERNSHIPS.md) — most roles there don't require a class year.\n\n"}
    must = (load_yaml(DATA / "must_have.yaml", {}) or {}).get("companies") or []
    have = {company_key(r["company"]) for r in rows}
    pages = (load_yaml(DATA / "career_pages.yaml", {}) or {}).get("pages") or {}
    must_missing = [m for m in must if company_key(m) not in have]
    must_keys = {company_key(m) for m in must_missing}
    extra = sorted(name for name in pages if company_key(name) not in have and company_key(name) not in must_keys)
    missing = must_missing + extra
    def not_yet(roles):
        return (f"**Not on this board yet:** {career_links(missing, pages)}. These companies hire {roles}, but their job sites aren't read here yet. "
                f"The links go to each company's own careers page.") if missing else ""

    skipped = 0
    def section_nav(stem, idx, total):
        name_of = (lambda i: f"{stem}.md" if i == 1 else f"{stem}-{i}.md")
        label = stem.replace("_", " ").replace("-", " ")
        bits = []
        if idx > 1:
            bits.append(f"[⬅ {label} page {idx - 1}]({name_of(idx - 1)})")
        bits.append(f"page {idx} of {total}")
        if idx < total:
            bits.append(f"[{label} page {idx + 1} ➡]({name_of(idx + 1)})")
        return " · ".join(bits)

    for key, name, fname in SECTIONS:
        stem = fname[:-3]
        for old in ROOT.glob(f"{stem}-*.md"):  # drop continuation pages from an earlier, larger run
            old.unlink()
        part = sorted((r for r in rows if r["section"] == key),
                      key=lambda r: (-date.fromisoformat(when(r)).toordinal(), r["company"].lower(), r["title"].lower()))
        skipped += sum(1 for r in part if not safe_url(r.get("url")))  # same rows table() leaves out
        tail = (f"\n{not_yet('new grads' if key == 'new_grad' else 'CS interns')}\n" if key != "early" and missing else "")

        def render(chunk, idx, total):
            head = f"# {name}\n\n[⬅ Back to the main page](./) · {len(part)} open" + (f" · page {idx} of {total}" if total > 1 else "") + f" · updated {today()}\n\n"
            nav = f"{section_nav(stem, idx, total)}\n\n" if total > 1 else ""
            body, _ = table(chunk, early=(key == "early"))
            watchlist = early_watchlist if key == "early" and idx == total else ""
            return (head + nav
                    + f"{intro.get(key, '')}**Click a job title to open the company's application page.**\n\n{LEGEND}\n\n{FILTER_SLOT}\n\n{body}\n"
                    + watchlist
                    + (f"\n{section_nav(stem, idx, total)}\n" if total > 1 else "")
                    + (tail if idx == total else "") + f"\n{DISCLAIMER}\n")

        chunks = paginate(part)
        texts = [render(chunk, i + 1, len(chunks)) for i, chunk in enumerate(chunks)]
        for idx, t in enumerate(texts, 1):
            (ROOT / (f"{stem}.md" if idx == 1 else f"{stem}-{idx}.md")).write_text(t, encoding="utf-8")


    skipped += write_track_pages(rows)

    # postings from this week get their own page, so the landing page stays short
    (ROOT / "NEW_THIS_WEEK.md").write_text(
        f"# 🆕 New this week\n\n[⬅ Back to the main page](./) · {len(new)} posted in the last 7 days · updated {today()}\n\n"
        f"**Click a job title to open the company's application page.**\n\n{LEGEND}\n\n{FILTER_SLOT}\n\n{new_section(new)}\n\n{DISCLAIMER}\n", encoding="utf-8")

    track_counts = {slug: len(track_rows(rows, slug)) for slug, _ in TRACKS}
    term_counts = {k: sum(1 for r in rows if k in terms(r["title"])) for k in ("co_op", "fall", "spring", "part_time")}
    track_table = "\n".join(f"| [{name}](track-{slug}.md) | {track_counts[slug]:,} |" for slug, name in TRACKS)
    boards = len((load_yaml(COMPANIES, {}) or {}).get("companies") or [])
    stale = unverified_count(rows)
    early = counts.get("early", 0)
    early_note = f"{early} open right now" if early else "None listed right now, check back soon"
    readme = f"""# Things I Wish I Knew: CS Edition

[![Daily refresh](https://github.com/rohitpeets/cs-internships-and-career-guide/actions/workflows/daily.yml/badge.svg)](https://github.com/rohitpeets/cs-internships-and-career-guide/actions/workflows/daily.yml)

A free starter kit for computer science and computer engineering students in the U.S.: **a job board refreshed every day** from companies' own career sites, plus **plain-English guides** on everything I wish someone had told me as a freshman.

## 🌐 [Open the live site →](https://rohitpeets.github.io/cs-internships-and-career-guide)

Search, filter, and browse everything in one place — easier than scrolling these files. **Start there.**

Last updated **{today()}**.

## 💼 Find jobs

| List | What's inside |
|---|---|
| 💼 **[Internships](INTERNSHIPS.md)** | {counts.get("internship", 0):,} open roles, newest first |
| 🎓 **[New grad](NEW_GRAD.md)** | {counts.get("new_grad", 0):,} full-time roles for graduating students |
| 🌱 **[Early programs](EARLY.md)** | For freshmen and sophomores. {early_note} |
| 🆕 **[New this week](NEW_THIS_WEEK.md)** | {len(new):,} roles posted in the last 7 days |

### Find jobs by track

| Track | Open roles |
|---|---|
{track_table}

_A role can fit more than one track, so the track counts add up to more than the total._

Every row links straight to the company's application page. Postings are tagged for citizenship, clearance and sponsorship rules, with the sentence each tag came from.

## 📘 Guides

| Guide | Read it if... |
|---|---|
| 🧭 **[Start here](guides/README.md)** | You're a freshman or sophomore and don't know where to begin |
| 📝 **[Your first resume](guides/resume.md)** | You need a resume, or yours isn't getting replies |
| 🛠️ **[Projects](guides/projects.md)** | You don't know what to build or how to finish it |
| 📨 **[Applying](guides/applying.md)** | You're about to apply: timing, referrals, coding tests, offers |
| 🤝 **[Networking](guides/networking.md)** | You know nobody yet: clubs, alumni, hackathons, career fairs |
| 🎤 **[Interviews](guides/interviews.md)** | You have a recruiter call, coding round or behavioral interview coming up |
| 🧩 **[Career tracks](guides/tracks.md)** | You're curious about software, embedded, hardware, security, IT, data or government and defense, and what each takes |
| 🗓️ **[4-year timeline](guides/timeline.md)** | You want to know what to do each semester |
| 🐙 **[GitHub](guides/github.md)** | You need to set up GitHub or make your repos look good |
| 💼 **[LinkedIn](guides/linkedin.md)** | You need a LinkedIn profile or want to reach alumni |
| 🧰 **[Resources](guides/resources.md)** | You want free courses, communities, scholarships, and tools |

## ℹ️ About

- **{len(rows):,} open roles** from **{boards:,} company job boards**, checked every day with automated tests on every run.{f" {stale:,} of them couldn't be re-checked recently and are marked ⚠." if stale else ""} How it works and how accurate it is: [docs/WRITEUP.md](docs/WRITEUP.md).
- It doesn't catch everything. Also check Handshake, LinkedIn, and [Simplify's internship lists](https://github.com/SimplifyJobs).
- Found a missing posting, a broken link, or a mistake? [Open a GitHub issue](https://github.com/rohitpeets/cs-internships-and-career-guide/issues/new) — anyone can, and we'll fix it.

## ⚖️ Disclaimer

This board is provided as is, without warranty of any kind. Listings and tags are generated automatically from employers' public job postings and can be wrong, incomplete or out of date. Always read the full posting on the employer's site. Citizenship and clearance tags are general information, not legal advice. This project is free, non-commercial, and not affiliated with or endorsed by any employer listed or any university.

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
        "boards": boards, "tracks": track_counts, "terms": term_counts,
        "unverified": stale}, indent=2) + "\n", encoding="utf-8")  # the site shows this next to the counts
    for f in [ROOT / name for _, _, name in SECTIONS] + sum((list(ROOT.glob(f"{name[:-3]}-*.md")) for _, _, name in SECTIONS), []) + [ROOT / "NEW_THIS_WEEK.md", ROOT / "README.md"] + list(ROOT.glob("track-*.md")):
        size = f.stat().st_size
        if size > MAX_PAGE_BYTES:  # GitHub stops rendering markdown at 512 KB; fail before a page silently goes blank
            sys.exit(f"{f.name} is {size:,} bytes, over the {MAX_PAGE_BYTES:,}-byte limit; split it before publishing")
    # search index for the site's cross-page filter (lazy-loaded by site.js on first keystroke)
    idx = []
    for key, _name, fname in SECTIONS:
        stem = fname[:-3]
        part = sorted((r for r in rows if r["section"] == key),
                      key=lambda r: (-date.fromisoformat(when(r)).toordinal(), r["company"].lower(), r["title"].lower()))
        part = [r for r in part if safe_url(r.get("url"))]
        for i, r in enumerate(part):
            page_num = i // MAX_ROWS_PER_PAGE + 1
            page_file = f"{stem}.html" if page_num == 1 else f"{stem}-{page_num}.html"
            idx.append([r["company"], r["title"], norm_location(r.get("location", "")), tag_str(r).replace("<br>", " "), safe_url(r["url"]), page_file])
    (ROOT / "assets" / "search-index.json").write_text(json.dumps(idx, separators=(",", ":")), encoding="utf-8")

    print(f"built: {dict(counts)}, new this week {len(new)}, rows left out for unsafe links {skipped}")


if __name__ == "__main__":
    main()
