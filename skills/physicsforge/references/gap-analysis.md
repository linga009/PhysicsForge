# PhysicsForge — 8-Phase Systematic Gap Analysis

A high-fidelity protocol for identifying and classifying gaps in a research area. This
replaces the single-phase gap taxonomy from prior versions of the skill.

The protocol is **sequential**: each phase informs the next. Phase 1 establishes what is
proven. Phase 2 surveys analogues. Phase 3 audits mathematical completeness. Phases 4–7
identify specific gap types. Phase 8 ranks them by tractability.

Each phase produces structured output that can be combined into a comprehensive gap
analysis suitable for guiding new research.

---

## WHEN TO USE THIS PROTOCOL

Trigger this protocol whenever the user asks:
- "Find the gap in [topic]"
- "What's missing in our understanding of [phenomenon]?"
- "What would be a good thesis topic in [area]?"
- "What are the open problems in [field]?"
- "Where could a new contribution be made in [topic]?"

Apply it before recommending a research direction. Do not skip phases.

---

## PHASE 1 — FOUNDATION MAPPING

**Goal**: Distinguish what is rigorously proven from what is widely assumed.

**Operation**:
1. Search literature for foundational papers in the area
2. For each foundational result, classify epistemic status:
   - `[THEOREM]` — complete proof, generally accepted
   - `[PROPOSITION]` — standard-argument proof, no controversy
   - `[CONJECTURE]` — widely believed, unproven
   - `[FOLKLORE]` — assumed by everyone, no clean proof in the literature
   - `[ASSUMPTION]` — used as input, not derived
   - `[CONTESTED]` — different authors disagree

**Output format**:
```
FOUNDATIONAL STRUCTURE OF [TOPIC]

THEOREMS:
[Theorem 1 statement]
  Reference: [arXiv ID + paper title]
  What it establishes: [...]
  Conditions required: [...]

PROPOSITIONS:
[Proposition 1 statement]
  Reference: [...]
  Standard proof technique: [...]

CONJECTURES:
[Conjecture 1 statement]
  Origin: [paper that first stated it]
  Evidence in favor: [...]
  Evidence against: [...]
  Status: ACTIVE / DORMANT / UNDER ATTACK

FOLKLORE / ASSUMPTIONS:
[Statement that is used everywhere but lacks clean proof]
  Where it appears: [...]
  Why it's believed: [...]
  Has anyone questioned it? [...]

CONTESTED CLAIMS:
[Statement] — Author A says X, Author B says Y
  Source of disagreement: [different framework / different definitions / direct contradiction]
  Resolution status: [...]
```

**Why this phase matters**: Most "gap analyses" treat the foundation as solid and look
only at frontier questions. The richest gaps are often in the foundation itself —
assumptions everyone makes but no one has proven.

---

## PHASE 2 — ANALOGUE SURVEY

**Goal**: Identify problems that have been solved in analogous systems but not yet
applied here. These are often the most tractable gaps.

**Operation**:
1. Search for the same mathematical structure in different physical contexts
2. Search for the same physical question in different mathematical formalisms
3. Identify cross-disciplinary tools that haven't been imported

**Output format**:
```
ANALOGOUS SYSTEMS

For each analogue:
SYSTEM: [name and brief description]
  Solved result: [what is known there]
  Mathematical mapping: [how it maps to our problem — be explicit]
  Predicted outcome here: [what the analogy would suggest]
  Where the analogy breaks: [specific differences]
  Tractability of applying it: NEAR / MEDIUM / FAR

UNUSED FORMALISMS

For each formalism not yet applied:
FORMALISM: [name]
  What it could address: [specific question]
  Obstacle to applying it: [what makes the application non-trivial]
  Closest existing attempt: [if any]
  Cross-disciplinary import potential: [how to adapt it]
```

