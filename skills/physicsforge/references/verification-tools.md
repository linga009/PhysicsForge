# PhysicsForge verification tools (`pfv`)

Executable checks for mathematics and physics: number theory, group theory, linear and polynomial algebra, analysis,
inequalities, probability, combinatorics, Lie algebras and anomalies, quantum information, GR and gauge theory, mechanics
and thermodynamics, vector calculus, QFT gamma-matrix algebra, dimensional analysis, derivation chains. Use them to try to
**break** a claim before relying on it. They check the statement you give them; they do not choose the statement for you.

## Use

```python
import sys; sys.path.insert(0, "${CLAUDE_PLUGIN_ROOT}/scripts")   # plugin install; in a clone use <repo>/scripts
from pfv import numtheory, groups, lie, algebra, smt              # any domain: pfv.DOMAINS lists all 16
from pfv.core import report
```

- Menu of every check and its arguments: `python -m pfv list` (or `list <domain>`), run from `scripts/`.
- Full docstring of one check: `python -m pfv doc check_isomorphic`.
- The toolkit's own regression suite (planted errors, about 3 minutes): `python -m pfv selftest`.
- Needs `sympy`, `numpy`, `scipy`; `smt` also needs `z3-solver` (without it those checks return INCONCLUSIVE with an
  install hint). `pip install -r scripts/requirements.txt` installs everything.
- Works on Windows: reports fall back to ASCII on a console that cannot print `═ ✓ ✗`, and check timeouts fire there
  too (a timer thread interrupts the main thread instead of SIGALRM).

## The loop: prove or disprove

1. Write the claim as a universal statement and say what would falsify it.
2. **Refute first.** Run the cheapest counterexample hunt (`find_counterexample`, `hunt_*`, or a `check_*` on a small case).
   One REFUTED settles the question. Surviving a hunt does not prove anything.
3. **Then prove**, using a check that can return VERIFIED (symbolic identity, exhaustive table, decision procedure).
4. Put `report([...], "target")` into the answer verbatim. Its "Not proven:" line must stay.
5. Map verdicts to the claim hierarchy: VERIFIED supports Theorem/Proposition for exactly the statement checked;
   CONSISTENT supports only Observation / `[NUMERICAL]`; INCONCLUSIVE is reported as such; REFUTED means fix or drop the claim.

## Verdicts (the only four values)

| Verdict | Meaning | Decisive? |
|---|---|---|
| REFUTED | A concrete witness, re-checked exactly (or labelled floating-point or statistical in `evidence`) | yes |
| VERIFIED | Exact symbolic identity, exhaustive check of a finite claim, or a complete decision procedure | yes |
| CONSISTENT | Passed the sample, range or tolerance named in `evidence`. Not a proof | no |
| INCONCLUSIVE | Unsupported input, timeout, unknown symbol, solver said unknown. Say so; never guess | no |

A typo, an unknown symbol or a wrong coordinate name is INCONCLUSIVE, never REFUTED.

## Which check answers which question: mathematics

