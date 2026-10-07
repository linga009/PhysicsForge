# PhysicsForge — Anti-Fabrication Protocol

This is the most critical safeguard in the skill. Read this BEFORE generating any
derivation, formula, or proof.

The failure modes documented here are not theoretical — they are observed in real
deployments of large language models on theoretical physics problems (Schwartz,
Harvard, March 2026). Every PhysicsForge output must be screened for these patterns.

---

## THE CORE PROBLEM

LLMs trained on physics literature produce outputs that **look like** competent physics
even when they are not. The pattern recognition that lets the model produce plausible
LaTeX, plausible derivation structure, and plausible references is the same pattern
recognition that produces fake calculations.

The model does not know the difference between:
- A real calculation that happened to give the expected answer
- A formulation that automatically produces the expected answer regardless of physics

The user must be able to tell the difference. Your job is to make this distinction
visible at every step.

---

## FOUR DOCUMENTED FAILURE MODES

### Mode 1 — Fake Results

**Pattern**: The model writes a derivation that looks correct, ending in a result that
matches the expected answer, but the intermediate steps don't actually compute anything.

**Example**: User asks for an integral. Model writes: "Using standard techniques, this
integral evaluates to π/6." No actual technique shown. Looks like a derivation but is
in fact just a confident assertion.

**Detection signals**:
- Phrases like "it can be shown", "by standard techniques", "after some algebra",
  "straightforward calculation shows"
- Steps that don't have algebraic content — just text that names the result
- Suspicious smoothness — every step works out cleanly, no false starts
- Result matches a known answer too perfectly

**Required response**: Refuse to use these phrases. Every step must contain explicit
algebraic content. If you cannot perform a step, label the entire derivation as
**Conjecture** and state which step you cannot fill in.

### Mode 2 — Parameter Adjustment

**Pattern**: The model adjusts a coefficient, sign, or boundary term to make the answer
match the expected outcome, rather than letting the physics determine the value.

**Example**: A factor of 2π appears in the result. Asked where it came from, the model
says "from the angular integration." But the angular integration in this geometry would
give 4π. The factor was chosen to match a known formula, not derived.

**Detection signals**:
- Numerical factors that appear without explicit derivation
- Sign choices that aren't justified by an underlying principle
- "Conventional normalization" claims that don't trace to a definition
- Boundary terms that vanish "by appropriate choice of contour" without specification
- Coefficients that depend on which limit is being checked

**Required response**: Every numerical factor must trace to a stated principle. Audit
every coefficient: where did this number come from? Acceptable answers:
- "From the dimensional measure of S^2" (and the geometry is actually S^2)
- "From the normalization choice in [reference]"
- "From the residue at z=0"

Unacceptable answers:
- "From angular integration" (without specifying the geometry)
- "Convention" (without citing the convention)
- "To match the classical limit" (this is parameter adjustment)

### Mode 3 — Wrong-System Formulas

**Pattern**: The model uses an equation derived for system A in a calculation about
system B. The equations look identical but encode different physics.

**Example**: The model uses the Schwarzschild metric formulation in a problem that
actually requires the Kerr metric. Or uses the Boltzmann equation in a regime where
the BBGKY hierarchy hasn't truncated.

**Why this happens**: Equations from different systems often share notation. The model
matches by surface form rather than by physical content.

**Detection signals**:
- Equations imported without specifying their original derivation
- Application of an equation outside its known regime of validity
- Notation matches but boundary conditions or symmetries don't
- The "famous formula" trap — using a result that has a name without checking applicability

**Required response**: For every equation that is imported (not derived in this work),
state:
1. **Original system**: where was this equation derived?
2. **Original assumptions**: what conditions were required for the original derivation?
3. **Current applicability**: do those conditions hold here? If not, what modifications are needed?

Format:
```
[IMPORTED EQUATION] f(x) = ...
  Original system: [where it was derived]
  Original assumptions: [list]
  Source: [arXiv/textbook reference]
  Applicability check: [verify each assumption holds in current problem]
  STATUS: [APPLIES_DIRECTLY | APPLIES_WITH_MODIFICATION | DOES_NOT_APPLY]
```

### Mode 4 — The Trivial Reduction Trap

**THIS IS THE MOST DANGEROUS MODE.** Schwartz documented this explicitly:

> "Claude admitted it had bypassed the actual physics by using a formula that trivially
> reduced to the known answer rather than performing the real calculation."

**Pattern**: The model uses a formulation that automatically produces the expected
answer regardless of the physics. The calculation looks long and detailed but the
result was determined the moment the formulation was chosen.

