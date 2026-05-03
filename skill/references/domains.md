# PhysicsForge — Domain-Specific Research Guidance

Read the relevant section(s) when working in a specific domain.

## TABLE OF CONTENTS

1. Fundamental Physics (QFT, GR, Quantum Gravity, Standard Model)
2. Quantum Mechanics & Quantum Information
3. Thermodynamics & Statistical Mechanics
4. Cosmology & Astrophysics
5. Condensed Matter & Emergent Phenomena
6. PDE Theory & Harmonic Analysis ← *NEW*
7. Geometric Analysis ← *NEW*
8. Stochastic Analysis & SPDE ← *NEW*
9. Numerical & Computational Methods ← *NEW*
10. Mathematical Physics Toolkit
11. Cross-Domain Connections

---

## 1. FUNDAMENTAL PHYSICS

### Quantum Field Theory
Key open gaps to explore:
- Non-perturbative effects invisible to Feynman diagrams (instantons, solitons, sphalerons)
- The cosmological constant problem — 120 orders of magnitude discrepancy
- Anomaly cancellation mechanisms beyond the Standard Model
- The Haag-Kastler axioms — mathematical foundations still incomplete
- IR/UV mixing in non-commutative field theories
- Resurgence and trans-series — beyond perturbation theory

Key mathematical tools:
- Path integral formulation, steepest descent / saddle-point approximation
- BRST cohomology for gauge theories
- Renormalization group (Wilsonian, exact RG, holographic RG)
- Operator product expansion, conformal bootstrap
- Lattice regularization

Key references: Weinberg QFT Vol 1-3, Peskin-Schroeder, Zinn-Justin, Polchinski, Coleman.

### General Relativity
Key open gaps:
- Singularity theorems — what replaces the singularity physically?
- The Cauchy horizon instability — is cosmic censorship provable?
- Exact solutions beyond Kerr — rotating charged black holes in matter
- Backreaction of quantum fields on spacetime geometry
- Initial value problem with quantum matter

Key mathematical tools:
- Penrose-Carter conformal diagrams
- Newman-Penrose formalism (spinors in curved spacetime)
- Arnowitt-Deser-Misner (ADM) decomposition
- Raychaudhuri equation and focusing theorem
- Geroch group (infinite-dimensional symmetry of vacuum GR)

### Quantum Gravity
Key open gaps:
- The problem of time — Hamiltonian constraint and frozen formalism
- Background independence vs. semiclassical limit
- Black hole information paradox — unitary evolution vs. Hawking radiation
- Trans-Planckian problem in inflation
- Emergent spacetime — from what does geometry emerge?

Key mathematical tools:
- Wheeler-DeWitt equation
- Spin networks and spin foams (LQG)
- Regge calculus and simplicial gravity
- Causal sets and discrete causal structure
- Holography — Ryu-Takayanagi, island formula

### Standard Model & Beyond
Key open gaps:
- Hierarchy problem — why is M_Higgs ≪ M_Pl without fine-tuning?
- Strong CP problem — why is θ_QCD < 10⁻¹⁰?
- Neutrino mass mechanism — Dirac vs. Majorana, seesaw
- Matter-antimatter asymmetry
- LHCb anomalies in B-meson decays
- Muon g-2 anomaly

---

## 2. QUANTUM MECHANICS & QUANTUM INFORMATION

### Foundations
Key open gaps:
- Measurement problem — no consensus after 100 years
- Emergence of classicality — when does decoherence suffice?
- Wigner's friend / Frauchiger-Renner
- Quantum-to-classical transition at mesoscopic scales
- Time in quantum mechanics — Page-Wootters mechanism

### Entanglement & Holography
- ER = EPR (Maldacena-Susskind): entanglement creates wormholes
- Quantum error correction in bulk reconstruction (HaPPY code, tensor networks)
- Entanglement entropy and Ryu-Takayanagi: `S = A/(4G_N)`
- Page curve and island formula

These provide a fertile `[UNIFICATION GAP]` between quantum information and gravity.

---

## 3. THERMODYNAMICS & STATISTICAL MECHANICS

### Arrow of Time
All fundamental laws are time-reversal symmetric. Macroscopic irreversibility must
emerge from initial conditions (Past Hypothesis). But why was the early universe in
an extremely low-entropy state?

