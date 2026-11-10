"""Write README.md (front page) and one table file per section from postings.json."""
import re
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import DATA, POSTINGS, ROOT, load_json, load_yaml, today  # noqa: E402

SECTIONS = [("internship", "Internships", "INTERNSHIPS.md"),
            ("new_grad", "New Grad", "NEW_GRAD.md"),
            ("early", "Early Programs (freshmen & sophomores)", "EARLY.md")]
LEGEND = """**Tags.** 🛂✅ the posting says it sponsors visas · 🛂❌ it says it doesn't · 🇺🇸 limited to U.S. citizens, green-card holders or U.S. persons (often ITAR) · 🔒 security clearance · 🌐 remote · ⚠ link couldn't be verified recently · ⏳ listed for 60+ days.
A blank tag means the posting doesn't say.

> 🛂❌ usually refers to future visa sponsorship (for example H-1B). It doesn't necessarily mean CPT or OPT can't be used. Check with the recruiter and your DSO."""


STATES = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut",
          "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
          "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
          "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
          "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
          "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
          "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
          "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
          "PR": "Puerto Rico"}
CITIES = {"new york": "New York", "nyc": "New York", "san francisco": "California", "bay area": "California", "los angeles": "California",
          "seattle": "Washington", "boston": "Massachusetts", "austin": "Texas", "houston": "Texas", "dallas": "Texas", "chicago": "Illinois",
          "atlanta": "Georgia", "denver": "Colorado", "washington, d": "District of Columbia", "new orleans": "Louisiana", "baton rouge": "Louisiana",
          "lake charles": "Louisiana", "lafayette, la": "Louisiana", "pittsburgh": "Pennsylvania", "philadelphia": "Pennsylvania",
          "san jose": "California", "mountain view": "California", "sunnyvale": "California", "santa clara": "California", "palo alto": "California",
          "san diego": "California", "irvine": "California", "plano": "Texas", "irving": "Texas", "san antonio": "Texas", "fort worth": "Texas",
          "tarrytown": "New York", "rensselaer": "New York", "sleepy hollow": "New York", "boise": "Idaho", "indianapolis": "Indiana",
          "omaha": "Nebraska", "parsippany": "New Jersey", "charlotte": "North Carolina", "raleigh": "North Carolina", "phoenix": "Arizona",
          "minneapolis": "Minnesota", "detroit": "Michigan", "columbus": "Ohio", "nashville": "Tennessee", "miami": "Florida",
          "orlando": "Florida", "tampa": "Florida", "salt lake": "Utah", "portland": "Oregon", "st. louis": "Missouri", "st louis": "Missouri",
          "kansas city": "Missouri", "milwaukee": "Wisconsin", "madison": "Wisconsin", "bentonville": "Arkansas", "huntsville": "Alabama"}
GULF = ["Louisiana", "Texas", "Mississippi", "Alabama", "Florida"]
GROUP_LAST = ["Remote", "Multiple locations", "Location not listed"]


def state_of(loc: str) -> str:
    """Group a posting under one state. Several states -> "Multiple locations"; only "remote" -> "Remote"."""
    loc = loc or ""
    found = {STATES[c] for c in re.findall(r"(?<![A-Za-z])([A-Z]{2})(?![A-Za-z])", loc) if c in STATES}
    low = loc.lower()
    found |= {name for name in STATES.values() if re.search(rf"\b{name.lower()}\b", low)}
    found |= {st for city, st in CITIES.items() if city in low}
    if len(found) == 1:
        return found.pop()
    if len(found) > 1 or re.search(r"multiple|various|\d+ locations", low):
        return "Multiple locations"
    if "remote" in low:
        return "Remote"
    return "Location not listed" if not loc.strip() or re.fullmatch(r"(?i)\s*(united states|usa|us|u\.s\.)\s*", loc) else "Multiple locations" if ";" in loc else "Location not listed"


def dedupe(rows):
    """Same company + title + location shown once (companies often post one job under several links)."""
    best = {}
    for r in rows:
        k = (r["company"].lower().strip(), r["title"].lower().strip(), (r.get("location") or "").lower().strip())
        if k not in best or r["first_seen"] < best[k]["first_seen"]:
            best[k] = r
    return list(best.values())


def anchor(name: str) -> str:
    return re.sub(r"[^a-z0-9 -]", "", name.lower()).replace(" ", "-")


def cell(s: str) -> str:
    return (s or "").replace("|", "/").replace("\n", " ").strip()


def tag_str(r) -> str:
    t, out = r.get("tags") or {}, []
    if t.get("sponsor") is True:
        out.append("🛂✅")
    elif t.get("sponsor") is False:
        out.append("🛂❌")
    if t.get("citizen"):
        out.append("🇺🇸")
    if t.get("clearance"):
        out.append("🔒")
    if t.get("remote"):
        out.append("🌐")
    if r.get("status") == "uncertain":
        out.append("⚠")
    if date.fromisoformat(r["first_seen"]) < date.today() - timedelta(days=60):
        out.append("⏳")
    return " ".join(out)


