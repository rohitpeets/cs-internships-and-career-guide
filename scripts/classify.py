"""Section and tag rules. Imported by the fetchers; run directly to re-classify sections of all postings.

Tags are three-state: True (the posting says so), False (it says the opposite), None (it doesn't say).
Every tag keeps the sentence that triggered it in `tag_evidence`.
"""
import re
import sys
from datetime import date

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from common import POSTINGS, load_json, save_json  # noqa: E402

TITLE_KEEP = re.compile(r"\b(intern(ship)?s?|co-?op|new grad(uate)?|entry[- ]level|early career|university grad(uate)?|graduate program|graduate (software|engineer\w*|developer|program\w*|analyst)|apprentice(ship)?|explore program|freshm[ae]n|sophomore)\b", re.I)
TITLE_DROP = re.compile(r"\b(senior|sr\.?|staff(?! augmentation)|principal|director|manager(?!\s*intern)|lead(?!ership)|phd|ph\.d|postdoc|mba|student worker)\b", re.I)

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
SPONSOR_HEDGE = re.compile(r"clearance|(available|offered|provided|sponsor)\s+(only\s+)?(for|to)\s+(select|exceptional|certain|some)\b|case[- ]by[- ]case|\bmay\b[^.]{0,20}sponsor|\b(cpt|opt|f-?1)\b", re.I)
# citizenship / green card / U.S. person must be stated as a requirement; export-control boilerplate alone doesn't count
CITIZEN = re.compile(
    r"u\.?s\.? citizen(ship)?[^.]{0,60}(required|only|must)|(must|required to) be (a )?u\.?s\.? (citizen|person)|(only|limited to) u\.?s\.? (citizens|persons)"
    r"|(must|required to|requires?|need to)[^.]{0,40}\bu\.?s\.? persons?\b|\bu\.?s\.? persons?\b[^.]{0,40}\b(required|only)"
    , re.I)
# a bare ITAR mention is shown as its own tag ("mentions ITAR"): ITAR roles are often, not always, limited to U.S. persons
ITAR = re.compile(r"\bitar\b", re.I)
CLEARANCE = re.compile(r"(security|secret|top secret|ts/sci|dod|public trust) clearance|clearance (is )?required|(obtain|maintain|hold) (an? |active )?(security )?clearance|\bts/sci\b"
                       r"|public trust (position|background|investigation|eligib\w*)", re.I)
REMOTE = re.compile(r"\bremote\b", re.I)
# F-1 students need CPT (during school) or OPT: a posting that rules those out is closed to them right now, not just later
NOT_REQUIRED = re.compile(r"\b(not|no)\b[^.]{0,20}\b(required|needed|necessary)\b|\bno (security )?clearance\b|:\s*none\b|^none\b", re.I)
NO_CPT = re.compile(r"(does not|doesn't|do not|don't|will not|won't|not|cannot|can't|unable to|no)\s+(\w+\s+){0,3}(accept|consider|support|eligible|available|allow|offer|provide|sponsor)\w*[^.]{0,40}\b(cpt|opt|curricular practical|optional practical|f-?1)\b"
                    r"|\b(cpt|opt|f-?1)\b[^.]{0,40}\b(not (be )?(accepted|eligible|considered|supported)|ineligible)"
                    r"|\bno (cpt|opt)\b", re.I)


NON_TECH = re.compile(r"\b(operations research|financial analy\w*|risk|tax|compliance|audit|pricing|actuarial|underwriting|marketing|sales|account (executive|manager)|finance|accounting|human resources|hr|recruit\w*|legal|paralegal|"
                      r"communications|public relations|customer (experience|success|service)|corporate strategy|supply chain|procurement|"
                      r"artist|graphic design|content|social media|events?|administrative|operations intern|game presentation|"
                      r"civil|geotechnical|structural|traffic|transportation|mechanical|environmental|chemical|process engineer|"
                      r"manufacturing|industrial|ehs|health and safety|safety engineer|construction|mining|petroleum|materials|"
                      r"warhead|harness|propulsion|thermal|fluids|geolog\w*|surveying|architect(ure)? intern|water resources|"
                      r"game design|game economy|tech art|fuel|trim|field manager|product manag\w*)\b", re.I)


