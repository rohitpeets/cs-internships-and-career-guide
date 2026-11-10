"""Write README.md (front page) and one table file per section from postings.json."""
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import POSTINGS, ROOT, load_json, today  # noqa: E402

SECTIONS = [("internship", "Internships", "INTERNSHIPS.md"),
            ("new_grad", "New Grad", "NEW_GRAD.md"),
            ("early", "Early Programs (freshmen & sophomores)", "EARLY.md")]
LEGEND = """**Tags.** 🛂✅ the posting says it sponsors visas · 🛂❌ it says it doesn't · 🇺🇸 U.S. citizenship / U.S. person required · 🔒 security clearance · 🌐 remote · ⚠ link couldn't be verified recently · ⏳ listed for 60+ days.
A blank tag means the posting doesn't say.

> 🛂❌ usually refers to future visa sponsorship (for example H-1B). It doesn't necessarily mean CPT or OPT can't be used. Check with the recruiter and your DSO."""


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


def table(rows) -> str:
    lines = ["| Company | Role | Location | Tags | Added |", "|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["first_seen"], r["company"].lower()), reverse=True):
        lines.append(f"| {cell(r['company'])} | [{cell(r['title'])}]({r['url']}) | {cell(r['location'])[:60]} | {tag_str(r)} | {r['first_seen'][5:]} |")
    return "\n".join(lines)


def new_section(new) -> str:
    if not new:
        return "_Nothing new this week yet._"
    if len(new) > 150:  # launch week (or a big new source): everything is "new", so point to the sections instead
        return "_Lots of postings were added this week, so browse the sections above. This list shows the newest additions once things settle._"
    shown = table(new[:75])
    return shown if len(new) <= 75 else shown + f"\n\nShowing the 75 newest of {len(new)}. The rest are in the section pages above."


def main():
    rows = load_json(POSTINGS, [])
    counts = Counter(r["section"] for r in rows)
    week_ago = (date.today() - timedelta(days=7)).isoformat()
    new = [r for r in rows if r["first_seen"] >= week_ago]

    for key, name, fname in SECTIONS:
        part = [r for r in rows if r["section"] == key]
        (ROOT / fname).write_text(f"# {name}\n\n[← back to the board](README.md) · {len(part)} open · updated {today()}\n\n{LEGEND}\n\n{table(part)}\n", encoding="utf-8")

    links = " · ".join(f"[{name}]({fname}) ({counts.get(key, 0)})" for key, name, fname in SECTIONS)
    readme = f"""# McNeese Jobs

Internships, new-grad roles and early programs for McNeese computer science and computer engineering students.
Pulled straight from companies' own job boards and refreshed daily. **Last updated {today()}.**

**Browse:** {links}

This board isn't the most complete one out there. It focuses on tags you can trust, Gulf Coast and local companies, and programs for freshmen and sophomores. For more breadth, also check Handshake, LinkedIn, and the community internship lists on GitHub.

{LEGEND}

## 🆕 New this week ({len(new)})

{new_section(new)}

---
Found a posting that should be here? Tell an ACM officer.
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    print(f"built: {dict(counts)}, new this week {len(new)}")


if __name__ == "__main__":
    main()
