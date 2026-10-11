# PhysicsForge — Methodological Toolkit Reference

The general-purpose techniques PhysicsForge reaches for inside the Derivation
Engine (Phase 3). These are the *moves* that turn axioms into formulae. Most
non-trivial derivations chain two or more of them.

---

## WHEN TO READ THIS FILE

Read this file when:
- Beginning any derivation in Phase 3 — pick the right method *before* writing
- The Pauli Protocol fails check [5] (dimensional) or [4] (symmetry/conservation)
- You're stuck and need a different angle on the same problem
- Auditing a paper where the authors' chosen method looks wrong for the regime
- Connecting two theories — the right method often lives at the seam between them

If a derivation isn't working, the first question is rarely "is the algebra
wrong?" — it's "am I using the right method for this regime?"

---

## METHOD SELECTION LADDER

Apply in this order before writing a single equation:

```
1. Dimensional / scaling analysis    →  bounds the answer's *form*
2. Conservation laws + symmetries    →  bounds the answer's *content*
3. Variational principle             →  bounds the answer's *trajectory*
4. Perturbation expansion            →  exact problem too hard; expand in ε
5. Group-theoretic classification    →  enumerate allowed states / couplings
6. Causality / analyticity           →  constrain response functions
7. Topology                          →  invariants survive when nothing else does
```

Each rung uses *less* dynamical detail and *more* structural reasoning. If
rungs 1–3 fully determine the answer, the dynamics were never the hard part.
This is a feature: it tells you the result is robust against modeling choices.

---

## METHOD 1 — SCALING AND SIMILARITY ANALYSIS

**Core idea.** Exploit how a system scales with characteristic parameters
(length, mass, energy, charge, time). The answer must be a function of the
dimensionless groups; everything else is fixed by dimensional necessity.

**Formal tool.** Buckingham π theorem: if a relation involves $n$ physical
quantities built from $k$ independent dimensions, it reduces to a relation
among $n - k$ dimensionless π-groups.

**Canonical examples.**
- Reynolds number $\mathrm{Re} = \rho U L / \mu$ in fluid dynamics —
  the *only* dimensionless group from $(\rho, U, L, \mu)$, so any
  drag/turbulence relation must be a function of it.
- Kolmogorov $-5/3$ spectrum: dimensional consistency of the energy cascade
  at inertial scales gives $E(k) \sim \varepsilon^{2/3} k^{-5/3}$.
- Self-similar blast wave (Taylor–Sedov): $R(t) \sim (E t^2 / \rho)^{1/5}$.

**When to use.**
- Before any detailed dynamics. Always.
- When you suspect a power-law answer.
- When the problem has a "scale-free" feel (turbulence, criticality, blackbody).

**When it fails.**
- When two dimensionless groups are present and neither dominates — you get
  the *form* but not the coefficient or which group sets the scale.
- Logarithms: dimensional analysis can hide $\log$ corrections (anomalous
  dimensions, running couplings).

**Pauli tie-in.** Required for check [5]. A failed dimensional check is
almost always a sign the wrong scaling has been used.

---

## METHOD 2 — CONSERVATION LAWS

**Core idea.** Energy, momentum, angular momentum, charge, baryon number,
lepton number, and (in suitable contexts) entropy, helicity, circulation,
or topological charge are conserved in closed systems. Use the *conservation*
to skip past the dynamics.

**Canonical examples.**
- Two-body collision: momentum and energy conservation determine outgoing
  kinematics without integrating any force law.
- Kepler problem: $E$ and $\vec L$ conserved → orbit is conic, no need to
  solve $\ddot{\vec r}$ directly.
- Hawking radiation thermodynamics: first law $dM = T \, dS_{BH} + \Omega \, dJ
  + \Phi \, dQ$ derives the temperature without quantum field theory.