FIELD_DROP = re.compile(r"\b(facilit(y|ies)|electrical engineer\w*|packaging|photonics|mechanic|diesel|maintenance|technician|civil|geotechnical|structural|traffic|transportation|mechanical|environmental|chemical|process|manufacturing|industrial|ehs|safety|construction|mining|petroleum|materials|warhead|harness|propulsion|thermal|fluids|surveying|water resources|game presentation|game design|game economy|tech art|fuel|trim|field engineer)\b", re.I)
STRONG_TECH = re.compile(r"\b(engineer(ing)?|developer|software|data scien\w*|data analy\w*|machine learning|information technology|it|erp|cyber\w*)\b", re.I)
# business areas a technical word can't rescue: "Tax & Data Analytics Intern" is a tax job
NO_RESCUE = re.compile(r"\b(sales|marketing|tax|audit|accounting|actuarial|operations research)\b", re.I)
PAST_TERM = re.compile(r"\b(spring|summer|fall|autumn|winter)?\s*[-–]?\s*(20\d\d)\s*[-–]?\s*(spring|summer|fall|autumn|winter)?\b", re.I)
GRAD_ONLY = re.compile(r"\b(ms|m\.s\.|masters?|master's|graduate (students?|level))\b", re.I)
UNDERGRAD = re.compile(r"\b(bs|b\.s\.|bachelor'?s?|undergrad\w*)\b", re.I)


NON_US = re.compile(r"\b(united kingdom|uk|england|scotland|wales|london|glasgow|edinburgh|belfast|northampton|ireland|dublin|cork|galway|"
    r"netherlands|amsterdam|eindhoven|rotterdam|germany|berlin|munich|hamburg|frankfurt|stuttgart|cologne|france|paris|lyon|toulouse|grenoble|suresnes|aubervilliers|"
    r"spain|madrid|barcelona|portugal|lisbon|italy|milan|rome|switzerland|zurich|geneva|belgium|brussels|austria|vienna|denmark|copenhagen|"
    r"sweden|stockholm|norway|oslo|finland|helsinki|poland|warsaw|krakow|wroclaw|gdansk|czech\w*|prague|brno|romania|bucharest|hungary|budapest|"
    r"greece|athens|turkey|istanbul|ukraine|kyiv|lithuania|vilnius|estonia|tallinn|latvia|riga|serbia|belgrade|croatia|bulgaria|"
    r"india|bangalore|bengaluru|hyderabad|pune|chennai|mumbai|delhi|noida|gurgaon|gurugram|kolkata|ahmedabad|sri lanka|colombo|pakistan|bangladesh|"
    r"canada|canadian|cad|toronto|vancouver|montreal|montréal|quebec|québec|ontario|ottawa|calgary|edmonton|mississauga|winnipeg|halifax|"
    r"singapore|malaysia|penang|kuala lumpur|vietnam|ho chi minh|hanoi|thailand|bangkok|indonesia|jakarta|philippines|manila|cebu|"
    r"hong kong|china|shanghai|beijing|shenzhen|guangzhou|chengdu|hangzhou|suzhou|taiwan|taipei|hsinchu|japan|tokyo|osaka|kyoto|korea|seoul|"
    r"australia|sydney|melbourne|brisbane|new zealand|auckland|israel|tel aviv|haifa|herzliya|jerusalem|"
    r"uae|dubai|abu dhabi|qatar|doha|saudi\w*|riyadh|egypt|cairo|nigeria|lagos|kenya|nairobi|south africa|johannesburg|cape town|"
    r"mexico|guadalajara|monterrey|brazil|são paulo|sao paulo|blumenau|argentina|buenos aires|chile|colombia|bogota|bogotá|peru|costa rica|guatemala|"
    r"lausanne|valbonne|sophia antipolis|knutsford|sgp|"
    r"armenia|yerevan|tbilisi|kazakhstan|almaty|uzbekistan|tashkent|morocco|casablanca|tunisia|ghana|accra|jordan|amman|lebanon|beirut|cyprus|malta|"
    r"luxembourg|iceland|slovakia|bratislava|slovenia|ljubljana|belarus|minsk|moldova|ecuador|quito|uruguay|montevideo|panama|dominican republic|"
    r"bahrain|kuwait|oman|nepal|kathmandu|cambodia|mongolia|basel|getafe|lysaker|north york|tan uyen|zaragoza|warszawa|wuxi|jiangsu|ovar|babenhausen|"
    r"emea|apac|latam|europe)\b", re.I)
