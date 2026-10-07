# PhysicsForge — Anti-Patterns Catalog

A catalogue of specific physics-writing anti-patterns. For each: name, what it looks
like, why it fails, and the correct behaviour.

This is a complement to `anti-fabrication.md` (which describes general failure modes)
and `iron-rules.md` (which states the inviolable rules). This file gives **concrete
examples** the model can recognize and avoid.

The pattern is adapted from Imbad0202's Anti-Patterns table format, applied to
physics-specific failure modes observed in real LLM-assisted work.

---

## ANTI-PATTERN 1 — "It can be shown that"

**What it looks like**:
> "It can be shown that the partition function factorizes as Z = Z_1 · Z_2 in the
> non-interacting limit."

**Why it fails**: This phrase is universally a placeholder for "I haven't actually
shown this and I'm not going to". A reader who tries to verify the claim is left
without a reference, a derivation, or a hint of the argument.

**Correct behaviour**:
- If the result IS shown elsewhere: cite the specific paper, equation, or derivation.
- If the result is genuinely standard: cite a textbook with page or equation number.
- If neither: derive it explicitly, even if the derivation is short.

**Replacement phrases that are honest**:
- "By Eq. (5) of [Smith 2018], Z = Z_1 · Z_2..." (cited)
- "Z = Z_1 · Z_2, which follows from the factorization of e^{-βH} when H = H_1 + H_2 with [H_1, H_2] = 0." (sketched)
- "We conjecture Z = Z_1 · Z_2 based on the non-interacting limit." (acknowledged uncertainty)

---

## ANTI-PATTERN 2 — Theorem-grade claims without proof

**What it looks like**:
> **Theorem 3.1.** *The system has a unique ground state.*
>
> *Proof.* Standard arguments using the Perron-Frobenius theorem give the result. ∎

**Why it fails**: A "Theorem" with a one-sentence "proof" referring to "standard
arguments" is not a theorem — it is a conjecture with overconfident formatting. The
reader cannot verify the result.

**Correct behaviour**:
- If you actually have the proof: write it out, even if compressed.
- If the proof is genuinely a textbook exercise: cite the textbook with theorem
  number, and downgrade to "Proposition" (theorems are reserved for novel proofs).
- If the proof is gestured: downgrade to "Conjecture" and explain what would be
  required to prove it.

**Correct version**:
> **Proposition 3.1.** *The system has a unique ground state.*
>
> *Proof.* The transfer matrix is positive and irreducible (verified by inspection
> of its entries; see App. A). By the Perron-Frobenius theorem [Reed-Simon vol. IV,
> Thm. XIII.43], the largest eigenvalue is non-degenerate, giving the result. ∎

---

## ANTI-PATTERN 3 — Trivial limit checks

**What it looks like**:
> "In the limit ℏ → 0, our result reduces to the classical equation, confirming the
> derivation."

**Why it fails**: Limit checks are only meaningful if they constrain the result. A
formula constructed to reduce to a known limit will trivially do so — that's not
verification.

**Correct behaviour**:
- Choose limits that are NOT trivially built into the construction.
- Show the reduction explicitly with intermediate steps.
- State what new information the limit check provides.
- Pick at least two independent limits.

**Better version**:
> "We verify three independent limits: (a) classical limit ℏ → 0 reduces to Eq. (X)
> as required, with the leading correction proportional to ℏ². (b) Free-particle
> limit V → 0 reduces to the Heisenberg uncertainty bound, which is non-trivial as
> our derivation did not assume the free case. (c) High-temperature limit β → 0
> recovers the classical equipartition result, providing an independent check."

---

## ANTI-PATTERN 4 — Citation by author + year only

**What it looks like**:
> "Following Smith (2019), we have..."

**Why it fails**: This format is unverifiable without additional information. Many
"Smith 2019" papers exist; the reader cannot confirm which one. This is also a
fabrication risk — the model may have invented a "Smith 2019" that doesn't exist.

**Correct behaviour**:
- Always include arXiv ID or DOI in the citation
- For canonical references, give a precise locator (equation number, page number)
- Verify the citation exists via Crossref / arXiv before delivery