**When to use.**
- Initial-vs-final state problems (you don't care what happens in between).
- Bounds: even when not conserved, slowly-varying invariants give *adiabatic*
  bounds.
- Sanity checks on numerical integrators (drift in conserved quantities = bug).

**When it fails.**
- Open / dissipative systems — but then look for *fluxes* of the conserved
  quantity at the boundary.
- Quantum anomalies: classical conservation can fail under quantization
  (chiral anomaly, conformal anomaly). Treat with care.

**Pauli tie-in.** Check [4]. List explicitly *which* laws you're invoking
and verify each one numerically on a sample point.

---

## METHOD 3 — NOETHER'S THEOREM

**Core idea.** Every continuous symmetry of the action yields a conserved
current. This *generates* the conservation laws of Method 2 from a deeper
structural fact: the symmetry of the Lagrangian.

**The map.**

| Symmetry of $S$ | Conserved quantity |
|---|---|
| Time translation | Energy |
| Spatial translation | Momentum |
| Rotation | Angular momentum |
| $U(1)$ phase | Electric charge |
| $SU(N)$ gauge | Non-abelian color/isospin currents |
| Conformal | Trace + special conformal currents |
| BRST | Cohomological charge (gauge consistency) |

**Procedure.** Given $\mathcal L(\phi, \partial \phi)$ invariant under
$\phi \to \phi + \epsilon \, \delta\phi$:

$$j^\mu = \frac{\partial \mathcal L}{\partial(\partial_\mu \phi)} \, \delta\phi
- K^\mu, \qquad \partial_\mu j^\mu = 0$$

where $K^\mu$ accounts for any total-derivative shift in $\mathcal L$.

**When to use.**
- Field theory, always — it's the only systematic way to get conserved
  currents.
- When you suspect a *new* conservation law and need to find the underlying
  symmetry.
- When constructing a new Lagrangian: design the symmetry first, the
  conservation law follows.

**When it fails.**
- Discrete symmetries don't yield Noether currents (use selection rules
  instead — see Method 8).
- Anomalous symmetries: the classical Noether current is broken by quantum
  effects. Compute the anomaly explicitly.

**Pauli tie-in.** Check [4]. If your action has a symmetry but you can't
find the corresponding conserved current, *something is wrong with the
derivation.*

---

## METHOD 4 — ORDER-OF-MAGNITUDE ESTIMATES

**Core idea.** Build the answer from fundamental constants and dominant
effects, ignoring numerical factors of order 1. The result is a *bound*
or *characteristic scale*, not a precise prediction.

**Canonical examples.**
- Free-fall time from height $L$: $t \sim \sqrt{L/g}$.
- Bohr radius: $a_0 \sim \hbar^2 / (m_e e^2)$ from balancing
  kinetic and Coulomb energy.
- Chandrasekhar mass: $M_{\mathrm{Ch}} \sim (\hbar c / G)^{3/2} / m_p^2$
  from balancing degeneracy pressure against gravity.
- Planck scale: combine $G, \hbar, c$ to get the unique mass/length/time.

**Procedure.**
1. Identify the relevant fundamental constants ($G, c, \hbar, k_B, e, m$).
2. Identify the characteristic scales of the problem ($L, T, E$).
3. Write the answer as the unique dimensionally-correct combination.
4. Sanity-check the exponent on each factor.
5. Compare numerically to known data — order-of-magnitude agreement is the
   bar.

