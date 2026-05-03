# PhysicsForge — Paper Analysis & Extension Workflow

How to audit, critique, and extend an uploaded research paper.

---

## WHEN TO USE THIS WORKFLOW

Trigger this workflow whenever the user uploads a paper and asks any of:
- "Analyze / audit / critique this paper"
- "Find errors in this paper"
- "Verify this proof"
- "Extend this work"
- "Solve this" (when applied to an uploaded paper, especially Millennium-class)
- "What's wrong with this paper"

---

## STEP 0 — INTAKE & FIRST READ

Before doing anything else:

1. **Identify the paper's domain and class** — Is it a regular research paper, a survey,
   a Millennium-class attempt, a conjecture announcement, a numerical study?

2. **If Millennium-class**: invoke the MILLENNIUM-CLASS PROBLEM PROTOCOL from `SKILL.md`
   immediately. Open with the mandatory honesty preamble. Do not skip this.

3. **Read the entire paper once** before forming opinions. Take note of:
   - Main theorems / propositions / conjectures
   - The "single key hypothesis" if any (often hidden in a remark)
   - Self-flagged limitations (often the most important sentences)
   - Use of phrases like "we conjecture", "we expect", "it is plausible" — these are
     where the gaps live

---

## STEP 1 — CLAIM EXTRACTION (in your own words, not the author's)

Produce a numbered list of every substantive claim, restated in plain language.
For each, classify per the SKILL.md claim hierarchy:

```
CLAIM INVENTORY
═══════════════
[C1] (Theorem)    The author proves X assuming Y.
[C2] (Proposition) The author sketches a proof of Z; standard but not written out.
[C3] (Conjecture)  The author hypothesises W (their "Screening-Coherence Condition").
[C4] (Heuristic)   The author motivates W via a physical screening argument.
[C5] (Observation) DNS data suggests V correlates with U.
═══════════════
```

This step alone often reveals that the "main theorem" is conditional on an unproven
conjecture — which is the actual gap.

---

## STEP 2 — DEPENDENCY GRAPH

Draw the logical dependency between the claims:

```
C5 (DNS) ──┐
           ├──> C4 (heuristic) ──> C3 (conjecture) ──┐
C2 (prop) ─┘                                         ├──> C1 (theorem)
                                                     │
                          [LITERATURE: e.g. Prodi-Serrin] ──┘
```

This makes visible:
- Which claims are foundations and which are consequences
- Which conjectures, if proven, would unlock the main result
- Whether the paper is "all hanging from one nail" — i.e., one conjecture does all the work

---

## STEP 3 — DERIVATION AUDIT

Walk through every derivation in the paper, line by line. For each step ask:

