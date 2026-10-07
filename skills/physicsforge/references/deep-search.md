# PhysicsForge — Deep Search Protocol

A multi-database, multi-mode literature research protocol. Replaces single-query
searches with systematic 6-phase coverage and 6 specialized analysis modes.

---

## WHEN TO USE

This protocol is the foundation of any research-grade literature analysis. Use when:
- Starting work on an unfamiliar topic
- Building the literature review for a manuscript
- Identifying gaps for new research
- Auditing whether a topic has been fully addressed
- Preparing a referee response that requires comparison with prior work

---

## DATABASE COVERAGE

A high-fidelity literature search uses multiple sources in parallel because each has
different coverage:

### OpenAlex — broadest coverage
- 250M+ scholarly works
- Best for: cross-disciplinary searches, citation networks, concept-based search
- API: `https://api.openalex.org/works?search=QUERY`
- Strengths: comprehensive metadata, open-access flagging, concept tagging
- Weaknesses: variable abstract quality, some duplicate entries

### Semantic Scholar — citation network strength
- 85M+ papers with rich citation graph
- Best for: finding related papers, recommendations, paper deep-dives
- API: `https://api.semanticscholar.org/graph/v1/paper/search?query=QUERY`
- Strengths: paper-level citation data, recommendation engine, influential citations
- Weaknesses: less broad than OpenAlex

### INSPIRE-HEP — physics specialty
- Authoritative for high-energy physics, gravitation, cosmology
- Best for: HEP-specific searches, established physics literature
- API: `https://inspirehep.net/api/literature?q=QUERY`
- Strengths: domain-specific accuracy, careful citation tracking
- Weaknesses: limited to physics

### Crossref — DOI verification
- Authoritative DOI lookup
- Best for: verifying citations exist
- API: `https://api.crossref.org/works/{DOI}`
- Use as final verification step

### NASA ADS — astronomy and astrophysics
- Authoritative for astronomical literature
- Best for: astrophysics, cosmology, astronomical instrumentation
- API: requires API key
- Use for astro-heavy searches

### arXiv (via web search)
- Preprint server, often the most current research
- Best for: recent results, papers not yet (or never) journal-published
- Access: via Anthropic web_search with `site:arxiv.org QUERY`

---

## THE 6-PHASE SEARCH PROTOCOL

For comprehensive coverage of a topic, apply all 6 phases. Each phase has a specific
purpose and should produce different results.

### Phase 1 — Broad foundation search

Execute parallel queries across OpenAlex, Semantic Scholar, and INSPIRE-HEP.

```
Query: [topic]
Year filter: 2015 to present (default; adjust by topic age)
Sort: by citation count (descending)
Per source: 15 results
```

**Purpose**: Identify the foundational, most-cited works in the area.

**Output**: A merged, deduplicated list of papers. Track which database returned each.

### Phase 2 — Recent developments

Repeat the search with year filter restricted to the last 3 years.

```
Query: [topic]
Year filter: 2022-2025 (rolling window)
Sort: by citation count (descending), with tiebreaker by date
```

**Purpose**: Identify what's currently active. Foundational papers may be from
decades ago; the current frontier is where new research happens.

**Output**: Papers that may or may not have many citations yet but are recent.

### Phase 3 — Review articles

Search explicitly for reviews and survey articles.

```
Query: "[topic]" review survey
Year filter: 2015 to present
```

**Purpose**: Reviews provide structured overviews and entry points. They cite the
foundational works (helping verify Phase 1) and identify open problems (informing
gap analysis).

**Output**: 5–10 review articles, ideally from different periods.

### Phase 4 — Citation network expansion

Take the top 4–5 most-cited papers from previous phases. For each, query Semantic
Scholar's recommendations API:

```
GET /recommendations/v1/papers/forpaper/{paperId}
```

**Purpose**: Find papers that share readership patterns with foundational works but
might not appear in keyword searches.

**Output**: Recommended papers per seed, deduplicated against previous phases.

### Phase 5 — Ranking and filtering

Combine all results from phases 1–4. Score each paper:

```
score = citations + recency_bonus
where recency_bonus = 200 if year >= 2022
                     = 100 if year >= 2020
                     = 50  if year >= 2018
                     = 0   otherwise
```

This balances established importance against current relevance.

