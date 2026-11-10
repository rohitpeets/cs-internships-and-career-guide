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
