# PhysicsForge — Citation Guard Protocol

A protocol to verify every citation in a manuscript before delivery. Prevents the
single most common form of AI-generated physics fraud: fabricated references.

This is a **delivery gate**. Manuscripts that fail Citation Guard must not be
delivered to clients or users.

---

## WHY THIS MATTERS

LLMs produce convincing-looking citations that don't exist. A citation like

> "Smith, J. (2018). Renormalization group flow in non-Abelian gauge theories.
> Physical Review D, 97, 094023."

may have correct format, plausible authors, plausible journal, plausible volume — and
not exist. The paper was not written, the journal article was not published, the
authors may not even be real.

This kind of fabrication is:
- Trivial for the model to produce
- Difficult for a casual reader to detect
- Catastrophic for the manuscript when discovered
- Damaging to the reputation of any researcher who delivers it

Citation Guard prevents this.

---

## WHEN TO TRIGGER

Run Citation Guard:
- Before delivering any manuscript
- Before delivering any literature review
- Before delivering any audit report that contains citations
- When the user says "verify these citations"
- When asked to "check the bibliography"
- After any literature search that produced a list of papers

This is mandatory before delivery. Skipping is a violation of the protocol.

---

## VERIFICATION SOURCES

Each citation must be verified against at least one authoritative database:

### For DOI-bearing citations
**Primary**: Crossref API (`https://api.crossref.org/works/{DOI}`)
- Verifies the DOI exists
- Returns title, authors, year, journal
- Authoritative for published papers

### For arXiv preprints  
**Primary**: arXiv API or direct URL (`https://arxiv.org/abs/{arXiv_ID}`)
- Verifies the preprint exists
- Returns title, authors, abstract, version history
- Authoritative for preprints

### For papers with both DOI and arXiv ID
Verify both. Confirm they refer to the same work.

### For book references
Use OpenLibrary or Google Books to confirm the book exists with stated title and
authors.

### For older papers without DOI
Use NASA ADS or INSPIRE-HEP for physics literature.
Use MathSciNet or zbMATH for mathematics literature.

---

## VERIFICATION VERDICT TYPES

For each citation, assign one of:

| Verdict | Meaning |
|---|---|
| `VERIFIED` | Citation exists and metadata matches what's stated in the manuscript |
| `VERIFIED_DRIFT` | Citation exists but metadata differs (year off, authors off, etc.) |
| `VERIFIED_RETRACTED` | Citation exists but paper has been retracted |
| `NOT_FOUND` | Cannot find the citation in any authoritative database |
| `AMBIGUOUS` | Multiple papers match; cannot determine which is intended |
| `UNVERIFIABLE` | No DOI, arXiv, or other lookup key provided |

---

## VERIFICATION PROCEDURE

For each citation in the manuscript:

### Step 1 — Extract identifiers
Identify the DOI, arXiv ID, ISBN, or other unique identifier in the citation.

If none is present, the citation is `UNVERIFIABLE` until an identifier is added.

### Step 2 — Query authoritative database
Use the appropriate API:
- DOI → Crossref
- arXiv → arXiv API
- HEP paper → INSPIRE-HEP
- Astro paper → NASA ADS

### Step 3 — Compare metadata
Compare the returned metadata against what's stated in the manuscript:
- Title match (allow minor formatting differences)
- Author surnames match (in same order, ignoring initial styling)
- Year matches
- Journal/venue matches

### Step 4 — Assign verdict
Based on the comparison:
- All metadata matches → `VERIFIED`
- Paper exists but some metadata wrong → `VERIFIED_DRIFT` with specific noted differences
- Paper exists but retracted → `VERIFIED_RETRACTED`
- Paper does not exist → `NOT_FOUND`

### Step 5 — Document
Record the verification result in the audit log.

---

## OUTPUT FORMAT

