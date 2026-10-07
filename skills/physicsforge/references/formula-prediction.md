# PhysicsForge — Formula Prediction Protocol

A methodology for predicting new physical formulae with maximal mathematical fidelity.
Combines the **Buckingham π theorem** (rigorous dimensional analysis) with symmetry
constraints, limiting case requirements, and literature analogy. Each component carries
its own epistemic status — keep them distinct.

This protocol distinguishes what dimensional analysis **proves** (functional structure
of the equation) from what physical input **suggests** (the specific functional form).

---

## WHEN TO USE THIS PROTOCOL

Trigger this protocol when the user asks:
- "Predict a formula for [phenomenon]"
- "Derive an equation for [system]"
- "What should the formula for X look like?"
- "Run Buckingham π on these quantities"
- "What does dimensional analysis say about [X]?"
- "Find an equation linking [A, B, C, ...]"

This is a derivation task, so anti-fabrication protocol applies. Read
`anti-fabrication.md` first.

---

## THE FOUR-STAGE PROTOCOL

### Stage 1 — Buckingham π theorem (rigorous, mathematical)
### Stage 2 — Symmetry constraints (rigorous, given the symmetries)
### Stage 3 — Limiting case requirements (constraint, not derivation)
### Stage 4 — Literature analogy (heuristic, must be justified)

Each stage carries its own epistemic status. The Buckingham result is a **theorem**.
Symmetry constraints are theorems given the assumed symmetries. Limiting cases give
constraints. Literature analogies are heuristics that must be justified system-by-system.

---

## STAGE 1 — BUCKINGHAM π THEOREM

### Statement

Given a physical equation involving n quantities expressed in d independent dimensions
(typically a subset of M, L, T, Q, Θ for mass, length, time, charge, temperature), the
equation can be reduced to a relationship among (n − r) dimensionless groups, where r
is the rank of the dimensional matrix.

In symbols: f(q₁, q₂, ..., qₙ) = 0 reduces to F(Π₁, Π₂, ..., Π_{n−r}) = 0

The Π_i are independent dimensionless combinations of the q_j.

### Why this is a theorem, not a heuristic

The proof is pure linear algebra. Given any physical equation that is dimensionally
consistent (which all valid physical equations are), it must depend only on
dimensionless combinations. The number of independent such combinations is determined
by the rank of the dimensional matrix.

**This is exact. It does not depend on the physics.** It only depends on what
quantities you put in and what their dimensions are.

### Algorithm

1. **List the relevant physical quantities** with their dimensions
2. **Build the dimensional matrix** A: rows = dimensions, columns = quantities
3. **Compute the rank** r of A (using Gaussian elimination over the rationals)
4. **The number of dimensionless groups** is n − r
5. **Find the null space** of A — each null vector gives the exponents of one Π group
6. **Express each Π** as a product of quantities raised to fractional/integer powers

### Example: simple pendulum

Quantities: T (period), l (length), g (gravity), m (mass)

Dimensions:
| | T | l | g | m |
|---|---|---|---|---|
| M | 0 | 0 | 0 | 1 |
| L | 0 | 1 | 1 | 0 |
| T | 1 | 0 | -2 | 0 |

Rank = 3, so n − r = 4 − 3 = 1 group.

Solving for the null vector: Π = T·g^{1/2}·l^{-1/2} = T·√(g/l)

Therefore: T·√(g/l) = const, giving T ∝ √(l/g).

**Mass m drops out.** The Buckingham analysis tells you this with certainty before any
physics — pure dimensional reasoning rules out mass dependence.

### Required output format for Stage 1

```
═══════════════ BUCKINGHAM π ANALYSIS ═══════════════
Quantities considered:
  q₁ = [name]: dimensions [M^a L^b T^c Q^d Θ^e]
  q₂ = ...
  ...

Dimensional matrix:
       q₁  q₂  q₃ ...
  M  [  ]
  L  [  ]
  T  [  ]
  Q  [  ]
  Θ  [  ]

Rank of dimensional matrix: r = ___
Number of dimensionless groups: n − r = ___

Independent Π groups:
  Π₁ = [explicit product of quantities with exponents]
  Π₂ = ...

The physics must satisfy: F(Π₁, Π₂, ...) = 0

CLAIM CLASSIFICATION: [DIMENSIONAL THEOREM]
  This result is exact. Any physically correct equation involving these quantities
  must reduce to this functional dependence.
══════════════════════════════════════════════════════
```