**Specific analogue categories to check**:
- Condensed matter analogues for HEP problems (and vice versa)
- Cosmological scale-up of laboratory results (and scale-down)
- Mathematical analogues (e.g., topology of solution spaces, dynamical systems)
- Information-theoretic restatements of physical questions
- Numerical analogues (lattice gauge theory, etc.)

---

## PHASE 3 — MATHEMATICAL COMPLETENESS AUDIT

**Goal**: Identify where the formalism breaks down or relies on unjustified steps.

**Operation**: For each major equation or framework in the area, check:

```
EXISTENCE GAPS
  - What objects are claimed to exist but not proven to?
  - What integrals are written but not shown to converge?
  - What limits are taken without justification?

UNIQUENESS GAPS  
  - What objects are shown to exist but not proven unique?
  - What "the solution" claims should be "a solution"?

CONVERGENCE GAPS
  - What series are summed without convergence proof?
  - What asymptotic expansions are used beyond their radius?
  - What perturbative results are used non-perturbatively without justification?

REGULARIZATION GAPS
  - What divergences are handled by procedure (renormalization, dim reg, etc.)
    without UV completion?
  - What boundary terms vanish "by appropriate choice"?
  - What contour deformations are claimed without justification?

OPERATOR ORDERING / QUANTIZATION GAPS
  - What classical expressions are turned into quantum operators ambiguously?
  - What ordering choices are made implicitly?

DOMAIN OF VALIDITY GAPS
  - What equations are used outside their proven regime?
  - What linear approximations are extended to large fluctuations?
```

**Output format**:
```
MATHEMATICAL COMPLETENESS REPORT FOR [TOPIC]

[GAP TYPE]: [Specific issue]
  Where it appears: [paper + equation reference]
  What is missing: [precise mathematical content]
  Why this matters: [physical or mathematical consequence]
  Closest progress: [partial results, if any]
  Status: OPEN / PARTIAL / RESOLVED-IN-SPECIAL-CASE
```

---

## PHASE 4 — EXPERIMENTAL STATUS

**Goal**: Map theoretical predictions to experimental verification status.

**Operation**: For each major prediction in the field, determine:

| Status | Meaning |
|---|---|
| MEASURED ✓ | Confirmed at stated precision |
| BOUNDED ○ | Constraints exist, prediction within bounds |
| TENSION △ | Prediction in mild conflict with measurement |
| EXCLUDED ✗ | Measurement rules out the prediction |
| PLANNED □ | Future experiment will test |
| UNEXPLORED ◇ | No measurement attempted |

**Output format**:
```
PREDICTION ↔ MEASUREMENT MAP FOR [TOPIC]

[Prediction 1]: [exact statement]
  Theoretical reference: [arXiv ID]
  Measurement status: [MEASURED/BOUNDED/TENSION/EXCLUDED/PLANNED/UNEXPLORED]
  If measured: precision = [X], reference = [...]
  If tension: nature of disagreement = [...]
  If unexplored: experimental requirements = [...]
  
TENSION POINTS:
[Predictions where theory and experiment disagree]
For each: physical interpretations under consideration

DISCRIMINATING MEASUREMENTS:
[The single measurement that would most constrain the theory space]
  Required precision: [...]
  Existing experimental capability: [...]
  Timeline: [years to feasibility]
```

---

## PHASE 5 — CROSS-DISCIPLINARY TOOLS

**Goal**: Identify methodologies from other fields that have not been applied here.

**Mathematical tools to check**:
- Algebraic geometry (motivic / derived)
- Differential / spectral geometry beyond standard usage
- Category theory and higher categories
- Random matrix theory
- Topological data analysis
- Operator algebras / non-commutative geometry
- Stochastic / rough path methods
- Information theory and entropy methods

**Physics methodologies to check**:
- Effective field theory beyond textbook applications
- Renormalization group beyond traditional usage
- Holographic / dual descriptions
- Quantum information methods (entanglement entropy, complexity)
- Numerical methods (lattice, tensor networks, neural quantum states)
- ML/AI methods adapted for theory

