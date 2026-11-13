from classify import keep_title, section, tags


def test_titles_kept_and_dropped():
    assert keep_title("Software Engineering Intern - Summer 2027")
    assert keep_title("New Grad Software Engineer")
    assert not keep_title("Senior Software Engineer")
    assert not keep_title("Engineering Manager")
    assert not keep_title("PhD Research Intern")
    assert not keep_title("Summer 2027: Marketing Intern")
    assert not keep_title("Summer 2027: Corporate Strategy Intern")
    assert not keep_title("Technical Design Artist, Intern 2027")
    # visual and creative design roles are not CS/CE work, even when they say "digital design" or "web"
    assert not keep_title("NBC News Creative & Digital Design Internships – Summer 2027")
    assert not keep_title("Product & Web Designer Intern (2027)")
    assert not keep_title("UX/UI Designer Intern")
    assert keep_title("Digital Design Engineer Intern")
    assert keep_title("Analog ASIC Design Intern (Summer 2027)")
    assert keep_title("Electronics Hardware Design Intern")
    assert keep_title("Web Developer Intern")
    assert not keep_title("Firmware Engineer Intern (Graduate Level) (Summer 2027)")
    assert not keep_title("Tencent Cloud CPaaS Product Management Intern")
    assert keep_title("Software Product Management Intern")
    assert keep_title("Summer 2027: Data Analytics Intern")
    assert not keep_title("Electrical Engineering Intern, 2027")  # plain EE: not CS/CE work in the title
    assert keep_title("Summer 2027: IT Services Intern")
    assert not keep_title("Supply Chain Tooling Engineer Intern")
    assert keep_title("2027 Internship State Estimation, Learned Mapping & Semantic SLAM")
    assert not keep_title("Sales Engineer Intern")


def test_sections():
    assert section("Software Engineer Intern") == "internship"
    assert section("Software Engineer, New Grad 2027") == "new_grad"
    assert section("Explore Intern (Freshman/Sophomore)") == "early"
    assert section("Software Engineering Intern", "Open to first-year and second-year students") == "early"


def test_sponsor_no_is_negation_aware():
    t, ev = tags("We are unable to sponsor visas for this role.")
    assert t["sponsor"] is False and "unable to sponsor" in ev["sponsor"]
    assert tags("This role does not offer visa sponsorship now or in the future.")[0]["sponsor"] is False
    assert tags("Candidates must be authorized to work without the need for sponsorship.")[0]["sponsor"] is False


def test_sponsor_yes_only_on_explicit_statement():
    assert tags("We will sponsor work visas for this position.")[0]["sponsor"] is True
    assert tags("F-1 students on CPT are welcome to apply.")[0]["sponsor"] is None  # CPT isn't sponsorship
    assert tags("Sponsorship is available for this position and other select roles.")[0]["sponsor"] is True
    assert tags("Sponsorship available for exceptional candidates.")[0]["sponsor"] is None
    assert tags("Great benefits and a fun team.")[0]["sponsor"] is None


def test_citizen_and_clearance():
    t, _ = tags("Must be a U.S. citizen. This role requires an active Secret clearance.")
    assert t["citizen"] is True and t["clearance"] is True
    assert tags("Applicants must be U.S. persons under ITAR.")[0]["citizen"] is True
    assert tags("We value citizenship in our community.")[0]["citizen"] is None


def test_non_cs_engineering_dropped():
    for t in ["Entry-Level Civil Engineer", "Intern/Co-op - Geotechnical Engineering (Summer 2027)", "2027 Mechanical Engineer Intern",
              "2027 Early Career Warhead Engineer", "Game Presentation Intern - Frederick Keys", "Intern - EHS Engineer",
              "Activision 2027 Summer Internships - Game Design", "Fuel Supply Analyst Intern", "Trim Engineering Intern"]:
        assert not keep_title(t), t
    assert not keep_title("Electrical Engineering Internship - Data Center Facilities")


def test_early_needs_title_or_explicit_statement():
    assert section("Data Engineering Intern", "In your first year on the team you will learn a lot.") == "internship"
    assert section("Software Intern", "This program is open to sophomores and juniors.") == "early"


def test_export_license_is_not_visa_sponsorship():
    assert tags("must comply with U.S. export control laws without sponsorship for an export license.")[0]["sponsor"] is None


def test_us_only():
    from classify import us_job
    assert not us_job("London, United Kingdom")
    assert not us_job("Amsterdam")
    assert us_job("Houston, TX") and us_job("Remote - US") and us_job("")


def test_school_specific_reqs_dropped():
    assert not keep_title("I-26002 - HEC Engineer Intern - LSU")
    assert not keep_title("I - 27002 - AK Field Engineer Intern - Colorado School of Mines")
    assert keep_title("Software Engineering Co-op (Jun-Dec 2027)")
    assert keep_title("Software Engineering Intern - McNeese State University")