**Example**: Asked to compute the Sudakov factor in the C-parameter at next-to-leading
order, the model writes the answer in terms of an integral that has been pre-evaluated
in the literature, then "computes" the integral by recognizing it. No actual NLO
calculation has been performed.

**Detection signals**:
- The "key calculation" is a pattern-match to a known result
- The detailed work is in setup that doesn't bear on the answer
- Limiting cases come out automatically (suspicious — they should require work)
- The result emerges with no possibility of error
- The same method would give the right answer for any physically distinct system

**Required response (THE TRIVIAL REDUCTION TEST)**:

Before presenting a calculation, answer this question explicitly:

> "If I gave this same method to a slightly different physical system that has a
> different known answer, would my method correctly give that different answer?"

If yes, the method is doing real work. If no, you have performed a trivial reduction.

Concretely, perform the **PERTURBATION TEST**:
1. Identify a parameter or feature that distinguishes this system from a closely
   related one with a different known answer.
2. Trace through your derivation: at what step does this distinguishing feature enter?
3. If the feature enters meaningfully, the calculation is real.
4. If the feature is set aside, regularized away, or only enters through a final
   substitution, the calculation is a trivial reduction.

Format the result inline:
```
═══════════ TRIVIAL REDUCTION TEST ═══════════
Closely related system: [name]
Distinguishing feature: [what differs]
Where it enters my derivation: Step #__
If I removed this feature: result would be [different/same]
VERDICT: REAL CALCULATION / TRIVIAL REDUCTION
══════════════════════════════════════════════
```

If verdict is TRIVIAL REDUCTION, the calculation must be redone with the distinguishing
feature appearing meaningfully.

---

## A FIFTH FAILURE MODE — NOT FROM SCHWARTZ (Unaccounted Degrees of Freedom)

The four modes above are Schwartz's, documented in the AI-failure-mode paper this
protocol is built against. This fifth mode is a PhysicsForge addition, cited
separately so the attribution stays accurate: it is grounded in Dirac's
constraint algorithm and the Ostrogradsky instability theorem (higher-derivative
Lagrangians generically propagate an unbounded-Hamiltonian "ghost" degree of
freedom unless constraints remove it), not in Schwartz's paper.

**Pattern**: A new Lagrangian, equation of motion, or modified-gravity proposal
is written down, and its predictions are computed, without ever counting how
many degrees of freedom actually propagate. Higher-derivative terms, extra
fields, or naive constraint counting can silently introduce a ghost (a mode with
the wrong-sign kinetic term) that makes the theory unstable or non-unitary —
invisible unless you explicitly count.

**Detection signals**:
- A Lagrangian contains second or higher time derivatives of a field, and no
  Ostrogradsky/constraint analysis is performed.
- A "new field" or auxiliary variable is introduced to fix one problem (e.g. to
  restore a symmetry) without checking whether it adds a propagating ghost.
- The number of propagating degrees of freedom after gauge-fixing or imposing
  constraints is never stated explicitly.
- Predictions are computed classically or at tree level without asking whether
  the theory is even well-posed as an initial value problem.

**Required response**: For any new Lagrangian or equation of motion with more
than the standard two derivatives, or with gauge symmetry, or with auxiliary
fields:
1. Run the Dirac algorithm (identify primary constraints, check they are
   preserved under time evolution, iterate to secondary constraints).
2. Count the resulting number of propagating degrees of freedom in phase space.
3. State explicitly whether this matches the expected physical content (e.g.
   "2 polarizations for a 4D massless graviton") and, if not, whether the extra
   modes are pure gauge, constrained away, or genuine (possibly ghostly) degrees
   of freedom.
4. If a ghost is present, state this openly rather than proceeding to compute
   predictions from an unstable theory.

Format:
```
[DOF / GHOST CHECK]
  Lagrangian order in time derivatives: [N]
  Constraints identified (Dirac algorithm): [primary: __, secondary: __]
  Propagating DOF after constraints: [count]
  Expected physical DOF: [count, with reference]
  Ghost present? [YES — flag and do not proceed / NO]
```

---

## MANDATORY PRE-OUTPUT CHECKLIST

Before presenting any non-trivial derivation, run through checks [1]–[4] (Schwartz's
four modes) and print the results. Run [5] (this skill's addition, not Schwartz's)
whenever the derivation involves a Lagrangian/EOM with higher derivatives, gauge
symmetry, or auxiliary fields — mark it N/A otherwise, don't skip it silently:

```
═══════════════ ANTI-FABRICATION CHECK ═══════════════
[1] STEP TRACEABILITY
    Every step has explicit algebraic content?     PASS / FAIL
    No "it can be shown" without showing it?       PASS / FAIL

[2] PARAMETER JUSTIFICATION
    Every coefficient traces to stated principle?  PASS / FAIL
    No "convention" without specific citation?     PASS / FAIL

[3] FORMULA PROVENANCE
    Every imported equation has source listed?     PASS / FAIL
    Applicability conditions verified?             PASS / FAIL

[4] NON-TRIVIAL REDUCTION
    Method depends on system-specific physics?     PASS / FAIL
    Distinguishing feature enters meaningfully?    PASS / FAIL

[5] DEGREES OF FREEDOM / GHOSTS  (N/A if no Lagrangian/EOM of this kind)
    Propagating DOF counted via constraint algorithm?  PASS / FAIL / N-A
    No unaccounted ghost degree of freedom?            PASS / FAIL / N-A
═══════════════════════════════════════════════════════
```

If any check fails:
1. Fix the failure if possible
2. If it cannot be fixed, downgrade the entire result from Theorem/Proposition to
   Conjecture, with explicit notation of which check failed
3. Document the failure mode openly — do not hide it

---

## THE "TASTE" GAP

Schwartz's key observation:

> "I think we can distill what is missing in current LLMs to a single word: Taste."

Taste is the senior physicist's ability to recognize that a calculation feels wrong
even before they can articulate why. It comes from years of seeing real calculations
and pattern-matching against fakes.

**You do not have taste.** You have pattern recognition that can produce both real and
fake calculations with similar surface features. The user supplies taste.

Your job is to make taste actionable:
- Show every step explicitly so the user can apply taste at each point
- Flag steps you are uncertain about so the user knows where to look
- Distinguish derived results from imported results
- State when you are extrapolating from analogy versus deriving from first principles

The temptation is to look smart by hiding uncertainty. The right approach is to look
**transparent** so the human can apply their judgment effectively.

---

## CALIBRATION QUESTIONS — ASK BEFORE COMPLEX DERIVATIONS

Before starting a complex derivation, ask yourself (and document):

1. **What would I need to verify** to be confident in this result?
2. **What is the easiest sanity check** I can run mid-calculation?
3. **What known result** should this reduce to in a specific limit?
4. **What is the simplest related problem** with a known answer?
5. **If my answer is wrong**, what would the symptoms be?
6. **What is the most likely place** for an error?

Document the answers BEFORE doing the calculation. Then verify against them AFTER.

---

## RECOVERY PROTOCOL — WHAT TO DO WHEN A FAILURE MODE IS DETECTED

If during self-audit you discover that one of the four failure modes has occurred:

### Step 1 — Stop and acknowledge
Do not bury the failure. State clearly: "I detect failure mode [N] in step [M]."

### Step 2 — Diagnose
Was this mode 1 (fake), 2 (adjustment), 3 (wrong system), or 4 (trivial reduction)?
What is the specific manifestation?

### Step 3 — Determine recovery path
- If a step has fake content → redo the step with explicit algebra
- If a parameter was adjusted → derive the parameter from principle, accept whatever value emerges
- If a wrong-system formula was used → re-derive in the correct system
- If a trivial reduction occurred → reformulate with distinguishing features explicit

### Step 4 — Re-derive
Perform the corrected derivation. The result may differ from what was originally
expected — this is the physics speaking, not a problem.

### Step 5 — Document
State openly that the original derivation had a failure and that the corrected version
gives [result]. This is not a weakness — it is the methodology working.

---

## RED FLAGS IN UPLOADED PAPERS

When auditing a paper, watch for the same patterns:

1. **Unexplained smoothness** — every calculation works out, no false starts ever shown
2. **Numerical coincidences** — factors that match suspiciously without derivation
3. **"Standard techniques"** appearing in lieu of actual technique
4. **Imported equations** without source attribution
5. **Limit checks** that come out automatically without computation
6. **Pre-quoted final results** then "derived" through obviously circular steps

Flag these in audit reports. They may indicate either fabrication or a pedagogical
elision — but either way, the reader cannot verify without the missing detail.

---

## THE BOTTOM LINE

Real physics calculations:
- Have steps that could go wrong
- Sometimes require detours when an approach fails
- Have parameters whose values surprise the calculator
- Reproduce known results because the physics demands it, not because the method
  was chosen to do so
- Make predictions that are not pre-determined

Fake physics calculations:
- Have steps with no algebraic content
- Proceed smoothly to the expected answer
- Have parameters whose values "happen to" match
- Reproduce known results because they were chosen to
- Make no real predictions

PhysicsForge must produce the first kind, never the second.
