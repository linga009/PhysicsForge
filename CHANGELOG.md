# Changelog

All notable changes to PhysicsForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project loosely follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Nothing yet.

## [3.0.0] — 2026-10-07 (Claude Code Plugin — Real Tools Wired In)

The skill content developed across v2.0–v2.9 below was built and validated
locally but never pushed past `main`'s v1.0.0 snapshot. This release ships all
of it at once, restructured as an installable **Claude Code plugin**, and
closes the gap this project kept finding: the skill's own instruction files
describing verification protocols never actually pointed at the real,
test-backed tools built to perform them.

### Added — Claude Code plugin structure

- `.claude-plugin/plugin.json` — plugin manifest (v3.0.0).
- `.claude-plugin/marketplace.json` — self-hosted marketplace listing, so the
  plugin can be installed with `/plugin marketplace add linga009/PhysicsForge`.
- `commands/audit.md`, `commands/gap-analysis.md`, `commands/citation-check.md`,
  `commands/derivation-check.md`, `commands/quantum-check.md`,
  `commands/preregister.md` — six slash commands, each invoking the real
  backing tool in `scripts/` rather than describing the protocol in prose
  alone.
- `scripts/` — `tools/` (from the previously-unmerged `tool/pre-registration`
  branch) renamed and relocated here: `citation_guard.py`, `deriv_check.py`,
  `quantum_check.py`, `prereg.sh`, `test_kerr_check.py`, their matching
  `test_*.py` regression suites, `golden_citations.jsonl`, and `STATUS.md`.
- `.github/workflows/tools-ci.yml` — carried over with paths updated from
  `tools/` to `scripts/`; runs the four deterministic test suites and the
  pre-registration audit on every push.
- `preregistrations/2026-09-28-isotope-shift.md` and
  `results/isotope_shift_result.txt` — the worked pre-registration example.

### Added — reconciled the full local reference set onto GitHub

`main` had fallen behind the actively-developed local skill: only 7 of the
(now) 25 reference files were tracked, and three files that existed only in a
separately-installed local copy (`extraordinary-claims.md`, `unit-systems.md`)
had never been reconciled with the v2.5–v2.9 lineage below. All three sources
are merged into `skills/physicsforge/references/` in this release, alongside
`methods.md` (the 9-method derivation toolkit, previously tracked on `main`
but never referenced by `SKILL.md`'s routing table).

### Fixed — the skill's protocols now actually point at the real tools

Diagnosed directly (by reading the files, not assumed): none of the skill's
instruction files referenced the test-backed tools built in v2.9 at all.
- `references/citation-guard.md` — its "TOOLS" section named a
  `verify_citations.py` script that never existed. Replaced with the actual
  `scripts/citation_guard.py` invocation, its real CLI flags, and the
  `/citation-check` command.
- `references/verification.md` — added a "PREFER THE REAL TESTED TOOLS"
  section pointing at `scripts/deriv_check.py`, `scripts/quantum_check.py`,
  and `scripts/test_kerr_check.py`'s documented lessons (symbol-identity
  traps, `simplify(...) == 0` false negatives) before its existing ad-hoc
  sympy patterns, which remain as a fallback.
- `SKILL.md` — added a "REAL TOOLS" section mapping each tool to the protocol
  it backs and the slash command that invokes it; added routing-table and
  activation-command rows for `methods.md`, `extraordinary-claims.md`,
  `unit-systems.md`, and pre-registration (none had any routing entry before).

### Changed

- `skill/` renamed to `skills/physicsforge/` (the layout a Claude Code plugin
  scans by default; also still usable standalone per the Installation
  section).
- `README.md` — added a Claude Code Plugin installation section (primary
  path); updated all `skill/` path references to `skills/physicsforge/`;
  updated the repository-structure diagram; corrected stale line counts in
  the reference-modules table and added a pointer to `SKILL.md`'s own
  REFERENCE FILES section as the authoritative, maintained index now that the
  module count has grown from 6 to 25.
