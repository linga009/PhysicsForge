# PhysicsForge — ScholarEval Framework (Physics Edition)

A quantitative, retrieval-augmented evaluation framework for physics papers, drafts,
research ideas, and audit deliverables. Adapted from ScholarEval (arXiv:2510.16234)
and the K-Dense AI scholar-evaluation skill, specialised for theoretical and
mathematical physics.

This complements the qualitative Pauli Protocol (`paper-analysis.md`) with numerical
scoring across eight dimensions. Use it whenever a structured, defensible numerical
assessment is needed — for client-facing audits, pre-submission reviews, or comparing
multiple drafts.

---

## TWO-AXIS FOUNDATION

ScholarEval rests on two literature-grounded criteria, both required:

### Soundness
Are the claims, methods, and derivations valid given existing literature?
- Is the mathematical apparatus correctly applied?
- Do the limiting cases recover known results?
- Are the assumptions consistent with what the cited works actually show?
- Does the derivation contain hidden steps or unjustified moves?

### Contribution
What does this advance beyond the existing literature?
- Is the result new, or does it restate existing work in different notation?
- If it extends prior results, what is the precise scope of the extension?
- Does it open new questions or close known ones?
- Is the claimed novelty justified relative to the works cited?

A paper can be sound but trivial (high soundness, low contribution) or bold but wrong
(high contribution claim, low soundness). Both axes are reported separately in the
final score.

---

## EIGHT EVALUATION DIMENSIONS

Each dimension is scored 1–5 with explicit rubrics. The overall score is the average,
with both axes (soundness, contribution) reported separately.

### Dimension 1 — Problem Formulation
Is the research question clearly stated, well-scoped, and physically meaningful?

| Score | Rubric |
|---|---|
| 5 | Question is precise, falsifiable, and addresses a known gap with explicit scope |
| 4 | Question is clear and meaningful but scope could be sharper |
| 3 | Question is identifiable but vague in places; scope unclear |
| 2 | Question implicit or buried; reader must reconstruct it |
| 1 | No clear research question; paper is descriptive without focus |

Physics-specific check: does the question identify an observable, an inequality, a
proof obligation, or a unification target? Vague questions ("understand X better")
score 2 or below.

### Dimension 2 — Literature Engagement
Has the relevant prior work been identified, cited, and engaged with substantively?

| Score | Rubric |
|---|---|
| 5 | All relevant work cited; explicit comparison with most-related results; engages with contesting views |
| 4 | Relevant work cited; comparison present but incomplete |
| 3 | Major works cited; comparison shallow; some adjacent work missing |
| 2 | Spotty citations; missing important prior work; superficial engagement |
| 1 | Reinvents existing wheels without acknowledging them |

Physics-specific check: arXiv search for related work in the last 5 years. Score
drops by 1 for every "obvious must-cite paper" that is missing.

### Dimension 3 — Mathematical Setup
Are axioms, definitions, and the formal framework stated explicitly?

| Score | Rubric |
|---|---|
| 5 | All axioms explicit; notation consistent; no hidden assumptions |
| 4 | Setup mostly explicit; minor notation drift; one or two implicit assumptions |
| 3 | Setup adequate but some assumptions buried; reader must infer |
| 2 | Significant unstated assumptions; notation inconsistent |
| 1 | Mathematical framework unclear; can't tell what is being assumed |

Physics-specific check: are sign conventions stated? Are units stated? Is the choice
of representation explicit? Most physics papers lose points here on hidden assumptions
about regularity of solutions or boundary conditions.

### Dimension 4 — Derivation Rigor
Does each step follow from the previous one with sufficient justification?

| Score | Rubric |
|---|---|
| 5 | Every non-trivial step justified; claim hierarchy honored throughout |
| 4 | Most steps justified; minor gaps acknowledged or fillable by expert |
| 3 | Major arc clear but key steps black-boxed; "it can be shown" appears |
| 2 | Several steps unjustified; conjecture treated as theorem in places |
| 1 | Derivation is gestural; key results asserted not derived |

Physics-specific check: apply the Pauli Protocol (`anti-fabrication.md`) to the
keystone derivation. Each FAIL drops the score by 1.

### Dimension 5 — Verification
Are limiting cases, dimensional analysis, conservation laws, and numerics consistent?

