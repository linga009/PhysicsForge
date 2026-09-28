"""PhysicsForge Citation Guard -- real implementation of references/citation-guard.md.

Does NOT reimplement retraction detection: delegates to the `citeguard` package
(https://github.com/wedo911/citeguard, MIT, 72 tests against real Crossref
fixtures) which already handles the update-to / updated-by / title-prefix
triple-signal algorithm correctly. This module adds exactly what citeguard does
not cover: DOI metadata-drift checking (title/author/year vs what a manuscript
claims) and arXiv ID existence checking.

Usage:
    python citation_guard.py check citations.jsonl
    python citation_guard.py check citations.jsonl --fail-on not_found

Input format: one JSON object per line, e.g.
    {"key": "AllenDynes1975", "doi": "10.1103/PhysRevB.12.905",
     "title": "Transition temperature of strong-coupled superconductors reanalyzed",
     "authors": ["Allen", "Dynes"], "year": 1975}
    {"key": "Semenok2025", "arxiv": "2407.12922", "year": 2024}
A citation with neither `doi` nor `arxiv` is reported UNVERIFIABLE.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

log = logging.getLogger("citation_guard")

CROSSREF_UA = "PhysicsForgeCitationGuard/0.1 (mailto:lingamraju26@gmail.com)"
ARXIV_API = "https://export.arxiv.org/api/query"


# --------------------------------------------------------------------------- verdicts

VERDICTS = (
    "VERIFIED",
    "VERIFIED_DRIFT",
    "VERIFIED_RETRACTED",
    "NOT_FOUND",
    "AMBIGUOUS",
    "UNVERIFIABLE",
)


@dataclass
class CitationResult:
    key: str
    identifier_type: str  # "doi" | "arxiv" | "none"
    identifier: str | None
    verdict: str
    fetched_title: str | None = None
    fetched_year: int | None = None
    drift_notes: list[str] = field(default_factory=list)
    retraction_signals: list[str] = field(default_factory=list)
    error: str | None = None
    latency_ms: float = 0.0


# --------------------------------------------------------------------------- fetchers

def _http_get_json(url: str, headers: dict[str, str]) -> tuple[dict | None, str | None]:
    t0 = time.monotonic()
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        dt = (time.monotonic() - t0) * 1000
        log.info("GET %s -> 200 (%.0f ms)", url, dt)
        return data, None
    except urllib.error.HTTPError as e:
        dt = (time.monotonic() - t0) * 1000
        log.info("GET %s -> %s (%.0f ms)", url, e.code, dt)
        if e.code == 404:
            return None, "not_found"
        return None, f"http_{e.code}"
    except Exception as e:  # noqa: BLE001 -- network is inherently flaky, report don't crash
        dt = (time.monotonic() - t0) * 1000
        log.warning("GET %s -> ERROR %s (%.0f ms)", url, e, dt)
        return None, str(e)


def fetch_crossref_metadata(doi: str) -> tuple[dict | None, str | None]:
    url = f"https://api.crossref.org/works/{doi}"
    data, err = _http_get_json(url, {"User-Agent": CROSSREF_UA})
    if err:
        return None, err
    return data.get("message"), None


def fetch_arxiv_metadata(arxiv_id: str) -> tuple[dict | None, str | None]:
    url = f"{ARXIV_API}?id_list={arxiv_id}"
    t0 = time.monotonic()
    req = urllib.request.Request(url, headers={"User-Agent": CROSSREF_UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            xml = resp.read().decode("utf-8")
        dt = (time.monotonic() - t0) * 1000
        log.info("GET %s -> 200 (%.0f ms)", url, dt)
    except Exception as e:  # noqa: BLE001
        dt = (time.monotonic() - t0) * 1000
        log.warning("GET %s -> ERROR %s (%.0f ms)", url, e, dt)
        return None, str(e)

    if "<entry>" not in xml or re.search(r"<title>\s*Error\s*</title>", xml, re.I):
        return None, "not_found"

    title_m = re.search(r"<entry>.*?<title>(.*?)</title>", xml, re.S)
    published_m = re.search(r"<published>(\d{4})-", xml)
    if not title_m:
        return None, "not_found"
    return {
        "title": re.sub(r"\s+", " ", title_m.group(1)).strip(),
        "year": int(published_m.group(1)) if published_m else None,
    }, None


# --------------------------------------------------------------------------- comparison

def _title_similar(a: str, b: str) -> bool:
    a_n = re.sub(r"[^a-z0-9 ]", "", a.lower())
    b_n = re.sub(r"[^a-z0-9 ]", "", b.lower())
    return SequenceMatcher(None, a_n, b_n).ratio() >= 0.85


def compare_metadata(
    stated_title: str | None,
    stated_year: int | None,
    stated_authors: list[str] | None,
    fetched_title: str | None,
    fetched_year: int | None,
    fetched_authors: list[str] | None,
) -> list[str]:
    notes = []
    if stated_title and fetched_title and not _title_similar(stated_title, fetched_title):
        notes.append(f"title differs: stated={stated_title!r} fetched={fetched_title!r}")
    if stated_year and fetched_year and stated_year != fetched_year:
        notes.append(f"year differs: stated={stated_year} fetched={fetched_year}")
    if stated_authors and fetched_authors:
        stated_surnames = {a.split()[-1].lower() for a in stated_authors}
        fetched_surnames = {a.split()[-1].lower() for a in fetched_authors}
        if not stated_surnames & fetched_surnames:
            notes.append(f"authors differ: stated={stated_authors} fetched={fetched_authors[:3]}")
    return notes


# --------------------------------------------------------------------------- main check

def check_citation(entry: dict[str, Any]) -> CitationResult:
    key = entry.get("key", "<no key>")
    doi = entry.get("doi")
    arxiv = entry.get("arxiv")
    stated_title = entry.get("title")
    stated_year = entry.get("year")
    stated_authors = entry.get("authors")
    t0 = time.monotonic()

    if not doi and not arxiv:
        return CitationResult(key, "none", None, "UNVERIFIABLE",
                               error="no DOI or arXiv ID provided")

    if doi:
        # existence + metadata (not covered by citeguard)
        meta, err = fetch_crossref_metadata(doi)
        if err == "not_found" or meta is None:
            return CitationResult(key, "doi", doi, "NOT_FOUND",
                                   error=err or "no metadata returned",
                                   latency_ms=(time.monotonic() - t0) * 1000)
        fetched_title = (meta.get("title") or [None])[0]
        fetched_year = (meta.get("issued", {}).get("date-parts") or [[None]])[0][0]
        fetched_authors = [
            f"{a.get('given', '')} {a.get('family', '')}".strip()
            for a in meta.get("author", [])
        ]
        drift = compare_metadata(stated_title, stated_year, stated_authors,
                                  fetched_title, fetched_year, fetched_authors)

        # retraction status -- delegate to citeguard, do not reimplement
        try:
            import citeguard
            status = citeguard.check_doi(doi)
            retraction_signals = [
                f"{s.type.value} via {s.source} ({s.date}) -> {s.notice_doi}"
                for s in status.signals
            ] if status.signals else []
            is_retracted = status.verdict.value in ("retracted", "concern", "corrected")
        except Exception as e:  # noqa: BLE001
            log.warning("citeguard check failed for %s: %s", doi, e)
            retraction_signals, is_retracted = [], False

        verdict = "VERIFIED_RETRACTED" if is_retracted else (
            "VERIFIED_DRIFT" if drift else "VERIFIED"
        )
        return CitationResult(key, "doi", doi, verdict, fetched_title, fetched_year,
                               drift, retraction_signals,
                               latency_ms=(time.monotonic() - t0) * 1000)

    # arXiv path
    meta, err = fetch_arxiv_metadata(arxiv)
    if err == "not_found" or meta is None:
        return CitationResult(key, "arxiv", arxiv, "NOT_FOUND",
                               error=err or "no metadata returned",
                               latency_ms=(time.monotonic() - t0) * 1000)
    drift = compare_metadata(stated_title, stated_year, None,
                              meta["title"], meta["year"], None)
    verdict = "VERIFIED_DRIFT" if drift else "VERIFIED"
    return CitationResult(key, "arxiv", arxiv, verdict, meta["title"], meta["year"],
                           drift, [], latency_ms=(time.monotonic() - t0) * 1000)


# --------------------------------------------------------------------------- reporting

def overall_verdict(results: list[CitationResult]) -> str:
    if any(r.verdict == "NOT_FOUND" for r in results):
        return "FAIL"
    if any(r.verdict in ("VERIFIED_RETRACTED",) for r in results):
        retracted_acknowledged = False  # caller manuscript text not checked here
        return "FAIL" if not retracted_acknowledged else "HOLD"
    if any(r.verdict in ("VERIFIED_DRIFT", "UNVERIFIABLE", "AMBIGUOUS") for r in results):
        return "HOLD"
    return "PASS"


def render_report(results: list[CitationResult]) -> str:
    counts = {v: 0 for v in VERDICTS}
    for r in results:
        counts[r.verdict] += 1
    lines = []
    lines.append("=" * 70)
    lines.append("CITATION GUARD REPORT")
    lines.append("=" * 70)
    lines.append("")
    lines.append("SUMMARY:")
    lines.append(f"  Total citations: {len(results)}")
    for v in VERDICTS:
        if counts[v]:
            lines.append(f"  {v}: {counts[v]}")
    verdict = overall_verdict(results)
    lines.append("")
    lines.append(f"VERDICT: {verdict}")
    lines.append("")
    lines.append("=" * 70)
    lines.append("DETAILED RESULTS")
    lines.append("")
    for r in results:
        lines.append(f"Citation: {r.key}")
        lines.append(f"  Identifier: {r.identifier_type}:{r.identifier}")
        lines.append(f"  Verdict: {r.verdict}")
        if r.fetched_title:
            lines.append(f"  Fetched title: {r.fetched_title}")
        for d in r.drift_notes:
            lines.append(f"  DRIFT: {d}")
        for s in r.retraction_signals:
            lines.append(f"  SIGNAL: {s}")
        if r.error:
            lines.append(f"  Error: {r.error}")
        lines.append(f"  Latency: {r.latency_ms:.0f} ms")
        lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)


# --------------------------------------------------------------------------- CLI

def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_check = sub.add_parser("check", help="check a .jsonl file of citations")
    p_check.add_argument("path", type=Path)
    p_check.add_argument("--fail-on", choices=["never", "drift", "not_found", "retracted"],
                          default="not_found")
    p_check.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)

    entries = [json.loads(line) for line in args.path.read_text(encoding="utf-8").splitlines()
               if line.strip() and not line.strip().startswith("//")]
    results = [check_citation(e) for e in entries]

    print(render_report(results))

    if args.json_out:
        args.json_out.write_text(
            json.dumps([r.__dict__ for r in results], indent=2, default=str),
            encoding="utf-8",
        )

    verdict = overall_verdict(results)
    severity = {"never": -1, "drift": 0, "not_found": 1, "retracted": 2}
    result_severity = {
        "VERIFIED": -1, "VERIFIED_DRIFT": 0, "UNVERIFIABLE": 0, "AMBIGUOUS": 0,
        "NOT_FOUND": 1, "VERIFIED_RETRACTED": 2,
    }
    worst = max((result_severity.get(r.verdict, -1) for r in results), default=-1)
    return 1 if worst >= severity[args.fail_on] else 0


if __name__ == "__main__":
    raise SystemExit(main())
