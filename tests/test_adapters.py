import json
from pathlib import Path

import pytest

import adapters

FIX = Path(__file__).parent / "fixtures"


class FakeResp:
    def __init__(self, data, status=200):
        self._d, self.status_code = data, status

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


def test_missing_board_is_empty():
    assert adapters.CLOUD["greenhouse"]("gone", FakeHttp({}, 404)) == []
