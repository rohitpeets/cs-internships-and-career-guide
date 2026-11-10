"""Shared helpers: paths, JSON/YAML I/O, URL keys, polite HTTP."""
import json
import os
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

USER_AGENT = "cs-internships-and-career-guide/1.0 (student job board; github.com/rohitpeets/cs-internships-and-career-guide)"
TRACKING = ("utm_", "source", "ref", "gh_src", "lever-source")


def today() -> str:
    return date.today().isoformat()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_json(path: Path, obj) -> None:
    """Atomic write (temp file + rename), so a crash never leaves half a file. Lists are written one record per line,
    so the daily commit's diff is only the rows that changed."""
    if isinstance(obj, list):
        text = "[\n" + ",\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in obj) + "\n]\n"
    else:
        text = json.dumps(obj, indent=1, ensure_ascii=False, sort_keys=True) + "\n"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


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
            r = self.s.request(method, url, timeout=self.timeout, **kw)  # sleeping happens outside the host lock
            if r.status_code not in (429, 503) or attempt == self.retries:
                return r
            try:
                delay = max(0.0, min(float(r.headers.get("Retry-After", "")), 60))
            except ValueError:
                delay = 5 * (attempt + 1)
            time.sleep(delay)
        return r

    def get(self, url: str, **kw) -> requests.Response:
        return self._call("GET", url, **kw)

    def post(self, url: str, **kw) -> requests.Response:
        return self._call("POST", url, **kw)
