"""Section and tag rules. Imported by the fetchers; run directly to re-classify sections of all postings.

Tags are three-state: True (the posting says so), False (it says the opposite), None (it doesn't say).
Every tag keeps the sentence that triggered it in `tag_evidence`.
"""
import re
import sys
from datetime import date

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from common import POSTINGS, load_json, save_json  # noqa: E402

TITLE_KEEP = re.compile(r"\b(intern(ship)?s?|co-?op|new grad(uate)?|entry[- ]level|early career|university grad(uate)?|graduate program|apprentice(ship)?|explore program|freshm[ae]n|sophomore)\b", re.I)
TITLE_DROP = re.compile(r"\b(senior|sr\.?|staff|principal|director|manager(?!\s*intern)|lead(?!ership)|phd|ph\.d|postdoc|mba|student worker)\b", re.I)

EARLY = re.compile(r"\b(freshm[ae]n|sophomores?|first[- ]year|second[- ]year|explore (intern|program)|step intern|engineering practicum)\b", re.I)
EARLY_TEXT = re.compile(r"\b(freshm[ae]n|sophomores?)\b[^.]{0,60}\b(eligible|encouraged|welcome|open to|apply|students)\b|\b(open to|for|eligible:?)\s+(current\s+)?(freshm[ae]n|sophomores?)\b|\b(open to|for|eligible:?)\s+(current\s+)?(first[- ]year|second[- ]year)\b[^.]{0,40}\b(students|undergrad\w*)", re.I)
NEW_GRAD = re.compile(r"\b(new grad(uate)?s?|entry[- ]level|university grad(uate)?|early career|graduate program)\b", re.I)
INTERN = re.compile(r"\b(intern(ship)?s?|co-?op)\b", re.I)

NEG = re.compile(r"\b(no|not|unable|cannot|can't|won't|without|neither|nor)\b", re.I)
SPONSOR_NO = re.compile(
    r"(unable|not able|will not|won't|cannot|can't|can ?not|does not|doesn't|do not|don't|is not able|are not able|not in a position)\s+(to\s+)?(\w+\s+){0,3}(sponsor|offer (visa |employment )?sponsorship)"
    r"|\bno\b[^.]{0,40}\bsponsorship"
    r"|without (the )?(need for |requiring )?(current or future )?(visa |employer |employment |immigration )?sponsorship"
    r"|not eligible for (visa |immigration )?sponsorship"
    r"|sponsorship\b[^.]{0,20}\b(do|does|will|can) not\b"
    r"|sponsorship[^.]{0,40}\b(is|are|will be) not (available|provided|offered)"
    r"|(require|need)s? (visa |immigration |employment )?sponsorship[^.]{0,80}\b(not be considered|ineligible|not eligible)"
    r"|(does not|doesn't|will not|won't|not) (accept|consider) (cpt|opt|f-?1)", re.I)
# a firm offer only: CPT/OPT eligibility isn't sponsorship, and "for select roles/candidates" isn't a promise
SPONSOR_YES = re.compile(
    r"\b(we|will|can|able to|happy to|willing to)\s+(\w+\s+){0,2}sponsor"
    r"|sponsorship (is )?(available|provided|offered)", re.I)
SPONSOR_HEDGE = re.compile(r"(available|offered|provided|sponsor)\s+(only\s+)?(for|to)\s+(select|exceptional|certain|some)\b|case[- ]by[- ]case|\bmay\b[^.]{0,20}sponsor|\b(cpt|opt|f-?1)\b", re.I)
# citizenship / green card / U.S. person must be stated as a requirement; export-control boilerplate alone doesn't count
CITIZEN = re.compile(
    r"u\.?s\.? citizen(ship)?[^.]{0,60}(required|only|must)|(must|required to) be (a )?u\.?s\.? (citizen|person)|(only|limited to) u\.?s\.? (citizens|persons)"
    r"|(must|required to|requires?|need to)[^.]{0,40}\bu\.?s\.? persons?\b|\bu\.?s\.? persons?\b[^.]{0,40}\b(required|only)"
    r"|\bitar\b", re.I)  # ITAR roles are limited to U.S. persons; generic "comply with export control laws" doesn't count
CLEARANCE = re.compile(r"(security|secret|top secret|ts/sci|dod) clearance|clearance (is )?required|(obtain|maintain|hold) (an? |active )?(security )?clearance|\bts/sci\b", re.I)
REMOTE = re.compile(r"\bremote\b", re.I)


