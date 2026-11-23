"""Compare this board's companies against Simplify's Summer 2027 list."""
import re
import sys
from pathlib import Path

def normalize(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())

def extract_simplify_companies(readme):
    pattern = re.compile(
        r'<td><strong><a [^>]*>([^<]+)</a></strong></td>\s*'
        r'<td>([^<]*)</td>\s*'
        r'<td>([^<]*(?:<br>[^<]*)*)</td>',
        re.DOTALL,
    )
    rows = []
    for m in pattern.finditer(readme):
        company = m.group(1).strip()
        title = m.group(2).strip()
        location = m.group(3).replace("<br>", ", ").strip()
        rows.append((company, title, location))
    return rows

def load_board_companies(repo):
    """Get company names from data/companies.yaml and data/manual.yaml."""
    import yaml
    companies = set()
    
    # companies.yaml
    cy = repo / "data" / "companies.yaml"
    if cy.exists():
        with open(cy, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for section in (data or {}).values():
            if isinstance(section, list):
                for entry in section:
                    if isinstance(entry, dict) and "name" in entry:
                        companies.add(normalize(entry["name"]))
    
    # manual.yaml
    my = repo / "data" / "manual.yaml"
    if my.exists():
        with open(my, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for p in (data or {}).get("postings", []):
            if isinstance(p, dict) and "company" in p:
                companies.add(normalize(p["company"]))
    
    return companies

def main():
    repo = Path(__file__).resolve().parent.parent
    simplify_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\Users\rohit\projects\simplify-compare\README.md")

    simplify_text = simplify_path.read_text(encoding="utf-8")
    simplify_rows = extract_simplify_companies(simplify_text)

    # Unique companies in Simplify (US-only, skip non-US locations)
    non_us = ("Canada", "UK", "Germany", "India", "Singapore", "Japan",
              "Australia", "Ireland", "Netherlands", "France", "Italy",
              "Spain", "China", "Korea", "Israel", "Sweden", "Switzerland",
              "Denmark", "Finland", "Norway", "Belgium", "Austria", "Poland",
              "Czech", "Brazil", "Mexico", "Taiwan", "Hong Kong")
    us_rows = [(c, t, loc) for c, t, loc in simplify_rows
               if not any(x in loc for x in non_us)]
    simplify_companies = {}
    for c, t, loc in us_rows:
        key = normalize(c)
        if key not in simplify_companies:
            simplify_companies[key] = c

    board_companies = load_board_companies(repo)

    matched = {k for k in simplify_companies if k in board_companies}
    missing = {k: simplify_companies[k] for k in simplify_companies if k not in board_companies}

    total = len(simplify_companies)
    covered = len(matched)
    pct = covered / total * 100 if total else 0

    print(f"Simplify US companies: {total}")
    print(f"On this board:         {covered}")
    print(f"Coverage:              {pct:.1f}%")
    print(f"\nNot on this board ({len(missing)}):")
    for name in sorted(missing.values(), key=str.lower):
        print(f"  {name}")

if __name__ == "__main__":
    main()