**Output format**:
```
UNUSED TOOLS FOR [TOPIC]

[Tool name]:
  Could address: [specific question]
  Application elsewhere: [where it has worked]
  Obstacle here: [what's hard about applying]
  First step toward application: [concrete starting point]
  Tractability: NEAR / MEDIUM / FAR
  Estimated time investment: [PhD scale / postdoc scale / multi-year program]
```

---

## PHASE 6 — CITATION DESERT MAP

**Goal**: Identify subtopics that were active but went quiet — these often contain
the most tractable gaps.

**Operation**:
1. Look at temporal patterns of publication in the area
2. Identify subtopics with peak activity 5–20 years ago that have since gone quiet
3. For each: diagnose why activity stopped

**Diagnoses**:
- `SOLVED` ✓ — problem actually got solved (verify the resolution)
- `WALL` ○ — research hit a technical wall
- `SUPERSEDED` △ — different approach took over
- `UNFASHIONABLE` □ — funding/community shifted
- `PREMATURE` ◇ — required tools didn't exist; might now

**Output format**:
```
CITATION DESERT MAP FOR [TOPIC]

[Subtopic name]
  Peak period: [years]
  Current activity: [low/none]
  Diagnosis: [SOLVED/WALL/SUPERSEDED/UNFASHIONABLE/PREMATURE]
  
  If SOLVED: verify resolution with current knowledge
  If WALL: what was the wall? Have new tools emerged?
  If SUPERSEDED: was the original approach actually wrong, or just inconvenient?
  If UNFASHIONABLE: are there results worth revisiting?
  If PREMATURE: what tools now exist that didn't then?
  
  Revisit value: HIGH / MEDIUM / LOW
  Best entry-point paper: [arXiv ID + reason]

OLD PAPERS WITH UNFOLLOWED IDEAS:
[Pre-2015 papers with novel ideas that received few citations and were never developed]
For each: original idea, why it stalled, why it might be ripe now
```

---

## PHASE 7 — CONTRADICTION REGISTRY

**Goal**: Document conflicting results in the literature. Resolving these is often the
most direct path to genuine new contribution.

**Operation**: Search specifically for contradictions and disagreements.

**Contradiction types**:
- `DIRECT_CONTRADICTION` — Paper A claims X, Paper B claims ¬X with same setup
- `DEFINITIONAL` — Authors use the same word for different things
- `DIFFERENT_ASSUMPTIONS` — Apparent contradiction dissolves if assumptions stated
- `COMPUTATIONAL_ERROR` — One paper has a documented mistake
- `REGIME_DEPENDENT` — Both correct in different regimes
- `UNRESOLVED` — Active debate, no consensus

**Output format**:
```
CONTRADICTION REGISTRY FOR [TOPIC]

[Contradiction 1]:
  Paper A (arXiv:XXXX): claims [X]
  Paper B (arXiv:YYYY): claims [Y]
  
  Type: DIRECT/DEFINITIONAL/ASSUMPTION/ERROR/REGIME/UNRESOLVED
  
  If DIRECT: which has stronger evidence?
  If DEFINITIONAL: state both definitions, identify which is standard
  If ASSUMPTION: list the differing assumption explicitly
  If ERROR: cite the correction (or note that it's uncorrected)
  If REGIME: state the boundary
  If UNRESOLVED: outline what would resolve it
  
  Resolution status: RESOLVED / DEBATED / UNACKNOWLEDGED
  Importance: would resolving this change predictions in the field?

QUIETLY ABANDONED RESULTS:
[Claims in old papers that nobody cites anymore but were never retracted]
For each: what the claim was, why people stopped citing it, is the original work actually wrong?
```

**Why phase 7 matters**: Unacknowledged contradictions are research opportunities.
Acknowledged debates are often well-traveled. The hidden contradictions — claims that
contradict each other but appear in different subcommunities that don't read each other —
are the richest territory.

---

## PHASE 8 — TRACTABILITY RANKING