# country codes ("Zaragoza, ESP", "BRA", "Ovar, PT"); two-letter codes that are also US states are left out on purpose
COUNTRY_CODE = re.compile(r"\b(BRA|ESP|PRT|POL|CHN|IRL|DEU|GBR|CAN|MEX|FRA|ITA|NLD|SWE|JPN|KOR|SGP|AUS|ISR|ARE|ROU|CZE|HUN|AUT|CHE|BEL|DNK|NOR|FIN|PHL|VNM|MYS|THA|IDN|TWN|HKG|ARG|CHL|COL|CRI|ZAF|EGY|TUR|GRC|IND)\b"
                          r"|,\s*(PT|PL|ES|MX|BR|SE|MY|VN|CN|IE|GB|UK|FR|NL|JP|KR|SG|AU|AE|RO|CZ|HU|AT|CH|BE|DK|NO|FI|PH|TH|TW|HK|CL|CR|ZA|EG|TR|GR)\s*$")
US_MARK = re.compile(r"(?i:\b(united states|usa|u\.s\.a?\.?)(?!\w))|\bUS\b")


US_STATE_END = re.compile(r",\s*(AL|AK|AZ|AR|CA|CO|CT|DE|DC|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY|PR)"
                          r"\s*(,\s*(?i:us|usa|united states( of america)?))?\s*$")


def us_job(location: str) -> bool:
    """Drop non-US jobs. "Athens, GA" and "Dublin, CA" are US: a city followed by a state code at the end wins.
    "Blumenau, SC, Brazil" isn't South Carolina, because the code isn't at the end. Otherwise a location naming another
    country or city counts as US only if it also says "United States"/"US" (multi-location postings)."""
    loc = (location or "").strip()
    parts = [p.strip() for p in loc.split(",") if p.strip()]
    if ";" not in loc and "|" not in loc and len(parts) >= 3 and re.fullmatch(r"[A-Z]{2}", parts[-1]):
        # "City, Region, CC": the last code is a country ("Toronto, ON, CA" is Canada, "Bengaluru, KA, IN" is India),
        # unless it's US, or a state after a county-style name ("Indianapolis, Marion County, IN")
        if parts[-1] == "US":
            return True
        if re.fullmatch(r"[A-Z]{2}", parts[-2]) or not US_STATE_END.search(loc):
            return False
    if US_STATE_END.search(loc):
        return True
    return not (NON_US.search(loc) or COUNTRY_CODE.search(loc)) or bool(US_MARK.search(loc))


# campus-specific reqs ("HEC Engineer Intern - LSU") are only open to that school's students
OTHER_SCHOOL = re.compile(r"-\s*(colorado school of mines|montana( state| tech)?|lsu|texas a&m|a&m|ou|clemson|ut|tulsa|purdue|georgia tech|"
                          r"[a-z .&]+ (university|college|state))\s*$", re.I)


# Allow-list: the title has to name CS or computer-engineering work. "Engineer" or "analyst" alone isn't enough.
CS_TITLE = re.compile(
    r"\b(robotic\w*|applied scientist|gpu|cuda|dft|(software|hardware|electrical|silicon|firmware|design) (validation|verification)|validation engineer\w*|fpga|asic|test automation|automation test\w*|erp|telecom\w*|software|developer|programmer\w*|programming|coding|data|machine learning|deep learning|ml|ai|a\.i\.|artificial intelligence|llm|nlp|"
    r"computer|cs|swe|cyber\w*|(information|network|cloud|application|product|software|it|data) security|security (engineer\w*|analyst|operations|research\w*)|offensive security|appsec|penetration test\w*|pentest\w*|information technology|it|information systems|network (engineer\w*|administrat\w*|operations|infrastructure|analyst)|networking|cloud|devops|sre|site reliability|"
    r"web|mobile (app\w*|developer|software|engineer\w*)|android|ios|full[- ]?stack|front[- ]?end|back[- ]?end|firmware|embedded|database|analytics|bioinformatics|"
    r"quant\w*|automation engineer\w*|robotics software|autonomy|computer vision|perception|slam|infrastructure engineer\w*|"
    r"platform engineer\w*|systems? administrat\w*|help ?desk|technical support|qa (engineer\w*|automation|test\w*|analyst)|software (qa|quality|test\w*)|quality assurance (engineer\w*|automation|analyst)|sdet|test automation|"
    r"technology intern\w*|tech intern\w*|technology (analyst|associate|program)|digital (design|technology)|"
    r"hardware|asic|fpga|vlsi|chip|silicon|semiconductor|soc|digital design|verification|signal processing|dsp|"
    r"computer engineering|electrical (and|&) computer|game (developer|engine|programmer)|gameplay|(computer|real-time) graphics|graphics (software|engineer\w*|programmer)|simulation software|solutions engineer\w*)\b", re.I)