Take the top 25 papers as the working set.

### Phase 6 — AI synthesis with web search

The final phase uses Claude with web_search to:
1. Find papers the direct APIs missed (especially arXiv preprints)
2. Synthesize across all gathered papers
3. Identify the structure of the field
4. Classify papers by their epistemic role

This phase produces structured output (see modes below).

---

## THE 6 ANALYSIS MODES

After Phase 6 has gathered the literature, choose an analysis mode based on the
research question.

### Mode 1 — synthesis (default)

Comprehensive literature review. Use when the user wants to understand a field.

**Prompt template**:
```
You are a physics literature expert. Conduct a comprehensive synthesis for: "[QUERY]"

Gathered papers (top 18):
[paper context]

Search arXiv for additional context. Then produce:

FIELD OVERVIEW:
[3 sentences on current state, dominant approaches, key open questions]

FOUNDATIONAL PAPERS:
[5-8 most important. Include arXiv IDs. One-line annotation each.]

RECENT HIGHLIGHTS (2022-2025):
[5 most significant recent papers with arXiv IDs]

CLAIM HIERARCHY STATUS:
[What is PROVEN? What is CONJECTURED? What is SPECULATIVE? Be specific.]

OPEN PROBLEMS:
[3-5 specific unsolved questions, ranked by tractability]

ESSENTIAL CITATIONS:
[If writing a paper on this topic, these must be cited]
```

### Mode 2 — gaps

Structured gap taxonomy. See `gap-analysis.md` for the dedicated 8-phase protocol.

For a quick gap mode within deep search, use:

```
Topic: "[QUERY]"
Gathered literature: [context]

Search: "[QUERY]" gap unsolved open problem

Produce structured gap taxonomy:
- MATHEMATICAL_GAP: [specific gaps in formalism]
- PHYSICAL_GAP: [interpretation/ontology issues]
- EXPERIMENTAL_GAP: [predictions without measurements]
- UNIFICATION_GAP: [frameworks that don't connect]
- SCALE_GAP: [theory works at one scale, fails at another]
- CONCEPTUAL_GAP: [concepts used without proper definition]
- CITATION_DESERT: [subtopics that went quiet]
- CROSS_DISCIPLINARY: [tools from other fields not applied here]

For each gap: what's missing, why it matters, what would close it, tractability.
```

### Mode 3 — audit (pre-submission preparation)

For preparing to write or submit a paper. Identifies what reviewers will check.

```
Pre-submission audit for paper on: "[TOPIC]"
Literature: [context]

Produce AUDIT BRIEF:
SUB-FIELD: [canonical arXiv category + reason]
CLAIM HIERARCHY RISKS: [common over-inflations in this area]
DIMENSIONAL PITFALLS: [typical errors in this field]
ESSENTIAL REFERENCES: [must-cite papers with arXiv IDs]
FORBIDDEN CLAIMS: [what cannot be claimed without extraordinary evidence]
REFEREE EXPECTATIONS: [what a careful PRD/JHEP referee will check]
RELATED WORK TO ACKNOWLEDGE: [papers that might overlap — check priority]
```

### Mode 4 — predict (next contribution)

Strategic research planning: what would be the next logical advance?

```
Field trajectory analysis: "[TOPIC]"
Recent literature: [context]

Search arXiv for the latest 2024-2025 work.

FIELD TRAJECTORY:
[Map: 10yr ago → 5yr ago → 2yr ago → now]

LOGICAL NEXT STEP:
[Given this trajectory, what result would naturally come next?]

PREDICTED FORMULA/RESULT:
[If a new result exists, what would its structure be?]

METHODOLOGY PREDICTION:
[Which mathematical/computational approach is most likely to yield it?]

WHO IS BEST POSITIONED:
[Active groups with the tools and proximity for this contribution]

EXPERIMENTAL WINDOW:
[Measurement in 3-5 years that could validate/invalidate]

CONFIDENCE LEVEL: HIGH/MEDIUM/LOW
```

### Mode 5 — contrarian (dissent search)

Find papers that challenge the consensus. Critical before relying on a "well-known"
result.