- `ETHICS-AND-USAGE.md` (added previously, carried forward unversioned) is
  included in this release's version bump.

---

## v2.9 — September 2026 (First Real Tools — Agentic Verification, Not Just Prompted)

### Shipped — pushed to GitHub, [PR #2](https://github.com/linga009/PhysicsForge/pull/2), CI observed running for real

Branch `tool/pre-registration` pushed; CI ran on GitHub's own infrastructure
for the first time, consistently across both the push and the PR trigger:

- `test-tools` (all four deterministic suites): **PASS**, 51s.
- `prereg-audit`: **PASS**, 5–6s — `prereg.sh audit` correctly verified the
  isotope-shift pre-registration from real commit history on a fresh runner.
- `citation-spot-check`: **FAIL**, both runs, same cause — a Crossref call
  returned `http_406`, consistently, never observed locally. `406` isn't in
  the retryable set. Most likely: Crossref treating GitHub's shared runner IP
  ranges differently than a residential IP. `continue-on-error: true` worked
  exactly as designed — the overall run still reports success, the PR isn't
  blocked. Real, open, not yet fixed; documented rather than hidden or
  guessed at. Full account in `scripts/STATUS.md`.

### Added — `test_kerr_check.py`: from-first-principles validation of the Kerr paper's central result

Using EinsteinPy's actual `Kerr()` tensor (not a hand-typed metric), directly
derives the Hamilton-Jacobi separation of Kerr null geodesics and checks it,
to exact symbolic zero, against `kerr_elliptic_thesis_v2_corrected.tex`'s
printed $R(r)$. Separability itself is tested directly (a vanishing mixed
partial derivative of the Hamilton-Jacobi bracket), not assumed via Carter's
ansatz — genuinely stronger than checking the claim against a textbook, which
is what the paper itself already does.

8/8, after three real bugs were found and fixed in the derivation code (none
in the paper): a symbol-identity trap (`Kerr()`'s internal `r, theta` are
different objects from external symbols with the same print-name, so
`.subs()` silently no-ops — caught by a loud `TypeError`, not a subtle wrong
answer); `sympy.simplify(diff) == 0` giving a false negative on expressions
later confirmed equal by direct numeric substitution (`.equals(0)` even
returned `None` once — numeric substitution was the more trustworthy check
here, not the "more symbolic" one); and a genuine sign error in the
derivation's own algebra, caught by testing against both $+R$ and $-R$ rather
than assuming which was correct. Full account in `scripts/STATUS.md`.

Deduplicating a redundant symbolic matrix inversion across test functions cut
runtime from >60s to a measured 25s.

### Added — `.github/workflows/tools-ci.yml`: CI wiring, on an unpushed branch

Three jobs: the three deterministic test suites on every push/PR touching
`tools/`; a separate `continue-on-error` job spot-checking `citation_guard.py`
against the real golden set (genuine network calls, allowed to fail without
blocking unrelated PRs); a `prereg-audit` job that runs `prereg.sh audit`
against any tracked pre-registration, so a human forgetting to audit locally
doesn't let an unverified confirmatory claim through.

Honestly scoped: YAML validity, individual install steps, and every command
were confirmed locally, including `prereg.sh audit`'s exact CI invocation
from the repo root. The workflow has not yet run on GitHub's own
infrastructure — nothing on `tool/pre-registration` has been pushed. "Wired
into CI" and "observed passing in CI" are kept as distinct claims.

### Packaged — `deriv_check.py` and `quantum_check.py`: demo scripts to real libraries + test suites

Both tools' `__main__` demo blocks are replaced with `test_deriv_check.py`
(7/7) and `test_quantum_check.py` (6/6), standalone zero-framework regression
suites mirroring `test_retry.py`'s pattern. Both libraries kept deliberately
free of a generic CLI — the real caller is Claude writing Python during Phase
5 Symbolic Verification, not a speculative expression-description file
format with no demonstrated need (over-engineering `idea-to-production-tool`
warns against).

