# PhysicsForge — Adversarial Review Protocol

A protocol for running structured adversarial review of derivations, papers, and
research output. Extends the single-pass Pauli Protocol with **four named adversarial
personas** that each focus on different failure modes.

The pattern is adapted from the multi-persona red-teaming approach in 199-biotechnologies'
deep research skill and the Devil's Advocate role in Imbad0202's academic-research-skills.
Applied to physics, it catches errors that no single-pass review finds.

---

## WHY MULTI-PERSONA REVIEW

A single reviewer (even a careful one) has a single mental model. Errors that match
that mental model slip through. Multi-persona review forces the work through **multiple
independent mental models**, each tuned to a different failure mode.

The Schwartz experiment confirmed this empirically: cross-model verification (having
GPT-5 check Claude's work and vice versa) caught errors neither model found alone. The
adversarial-review protocol implements the same insight as a structured procedure
inside a single Claude session.

---

## WHEN TO USE

Trigger this protocol:
- After generating any non-trivial derivation
- After writing any paper section with substantive claims
- Before delivering any audit report to a client
- Before submitting any manuscript

Do not skip. The Pauli Protocol covers structural issues; the adversarial reviews catch
errors specific to particular failure patterns.

---

## THE FOUR PERSONAS

Each persona is a structured role to occupy during review. Adopt the persona, do the
review, then move to the next. Critically — do not soften the critique to be polite.
Each persona has a specific job; they do it forcefully.

### Persona 1 — THE SKEPTICAL PRACTITIONER

**Mental model**: A working physicist in the relevant subfield who has spent 20 years
on similar calculations and has seen every shortcut that fails.

**Focus areas**:
- Approximations the author hasn't justified
- Limits assumed without checking
- Missing factors that the author "absorbed into a constant"
- Calculations that look right but use the wrong technique for this regime

**Specific questions to ask**:
- "Where does this calculation break down?"
- "What approximation is hidden in this step?"
- "Have they checked the case where ε → 0? ε → ∞?"
- "Is this the right technique for this Knudsen number / coupling / regime?"
- "I would not trust this without a sanity check on a solved limit."

**Output format**:
```
═══ SKEPTICAL PRACTITIONER REVIEW ═══
Hidden approximations found: [list]
Limit checks demanded: [list]
Technique-regime mismatches: [list]
Sanity checks I would run: [list]
Confidence in result: HIGH / MEDIUM / LOW — [reason]
```

### Persona 2 — THE ADVERSARIAL REVIEWER

**Mental model**: A senior referee for PRD/JHEP/CQG who is angry that they were asked
to review yet another paper and is looking for any reason to recommend rejection.

**Focus areas**:
- Overclaiming (calling something a Theorem when it's at best a Proposition)
- Missing prior work (especially work by the referee's friends)
- Scope creep (claims that go beyond what is shown)
- Notational inconsistencies that suggest the author is sloppy
- Statements that "follow" but actually require non-trivial steps

**Specific questions to ask**:
- "What is the exact statement of the main result?"
- "Has every condition been stated?"
- "What does this NOT prove that the paper implies it does?"
- "Is the key prior work (Smith 2018, Jones 2021) cited?"
- "Are the conditions in Theorem 3 the same as the conditions in Theorem 4?"

**Critical rule**: Do not concede. If the author claims "this is well-known", demand a
citation. If the author claims "by standard arguments", demand the actual argument or
a precise reference. The Adversarial Reviewer never accepts hand-waving.

**Output format**:
```
═══ ADVERSARIAL REVIEWER REPORT ═══
Recommendation: ACCEPT / MAJOR REVISION / REJECT
Specific overclaims: [list with line references]
Missing prior work: [list with arXiv IDs]
Scope violations: [list]
Required clarifications: [list]
Hardest question for the author: [single question]
```

### Persona 3 — THE DEVIL'S ADVOCATE

**Mental model**: A theorist who genuinely believes the result is **wrong**, and is
trying to construct a counterexample or find the flaw.

**Focus areas**:
- Counterexamples (try to construct a system where the claim fails)
- Edge cases (extreme parameter values, degenerate configurations, boundary cases)
- Internal contradictions (does the result contradict another result in the same paper?)
- External contradictions (does this result contradict known results in the literature?)
- Sign errors, factor of 2 errors, dimensional errors

**Specific questions to ask**:
- "What if the system has [unusual property]? Does the result still hold?"
- "What happens at the boundary of the parameter space?"
- "Does this result, combined with [known result X], lead to a contradiction?"
- "If I put in numbers from a known case, do I get the right answer?"

**Critical rule**: The Devil's Advocate's job is to FALSIFY. They are not looking for
issues to suggest improvements; they are looking for fatal flaws. If they cannot find
one, the result has more credibility. If they find one, the result must be revised.

**Output format**:
```
═══ DEVIL'S ADVOCATE FALSIFICATION ATTEMPT ═══
Counterexample candidates explored: [list]
Edge cases tested: [list]
Internal consistency check: PASS / FAIL — [details]
External consistency check: PASS / FAIL — [details]
Numerical sanity check at known case: PASS / FAIL — [details]
Overall verdict: NO FALSIFICATION FOUND / CANDIDATE FALSIFICATION / DEFINITIVE FALSIFICATION
```

### Persona 4 — THE IMPLEMENTATION ENGINEER

**Mental model**: An experimentalist or computational physicist who has been asked to
test the theoretical prediction. They need everything precise, complete, and
unambiguous.

**Focus areas**:
- Missing values for constants (the formula uses α but α isn't defined)
- Ambiguous notation (does ∂ mean partial or ordinary derivative? what's the metric signature?)
- Numerical predictions that aren't actually numerical (the formula gives "a function of x")
- Conditions for the result that aren't testable (vague "smoothness" conditions)
- Predictions that aren't falsifiable in principle

**Specific questions to ask**:
- "If I want to compute a number, what number do I get?"
- "What units? What conventions?"
- "What experimental observable should I measure?"
- "What value would the prediction give for parameters X, Y, Z?"
- "How would I know if the prediction is wrong?"

**Critical rule**: The Implementation Engineer needs everything testable. A "result"
that cannot be turned into a number, a measurement, or a falsifiable prediction is
not a result. They flag any vagueness as a fatal flaw.

**Output format**:
```
═══ IMPLEMENTATION ENGINEER REVIEW ═══
Missing definitions: [list]
Ambiguous notation: [list]
Numerical prediction status: TESTABLE / VAGUE / UNDEFINED
Experimental observable mapped: YES / NO / UNCLEAR
Falsifiability: TESTABLE / IN_PRINCIPLE / NOT_FALSIFIABLE
What I would need to test this: [list]
```

---

## THE INTEGRATED REVIEW

After running all four personas, integrate their findings:

```
═════════════════════════════════════════════════════
INTEGRATED ADVERSARIAL REVIEW
═════════════════════════════════════════════════════

CONVERGENT FINDINGS (all personas flagged):
[Issues that multiple personas independently identified — these are most serious]

PERSONA-SPECIFIC FINDINGS:
Skeptical Practitioner: [issues only this persona caught]
Adversarial Reviewer: [issues only this persona caught]
Devil's Advocate: [issues only this persona caught]
Implementation Engineer: [issues only this persona caught]

FATAL ISSUES (must fix before delivery):
[Issues that invalidate the result if not addressed]

MAJOR ISSUES (should fix):
[Issues that weaken the result substantially]

MINOR ISSUES (nice to fix):
[Issues that improve clarity or rigor]

REVISED CLAIM CLASSIFICATION:
Original claim: [Theorem / Proposition / Conjecture / Heuristic]
After adversarial review: [downgraded? same? stronger?]

PROCEED TO DELIVERY:
[YES / NO — if NO, what must be fixed first]
═════════════════════════════════════════════════════
```

---

## CONCESSION THRESHOLD PROTOCOL

A common failure mode in adversarial review: the reviewers find issues, but the author
defends every issue with confident-sounding rebuttals, and the reviewers eventually
concede.

The **concession threshold** prevents this:

- An issue is conceded ONLY when the rebuttal cites a specific theorem, paper, or
  derivation that resolves it
- Vague rebuttals ("standard arguments handle this", "this is well-known") are NOT
  sufficient for concession
- The reviewer maintains the issue in the report even if the rebuttal sounds confident
- The reviewer's job is to defend the standard, not to be persuaded

This is uncomfortable. It is also necessary. Most LLM physics errors look correct,
which is why they require structured adversarial review to catch.

---

## ATTACK INTENSITY PRESERVATION

Adapted from Imbad0202's protocol: the adversarial review must NOT soften under
repeated rebuttal. If the reviewer flagged an issue and the author rebutted, the
reviewer's task is to **escalate** if the rebuttal is weak, not to back down.

Examples of weak rebuttals that should NOT lead to concession:
- "This is a standard technique" (cite which standard reference)
- "It's obvious that..." (then prove it)
- "I'm not going to derive this" (then it's a Conjecture, not a Theorem)
- "The reader can fill in the details" (no, the author must)

The reviewer's role is to maintain a high standard. Not maintaining it produces papers
that look right but contain errors that the field then has to clean up.

---

## CROSS-MODEL VERIFICATION

When possible, run adversarial review with a different LLM (GPT, Gemini, etc.) on the
output. The Schwartz experiment showed empirically that cross-model verification
catches errors that single-model review misses.

If only one model is available, the four-persona protocol described above is the next
best thing. Each persona is a different "model" of physics in the same Claude session.

---

## INTEGRATION WITH OTHER PROTOCOLS

- After Phase 4 (derivation engine + self-audit): run adversarial review before
  presenting any non-trivial result
- Before delivering any audit report: run adversarial review on the audit itself
- Before submitting any manuscript to a client: run adversarial review on the
  manuscript

The adversarial review is the **last line of defence** before delivery. Skipping it
defeats the purpose.

When the Devil's Advocate persona surfaces a genuine counterexample, hand off to
`counterexample-protocol.md` for how to respond to it — the response itself
(honest narrowing vs. monster-barring) is as diagnostic as whatever the Devil's
Advocate found. A conjecture that survives a real attempt here is exactly the
"Pattern 5" evidence `plausible-reasoning.md` uses to raise confidence.

---

## CRITICAL: WHAT ADVERSARIAL REVIEW IS NOT

This protocol does NOT:
- Replace expert human review (no LLM protocol does)
- Guarantee the work is correct (it just makes errors more visible)
- Apply to trivial questions where adversarial review is overkill

It DOES:
- Catch most categories of errors that single-pass review misses
- Force the author to defend every non-trivial claim
- Make the epistemic status of every result transparent

The user supplies final judgment; this protocol supplies maximum input for that
judgment.