**Correct version**:
> "Following [Smith 2019, arXiv:1903.12345, Eq. (15)], we have..."

---

## ANTI-PATTERN 5 — Hidden assumptions in "the natural choice"

**What it looks like**:
> "The natural choice for the metric is g_μν = η_μν + h_μν."

**Why it fails**: Calling something "natural" hides the actual reasoning. Different
authors find different things natural, and the choice often determines the result.

**Correct behaviour**:
- State the actual assumption: "We assume linearization around Minkowski space, valid
  for weak gravitational fields where |h_μν| ≪ 1."
- Acknowledge alternatives: "Other choices (e.g., expansion around Schwarzschild) are
  appropriate for different regimes."
- Tag the assumption: `[ASSUMPTION]` so it's clear this is input, not derivation.

---

## ANTI-PATTERN 6 — Plot-fits-expectation parameter adjustment

**What it looks like**:
> "We find that with α = 1.7, our prediction matches the data within 5%."

**Why it fails**: If α was determined by fitting the data, the prediction is no
longer testing the theory — it is fitting it. This is the precise failure mode
Schwartz observed when Claude tweaked parameters until plots matched.

**Correct behaviour**:
- If α is derived from theory: cite the derivation. The 5% agreement is then
  meaningful.
- If α is fitted from data: state this. The 5% agreement is then by construction.
- If α was tuned to "make the plot work": this is a bug. Find the actual reason for
  the disagreement.

**Honest version**:
> "Theory predicts α = 1.732 (Eq. 12). The data give α_fit = 1.745 ± 0.05. The
> agreement is 0.7% within experimental uncertainty, providing a non-trivial test
> of the theory."

---

## ANTI-PATTERN 7 — Notation drift across sections