Each "deliberately wrong" calibration case is now framed as an explicit
meta-level assertion (the passing test is "the tool correctly says NOT ok",
never "the claim is true") so a future CI failure there unambiguously means
the checker broke, not that a withdrawn claim became true.

One real error was caught and corrected while writing `test_quantum_check.py`:
the earlier report of the incomplete-Kraus-set test's failure magnitude
(quantum_check.py's session) was itself slightly wrong — 0.15 is
`dim × (missing term's weight)` under QuTiP's default trace norm, not the
missing weight alone as first stated. Corrected in `scripts/STATUS.md`, not
left standing.

### Hardened — `citation_guard.py`: retry, backoff, and caching, all tested

Added exponential backoff with jitter for transient failures (connection
errors, 5xx), `Retry-After` honored on 429s, 404s correctly never retried,
and a 24h-TTL on-disk cache (`--no-cache` to bypass). Validated with a new
deterministic suite (`test_retry.py`, 12/12) using an injected fetcher and
fake clock instead of hoping the real network happens to be flaky during the
test — per "determinism before deltas." Two real bugs were caught by that
suite and by the real golden-set rerun, not assumed away: a cache directory
that wasn't recreated after removal (silent write failures), and
`citeguard.check_doi()`'s injectable cache parameter going unused, leaving
its own internal Crossref calls uncached — fixing the second took a warm
golden-set run from ~44% faster to **6.5× faster** (10.1s → 1.5s), with
identical, correct results throughout.

### Added — `prereg.sh`: pre-registration, vendored and fully validated

Vendored from `K-Dense-AI/science-superpowers` (MIT license, notice
preserved), adapted only in default paths — the mechanism (git commit
ancestry via `git merge-base --is-ancestor`, not forgeable timestamps) was
already correctly designed. This is architecturally different from every
other guardrail in this project: it *prevents* post-hoc parameter/hypothesis
adjustment (`anti-fabrication.md` Mode 2) rather than detecting it after the
fact.

Validated end-to-end in a real git repository, not asserted: pre-registered a
genuinely fresh, never-before-computed claim (the $^{13}$C isotope $T_c$ shift
implied by the superconductivity paper's falsification chapter, $T_c\propto
M^{-\alpha}$), froze it, then computed the answer (−3.9355%, confirming the
registered 3.5–4.5% range). `prereg.sh audit` passed. A deliberate adversarial
test — editing the registered range *after* seeing the answer, exactly the
dishonest move this tool exists to prevent — was then correctly caught as a
FAIL with the exact diff shown, before the state was restored to the honest
PASS. One real bug was found in the process (a spurious path warning on this
session's particular temp-directory layout) and documented, not hidden.

### Added — three tool-backed verifiers, each validated on real data

Following `idea-to-production-tool`'s discipline (prototype one insight,
validate on real messy data, mine prior art, evaluate honestly, retract what
doesn't replicate) rather than building a speculative agentic framework.
Full details, including honest negative results and bugs caught in the
process, are in `scripts/STATUS.md` — summarized here:

- **`citation_guard.py`** — real implementation of `citation-guard.md`'s
  verdict taxonomy. Delegates retraction detection to the existing, tested
  `citeguard` library rather than reimplementing it; adds DOI metadata-drift
  checking and arXiv support on top. Validated 13/13 against a golden set
  built from this project's own already-verified/refuted citations; caught
  and fixed one real bug (an http→https redirect silently producing a false
  not-found) in the process.
- **`deriv_check.py`** — real implementation of `verification.md` Patterns 1
  (dimensional analysis, via `sympy.physics.units`'s actual `DimensionSystem`)
  and 2/7 (limiting cases). Validated against six real claims from this
  project's own manuscripts (the superconductivity paper's exact $T_c$-vs-
  $\omega_{\log}$ linearity, its 2/3 biaxial-pressure factor, its printed
  constant, the carbon-capture paper's dimensional consistency, and the
  deliberately-withdrawn 300 K claim, which correctly fails by the exact
  3759.86 K computed by hand earlier in this session). Two real bugs in the
  checker itself were caught and fixed by running it, not hidden.
- **`quantum_check.py`** — QuTiP-backed unitarity/CPTP/entanglement checks.
  No QM/QI paper exists in this project yet, so this is calibration against
  canonical textbook facts (Tsirelson's bound, Bell-state entropy, the
  depolarizing channel), explicitly distinguished from validation against our
  own messy data — that distinction is Pólya Pattern 2 territory
  (`plausible-reasoning.md`) and is kept visible, not blurred.

### Pauli Protocol — honest coverage audit
Two of the seven Pauli Protocol checks ([5] dimensional, [6] limiting case)
are now genuinely tool-backed rather than self-reported; one more ([4]
conservation/symmetry) is partially covered for the quantum-mechanical case.
The other four are judgment calls that shouldn't be hard-automated — see
`scripts/STATUS.md` for the full table and the reasoning for each.

### Researched, explicitly not built this round — with reasoning
`Cadabra2` (no PyPI wheel for this platform — real negative result),
`SageMath`/`Maxima`/`GAP` (deferred: no queued claim to validate against yet,
and this session has first-hand evidence toolchain installs here are costly),
Lean 4 / `leanprover-community/physlib` (real and relevant — 1000+ formalized
quantum-information theorems — but not installed speculatively; a concrete
first target is proposed in `scripts/STATUS.md` instead of building blind).

---

## v2.8 — September 2026 (Theoretician's Reasoning — Literature Grounding)

### Added — Three new reference files, grounded in the published literature on how theoretical research is actually done

Everything added before this release was original synthesis (the Pauli Protocol,
Anti-Fabrication Protocol, Iron Rules, etc.) or drawn from adjacent skill projects
(K-Dense, academic-research-skills). This release adds machinery drawn from named,
citable sources in the philosophy and practice of mathematics/physics research,
chosen specifically to fill gaps the existing (already extensive) apparatus didn't
cover — verified by comparing against `methods.md`'s nine derivation methods,
`anti-patterns.md`'s twenty entries, and `scholar-eval.md`'s eight dimensions
before writing anything, to avoid duplicating what already existed.

**`references/counterexample-protocol.md`** — Imre Lakatos, *Proofs and
Refutations* (Cambridge University Press, 1976). Names the specific responses to
a counterexample against your own claim (surrender, monster-barring,
exception-barring, monster-adjustment, lemma-incorporation, proofs-and-refutations
proper) and forbids monster-barring — added to `SKILL.md`'s FORBIDDEN BEHAVIORS.
Motivated directly by a real case: a manuscript's "the target region is empty"
claim, refuted by a real material (LaH₁₀) sitting inside that region, and honestly
narrowed rather than defended.

**`references/breakthrough-red-flags.md`** — Scott Aaronson's "Ten Signs a Claimed
Mathematical Breakthrough is Wrong" (2008) and "Eight Signs a Claimed P≠NP Proof is
Wrong" (2010), and John Baez's Crackpot Index (1998, updated). A sociological/
structural checklist for claimed breakthroughs, distinct from ScholarEval's
internal-quality rubric. Notably, Aaronson's P≠NP Sign 1 ("can't explain why the
method fails on a known-easy neighboring problem") independently reproduces this
skill's own Trivial Reduction Test — documented as a cross-check, not a
coincidence to ignore.

**`references/plausible-reasoning.md`** — George Pólya, *Mathematics and
Plausible Reasoning* (Princeton University Press, 1954) and *How to Solve It*
(1945). A graded-confidence framework for conjectures still being formed —
distinct from the Claim Hierarchy's categorical labels — built around five
patterns (unexpected vs. designed-in confirmation, generic vs. special-case
checks, independent vs. repeated evidence, structural vs. surface analogy,
survived-attack evidence). Deliberately qualitative (Low/Moderate/High), not a
fabricated numeric score.

**`references/anti-fabrication.md`** — added a fifth failure mode (unaccounted
degrees of freedom / ghosts, grounded in Dirac's constraint algorithm and the
Ostrogradsky instability theorem), explicitly separated from Schwartz's original
four so the attribution stays accurate.

Cross-references added in `paper-analysis.md`, `scholar-eval.md`,
`adversarial-review.md`, and `formula-prediction.md` so the new files are reached
from the existing workflows, not just from `SKILL.md`'s routing table.

---

## v2.7 — May 2026 (Discovery Engine — Deep Architecture)

### Added — Cross-Engine Triangulation + Seed Expansion Graph

The four enhancements in v2.6 hardened the existing pipeline against
known failure modes. The two enhancements in v2.7 change the pipeline's
*structure*: the search becomes broader (3 parallel engines) and deeper
(each surviving seed spawns a cluster of 3 children).

**Enhancement 5: Cross-Engine Triangulation**

Phase 2 now runs three engines IN PARALLEL with distinct system prompts
and personas:
- ENGINE A — SYNTHESIST (recognises isomorphisms across fields)
- ENGINE B — CONTRARIAN (challenges accepted dogma)
- ENGINE C — CROSS-DISCIPLINE EXPLORER (imports tools from non-physics)

Each engine produces 20 seeds independently. The three pools (60 seeds)
are combined for the adversarial pass. Seeds appearing in multiple
engines (after semantic clustering by claim overlap) get a +1.5 boost
to their combined score. Seeds appearing in one engine get no boost.

This addresses the v2.6 limitation that even with structured prompting,
a single creative pass produces ideas in the natural orbit of the model's
trained patterns for the target domain. Three engines with adversarial
personas surface ideas a single engine would miss.

**Enhancement 6: Seed Expansion Graph (cluster-not-isolate)**

After the adversarial pass narrows the seed pool, a new cluster
construction phase runs. For each surviving parent seed, the model
generates 3 child variations:
- CHILD-S (SHARPENING):     mathematically more precise version
- CHILD-G (GENERALISATION): same insight applied to a broader class
- CHILD-D (DUAL):           inverse problem or opposite direction

The seed pool grows from ~30 (post-adversarial) to ~120 (parents +
children). Development phase selects from the combined pool — a strong
child is often more developable than its weak parent.

Cluster richness becomes a scoring signal:
- HIGH richness (2+ strong children): +1.0 to combined score
- MEDIUM richness (1 strong child): +0.3
- LOW richness (isolated peak):     -0.5 penalty

The unit of output is the cluster, not the individual idea. A user
pursuing a cluster has 4 related calculations to attempt rather than 1,
which dramatically increases the chance of landing on a tractable result.

### Calibration metrics for v2.7

Targets over v2.6:
- Cluster yield: ≥3 strong clusters per run (was N/A)
- Engine-agreement signal: 15–25% of seeds in ≥2 engines (was 0%)
- Wasted-development rate: <15% (was 10–20%)
- Cross-disciplinary fraction: 70%+ (was 50%)

If these don't improve in a 5-run trial, the architectural changes can
be reverted to v2.6. The 2.5× API cost must deliver proportional quality.

### Migration

v2.7 is structurally backward-compatible. The skill description and routing
entries are additive over v2.6.

## v2.6 — May 2026 (Discovery Engine — Performance Hardening)

### Added — Four enhancements addressing observed failure modes

After end-to-end testing of the v2.5 Discovery Engine on a real research
domain (spectral geometry of vacuum energy), four failure modes were
identified and addressed in v2.6:

**F1: Reframings passed novelty but failed depth check**
**F2: Optimistic clarity scoring when FIRST STEP couldn't be made concrete**
**F3: Recency blind spot — papers <12 months old missed by default**
**F4: Pattern drift — ideas in natural orbit, not genuinely cross-disciplinary**

The enhancements (documented fully in `references/discovery.md`):

1. **Adversarial Ideation Pass** — between Phase 2 (seed generation) and
   Phase 3 (development), a Skeptic persona tags each seed with one of:
   REFRAMING, SPECIAL_CASE, TRIVIAL, BLOCKED, WEAK, NONE. Seeds tagged with
   the first four are eliminated. Expected to remove 30–50% of seeds before
   they consume development effort.

2. **First-Equation Stress Test** — Phase 3 output now requires a FIRST
   EQUATION field containing the literal mathematical object to compute
   (formula, integral, limit, operator definition — not English prose).
   Ideas marked PROGRAMME (research direction without a concrete first
   equation) automatically have Clarity and Tractability scores reduced
   by 3 points each.

3. **Failure-Mode Taxonomy Gate** — between Phase 4 (novelty check) and
   Phase 5 (ranking), each idea is classified against a 9-mode failure
   taxonomy. Ideas tagged SCHEME_DEP, FORMAL_SYM, REFRAMING, OBVIOUS_LIMIT,
   or CHANGE_OF_VARS are auto-rejected. NO_GO_BLOCKED and ANTHROPIC are
   flagged with major warnings. ADJACENT_FIELD ideas are redirected to
   theory-bridge.md.

4. **Forced-Pair Triangulation** (alternative Phase 2 mode) — a constrained
   generation approach that pairs the target domain with pre-selected
   "outside fields" (category theory, p-adic analysis, optimal transport,
   persistent homology, etc.) and forces ideas at each intersection.
   Outside-field ratio target rises from ~25% to ~50%.

### Migration

v2.6 is fully backward-compatible with v2.5. The base 5-phase pipeline
still works; the enhancements are additive.

## v2.5 — May 2026 (Discovery Engine Release)

### Added — Discovery Engine

**`references/discovery.md`** — A creative idea generation protocol that
inverts the standard research workflow. Instead of "given the existing literature,
what's the next step?" it asks "what hasn't been tried, drawing on connections across
all of science?"

The protocol uses seven creative modes, each targeting a different type of novelty
gap:

1. **ANALOGY IMPORT** — map the unsolved problem to a solved one in another field
2. **TOOL TRANSPLANT** — apply a technique from elsewhere that hasn't been used here
3. **LIMITING CASE** — explore an extreme parameter nobody has studied
4. **SYMMETRY QUESTION** — break, extend, gauge, or deform a known symmetry
5. **SCALE INSERTION** — identify a new dimensionless ratio not yet studied
6. **CONTRADICTION HUNT** — find two results that imply an untested prediction
7. **INVERSE PROBLEM** — flip the standard direction (given outcome, find theory)

Five-phase pipeline: Landscape mapping → Creative ideation (20 seeds) → Development
(top N) → Novelty verification (arXiv check) → Scoring & ranking
(Novelty 35% + Tractability 30% + Significance 25% + Clarity 10%).

The protocol explicitly forces multi-disciplinary thinking and contrarianism ("at
least 2 ideas must challenge widely-accepted assumptions"). Ideas already in the
literature are filtered out via the novelty verification phase.

### Migration

v2.5 is fully backward-compatible with v2.1. To upgrade: replace `SKILL.md` and
add `discovery.md` to references.

## v2.1 — May 2026

Adds three new reference files derived from a deep audit of the K-Dense AI scientific
skills repository (github.com/K-Dense-AI) and the academic-research-skills repository
(github.com/Imbad0202/academic-research-skills). These additions formalise patterns
that were implicit in v2.0 and codify them into protocols.

### Added — three new reference files

**`references/scholar-eval.md`** — Implements the **ScholarEval framework**
(arXiv:2510.16234) adapted for theoretical physics. Quantitative 8-dimension
scoring (Problem Formulation, Literature Engagement, Mathematical Setup,
Derivation Rigor, Verification, Physical Interpretation, Writing Quality,
Citation Verification) complementing the qualitative Pauli Protocol. Five-tier
verdict thresholds from Exceptional (4.5+) to Major rework (<3.0).

**`references/adversarial-review.md`** — Formalises **Devil's Advocate review
with concession scoring**, directly addressing the "Claude loves to please"
failure mode. Concession threshold (pushback scored 1–5, concession only at
≥4), anti-sycophancy rule, no-consecutive-concessions, two-pass
advocate/adversary review pattern.

**`references/dialogue-health.md`** — Self-monitoring protocol for long
sessions and multi-day calculations: Persistent Agreement, Premature
Convergence, Frame Lock, Context Rot, Agentic Laziness, Concern Suppression.
Intent detection (Exploratory / Goal-Oriented / Diagnostic / Pedagogical) and
a checkpoint pattern for multi-day work.

### Sources

- Eskelinen et al., "ScholarEval: Research Idea Evaluation Grounded in Literature"
  (arXiv:2510.16234, 2025)
- K-Dense AI scholar-evaluation skill (github.com/K-Dense-AI/claude-scientific-writer)
- Imbad0202 et al., "Academic Research Skills for Claude Code"
  (github.com/Imbad0202/academic-research-skills, deep-research v2.7)
- Anthropic, "Long-running Claude for scientific computing" (Mishra-Sharma, March 2026)
- Schwartz, "Vibe physics: The AI grad student" (Anthropic, March 2026)

### Migration

v2.1 is fully backward-compatible with v2.0. New activation commands and
routing entries are additive.

---

## v2.0 — May 2026

This was a substantial enhancement built on lessons from real-world LLM-assisted
physics research and the methodologies prototyped during the Forge Physics Review
consultancy build.

### Added — six new reference files

**`references/deep-search.md`** — Multi-database search protocol replacing
single-source queries. Six-phase systematic search across OpenAlex, Semantic
Scholar, INSPIRE-HEP, Crossref, NASA ADS, and arXiv. Eight specialised modes
(synthesis, gaps, audit, recent, compare, predict, contrarian, referee).

**`references/gap-analysis.md`** — Replaces the single-step gap taxonomy in v1
with an eight-phase systematic protocol: Foundation Mapping, Analogue Survey,
Mathematical Completeness, Experimental Status, Cross-Disciplinary Tools,
Citation Desert Map, Contradiction Registry, Tractability Ranking.

**`references/formula-prediction.md`** — Buckingham π theorem methodology with
explicit epistemic status tagging, distinguishing theorem-grade dimensional/
symmetry results from heuristic analogy-based ones. Eight-step procedure from
quantity enumeration through discriminating measurement.

**`references/theory-bridge.md`** — Cross-framework analysis with seven-type
relationship classification (Regime-Complementary through
Fundamentally-Incompatible). Seven-step protocol from framework specification
through resolution strategy ranking.

**`references/citation-guard.md`** — Mandatory pre-delivery citation
verification protocol. Every citation must be database-verified before
delivery, with a hard block on FAIL verdict.

**`references/anti-fabrication.md`** — Documents the four failure modes
observed in the Schwartz Harvard 2026 experiment: Fake Results, Parameter
Adjustment, Formula Transposition, Oversimplification. Detection signals,
calibration questions, and recovery protocols for each.

### Updated — SKILL.md

Methodology expanded from five phases to eight. Anti-fabrication checks
embedded in every phase. Self-audit required after derivation generation.
Citation Guard required before delivery.

### Migration

v2.0 is fully backward-compatible. All v1.0 activation commands work
unchanged; new activation commands are additive.

---

## [1.0.0] — 2026-05-03

### Added — initial public release

#### Anthropic Skill (`skill/`)

- `SKILL.md` — dispatcher with identity / cognitive persona, claim hierarchy (Theorem / Proposition / Lemma / Corollary / Conjecture / Heuristic / Observation), Millennium-class problem protocol with mandatory honesty preamble, five-phase research methodology (literature reconnaissance → gap taxonomy → derivation engine → Pauli Protocol → symbolic verification), epistemic labelling system, activation command routing.
- `references/output-rules.md` — ten anti-truncation rules, word-count minimums per paper section, forbidden placeholder list, paper generation sequence.
- `references/latex-engine.md` — document class selection, full preamble (including `tikz-feynman`, `cleveref`, `physics`, custom theorem environments and physics macros), all fourteen paper sections with templates, equation environment standards, table standard, Feynman diagram standard, label prefix conventions, paper length calibration, compilation instructions.
- `references/paper-analysis.md` — eight-step audit workflow (intake → claim extraction → dependency graph → derivation audit → hidden assumption hunt → consistency checks → novelty assessment → remaining gap statement → proposed extension), audit output format, anti-patterns.
- `references/verification.md` — seven `sympy` verification patterns (dimensional analysis, limiting cases, algebraic identities, sign / convention checks, integral and operator identities, tensor / index contractions, known-formula recovery), failure interpretation guide, sympy limitations.
- `references/examples.md` — three worked calibration examples: PRL "Identifying the Gap" section on the cosmological constant problem, paper critique of a fake Riemann Hypothesis proof, six-angle symbolic verification of $E^2 = (pc)^2 + (mc^2)^2$.
- `references/domains.md` — eleven domain-specific modules (fundamental physics, QM & quantum information, thermodynamics & statistical mechanics, cosmology & astrophysics, condensed matter, PDE & harmonic analysis, geometric analysis, stochastic analysis & SPDE, numerical methods, mathematical physics toolkit), plus a fifteen-row cross-domain bridge table.

#### Gemini Gem (`gemini-gem/`)

- `instructions.md` — single-file consolidated version containing all skill content (zero information loss), restructured for Gemini's single-prompt environment.

Improvements over the multi-file skill:

- Operational pass/fail criteria for each Pauli Protocol check.
- Explicit anti-sycophancy rules (no soft openings, no capitulation under pushback, no hedge-praise, calibrated confidence statements).
- Forbidden-phrase list for Millennium-class responses (*"I have solved"*, *"this proves"*, *"QED"*, *"this resolves"*, *"this settles"*, *"definitively shows"*).
- Pushback-resistance rule with verbatim response when user pressures for theorem-relabelling.
- First-response protocol covering Millennium-trigger detection, paper-upload confirmation, and one-question disambiguation.
- Explicit MathJax delimiter conventions for Gemini's LaTeX rendering.
- Code block conventions per content type.
- Session-continuity rule for handling no-memory-across-chats.
- Refusal templates with five concrete trigger conditions.
- Nine smoke-test prompts with expected behaviours.

#### Repository scaffolding

- `README.md` — comprehensive description, installation across three LLM environments, core concepts, reference module index, activation commands, worked example, use cases, limitations, FAQ, roadmap.
- `LICENSE` — MIT.
- `CONTRIBUTING.md` — five contribution paths, PR checklist, style guide.
- `CHANGELOG.md` — this file.
- `.gitignore` — standard editor / OS / build artefact exclusions.
- `.github/ISSUE_TEMPLATE/bug_report.md` — structured rule-violation report.
- `.github/ISSUE_TEMPLATE/feature_request.md` — structured enhancement proposal.
- `.github/PULL_REQUEST_TEMPLATE.md` — PR self-checklist.

[1.0.0]: https://github.com/<your-username>/physicsforge/releases/tag/v1.0.0