| Question | Check |
|---|---|
| Is this universal statement over the integers true? | `numtheory.find_counterexample` (finite range gives CONSISTENT unless `complete=True`) |
| Prime? Factorisation right? | `certify_prime` (certificate), `check_factorization` |
| Congruence, CRT, orders, Legendre/Jacobi symbols, lifting the exponent | `check_congruence`, `check_crt`, `check_order_claim`, `check_symbol_claims`, `check_lte` |
| Any integer solutions? Local obstruction? | `diophantine_search`, `modular_obstruction`, `check_pell`, `check_two_squares`, `smt.check_no_integer_solutions` |
| Elliptic-curve point count, Hasse bound | `check_hasse` (needs prime p > 3) |
| Is this multiplication table a group? Subgroup, normal subgroup, homomorphism? | `groups.check_group_axioms`, `check_subgroup`, `check_normal`, `check_homomorphism` |
| Are two groups isomorphic? | `check_isomorphic` (invariants refute, an explicit map verifies) |
| How many abelian groups of order n? Sylow counts? Is a group of order n simple? | `check_abelian_count`, `check_sylow_count`, `simplicity_by_sylow` (can refute simplicity; cannot prove it) |
| Character table, Burnside orbit counting | `check_character_table`, `check_burnside`, `necklace_count` |
| Exact rank, determinant, eigenvalues, definiteness, Cayley-Hamilton | `linalg.check_rank`, `check_determinant`, `check_eigenvalues_exact`, `check_positive_definite`, `check_cayley_hamilton` |
| Polynomial identity, factorisation, irreducibility mod p | `algebra.check_polynomial_identity`, `check_factorization_poly`, `check_irreducible` |
| Nested radicals, minimal polynomial of an algebraic number | `check_algebraic_identity`, `check_minimal_polynomial` |
| Real root count, discriminant, polynomial systems, ideal membership | `check_real_root_count`, `check_discriminant`, `check_system_solutions`, `check_ideal_membership` |
| Identity, derivative, antiderivative, limit, series | `analysis.check_identity`, `check_derivative`, `check_antiderivative`, `check_limit`, `check_series` |
| Integral or sum with a claimed value; does a series converge? | `check_integral` (singularities split, principal value rejected), `check_sum`, `check_convergence` |
| Polynomial or rational inequality, with side conditions | `smt.check_real_claim` (complete decision procedure; counterexample or proof), `analysis.check_inequality` |
| ODE or PDE solution, harmonic or analytic function, residue, Fourier pair | `check_solves`, `check_harmonic`, `check_analytic`, `check_residue`, `check_fourier_pair` |
| Is each step of this derivation valid? Lost or extraneous roots? | `derivation.check_chain`, `check_equation_chain`, `check_candidates` |
| Counting formula, sequence, generating function, recurrence, spanning trees, chromatic number | `combinat.check_count_formula`, `check_known_sequence`, `check_generating_function`, `check_recurrence`, `check_spanning_trees`, `check_chromatic_number` |
| Probability, conditional probability, expectation (finite space) | `probability.check_probability`, `check_conditional`, `check_expectation` |
| Density, Markov chain | `check_pdf`, `check_stochastic_matrix`, `check_stationary` |
| Propositional logic | `smt.check_tautology`, `check_logical_equivalence` |

## Which check answers which question: physics