**Goal**: Synthesize phases 1–7 into a ranked actionable research agenda.

**Operation**: For each gap identified in phases 1–7, score on three axes:

```
IMPACT:
  HIGH:    solving this would change predictions across the field
  MEDIUM:  solving this would advance a specific subarea significantly  
  LOW:     solving this resolves a technical issue but doesn't change much

TRACTABILITY:
  NEAR:    tools exist; needs careful application (1–3 yr)
  MEDIUM:  tools mostly exist; needs adaptation (3–7 yr)
  FAR:     requires new mathematical/experimental tools (>10 yr)

CROWD:
  EMPTY:   few or no groups working on this
  SPARSE:  a few groups; you could matter
  CROWDED: many strong groups; competitive
```

**Best research targets are HIGH impact + NEAR/MEDIUM tractability + EMPTY/SPARSE crowd.**

**Output format**:
```
RANKED RESEARCH AGENDA FOR [TOPIC]

#1 [Highest priority gap]
  Source phase: [which phase identified this]
  Specific question: [exact, answerable question]
  Impact: HIGH/MEDIUM/LOW — [why]
  Tractability: NEAR/MEDIUM/FAR — [what tools exist]
  Crowd: EMPTY/SPARSE/CROWDED
  Score: [composite]
  
  First concrete step a researcher could take this year:
  [Specific action — derive X, compute Y, search for Z in data]
  
  What "partial progress" looks like:
  [Intermediate milestone that would constitute meaningful advance]
  
  Best journal home: [PRL/JHEP/CQG/PRD/etc.]
  Best-positioned groups: [if known]

#2 [Next priority]
  ...

[Continue for top 5–7 gaps]

SUMMARY TABLE:
| # | Gap | Type | Impact | Tractability | Crowd | First step |
|---|-----|------|--------|--------------|-------|------------|
| 1 | ... | ...  | HIGH   | NEAR         | EMPTY | ...        |
```

---

## OUTPUT INTEGRATION

After running all 8 phases, integrate them into a final research brief:

```
═══════════════════════════════════════════════════════════
SYSTEMATIC GAP ANALYSIS BRIEF: [TOPIC]
═══════════════════════════════════════════════════════════

EXECUTIVE SUMMARY:
[3 sentences: state of the field, top 3 gaps, recommended direction]

FOUNDATION (Phase 1):
[1 paragraph synthesizing the proven/conjectured/assumed structure]

ANALOGUES NOT YET APPLIED (Phase 2):
[1 paragraph: most promising cross-system applications]

MATHEMATICAL GAPS (Phase 3):
[List of completeness issues with severity]

EXPERIMENTAL OPPORTUNITIES (Phase 4):
[Top discriminating measurements]

CROSS-DISCIPLINARY OPPORTUNITIES (Phase 5):
[Top unused tools]

CITATION DESERTS (Phase 6):
[Most promising abandoned subtopics]

CONTRADICTIONS (Phase 7):
[Most consequential unresolved disagreements]

RANKED AGENDA (Phase 8):
[Top 5 gaps with first steps]

CLAIM CLASSIFICATION:
- Foundation status: based on [phase 1 sources]
- Gap identification: [systematic, but not exhaustive]
- Tractability estimates: [HEURISTIC — based on tools currently available]
- Recommendations: [based on rank ordering of impact × tractability]
═══════════════════════════════════════════════════════════
```

---

## CRITICAL: WHAT GAP ANALYSIS IS NOT

Gap analysis is **not** a list of "things people don't know yet." Lots of things are
unknown but uninteresting or intractable. Useful gap analysis identifies questions that
are:

1. **Specific** — phrased so that "is it answered?" has a definite yes/no
2. **Tractable** — addressable with current or imminent tools
3. **Important** — would matter if answered
4. **Sourced** — traced to specific literature, not invented

Resist the temptation to manufacture impressive-sounding "open problems" that lack
these properties. A short list of real, sourced, tractable gaps is more valuable than
a long list of vague ones.