```
═══════════════════════════════════════════════════════════════════
CITATION GUARD REPORT
Manuscript: [title or filename]
Date: [date]
═══════════════════════════════════════════════════════════════════

SUMMARY:
  Total citations: [N]
  Verified: [count] ([percentage])
  Verified with drift: [count]
  Retracted: [count]
  Not found: [count]
  Unverifiable (no identifier): [count]

VERDICT: PASS / HOLD / FAIL

═══════════════════════════════════════════════════════════════════
DETAILED RESULTS

Citation 1: [as stated in manuscript]
  Identifier used: [DOI / arXiv ID]
  Database: [Crossref / arXiv / etc.]
  Verdict: VERIFIED
  Verified metadata:
    Title: [✓ matches / ✗ differs]
    Authors: [✓ matches / ✗ differs]
    Year: [✓ matches / ✗ differs]
    Venue: [✓ matches / ✗ differs]

Citation 2: [as stated]
  Verdict: NOT_FOUND
  Database queried: [...]
  Lookup attempted: [identifier]
  Possible explanations:
    - Typo in identifier (suggest: [...])
    - Citation fabricated
    - Paper exists but unindexed
  Required action: replace or remove this citation
  
[... continue for all citations ...]

═══════════════════════════════════════════════════════════════════
ACTIONS REQUIRED:
  1. [specific action for each NOT_FOUND]
  2. [specific action for each VERIFIED_DRIFT]
  3. [specific action for each VERIFIED_RETRACTED]
  4. [specific action for each UNVERIFIABLE]

DELIVERABILITY:
  - PASS: all citations verified, no drift
  - HOLD: drift or unverifiable citations exist; needs author review
  - FAIL: NOT_FOUND citations exist; manuscript cannot be delivered
═══════════════════════════════════════════════════════════════════
```

---

## VERDICT THRESHOLDS

### PASS
- All citations VERIFIED
- 0 citations NOT_FOUND
- 0 citations VERIFIED_RETRACTED (without explicit retraction note in manuscript)
- ≤1 citation VERIFIED_DRIFT (with metadata differences noted)
- ≤2 citations UNVERIFIABLE (only if non-DOI sources like books or theses)

→ Manuscript can be delivered.

### HOLD  
- 0 citations NOT_FOUND
- Some VERIFIED_DRIFT citations needing correction
- Some UNVERIFIABLE citations needing identifiers added
- Any VERIFIED_RETRACTED needing explicit retraction acknowledgment

→ Manuscript needs revision but is not fundamentally compromised.

### FAIL
- 1+ citations NOT_FOUND (likely fabricated)
- 1+ citations VERIFIED_RETRACTED with no acknowledgment

→ Manuscript MUST NOT be delivered. The author must replace or remove problematic
   citations and re-run Citation Guard.

---

## SPECIAL CASES

### Self-citations
If the manuscript cites the author's own work, verify exists in the same way as any
other citation. Self-citations to non-existent papers are still fabrication.

### Forthcoming / submitted papers
Citations to "submitted" or "in preparation" papers cannot be verified externally.
These should be:
- Marked with `[UNVERIFIABLE — submitted]` in the verification log
- Used sparingly
- Replaced with verifiable references where possible

### Personal communications
Cannot be verified externally. Should be flagged but are acceptable in moderation if
clearly marked as personal communication in the manuscript.

### Conference proceedings
Many conferences publish proceedings indexed in Crossref. Verify those normally.
Unindexed talks should be marked `[UNVERIFIABLE — conference talk]`.

### Textbooks
Verify ISBN against OpenLibrary or Google Books. If no ISBN given, request one.

### Translated or non-English titles
Verify the original-language title; the English translation may not match the
indexed record exactly.

### Old papers (pre-1990) without arXiv or DOI
Use INSPIRE-HEP for physics or MathSciNet for math. Some legitimate older papers may
not appear in modern indices — these can be `UNVERIFIABLE` but acceptable if cited
correctly with full publication information.

---

## INTEGRATION WITH MANUSCRIPT WORKFLOW

### During literature search
Mark each result with verification status as you collect it. Don't gather a list of
"possible papers" then verify later — verify as you go.

### During manuscript writing
Maintain a verified-citations file separately. Only cite from this file. If you find
yourself wanting to cite something not yet verified, verify it first.