| Question | Check |
|---|---|
| Dimensions of both sides, natural units, number of dimensionless groups | `dimensions.check_dimensions`, `check_expected_dimension`, `check_pi_count` |
| Spin algebra, Pauli algebra, Hermitian, unitary, density matrix | `quantum.check_angular_momentum_algebra`, `check_pauli_algebra`, `check_hermitian`, `check_unitary`, `check_density_matrix` |
| Is this map a valid channel? Lindblad generator? Entangled? Uncertainty relation? | `check_channel`, `check_lindblad_generator`, `check_entangled`, `check_uncertainty` |
| Entanglement entropy of a bipartite pure state (bits) | `quantum.check_entanglement_entropy` (flags a mixed global state: then it is only the marginal's entropy) |
| Is this inequality true for all states? | `quantum.hunt_state_counterexample` (hunt; a pass is CONSISTENT) |
| Lie algebra closure, Casimir, irrep dimension (A to G) | `lie.check_lie_algebra`, `check_casimir_sum_rule`, `check_irrep_dimension`, `check_decomposition` |
| Anomaly cancellation, SU(N) cubic coefficient, beta coefficients | `check_anomaly_free`, `check_su_cubic`, `sm_beta_coefficients` |
| Is this metric a vacuum solution? Curvature invariant? Killing vector? | `geometry.check_vacuum_solution`, `check_curvature_invariant`, `check_killing`, `check_riemann_symmetries` |
| Gauge invariance, Maxwell from a potential, Yang-Mills Bianchi | `check_abelian_gauge_invariance`, `check_maxwell_from_potential`, `check_yang_mills_bianchi` |
| Equations of motion, canonical map, Poisson bracket, conserved quantity | `mechanics.check_eom`, `check_canonical`, `check_poisson`, `check_conserved_on_shell`, `check_conserved_numeric` |
| Thermodynamic potential (extensivity, Euler relation, concavity) | `check_homogeneous`, `check_euler_relation`, `check_equation_of_state`, `check_concavity` |
| Kramers-Kronig pair | `check_kramers_kronig` |
| grad, div, curl, Laplacian in cylindrical or spherical coordinates | `vectorcalc.check_grad`, `check_div`, `check_curl`, `check_laplacian` |
| Vector identity valid for all fields; flux; line integral; Gauss | `check_vector_identity`, `check_flux_sphere`, `check_line_integral`, `check_divergence_theorem_box` |
| Dirac matrices, trace and contraction identities, Lorentz generators | `qft.check_clifford`, `check_gamma_identity`, `check_lorentz_generators` |
| Ward identity of an amplitude | `qft.check_ward_identity` |

Also available: `numtheory.check_claimed_value`, `check_arithmetic_identity`, `check_multiplicative`, `check_wilson_fermat`,
`check_lucas_binomial`; `groups.check_cyclic`, `check_element_order`, `check_class_equation`, `check_burnside_lemma_on_table`;
`linalg.check_diagonalizable`, `check_expm_identity`, `hunt_matrix_counterexample`; `analysis.check_contour_circle`;
`combinat.check_binomial_identity`; `derivation.check_final_answer`; `geometry.check_metric`, `check_contracted_bianchi`,
`check_covariant_conservation`; `mechanics.check_conserved_hamiltonian`; `quantum.check_perturbative_shift`,
`check_trace_obstruction`; `vectorcalc.check_solenoidal`, `check_irrotational`, `check_potential`, `check_vector_potential`.

## Pitfalls the tools guard against, and ones that stay with you

- A finite range is not a proof. `n*n+n+41` is prime for n = 0..39 and fails at 40. A pass over a range is CONSISTENT.
- Principal value is not the integral (`1/x` on [-1,1] diverges). Abel or zeta values are not series sums (1+2+3+... is not -1/12).
  Conditionally convergent series are INCONCLUSIVE for absolute-convergence questions.
- Sylow counting can show a group of a given order is not simple; it cannot show that a particular group is simple.
- Conventions change signs. State yours: Casimir sum rule `dim(R) C2(R) = dim(G) T(R)`; thermodynamic Euler relation
  `U = TS - pV + mu N`; sign of `eps^{0123}` (the QFT checks take `eps0123`); Cartan matrix convention for G2.
- `z3` checks add the side conditions "denominator is nonzero" and "square-root argument is nonnegative". A VERIFIED result then holds on that domain, and the evidence says so.
- **Floats are never snapped.** A Python float or sympy Float is read exactly as written: `0.3333333333` is
  3333333333/10^10, not 1/3. (Earlier versions snapped it with `nsimplify`, and a false claim could come back VERIFIED.)
  - A claimed value given as a float: exact equality is VERIFIED, agreement within 1e-9 is CONSISTENT ("approximation,
    not the exact value"), a larger gap is REFUTED. So `0.1666666666` for P = 1/6 is CONSISTENT; `0.17` is REFUTED.
  - Input data given as floats (matrix entries, constants in a `smt` claim) can reach CONSISTENT at most: a proof about
    approximate numbers is not a proof about the exact values they stand for. A REFUTED witness is kept, with a caveat
    that it holds for the decimals as written.
  - Strings are what you typed: `"1/3"` and `"0.5"` are exact. Pass exact values as strings, `Fraction`s or sympy
    `Rational`s whenever the claim is exact.
- Expression strings in `qft.check_gamma_identity` and `vectorcalc.check_vector_identity` are evaluated as Python. Do not pass untrusted text.
- A VERIFIED result says the statement you typed is true. Check that it is the statement you meant.

## Examples (these run as written)

```python
import sympy as sp
from pfv import numtheory as nt, groups as gr, lie, smt
from pfv.core import report

# 1. A famous false pattern: refuted by one witness.
r1 = nt.find_counterexample(lambda n: sp.isprime(n * n + n + 41), range(0, 100), claim="n^2+n+41 is prime for all n >= 0")

# 2. Two groups of order 8 that are NOT isomorphic: Z2 x Z4 versus the dihedral group of the square.
r2 = gr.check_isomorphic(gr.direct_product(gr.cyclic(2), gr.cyclic(4)), gr.dihedral(4))

# 3. Exact anomaly cancellation for one Standard Model generation.
r3 = lie.check_anomaly_free(lie.STANDARD_MODEL_GEN, "Standard Model, one generation")

# 4. A complete proof of an inequality with side conditions (Nesbitt), and a refutation of a slightly wrong version.
r4 = smt.check_real_claim("a/(b+c)+b/(c+a)+c/(a+b) >= 3/2", ["a>0", "b>0", "c>0"])
r5 = smt.check_real_claim("a/(b+c)+b/(c+a)+c/(a+b) >= 151/100", ["a>0", "b>0", "c>0"])

assert [r.verdict for r in (r1, r2, r3, r4, r5)] == ["REFUTED", "REFUTED", "VERIFIED", "VERIFIED", "REFUTED"]
print(report([r1, r2, r3, r4, r5], "five claims"))
```

```python
from pfv import qft, vectorcalc as vc, algebra as al

# Contraction identity in four dimensions, proved for ALL vectors (symbolic components), and the same identity with a planted wrong sign.
good = qft.check_gamma_identity("sum(gu(m)*slash(p)*gl(m) for m in range(4))", "-2*slash(p)", vectors=("p",))
bad = qft.check_gamma_identity("sum(gu(m)*slash(p)*gl(m) for m in range(4))", "2*slash(p)", vectors=("p",))

# curl(A x B) for ALL smooth fields, and the version with the two advection terms swapped.
v1 = vc.check_vector_identity("curl(cross(A,B))", "A*div(B) - B*div(A) + adv(B,A) - adv(A,B)", vectors=("A", "B"))
v2 = vc.check_vector_identity("curl(cross(A,B))", "A*div(B) - B*div(A) + adv(A,B) - adv(B,A)", vectors=("A", "B"))

# The minimal polynomial of sqrt(2)+sqrt(3), and a polynomial that vanishes there but is not minimal.
m1 = al.check_minimal_polynomial("sqrt(2)+sqrt(3)", "x**4-10*x**2+1")
m2 = al.check_minimal_polynomial("sqrt(2)", "x**4-4")

assert [r.verdict for r in (good, bad, v1, v2, m1, m2)] == ["VERIFIED", "REFUTED", "VERIFIED", "REFUTED", "VERIFIED", "REFUTED"]
```

```python
from fractions import Fraction
from pfv import probability as pb, linalg as la

# Floats are read exactly as written, never snapped to a "nice" rational.
die = range(1, 7)
exact = pb.check_probability(die, lambda o: o == 1, Fraction(1, 6))      # exact claim, exact truth
approx = pb.check_probability(die, lambda o: o == 1, 0.1666666666)       # a decimal approximation of 1/6
wrong = pb.check_probability(die, lambda o: o == 1, 0.17)                # not 1/6 at any reasonable precision
rank = la.check_rank([[1, 0.3333333333], [3, 1]], 1)                     # det is 1e-10 for these decimals: rank 2

assert [r.verdict for r in (exact, approx, wrong, rank)] == ["VERIFIED", "CONSISTENT", "REFUTED", "REFUTED"]
```

## What this does not do

It does not find the right statement, understand a physical model, or replace a written proof. It does not give you a Lean
or Coq certificate (z3's "unsat" is trusted, not independently certified). It cannot decide undecidable questions: general
Diophantine equations and descent arguments come back INCONCLUSIVE, which is the correct answer. On its own regression
corpus the checks never return VERIFIED for a planted-false claim, but that corpus was written by the same author as the
checks; treat the tools as a strong filter for algebra and finite-structure errors, not as an oracle.
