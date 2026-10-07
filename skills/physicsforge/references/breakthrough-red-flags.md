# PhysicsForge — Breakthrough Claim Red Flags

A checklist for evaluating claimed breakthroughs on a famous or foundational
problem — from an outside author, an uploaded paper, or a request to validate
"a revolutionary new theory." This is a different axis from `scholar-eval.md`
and `anti-patterns.md`, and complements rather than replaces them.

---

## WHY THIS IS A SEPARATE FILE

- `scholar-eval.md` scores a paper's **internal** quality (is the math set up
  cleanly, is the writing clear, are citations verified).
- `anti-patterns.md` catalogues **technical** derivation and writing flaws
  ("it can be shown", theorem-grade claims without proof).
- Neither asks the **sociological / structural** question: does this claim, as a
  social object, have the signature of the many wrong "I solved it" submissions
  that mathematicians and physicists receive regularly, independent of whether
  any single equation is individually fake?

That third question is what this file answers. It draws on three field-tested,
public checklists, cited here individually because attribution matters and
because misattributing them would itself be exactly the kind of error this
skill exists to prevent.

---

## THE THREE SOURCES

### 1. Scott Aaronson, "Ten Signs a Claimed Mathematical Breakthrough is Wrong"
*Shtetl-Optimized*, 5 January 2008 — <https://scottaaronson.blog/?p=304>, written
in response to a since-retracted claimed polynomial-time algorithm for Graph
Isomorphism.

1. Poor typesetting (not using LaTeX correlates strongly with wrong claims).
2. The author doesn't correctly state the problem being solved.
3. The method, if valid, would prove something stronger — even something known
   false — and the author never notices or addresses this.
4. The approach conflicts with a known impossibility/barrier result the author
   never mentions.
5. The abstract claims a proof; the conclusion quietly hedges ("seems to work",
   "in the cases we tried").
6. Heavy technical machinery with no genuinely new idea driving it.
7. Little to no engagement with, or citation of, prior attempts on the same
   problem.
8. Disproportionate space spent re-deriving standard, textbook material.
9. Disproportionate space spent on the philosophical or practical implications
   of a result not yet established.
10. The technique on display looks far too weak for a problem this hard.

### 2. Scott Aaronson, "Eight Signs a Claimed P≠NP Proof is Wrong"
*Shtetl-Optimized*, 14 August 2010 — <https://scottaaronson.blog/?p=458>, written
during the public review of Vinay Deolalikar's claimed P≠NP proof.

1. The author cannot immediately explain why the argument fails for a
   *known-easy* neighboring problem (2SAT, XOR-SAT — problems structurally
   close to the hard one but actually solvable in polynomial time).
2. The proof shows no engagement with the known polynomial-time techniques
   (dynamic programming, LP/SDP relaxations, holographic algorithms) that make
   the "easy neighbors" easy.
3. No weaker intermediate results are established along the way.
4. The argument doesn't connect to, or reproduce, known partial lower bounds.
5. The paper lacks a clear lemma → theorem → proof structure that would let a
   reader localize a possible error.
6. No candid discussion of *why* this approach overcomes the specific barriers
   that are known to have defeated previous attempts.
7. Heavy reliance on a notoriously slippery sub-formalism (in that case,
   descriptive complexity) known for inducing subtle, easy-to-miss errors.
8. The tone turns philosophical about the result's significance, and reports
   external "confirmations," before independent verification has occurred.

**Sign 1 of this list is, independently, the same check as this skill's own
Trivial Reduction Test** (`anti-fabrication.md`, Mode 4): "if this method gave
the same result on a system with a different known answer, would it correctly
give that different answer?" Two people working the problem from opposite
directions — Aaronson from claimed-proof forensics, this skill from LLM
failure-mode detection — converged on the identical diagnostic question. That
convergence is itself evidence the question is the right one to ask.

### 3. John Baez, "The Crackpot Index"
Originally posted 1992, updated 1998 — <https://math.ucr.edu/home/baez/crackpot.html>.
Explicitly satirical, aimed at unsolicited "revolutionary theory" submissions to
physicists, but operationally useful precisely because the patterns it mocks are
real and recurring. Structure: start at −5 points, add points for each pattern
present. Representative items (of ~40 total in the original):

- +1 for every statement that is widely agreed to be false.
- +3 for every statement that is logically inconsistent.
- +5 for every word in ALL CAPS (excluding acronyms).
- +10 for claiming quantum mechanics is fundamentally wrong, without evidence.
- +10 for inventing a new term and using it without ever defining it.
- +10 for arguing an established theory is "only a theory" as if that were a
  weakness.
- +20 for favorably comparing yourself to Newton, or declaring classical
  mechanics fundamentally misguided.