def test_allow_list_needs_cs_work_in_title():
    for t in ["Roadway Engineering Intern - Spring/Summer 2027", "Electrical Engineering (Substation) Intern - Summer 2027",
              "Packaging Engineering Co-op", "Business Analyst Intern", "Risk Control Intern", "Quality Engineering Intern",
              "Component Engineering Intern", "Undergraduate Investment Analyst Intern (Summer 2027) - Investment Office",
              "New Grad GIS Analyst I (For Current/Previous HNTB Interns ONLY)"]:
        assert not keep_title(t), t
    for t in ["CSG Hardware Engineering Intern", "Firmware Engineering Intern", "Data Engineer Intern", "IT Intern",
              "Summer 2027 - Technology Intern", "Cybersecurity Analyst Intern", "FPGA Design Intern", "Software Engineering Co-op (Jun-Dec 2027)"]:
        assert keep_title(t), t


def test_sponsor_regressions_from_audit():
    for s in ["No relocation assistance or visa sponsorship is available for this position.",
              "No H-1B sponsorship is provided.",
              "Sponsorship is not available for this position.",
              "Candidates who require sponsorship now or in the future will not be considered.",
              "Visa sponsorship: we do not offer it."]:
        assert tags(s)[0]["sponsor"] is False, s


def test_export_control_alone_is_not_citizenship():
    assert tags("You must comply with U.S. Export Control Laws.")[0]["citizen"] is None
    # a bare ITAR mention gets its own "mentions ITAR" tag, not "citizens only"
    t, ev = tags("This position is subject to ITAR.")
    assert t["citizen"] is None and t["itar"] is True and ev["itar"] == "This position is subject to ITAR."
    assert tags("Applicants must be U.S. persons under ITAR.")[0]["citizen"] is True


def test_evidence_not_cut_at_abbreviation():
    _, ev = tags("Must be a U.S. citizen to apply. Great team.")
    assert ev["citizen"] == "Must be a U.S. citizen to apply."


def test_heading_is_read_with_the_line_after_it():
    # "ITAR Requirement:" alone says nothing; the next line decides the tag and is shown as evidence
    t, ev = tags("ITAR Requirement:\nApplicants must be U.S. persons.")
    assert t["citizen"] is True and ev["citizen"] == "ITAR Requirement: Applicants must be U.S. persons."
    t, ev = tags("ITAR Requirement:\nThis role works with export-controlled data.")
    assert t["citizen"] is None and t["itar"] is True and ev["itar"].startswith("ITAR Requirement: This role")


def test_clearance_none_is_not_a_clearance():
    assert tags("Minimum Clearance Required to Start: None")[0]["clearance"] is None
    assert tags("Security Clearance:\nNone required.")[0]["clearance"] is None
    assert tags("Minimum Clearance Required to Start: TS/SCI")[0]["clearance"] is True
    assert tags("Security Clearance:\nActive Secret clearance required.")[0]["clearance"] is True


def test_quote_not_cut_at_e_g_across_a_line_break():
    _, ev = tags("We do not provide sponsorship for employment visa status (e.\ng., H-1B). Thanks.")
    assert ev["sponsor"] == "We do not provide sponsorship for employment visa status (e. g., H-1B)."


# ---- tracks and terms (from the title, applied at build time) ----

def test_track_from_title():
    from classify import track
    cases = {
        "Software Engineering Intern - Summer 2027": "software",
        "Backend Developer Intern": "software",
        "2027 Intern - Software Engineer": "software",
        "Summer 2027 - Technology Intern": "software",  # CS-generic defaults to software
        "Embedded Software Intern": "embedded",
        "Firmware Engineering Intern": "embedded",
        "RTOS Development Co-op": "embedded",
        "Microcontroller Applications Intern": "embedded",
        "FPGA Design Intern": "hardware",
        "ASIC Engineer Intern, Annapurna Labs - 2027": "hardware",
        "RTL Design Intern": "hardware",
        "Design Verification Intern": "hardware",
        "Silicon Validation Intern": "hardware",
        "VLSI Physical Design Intern": "hardware",
        "CSG Hardware Engineering Intern": "hardware",
        "Cybersecurity Analyst Intern": "security",
        "Intern/Co-op - Cyber Security (Spring & Summer 2027)": "security",
        "Penetration Testing Intern": "security",
        "SOC Analyst Intern": "security",
        "Software Engineer Intern - Product Security": "security",
        "Intern, Information Technology": "it",
        "IT Help Desk Intern": "it",
        "Network Engineer Intern": "it",
        "Systems Administrator Intern": "it",
        "Co-op, IT Analyst: Spring": "it",
        "2027 Business Technology Solutions Intern - Cloud Engineering (Undergraduate)": "it",
        "Data Center Operations Intern": "it",
        "Data Engineer Intern": "data",
        "Financial Data Analyst Intern": "data",
        "Advertising & Partnerships: Data Science Internship – Summer 2027": "data",
        "Machine Learning Engineer, Applied AI Co-Op Intern, Winter 2027": "data",
        "Summer 2027: Data Analytics Intern": "data",
        "Agentic AI Engineer Co-Op": "data",
        "Software Engineer Internship – AI Platform Team": "software",  # a software role on an AI team
        "Summer Intern - Software Engineering - Quality Assurance": "software",
    }
    for title, want in cases.items():
        assert track(title) == want, (title, track(title))