```
Critical search for: "[TOPIC]"

Search:
1. site:arxiv.org "[TOPIC]" criticism
2. "[TOPIC]" wrong incorrect error reanalysis
3. Alternative approaches with different results

CONTESTED RESULTS:
For each: claim, challenge, papers (both sides), assessment

KNOWN ERRORS AND CORRECTIONS:
[Papers with acknowledged errors]

ALTERNATIVE FRAMEWORKS:
[Different predictions, how to discriminate]

WIDELY-CITED BUT SHAKY:
[High-citation results with fragile assumptions]

MOST VULNERABLE ASSUMPTION:
[The single assumption most likely wrong]
```

### Mode 6 — referee (mock referee report)

Simulate a critical referee for a paper or proposal.

```
Mock referee report for: "[TOPIC]"

Search recent papers in this area for current standards.

FIRST READING:
[What strikes you immediately]

TECHNICAL OBJECTIONS:
1. [Specific mathematical check]
2. [Limiting case demand]
3. [Prior work comparison]
4. [Dimensional analysis check]
5. [Perturbative validity check]

CLAIM CLASSIFICATION CHALLENGES:
[Statements that overclaim — calling theorem what is conjecture]
[Results to downgrade]

PRIOR WORK CITATIONS:
[Must-cite papers; partially overlapping papers to distinguish]

SCOPE QUESTIONS:
[Generality claims to challenge]
[Hidden assumptions narrowing the result]

RECOMMENDATION CRITERIA:
ACCEPT if: [conditions]
MAJOR REVISION if: [what must change]
REJECT if: [unrecoverable issues]

HARDEST QUESTION:
[The one question revealing fatal flaw if unanswered]
```

---

## QUERY CONSTRUCTION

### Keep queries short and specific
- 1-6 words for best results
- Start broad, narrow if needed
- Use specific physics terminology when available

### Smart query routing
- Numeric ID matching `\d{4}\.\d{4,5}` → likely arXiv ID, route to direct paper lookup
- DOI matching `10\.\d{4,}` → route to Crossref direct lookup
- Author names → use author search APIs
- Concept queries → use OpenAlex concept search

### Avoid these in standard queries
- The minus operator (`-`)
- The site operator (`site:`) except in deliberate web search
- Quotes for exact matching (unless verifying a specific phrase)

These tend to return empty or unexpected results in academic APIs.

---

## RESULT DEDUPLICATION

Papers may appear in multiple databases. Deduplicate using priority order:

1. arXiv ID (most reliable)
2. DOI
3. Title-similarity (first 50 chars, lowercased)

When duplicates are detected, prefer the source with richer metadata (typically S2
or OpenAlex over INSPIRE).

---

## OUTPUT STANDARDS

Search outputs must always include:

For each paper:
- Title
- Authors (truncated to first 3 with et al. notation)
- Year
- Journal/venue (if published)
- Citation count
- arXiv ID and DOI (if available)
- Source database (oa/s2/ins/ads)

Never present papers without source attribution. Never invent metadata.

---

## INTEGRATION WITH ANTI-FABRICATION

After deep search, before using any paper as a reference:

1. Verify the paper exists (Citation Guard step)
2. Confirm the metadata matches what was returned by the search
3. If using the paper for a specific claim, read the abstract or paper to confirm the
   claim is in fact supported

LLMs sometimes "remember" the existence of papers based on training data patterns,
producing plausible-sounding references that don't actually exist. Direct database
verification is the only reliable check.

---

## RATE LIMITS AND ETIQUETTE

Respect API rate limits:
- OpenAlex: 100,000 requests/day (with mailto), 10/sec
- Semantic Scholar: 100 requests/5 minutes for free tier
- INSPIRE-HEP: ~15 requests/second
- Crossref: please include mailto for polite pool

Insert 200ms delays between queries when running batches. For large literature
sweeps, batch 20–30 queries with appropriate spacing.

---

## CRITICAL: COVERAGE IS NOT COMPLETENESS

The 6-phase protocol provides high coverage, but no search is complete. Always
acknowledge:

- Some papers may not be indexed
- Recent preprints may not appear in search results
- Non-English literature may be undercovered
- Conference talks and unpublished work are not searchable

State coverage limitations explicitly in any literature review:

> "This review covers literature indexed in OpenAlex, Semantic Scholar, and INSPIRE-HEP
> as of [date]. Recent preprints may be undercovered. Non-English literature is not
> systematically reviewed."

This honest framing is more useful than implicit claims of completeness.