- Penrose's Weyl Curvature Hypothesis — entropy of gravity
- Fluctuation theorems: Jarzynski equality `⟨e^{-βW}⟩ = e^{-βΔF}`
- Crooks fluctuation theorem
- Landauer's principle — erasure costs `k_B T ln 2`

### Black Hole Thermodynamics
- 0th: surface gravity κ constant on horizon
- 1st: `dM = κ/(8π) dA + ΩdJ + ΦdQ`
- 2nd: `dA ≥ 0` classically (Hawking area theorem)
- 3rd: cannot reach κ = 0 by finite processes

The 2nd law fails quantum mechanically (Hawking radiation reduces A).
Generalized second law: `d(S_BH + S_outside)/dt ≥ 0`.

---

## 4. COSMOLOGY & ASTROPHYSICS

### Dark Matter
- DAMA/LIBRA annual modulation (unconfirmed)
- Bullet Cluster — strong evidence for collisionless DM
- Small-scale structure problems
- JWST early massive galaxy problem — challenges ΛCDM

Beyond WIMPs:
- Fuzzy dark matter: `m ~ 10⁻²² eV`
- Primordial black holes
- Self-interacting dark matter
- MOND and TeVeS

### Inflation
- Trans-Planckian problem
- Eternal inflation and the measure problem
- Initial conditions for inflation
- Primordial gravitational waves: `r = T/S` upper bound from Planck/BICEP

---

## 5. CONDENSED MATTER & EMERGENT PHENOMENA

### Topological Phases
- Chern-Simons theory in 3D topological insulators and QFT
- Anyons in 2+1D — fractional statistics
- Non-Abelian anyons (Majorana modes) = topological qubits
- TQFT — Witten's Jones polynomial work

### High-Tc Superconductivity
Still unsolved after 40 years:
- Mechanism of Cooper pairing in cuprates
- Pseudogap phase — what is the order parameter?
- Strange metal phase: ρ ~ T (not T²)
- AdS/CFT applied to strange metals

### Universality and Emergence
Why do completely different systems obey the same equations?
- Ising model critical exponents in liquid-gas, magnets, neural networks
- KPZ equation in wildly different physical systems

---

## 6. PDE THEORY & HARMONIC ANALYSIS *(NEW)*

The toolkit for fluid dynamics, dispersive equations, geometric flows, and the
analytic side of mathematical physics.

### Function Spaces
| Space | Used for |
|---|---|
| L^p (Lebesgue) | Energy estimates, basic integrability |
| W^{k,p} (Sobolev) | Weak derivatives, embedding theorems |
| H^s (fractional Sobolev) | Critical exponents, scaling |
| C^{k,α} (Hölder) | Pointwise smoothness, Schauder estimates |
| BMO (bounded mean oscillation) | Endpoint of Calderón-Zygmund theory |
| Besov B^s_{p,q} | Refined regularity, paraproducts |
| Triebel-Lizorkin F^s_{p,q} | Most general scale of function spaces |

### Key Inequalities (every PDE paper uses these)
- **Hölder**: `‖fg‖_{L^r} ≤ ‖f‖_{L^p} ‖g‖_{L^q}`, `1/r = 1/p + 1/q`
- **Sobolev embedding**: `H^s ↪ L^p` for `1/p = 1/2 − s/n` (when valid)
- **Gagliardo-Nirenberg**: interpolation between L^p and H^s
- **Hardy-Littlewood-Sobolev**: `I_α: L^p → L^q`, `1/q = 1/p − α/n`
- **Calderón-Zygmund**: singular integral operators bounded on L^p (1<p<∞)
- **Strichartz**: space-time estimates for dispersive equations
- **Bernstein**: frequency localization estimates

### Critical / Subcritical / Supercritical Scaling
For an equation with scaling `u_λ(x,t) = λ^a u(λx, λ^b t)`:
- Subcritical: norm decreases under scaling — global existence usually provable
- Critical: norm invariant under scaling — borderline
- Supercritical: norm grows under scaling — global regularity often open

For 3D Navier-Stokes: H^{1/2} is critical. Energy E ∈ L²_t H¹_x is supercritical.

### Paradifferential Calculus
Decompose product `fg = T_f g + T_g f + R(f,g)` (Bony):
- Low-high frequency products easy
- High-high products contained in remainder R
- Basic tool in modern wave/Schrödinger equation theory

