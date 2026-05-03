# PhysicsForge — Worked Examples

Three examples showing what good output looks like in different modes.

---

## EXAMPLE 1 — A Finished PRL-Style Section

This example shows the level of completeness, equation density, and tone expected
from `latex-engine.md` output. Use this as a calibration target.

### User request
*"Write the 'Identifying the Gap' section of a PRL letter on the cosmological
constant problem."*

### Output

```latex
\section{Identifying the Gap}
\label{sec:gap}

The cosmological constant problem is the most severe quantitative discrepancy
between theory and observation in physics. The observed value of the vacuum
energy density is~\cite{Planck2020}
\begin{equation}
  \rho_\Lambda^\text{obs} \approx (2.3 \times 10^{-3}\,\text{eV})^4
  \approx 4.0 \times 10^{-47}\,\text{GeV}^4.
  \label{eq:rho-obs}
\end{equation}
The naive QFT prediction, obtained by summing zero-point energies of all known
fields up to the Planck cutoff $\Lambda_{UV} = M_{Pl}$, gives
\begin{equation}
  \rho_\Lambda^\text{QFT} \sim \int_0^{M_{Pl}} \frac{d^3 k}{(2\pi)^3}\,
  \frac{1}{2}\sqrt{k^2 + m^2} \sim M_{Pl}^4 \approx 4.7 \times 10^{72}\,\text{GeV}^4.
  \label{eq:rho-qft}
\end{equation}
The ratio $\rho_\Lambda^\text{obs} / \rho_\Lambda^\text{QFT} \sim 10^{-120}$ requires
a cancellation of $120$ decimal places between the bare and induced contributions.

The standard responses partition into three families. \textit{Anthropic selection}
within a multiverse with varying $\Lambda$~\cite{Weinberg1989} predicts $\Lambda$ near
the boundary of galaxy formation, but presupposes a measure on the multiverse that
remains undefined~\cite{GuthVanchurin2011}. \textit{Symmetry-based cancellation},
exemplified by unbroken supersymmetry, would set $\rho_\Lambda = 0$ exactly; broken
SUSY at scale $M_{SUSY} \gtrsim 1$ TeV instead generates $\rho_\Lambda \sim M_{SUSY}^4
\approx 10^{12}\,\text{GeV}^4$, off by $59$ orders of magnitude~\cite{Witten2001}.
\textit{Modified gravity} — quintessence~\cite{CaldwellSteinhardt1998}, $f(R)$~\cite{
SotiriouFaraoni2010}, and unimodular gravity~\cite{Weinberg1989} — typically replaces
one fine-tuning with another or fails to address the radiative-correction problem.

We identify three structural features that any successful resolution must possess,
none of which is satisfied by the existing approaches:
\begin{enumerate}[label=(\roman*)]
  \item \textbf{UV/IR mixing}: the cancellation must couple Planck-scale physics
    to Hubble-scale physics, since $\rho_\Lambda^\text{obs}$ is set by $H_0^2 M_{Pl}^2$
    rather than by any pure UV scale.
  \item \textbf{Stability under radiative corrections}: any mechanism that sets
    the tree-level $\Lambda$ to zero must survive loop corrections of order
    $M_{Pl}^4$, not merely $M_{Higgs}^4$ or $M_{SUSY}^4$.
  \item \textbf{Compatibility with the equivalence principle}: the mechanism must
    not introduce fifth forces ruled out by torsion-balance experiments at the
    $10^{-13}$ level~\cite{Touboul2017}.
\end{enumerate}

The remainder of this paper presents a framework satisfying all three constraints.
```

### What this demonstrates

- Real numerical values with citations
- Equation block with derived consequence (the 120 orders)
- Tripartite literature survey, each with its specific failure mode
- Three numbered constraints that the new framework must satisfy
- No placeholders, no hand-waving, no "it can be shown"

---

## EXAMPLE 2 — A Paper Critique (Audit Output)

This example shows the format expected from `paper-analysis.md` workflow.

### User request
*"Audit this paper's main derivation."* [paper claims to prove the
Riemann Hypothesis via a heuristic operator construction]

### Output (excerpt)