def test_soc_chip_is_not_a_security_operations_center():
    from classify import track
    assert track("SoC Design Verification Intern") == "hardware"


def test_gov_flag_from_title_or_tags():
    from classify import is_gov
    assert is_gov({"title": "Software Intern - Department of Energy National Laboratory", "tags": {}})
    assert is_gov({"title": "Software Engineering Intern", "tags": {"clearance": True}})
    assert is_gov({"title": "Software Engineering Intern", "tags": {"citizen": True}})
    assert not is_gov({"title": "Software Engineering Intern", "tags": {"itar": True}})  # a bare ITAR mention isn't enough
    assert not is_gov({"title": "Software Engineering Intern", "tags": {}})


def test_terms_from_title():
    from classify import terms
    assert terms("Software Engineering Intern - Summer 2027") == []  # summer is the default, not tagged
    assert terms("Wabtec Spring 2027 Software Engineering Co-Op (10-Week)") == ["co_op", "spring"]
    assert terms("Intern/Co-op - Cyber Security (Spring & Summer 2027)") == ["co_op", "spring"]
    assert terms("Software Engineering Intern - Fall 2027") == ["fall"]
    assert terms("Autumn 2027 Data Intern") == ["fall"]
    assert terms("Part-Time IT Intern") == ["part_time"]
    assert terms("Part Time Software Developer Intern (Spring)") == ["spring", "part_time"]
    assert terms("Cooperative Education Student - Software") == ["co_op"]


# ---- text tags (set at fetch time from the posting description) ----

def test_oa_platforms():
    t, ev = tags("Candidates will complete a HackerRank challenge. Great team.")
    assert t["oa"] is True and "HackerRank" in ev["oa"]
    assert tags("Next step is a CodeSignal General Coding Assessment.")[0]["oa"] is True
    assert tags("You will receive a Codility test.")[0]["oa"] is True
    assert tags("Selected applicants complete an online assessment.")[0]["oa"] is True
    assert tags("Interviews are held on campus.")[0]["oa"] is None


def test_min_gpa():
    cases = {
        "Minimum 3.0 GPA.": 3.0,
        "Must have a GPA of 3.5 or higher.": 3.5,
        "Cumulative GPA of 3.2 or above required.": 3.2,
        "Minimum cumulative GPA of 2.75 on a 4.0 scale.": 2.75,
        "3.0/4.0 GPA or better.": 3.0,
        "GPA: 3.0+": 3.0,
        "Requires at least a 2.8 GPA.": 2.8,
        "Minimum GPA of 3.0 required; 3.5 preferred.": 3.0,
    }
    for s, want in cases.items():
        t, ev = tags(s)
        assert t["min_gpa"] == want, (s, t["min_gpa"])
        assert ev["min_gpa"] == s
    for s in ["A 3.5 GPA is preferred.", "Strong academic record.", "Please include your GPA on your resume.",
              "Version 3.0 of our GPA calculator.", "We have 4.0 stars on Glassdoor."]:
        assert tags(s)[0]["min_gpa"] is None, s


def test_clearance_level():
    def lvl(s):
        t, _ = tags(s)
        return t["clearance_level"]
    assert lvl("Must be able to obtain a Secret clearance.") == "secret"
    assert lvl("Active Top Secret clearance required.") == "top secret"
    assert lvl("Minimum Clearance Required to Start: TS/SCI") == "ts/sci"
    assert lvl("Must hold an active TS/SCI clearance with polygraph.") == "ts/sci + poly"
    assert lvl("Requires an active security clearance. Secret level.") == "secret"
    assert lvl("Must be able to obtain a Public Trust clearance.") == "public trust"
    assert lvl("Ability to obtain a security clearance.") is None  # clearance, level not stated
    assert lvl("Secret clearance required; Top Secret preferred.") == "secret"  # the required level, not the preferred one
    assert lvl("We keep trade secrets safe. Great team.") is None  # no clearance tag, no level
    from classify import clearance_level
    assert clearance_level("This role requires an active Top Secret/SCI clearance.") == "ts/sci"  # build time, from stored evidence


def test_public_trust_counts_as_clearance():
    assert tags("Must be able to obtain a Public Trust clearance.")[0]["clearance"] is True
    assert tags("This is a public trust position requiring a background investigation.")[0]["clearance"] is True
    assert tags("We value public trust in our products.")[0]["clearance"] is None