# Visual and creative design roles ("Creative & Digital Design", "Web Designer") aren't CS/CE work.
# Chip and circuit design ("Digital Design Engineer", "ASIC Design") is, so those words keep a title.
VISUAL_DESIGN = re.compile(r"\b(creative|(product|web|ux|ui|ux/ui|ui/ux|visual|graphic|brand|interaction|motion) designers?)\b", re.I)
CHIP_DESIGN = re.compile(r"\b(engineer\w*|asic|fpga|rtl|vlsi|silicon|chip|circuit|analog|electronics|hardware|pcb|ic|soc)\b", re.I)
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
    if FIELD_DROP.search(title) and not re.search(r"\b(software|developer|programmer|firmware|embedded|computer|data scien\w*|it)\b", title, re.I):
        return False
    if expired_term(title):
        return False
    if VISUAL_DESIGN.search(title) and not CHIP_DESIGN.search(title):
        return False
    return not NON_TECH.search(title) or (bool(STRONG_TECH.search(title)) and not NO_RESCUE.search(title))


def expired_term(title: str, today: date | None = None) -> bool:
    """ "2026 Summer Intern" listed in November 2026 is over. A term counts as past once its season has started:
    spring after February, summer after July, fall after October, winter after January of that year."""
    today = today or date.today()
    starts = {"winter": 1, "spring": 3, "summer": 8, "fall": 11, "autumn": 11}
    for m in PAST_TERM.finditer(title):
        year, season = int(m.group(2)), (m.group(1) or m.group(3) or "").lower()
        if year < today.year:
            return True
        if year == today.year and season and today.month >= starts[season]:
            return True
    return False


def early_evidence(title: str, text: str = "") -> str | None:
    """The sentence (or title) that makes a posting an early program; shown on EARLY.md so students can check it."""
    if EARLY.search(title):
        return title
    m = EARLY_TEXT.search((text or "")[:3000])
    if not m:
        return None
    return next((x for x in sentences(text[:3000]) if EARLY_TEXT.search(x)), m.group(0))[:300]


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
    out = []
    for x in SENT_END.split(text or ""):
        x = " ".join(x.split())
        if not x:
            continue
        if out and re.search(r"(^|[\s(])[A-Za-z]\.$", out[-1]):  # a line break inside "e.g." or "U.S.": rejoin
            out[-1] += " " + x
        else:
            out.append(x)
    return out


def _hit(sents, rx, skip=None):
    """First sentence matching rx. A heading ("ITAR Requirement:") is read together with the line after it,
    since the heading alone doesn't say what's required. skip(text) rejects a match (e.g. "Clearance: None")."""
    for i, x in enumerate(sents):
        full = f"{x} {sents[i + 1]}" if x.endswith(":") and i + 1 < len(sents) else x
        if rx.search(full) and not (skip and skip(full)):
            return full
    return None


# ---- tracks and terms: read from the title only, so they're set at build time for every stored row ----
# One primary track per row, first match wins. Specific roles (security, embedded, hardware, a named data or IT role)
# beat "software"; a passing mention ("Software Engineer, AI Platform") stays software. Anything else CS-generic is software.
TRACKS = [("software", "Software"), ("embedded", "Embedded and firmware"), ("hardware", "Hardware and chips"),
          ("security", "Security"), ("it", "IT and networking"), ("data", "Data, ML and AI"), ("gov", "Government and defense")]
SECURITY_T = re.compile(r"\b(cyber\w*|security|pen(etration)?[- ]?test\w*|pentest\w*|soc analyst|security operations|appsec|red team|blue team|threat|vulnerabilit\w*|malware|forensic\w*)\b", re.I)
EMBEDDED_T = re.compile(r"\b(firmware|embedded|rtos|real[- ]time operating|micro-?controllers?|bare[- ]metal)\b", re.I)
HARDWARE_T = re.compile(r"\b(fpga|asic|rtl|vlsi|silicon|chips?|semiconductor|soc|system[- ]on[- ]chip|dft|digital design|physical design|"
                        r"(design|hardware|pre-?silicon|post-?silicon) (verification|validation)|verification engineer\w*|hardware)\b", re.I)