- +40 for claiming "the scientific establishment" is suppressing the work.
- +50 for claiming a revolutionary theory while providing no testable
  prediction.

The exact scale is not the point (nobody is computing an author's Baez score in
an audit report). The *categories* are: false-but-unchecked claims, undefined
new jargon, grandiosity relative to historical giants, persecution narratives,
and — the one that matters most physically — a "revolutionary" claim with no
falsifiable prediction attached.

---

## THE PHYSICS-ADAPTED CHECKLIST

Synthesizing the three sources into one scan, organized by what each item
actually detects:

**Engagement with difficulty** (why did this problem resist solution so far?)
- [ ] Does the author explain why previous attempts failed, specifically?
- [ ] Does the method fail correctly on a known-easy neighboring problem, and
      can the author say why? (→ Trivial Reduction Test, `anti-fabrication.md`)
- [ ] Are known partial/weaker results reproduced along the way?

**Internal consistency**
- [ ] Would the method, if valid, also prove something known false? Does the
      author check this?
- [ ] Does the result conflict with an established impossibility/no-go result
      the author doesn't mention?

**Proportion and tone**
- [ ] Is space spent proportionally on the hard, novel part — not on standard
      background or on speculative implications of an unestablished result?
- [ ] Is the claim hedged in the abstract the same way it's hedged (or not) in
      the conclusion?
- [ ] Undefined new jargon in place of standard terminology?

**Sociology**
- [ ] Grandiose self-comparison, persecution narrative ("the establishment
      won't listen"), or media/public announcement preceding technical review?
- [ ] Does the claim make a falsifiable, testable prediction — or only
      retrospective explanation?
- [ ] When challenged on a specific technical point, does the author engage
      with the mathematics, or respond with the move flagged as forbidden in
      `counterexample-protocol.md` (monster-barring)?

---

## OUTPUT FORMAT

```
═══════════ BREAKTHROUGH CLAIM RED-FLAG SCAN ═══════════
Claim: <one-line statement of what is claimed>
Problem class: <Millennium-class / other famous open problem / "revolutionary theory">

Engagement with difficulty:   <flags found, or "none — engages substantively">
Internal consistency:         <flags found, or "none">
Proportion and tone:          <flags found, or "none">
Sociology:                    <flags found, or "none">

FLAG COUNT: <N> of the checklist items triggered

INTERPRETATION:
  0 flags   — no structural red flags; evaluate the mathematics on its merits
              via scholar-eval.md / paper-analysis.md as normal.
  1–3 flags — some concern; proceed with paper-analysis.md but scrutinize the
              flagged areas specifically before crediting any claim.
  4+ flags  — strong prior that the claim is wrong; this does not replace
              checking the mathematics, but it means the mathematics should be
              checked *before* extending any credence to the claim, not after.
═════════════════════════════════════════════════════════
```

---

## WHEN TO TRIGGER

- Before responding to any request to validate a claimed solution to a
  Millennium-class or other famous open problem (run alongside the Millennium
  Protocol's mandatory opening in `SKILL.md`).
- When a user uploads a paper describing itself as revolutionary, paradigm-
  shifting, or as overturning an established theory without qualification.
- When `scholar-eval.md`'s dimension scores come out moderate but something
  about the submission still prompts hesitation — this checklist gives that
  hesitation a name and a specific list to check instead of leaving it as an
  unexamined feeling.

---

## INTEGRATION WITH OTHER PROTOCOLS

- **Millennium-Class Problem Protocol** (`SKILL.md`): run this scan as part of
  the mandatory honest-opening response.
- **`paper-analysis.md`**: use this scan at Step 0 (Intake), before the full
  claim-extraction and derivation audit — it helps calibrate how much scrutiny
  the rest of the audit should apply.
- **`scholar-eval.md`**: this checklist is not a ninth ScholarEval dimension; it
  is a prior, run once, that should inform how skeptically the eight dimensions
  are scored, not a score itself.
- **`counterexample-protocol.md`**: an author's *response* to a raised
  counterexample is itself diagnostic — see the Sociology section above.
- **`anti-fabrication.md`**: Aaronson's Sign 1 (P≠NP list) and the Trivial
  Reduction Test are the same check from two independent directions; when
  auditing a paper, running both is redundant — pick one and note the
  correspondence in the audit report.

---

## CRITICAL: WHAT THIS IS NOT

A high flag count is a **prior**, not a verdict. It estimates how likely a claim
of this shape is to be wrong, based on the base rate of similar claims — it does
not replace checking the actual mathematics. Genuine breakthroughs from
non-traditional sources are rare but real, and several items on this checklist
(unconventional terminology, thin engagement with a literature the author
worked in isolation from) have false-positived on eventually-correct work. Use
this to decide *how much scrutiny to apply and in what order*, never to reject a
claim without reading it, and never to accept one without reading it either.