**When to use.**
- *First*, before any detailed calculation. The estimate sets the target.
- When the full calculation is intractable.
- To bound parameters in a new theory ("if this scale isn't $\sim$ Planck,
  why?").

**When it fails.**
- Precision matters (factor of 2 changes the physics).
- Dimensionless ratios are hierarchical (e.g. $m_e / m_p \approx 1/1836$).
  Then "order 1" is a lie — track the small parameter explicitly via Method 6.

---

## METHOD 5 — VARIATIONAL PRINCIPLES

**Core idea.** The actual trajectory / field configuration extremizes a
functional (action, energy, free energy). Equations of motion follow from
$\delta S = 0$.

**Canonical examples.**
- Principle of least action: $S = \int L \, dt$ → Euler–Lagrange → Newton.
- Fermat's principle: light extremizes optical path length → Snell's law.
- General relativity: Einstein–Hilbert action $S = \frac{1}{16\pi G} \int R
  \sqrt{-g} \, d^4 x$ → Einstein field equations.
- Density functional theory: ground state minimizes the energy functional
  over electron densities.

**Why it's powerful.**
- *Symmetries* of the action are visible as transformations leaving $S$
  invariant — directly feeds Method 3.
- *Constraints* (holonomic or non-holonomic) enter via Lagrange multipliers
  with clear physical meaning (forces of constraint, gauge multipliers).
- *Approximations*: trial functions with parameters → variational bounds
  (e.g., Rayleigh–Ritz for ground states).

**When to use.**
- Whenever you want equations of motion *and* their symmetry structure
  simultaneously.
- For approximate ground states (variational method beats perturbation when
  no obvious small parameter exists).
- To enforce gauge invariance and constraints cleanly.

**When it fails.**
- Dissipative systems: no straightforward action principle (though
  variational structures exist for some — Onsager, Rayleigh dissipation).
- The functional may be unbounded below (e.g., conformal mode in Euclidean
  gravity) — extremization isn't enough; you need a saddle.

---

## METHOD 6 — PERTURBATION AND EXPANSION METHODS

**Core idea.** Replace an intractable problem $H = H_0 + \epsilon V$ with a
series in the small parameter $\epsilon$. Solve $H_0$ exactly; correct
order-by-order.

**Canonical examples.**
- Quantum mechanical perturbation theory: energy shifts $E_n^{(1)} = \langle
  n | V | n \rangle$, etc.
- Feynman diagrams in QED: expansion in the fine-structure constant
  $\alpha \approx 1/137$.
- Boundary-layer theory in fluids: matched asymptotic expansion in $1/\mathrm{Re}$.
- Cosmological perturbation theory: expansion of GR around an FRW background.

**Variants.**
- *Regular perturbation*: solution is analytic in $\epsilon$ at $\epsilon = 0$.
- *Singular perturbation*: solution changes character at $\epsilon = 0$
  (boundary layers, WKB, multiple scales).
- *Renormalization-group improvement*: resum logarithms when naive
  perturbation theory diverges at large scales.

**When to use.**
- A small dimensionless parameter exists and is *physically* small.
- The unperturbed problem is exactly solvable.
- You want systematic, controllable corrections.

**When it fails — and how to spot it.**
- *Strong coupling*: $\epsilon \not\ll 1$ in the regime of interest. Then
  use non-perturbative methods (lattice, instantons, dualities).
- *Asymptotic but divergent series*: QED is famously asymptotic. Optimal
  truncation; resum via Borel; keep only the first few terms.
- *Secular terms*: $\epsilon t$ grows large at long times → multiple-scale
  analysis or RG.

**Pauli tie-in.** Check [3]. If your perturbation parameter is hidden
("smallness" never made explicit), flag it as an assumption.

---

## METHOD 7 — CAUSALITY AND ANALYTICITY CONSTRAINTS

**Core idea.** Response functions in physical systems are causal: the
response cannot precede the stimulus. Causality in the time domain becomes
*analyticity in the upper half complex frequency plane*. This is a hard
constraint on functional form.

**Canonical examples.**
- Kramers–Kronig relations: real and imaginary parts of $\chi(\omega)$ are
  Hilbert transforms of each other. Knowing absorption fixes dispersion.
- $S$-matrix analyticity: poles ↔ bound states / resonances; cuts ↔
  thresholds. Whole bootstrap programmes are built on this.
- Forward dispersion relations: positivity of $\mathrm{Im} \, A(s)$ implies
  bounds on EFT coefficients (positivity bounds, $a$-theorem).

**Procedure for response-function problems.**
1. Identify the causal response (linear, time-translation invariant).
2. Fourier transform → $\chi(\omega)$ analytic in upper half plane.
3. Apply Cauchy's theorem on a contour closed in the upper half plane.
4. Read off the integral relation between Re and Im parts.

**When to use.**
- Linear response in any field (optics, condensed matter, quantum scattering).
- Effective field theory: positivity / unitarity bounds on Wilson coefficients.
- Whenever the question is "what *can't* this function look like?"

**When it fails.**
- Non-linear response: superposition fails, Kramers–Kronig doesn't apply
  directly.
- Non-causal effective theories (acausal regulators, advanced Green's
  functions) — physical only as intermediate steps.

---

## METHOD 8 — GROUP THEORY AND REPRESENTATION THEORY

**Core idea.** Symmetries form groups. Physical states transform in
*representations* of those groups. Selection rules, allowed couplings, and
multiplet structure all follow from representation theory.

**Canonical examples.**
- Spherical harmonics: irreducible reps of $SO(3)$ → $\ell, m$ quantum
  numbers, $|\Delta \ell| = 0, 1$ selection rules.
- Hadron multiplets: $SU(3)_{\text{flavor}}$ classification — octets,
  decuplets, singlets predicted the $\Omega^-$.
- Crystal field splittings: point-group reps of the local symmetry partition
  degenerate atomic levels.
- Standard Model gauge structure: $SU(3) \times SU(2) \times U(1)$ — every
  particle is labeled by its rep.

**Operational outputs.**
- *Selection rules*: which matrix elements vanish by symmetry alone.
- *Multiplet content*: how an irrep of $G$ decomposes under a subgroup
  $H \subset G$ (branching rules).
- *Invariant tensors*: what couplings are allowed in a Lagrangian.
- *Casimirs*: labels for irreducible representations (mass formulae,
  GMOR-type relations).

**When to use.**
- Whenever a symmetry is present and exact (or nearly so).
- Classifying particle content of a new theory before doing dynamics.
- Computing matrix elements in atomic/molecular/nuclear physics.

**When it fails.**
- Spontaneously broken symmetries: the group structure is hidden, but reveals
  itself in Goldstone modes — handle via the coset $G/H$ and effective
  Lagrangians.
- Approximate symmetries: useful as organizing principles; corrections must
  be tracked.

---

## METHOD 9 — TOPOLOGICAL AND GEOMETRICAL CONSTRAINTS

**Core idea.** Some quantities are invariant under continuous deformations.
They cannot change unless the system passes through a singularity. This makes
them *robust* — and quantized.

**Canonical examples.**
- Quantized magnetic flux in superconductors: $\Phi = n \cdot h/(2e)$ from
  single-valuedness of the order parameter.
- Integer quantum Hall effect: $\sigma_{xy} = n \, e^2/h$ where $n$ is the
  Chern number of the filled bands.
- Berry phase: holonomy of the parameter-space connection — geometric, not
  dynamical.
- Index theorems (Atiyah–Singer): analytic indices of differential operators
  equal topological invariants of the underlying manifold.
- 't Hooft–Polyakov monopole: topological charge $\pi_2(G/H)$ of the vacuum
  manifold.

**Operational outputs.**
- *Quantization* without quantum mechanics — purely geometric.
- *Robustness* — small perturbations cannot lift a topological gap.
- *Anomalies* via index theorems: the chiral anomaly is the index of the
  Dirac operator in a background gauge field.
- *Classification* of phases of matter (topological insulators, SPT phases)
  by homotopy / cohomology of the parameter space.

**When to use.**
- Whenever a quantity appears strictly quantized in experiment with no
  obvious dynamical reason.
- Defects, vortices, solitons, instantons — all topological in origin.
- When perturbation theory is blind to a phenomenon (instanton effects,
  $\theta$-vacua).

**When it fails.**
- Topology classifies; it does not give energies. Dynamics still required
  for spectra, transition rates, etc.
- Topological invariants can change at phase transitions — track the gap.

---

## CHAINING METHODS — THE TYPICAL PATTERN

A real derivation rarely uses one method in isolation. Common chains:

**Pattern A — "What can the answer look like?"**
1. Dimensional analysis (Method 1) → functional form up to a dimensionless function.
2. Symmetry / group theory (Methods 2, 3, 8) → constrain that function.
3. Limiting cases (Method 4) → fix overall coefficient.
4. Verification (`verification.md`) → numerical check at sample point.

**Pattern B — "How do I solve this nearly-soluble problem?"**
1. Variational principle (Method 5) → write the action.
2. Symmetries (Method 3) → identify conserved currents.
3. Perturbation expansion (Method 6) → expand around the solvable limit.
4. Causality (Method 7) → check response functions are physical.

**Pattern C — "Why is this quantity exactly fixed?"**
1. Look for topological origin (Method 9).
2. If none, look for symmetry-protected origin (Methods 3, 8).
3. If none, look for analyticity / unitarity origin (Method 7).
4. If still none, the quantization is dynamical and needs detailed work.

**Pattern D — "I want to write a new Lagrangian."**
1. Choose the symmetry group (Method 8).
2. Enumerate invariant operators of the right dimension (Methods 1, 8).
3. Verify Noether currents come out right (Method 3).
4. Check causality / unitarity / positivity bounds (Method 7).
5. Identify topological terms ($\theta$-terms, Wess–Zumino) (Method 9).

---

## METHOD-METHOD CONSISTENCY CHECKS

Different methods applied to the same problem must agree. When they don't,
*one of them is being misapplied* — find the error before continuing.

| If methods disagree | Likely diagnosis |
|---|---|
| Scaling vs perturbation | Hidden log / anomalous dimension; or expansion is asymptotic |
| Conservation vs Noether | Anomaly — quantum breaking of classical symmetry |
| Topology vs dynamics | Nothing wrong; topology bounds, dynamics fills in |
| Causality vs perturbation | Series is divergent or non-Borel-summable |
| Group theory vs experiment | Symmetry is approximate, not exact |

A genuine mismatch is a *physics result*, not a bug. Document it carefully —
this is where new physics tends to live.

---

## WHEN NONE OF THESE WORK

If all nine methods fail to make progress, the problem is likely:
- A genuinely non-perturbative regime (strong coupling, no small parameter).
- A foundational gap (definitions are inconsistent — Conceptual gap).
- Genuinely open (Millennium-class — invoke that protocol, don't fake a proof).

In that case, the deliverable is a precise statement of *which methods fail
and why* — that is itself a research contribution. Do not paper over the
failure with hand-waving.