SOFTWARE_T = re.compile(r"\b(software|developer|programmer|swe|sde|full[- ]?stack|front[- ]?end|back[- ]?end|web|mobile|ios|android|game)\b", re.I)
DATA_STRONG = re.compile(r"\b(data scien\w*|data analy\w*|data engineer\w*|machine learning|ml engineer\w*|ai engineer\w*|ai/ml|ml/ai|"
                         r"applied scientist|research scientist|deep learning|computer vision|nlp|business intelligence|analytics)\b", re.I)
DATA_WEAK = re.compile(r"\b(data|ml|ai|a\.i\.|artificial intelligence|llm|generative|agentic|scientist|statistic\w*)\b", re.I)
IT_STRONG = re.compile(r"(?<![\w-])IT(?![\w-])|\b(information technology|information systems|help ?desk|service desk|desktop support|technical support|"
                       r"network (engineer\w*|administrat\w*|operations|analyst|infrastructure)|networking|system(s)? administrat\w*|sysadmin|"
                       r"data center|cloud (engineer\w*|operations|infrastructure)|infrastructure (engineer\w*|operations|analyst))\b")
IT_WEAK = re.compile(r"\b(cloud|infrastructure|devops|site reliability|sre|network\w*|systems engineer\w*)\b", re.I)
IT_STRONG_I = re.compile(IT_STRONG.pattern.split("|", 1)[1], re.I)  # everything but the bare "IT", case-insensitive

# rows on the gov page: a government/lab/defense title, or a posting that requires clearance or U.S. citizenship
GOV = re.compile(r"\b(u\.?s\.? government|government|federal|national lab\w*|laborator(y|ies)|jpl|jet propulsion|nasa|dod|department of (defense|energy)|"
                 r"navy|naval|army|air force|space force|missile|defense)\b", re.I)

TERMS = [("co_op", re.compile(r"\b(co-?op|co-?operative education)\b", re.I)), ("fall", re.compile(r"\b(fall|autumn)\b", re.I)),
         ("spring", re.compile(r"\bspring\b", re.I)), ("part_time", re.compile(r"\bpart[- ]?time\b", re.I))]


def track(title: str) -> str:
    """The posting's main track, from its title. Used for the track-*.md pages."""
    t = title or ""
    if SECURITY_T.search(t) and not re.search(r"\bsoc\b(?! analyst)", t, re.I):  # "SoC" is a chip, "SOC analyst" is security
        return "security"
    if EMBEDDED_T.search(t):
        return "embedded"
    if HARDWARE_T.search(t) and not re.search(r"\bsoftware (verification|validation)\b", t, re.I):
        return "hardware"
    if DATA_STRONG.search(t):
        return "data"
    if IT_STRONG.search(t) or IT_STRONG_I.search(t):
        return "it"
    if SOFTWARE_T.search(t):
        return "software"
    if DATA_WEAK.search(t):
        return "data"
    if IT_WEAK.search(t):
        return "it"
    return "software"


def is_gov(r) -> bool:
    t = r.get("tags") or {}
    return bool(GOV.search(r.get("title", "")) or t.get("clearance") or t.get("citizen"))


def terms(title: str) -> list[str]:
    """Non-summer terms named in the title. Summer is the default and isn't tagged."""
    return [k for k, rx in TERMS if rx.search(title or "")]


# ---- text tags that need the description (set at fetch time) ----
OA = re.compile(r"\b(hackerrank|hacker rank|codesignal|code signal|codility|online (coding )?assessments?)\b", re.I)
GPA_NUM = re.compile(r"(?<![\d./])([234]\.\d{1,2})(?![\d])")  # not the "4.0" in "3.0/4.0"
GPA_MIN_WORD = re.compile(r"\b(minimum|min\.?|at least|no less than|or (higher|above|better|greater)|required|requires?|must)\b|\d\s*\+", re.I)
PREFERRED = re.compile(r"\b(preferred|prefer|desired|a plus|ideally)\b", re.I)
CLEARANCE_LEVELS = [("ts/sci", re.compile(r"\bts\s*/\s*sci\b|\btop secret\s*/\s*sci\b|\bts\s*sci\b", re.I)),
                    ("top secret", re.compile(r"\btop[- ]secret\b|\bTS\b(?!/)", re.I)),
                    ("secret", re.compile(r"\bsecret\b", re.I)),
                    ("public trust", re.compile(r"\bpublic trust\b", re.I))]