# the board is for CS / computer engineering students: keep technical roles only
TECH = re.compile(r"\b(robotic\w*|applied scientist|gpu|cuda|dft|(software|hardware|electrical|silicon|firmware|design) (validation|verification)|validation engineer\w*|fpga|asic|test automation|automation test\w*|erp|telecom\w*|software|developer|engineer(ing)?|data|machine learning|ml|a\.?i\.?|artificial intelligence|computer|cyber|security|"
                  r"it|information technology|network|cloud|devops|sre|site reliability|infrastructure|platform|embedded|firmware|hardware|"
                  r"electrical|robotics|autonomy|computer vision|systems|research|analytics|analyst|quant(itative)?|product manag\w*|"
                  r"technical program|qa|test|automation|web|mobile|android|ios|full[- ]?stack|front[- ]?end|back[- ]?end|game|graphics|"
                  r"database|bioinformatics|scientist|technology|tech|slam|mapping|perception|estimation|autonomous|controls?|tooling|simulation)\b", re.I)
NON_TECH = re.compile(r"\b(marketing|sales|account (executive|manager)|finance|accounting|human resources|hr|recruit\w*|legal|paralegal|"
                      r"communications|public relations|customer (experience|success|service)|corporate strategy|supply chain|procurement|"
                      r"artist|graphic design|content|social media|events?|administrative|operations intern|game presentation|"
                      r"civil|geotechnical|structural|traffic|transportation|mechanical|environmental|chemical|process engineer|"
                      r"manufacturing|industrial|ehs|health and safety|safety engineer|construction|mining|petroleum|materials|"
                      r"warhead|harness|propulsion|thermal|fluids|geolog\w*|surveying|architect(ure)? intern|water resources|"
                      r"game design|game economy|tech art|fuel|trim|field manager)\b", re.I)


FIELD_DROP = re.compile(r"\b(facilit(y|ies)|civil|geotechnical|structural|traffic|transportation|mechanical|environmental|chemical|process|manufacturing|industrial|ehs|safety|construction|mining|petroleum|materials|warhead|harness|propulsion|thermal|fluids|surveying|water resources|game presentation|game design|game economy|tech art|fuel|trim|field engineer)\b", re.I)
STRONG_TECH = re.compile(r"\b(engineer(ing)?|developer|software|data scien\w*|data analy\w*|analytics|machine learning|information technology|it|erp)\b(?!.*\b(sales|marketing)\b)", re.I)
GRAD_ONLY = re.compile(r"\b(ms|m\.s\.|masters?|master's)\b", re.I)
UNDERGRAD = re.compile(r"\b(bs|b\.s\.|bachelor'?s?|undergrad\w*)\b", re.I)


NON_US = re.compile(r"\b(united kingdom|uk|england|london|ireland|dublin|netherlands|amsterdam|germany|berlin|munich|france|paris|spain|"
                    r"italy|switzerland|zurich|india|bangalore|bengaluru|hyderabad|pune|canada|toronto|vancouver|montreal|ontario|"
                    r"singapore|hong kong|china|shanghai|beijing|japan|tokyo|korea|seoul|australia|sydney|israel|tel aviv|poland|"
                    r"mexico|brazil|argentina|philippines|emea|apac|europe)\b", re.I)
US = re.compile(r"\b(united states|usa|u\.s\.|us|remote|[A-Z][a-z]+,\s*[A-Z]{2})\b")


def us_job(location: str) -> bool:
    """Drop clearly non-US jobs; keep US, US-remote and blank locations."""
    loc = location or ""
    return not NON_US.search(loc) or bool(US.search(loc))


# campus-specific reqs ("HEC Engineer Intern - LSU") are only open to that school's students
OTHER_SCHOOL = re.compile(r"-\s*(colorado school of mines|montana( state| tech)?|lsu|texas a&m|a&m|ou|clemson|ut|tulsa|purdue|georgia tech|"
                          r"[a-z .&]+ (university|college|state))\s*$", re.I)


