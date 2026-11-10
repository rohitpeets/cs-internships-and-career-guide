"""Shared helpers: paths, JSON/YAML I/O, URL keys, polite HTTP."""
import json
import threading
import time
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
POSTINGS = DATA / "postings.json"
REMOVED = DATA / "removed.json"
COMPANIES = DATA / "companies.yaml"
MANUAL = DATA / "manual.yaml"
LOCAL = DATA / "local.json"  # written only by the laptop job (Workday, Oracle)

USER_AGENT = "mcneese-jobs/1.0 (student job board; github.com/rohitpeets/mcneese-jobs)"
TRACKING = ("utm_", "source", "ref", "gh_src", "lever-source")


def today() -> str:
    return date.today().isoformat()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def load_yaml(path: Path, default):
    if not path.exists():
        return default
    return yaml.safe_load(path.read_text(encoding="utf-8")) or default


def url_key(url: str) -> str:
    """Apply URL without tracking parameters or a trailing slash; job-id parameters are kept."""
    s = urlsplit(url.strip())
    q = [(k, v) for k, v in parse_qsl(s.query) if not k.lower().startswith(TRACKING)]
    return urlunsplit((s.scheme.lower(), s.netloc.lower(), s.path.rstrip("/"), urlencode(q), "")).lower()


_HOST_LAST: dict = {}
_HOST_LOCKS: dict = {}
_LOCKS_LOCK = threading.Lock()


class Http:
    """requests session; every Http object shares one pacing clock per host, so boards on the
    same host (boards-api.greenhouse.io) never go back-to-back. 429/503 are retried with backoff."""

    def __init__(self, gap: float = 1.0, timeout: float = 20.0, retries: int = 3):
        self.s = requests.Session()
        self.s.headers["User-Agent"] = USER_AGENT
        self.gap, self.timeout, self.retries = gap, timeout, retries

    def _wait_turn(self, host: str) -> None:
        with _LOCKS_LOCK:
            lock = _HOST_LOCKS.setdefault(host, threading.Lock())
        with lock:
            wait = self.gap - (time.monotonic() - _HOST_LAST.get(host, 0))
            if wait > 0:
                time.sleep(wait)
            _HOST_LAST[host] = time.monotonic()

    def _call(self, method: str, url: str, **kw) -> requests.Response:
        host = urlsplit(url).netloc
        for attempt in range(self.retries + 1):
            self._wait_turn(host)
            r = self.s.request(method, url, timeout=self.timeout, **kw)
            if r.status_code not in (429, 503) or attempt == self.retries:
                return r
            try:
                delay = min(float(r.headers.get("Retry-After", "")), 60)
            except ValueError:
                delay = 5 * (attempt + 1)
            time.sleep(delay)
        return r

    def get(self, url: str, **kw) -> requests.Response:
        return self._call("GET", url, **kw)

    def post(self, url: str, **kw) -> requests.Response:
        return self._call("POST", url, **kw)