### Common pitfalls in Stage 1

- **Missing a relevant quantity**: If you forget to include a quantity that does
  matter, your Π groups will be wrong. **Audit the input list before running.**
- **Including an irrelevant quantity**: This adds a fake degree of freedom.
- **Wrong dimensions**: Double-check every dimensional assignment.
- **Confusing units with dimensions**: 1 eV and 1 kg both have units of "mass" in
  natural units; be consistent.

---

## STAGE 2 — SYMMETRY CONSTRAINTS

After Buckingham, the physics is f(Π₁, Π₂, ..., Π_k) = 0. Symmetry constraints further
restrict the form of f.

### Common symmetries and their consequences

| Symmetry | Constraint on f |
|---|---|
| Lorentz invariance | f depends only on Lorentz scalars |
| Rotational invariance | f depends only on rotational scalars |
| Translational invariance | f cannot depend on absolute position |
| Time-reversal symmetry | f must be even in time-derivative quantities |
| Parity (P) | f cannot contain pseudoscalar combinations unless P-violating |
| Charge conjugation (C) | f cannot mix particle/antiparticle terms unless C-violating |
| CPT | f must respect the combined symmetry |
| Gauge invariance (U(1)) | f must be expressible in gauge-invariant variables |
| Scale invariance | f cannot contain dimensional scales — typically eliminates Π groups |

### Required output format for Stage 2

```
═══════════════ SYMMETRY ANALYSIS ═══════════════
Stated symmetries:
  - [Symmetry 1]: [...]
  - [Symmetry 2]: [...]

Forbidden terms (by symmetry):
  - [Term]: forbidden by [which symmetry]
  
Required terms (by symmetry):
  - [Term]: required by [which symmetry]
  
Allowed functional forms after symmetry:
  f(Π₁, ..., Π_k) restricted to: [...]

CLAIM CLASSIFICATION: [SYMMETRY THEOREM]
  Given the stated symmetries hold, f cannot have the forbidden terms.
  Conditional on assumed symmetries.
══════════════════════════════════════════════════
```

### Critical caveat

Symmetries are **assumed**, not derived. State which symmetries you are assuming and
why they are appropriate. If the system spontaneously breaks a symmetry (e.g.,
spontaneous magnetization in a ferromagnet below Tc), the broken symmetry no longer
constrains f.

---

## STAGE 3 — LIMITING CASE REQUIREMENTS

The functional form f must reduce to known results in specific limits. Each limit gives
a constraint.

### Required limits to check

For any predicted formula, verify behavior in:

1. **Weak coupling / linear limit**: f → first nonzero term in the small parameter
2. **Strong coupling / nonlinear limit**: f → known result if available
3. **Classical limit** (ℏ → 0): quantum result reduces to classical
4. **Non-relativistic limit** (v/c → 0): relativistic result reduces to Galilean
5. **Thermodynamic limit** (N → ∞): finite-system result reduces to bulk
6. **Continuum limit** (lattice spacing → 0): discrete result reduces to continuous
7. **Static limit** (∂_t → 0): dynamic result reduces to equilibrium
8. **Free limit** (interactions → 0): coupled result reduces to free theory

### Required output format for Stage 3

```
═══════════════ LIMITING CASE ANALYSIS ═══════════════
Required limit 1: [name]
  Expected: [known result this limit must reproduce]
  My candidate form gives: [result]
  Match: ✓ / ✗
  If ✗: my candidate must be modified to satisfy this limit

Required limit 2: [name]
  ...

Constraints on f from limits:
  - In limit X, f → [...]
  - In limit Y, f → [...]
  
Combined functional form (with limit constraints):
  [...]

CLAIM CLASSIFICATION: [CONSTRAINT]
  These are consistency requirements, not derivations.
══════════════════════════════════════════════════════
```

