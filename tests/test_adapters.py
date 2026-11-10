import json
from pathlib import Path

import pytest

import adapters

FIX = Path(__file__).parent / "fixtures"


class FakeResp:
    def __init__(self, data, status=200):
        self._d, self.status_code, self.ok = data, status, status < 400

    def json(self):
        return self._d

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


class FakeHttp:
    def __init__(self, data, status=200):
        self.r = FakeResp(data, status)

    def get(self, *a, **k):
        return self.r


@pytest.mark.parametrize("name", ["greenhouse", "lever", "ashby"])
def test_fixture_parses(name):
    data = json.loads((FIX / f"{name}.json").read_text(encoding="utf-8"))
    jobs = adapters.CLOUD[name]("demo", FakeHttp(data))
    assert jobs and all(j["title"] and j["url"].startswith("http") for j in jobs)


@pytest.mark.parametrize("name,bad", [("greenhouse", {"oops": 1}), ("lever", {"jobs": []}), ("ashby", [])])
def test_unexpected_shape_fails_loudly(name, bad):
    with pytest.raises(adapters.ShapeError):
        adapters.CLOUD[name]("demo", FakeHttp(bad))


def test_smartrecruiters_parses():
    class H:
        def get(self, url, params=None, **k):
            if params:  # list call
                data = {"content": [{"id": "1", "name": "Software Engineer Intern", "location": {"city": "Austin", "region": "TX", "country": "us"}}],
                        "totalFound": 1} if params["q"] == "intern" else {"content": [], "totalFound": 0}
            else:  # detail call
                data = {"postingUrl": "https://jobs.smartrecruiters.com/acme/1",
                        "jobAd": {"sections": {"qualifications": {"text": "<p>We are unable to sponsor visas.</p>"}}}}
            return FakeResp(data)
    jobs = adapters.CLOUD["smartrecruiters"]("acme", H())
    assert [j["location"] for j in jobs] == ["Austin, TX, US"] and "unable to sponsor" in jobs[0]["text"]


def test_amazon_parses():
    data = {"hits": 1, "jobs": [{"id": "1", "title": "2027 Software Dev Engineer Intern", "job_path": "/en/jobs/1/sde-intern",
                                 "normalized_location": "Seattle, Washington, USA", "description": "Build things.",
                                 "basic_qualifications": "Enrolled in a CS degree.", "preferred_qualifications": ""}]}
    jobs = adapters.CLOUD["amazon"]("amazon", FakeHttp(data))
    assert jobs[0]["url"] == "https://www.amazon.jobs/en/jobs/1/sde-intern" and "CS degree" in jobs[0]["text"]
