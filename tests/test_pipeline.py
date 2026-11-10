"""Safety rules from DESIGN.md: closing, gone boards, the failure threshold, the shrink guard, laptop staleness."""
import json
import subprocess
import sys
from datetime import date, timedelta

import pytest

import adapters
import build_readme
import check_links
import classify
import fetch_ats
import merge_local
import validate


def job(n):
    return {"title": f"Software Engineering Intern {n}", "url": f"https://x.com/jobs/{n}", "location": "Austin, TX", "text": ""}


@pytest.fixture
def board(tmp_path, monkeypatch):
    """A one-company world: companies.yaml with board 'acme', fake greenhouse adapter, temp data files."""
    comp = tmp_path / "companies.yaml"
    comp.write_text("companies:\n  - {name: Acme, ats: greenhouse, board: acme}\n")
    for name, path in (("COMPANIES", comp), ("POSTINGS", tmp_path / "postings.json"), ("REMOVED", tmp_path / "removed.json"),
                       ("BLOCKED", tmp_path / "blocked.json")):
        monkeypatch.setattr(fetch_ats, name, path)
    state = {"jobs": [job(1), job(2)], "error": None}

    def fake(b, http):
        if state["error"]:
            raise state["error"]
        return adapters.Jobs(state["jobs"])
    monkeypatch.setitem(adapters.CLOUD, "greenhouse", fake)
    monkeypatch.setattr(sys, "argv", ["fetch_ats.py", "--cloud"])

    def run(day):
        monkeypatch.setattr(fetch_ats, "today", lambda: day)
        fetch_ats.main()
        return {r["title"]: r for r in json.loads((tmp_path / "postings.json").read_text())}
    return state, run


def test_closes_after_two_days_missing_not_two_runs(board):
    state, run = board
    run("2026-11-01")
    state["jobs"] = [job(1)]
    run("2026-11-02")
    rows = run("2026-11-02")  # a second run the same day is not a second strike
    assert "Software Engineering Intern 2" in rows
    rows = run("2026-11-03")
    assert "Software Engineering Intern 2" not in rows and "Software Engineering Intern 1" in rows


def test_gone_board_flags_rows_instead_of_closing(board):
    state, run = board
    run("2026-11-01")
    state["error"] = adapters.BoardGone("acme: HTTP 404")
    run("2026-11-02")
    rows = run("2026-11-03")
    assert len(rows) == 2 and all(r["status"] == "uncertain" for r in rows.values())


def test_suddenly_empty_feed_does_not_close(board):
    state, run = board
    run("2026-11-01")
    state["jobs"] = []
    run("2026-11-02")
    rows = run("2026-11-03")
    assert len(rows) == 2


def test_failed_run_saves_nothing(board, tmp_path):
    state, run = board
    run("2026-11-01")
    before = (tmp_path / "postings.json").read_text()
    state["error"] = RuntimeError("network down")
    with pytest.raises(SystemExit):
        run("2026-11-02")
    assert (tmp_path / "postings.json").read_text() == before


def test_404_raises_board_gone():
    class R:
        status_code = 404
    class H:
        def get(self, *a, **k):
            return R()
    for name in ("greenhouse", "lever", "ashby", "smartrecruiters"):
        with pytest.raises(adapters.BoardGone):
            adapters.CLOUD[name]("old-slug", H())


def test_uncertain_rows_expire_after_a_week(tmp_path, monkeypatch):
    old = (date.today() - timedelta(days=8)).isoformat()
    rows = [{"id": "a", "url": "u", "source": "workday", "status": "uncertain", "uncertain_since": old},
            {"id": "b", "url": "u", "source": "workday", "status": "open"}]
    p, rm = tmp_path / "p.json", tmp_path / "r.json"
    p.write_text(json.dumps(rows))
    monkeypatch.setattr(check_links, "POSTINGS", p)
    monkeypatch.setattr(check_links, "REMOVED", rm)
    monkeypatch.setattr(sys, "argv", ["check_links.py", "--stale-only"])
    check_links.main()
    assert [r["id"] for r in json.loads(p.read_text())] == ["b"]


def test_stale_laptop_rows_marked_uncertain(tmp_path, monkeypatch):
    p, loc = tmp_path / "p.json", tmp_path / "l.json"
    p.write_text("[]")
    loc.write_text(json.dumps({"fetched_at": "2026-01-01T00:00:00+00:00", "rows": [{"id": "a", "company": "X", "title": "t", "source": "workday"}]}))
    monkeypatch.setattr(merge_local, "POSTINGS", p)
    monkeypatch.setattr(merge_local, "LOCAL", loc)
    merge_local.main()
    r = json.loads(p.read_text())[0]
    assert r["status"] == "uncertain" and r["uncertain_since"] == "2026-01-01"


