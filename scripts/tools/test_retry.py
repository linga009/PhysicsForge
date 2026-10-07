"""Deterministic tests for citation_guard.py's retry/cache logic.

Per idea-to-production-tool's "determinism before deltas": retry behavior is
tested by injecting a fake fetch function and a fake sleep, not by hoping the
real network happens to be flaky during the test run (or waiting through real
backoff delays). This is a real regression test, run with plain `python`
(no pytest dependency needed -- kept zero-dependency like prereg.sh).
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
import citation_guard as cg  # noqa: E402

FAILURES = []


def check(name: str, cond: bool, detail: str = ""):
    mark = "PASS" if cond else "FAIL"
    print(f"[{mark}] {name}" + (f" -- {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


def reset_cache():
    if cg.CACHE_DIR.exists():
        shutil.rmtree(cg.CACHE_DIR)


def test_retries_transient_then_succeeds():
    """A URLError on the first two attempts, success on the third, must
    succeed overall and call sleep exactly twice (once per failed attempt)."""
    reset_cache()
    calls = {"n": 0}
    sleeps = []

    def fake_once(url, headers):
        calls["n"] += 1
        if calls["n"] < 3:
            return None, "retry:simulated transient failure"
        return '{"ok": true}', None

    with patch.object(cg, "_http_get_once", side_effect=fake_once):
        text, err = cg._http_get("http://example.test/x", {}, sleep=sleeps.append,
                                  use_cache=False)

    check("succeeds after 2 transient failures", text == '{"ok": true}' and err is None,
          f"got text={text!r} err={err!r}")
    check("called the fetcher exactly 3 times", calls["n"] == 3, f"got {calls['n']}")
    check("slept exactly twice (once per retry)", len(sleeps) == 2, f"got {len(sleeps)}")
    check("backoff increases (2nd sleep >= 1st)", sleeps[1] >= sleeps[0] if len(sleeps) == 2 else False)


def test_404_is_not_retried():
    """A 404 must return immediately, with zero sleeps -- retrying a real
    not-found answer would be pointless and would hammer the API."""
    reset_cache()
    calls = {"n": 0}
    sleeps = []

    def fake_once(url, headers):
        calls["n"] += 1
        return None, "not_found"

    with patch.object(cg, "_http_get_once", side_effect=fake_once):
        text, err = cg._http_get("http://example.test/missing", {}, sleep=sleeps.append,
                                  use_cache=False)

    check("returns not_found", err == "not_found", f"got err={err!r}")
    check("called the fetcher exactly once (no retry)", calls["n"] == 1, f"got {calls['n']}")
    check("never slept", len(sleeps) == 0, f"got {len(sleeps)}")


def test_exhausts_retries_and_reports_last_error():
    """A URL that always fails transiently must give up after max_retries
    and report a failure, not hang or silently succeed."""
    reset_cache()
    calls = {"n": 0}

    def fake_once(url, headers):
        calls["n"] += 1
        return None, "retry:always fails"

    with patch.object(cg, "_http_get_once", side_effect=fake_once):
        text, err = cg._http_get("http://example.test/always-down", {},
                                  max_retries=2, sleep=lambda s: None, use_cache=False)

    check("gives up and returns an error", text is None and err == "always fails",
          f"got text={text!r} err={err!r}")
    check("attempted exactly max_retries+1 times", calls["n"] == 3, f"got {calls['n']}")


def test_retry_after_header_is_honored():
    """A 429 with Retry-After: 7 must sleep ~7s, not the default backoff."""
    reset_cache()
    calls = {"n": 0}
    sleeps = []

    def fake_once(url, headers):
        calls["n"] += 1
        if calls["n"] == 1:
            return None, "retry:http_429:7"
        return "ok", None

    with patch.object(cg, "_http_get_once", side_effect=fake_once):
        cg._http_get("http://example.test/ratelimited", {}, sleep=sleeps.append,
                      use_cache=False)

    check("honored Retry-After value (7s) rather than default backoff",
          len(sleeps) == 1 and sleeps[0] == 7.0, f"got sleeps={sleeps}")


def test_cache_avoids_second_fetch():
    """Two calls to the same URL with caching on must only hit the network once."""
    reset_cache()
    calls = {"n": 0}

    def fake_once(url, headers):
        calls["n"] += 1
        return '{"cached": true}', None

    with patch.object(cg, "_http_get_once", side_effect=fake_once):
        cg._http_get("http://example.test/cacheme", {}, sleep=lambda s: None, use_cache=True)
        cg._http_get("http://example.test/cacheme", {}, sleep=lambda s: None, use_cache=True)

    check("second call served from cache (fetcher called once, not twice)",
          calls["n"] == 1, f"got {calls['n']}")
    reset_cache()


def test_no_cache_flag_bypasses_cache():
    reset_cache()
    calls = {"n": 0}

    def fake_once(url, headers):
        calls["n"] += 1
        return '{"x": 1}', None

    with patch.object(cg, "_http_get_once", side_effect=fake_once):
        cg._http_get("http://example.test/nocache", {}, sleep=lambda s: None, use_cache=False)
        cg._http_get("http://example.test/nocache", {}, sleep=lambda s: None, use_cache=False)

    check("--no-cache equivalent (use_cache=False) hits the network every time",
          calls["n"] == 2, f"got {calls['n']}")
    reset_cache()


if __name__ == "__main__":
    test_retries_transient_then_succeeds()
    test_404_is_not_retried()
    test_exhausts_retries_and_reports_last_error()
    test_retry_after_header_is_honored()
    test_cache_avoids_second_fetch()
    test_no_cache_flag_bypasses_cache()

    print()
    if FAILURES:
        print(f"RESULT: FAIL ({len(FAILURES)} failed: {', '.join(FAILURES)})")
        raise SystemExit(1)
    print("RESULT: PASS (all retry/cache tests passed)")
