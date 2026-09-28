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

## EXAMPLE 4 — A Real Self-Audit, With External Verification

Examples 1–3 are illustrative. This one is real: an author (Linga Murthy Narlagiri)
used the audit workflow on his own unpublished draft, *"Phonon-Mediated
Superconductivity in LaMgC₂ Clathrates."* Unlike Examples 1–3, every number below
was independently recomputed (`ad_validate.py`, reproducing the Allen–Dynes formula
in Python) and every reference was checked against Crossref and the source paper's
own text, not asserted from memory. This is what the audit workflow looks like
against a real literature base rather than a synthetic strawman.

### User request
*"Audit this paper's central claim."* [draft claims the (λ, ω_log) parameter region
needed for Tc = 300 K is "empty" — i.e. unreachable by any real material]

### Output (excerpt)

```
═══════════ PAPER CRITIQUE ═══════════
Author's claim: "The target region is empty" — no (λ, ω_log, μ*) combination
reachable by real matter gives Tc = 300 K in this compound class.

CLAIM INVENTORY
═══════════════
[C1] (Theorem-claimed)  Allen–Dynes Eq. gives Tc = 300 K only for (λ, ω_log) pairs
                          that no known material occupies.
[C2] (Heuristic)         Diamond's Debye temperature (2230 K) bounds ω_log for any
                          light-element compound; used to reject the low-λ rows.
[C3] (Established)       λ_c ≈ 3.0–3.7 bounds where Migdal–Eliashberg theory itself
                          holds [Yuzbashyan & Altshuler, PRB 106, 054518 (2022)].
[C4] (Theorem-claimed)   Allen–Dynes over-predicts Nb by 1.8× and H₃S by 1.5×,
                          used to argue the formula carries no safety margin.

DERIVATION AUDIT
════════════════
Target-Tc inversion table (λ = 1.5–4.5, μ* = 0.10–0.16):
  ✓ Recomputed independently. C(1.5, 0.13) = 1.335701 K/meV, matching the
    manuscript to all six printed digits. The arithmetic is correct.

C2 — "diamond bounds ω_log at 2230 K":
  ✗ Wrong quantity. 2230 K is a Debye temperature (a heat-capacity fit), not a
    phonon-frequency ceiling. Diamond's actual highest optical mode is the
    1332 cm⁻¹ Raman line = 165 meV = 1917 K [Warren, Yarnell, Dolling & Cowley,
    Phys. Rev. 158, 805 (1967)] — already below the value used.
  ✗ Also not the tightest bound available: the C≡C stretch of the acetylide
    CaC₂ sits at 1864 cm⁻¹ = 231 meV [Zheng et al., Chem. Sci. 8, 298 (2017)],
    stiffer than diamond. "Diamond is the stiffest lattice" is false as stated.

C1 — "the region is empty":
  ✗ Contradicted by a known material. Full-Eliashberg calculations for LaH₁₀
    give λ ≈ 3.4–3.9, ω_log ≈ 69–78 meV, Tc = 246–271 K at 170–210 GPa
    [Kruglov et al., Phys. Rev. B 101, 024508 (2020), Table 1] — inside the
    same corner of (λ, ω_log) space the manuscript's own table requires for
    Tc = 300 K at λ ≈ 3–4.5. A region containing a real, measured near-neighbour
    cannot be called empty; it can only be argued unreachable *without hydrogen*.

C4 — "Allen–Dynes over-predicts by 1.8× / 1.5×":
  ✗ Unsourced input. The 23 meV used as ω_log(Nb) is the energy of niobium's
    highest phonon peak [Zarea, Ueki & Sauls, Front. Phys. 11, 1269872 (2023)],
    not the logarithmic average — ω_log is necessarily lower than the spectrum's
    peak. Using a peak as an average manufactures the "over-prediction."
  ✗ Opposite sign found on a controlled test. Applying Allen–Dynes to Kruglov's
    own (λ, ω_log) for LaH₁₀ *under*-predicts the full-Eliashberg Tc by 26–30%
    (182 K vs 259 K at 170 GPa; 174 K vs 249 K at 210 GPa) — not over-predicts.
  ⚠ Formula accuracy is input-bottlenecked, not fixed-bias: the same equation
    applied to H₃S spans 201–270 K depending only on whether the phonon
    spectrum came from a PBE or PBE0 functional [Komelj & Krakauer, Phys. Rev. B
    92, 205125 (2015)] — a ~25% swing from DFT choice alone.

HIDDEN ASSUMPTION
═════════════════
The "empty region" conclusion silently assumes Allen–Dynes has a single,
known-direction bias that can be used to sign off on exclusion. The controlled
comparison above shows the bias is input-dependent and, for λ ≳ 3, is a roughly
25–30% *under*-prediction — the opposite direction from what C4 implied.

VERDICT
═══════
"The region is empty" does not survive: LaH₁₀ is a counterexample sitting inside
the same parameter corner the paper claims is unreachable. The defensible, narrower
claim is that *this specific compound* is disfavoured — it has no hydrogen and its
dominant mass (La, 138.9 u) sets a heavy, soft framework — while the high-λ rows sit
at or beyond λ_c (C3, correctly used) and the low-λ rows still require 79–99% of the
total coupling to sit in a single stiff mode (a weighted-mean bound, not the
diamond-Debye argument used originally).

Status of the claim: the "empty" framing is falsified by a cited counterexample.
The "disfavoured, for three independent and individually weaker reasons" framing
survives and is what the revised manuscript now states.

PAULI PROTOCOL applied to author's claim "the target region is empty"
═════════════════════════════════════════════
[1] Falsifiability:    PASS (falsifiable) — and in fact FALSIFIED (see C1 audit)
[2] Restatement:       FAIL — "empty" restates as "empty for hydrides too",
                        which is false; the intended claim was narrower
[3] Hidden assumption: FAIL — assumed Allen–Dynes bias direction, untested
[4] Symmetry:          N/A
[5] Dimensional:       FAIL in one printed display equation (k_B silently
                        dropped, energy returned where a temperature was
                        claimed) though the tabulated numbers were computed
                        correctly; corrected in the revision
[6] Limiting case:     FAIL — the known LaH₁₀ limiting case, which sits inside
                        the claimed-empty region, was not checked against it
[7] Peer-review:       FAIL — a referee working on hydride superconductivity
                        would cite LaH₁₀ as an immediate counterexample
═════════════════════════════════════════════

Recommendation: downgrade "the target region is empty" to "the target region is
occupied only by hydrides; this compound is disfavoured for three stated, weaker
reasons — mass mismatch, a mean-value bound on ω_log, and proximity to λ_c — none
of which alone is decisive." Ship the falsification checklist and the DFPT
calculation that would settle it, rather than the stronger unsupported claim.
═════════════════════════════════════
```