# Allow-list: the title has to name CS or computer-engineering work. "Engineer" or "analyst" alone isn't enough.
CS_TITLE = re.compile(
    r"\b(robotic\w*|applied scientist|gpu|cuda|dft|(software|hardware|electrical|silicon|firmware|design) (validation|verification)|validation engineer\w*|fpga|asic|test automation|automation test\w*|erp|telecom\w*|software|developer|programm\w*|coding|data|machine learning|deep learning|ml|ai|a\.i\.|artificial intelligence|llm|nlp|"
    r"computer|cs|cyber\w*|security|information technology|it|information systems|network\w*|cloud|devops|sre|site reliability|"
    r"web|mobile|android|ios|full[- ]?stack|front[- ]?end|back[- ]?end|firmware|embedded|database|analytics|bioinformatics|"
    r"quant\w*|automation engineer\w*|robotics software|autonomy|computer vision|perception|slam|infrastructure engineer\w*|"
    r"platform engineer\w*|systems? administrat\w*|help ?desk|technical support|qa|quality assurance|sdet|test automation|"
    r"technology intern\w*|tech intern\w*|technology (analyst|associate|program)|digital (design|technology)|"
    r"hardware|asic|fpga|vlsi|chip|silicon|semiconductor|soc|digital design|verification|signal processing|dsp|"
    r"computer engineering|electrical (and|&) computer|game (developer|engine|programmer)|gameplay|graphics|simulation software)\b", re.I)
INTERNAL_ONLY = re.compile(r"\b(current|previous|recent|returning)\b[^)]{0,40}\binterns?\b[^)]{0,20}\bonly\b|\bfor current\b", re.I)


def keep_title(title: str) -> bool:
    if not CS_TITLE.search(title) or INTERNAL_ONLY.search(title) or NON_US.search(title):
        return False
    if GRAD_ONLY.search(title) and not UNDERGRAD.search(title):
        return False
    if OTHER_SCHOOL.search(title) and not re.search(r"mcneese", title, re.I):
        return False
    if not TITLE_KEEP.search(title) or TITLE_DROP.search(title):  # CS_TITLE above already requires technical work
        return False
    # "Supply Chain Tooling Engineer Intern" is technical even though it names a business area
    if FIELD_DROP.search(title):
        return False
    return not NON_TECH.search(title) or (bool(STRONG_TECH.search(title)) and not re.search(r"\bsales\b", title, re.I))


def section(title: str, text: str = "") -> str | None:
    blob = f"{title}\n{text[:3000]}"
    if EARLY.search(title) or EARLY_TEXT.search(text[:3000]):
        return "early"
    if NEW_GRAD.search(title) and not INTERN.search(title):
        return "new_grad"
    if INTERN.search(title):
        return "internship"
    y = date.today().year
    if re.search(rf"\b(class of|graduat\w*[^.]{{0,30}})({y}|{y + 1})\b", blob, re.I) and not INTERN.search(blob[:500]):
        return "new_grad"
    return None


SENT_END = re.compile(r"(?<=[.!?])(?<!\b[A-Za-z]\.)(?<!e\.g\.)(?<!i\.e\.)(?<!etc\.)\s+(?=[A-Z(])|\n+")


def sentences(text: str) -> list[str]:
    return [" ".join(x.split()) for x in SENT_END.split(text or "") if x and x.strip()]


def tags(text: str, location: str = "") -> tuple[dict, dict]:
    t, ev = {"sponsor": None, "citizen": None, "clearance": None, "remote": bool(REMOTE.search(location))}, {}
    sents = [x for x in sentences(text) if not re.search(r"export licen[cs]e", x, re.I)]
    no = next((x for x in sents if SPONSOR_NO.search(x)), None)
    yes = next((x for x in sents if SPONSOR_YES.search(x) and not NEG.search(x) and not SPONSOR_HEDGE.search(x)), None)
    if no:  # any "no" sentence wins: a wrong "sponsors" tag costs a student the most
        t["sponsor"], ev["sponsor"] = False, no[:300]
    elif yes:
        t["sponsor"], ev["sponsor"] = True, yes[:300]
    for name, rx in (("citizen", CITIZEN), ("clearance", CLEARANCE)):
        hit = next((x for x in sents if rx.search(x)), None)
        if hit:
            t[name], ev[name] = True, hit[:300]
    return t, ev


def strip_html(html: str) -> str:
    import html as h
    text = re.sub(r"<(br|/p|/li|/div|/h\d)[^>]*>", "\n", h.unescape(html or ""), flags=re.I)
    return re.sub(r"[ \t]+", " ", re.sub(r"<[^>]+>", " ", text)).strip()


if __name__ == "__main__":
    rows = load_json(POSTINGS, [])
    for r in rows:  # sections are set at fetch time from the full description; only fill gaps here
        r["section"] = r.get("section") or section(r["title"]) or "internship"
    save_json(POSTINGS, rows)
    print(f"classified {len(rows)} postings")