### Open problems in PDE
- 3D Navier-Stokes regularity (Clay)
- Onsager conjecture for Euler (resolved 2018 by Isett)
- Generic singularities in mean curvature flow
- Black hole stability for Kerr (partial progress: De Giorgi-Klainerman-Szeftel)
- Pointwise convergence of Schrödinger semigroups (Carleson problem, partially resolved)

### Key references
Stein "Singular Integrals", Tao "Nonlinear Dispersive Equations",
Bahouri-Chemin-Danchin "Fourier Analysis and Nonlinear PDE",
Klainerman-Christodoulou "Global Nonlinear Stability of Minkowski".

---

## 7. GEOMETRIC ANALYSIS *(NEW)*

The interface between PDE theory and Riemannian geometry.

### Geometric Flows
- **Ricci flow**: `∂_t g = −2 Ric(g)` — used in Poincaré conjecture proof
- **Ricci-DeTurck flow**: gauge-fixed Ricci, strictly parabolic
- **Mean curvature flow**: `∂_t F = H ν` — minimal surface formation
- **Yamabe flow**: scalar curvature flow
- **Inverse mean curvature flow**: used in Penrose inequality

### Monotonicity Formulas
The fundamental tool for proving regularity / non-blowup:
- Huisken's formula for mean curvature flow
- Perelman's W-functional for Ricci flow (the breakthrough)
- Ecker-Huisken for harmonic map heat flow
- The Gaussian density / "shrinker" approach

### Key tools
- Bochner formula (commutator of Δ and ∇)
- Weitzenböck formula (curvature corrections)
- De Giorgi-Nash-Moser iteration (Hölder regularity)
- Krylov-Safonov (parabolic Harnack)
- Caffarelli-Silvestre extension (fractional Laplacian = local PDE in higher dim)

### Open problems
- Singularity classification in Ricci flow beyond 3D
- Generic mean curvature flow singularities (Schoen-Wolfson conjecture)
- Min-max minimal surfaces in arbitrary manifolds
- Yau's conjecture on infinitely many minimal surfaces (resolved 2018 by Song)

### Key references
Hamilton, Perelman papers, Huisken-Polden, Tao-Topping notes,
Colding-Minicozzi "A Course in Minimal Surfaces".

---

## 8. STOCHASTIC ANALYSIS & SPDE *(NEW)*

Random PDE — relevant to turbulence, statistical field theory, growth processes,
and conformal field theory via SLE.

### Brownian motion & SDE
- Itô calculus: `df = ∂_t f dt + ∂_x f dB + (1/2) ∂_xx f dt`
- Stratonovich vs. Itô conventions (sign / drift differences)
- Existence/uniqueness via Picard iteration with Itô isometry

### Stochastic PDE
- KPZ equation: `∂_t h = ∂_xx h + (∂_x h)² + ξ` where ξ = white noise
  - Hairer's regularity structures (2014 Fields medal)
  - Universality across many growth processes
- Stochastic Navier-Stokes: forced or with multiplicative noise
- Stochastic quantization (Parisi-Wu): `∂_t φ = −δS/δφ + ξ`
- Φ⁴_3 model — constructed via regularity structures / paracontrolled distributions

### Key constructs
- Schramm-Loewner Evolution (SLE_κ) — conformally invariant random curves
- Random matrices and Tracy-Widom distribution
- Liouville quantum gravity (LQG) and KPZ relation

### Open problems
- Rigorous Yang-Mills measure construction in 4D (Clay)
- Φ⁴_4 — non-existence, non-trivial massless scaling limit?
- Universality of fluid turbulence under stochastic forcing

### Key references
Hairer "Regularity structures",
Da Prato-Zabczyk "Stochastic Equations in Infinite Dimensions",
Werner "SLE notes", Sheffield "GFF and LQG".

---

## 9. NUMERICAL & COMPUTATIONAL METHODS *(NEW)*

When analytical methods stall, computation provides evidence and counterexamples.

### Numerical evidence for / against conjectures
- DNS of turbulence (Ishihara et al., Buaria et al.) — for Navier-Stokes
- Lattice QCD — for confinement, mass gap, hadron spectrum
- Monte Carlo for statistical models — critical exponents to high precision
- Bootstrap methods — conformal field theory, S-matrix bootstrap