| Score | Rubric |
|---|---|
| 5 | All limits checked; dimensions verified throughout; numerics included |
| 4 | Major limits checked; dimensional analysis present; numerics partial |
| 3 | Some verification present but incomplete |
| 2 | Verification minimal; obvious limits not checked |
| 1 | No verification; reader must check everything from scratch |

Physics-specific check: does the result reproduce at least two known limits? Does
dimensional analysis hold throughout? Are numerical values within expected ranges?

### Dimension 6 — Physical Interpretation
Does the paper explain what the results mean physically?

| Score | Rubric |
|---|---|
| 5 | Every key result has clear physical interpretation; intuition built |
| 4 | Most results interpreted; some technical points unexplained |
| 3 | Mathematical results presented; physical meaning sparse |
| 2 | Math without physics; reader can't see the picture |
| 1 | Physical content unclear or absent |

Physics-specific check: can the reader explain the result in one sentence to a
colleague? If not, the score is at most 3.

### Dimension 7 — Writing Quality
Is the paper clear, well-structured, and readable?

| Score | Rubric |
|---|---|
| 5 | Excellent structure, prose, and transitions; reads like a finished paper |
| 4 | Good structure; minor prose issues; could be slightly tighter |
| 3 | Adequate but rough; sections could be reordered or rewritten |
| 2 | Structure unclear; prose obscures content; significant editing needed |
| 1 | Hard to follow; major restructuring required |

Physics-specific check: are equations introduced before they are referenced? Is
notation defined at first use? Is the abstract a faithful summary of the paper?

### Dimension 8 — Citation Verification
Are all citations real, accurate, and appropriately used?

| Score | Rubric |
|---|---|
| 5 | All citations verified, appropriate; quotations accurate; no missing must-cites |
| 4 | All citations verified; minor placement issues |
| 3 | Citations mostly verified; one or two wrong attributions or weak supports |
| 2 | Multiple unverified citations; some misattributions |
| 1 | Fabricated or fundamentally wrong citations present |

Physics-specific check: run Citation Guard (`citation-guard.md`) before scoring. Any
FAIL on Citation Guard caps this dimension at 1.

---

## OVERALL ASSESSMENT THRESHOLDS

After scoring all eight dimensions, compute the average and apply the threshold:

| Average | Verdict | Action |
|---|---|---|
| **4.5+** | Exceptional / Top-tier | Submit to flagship journal (PRL, Nature) |
| **4.0–4.4** | Strong / Minor revisions | Submit to standard journal after polish |
| **3.5–3.9** | Good / Major revisions | Substantial work needed before submission |
| **3.0–3.4** | Acceptable / Significant revisions | Re-derive or re-frame portions |
| **<3.0** | Major rework | Do not submit; restart from problem formulation |

Both axes (soundness, contribution) must be ≥3.0 for submission readiness — a paper
that is sound but trivial (contribution <3.0) or bold but wrong (soundness <3.0)
should not be submitted regardless of the average.

---

## OUTPUT FORMAT

```
═══════════════════════════════════════════════════
SCHOLAREVAL — PHYSICS EDITION
═══════════════════════════════════════════════════

PAPER: [title, authors, version]
REVIEWER: PhysicsForge / [reviewer name]
DATE: [date]

─── DIMENSION SCORES ───
1. Problem Formulation:    [score]/5  — [one-line justification]
2. Literature Engagement:  [score]/5  — [...]
3. Mathematical Setup:     [score]/5  — [...]
4. Derivation Rigor:       [score]/5  — [...]
5. Verification:           [score]/5  — [...]
6. Physical Interpretation:[score]/5  — [...]
7. Writing Quality:        [score]/5  — [...]
8. Citation Verification:  [score]/5  — [...]

─── AXIS SCORES ───
Soundness:    [average of 3,4,5,8] = [score]/5
Contribution: [average of 1,2,6]   = [score]/5

─── OVERALL ───
Average:  [score]/5
Verdict:  [EXCEPTIONAL / STRONG / GOOD / ACCEPTABLE / REWORK]
Action:   [recommendation]

─── KEY STRENGTHS (top 3) ───
1. [...]
2. [...]
3. [...]

─── KEY WEAKNESSES (top 3, with severity) ───
1. [FATAL/MAJOR/MINOR]: [...]
2. [...]
3. [...]

─── REQUIRED ACTIONS BEFORE SUBMISSION ───
1. [specific action with location in paper]
2. [...]

─── OPTIONAL IMPROVEMENTS ───
1. [...]
2. [...]

─── EVIDENCE ───
[For each substantive scoring decision, cite the specific section/equation/claim]
═══════════════════════════════════════════════════
```