### Before final delivery
Run full Citation Guard on the complete manuscript. Generate the verification report.
Attach the report to the manuscript as supplementary material — clients should see
that verification was done.

### Post-delivery
Keep the verification log. If any citation is later questioned, you have evidence of
verification.

---

## COMMON FABRICATION PATTERNS TO WATCH

These are patterns the model is prone to producing. When you see them, increase
verification scrutiny:

1. **Plausible-sounding titles** that match the topic too well — too on-the-nose
2. **Round-number page ranges** — "pages 100-110" rather than "pages 103-117"  
3. **Suspiciously canonical journals** — every paper in PRD or PRL when the topic
   typically also appears in JHEP or CQG
4. **Authors with names that sound right but combine in unusual orders**
5. **Dates that just match the topic's apparent peak** — many "2021" papers in a
   discussion of work that was actually mostly done in different years
6. **Volume/issue numbers that follow patterns** — V97 N9 P094023, V98 N9 P094023, ...
7. **References to "personal communication" or "private notes"** — unverifiable

When patterns like these appear, treat the citations with extra suspicion. Verify
thoroughly.

---

## WHAT TO DO IF FABRICATION IS DETECTED

If verification reveals fabricated citations in a manuscript:

### Step 1 — Document
Record exactly which citations failed verification and why.

### Step 2 — Investigate scope
Are there other fabrications? Run the rest of the manuscript through Citation Guard.
Often fabrication is not isolated — multiple citations may be affected.

### Step 3 — Audit other claims
Citations are easy to verify; other claims may also be fabricated. Apply the
anti-fabrication protocol to the technical content as well.

### Step 4 — Report honestly
If the manuscript is from a client, report findings clearly. The client may not have
been aware of the fabrication (it may have come from a co-author, an LLM tool, etc.).
Honest reporting is more valuable than concealment.

### Step 5 — Refuse delivery
A manuscript with fabricated citations cannot be delivered as-is. Either:
- Replace the citations with verified ones
- Remove the claims that were supported by fabricated citations
- Reject the manuscript

---

## TOOLS

For automated verification, use the real backing tool, not a manual API call:

- **`scripts/citation_guard.py`** — the actual verifier behind this protocol. Takes
  a `.jsonl` file of citations (one `{"key": ..., "doi": ...}` or `{"key": ..., "arxiv": ...}` object per
  line), queries Crossref and the arXiv API with retry/backoff and on-disk caching,
  and layers the `citeguard` library's triple-signal retraction detection
  (Crossref `update-to`, Retraction-Watch-backfilled `updated-by`, title-prefix) on
  top. Run it directly:
  ```
  python scripts/citation_guard.py check citations.jsonl --fail-on retracted
  ```
  Exit code and `VERDICT` line map directly onto this file's PASS/HOLD/FAIL
  thresholds above. In a plugin install, invoke it via the `/citation-check` slash
  command instead of calling Python directly.
- The Crossref API directly (what the script itself calls): `curl https://api.crossref.org/works/{DOI}`
- The arXiv API directly: `curl "https://export.arxiv.org/api/query?id_list={arXiv_ID}"`
- INSPIRE-HEP for physics: `https://inspirehep.net/api/literature?q={query}`

Manual `curl` calls are a fallback for one-off spot checks, or for identifier types
the script doesn't yet cover (ISBN, INSPIRE). For anything resembling a full
manuscript bibliography, use the script — it is tested (`scripts/test_retry.py`)
and catches retractions the manual API calls above do not.

For manual verification, search the paper title and authors on:
- Google Scholar
- arXiv
- Crossref
- INSPIRE-HEP
- NASA ADS

If a paper cannot be found in any of these, it likely doesn't exist.

---

## CRITICAL FAILURE MODE

The most dangerous thing Citation Guard prevents is fabricated citations that the
checker might let through because they "sound right."

Defense: **always do the actual database lookup**. Do not assume a citation is real
because it looks plausible. The fabrication patterns specifically aim to look plausible.

If the database lookup returns no result, the citation is fabricated — even if the
metadata seems to fit the topic perfectly.