### When to invoke numerics in a paper
- To support a [CONJECTURE] with [NUMERICAL] evidence
- To rule out a candidate counterexample
- To estimate a constant in an inequality
- To check a derived formula against direct simulation

### Tools
- `numpy / scipy` — general-purpose
- `sympy` — symbolic verification (see verification.md)
- `dedalus` — spectral PDE solver
- `firedrake / FEniCS` — finite element
- `jax` — autodiff for inverse problems and physics-informed networks
- `julia DifferentialEquations.jl` — high-performance ODE/SDE/DAE

### Limits of computation
- Cannot prove existence/uniqueness rigorously (only support conjectures)
- Discretization always introduces some error
- Long-time integration accumulates numerical dissipation
- Stochastic methods give only statistical confidence

### Computer-assisted proofs
A respectable category in modern math:
- Hales' proof of Kepler conjecture (formal verification 2014)
- Helfgott's proof of ternary Goldbach
- Interval arithmetic for chaotic ODE (Lorenz attractor existence: Tucker)

For PhysicsForge purposes: numerical evidence is `[NUMERICAL]`-tagged, never
labeled as proof unless it's a formally verified computer-assisted proof.

---

## 10. MATHEMATICAL PHYSICS TOOLKIT

### When to reach for each tool

| Problem type | Mathematical tool |
|---|---|
| Symmetries and conservation laws | Lie groups, Noether's theorem |
| Gauge theories | Fiber bundles, connections, curvature |
| Topological invariants | Characteristic classes, index theorems |
| Quantum anomalies | BRST cohomology, descent equations |
| Integrable systems | Lax pairs, inverse scattering, r-matrices |
| String amplitudes | Modular forms, L-functions |
| Quantum geometry | Noncommutative geometry, spectral triples |
| Twistor methods | Penrose transform, twistor string theory |
| Higher categories | ∞-categories, derived geometry |
| Exceptional structures | G₂, F₄, E₆, E₇, E₈ and octonions |
| Singular integrals | Calderón-Zygmund, T(1) theorem |
| Random geometry | SLE, LQG, GFF |

### Atiyah-Singer Index Theorem
`index(D) = ∫_M ch(E) ∧ Â(M)`

Used in: anomaly cancellation in string theory, Dirac operator spectrum in LQG,
topological phases in condensed matter.
Worth deploying whenever anomalies, zero modes, or topological invariants appear.

### Exceptional Lie Groups
- G₂: holonomy of 7-manifolds in M-theory compactifications
- F₄: symmetry of Jordan algebra of 3×3 octonionic matrices
- E₆, E₇, E₈: GUT, heterotic string E₈×E₈
- Octonions: appear in triality of SO(8)

Conspicuously underused in quantum gravity — productive gap.

---

## 11. CROSS-DOMAIN CONNECTIONS

| Domain A | Domain B | The bridge |
|---|---|---|
| Black hole thermodynamics | Quantum information | ER=EPR, holographic entropy |
| Topological insulators | QFT anomalies | Bulk-boundary correspondence |
| Statistical mechanics | QFT | Euclidean path integral ↔ partition function |
| Knot theory | Chern-Simons theory | Jones polynomial from physics |
| Number theory | String theory | Modular forms, L-functions, moonshine |
| Fluid dynamics | GR | Membrane paradigm, black hole viscosity |
| Quantum chaos | Black holes | Fast scrambling, OTOCs, SYK |
| Neural networks | Holography | Information-theoretic tensor networks |
| Random matrices | Quantum chaos | Wigner-Dyson, SYK |
| Random PDE | CFT | SLE_κ, Liouville quantum gravity |
| Geometric flow | Topology | Ricci flow → Poincaré conjecture |
| Mean curvature flow | Singularity formation | Type-I vs Type-II singularities |
| Fluid mechanics | Geometric measure theory | Onsager conjecture, weak solutions |
| Optimal transport | Ricci curvature | Lott-Sturm-Villani synthetic Ricci |
| Lagrangian mean curvature | Calabi-Yau geometry | Special Lagrangians, mirror symmetry |

These bridges are productive search areas for `[UNIFICATION GAP]` work.
