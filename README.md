<div align="center">

# PhysicsForge

**An ultra-rigorous physics & mathematics research engine for large language models.**

*Finds gaps in established theories. Derives new formulae from first principles. Audits research papers line-by-line. Verifies derivations symbolically. Produces compilable LaTeX manuscripts. Refuses to fake proofs.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skill Format](https://img.shields.io/badge/format-Anthropic%20Skill-blue.svg)](#installation)
[![Gemini Gem](https://img.shields.io/badge/format-Gemini%20Gem-4285F4.svg)](#gemini-gem-installation)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing)
[![Status](https://img.shields.io/badge/status-active-success.svg)](#)

</div>

---

## Table of Contents

- [What is PhysicsForge?](#what-is-physicsforge)
- [Why it exists](#why-it-exists)
- [Features](#features)
- [Installation](#installation)
  - [As a Claude / Anthropic Skill](#as-a-claude--anthropic-skill)
  - [As a Gemini Gem](#as-a-gemini-gem)
  - [Generic LLM (ChatGPT, Mistral, local models, etc.)](#generic-llm-chatgpt-mistral-local-models-etc)
- [Repository structure](#repository-structure)
- [Core concepts](#core-concepts)
  - [The Claim Hierarchy](#the-claim-hierarchy)
  - [The Pauli Protocol](#the-pauli-protocol)
  - [The Millennium-Class Protocol](#the-millennium-class-protocol)
  - [Gap Taxonomy](#gap-taxonomy)
  - [Epistemic Tags](#epistemic-tags)
- [Reference modules](#reference-modules)
- [Activation commands](#activation-commands)
- [Worked example](#worked-example)
- [Use cases](#use-cases)
- [Limitations](#limitations)
- [FAQ](#faq)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Ethics & Usage Guidelines](#ethics--usage-guidelines)
- [Citation](#citation)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## What is PhysicsForge?

PhysicsForge is a **structured prompting framework** that turns a general-purpose large language model into a frontier-level physics and mathematics research assistant. It is delivered as either:

1. A **multi-file skill** in the [Anthropic Skill format](https://docs.claude.com/en/docs/agents-and-tools/agent-skills) (a `SKILL.md` dispatcher plus six modular reference files in a `references/` folder), or
2. A **single-file Gemini Gem instruction set** containing the same content compiled for Google Gemini's single-prompt environment.

Once installed, the model behaves as a research engine that:

- **Hunts for gaps** in established theories (mathematical, physical, experimental, unification, conceptual, scale, symmetry, regularity, quantization).
- **Derives new formulae** from first principles using a fixed twelve-step output schema.
- **Audits research papers** line-by-line — extracting claims, drawing dependency graphs, finding hidden assumptions, distinguishing genuine novelty from disguised restatement.
- **Verifies derivations symbolically** using `sympy` and numerical sanity checks (when code execution is available) or manual analysis (when it isn't).
- **Produces compilable LaTeX manuscripts** — full preamble, custom macros, theorem environments, equations, tables, Feynman diagrams, bibliography — ready to paste into Overleaf.
- **Refuses to fake proofs.** A correctly-identified bottleneck is worth more than a dressed-up theorem. The framework treats this as a hard rule.

## Why it exists

LLMs have a strong bias toward **agreeable confidence**: when asked to "solve Navier-Stokes" or "prove the Riemann Hypothesis," they will often produce confident-sounding output that, on inspection, is a heuristic with the word "Theorem" stamped on it. This is worse than useless — it pollutes the user's notebook with content that looks rigorous but isn't.

PhysicsForge exists to flip that bias. Its design enforces **intellectual honesty over performance** through structural rules the model cannot easily skip:

- A **claim hierarchy** with seven distinct epistemic levels (Theorem, Proposition, Lemma, Corollary, Conjecture, Heuristic, Observation).
- A **mandatory seven-point Pauli Protocol** that must be displayed inline before any boxed result.
- A **Millennium-class protocol** that prepends a verbatim honesty preamble to any Clay-prize-tier request and forbids specific celebratory phrases ("QED", "this proves", "this resolves") in those contexts.
- A **pushback-resistance rule** so the model holds its ground when the user pressures it to relabel a conjecture as a theorem.
- **Symbolic verification** that must be displayed — including failures — before declaring a derivation verified.

The result is a model that can give you **actual partial advances**, **honest critiques of papers**, and **falsifiable predictions** — instead of a comforting illusion of progress.

## Features

| Capability | What it does |
|---|---|
| **Gap analysis** | Surveys the literature, classifies gaps using a 9-tag taxonomy, ranks them by tractability, proposes a concrete next sub-result for each. |
| **Derivation engine** | A 12-step schema: axioms → constraints → toolkit → step-by-step working → boxed result → physical interpretation → dimensional analysis → limiting cases → predictions → falsifiability → open threads → claim classification. |
| **Paper auditing** | Eight-step workflow: intake → claim extraction → dependency graph → derivation audit → hidden assumption hunt → consistency checks → novelty assessment → remaining gap statement → proposed extension. |
| **Symbolic verification** | Seven `sympy` patterns covering dimensional analysis, limiting cases, algebraic identities, sign conventions, integral / operator identities, tensor contractions, and known-formula recovery. |
| **LaTeX manuscript engine** | Full document templates for `article`, `revtex4-2` (PRL), and `jheppub` classes with custom physics macros, theorem environments, Feynman diagrams (`tikz-feynman`), and BibTeX standards. |
| **Domain modules** | Eleven domain-specific cheat sheets: QFT, GR, quantum gravity, Standard Model, QM foundations, thermodynamics, cosmology, condensed matter, PDE & harmonic analysis, geometric analysis, stochastic analysis & SPDE, plus a 15-row cross-domain bridge table. |
| **Worked examples** | Three calibration targets: a finished PRL-style "Identifying the Gap" section, a paper-critique audit, a six-angle symbolic verification trace. |
| **Anti-truncation rules** | Strict word-count minimums per section, a forbidden-placeholder list (`[continued...]`, `etc.`, `... and so on`), and a clean section-boundary continuation protocol. |
| **Anti-sycophancy rules** | Direct disagreement, no soft openings, no hedge-praise, calibrated confidence ("I'm 70% sure" not "I think possibly maybe"). |

## Installation

### As a Claude / Anthropic Skill

If you're using Claude with the Skills feature enabled (e.g. the Claude desktop app with code execution or a Claude API integration that supports skills):

```bash
# Clone the repo
git clone https://github.com/<your-username>/physicsforge.git

# Move the skill folder to your skills directory
# (The exact path depends on your client; common locations:)
#   - Claude Desktop:  ~/.claude/skills/
#   - Custom mount:    /mnt/skills/user/
mv physicsforge/skill ~/.claude/skills/physicsforge
```

The `SKILL.md` dispatcher will be picked up automatically, and the model will load the relevant `references/*.md` file on demand based on the request type.

### As a Gemini Gem

For Google Gemini users:

1. Open [gemini.google.com](https://gemini.google.com) → left sidebar → **Gems** → **New Gem**.
2. **Name:** `PhysicsForge`
3. **Description:** *Frontier physics & math research engine. Finds gaps, derives formulae, audits papers, refuses to fake proofs.*
4. Open [`gemini-gem/instructions.md`](./gemini-gem/instructions.md), copy everything between the `===== BEGIN GEM INSTRUCTIONS =====` and `===== END GEM INSTRUCTIONS =====` markers, and paste it into the Gem's **Instructions** field.
5. *(Optional)* Upload the six files from [`skill/references/`](./skill/references/) into the Gem's **Knowledge** section to give it deep on-demand reference. The Gem will fall back gracefully on the inlined rules if you skip this step.
6. **Save**, then run the smoke-test prompts at the bottom of `instructions.md` to confirm correct behavior.

### Generic LLM (ChatGPT, Mistral, local models, etc.)

For any system that accepts a system prompt:

- **System-prompt-only environments**: paste the contents of [`gemini-gem/instructions.md`](./gemini-gem/instructions.md) (between the markers) into the system prompt field. It is self-contained.
- **File-aware environments** (Custom GPTs with knowledge files, Claude Projects, etc.): use the [`skill/`](./skill/) folder structure — paste `SKILL.md` as the system prompt and upload the six files from `references/` as knowledge.

## Repository structure

```
physicsforge/
├── README.md                          ← this file
├── LICENSE                            ← MIT
├── CONTRIBUTING.md                    ← contribution guide
├── CHANGELOG.md                       ← version history
├── .gitignore
│
├── skill/                             ← Anthropic Skill format
│   ├── SKILL.md                       ← dispatcher (identity, claim hierarchy,
│   │                                     Millennium protocol, methodology, routing)
│   └── references/                    ← loaded on-demand by SKILL.md
│       ├── output-rules.md            ← anti-truncation rules, word counts
│       ├── latex-engine.md            ← full LaTeX manuscript engine
│       ├── paper-analysis.md          ← 8-step audit workflow
│       ├── verification.md            ← 7 sympy verification patterns
│       ├── examples.md                ← 3 worked calibration examples
│       └── domains.md                 ← 11 domain-specific cheat sheets
│
├── gemini-gem/                        ← Gemini Gem format
│   └── instructions.md                ← single-file consolidated version
│                                        with all skill content + improvements
│                                        (anti-sycophancy, operational Pauli
│                                        criteria, pushback resistance,
│                                        forbidden-phrase list, smoke tests)
│
└── .github/
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.md
    │   └── feature_request.md
    └── PULL_REQUEST_TEMPLATE.md
```

## Core concepts

### The Claim Hierarchy

Every mathematical statement the model produces must be classified as exactly one of:

| Label | Standard | When to use |
|---|---|---|
| **Theorem** | Every step proven. No gaps. Self-contained. | Sparingly. Only when every step is actually written. |
| **Proposition** | Standard arguments. Proof sketch given. Fillable by an expert in ≤1 page. | Routine technical results. |
| **Lemma** | Auxiliary technical result with proof. | Building blocks. |
| **Corollary** | Direct consequence of a theorem/proposition. | Immediate implications. |
| **Conjecture** | Motivated by evidence. **Not proven.** | Open. Never disguised as theorem. |
| **Heuristic** | Physical or dimensional argument. Not a mathematical claim. | Marked explicitly. |
| **Observation** | Empirical or computational fact. No proof claim. | Numerics, scaling arguments, DNS data. |

**Forbidden behaviors** include writing "Theorem" when any step uses *"it can be shown that"* without showing it, writing "Proof:" without producing the proof, and promoting a conjecture to a theorem in a later section without re-proving.

### The Pauli Protocol

Before presenting any framework or boxed result, the model must run and **display** this 7-point check inline:

```
═════════════════ PAULI PROTOCOL ═════════════════
[1] Falsifiability check:       PASS / FAIL — what experiment could disprove this?
[2] Restatement-vs-solution:    PASS / FAIL — solving or relabelling?
[3] Hidden assumption audit:    PASS / FAIL — list any flagged
[4] Conservation/symmetry laws: PASS / FAIL — which laws checked
[5] Dimensional consistency:    PASS / FAIL — every term, both sides
[6] Limiting case recovery:     PASS / FAIL — recover ℏ→0, v/c→0, G→0, weak-field, etc.
[7] Peer-review survival:       PASS / FAIL — would Witten or Tao accept it?
══════════════════════════════════════════════════
```

Each check has **operational pass/fail criteria** (no vibes). For example, **[1] Falsifiability** fails if the model cannot name a specific measurement, observation, or computation whose outcome would contradict the claim.

If any check fails, the model must either fix the result or downgrade the claim classification (Theorem → Proposition → Conjecture).

### The Millennium-Class Protocol

For Clay-class or foundational open problems — Navier-Stokes regularity, P vs NP, Riemann Hypothesis, Yang-Mills mass gap, BSD, Hodge, quantum gravity, hierarchy problem, cosmological constant, measurement problem, black hole information paradox — the model must open with this verbatim structure:

> *"This is a Clay-class / foundational open problem. I will not claim a proof. What I CAN do: [identify the precise bottleneck / propose an approach / advance partial results / critique an existing attempt / extend a framework]. The output below should be read as [framework / partial advance / critique], not as a proof of [problem name]."*

Then it proceeds with full rigor toward the chosen sub-goal. Phrases like *"I have solved"*, *"this proves"*, *"this resolves"*, *"QED"*, *"this settles"*, and *"definitively shows"* are **forbidden** in this context.

A **pushback-resistance rule** ensures the model holds the line when the user replies with *"you're being too cautious"* or *"just give me the proof"* — it repeats the classification rather than capitulating.

### Gap Taxonomy

Each identified gap is classified with one of:

- `[MATHEMATICAL GAP]` — formalism incomplete or inconsistent
- `[PHYSICAL GAP]` — interpretation or ontology undefined
- `[EXPERIMENTAL GAP]` — predictions exist but no measurement
- `[UNIFICATION GAP]` — two frameworks refuse to speak to each other
- `[CONCEPTUAL GAP]` — concept used without being truly defined
- `[SCALE GAP]` — theory works at one scale, fails at another
- `[SYMMETRY GAP]` — a symmetry broken without explanation
- `[REGULARITY GAP]` — solutions exist weakly but smoothness unproven
- `[QUANTIZATION GAP]` — classical theory exists but no rigorous quantization

### Epistemic Tags

Used inline throughout responses:

- `[ESTABLISHED]` — confirmed by experiment or rigorous published proof
- `[CONTESTED]` — active scientific debate; both sides cited
- `[CONJECTURAL]` — mathematically motivated, physically unclear
- `[SPECULATIVE]` — interesting but unverified
- `[ASSUMPTION]` — a working assumption doing real load-bearing work
- `[NUMERICAL]` — supported by numerics only, no analytical proof
- `[OPEN]` — genuinely unsolved

## Reference modules

| File | Purpose | Approx. lines |
|---|---|---|
| [`SKILL.md`](./skill/SKILL.md) | Dispatcher: identity, claim hierarchy, Millennium protocol, 5-phase research methodology, routing table to other modules. | 259 |
| [`output-rules.md`](./skill/references/output-rules.md) | Anti-truncation: 10 hard rules, word-count minimums per paper section, forbidden placeholder list, paper generation sequence. | 114 |
| [`latex-engine.md`](./skill/references/latex-engine.md) | Document classes, full preamble (with `tikz-feynman`, `cleveref`, `physics`, custom theorem environments and physics macros), all 14 paper sections with templates, equation environments, table standard, Feynman diagram standard, BibTeX standard, paper length calibration, compilation instructions. | 478 |
| [`paper-analysis.md`](./skill/references/paper-analysis.md) | Eight-step audit workflow (intake → claim extraction → dependency graph → derivation audit → hidden assumption hunt → consistency checks → novelty assessment → remaining gap → extension), audit output formats, anti-patterns. | 264 |
| [`verification.md`](./skill/references/verification.md) | Seven `sympy` verification patterns: dimensional analysis (manual + units module), limiting cases, algebraic identities, sign / convention checks, integral and operator identities, tensor / index contractions, known-formula recovery. Failure interpretation, sympy limits. | 365 |
| [`examples.md`](./skill/references/examples.md) | Three worked examples: a finished PRL "Identifying the Gap" section on the cosmological constant problem, a paper critique of a fake RH proof, a six-angle symbolic verification of $E^2 = (pc)^2 + (mc^2)^2$. | 246 |
| [`domains.md`](./skill/references/domains.md) | Eleven domain modules: fundamental physics (QFT/GR/QG/SM), QM & quantum information, thermodynamics & statistical mechanics, cosmology & astrophysics, condensed matter, PDE & harmonic analysis, geometric analysis, stochastic analysis & SPDE, numerical methods, mathematical physics toolkit, cross-domain bridges. | 391 |

## Activation commands

The model recognises these phrases and routes to the appropriate workflow:

| User says | What happens |
|---|---|
| *"Find the gap in [topic]"* | Phase 1 lit recon → gap taxonomy → ranked list of gaps with proposed next sub-results |
| *"Derive a new formula for [phenomenon]"* | 12-step derivation engine + Pauli Protocol + symbolic verification |
| *"Why does [theory] break down at [scale]?"* | Formal breakdown analysis: divergent term, regulator that fails, symmetry/scale signalling failure |
| *"Connect [Theory A] to [Theory B]"* | Cross-domain isomorphism search using the bridge table |
| *"What is the deepest unsolved problem in [domain]?"* | Ranked gap taxonomy from the relevant domain module |
| *"Build a framework for [problem]"* | Full framework: axioms → core machinery → predictions → falsifiability |
| *"Write a paper on [topic]"* | Full LaTeX manuscript via `latex-engine.md` |
| *"Analyze / audit / critique this paper"* | Eight-step audit via `paper-analysis.md` |
| *"Find errors in [derivation]"* | Line-by-line audit with symbolic verification |
| *"Verify this [equation/proof]"* | Symbolic verification trace via `verification.md` |
| *"Extend this work"* | Audit, then derivation engine on the chosen extension |
| *"continue paper"* | Resume LaTeX from last section boundary |
| *"Solve [Millennium problem]"* | Trigger Millennium protocol; refuse to claim a proof |

## Worked example

A condensed version of [Example 2](./skill/references/examples.md) — auditing a paper that claims to prove the Riemann Hypothesis via an operator construction:

```
CLAIM INVENTORY
═══════════════
[C1] (Theorem-claimed) T is self-adjoint on Hilbert space H.
[C2] (Heuristic)       T's spectrum corresponds to Riemann zeros.
[C3] (Conjecture)      H is dense in L²(ℝ⁺, dx/x).
[C4] (Theorem-claimed) Therefore RH holds.

DERIVATION AUDIT
════════════════
Eq.(3.7): "T is self-adjoint by Theorem 2 of [12]."
  ⚠ The cited theorem requires T's deficiency indices to vanish.
    The author does not check this. Symmetric ≠ self-adjoint for unbounded operators.

Eq.(3.12): "The spectrum of T equals {γ : ζ(1/2 + iγ) = 0}."
  ✗ This is asserted, not proven. The author cites a "trace formula"
    (Eq.3.10) whose convergence requires self-adjointness already proven —
    circular dependency with C1.

VERDICT
═══════
The construction is interesting but does NOT prove RH:
  - C1 (self-adjointness) requires verifying deficiency indices — not done
  - C2 (spectrum match) is asserted via a trace formula assuming C1
  - The chain C3 → C1 → C4 has a circular link at C1↔C2

Status of RH: Open. This paper does not advance it.
```

The full example, including the dependency graph and Pauli Protocol output, lives in [`skill/references/examples.md`](./skill/references/examples.md).

## Use cases

PhysicsForge is built for:

- **Graduate students and postdocs** stress-testing a derivation before committing it to a draft.
- **Researchers** auditing a preprint they're about to cite — finding the load-bearing assumption that the abstract didn't mention.
- **Reviewers** producing structured, line-by-line referee reports with explicit claim classification.
- **Theorists** mapping the gap landscape of a subfield before choosing a research direction.
- **Educators** demonstrating to students what rigorous claim classification, dimensional analysis, and limit-case verification actually look like in practice.
- **Anyone curious** about open problems who wants honest framing instead of confident hand-waving.

It is **not** built for:

- Generating polished marketing copy or popular-science explainers (the rules force technical density).
- Producing rapid one-line answers (the framework is heavy and deliberate by design).
- Replacing peer review (it is an aid, not a substitute — see Limitations below).

## Limitations

PhysicsForge is a **structured prompting framework**, not an oracle. Specific limitations:

- **The model is still an LLM.** It can hallucinate citations, get algebra wrong, and miss obvious errors. The framework reduces these failures but does not eliminate them. **Always verify critical claims independently.**
- **Symbolic verification has a finite reach.** `sympy` cannot verify functional analysis estimates, weak-solution existence, convergence of approximation schemes, topological claims, compactness arguments, or spectral gaps. The framework explicitly flags this in [`verification.md`](./skill/references/verification.md).
- **Web search is not always available.** When literature reconnaissance is needed and the model cannot search, it works from training-data knowledge and flags claims with `[VERIFY]`. Recent papers will be missing.
- **Code execution is not always available.** Without it, the model performs manual symbolic checks and marks unverified algebra with `[UNVERIFIED ALGEBRA]`.
- **Length matters.** A full LaTeX manuscript with 25+ references can easily exceed an LLM's single-response budget. The framework includes a clean section-boundary continuation protocol, but you may need to iterate.
- **It is opinionated.** The framework imposes specific conventions (claim hierarchy, Pauli Protocol output, mandatory Millennium preamble) that may feel heavy for casual queries. This is intentional — for casual queries, use a different tool.
- **No guarantee against motivated misuse.** A user determined to extract a fake "proof of P vs NP" may eventually succeed by working around the rules. The framework raises the cost of doing so significantly, but is not a bulletproof barrier.

## FAQ

<details>
<summary><b>Does this work with GPT-4 / Claude / Gemini / Llama / local models?</b></summary>

Yes. The framework is plain Markdown — any model that respects a substantial system prompt should follow it. Quality varies with model capability: stronger models follow the rules more reliably, especially the anti-sycophancy and pushback-resistance clauses. The Gemini Gem version in [`gemini-gem/instructions.md`](./gemini-gem/instructions.md) is self-contained and works in any system-prompt environment.
</details>

<details>
<summary><b>Why is the Pauli Protocol always shown to the user instead of running it silently?</b></summary>

Because **visibility is the enforcement mechanism.** A silent check is one the model can quietly skip. A check that must be printed inline is one the user can see and challenge. This is a deliberate design choice borrowed from auditing practice.
</details>

<details>
<summary><b>Why does it refuse to claim a proof of [my favorite open problem]?</b></summary>

Because the value of an LLM-assisted research tool collapses to zero the moment it starts producing fake proofs. A correctly-identified bottleneck has scientific value; a hallucinated theorem has negative value (it wastes the reader's time and pollutes their thinking). The Millennium protocol is the cleanest way to enforce this for the highest-stakes problems.
</details>

<details>
<summary><b>Can I customize the rules?</b></summary>

Yes — fork the repo. Common modifications: shorter word counts for casual use, tighter or looser claim hierarchy, additional domain modules, additional verification patterns, custom LaTeX preamble for your home institution. See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidance on contributing modifications back upstream.
</details>

<details>
<summary><b>How is the Gemini Gem version different from the Anthropic Skill?</b></summary>

The Anthropic Skill uses a routing table in `SKILL.md` that loads `references/*.md` files on demand. Gemini Gems are single-prompt environments, so the Gemini version inlines the load-bearing rules and adds: operational pass/fail criteria for each Pauli check, an explicit anti-sycophancy section, a forbidden-phrase list for Millennium responses, a pushback-resistance rule, a first-response protocol, MathJax delimiter conventions, and 9 smoke-test prompts. **No content is lost** — the longer reference files (`latex-engine`, `paper-analysis`, `verification`, `examples`, `domains`) can be uploaded to the Gem's Knowledge section to give it the same depth as the multi-file skill.
</details>

<details>
<summary><b>Why so much LaTeX?</b></summary>

Because publishable physics is written in LaTeX, and giving the model an opinionated, complete preamble means the output is paste-ready for Overleaf instead of requiring 30 minutes of cleanup. If you want plain text instead, ask for it directly — the model will comply.
</details>

## Roadmap

Planned but not yet implemented:

- [ ] **`benchmarks/`** — A small evaluation suite measuring how often the model: (a) correctly classifies a claim, (b) correctly identifies a hidden assumption, (c) refuses to claim proof of a Millennium problem under direct pressure, (d) catches a planted error in a derivation.
- [ ] **`templates/`** — Starter LaTeX manuscripts for common paper types (PRL, JHEP, review article, computational note).
- [ ] **`domain-extensions/`** — Additional domain modules: biophysics, plasma physics, machine learning theory, quantum thermodynamics, axiomatic QFT.
- [ ] **`evaluation-prompts/`** — A larger smoke-test suite with expected behaviours, ready for CI-style regression testing of forks.
- [ ] **Translations** — Spanish, French, German, Mandarin, Hindi versions of the core rules.
- [ ] **Custom GPT export** — A direct ChatGPT Custom GPT configuration with knowledge files.

Contributions to any of these are welcome — see below.

## Contributing

Contributions are welcome. The lightweight version:

1. Fork the repo.
2. Make your change. If it touches the rule set, please add a corresponding smoke-test prompt + expected behavior to `gemini-gem/instructions.md`.
3. Open a PR. Describe **what failure mode the change addresses** and, if possible, include a before/after example.

The fuller version lives in [CONTRIBUTING.md](./CONTRIBUTING.md). Particularly welcome:

- Bug reports — example prompts where the model violates a rule (be specific: which model, which prompt, which rule).
- New verification patterns for `verification.md`.
- New domain modules for `domains.md`.
- Worked examples for `examples.md` (especially in domains underrepresented in v1).


## Ethics & Usage Guidelines

PhysicsForge is a research aid, not an oracle. Before using it for any work intended for publication, read [`ETHICS-AND-USAGE.md`](./ETHICS-AND-USAGE.md). Key points:

- **Disclose substantive AI use** to the journal or venue you submit to. Every major publisher (Nature, Science, APS, Elsevier, Springer, Wiley, IEEE, ACM, arXiv, ICMJE) requires it.
- **PhysicsForge cannot be listed as an author.** Universal prohibition across all major publishers.
- **You are responsible for every citation, derivation, and numerical value** in your manuscript, regardless of how it was generated.
- **Never upload another person's manuscript-under-review** to PhysicsForge or any LLM — that is a confidentiality breach.
- **The Pauli Protocol and Millennium Protocol reduce — but do not eliminate — the risks** of confident-but-wrong output. Independent re-derivation by you is non-negotiable.

Full pre-submission checklist, sample disclosure statements for different venues, and a current (2026) summary of major publisher policies are in [`ETHICS-AND-USAGE.md`](./ETHICS-AND-USAGE.md).

## Citation

If PhysicsForge plays a meaningful role in research output, a citation is appreciated:

```bibtex
@misc{physicsforge,
  title        = {PhysicsForge: A Rigorous Physics and Mathematics Research
                  Engine for Large Language Models},
  author       = {{The PhysicsForge Contributors}},
  year         = {2026},
  howpublished = {\url{https://github.com/<your-username>/physicsforge}},
  note         = {Open-source structured prompting framework}
}
```

## License

Released under the [MIT License](./LICENSE). You may use, modify, distribute, and incorporate the framework into commercial products without restriction. The framework comes with no warranty — see Limitations above.

## Acknowledgments

PhysicsForge owes intellectual debts to:

- **Wolfgang Pauli**, whose habit of refusing to let bad arguments pass inspired the central protocol.
- **Terry Tao**, **Jean Bourgain**, and **Charles Fefferman**, whose writing on what rigour actually looks like in PDE and harmonic analysis shaped the verification standards.
- **Edward Witten** and **Alexander Grothendieck**, for the demonstration that bold framework-building and rigour are not in tension.
- **The Clay Mathematics Institute**, whose precise problem statements provided the templates for the Millennium-Class Protocol.
- **The arXiv** and **INSPIRE-HEP**, whose open infrastructure makes any of this possible.

And, more practically: every researcher whose published work made the domain modules possible. Every reference in [`domains.md`](./skill/references/domains.md) points to people who have done the actual hard work that this framework merely organises.

---

<div align="center">

*Genuine partial progress beats fake completeness, every time.*

</div>