**What it looks like**:
> Section 2 uses ψ for the wavefunction.
> Section 4 uses Φ for the wavefunction (without saying it's the same thing).
> Section 6 uses φ for the wavefunction.

**Why it fails**: The reader cannot tell if these are the same object or different
objects. Inconsistent notation suggests the author hasn't been careful.

**Correct behaviour**:
- Use one notation per object throughout the paper
- If notation must change (e.g., entering a different convention), state explicitly:
  "From here, we use Φ for the wavefunction (formerly ψ) to match the convention of
  [Smith 2018]."
- Maintain a notation table for long manuscripts

---

## ANTI-PATTERN 8 — Bullet-list derivations

**What it looks like**:
> The proof proceeds in three steps:
> - Step 1: Apply the equation of motion
> - Step 2: Use the boundary conditions
> - Step 3: Take the limit ℏ → 0

**Why it fails**: A derivation is not a list. Each step depends on the previous one;
the relationship is sequential and logical, not enumerative. Bullet-listing erases
the dependency structure.

**Correct behaviour**: Write the derivation as flowing prose with numbered equations.
The mathematical content goes in display equations; the connecting logic goes in
prose between them.

**Correct version**:
> Beginning from the equation of motion (Eq. 14), we apply the boundary condition
> ψ(0) = 0, which restricts the solution space to odd-parity wavefunctions. The
> resulting expression (Eq. 17) admits a sensible classical limit only if we treat
> ℏ as a small parameter; expanding in powers of ℏ gives, to leading order, the
> classical Hamilton-Jacobi equation (Eq. 19). Higher-order corrections produce the
> WKB hierarchy.

---

## ANTI-PATTERN 9 — Concluding without conclusion

**What it looks like**:
> "In conclusion, we have presented a new approach to the problem. Our method has
> several advantages. Future work will explore further applications."

**Why it fails**: This is conclusion-shaped text that doesn't conclude anything. It
states "we did something good" without saying what was done or why it matters.

**Correct behaviour**: A real conclusion has three parts:
1. **What was actually established** (the result, restated precisely)
2. **Why this matters** (specific consequences, not generic "advances")
3. **What is still open** (specific next questions, not generic "future work")

**Correct version**:
> We have derived an exact expression for the partition function of the kinetic
> freeze-out problem in degenerate fermionic matter (Eq. 47), valid in the regime
> n/n_F < 0.1. The result resolves the discrepancy between the Boltzmann and
> hydrodynamic approaches in the early-universe context first identified by [Jones
> 2019]. The principal open question is whether the expansion converges for
> n/n_F > 0.1; we conjecture that the radius of convergence is set by the
> thermal-de-Broglie wavelength compared to the inter-particle spacing.

---

## ANTI-PATTERN 10 — "Recent advances" without dates

**What it looks like**:
> "Recent advances in machine learning have transformed our understanding of the
> field."

**Why it fails**: "Recent" is undefined. A paper from 2024 saying "recent" might be
published in 2026. The phrase is also empty — what advances? In what direction?

**Correct behaviour**: State specifically what advances, when they happened, and who
made them.

**Correct version**:
> "Beginning with [Smith 2022, arXiv:2201.XXXXX], machine-learning methods have
> been applied to lattice QCD calculations, producing speed-ups of 10x for
> [specific calculation type] while maintaining controlled errors."

---

## ANTI-PATTERN 11 — Theorem packaging weakness

**What it looks like**:
> "We have shown that the system has interesting properties."

**Why it fails**: "Interesting" is not a property. The reader cannot verify what was
shown.

**Correct behaviour**: State the actual result with mathematical precision.

**Correct version**:
> "We have shown that the system exhibits a phase transition at T_c = 1.42(3) J/k_B,
> with mean-field exponent α = 0.5 and correlation-length exponent ν = 0.65 ± 0.05
> below T_c."

---

## ANTI-PATTERN 12 — Abstract that doesn't abstract

**What it looks like**:
> "This paper presents a study of [topic]. We use [method] to investigate [phenomenon].
> Our results have implications for [field]."

**Why it fails**: The abstract states the structure of the paper without conveying
its content. The reader cannot tell from this abstract whether the paper is
interesting.

**Correct behaviour**: An abstract states what is shown, in terms specific enough
that a reader can decide whether to read the paper.

**Correct version**:
> "We compute the kinetic freeze-out time for degenerate fermionic matter in a
> radiation-dominated cosmological background using the Boltzmann equation with
> Pauli blocking. The freeze-out time scales as t_f ∝ T_F^{-2/3}, two orders of
> magnitude faster than naive Maxwell-Boltzmann predictions. We discuss
> implications for sterile-neutrino dark matter scenarios where this freeze-out
> regime is operative."

---

## ANTI-PATTERN 13 — Conservation-law violation passed without check

**What it looks like**: A derivation produces an expression that violates energy,
momentum, charge, or particle-number conservation, and the violation is not noticed.

**Why it fails**: Conservation laws are powerful constraints. A result that violates
them is wrong. Failing to check conservation is failing to apply one of the
strongest available checks.

**Correct behaviour**: For every result, explicitly check conservation:
- "Energy conservation: ∂E/∂t = 0 by Eq. (X). ✓"
- "Charge conservation: ∂_μ J^μ = 0 follows from gauge invariance. ✓"

If conservation fails, the derivation has an error — find and fix it.

---

## ANTI-PATTERN 14 — Symmetry-violation passed without check

**What it looks like**: A result is asserted to respect a symmetry (Lorentz, gauge,
parity, etc.) without explicit verification.

**Why it fails**: Asserted symmetries are often broken by intermediate steps that
the author didn't notice. Explicit verification is the only protection.

**Correct behaviour**: For every claimed symmetry of a result, verify:
- Lorentz: contractions match, indices are summed correctly
- Gauge: result depends only on field strengths, not potentials
- Parity: pseudoscalars and scalars don't mix
- Time-reversal: T-odd and T-even quantities don't mix

---

## ANTI-PATTERN 15 — Equation-by-equation paper

**What it looks like**: A paper consisting almost entirely of equations with minimal
connecting text.

**Why it fails**: Equations without context don't communicate. The reader cannot
follow the derivation, cannot tell what's important, cannot identify the main result.

**Correct behaviour**: For every equation, the surrounding prose should answer:
- What does this equation represent physically?
- What does it follow from?
- What is its significance?
- What does it lead to?

A rough rule: equation density of more than 1 per 100 words of prose suggests
under-explanation.

---

## ANTI-PATTERN 16 — "We will show" without showing

**What it looks like**:
> "In this paper, we will show that [strong claim]. We will derive [other strong
> claim]. We will demonstrate [yet another claim]."