---

## STAGE 4 — LITERATURE ANALOGY

Search literature for equations with the same dimensional structure. This is the most
heuristic stage — be careful about applicability.

### Operation

For each Π group structure or candidate functional form found by stages 1–3, search:
1. arXiv (via web search) for equations with the same dimensional combination
2. Physics textbooks for known results in the same dimensional class
3. Cross-disciplinary literature for analogous mathematical structures

### Critical filter

For each analogous equation found, ask:
- Does the analogue's derivation rely on assumptions that hold in our system?
- Does the analogue's regime of validity overlap with ours?
- Are the physical mechanisms genuinely similar, or just dimensionally similar?

**Dimensional similarity is not physical similarity.** Many equations have the same
dimensional form but encode entirely different physics.

### Required output format for Stage 4

```
═══════════════ LITERATURE ANALOGY ═══════════════
Searched for: [search terms]

Analogous equations found:
[Equation 1]: [formula]
  Original system: [where it was derived]
  Source: [arXiv ID + paper]
  Mechanism: [physical content]
  Applicability to our problem:
    - Required assumptions hold? [YES/NO/PARTIAL]
    - Regime overlaps? [YES/NO/PARTIAL]
    - Mechanism similar? [YES/NO/UNCLEAR]
  Verdict: USEFUL ANALOGY / SUPERFICIAL ANALOGY / NOT APPLICABLE

Candidate functional forms inspired by analogy:
  Form A: [formula]
    Status: [SUGGESTED BY ANALOGY — needs derivation in our system]
  Form B: [formula]
    ...

CLAIM CLASSIFICATION: [HEURISTIC] for the specific functional form
  The analogy is a guide, not a derivation. To upgrade to PROPOSITION, 
  derive the form from first principles in our system.
══════════════════════════════════════════════════
```

Grade how much this analogy should actually raise confidence using Pattern 4 of
`plausible-reasoning.md`: does the candidate system share the *structural*
assumptions that made the analogous problem solvable, or only the surface form
of the equation? The latter is exactly the Wrong-System-Formula failure mode in
`anti-fabrication.md` if it's used to assert a result, but is fine as a
heuristic starting point here as long as it's labelled one.

---

## INTEGRATING THE FOUR STAGES

Final output integrates all four stages with explicit epistemic status for each
component:

```
═══════════════════════════════════════════════════════════════════
FORMULA PREDICTION FOR [PHENOMENON]
═══════════════════════════════════════════════════════════════════

STAGE 1 — DIMENSIONAL ANALYSIS [THEOREM]:
  The physics must reduce to F(Π₁, ..., Π_k) = 0 with [k] groups
  Π₁ = [...]
  Π₂ = [...]
  
  → This is exact. Independent of physical content.

STAGE 2 — SYMMETRY [THEOREM, conditional]:
  Given symmetries [list], F cannot depend on [forbidden combinations]
  Allowed forms: F(Π₁, ..., Π_k) restricted to [...]
  
  → Exact given the assumed symmetries.

STAGE 3 — LIMITING CASES [CONSTRAINT]:
  In limit [X]: F → [known]
  In limit [Y]: F → [known]
  Form must satisfy these constraints.
  
  → Necessary, not sufficient.

STAGE 4 — LITERATURE ANALOGY [HEURISTIC]:
  Analogous equations: [list with arXiv IDs]
  Suggested functional form: [...]
  
  → Suggestion only. Requires derivation to confirm.

═══════════════ INTEGRATED PREDICTION ═══════════════
Most likely functional form:
  [explicit formula]

Why this is the most likely form:
  [combine evidence from stages 1–4]

Alternative forms not ruled out:
  [formula]: would be selected if [...]
  [formula]: would be selected if [...]

DISCRIMINATING MEASUREMENT:
  [Specific experiment that would distinguish forms]
  
EPISTEMIC STATUS BY COMPONENT:
  Functional structure (depends only on Π groups): [THEOREM]
  Symmetry-allowed combinations: [THEOREM, conditional on symmetries]
  Limiting case behavior: [CONSTRAINT, must be satisfied]
  Specific functional form selected: [HEURISTIC, requires derivation]

WHAT THIS DOES NOT PROVE:
  - The specific functional form is suggested by analogy, not derived
  - The numerical coefficients are not determined by this analysis
  - The result holds within the regime of the assumed symmetries
══════════════════════════════════════════════════════
```

