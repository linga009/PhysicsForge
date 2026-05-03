# Changelog

All notable changes to PhysicsForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project loosely follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `ETHICS-AND-USAGE.md` — comprehensive ethics and usage guidelines covering disclosure requirements, authorship rules, verification responsibilities, peer-review confidentiality, framework-specific risks, a current (2026) summary of major publisher policies (Nature, Science, APS, Elsevier, Springer, Wiley, Taylor & Francis, SAGE, IEEE, ACM, arXiv, ICMJE, PLOS), sample disclosure statements at three levels (minimal / moderate / heavy), educational-use guidance, a pre-submission checklist, and references to primary policy sources.
- README section linking to ethics document and summarising key points.

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