POLY = re.compile(r"\b(poly|polygraph|ci[- ]poly|full[- ]scope)\b", re.I)


def min_gpa(sents) -> tuple[float | None, str | None]:
    """The lowest GPA a posting says it requires ("minimum 3.0 GPA", "GPA of 3.5 or higher"). A GPA that's only preferred doesn't count."""
    for x in sents:
        if not re.search(r"\bgpa\b|grade point average", x, re.I) or not GPA_MIN_WORD.search(x):
            continue
        nums = []
        for m in GPA_NUM.finditer(x):
            near = x[max(0, m.start() - 40): m.end() + 40]
            after = x[m.end(): m.end() + 20]
            if not re.search(r"\bgpa\b|grade point", near, re.I) or PREFERRED.search(after):
                continue
            if re.search(r"\bon a\s*$", x[max(0, m.start() - 6): m.start()]) or re.match(r"\s*scale", after):
                continue  # "on a 4.0 scale"
            nums.append(float(m.group(1)))
        if nums:
            return min(nums), x
    return None, None


def clearance_level(text: str) -> str | None:
    """The clearance level named in a sentence: public trust, secret, top secret or ts/sci, plus "+ poly" for a polygraph.
    The first level mentioned wins, so "Secret required; Top Secret preferred" is secret."""
    # earliest mention wins; at the same spot the more specific level wins ("Top Secret/SCI" is ts/sci, not top secret)
    found = [(m.start(), i, name) for i, (name, rx) in enumerate(CLEARANCE_LEVELS) for m in [rx.search(text or "")] if m]
    if not found:
        return None
    name = min(found)[2]
    return name + (" + poly" if POLY.search(text) else "")


def tags(text: str, location: str = "") -> tuple[dict, dict]:
    t, ev = {"sponsor": None, "citizen": None, "clearance": None, "no_cpt": None, "remote": bool(REMOTE.search(location))}, {}
    sents = [x for x in sentences(text) if not re.search(r"export licen[cs]e", x, re.I)]
    no = next((x for x in sents if SPONSOR_NO.search(x)), None)
    yes = next((x for x in sents if SPONSOR_YES.search(x) and not NEG.search(x) and not SPONSOR_HEDGE.search(x)), None)
    if no:  # any "no" sentence wins: a wrong "sponsors" tag costs a student the most
        t["sponsor"], ev["sponsor"] = False, no[:300]
    elif yes:
        t["sponsor"], ev["sponsor"] = True, yes[:300]
    for name, rx in (("citizen", CITIZEN), ("clearance", CLEARANCE), ("no_cpt", NO_CPT)):
        hit = _hit(sents, rx, NOT_REQUIRED.search if name == "clearance" else None)
        if hit:
            t[name], ev[name] = True, hit[:300]
    t["itar"] = None
    if not t["citizen"]:
        hit = _hit(sents, ITAR)
        if hit:
            t["itar"], ev["itar"] = True, hit[:300]
    t["clearance_level"] = None
    if t["clearance"]:  # the level from the tagged sentence, else from another sentence about clearance
        for x in [ev["clearance"]] + [x for x in sents if re.search(r"clearance|ts\s*/\s*sci|polygraph|\bsecret\b|public trust", x, re.I)]:
            lvl = clearance_level(x)
            if lvl:
                t["clearance_level"] = lvl
                break
    t["oa"] = None
    hit = _hit(sents, OA)
    if hit:
        t["oa"], ev["oa"] = True, hit[:300]
    t["min_gpa"], hit = min_gpa(sents)
    if hit:
        ev["min_gpa"] = hit[:300]
    return t, ev


def strip_html(html: str) -> str:
    import html as h
    text = re.sub(r"<(br|/p|/li|/div|/h\d)[^>]*>", "\n", h.unescape(html or ""), flags=re.I)
    return re.sub(r"[ \t]+", " ", re.sub(r"<[^>]+>", " ", text)).strip()


if __name__ == "__main__":
    before = load_json(POSTINGS, [])
    rows = [r for r in before if r.get("source") == "manual" or (keep_title(r["title"]) and us_job(r.get("location", "")))]
    print(f"filter: {len(before)} -> {len(rows)}")
    for r in rows:  # sections are set at fetch time from the full description; only fill gaps here
        r["section"] = r.get("section") or section(r["title"]) or "internship"
    save_json(POSTINGS, rows)
    print(f"classified {len(rows)} postings")