def added(d: str) -> str:
    return date.fromisoformat(d).strftime("%b %-d") if sys.platform != "win32" else date.fromisoformat(d).strftime("%b %#d")


def table(rows, why=False) -> str:
    head = "| Company | Role | Location | Tags | Added |" + (" Why it's listed |" if why else "")
    lines = [head, "|---|---|---|---|---|" + ("---|" if why else "")]
    for r in sorted(rows, key=lambda r: (-date.fromisoformat(r["first_seen"]).toordinal(), r["company"].lower(), r["title"].lower())):
        line = f"| {cell(r['company'])} | [{cell(r['title'])}]({r['url']}) | {cell(r['location'])[:60]} | {tag_str(r)} | {added(r['first_seen'])} |"
        if why:
            line += f" {cell((r.get('tag_evidence') or {}).get('early', ''))[:160]} |"
        lines.append(line)
    return "\n".join(lines)


def grouped(rows) -> str:
    """One table per state, Gulf Coast first, so a student can jump to where they'd actually live."""
    by = defaultdict(list)
    for r in rows:
        by[state_of(r.get("location", ""))].append(r)
    order = [g for g in GULF if g in by] + sorted(g for g in by if g not in GULF and g not in GROUP_LAST) + [g for g in GROUP_LAST if g in by]
    index = " · ".join(f"[{g} ({len(by[g])})](#{anchor(g)})" for g in order)
    parts = [f"**Jump to a state:** {index}"]
    for g in order:
        parts.append(f"## {g}\n\n{table(by[g])}\n\n[⬆ Top](#top)")
    return "\n\n".join(parts)


def new_section(new, launched: str) -> str:
    start = date.fromisoformat(launched) + timedelta(days=7)
    if date.today() < start:  # launch week: every posting is "new", so the list would just repeat the board
        return f"_The board started on {added(launched)}. From {added(start.isoformat())}, this list shows postings added in the past 7 days._"
    if not new:
        return "_Nothing new this week yet._"
    if len(new) > 150:  # a big new source was added this week
        return f"_{len(new)} postings were added this week (a new source was connected). Browse the sections above._"
    shown = table(new[:75])
    return shown if len(new) <= 75 else shown + f"\n\nShowing the 75 newest of {len(new)}. The rest are in the section pages above."


def main():
    rows = dedupe(load_json(POSTINGS, []))
    counts = Counter(r["section"] for r in rows)
    week_ago = (date.today() - timedelta(days=7)).isoformat()
    launched = min((r["first_seen"] for r in rows), default=today())
    new = [r for r in rows if r["first_seen"] >= week_ago]

    intro = {"early": "Postings that say freshmen or sophomores can apply, or programs built for them. "
                      "The last column shows the sentence from the posting, so you can check it.\n\n"
                      "Big-company programs like Google STEP, Microsoft Explore and Meta University aren't read by this board yet. "
                      "Check their student career pages directly in the fall.\n\n"}
    for key, name, fname in SECTIONS:
        part = [r for r in rows if r["section"] == key]
        body = table(part, why=True) if key == "early" else grouped(part)
        (ROOT / fname).write_text(f"<a id=\"top\"></a>\n\n# {name}\n\n[⬅ Back to the main page](README.md) · {len(part)} open · updated {today()}\n\n"
                                  f"{intro.get(key, '')}**Click a job title to open the company's application page.**\n\n{LEGEND}\n\n{body}\n", encoding="utf-8")

    must = (load_yaml(DATA / "must_have.yaml", {}) or {}).get("companies") or []
    names = " ".join(r["company"].lower() for r in rows)
    missing = [m for m in must if m.lower() not in names]
    not_yet = (f"**Not on this board yet:** {', '.join(missing)}. These companies hire CS interns, but their job sites aren't read here yet. "
               f"Check their careers pages directly.") if missing else ""

    icons = {"internship": "💼", "new_grad": "🎓", "early": "🌱"}
    links = "\n".join(f"| {icons[key]} **{name}** | {counts.get(key, 0)} | **[👉 Open the list]({fname})** |" for key, name, fname in SECTIONS)
    readme = f"""# McNeese Jobs

Internships, new-grad roles and early programs for McNeese computer science and computer engineering students.
Pulled straight from companies' own job boards and refreshed daily. **Last updated {today()}.**

## Find jobs

**Click "👉 Open the list"** next to a section to see its jobs. Each job title in a list is a link to the company's application page.

| Section | Open roles | Link |
|---|---|---|
{links}

Each list is grouped by state, with Louisiana and the Gulf Coast first. Tags come only from a sentence in the posting itself. A blank tag means the posting doesn't say, not "no".

This board doesn't cover everything. It reads about half of what paid job aggregators list. For more, also check Handshake, LinkedIn, and the community internship lists on GitHub.

{not_yet}

{LEGEND}

## 🆕 New this week

{new_section(new, launched)}

---
Found a posting that should be here? Tell an ACM officer.
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    print(f"built: {dict(counts)}, new this week {len(new)}")


if __name__ == "__main__":
    main()