def test_shrink_guard_uses_7_commit_high_and_reset(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    g = lambda *a: subprocess.run(["git", *a], check=True, capture_output=True)
    g("init", "-q")
    g("config", "user.email", "t@t")
    g("config", "user.name", "t")
    for n, msg in ((100, "a"), (60, "b"), (40, "c")):
        (tmp_path / "data/postings.json").write_text(json.dumps([{}] * n))
        g("add", ".")
        g("commit", "-qm", msg)
    assert validate.previous_count() == 100  # 40 now is under half of 100 even though the last step was 60 -> 40
    (tmp_path / "data/postings.json").write_text(json.dumps([{}] * 30))
    g("add", ".")
    g("commit", "-qm", "stricter filter [reset-baseline]")
    assert validate.previous_count() == 30


def test_us_job_locations():
    assert classify.us_job("Vienna, VA, United States")
    assert classify.us_job("Remote - US; London")
    assert not classify.us_job("Blumenau, SC, Brazil")
    assert not classify.us_job("Penang, Malaysia")
    assert not classify.us_job("CAD Remote – ON")


def test_board_dedupes():
    a = {"company": "T-Mobile", "title": "SWE Intern", "location": "Bellevue, WA", "first_seen": "2026-11-02"}
    b = {**a, "first_seen": "2026-11-01"}
    assert build_readme.dedupe([a, b]) == [b]


def test_untrusted_text_cannot_inject_markdown_or_html():
    evil = 'Software Intern](https://evil.example/login) [Apply <img src=x onerror=alert(1)> | x\r\r# Fake'
    out = build_readme.text(evil)
    assert "](" not in out and "<img" not in out and "|" not in out and "\n" not in out and "\r" not in out


def test_only_plain_http_links():
    assert build_readme.safe_url("javascript:alert(1)") is None
    assert build_readme.safe_url("https://x.com/a b") is None
    assert build_readme.safe_url("https://x.com/jobs/1\n## Urgent") is None
    assert build_readme.safe_url("https://x.com/j(1)|x") == "https://x.com/j%281%29%7Cx"


def test_paginate_reports_cap():
    pages = lambda off: ([1] * 100, 5000)
    items, complete = adapters.paginate(pages, 100, cap=300)
    assert len(items) == 300 and complete is False


def test_us_cities_named_like_foreign_ones():
    for loc in ("Athens, GA", "Dublin, CA", "Paris, TX", "London, KY", "Vienna, VA, United States"):
        assert classify.us_job(loc), loc


def test_no_cpt_tag():
    assert classify.tags("We do not accept CPT or OPT for this role.")[0]["no_cpt"] is True
    assert classify.tags("This role is not eligible for OPT.")[0]["no_cpt"] is True
    assert classify.tags("We will not sponsor H-1B visas.")[0]["no_cpt"] is None


def test_final_audit_rows():
    for t in ("Electronic Security Intern", "2027 Intern - QA, QMS", "Tax & Data Analytics Intern",
              "Data Center Electrical Engineering Intern", "Undergraduate Financial Analytics Intern",
              "Silicon Photonics Packaging Engineer Co-op", "Defense Science and Technology Graduate Student Internship"):
        assert not classify.keep_title(t), t
    for t in ("QA Automation Intern", "Cybersecurity Risk Analyst Intern", "Electrical and Computer Engineering Intern"):
        assert classify.keep_title(t), t
    for loc in ("Zaragoza, ESP", "BRA", "Ovar, PT", "Wuxi, Jiangsu"):
        assert not classify.us_job(loc), loc


def test_expired_terms():
    nov = date(2026, 11, 9)
    assert classify.expired_term("2026 Summer Intern", nov) and classify.expired_term("Software Intern - Fall 2026", nov)
    assert classify.expired_term("2025 Co-op", nov)
    assert not classify.expired_term("Summer 2027 Software Engineering Intern", nov)
    assert not classify.expired_term("Software Engineering Co-op (Jan-Aug 2027)", nov)


def test_clearance_wording():
    t = classify.tags
    assert t("Upon start, you will be sponsored for a TS/SCI clearance.")[0]["sponsor"] is None
    assert t("A security clearance is not required for this role.")[0]["clearance"] is None
    assert t("This position is not eligible for sponsorship, OPT, or CPT.")[0]["no_cpt"] is True


def test_city_region_country_code_locations():
    # "City, Region, CC" (SmartRecruiters style): the last code is a country, even when it looks like a state
    assert not classify.us_job("Sofia, Bosch Digital, Sofia City Province, BG")
    assert not classify.us_job("Bengaluru, KA, IN")
    assert not classify.us_job("Toronto, ON, CA")
    assert classify.us_job("Austin, TX, US")
    assert classify.us_job("Indianapolis, Marion County, IN")
    assert classify.us_job("Dublin, CA") and classify.us_job("Athens, GA")


class _Resp:
    def __init__(self, code, text=""):
        self.status_code, self.text, self.headers, self.ok = code, text, {}, code < 400


def test_http_stops_on_403_and_never_retries(monkeypatch):
    import common
    calls = []
    h = common.Http(gap=0)
    monkeypatch.setattr(h.s, "request", lambda m, u, **k: calls.append(u) or _Resp(403))
    with pytest.raises(common.Blocked):
        h.get("https://blocked.example/jobs")
    assert len(calls) == 1


def test_http_follows_robots_txt_when_asked(monkeypatch):
    import common
    h = common.Http(gap=0, check_robots=True)
    monkeypatch.setattr(h.s, "get", lambda u, **k: _Resp(200, "User-agent: *\nDisallow: /api/\n"))
    monkeypatch.setattr(h.s, "request", lambda m, u, **k: _Resp(200))
    with pytest.raises(common.Blocked):
        h.get("https://robots.example/api/jobs")
    assert h.get("https://robots.example/careers").status_code == 200
    # documented APIs (Greenhouse, Lever...) don't check robots.txt
    plain = common.Http(gap=0)
    monkeypatch.setattr(plain.s, "request", lambda m, u, **k: _Resp(200))
    assert plain.get("https://robots.example/api/jobs").status_code == 200


def test_missing_robots_txt_means_allowed(monkeypatch):
    import common
    h = common.Http(gap=0, check_robots=True)
    monkeypatch.setattr(h.s, "get", lambda u, **k: _Resp(404))
    monkeypatch.setattr(h.s, "request", lambda m, u, **k: _Resp(200))
    assert h.get("https://norobots.example/api/jobs").status_code == 200