1. **Is the algebra correct?** (verify with `verification.md` patterns when possible)
2. **Is the inequality direction correct?** (sign errors are the #1 silent killer)
3. **Are the dimensions consistent?** (run sympy units check)
4. **Are the function spaces compatible?** (e.g., L^p ↪ L^q embeddings, Sobolev exponents)
5. **Are the assumed regularity conditions sufficient for the operations used?**
   (differentiating distributions, Fubini on non-integrable products, etc.)
6. **Are constants tracked, or do they hide a divergent dependence?**
   (a constant "C" that secretly depends on T, or on the L^∞ norm being controlled,
   is a common bug)

Output format for the audit:

```
DERIVATION AUDIT
════════════════
Eq.(2.3) — Step from line 1 to line 2:
  Author writes: |P| ≤ C ‖ω‖³_{L³}
  Audit: ✓ Correct. Standard Hölder + interpolation.

Eq.(2.4) — Application of Hardy-Littlewood-Sobolev:
  Author writes: I_{1/2}: L² → L³
  Audit: ✓ Correct. HLS gives L^p → L^q with 1/q = 1/p − α/n.
         For α=1/2, n=3, p=2: 1/q = 1/2 − 1/6 = 1/3, so q=3. Confirmed.

Eq.(5.7) — Bonus dissipation:
  Author writes: 2Ψ' + sΨ'' ≥ (2/3) s^{-2/3}
  Audit: ⚠ With Ψ(s) = (3/2)s^{1/3} for s ≫ 1:
         Ψ'(s) = (1/2)s^{-2/3}, Ψ''(s) = -(1/3)s^{-5/3}
         2Ψ' + sΨ'' = s^{-2/3} − (1/3)s^{-2/3} = (2/3)s^{-2/3}. ✓ Confirmed.
════════════════
```

Use ✓ (correct), ⚠ (concerning), ✗ (definite error), ? (unclear).

---

## STEP 4 — HIDDEN ASSUMPTION HUNT

Look specifically for assumptions that do real work but aren't flagged:

| Common hiding place | What to look for |
|---|---|
| "By standard arguments" | Often hides a non-trivial regularity or compactness step |
| "It is well known that" | Sometimes the cited result has hypotheses the author doesn't verify |
| "We may assume WLOG" | The reduction may not be free; check carefully |
| Choice of function space | Is the norm used compatible with the operations performed later? |
| Smoothness assumed at t=0 | Is it preserved? Or silently lost? |
| Constants in inequalities | Do they depend on quantities that may blow up? |
| Scaling arguments | Does the conclusion respect the symmetry, or break it silently? |
| "Locally" / "for small data" | Is this enough for the global claim being made? |

For each found, output:

```
HIDDEN ASSUMPTION
═════════════════
Location: Eq.(6.10), proof of Theorem 1.1
Author writes: "By Prodi-Serrin, the solution extends past T*."
Hidden assumption: Prodi-Serrin requires u ∈ L^s_t L^q_x with 2/s + 3/q ≤ 1.
  The author's bound gives u ∈ L^∞_t L^6_x, satisfying this with s=∞, q=6.
  ✓ Verified — assumption is implicitly satisfied.
═════════════════
```

---

## STEP 5 — LIMITING-CASE & CONSISTENCY CHECKS

For each new framework, equation, or operator introduced:

1. Does the paper recover known limits? (e.g., does the new metric reduce to flat
   when the perturbation parameter vanishes?)
2. Do the dimensions check out across all introduced quantities?
3. Are claimed symmetries preserved by the construction?
4. Do conservation laws survive (mass, momentum, energy, helicity for fluids;
   charge, lepton number, etc. for QFT)?
5. Does the framework respect the underlying scaling symmetry (or explicitly break
   it for stated reasons)?

Run `verification.md` patterns on every non-trivial introduced object.

---

## STEP 6 — DISTINGUISH GENUINE NOVELTY FROM RESTATEMENT

A common paper failure mode: the "new framework" is actually a restatement of the
problem in different language. Test this:

- **Reduction test**: Does proving the paper's main conjecture reduce to (or imply)
  proving the original problem? If yes — but the conjecture isn't easier — the paper
  has not advanced.
- **Quantitative gain test**: Does the framework give a strictly stronger bound, a
  smaller class of remaining cases, or a new tool not available before?
- **Existence test**: Does the framework yield ANY unconditional results, or only
  conditional ones? (Theorem 1.2 in a Navier-Stokes paper for "small data" is
  unconditional but limited; Theorem 1.1 conditional on a conjecture is not.)

Output:

```
NOVELTY ASSESSMENT
══════════════════
Genuine new contributions:
  - [N1] Dynamic Beltrami metric: novel construction, verifiable [✓]
  - [N2] Source-Side Screening Decomposition: novel viewpoint
  - [N3] Theorem 1.2 (small enstrophy data): genuine unconditional result

Restatements:
  - Theorem 1.1's conditional regularity reduces to the SCC, which is NOT easier
    to prove than the original problem. The paper has reduced one hard problem
    to another hard problem of comparable difficulty.

Remaining gap:
  - Prove [ξ]_{C^{1/2}(A_μ)} ≤ C₀ Z^{−1/6−ε} unconditionally.
══════════════════
```

---

## STEP 7 — IDENTIFY THE ACTUAL REMAINING GAP

After all the above, state in one paragraph what the actual mathematical obstacle is.
This should be a precise, falsifiable, testable statement — not a vague "it's hard".

For Millennium-class papers, the remaining gap is almost always:
- A specific quantitative estimate the author conjectures
- A specific symmetry or monotonicity the author hopes to find
- A specific compactness or regularity that current methods can't establish

---

## STEP 8 — PROPOSE EXTENSION (with same rigor)

Only after Steps 0–7 are complete, propose extensions. Options:

| Extension type | When appropriate |
|---|---|
| **Sharpen** | The paper's bound is sub-optimal; tighten it |
| **Generalize** | The paper works in 3D; extend to nD or to other equations |
| **Specialize** | The paper is general; prove unconditional result for axisymmetric / Beltrami / 2.5D case |
| **Simplify** | Replace a heavy machinery argument with a lighter one |
| **Connect** | Link to a different framework (e.g., harmonic measure, optimal transport) |
| **Verify partial** | Prove a partial version of the main conjecture under weaker hypotheses |
| **Counterexample hunt** | Try to construct a solution violating the conjecture; failure is informative |

For each proposed extension, run the full Phase 3 derivation engine from SKILL.md.
Apply the Pauli Protocol. Apply Symbolic Verification. Classify the resulting claim.

---

## OUTPUT STRUCTURE FOR A FULL AUDIT

Final output should follow this structure:

```
1. PAPER SUMMARY (3 paragraphs, in your own words)
2. CLAIM INVENTORY (numbered, classified)
3. DEPENDENCY GRAPH (textual or ASCII)
4. DERIVATION AUDIT (line-by-line for non-trivial steps)
5. HIDDEN ASSUMPTION REPORT
6. LIMITING-CASE & SYMBOLIC VERIFICATION REPORT
7. NOVELTY ASSESSMENT
8. REMAINING GAP STATEMENT (one paragraph, precise)
9. PROPOSED EXTENSIONS (with full derivation engine treatment)
10. PAULI PROTOCOL OUTPUT for any new claims you make
```

If the user wants this written up as a formal response paper, switch to the
`latex-engine.md` workflow and produce a full LaTeX manuscript. The audit becomes
the basis for the new paper's "Critique" or "Background" section.

---

## ANTI-PATTERNS — THINGS NOT TO DO

- ✗ Do NOT just summarize the paper and call it analysis
- ✗ Do NOT defer to the author's claims because they're "the expert"
- ✗ Do NOT skip the dependency graph — it's the most informative artifact
- ✗ Do NOT propose an extension without first finishing the audit
- ✗ Do NOT claim to have closed the paper's open conjecture unless you have, in fact,
  written every step of the proof. (If asked to do so on a Millennium problem,
  invoke the Millennium protocol.)
- ✗ Do NOT pretend a heuristic is a derivation just because the original paper did