---

## WHEN TO USE SCHOLAREVAL

Trigger this evaluation:

- **Pre-submission**: Before submitting any manuscript to a journal
- **Client audit**: For Forge Physics Review Tier 3+ deliverables (Pre-Submission Audit)
- **Self-evaluation**: After completing a draft, before the next iteration
- **Comparison**: When choosing between multiple drafts of the same paper
- **Triage**: When a reviewer assignment is large and papers must be ranked

Do NOT use ScholarEval for:
- Initial brainstorming (too early; nothing to score yet)
- Section-level audits (use Pauli Protocol instead — see `paper-analysis.md`)
- Citation-only checks (use Citation Guard instead)
- Methodological gap-finding (use 8-phase gap analysis instead)

---

## INTEGRATION WITH OTHER PROTOCOLS

ScholarEval is the **delivery scorecard**. It runs after the qualitative protocols:

0. **Breakthrough red-flag scan** — if applicable, run first to calibrate scrutiny
   (`breakthrough-red-flags.md`); this is a prior, not a ninth dimension
1. **Deep search** — gather literature context (`deep-search.md`)
2. **Paper analysis** — qualitative Pauli Protocol (`paper-analysis.md`)
3. **Citation Guard** — verify all references (`citation-guard.md`)
4. **Adversarial review** — adversarial second pass (`adversarial-review.md`)
5. **ScholarEval** — quantitative scoring summary (this document)

If, during scoring, the author's response to a raised objection looks like
monster-barring (redefining terms to dodge a valid counterexample rather than
engaging with it — see `counterexample-protocol.md`), that is itself evidence
for a lower Dimension 4 (Derivation Rigor) score.

The output of ScholarEval is a single-page numerical report that synthesises the
qualitative findings of steps 2–4 into actionable scores. For Forge Physics Review
clients, this is the document that anchors the audit deliverable.

---

## CALIBRATION AGAINST KNOWN PAPERS

A useful practice: periodically score known top-tier and known-flawed papers to
calibrate the rubric.

Known top-tier physics papers should score ≥4.5:
- Maldacena's AdS/CFT (1997): would score 5,5,5,5,5,5,5,5
- 't Hooft & Veltman renormalization (1972): 5,5,5,5,4,4,5,5
- Bell's inequality (1964): 5,5,5,5,5,5,5,5

Known-flawed papers (that should fail review):
- Cold fusion (Fleischmann-Pons 1989): low Verification, low Mathematical Setup
- Various retracted papers: trace the failure to specific dimensions

If your scoring is consistently above or below these calibration points, recalibrate
the rubric for your usage.

---

## CRITICAL: WHAT SCHOLAREVAL IS NOT

ScholarEval is NOT:
- A substitute for domain expertise. The reviewer must understand the physics.
- A substitute for the Pauli Protocol. Quantitative scoring complements qualitative
  audit, doesn't replace it.
- A guarantee. A score of 4.5 doesn't mean the paper is correct; it means the
  reviewer (with this framework) thinks it's strong.

ScholarEval IS:
- A defensible numerical record. Clients of Forge Physics Review get a number with
  a justification, not a vague "looks good" or "needs work".
- A consistency tool. Different reviewers using the same framework should arrive at
  similar scores for the same paper.
- A communication aid. The 8 dimensions help authors understand exactly what to
  improve and where.

---

## REFERENCE

ScholarEval framework: Eskelinen et al., "ScholarEval: Research Idea Evaluation
Grounded in Literature" (arXiv:2510.16234, 2025).

K-Dense AI implementation: github.com/K-Dense-AI/claude-scientific-writer
(scholar-evaluation skill).

This adaptation specialised for theoretical and mathematical physics by PhysicsForge
v2.1 (May 2026).