### What this demonstrates

- The audit changed the paper's actual conclusion, not just its wording: "empty"
  (false) became "occupied only by hydrides, and this candidate is disfavoured"
  (defensible) — a materially weaker and more honest claim.
- Every corrected number came from checking a primary source (Crossref DOI lookup
  plus reading the cited paper's own table), not from the auditor's memory.
- A claim can be internally consistent (the arithmetic was right) and still be
  false, because the error was in an input value, not the formula.
- Reusing a spectral *peak* as if it were a *logarithmic average* is a specific,
  checkable error pattern worth watching for in any paper quoting Allen–Dynes,
  McMillan, or similar phonon-averaged formulas.
- The corrected manuscript — Narlagiri, *"Phonon-Mediated Superconductivity in
  LaMgC₂ Clathrates"* (2026) — carries its own revision-notes appendix with the
  itemised diff against the earlier draft, so a reader can verify every claim
  above against the primary text rather than this summary.

---

## HOW TO USE THESE EXAMPLES

When generating output, mentally compare against these:

- **Density of equations**: Example 1 shows ~3 equations per page, each derived,
  none unmotivated. Match this density.
- **Specificity of critique**: Example 2 names the precise failed step, not "the
  argument is hand-wavy". Match this specificity.
- **Multiplicity of checks**: Example 3 runs six verification angles. Don't run
  one and call it verified.
- **External grounding**: Example 4 shows every disputed number resolved against
  a primary source (a DOI, a table in the cited paper) rather than an internal
  re-derivation alone. When a claim rests on an external fact, go check the fact.

If your draft response would not pass these standards, rewrite it before
sending to the user.