```
═══════════ PAPER CRITIQUE ═══════════
Author's claim: Theorem 3.1 — RH is true.
Author's proof structure: Construct self-adjoint operator T whose eigenvalues are
the imaginary parts of nontrivial Riemann zeros.

CLAIM INVENTORY
═══════════════
[C1] (Theorem-claimed)   T is self-adjoint on Hilbert space H.
[C2] (Heuristic)         T's spectrum corresponds to Riemann zeros.
[C3] (Conjecture)        H is dense in L²(ℝ⁺, dx/x).
[C4] (Theorem-claimed)   Therefore RH holds.

DEPENDENCY GRAPH
════════════════
C3 (conjecture) ──> C1 (claimed theorem)
                      └──> C4 (claimed theorem)
C2 (heuristic) ─────────┘

DERIVATION AUDIT
════════════════
Eq.(3.4): "T is symmetric since ⟨Tf,g⟩ = ⟨f,Tg⟩ for f,g ∈ D(T)."
  ✓ Symmetry on the dense domain D(T) is correctly verified.

Eq.(3.7): "T is self-adjoint by Theorem 2 of [12]."
  ⚠ The cited theorem requires T's deficiency indices to vanish.
    The author does not check this. Symmetric ≠ self-adjoint for unbounded operators.

Eq.(3.12): "The spectrum of T equals {γ : ζ(1/2 + iγ) = 0}."
  ✗ This is asserted, not proven. The author cites a "trace formula"
    (Eq.3.10) whose convergence requires self-adjointness already proven —
    circular dependency with C1.

HIDDEN ASSUMPTION
═════════════════
Section 4: "By Stone's theorem the unitary group e^{iTt} is well-defined."
  Hidden: Stone's theorem requires self-adjointness. Cannot be invoked
  before C1 is established. Logical circularity.

VERDICT
═══════
The construction is interesting but does NOT prove RH:
  - C1 (self-adjointness) requires verifying deficiency indices — not done
  - C2 (spectrum match) is asserted via a trace formula assuming C1
  - The chain C3 → C1 → C4 has a circular link at C1↔C2

Genuine novelty: The proposed operator T has a clean group-theoretic structure
that may be of independent interest (Section 5).

Status of RH: Open. This paper does not advance it.

PAULI PROTOCOL applied to author's Theorem 3.1
═════════════════════════════════════════════
[1] Falsifiability:    PASS (RH is falsifiable)
[2] Restatement:       FAIL — proves "RH iff C3" rather than RH
[3] Hidden assumption: FAIL — self-adjointness is not verified
[4] Symmetry:          PASS (uses standard inner product)
[5] Dimensional:       N/A (pure math, no dimensions)
[6] Limiting case:     N/A
[7] Peer-review:       FAIL — would not pass at Annals
═════════════════════════════════════════════

Recommendation: downgrade Theorem 3.1 to "Conditional Theorem assuming
self-adjointness of T". The paper is then a contribution to the
Hilbert-Pólya program, not a proof of RH.
═════════════════════════════════════
```

### What this demonstrates

- Honest verdict, no deference to the author
- Specific equation-by-equation audit, not vague critique
- Identifies the precise circular dependency
- Acknowledges genuine novelty separately
- Pauli Protocol applied to the author's claim, not to one's own work

---

## EXAMPLE 3 — A Symbolic Verification Trace

This example shows what a `verification.md` execution looks like in practice.

### User request
*"I derived this formula. Verify it."* [user provides $E^2 = (pc)^2 + (mc^2)^2$]

### Output

```
Running symbolic verification on E² = (pc)² + (mc²)²

═══════════ SYMBOLIC VERIFICATION ═══════════
Target:    Relativistic energy-momentum relation E² = (pc)² + (mc²)²
Tool used: sympy + numerical sanity checks

Setup:
  E, p, m, c = symbols('E p m c', positive=True, real=True)
  formula = sp.Eq(E**2, (p*c)**2 + (m*c**2)**2)

Check 1 — Dimensional consistency:
  [E²]      = M² L⁴ T⁻⁴
  [(pc)²]   = (M L T⁻¹ · L T⁻¹)² = M² L⁴ T⁻⁴      ✓
  [(mc²)²]  = (M · L² T⁻²)² = M² L⁴ T⁻⁴            ✓
  All three terms have identical dimensions — PASS

Check 2 — Limit p → 0 (rest):
  formula.subs(p, 0) → E² = (mc²)² → E = mc²        ✓
  Recovers Einstein's rest energy.

Check 3 — Limit m → 0 (massless):
  formula.subs(m, 0) → E² = (pc)² → E = pc          ✓
  Recovers photon dispersion E = pc.

Check 4 — Newtonian limit (p ≪ mc):
  Solve for E, expand to O(p²):
  E = sqrt((pc)² + (mc²)²) = mc² · sqrt(1 + (p/mc)²)
  Taylor expansion to O(p⁴):
    E ≈ mc² + p²/(2m) − p⁴/(8m³c²) + O(p⁶)         ✓
  Recovers rest energy + classical kinetic + leading relativistic correction.

Check 5 — Numerical evaluation at relativistic speed:
  m = 9.109e-31 kg (electron), v = 0.9c
  Direct: E = γmc² = 2.294 · 8.187e-14 = 1.879e-13 J
  Formula: p = γmv = 5.5e-22, E_formula = sqrt((pc)² + (mc²)²) = 1.879e-13 J ✓
  Match to 4 significant figures.

Check 6 — Lorentz invariance:
  E² − (pc)² = (mc²)² is the squared norm of the 4-momentum p^μ p_μ
  This must be a Lorentz scalar by construction
  Verified by checking that the right-hand side is independent of frame    ✓

Verdict: PASS — formula is dimensionally consistent, recovers all
expected limits, matches numerical values, and is manifestly Lorentz invariant.

═════════════════════════════════════════════
```

### What this demonstrates

- Six independent verification angles, not just one
- Both symbolic (sympy) and numerical (numpy) checks
- Each known limit recovered explicitly
- Numerical values cross-checked with two computation paths
- Clear PASS verdict with justification

---

## HOW TO USE THESE EXAMPLES

When generating output, mentally compare against these:

- **Density of equations**: Example 1 shows ~3 equations per page, each derived,
  none unmotivated. Match this density.
- **Specificity of critique**: Example 2 names the precise failed step, not "the
  argument is hand-wavy". Match this specificity.
- **Multiplicity of checks**: Example 3 runs six verification angles. Don't run
  one and call it verified.

If your draft response would not pass these standards, rewrite it before
sending to the user.