---

## ANTI-FABRICATION CHECKS FOR FORMULA PREDICTION

After producing a candidate formula, before presenting it:

### Check 1 — Buckingham was actually run
Did you actually do the linear algebra, or did you guess the Π groups?

If you wrote down the Π groups without computing the rank of the dimensional matrix
explicitly, you have not done the Buckingham analysis. Redo it explicitly.

### Check 2 — Formula matches Π structure
Does your candidate formula respect the Π structure? Specifically: can it be written
as a function of the Π groups only, with no leftover dimensional dependence?

If your formula has dimensional content that doesn't appear in any Π group, something
has gone wrong.

### Check 3 — Symmetry was applied to the formula, not assumed
Does the formula actually have the stated symmetries when you apply them explicitly?

Don't say "Lorentz invariant" without checking that the formula transforms correctly
under boosts.

### Check 4 — Limiting cases were computed, not asserted
Did you actually take the limit and see what your formula becomes? Or did you assert
that the limit "obviously" gives the known result?

Limits should be computed term by term.

### Check 5 — Analogy is not transplant
If you used a formula from another system, did you verify that the assumptions of the
original system hold here? Or did you just match dimensional notation?

---

## EXAMPLE: PREDICTING THE BLACKBODY SPECTRUM (PEDAGOGICAL)

Walk through how the protocol applies to a known result:

**Quantities**: B (intensity), T (temperature), ν (frequency), h (Planck), kB (Boltzmann), c (speed of light)

**Stage 1**: 6 quantities, 3 independent dimensions (M, L, T, Θ), so 3 Π groups.

Computing: Π₁ = hν/(kBT) (dimensionless ratio), Π₂ = ... etc.

The physics must satisfy: F(hν/kBT, ...) = 0.

**Stage 2**: Equilibrium isotropic radiation has full rotational symmetry. Time-reversal
symmetric for blackbody. Reduces dependence to scalar combinations of Π groups.

**Stage 3**: Required limits:
- High T (kBT ≫ hν): Rayleigh-Jeans law, B ∝ T·ν²
- Low T (kBT ≪ hν): Wien limit, B ∝ ν³ exp(-hν/kBT)

These two limits together strongly constrain F.

**Stage 4**: Search for distributions that interpolate between these limits gives the
Bose-Einstein distribution form: 1/(exp(hν/kBT) − 1).

**Integrated prediction**: B(ν, T) = (2hν³/c²) · 1/(exp(hν/kBT) − 1)

The functional structure (ν³ prefactor times function of hν/kBT) is determined by the
Buckingham analysis combined with the limiting cases. Only the specific interpolating
function 1/(exp − 1) requires the additional input of Bose-Einstein statistics.

This example demonstrates how dimensional theorem + symmetry + limits can predict the
correct form, with the final functional choice traceable to specific physical input
rather than guessed.

---

## EPISTEMIC HONESTY IN FORMULA PREDICTION

The most important rule: **never present a heuristic prediction as a derivation.**

A formula obtained by Buckingham + symmetry + analogy is not a derived result. It is
a prediction or candidate. To upgrade to a derived result, you must:

1. Specify the underlying microscopic theory or principle
2. Carry out an explicit derivation from that starting point
3. Verify that the derivation produces the predicted formula

Skipping step 2 because the prediction matches expectation is the trivial reduction
trap. **Do not skip step 2.**

If a derivation cannot be produced, the prediction remains a [CONJECTURE] or
[HEURISTIC]. This is honest. It is also what good physicists do.