**Why it fails**: Promises in the introduction must be delivered in the body. A
paper that claims more in the introduction than it shows in the body is mis-advertised.

**Correct behaviour**:
- After drafting the body, return to the introduction and verify each promise is
  fulfilled
- If a promise was not delivered, either deliver it or remove the promise
- Use precise verbs: "show", "derive", "compute" have specific meanings; honour them

---

## ANTI-PATTERN 17 — Numerical claim without precision

**What it looks like**:
> "Our calculation gives a value about 30% larger than experiment."

**Why it fails**: "About 30%" is not a measurement. The reader cannot tell if the
agreement is meaningful (within the experimental and theoretical uncertainties) or
indicative of a real discrepancy.

**Correct behaviour**: State numerical results with their uncertainties:
> "Our calculation gives 1.42(3) J/mol, 28% larger than the experimental value
> 1.11(2) J/mol [Smith 2018]. The 28(4)% discrepancy is statistically significant
> (>5σ) and points to systematic effects we discuss in §V."

---

## ANTI-PATTERN 18 — Fitted parameter masquerading as theory parameter

**What it looks like**: A theory has a parameter c that is "determined by fitting
to data" but is then reported as a theoretical prediction.

**Why it fails**: A parameter determined by fitting cannot also be a theoretical
prediction. Conflating these inflates the apparent predictivity of the theory.

**Correct behaviour**: State unambiguously which parameters are:
- **Predicted** by the theory (derived from first principles)
- **Fitted** from the data (free parameters tuned to match)
- **Inputs** (taken from external measurement)

A theory's predictivity is determined by how few parameters are fitted versus how
many predictions are produced.

---

## ANTI-PATTERN 19 — "More research is needed"

**What it looks like**: A conclusion that ends "more research is needed" or "future
work will explore..." without specifying what research or what future work.

**Why it fails**: This is filler. Useful future-work statements specify the question,
the approach, and the expected payoff.

**Correct behaviour**:
- "It remains open whether [specific question] holds for [specific case]. The
  technique most likely to settle this is [specific method]."
- "An immediate extension is [specific generalization], which would require addressing
  [specific obstacle]."

---

## ANTI-PATTERN 20 — Confidence-without-evidence

**What it looks like**:
> "It is clear that..." / "It is obvious that..." / "Surely..." / "Of course..."

**Why it fails**: These phrases assert that the reader will agree, replacing the
need for evidence with social pressure. They appear most often when the author
themselves is uncertain.

**Correct behaviour**:
- If the claim IS clear, demonstrate the clarity (one-line argument or citation)
- If the claim is NOT clear, drop the modifier and provide the actual argument
- If you find yourself writing "obviously", that is a signal to slow down

---

## USE OF THIS CATALOGUE

When generating output:

1. **Before writing a section**: Skim this catalogue for patterns relevant to what
   you're about to write.

2. **After writing a section**: Audit the output against this catalogue. Each
   pattern detected should be revised before continuing.

3. **Before delivery**: Run a final pass against the most common patterns
   (anti-patterns 1, 2, 4, 6, 13, 14).

This catalogue is meant to be **non-exhaustive** — physics has more anti-patterns
than any list can capture. The patterns here are the most common in LLM-assisted
physics work. Encountering a new failure mode? Add it to local notes for future
sessions.

---

## INTEGRATION WITH OTHER PROTOCOLS

- During derivation: anti-patterns 1, 2, 3 are most relevant
- During paper writing: anti-patterns 7, 8, 9, 10, 11, 12, 15, 16, 19, 20
- During citation: anti-patterns 4 is critical
- During parameter fitting: anti-patterns 6, 18 are critical
- During physical reasoning: anti-patterns 5, 13, 14, 17 are critical

The full catalogue should be in mind throughout, but specific patterns are more
relevant at specific stages.
