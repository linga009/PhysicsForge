---
name: citation-check
description: Verify every citation in a manuscript/bibliography against Crossref, arXiv, and retraction databases using the real citation_guard.py tool
argumentHint: [path to manuscript, bibliography, or .jsonl citation file]
---

The user wants citations verified: `$ARGUMENTS`.

Read `skills/physicsforge/references/citation-guard.md` for the full protocol,
verdict types, and PASS/HOLD/FAIL thresholds before reporting results.

1. If given a `.jsonl` file already in the tool's format, use it directly. One object per
   line, with a `doi` or an `arxiv` key (exactly these names; `arxiv_id` is ignored) and
   the metadata as the manuscript states it, so drift can be detected:
   `{"key": "AllenDynes1975", "doi": "10.1103/PhysRevB.12.905", "title": "...", "authors": ["Allen", "Dynes"], "year": 1975}`
   `{"key": "Semenok2025", "arxiv": "2407.12922", "year": 2024}`
   Otherwise, extract every DOI/arXiv ID from the given manuscript or
   bibliography and build one (ask the user for identifiers that are missing
   rather than guessing them).
2. Run the real tool — do not hand-verify via ad-hoc web search when this tool
   is available:
   ```
   python ${CLAUDE_PLUGIN_ROOT}/scripts/citation_guard.py check <file>.jsonl --fail-on retracted
   ```
   Add `--json-out <path>` if the user wants a machine-readable report, and
   `--no-cache` if they explicitly want to bypass the 24h on-disk cache (e.g.
   re-checking a citation that was recently corrected upstream).
3. The tool checks DOI/arXiv existence via Crossref and the arXiv API (with
   retry/backoff) and retraction status via the `citeguard` library's
   triple-signal detection (Crossref `update-to`, Retraction-Watch-backfilled
   `updated-by`, title-prefix matching).
4. Report results using `citation-guard.md`'s exact output format: per-citation
   verdict (VERIFIED / VERIFIED_DRIFT / VERIFIED_RETRACTED / NOT_FOUND /
   UNVERIFIABLE), then the overall PASS/HOLD/FAIL deliverability verdict.
5. If the tool reports a network error (e.g. the known Crossref `http_406`
   issue on some runner IPs), say so explicitly — do not silently fall back to
   presenting the citation as verified or unverified without noting the tool
   couldn't reach the database.

A citation with no identifier is `UNVERIFIABLE`, not fabricated — but flag it
for the user to supply one. Never assume a citation is real because it "sounds
right"; only the tool's actual database lookup counts as verification.
