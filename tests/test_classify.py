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
    assert keep_title("Electrical Engineering Intern, 2027")
    assert keep_title("Summer 2027: IT Services Intern")
    assert keep_title("Supply Chain Tooling Engineer Intern")
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
    assert tags("F-1 students on CPT are welcome to apply.")[0]["sponsor"] is True
    assert tags("Great benefits and a fun team.")[0]["sponsor"] is None


def test_citizen_and_clearance():
    t, _ = tags("Must be a U.S. citizen. This role requires an active Secret clearance.")
    assert t["citizen"] is True and t["clearance"] is True
    assert tags("Applicants must be U.S. persons under ITAR.")[0]["citizen"] is True
    assert tags("We value citizenship in our community.")[0]["citizen"] is None


def test_non_cs_engineering_dropped():
    for t in ["Entry-Level Civil Engineer", "Intern/Co-op - Geotechnical Engineering (Summer 2027)", "2027 Mechanical Engineer Intern",
              "2027 Early Career Warhead Engineer", "Game Presentation Intern - Frederick Keys", "Intern - EHS Engineer"]:
        assert not keep_title(t), t
    assert keep_title("Electrical Engineering Internship - Data Center Facilities")


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
