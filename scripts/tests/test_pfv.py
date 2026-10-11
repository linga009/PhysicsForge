"""Planted-error test suite for pfv.

Contract tested for every check: it must NOT refute a true claim and it MUST refute a planted false one,
and it must never return VERIFIED for something false (soundness). Run:  python3 -m pfv selftest
"""
import itertools
import math
import os
import random
import sys
import unittest
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import sympy as sp

from pfv.core import REFUTED, VERIFIED, CONSISTENT, INCONCLUSIVE, report, overall
from pfv import numtheory as nt, groups as gr, lie, quantum as qm, linalg as la, analysis as an
from pfv import derivation as dv, dimensions as dm, geometry as geo, mechanics as me, combinat as cb
from pfv import algebra as al, probability as pb, qft, vectorcalc as vc, smt


class Base(unittest.TestCase):
    def ok(self, r, msg=""):
        self.assertIn(r.verdict, (VERIFIED, CONSISTENT), f"true claim wrongly not accepted: {r}\n{msg}")

    def proved(self, r, msg=""):
        self.assertEqual(r.verdict, VERIFIED, f"expected VERIFIED: {r}\n{msg}")

    def bad(self, r, msg=""):
        self.assertEqual(r.verdict, REFUTED, f"planted error not caught: {r}\n{msg}")

    def not_proved(self, r, msg=""):
        self.assertNotEqual(r.verdict, VERIFIED, f"unsound: VERIFIED a non-theorem: {r}\n{msg}")


# ---------------------------------------------------------------------------- core
class TestCore(Base):
    def test_overall_and_report(self):
        a = nt.check_claimed_value(4, 4)
        b = nt.find_counterexample(lambda n: n >= 0, range(10))
        self.assertEqual(overall([a]), VERIFIED)
        self.assertEqual(overall([a, b]), CONSISTENT)
        self.assertEqual(overall([a, nt.check_claimed_value(4, 5)]), REFUTED)
        txt = report([a, b], "t")
        self.assertIn("Not proven", txt)
        self.assertIn("SYMBOLIC VERIFICATION", txt)

    def test_bool_semantics(self):
        self.assertTrue(bool(nt.check_claimed_value(1, 1)))
        self.assertFalse(bool(nt.check_claimed_value(1, 2)))


# ---------------------------------------------------------------------------- number theory
class TestNumberTheory(Base):
    def test_claimed_value(self):
        self.proved(nt.check_claimed_value(Fraction(1, 3), "1/3"))
        for c in (105, 65, 67):
            self.bad(nt.check_claimed_value(66, c))

    def test_euler_polynomial_trap(self):
        r = nt.find_counterexample(lambda n: sp.isprime(n * n + n + 41), range(0, 39))
        self.assertEqual(r.verdict, CONSISTENT)          # passes on 0..38 but is NOT a theorem: must not be VERIFIED
        self.bad(nt.find_counterexample(lambda n: sp.isprime(n * n + n + 41), range(0, 60)))

    def test_factorization_and_primes(self):
        self.proved(nt.check_factorization(360, {2: 3, 3: 2, 5: 1}))
        self.bad(nt.check_factorization(360, {2: 3, 3: 2, 6: 1}))
        self.bad(nt.check_factorization(360, {2: 2, 3: 2, 5: 1}))
        for p in (2, 3, 97, 1000003, 2 ** 61 - 1):
            self.proved(nt.certify_prime(p))
        for c in (1, 91, 561, 1000001):
            self.bad(nt.certify_prime(c))

    def test_orders_against_bruteforce(self):
        for n in range(2, 40):
            for a in range(1, n):
                if math.gcd(a, n) != 1:
                    continue
                k = 1
                while pow(a, k, n) != 1:
                    k += 1
                self.proved(nt.check_order_claim(a, n, k))
                self.bad(nt.check_order_claim(a, n, k + 1))

    def test_crt(self):
        self.proved(nt.check_crt([2, 3, 2], [3, 5, 7], 23))
        self.bad(nt.check_crt([2, 3, 2], [3, 5, 7], 24))
        self.bad(nt.check_crt([1, 2], [4, 6]))               # inconsistent: x odd and x even

    def test_residues_and_reciprocity(self):
        for n in (7, 11, 15, 21):
            for a in range(n):
                truth = any((x * x - a) % n == 0 for x in range(n))
                self.proved(nt.is_quadratic_residue_claim(a, n, truth))
                self.bad(nt.is_quadratic_residue_claim(a, n, not truth))
        for p, q in [(7, 11), (5, 13), (3, 7)]:
            self.proved(nt.check_symbol_claims(p, q))

    def test_lte_pell_squares(self):
        self.proved(nt.check_lte(3, 10, 1, 9))
        self.bad(nt.check_lte(3, 10, 1, 9, claimed=3))
        self.proved(nt.check_pell(61, 1766319049, 226153980))
        self.bad(nt.check_pell(61, 1766319049, 226153981))
        for n in range(1, 120):
            truth = any(math.isqrt(n - a * a) ** 2 == n - a * a for a in range(math.isqrt(n) + 1))
            self.proved(nt.check_two_squares(n, truth))
            self.bad(nt.check_two_squares(n, not truth))

    def test_elliptic_curves_against_bruteforce(self):
        for p in (5, 7, 11, 13):
            for a in range(p):
                for b in range(p):
                    if (4 * a ** 3 + 27 * b ** 2) % p == 0:
                        continue
                    pts = 1 + sum(1 for x in range(p) for y in range(p) if (y * y - x ** 3 - a * x - b) % p == 0)
                    self.assertEqual(nt.ec_count(a, b, p), pts)
                    self.proved(nt.check_hasse(a, b, p, pts))
                    self.bad(nt.check_hasse(a, b, p, pts + 1))

    def test_zsigmondy(self):
        self.bad(nt.zsigmondy_primitive_divisor(2, 6))        # the famous exception
        for n in (2 + 1, 4, 5, 7, 8, 9):
            self.proved(nt.zsigmondy_primitive_divisor(2, n))

    def test_modular_obstruction_soundness(self):
        self.proved(nt.modular_obstruction(lambda x, y, z: x ** 3 + y ** 3 + z ** 3 - 4, 3))   # mod 9
        self.proved(nt.modular_obstruction(lambda x, y: x * x + y * y - 3, 2))                    # mod 4
        # soundness: whenever it proves 'no solution', a brute search must find none
        rng = random.Random(0)
        for _ in range(30):
            c = rng.randint(-5, 5)
            f = lambda x, y, c=c: x * x - 7 * y * y - c
            r = nt.modular_obstruction(f, 2)
            if r.verdict == VERIFIED:
                self.assertFalse(any(f(x, y) == 0 for x in range(-60, 61) for y in range(-60, 61)))
        self.not_proved(nt.modular_obstruction(lambda x, y: x * x - 2 * y * y - 1, 2))         # has solutions

    def test_lucas_wilson_multiplicative(self):
        self.proved(nt.check_lucas_binomial(100, 37, 7))
        self.bad(nt.check_lucas_binomial(100, 37, 7, claimed=3))
        for n in (2, 3, 5, 7, 13, 561, 1105):
            self.proved(nt.check_wilson_fermat(n))
        self.ok(nt.check_multiplicative(lambda n: int(sp.divisor_sigma(n))))
        self.bad(nt.check_multiplicative(lambda n: n + 1))

    def test_diophantine(self):
        self.bad(nt.diophantine_search(lambda x, y: x * x - 2 * y * y - 1, 2, 20, claim_no_solution=True))
        r = nt.diophantine_search(lambda x, y, z: x ** 3 + y ** 3 + z ** 3 - 4, 3, 6, claim_no_solution=True)
        self.assertEqual(r.verdict, CONSISTENT)               # absence in a box is never a proof


# ---------------------------------------------------------------------------- group theory
class TestGroups(Base):
    @classmethod
    def setUpClass(cls):
        cls.D4, cls.Q8 = gr.dihedral(4), gr.quaternion_group()
        cls.S3 = gr.symmetric(3)[1]
        cls.Z7 = gr.cyclic(7)
        cls.A4 = gr.alternating(4)[1]

    def test_axioms_true(self):
        for T in (self.D4, self.Q8, self.S3, self.Z7, self.A4, gr.dihedral(5), gr.direct_product(gr.cyclic(2), gr.cyclic(4))):
            self.proved(gr.check_group_axioms(T))

    def test_axioms_every_single_entry_mutation_is_caught(self):
        for T in (self.S3, self.Q8, self.Z7, self.D4):
            n = len(T)
            for i in range(n):
                for j in range(n):
                    for v in range(n):
                        if v == T[i, j]:
                            continue
                        M = T.copy(); M[i, j] = v
                        self.bad(gr.check_group_axioms(M), f"mutation {(i, j, v)}")

    def test_non_group_tables(self):
        self.bad(gr.check_group_axioms(np.array([[0, 1], [1, 3]])))                      # closure
        sub = np.array([[(i - j) % 5 for j in range(5)] for i in range(5)])             # subtraction: not associative
        self.bad(gr.check_group_axioms(sub))
        self.bad(gr.check_group_axioms(np.array([[0, 0], [0, 0]])))

    def test_isomorphism_classes_of_order_8(self):
        z8 = gr.cyclic(8); z4z2 = gr.direct_product(gr.cyclic(4), gr.cyclic(2))
        z2z2z2 = gr.direct_product(gr.cyclic(2), gr.direct_product(gr.cyclic(2), gr.cyclic(2)))
        gs = {"Z8": z8, "Z4xZ2": z4z2, "Z2^3": z2z2z2, "D4": self.D4, "Q8": self.Q8}
        for a, b in itertools.product(gs, repeat=2):
            r = gr.check_isomorphic(gs[a], gs[b])
            if a == b:
                self.proved(r)
            else:
                self.bad(r, f"{a} vs {b}")
        self.proved(gr.check_isomorphic(gr.dihedral(3), self.S3))
        self.proved(gr.check_isomorphic(gr.cyclic(6), gr.direct_product(gr.cyclic(2), gr.cyclic(3))))

    def test_homomorphisms(self):
        els, S3 = gr.symmetric(3)
        sign = [0 if e.is_even else 1 for e in els]
        self.proved(gr.check_homomorphism(S3, gr.cyclic(2), sign))
        for k in range(len(sign)):
            m = list(sign); m[k] = 1 - m[k]
            self.bad(gr.check_homomorphism(S3, gr.cyclic(2), m))

    def test_subgroups_normal_quotient(self):
        els, S3 = gr.symmetric(3)
        A3 = [i for i, e in enumerate(els) if e.is_even]
        self.proved(gr.check_subgroup(S3, A3)); self.proved(gr.check_normal(S3, A3))
        two = [0, [i for i, e in enumerate(els) if e.order() == 2][0]]
        self.proved(gr.check_subgroup(S3, two)); self.bad(gr.check_normal(S3, two))
        self.bad(gr.check_subgroup(S3, [0, 1, 2]) if not gr.check_subgroup(S3, [0, 1, 2]).verified else gr.check_subgroup(S3, [1, 2]))
        cos, Q = gr.quotient_table(S3, A3)
        self.proved(gr.check_isomorphic(Q, gr.cyclic(2)))

    def test_class_equation_and_orders(self):
        for T in (self.D4, self.Q8, self.S3, self.A4):
            self.proved(gr.check_class_equation(T))
        self.proved(gr.check_element_order(self.Q8, 2, 4)); self.bad(gr.check_element_order(self.Q8, 2, 2))
        self.proved(gr.check_cyclic(self.Z7, True)); self.proved(gr.check_cyclic(self.S3, False)); self.bad(gr.check_cyclic(self.S3, True))

    def test_abelian_counts(self):
        known = {8: 3, 12: 2, 16: 5, 36: 4, 72: 6, 360: 6, 720: 10}
        for n, c in known.items():
            self.proved(gr.check_abelian_count(n, c)); self.bad(gr.check_abelian_count(n, c + 1))

    def test_sylow_counts(self):
        self.proved(gr.check_sylow_count(self.S3, 3)); self.proved(gr.check_sylow_count(self.A4, 2)); self.proved(gr.check_sylow_count(self.A4, 3))

    def test_simplicity_soundness(self):
        # orders of non-abelian simple groups below 10000 (ATLAS): the prover must never claim these have none
        simple = {60, 168, 360, 504, 660, 1092, 2448, 2520, 3420, 4080, 5616, 6048, 6072, 7800, 7920, 9828}
        for n in range(2, 1300):
            r = gr.simplicity_by_sylow(n)
            if n in simple:
                self.not_proved(r, f"order {n} has a simple group")
        # and a few classic wins
        for n in (12, 30, 36, 56, 105, 200, 1000):
            self.proved(gr.simplicity_by_sylow(n))
        for n in (60, 168):
            self.assertEqual(gr.simplicity_by_sylow(n).verdict, INCONCLUSIVE)

    def test_character_tables(self):
        for T in (self.D4, self.Q8, self.S3, self.A4, gr.cyclic(5)):
            cl, sz, X = gr.character_table(T)
            self.proved(gr.check_character_table(X, sz, len(T)))
            Y = X.copy(); Y[-1, -1] += 0.1
            self.bad(gr.check_character_table(Y, sz, len(T)))

    def test_burnside_and_necklaces(self):
        self.proved(gr.check_burnside([[1, 2, 3, 0]], 4, 1)); self.bad(gr.check_burnside([[1, 2, 3, 0]], 4, 2))
        self.proved(gr.check_burnside([[1, 0, 2, 3]], 4, 3))
        self.assertEqual(gr.necklace_count(6, 2), 14); self.assertEqual(gr.necklace_count(6, 2, True), 13)
        self.assertEqual(gr.necklace_count(5, 3), 51)


# ---------------------------------------------------------------------------- Lie algebras
class TestLie(Base):
    def test_algebras(self):
        for N in (2, 3, 4):
            self.proved(lie.check_lie_algebra(lie.su_generators(N)))
        self.proved(lie.check_lie_algebra(lie.so_generators(4)))
        self.bad(lie.check_lie_algebra(lie.su_generators(3)[:7]))
        g = lie.su_generators(3); g[0] = g[0] + 0.1 * g[1] * 1j
        self.bad(lie.check_lie_algebra(g))

    def test_sum_rule(self):
        for N, kinds in ((2, ("fund",)), (3, ("fund", "sym", "adj")), (4, ("fund", "anti", "sym")), (5, ("fund", "anti"))):
            for k in kinds:
                self.proved(lie.check_casimir_sum_rule(lie.su_rep(N, k), N * N - 1))
        self.bad(lie.check_casimir_sum_rule(lie.su_rep(3, "fund"), 9))     # wrong dim G

    def test_decomposition(self):
        g = lie.tensor_gens(lie.su_rep(3, "fund"), lie.su_rep(3, "conj"))
        self.ok(lie.check_decomposition(g, {0.0: 1, 3.0: 8}))
        self.bad(lie.check_decomposition(g, {0.0: 1, 3.0: 9}))
        g3 = lie.tensor_gens(lie.tensor_gens(lie.su_rep(3, "fund"), lie.su_rep(3, "fund")), lie.su_rep(3, "fund"))
        self.ok(lie.check_decomposition(g3, {0.0: 1, 3.0: 16, 6.0: 10}))   # 3x3x3 = 1 + 8 + 8 + 10  (C2 = 0, 3, 6)

    def test_weyl_dimensions(self):
        known = [("A", 2, [1, 1], 8), ("A", 2, [3, 0], 10), ("A", 4, [0, 1, 0, 0], 10), ("A", 4, [1, 0, 0, 1], 24),
                 ("B", 2, [1, 0], 5), ("B", 2, [0, 1], 4), ("C", 2, [1, 0], 4), ("C", 2, [0, 1], 5),
                 ("D", 5, [0, 0, 0, 0, 1], 16), ("D", 4, [0, 1, 0, 0], 28), ("E", 6, [1, 0, 0, 0, 0, 0], 27),
                 ("E", 6, [0, 1, 0, 0, 0, 0], 78), ("E", 7, [0, 0, 0, 0, 0, 0, 1], 56), ("E", 7, [1, 0, 0, 0, 0, 0, 0], 133),
                 ("E", 8, [0, 0, 0, 0, 0, 0, 0, 1], 248), ("F", 4, [0, 0, 0, 1], 26), ("F", 4, [1, 0, 0, 0], 52),
                 ("G", 2, [1, 0], 7), ("G", 2, [0, 1], 14), ("G", 2, [2, 0], 27)]
        for k, r, lab, d in known:
            self.proved(lie.check_irrep_dimension(k, r, lab, d))
            self.bad(lie.check_irrep_dimension(k, r, lab, d + 1))
        for (k, r), dim in {("A", 2): 8, ("B", 3): 21, ("C", 3): 21, ("D", 4): 28, ("E", 8): 248, ("F", 4): 52, ("G", 2): 14}.items():
            self.assertEqual(lie.lie_algebra_dimension(k, r), dim)

    def test_anomalies(self):
        self.proved(lie.check_anomaly_free(lie.STANDARD_MODEL_GEN, "SM generation"))
        self.bad(lie.check_anomaly_free(lie.STANDARD_MODEL_GEN[:-1], "SM without e^c"))
        self.bad(lie.check_anomaly_free([("Q", 3, 2, sp.Rational(1, 3))] + lie.STANDARD_MODEL_GEN[1:], "wrong Y_Q"))
        nu = lie.STANDARD_MODEL_GEN + [("nu^c", 1, 1, 0)]
        self.proved(lie.check_anomaly_free(nu, "SM + right-handed neutrino"))     # a singlet changes nothing
        # SU(2) Witten anomaly: a single lepton doublet and no quarks has an odd number of doublets
        self.bad(lie.check_anomaly_free([("L", 1, 2, sp.Rational(0))], "one doublet"))

    def test_su_cubic(self):
        for N in (3, 4, 5, 6):
            for kind in ("fund", "conj", "sym", "anti"):
                f = lie.su_cubic_formula(N, kind)
                self.proved(lie.check_su_cubic(N, kind, f)); self.bad(lie.check_su_cubic(N, kind, f + 1))
        # Georgi-Glashow: 10 + 5bar is anomaly free
        self.assertAlmostEqual(lie.su_cubic_coefficient(5, "anti") + lie.su_cubic_coefficient(5, "conj"), 0, places=6)

    def test_beta_coefficients(self):
        b = lie.sm_beta_coefficients()
        self.assertEqual((b["b3"], b["b2"], b["b1_GUT"]), (7, sp.Rational(19, 6), sp.Rational(-41, 10)))


# ---------------------------------------------------------------------------- quantum
class TestQuantum(Base):
    def test_spin_algebra(self):
        for j in (0.5, 1, 1.5, 2, 3):
            self.proved(qm.check_angular_momentum_algebra(*qm.spin_matrices(j)))
        Jx, Jy, Jz = qm.spin_matrices(1)
        self.bad(qm.check_angular_momentum_algebra(Jx, Jz, Jy))
        self.bad(qm.check_angular_momentum_algebra(Jx, Jy, 2 * Jz))
        self.proved(qm.check_pauli_algebra()); self.bad(qm.check_pauli_algebra((qm.SX, qm.SZ, qm.SY)))

    def test_states_and_unitaries(self):
        bell = qm.dm([1, 0, 0, 1])
        self.proved(qm.check_density_matrix(bell)); self.bad(qm.check_density_matrix(1.1 * bell)); self.bad(qm.check_density_matrix(bell - 0.6 * np.eye(4) * 0.25 * 0 + np.diag([0.6, -0.6, 0.5, -0.5]) * 0.5))
        H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        self.proved(qm.check_unitary(H)); self.bad(qm.check_unitary(H * 1.01))
        self.proved(qm.check_hermitian(qm.SY)); self.bad(qm.check_hermitian(np.array([[0, 1j], [1j, 0]])))

    def test_entanglement(self):
        bell = qm.dm([1, 0, 0, 1])
        self.proved(qm.check_entangled(bell))
        self.bad(qm.check_entangled(np.eye(4) / 4))
        werner = lambda p: p * bell + (1 - p) * np.eye(4) / 4
        self.proved(qm.check_entangled(werner(0.5))); self.bad(qm.check_entangled(werner(0.2)))   # threshold p = 1/3
        self.assertAlmostEqual(qm.concurrence(bell), 1.0, places=6)
        self.assertAlmostEqual(qm.von_neumann_entropy(qm.ptrace(bell, (2, 2), [0])), 1.0, places=9)

    def test_channels(self):
        g = 0.3; K0 = np.array([[1, 0], [0, np.sqrt(1 - g)]]); K1 = np.array([[0, np.sqrt(g)], [0, 0]])
        self.proved(qm.check_channel([K0, K1], 2))
        self.bad(qm.check_channel([K0], 2))                         # not trace preserving
        self.bad(qm.check_channel(lambda X: X.T, 2))                # transpose: positive, not completely positive
        self.bad(qm.check_channel(lambda X: -0.2 * X + 1.2 * qm.SY @ X @ qm.SY, 2))
        self.proved(qm.check_channel(lambda X: np.trace(X) * np.eye(2) / 2, 2))

    def test_lindblad(self):
        sm = np.array([[0, 1], [0, 0.]])
        self.proved(qm.check_lindblad_generator(qm.lindbladian(0.3 * qm.SZ, [sm], [0.5], 2), 2))
        self.bad(qm.check_lindblad_generator(qm.lindbladian(0.3 * qm.SZ, [sm], [-0.5], 2), 2))

    def test_uncertainty_perturbation_spectrum(self):
        rng = np.random.default_rng(3)
        for _ in range(50):
            A = rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3)); A = A + A.conj().T
            B = rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3)); B = B + B.conj().T
            self.proved(qm.check_uncertainty(A, B, rng.normal(size=3) + 1j * rng.normal(size=3), "schrodinger"))
        self.proved(qm.check_eigenvalues(qm.SZ, [-1, 1])); self.bad(qm.check_eigenvalues(qm.SZ, [-1, 2]))
        H0 = np.diag([0, 1, 3.]); V = np.array([[0.2, 0.3, 0], [0.3, 0, 0.4], [0, 0.4, -0.1]])
        _, E1, E2 = qm.perturbation_series(H0, V, 0)
        self.proved(qm.check_perturbative_shift(H0, V, 0, E1, E2))
        self.bad(qm.check_perturbative_shift(H0, V, 0, E1, E2 + 0.05)); self.bad(qm.check_perturbative_shift(H0, V, 0, E1 + 0.05, E2))
        self.bad(qm.check_trace_obstruction(7))

    def test_state_hunters(self):
        S = qm.von_neumann_entropy
        # FALSE: conditional entropy is non-negative (true classically, false for entangled states)
        self.bad(qm.hunt_state_counterexample(lambda r: S(r) - S(qm.ptrace(r, (2, 2), [1])), (2, 2)))
        # TRUE theorems must not be refuted
        self.ok(qm.hunt_state_counterexample(lambda r: S(qm.ptrace(r, (2, 2), [0])) + S(qm.ptrace(r, (2, 2), [1])) - S(r), (2, 2), n=400))
        self.ok(qm.hunt_state_counterexample(lambda r: min(qm.entropy_inequalities(r, (2, 2, 2)).values()), (2, 2, 2), n=150))
        # FALSE: concurrence of every two-qubit state is 0 -> found by structured states
        self.bad(qm.hunt_state_counterexample(lambda r: -qm.concurrence(r), (2, 2), n=50))


# ---------------------------------------------------------------------------- linear algebra
class TestLinalg(Base):
    def test_exact_rank_det_eig(self):
        self.proved(la.check_rank(sp.Matrix([[1, 0], [0, sp.Rational(1, 10 ** 17)]]), 2))
        self.proved(la.check_rank([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 2)); self.bad(la.check_rank([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 3))
        self.proved(la.check_determinant([[1, 2], [3, 4]], -2)); self.bad(la.check_determinant([[1, 2], [3, 4]], 2))
        self.proved(la.check_eigenvalues_exact([[2, 1, 0], [0, 2, 1], [0, 0, 2]], [2, 2, 2]))
        self.bad(la.check_eigenvalues_exact([[2, 1], [0, 3]], [2, 2]))
        self.proved(la.check_diagonalizable([[2, 1], [0, 2]], False)); self.bad(la.check_diagonalizable([[2, 1], [0, 2]], True))
        self.proved(la.check_cayley_hamilton([[1, 2], [3, 4]]))

    def test_definiteness(self):
        self.proved(la.check_positive_definite([[2, -1, 0], [-1, 2, -1], [0, -1, 2]], "pd"))
        self.bad(la.check_positive_definite([[1, 2], [2, 1]], "pd"))
        self.proved(la.check_positive_definite([[1, 1], [1, 1]], "psd")); self.bad(la.check_positive_definite([[1, 1], [1, 1]], "pd"))
        # Sylvester trap: leading minors 0, 0 but not PSD
        self.bad(la.check_positive_definite([[0, 0], [0, -1]], "psd"))
        # exact Hilbert 14 is positive definite although floating-point Cholesky fails
        H = sp.Matrix(14, 14, lambda i, j: sp.Rational(1, i + j + 1))
        self.proved(la.check_positive_definite(H, "pd"))

    def test_expm_and_hunter(self):
        A = np.array([[0, 1], [0, 0.]]); B = np.array([[0, 0], [1, 0.]])
        self.bad(la.check_expm_identity(A, B)); self.proved(la.check_expm_identity(A, 2 * A))
        self.ok(la.hunt_matrix_counterexample(lambda M: np.linalg.norm(M @ M, 2) <= np.linalg.norm(M, 2) ** 2 * (1 + 1e-12), n=800))
        self.bad(la.hunt_matrix_counterexample(lambda M: np.linalg.norm(M @ M, 2) >= np.linalg.norm(M, 2) ** 2 / 2, n=800))
        self.bad(la.hunt_matrix_counterexample(lambda M: abs(np.linalg.det(M @ M.T)) >= 1e-9, n=300))     # singular family exists


# ---------------------------------------------------------------------------- analysis
class TestAnalysis(Base):
    TRUE_IDS = [("sin(x)**2+cos(x)**2", "1"), ("cosh(x)**2-sinh(x)**2", "1"), ("sin(2*x)", "2*sin(x)*cos(x)"), ("cos(2*x)", "1-2*sin(x)**2"),
                ("exp(x)*exp(y)", "exp(x+y)"), ("log(x*y)", "log(x)+log(y)"), ("sqrt(x**2)", "x"), ("(x**3-y**3)/(x-y)", "x**2+x*y+y**2"),
                ("tan(x)", "sin(x)/cos(x)"), ("sinh(x)", "(exp(x)-exp(-x))/2"), ("atan(x)+atan(1/x)", "pi/2"), ("exp(I*x)", "cos(x)+I*sin(x)"),
                ("(x+y)**3", "x**3+3*x**2*y+3*x*y**2+y**3"), ("1/(x*(x+1))", "1/x-1/(x+1)"), ("cos(x)**4-sin(x)**4", "cos(2*x)"),
                ("sin(3*x)", "3*sin(x)-4*sin(x)**3"), ("cosh(2*x)", "2*cosh(x)**2-1"), ("log(x**3)", "3*log(x)"), ("exp(log(x))", "x"),
                ("sin(x+y)", "sin(x)*cos(y)+cos(x)*sin(y)")]

    def test_identities_true_and_planted(self):
        for l, r in self.TRUE_IDS:
            self.ok(an.check_identity(l, r), f"{l} = {r}")
            for wrong in (f"({r})+1", f"2*({r})", f"({r})*(1+x/100)"):
                self.bad(an.check_identity(l, wrong), f"{l} = {wrong}")

    def test_domain_matters(self):
        self.proved(an.check_identity("sqrt(x**2)", "x", "positive")); self.bad(an.check_identity("sqrt(x**2)", "x", "real"))
        self.bad(an.check_identity("log(x*y)", "log(x)+log(y)", "real"))

    def test_derivatives_integrals(self):
        self.proved(an.check_derivative("x**x", "x**x*(log(x)+1)", "x")); self.bad(an.check_derivative("x**x", "x*x**(x-1)", "x"))
        cases = [("exp(-x**2)", "-oo", "oo", "sqrt(pi)"), ("sin(x)/x", "0", "oo", "pi/2"), ("x**2", "0", "3", "9"),
                 ("1/(1+x**2)", "-oo", "oo", "pi"), ("log(x)", "0", "1", "-1"), ("x*exp(-x)", "0", "oo", "1")]
        for e, a, b, v in cases:
            self.ok(an.check_integral(e, "x", a, b, v), e)
            self.bad(an.check_integral(e, "x", a, b, f"({v})+1/1000000"), e)
        self.bad(an.check_integral("1/x", "x", 0, 1, 1))                                   # divergent integral

    def test_sums_limits_series(self):
        self.ok(an.check_sum("1/n**2", "n", 1, "oo", "pi**2/6")); self.bad(an.check_sum("1/n**2", "n", 1, "oo", "pi**2/8"))
        self.ok(an.check_sum("1/(n*(n+1))", "n", 1, "oo", 1)); self.bad(an.check_sum("2**(-n)", "n", 0, "oo", 3))
        self.proved(an.check_limit("sin(x)/x", "x", 0, 1)); self.bad(an.check_limit("sin(x)/x", "x", 0, 0))
        self.bad(an.check_limit("1/x", "x", 0, "oo"))               # two-sided limit does not exist
        self.bad(an.check_limit("abs(x)/x", "x", 0, 1))
        self.proved(an.check_series("exp(x)", "x", 0, 4, "1+x+x**2/2+x**3/6")); self.bad(an.check_series("exp(x)", "x", 0, 4, "1+x+x**2/2+x**3/3"))
        self.proved(an.check_series("cos(x)", "x", 0, 6, "1-x**2/2+x**4/24"))

    def test_convergence(self):
        truth = [("1/n", False), ("1/n**2", True), ("n!/n**n", True), ("2**n/n!", True), ("1/sqrt(n)", False), ("n/(n+1)", False), ("1/n**1.5", True)]
        for t, c in truth:
            r = an.check_convergence(t, "n", c)
            self.assertIn(r.verdict, (VERIFIED, INCONCLUSIVE), f"{t}: {r}")
            self.assertNotEqual(an.check_convergence(t, "n", not c).verdict, VERIFIED, f"unsound on {t}")
        self.bad(an.check_convergence("1/n", "n", True))              # the harmonic series diverges

    def test_inequalities(self):
        box = {"x": (-3, 3), "y": (-3, 3)}
        self.proved(an.check_inequality("x*y", "(x**2+y**2)/2", box))                 # AM-GM as exact PSD certificate
        self.bad(an.check_inequality("x*y", "(x**2+y**2)/3", box))
        self.proved(an.check_inequality("0", "x**2+1", {"x": (-5, 5)}))
        self.bad(an.check_inequality("x**2+1", "2*x", {"x": (-5, 5)}))               # x^2 + 1 <= 2x false: gap = -(x-1)^2
        self.bad(an.check_inequality("sin(x)", "x", {"x": (-3, 3)}))
        self.ok(an.check_inequality("sin(x)", "x", {"x": (0, 3)}))
        self.bad(an.check_inequality("1+x", "exp(x)-0.5", {"x": (-2, 2)}))              # fails near x = 0
        self.ok(an.check_inequality("1+x", "exp(x)", {"x": (-2, 2)}))                   # true everywhere

    def test_ode_pde_complex_fourier(self):
        x, t = sp.symbols("x t"); y = sp.Function("y"); u = sp.Function("u")
        ode = sp.Eq(y(x).diff(x, 2) + y(x), 0)
        self.proved(an.check_solves(ode, y(x), sp.sin(x) + 2 * sp.cos(x))); self.bad(an.check_solves(ode, y(x), sp.sinh(x)))
        heat = sp.Eq(u(x, t).diff(t), u(x, t).diff(x, 2))
        self.proved(an.check_solves(heat, u(x, t), sp.exp(-t) * sp.sin(x))); self.bad(an.check_solves(heat, u(x, t), sp.exp(t) * sp.sin(x)))
        self.proved(an.check_solves(ode, y(x), sp.cos(x), ics=[(lambda s: s.subs(x, 0), 1)])); self.bad(an.check_solves(ode, y(x), sp.cos(x), ics=[(lambda s: s.subs(x, 0), 2)]))
        self.proved(an.check_residue("exp(z)/z**2", "z", 0, 1)); self.bad(an.check_residue("exp(z)/z**2", "z", 0, 2))
        self.proved(an.check_analytic("z**2", "z")); self.bad(an.check_analytic("conjugate(z)", "z"))
        self.proved(an.check_harmonic("x**2-y**2", ["x", "y"])); self.bad(an.check_harmonic("x**2+y**2", ["x", "y"]))
        self.ok(an.check_fourier_pair("exp(-x**2/2)", "exp(-k**2/2)", "x", "k", "unitary"))
        self.bad(an.check_fourier_pair("exp(-x**2/2)", "exp(-k**2/2)", "x", "k", "physics"))      # missing sqrt(2 pi)
        self.ok(an.check_fourier_pair("exp(-x**2/2)", "sqrt(2*pi)*exp(-k**2/2)", "x", "k", "physics"))


# ---------------------------------------------------------------------------- derivations
class TestDerivation(Base):
    def test_expression_chains(self):
        self.proved(dv.check_chain(["(x+1)**2", "x**2+2*x+1", "(x+1)*(x+1)"]))
        r = dv.check_chain(["(x+1)**2", "x**2+2*x+1", "x**2+x+1", "x*(x+1)+1"])
        self.bad(r); self.assertIn("step 2 -> step 3", str(r.witness["first_bad_transition"]))
        self.bad(dv.check_chain(["sin(2*x)", "2*sin(x)*cos(x)", "2*sin(x)"]))

    def test_equation_chains(self):
        x = sp.Symbol("x")
        r = dv.check_equation_chain(["sqrt(x+2) = x", "x+2 = x**2", "(x-2)*(x+1) = 0"], x)
        self.assertEqual(r.verdict, VERIFIED); self.assertIn("EXTRANEOUS", r.detail)
        self.bad(dv.check_equation_chain(["sqrt(x+2) = x", "x+2 = x**2", "(x-2)*(x+1) = 0"], x, claimed=[2, -1]))
        self.proved(dv.check_equation_chain(["sqrt(x+2) = x", "x+2 = x**2", "(x-2)*(x+1) = 0"], x, claimed=[2]))
        self.bad(dv.check_equation_chain(["x**2 = 3*x", "x = 3"], x))                 # divides by x, loses x = 0
        self.proved(dv.check_equation_chain(["x**2 = 3*x", "x*(x-3) = 0"], x, mode="equivalent"))
        self.bad(dv.check_equation_chain(["sqrt(x+2) = x", "x+2 = x**2"], x, mode="equivalent"))
        self.bad(dv.check_candidates("sqrt(x+2) = x", x, [2, -1])); self.proved(dv.check_candidates("sqrt(x+2) = x", x, [2]))


# ---------------------------------------------------------------------------- dimensions
class TestDimensions(Base):
    T = {"m": dm.M_, "v": dm.VELOCITY, "x": dm.L_, "t": dm.T_, "E": dm.ENERGY, "p": dm.MOMENTUM, "omega": dm.FREQUENCY, "k": dm.L_ ** -1,
         "F": dm.FORCE, "g": dm.ACCEL, "l": dm.L_, "q": dm.CHARGE, "r": dm.L_, "T": dm.TH_, "S": dm.ENERGY / dm.TH_, "B": dm.B_FIELD}

    def test_true_formulas(self):
        good = [("E", "p**2/(2*m)"), ("E", "m*c**2"), ("omega", "sqrt(g/l)"), ("E", "hbar*omega"), ("E", "k_B*T"), ("E", "T*S"),
                ("F", "q**2/(4*pi*epsilon_0*r**2)"), ("c", "1/sqrt(epsilon_0*mu_0)"), ("F", "q*v*B"), ("E", "m*v**2/2")]
        for a, b in good:
            self.ok(dm.check_dimensions(a, b, self.T), f"{a} = {b}")

    def test_planted_errors(self):
        bad = [("E", "p**2/m*c"), ("E", "m*c"), ("omega", "sqrt(g*l)"), ("E", "hbar*k"), ("F", "q**2/(4*pi*epsilon_0*r)"), ("E", "m*v"), ("c", "1/(epsilon_0*mu_0)"),
               ("F", "q*B"), ("E", "m*g")]
        for a, b in bad:
            self.bad(dm.check_dimensions(a, b, self.T), f"{a} = {b}")

    def test_internal_inhomogeneity(self):
        self.bad(dm.check_dimensions("E + p", "E", self.T)); self.bad(dm.check_dimensions("exp(x)", "1", self.T)); self.bad(dm.check_dimensions("sin(omega)", "1", self.T))
        self.ok(dm.check_dimensions("exp(-x/l)", "1", self.T))

    def test_planck_and_pi(self):
        self.ok(dm.check_expected_dimension("sqrt(hbar*G/c**3)", {}, dm.L_)); self.bad(dm.check_expected_dimension("sqrt(hbar*G/c**5)", {}, dm.L_))
        self.ok(dm.check_expected_dimension("sqrt(hbar*G/c**5)", {}, dm.T_)); self.ok(dm.check_expected_dimension("sqrt(hbar*c/G)", {}, dm.M_))
        v = {"F": dm.FORCE, "rho": dm.M_ / dm.L_ ** 3, "v": dm.VELOCITY, "D": dm.L_, "mu": dm.M_ / (dm.L_ * dm.T_)}
        self.proved(dm.check_pi_count(v, 2)); self.bad(dm.check_pi_count(v, 3))
        self.assertEqual(dm.planck_units()["length"], (Fraction(1, 2), Fraction(-3, 2), Fraction(1, 2)))
        self.assertEqual(dm.to_natural(dm.ENERGY), 1); self.assertEqual(dm.to_natural(dm.L_), -1)


# ---------------------------------------------------------------------------- geometry / gauge
class TestGeometry(Base):
    def test_schwarzschild_and_wrong_metrics(self):
        t, r, th, ph, M = sp.symbols("t r theta phi M", positive=True)
        x = [t, r, th, ph]; f = 1 - 2 * M / r
        g = sp.diag(-f, 1 / f, r ** 2, r ** 2 * sp.sin(th) ** 2)
        self.ok(geo.check_vacuum_solution(g, x))
        self.bad(geo.check_vacuum_solution(sp.diag(-f, 1 / f ** 2, r ** 2, r ** 2 * sp.sin(th) ** 2), x))
        self.bad(geo.check_vacuum_solution(sp.diag(-(1 - 2 * M / r ** 2), 1 / (1 - 2 * M / r ** 2), r ** 2, r ** 2 * sp.sin(th) ** 2), x))
        H = sp.Symbol("H", positive=True)
        ds = sp.diag(-(1 - H ** 2 * r ** 2), 1 / (1 - H ** 2 * r ** 2), r ** 2, r ** 2 * sp.sin(th) ** 2)
        self.ok(geo.check_vacuum_solution(ds, x, Lambda=3 * H ** 2)); self.bad(geo.check_vacuum_solution(ds, x, Lambda=H ** 2))
        self.ok(geo.check_killing([1, 0, 0, 0], g, x)); self.ok(geo.check_killing([0, 0, 0, 1], g, x)); self.bad(geo.check_killing([0, 1, 0, 0], g, x))
        self.ok(geo.check_curvature_invariant(g, x, "48*M**2/r**6")); self.bad(geo.check_curvature_invariant(g, x, "12*M**2/r**6"))
        self.assertEqual(geo.check_curvature_invariant(g, x, "48*Q**2/r**6").verdict, INCONCLUSIVE)    # unknown symbol is not a refutation

    def test_identities_hold_for_arbitrary_metrics(self):
        t, r, th, ph = sp.symbols("t r theta phi", positive=True)
        A, B = sp.Function("A")(r), sp.Function("B")(r)
        g = sp.diag(-A, B, r ** 2, r ** 2 * sp.sin(th) ** 2)
        self.ok(geo.check_contracted_bianchi(g, [t, r, th, ph]))
        self.ok(geo.check_riemann_symmetries(sp.diag(-1, 1, r ** 2, r ** 2 * sp.sin(th) ** 2), [t, r, th, ph]))   # flat space in spherical coords
        self.proved(geo.check_metric(g, [t, r, th, ph]))
        self.assertEqual(geo.check_metric(g, [t, r, th, ph], (1, 3)).verdict, INCONCLUSIVE)     # signature of A(r), B(r) is undecidable
        self.bad(geo.check_metric(sp.Matrix([[1, 2], [3, 1]]), [t, r]))

    def test_gauge(self):
        X = sp.symbols("x0:4", real=True)
        sig = [sp.Matrix([[0, 1], [1, 0]]), sp.Matrix([[0, -sp.I], [sp.I, 0]]), sp.Matrix([[1, 0], [0, -1]])]
        T = [s / 2 for s in sig]
        self.proved(geo.check_yang_mills_bianchi(T, X, -1)); self.bad(geo.check_yang_mills_bianchi(T, X, +1))
        A = [X[1] * X[2], X[0] ** 2, X[3], X[0] * X[1]]
        self.proved(geo.check_abelian_gauge_invariance(A, X, X[0] * X[1] ** 2)); self.proved(geo.check_maxwell_from_potential(A, X))


# ---------------------------------------------------------------------------- mechanics / thermo
class TestMechanics(Base):
    def test_lagrangian_hamiltonian(self):
        t = sp.Symbol("t"); q = sp.Function("q")(t); m, k = sp.symbols("m k", positive=True)
        L = m * q.diff(t) ** 2 / 2 - k * q ** 2 / 2
        self.proved(me.check_eom(L, [q], t, [sp.Eq(m * q.diff(t, 2), -k * q)])); self.proved(me.check_eom(L, [q], t, [sp.Eq(q.diff(t, 2), -k * q / m)]))
        self.bad(me.check_eom(L, [q], t, [sp.Eq(m * q.diff(t, 2), k * q)]))
        qs, ps = sp.symbols("q p", positive=True)
        self.proved(me.check_canonical([sp.log(sp.sin(ps) / qs)], [qs * sp.cot(ps)], [qs], [ps]))
        self.bad(me.check_canonical([sp.log(sp.sin(ps) / qs)], [2 * qs * sp.cot(ps)], [qs], [ps]))
        x, y, z, px, py, pz = sp.symbols("x y z p_x p_y p_z")
        Lz, Lx = x * py - y * px, y * pz - z * py
        self.proved(me.check_poisson(Lz, Lx, [x, y, z], [px, py, pz], z * px - x * pz)); self.bad(me.check_poisson(Lz, Lx, [x, y, z], [px, py, pz], x * pz - z * px))
        self.assertEqual(me.check_poisson(Lz, Lx, [x, y, z], [px, py, pz], "z*qx-x*qz").verdict, INCONCLUSIVE)   # typo is not a refutation
        H = (px ** 2 + py ** 2 + pz ** 2) / 2 + (x ** 2 + y ** 2 + z ** 2) ** 2
        self.proved(me.check_conserved_hamiltonian(Lz, H, [x, y, z], [px, py, pz])); self.bad(me.check_conserved_hamiltonian(Lz, H + x ** 2 * z, [x, y, z], [px, py, pz]))

    def test_noether_numeric(self):
        t = sp.Symbol("t"); r = sp.Function("r")(t); ph = sp.Function("phi")(t); m, k = sp.symbols("m k", positive=True)
        Lag = m * (r.diff(t) ** 2 + r ** 2 * ph.diff(t) ** 2) / 2 + k / r
        self.proved(me.check_conserved_on_shell(m * r ** 2 * ph.diff(t), Lag, [r, ph], t)); self.bad(me.check_conserved_on_shell(m * r * ph.diff(t), Lag, [r, ph], t))
        self.ok(me.check_conserved_numeric(lambda t, y: [y[1], -y[0]], [1, 0], 40, lambda y: y[0] ** 2 + y[1] ** 2))
        self.bad(me.check_conserved_numeric(lambda t, y: [y[1], -y[0] - 0.01 * y[1]], [1, 0], 40, lambda y: y[0] ** 2 + y[1] ** 2))

    def test_thermo(self):
        U, V, N, kB, c0 = sp.symbols("U V N k_B c", positive=True)
        S_good = N * kB * (sp.log(V / N * (U / N) ** sp.Rational(3, 2)) + c0)
        S_bad = N * kB * (sp.log(V * (U / N) ** sp.Rational(3, 2)) + c0)         # Sackur-Tetrode with the 1/N dropped
        self.proved(me.check_homogeneous(S_good, [U, V, N], 1)); self.bad(me.check_homogeneous(S_bad, [U, V, N], 1))
        self.proved(me.check_equation_of_state(S_good, U, V, N, claimed_P_over_T=N * kB / V, claimed_inv_T=sp.Rational(3, 2) * N * kB / U))
        self.bad(me.check_equation_of_state(S_good, U, V, N, claimed_P_over_T=2 * N * kB / V))
        self.proved(me.check_concavity(S_good, [U, V, N], {U: 3, V: 2, N: 1, kB: 1, c0: 0}))
        Ss = sp.Symbol("S", positive=True)
        self.proved(me.check_euler_relation(Ss ** 2 / V, Ss, V))                         # degree-1 homogeneous U(S, V)
        self.bad(me.check_euler_relation(Ss ** 2 / V ** 2, Ss, V))                       # degree 0: not extensive

    def test_kramers_kronig(self):
        w0, gam = 1.0, 0.3
        self.ok(me.check_kramers_kronig(lambda w: 1 / (w0 ** 2 - w ** 2 - 1j * gam * w), [0.2, 0.8, 1.5, 3.0]))
        self.bad(me.check_kramers_kronig(lambda w: 1 / (w0 ** 2 - w ** 2 + 1j * gam * w), [0.2, 0.8, 1.5, 3.0]))     # acausal


# ---------------------------------------------------------------------------- combinatorics
class TestCombinat(Base):
    def test_sequences_counts(self):
        for name, n, v in [("catalan", 5, 42), ("derangements", 6, 265), ("bell", 5, 52), ("partitions", 10, 42), ("fibonacci", 10, 55), ("motzkin", 5, 21)]:
            self.proved(cb.check_known_sequence(name, n, v)); self.bad(cb.check_known_sequence(name, n, v + 1))
        brute = lambda n: sum(1 for p in itertools.permutations(range(n)) if all(p[i] != i for i in range(n)))
        self.ok(cb.check_count_formula(lambda n: round(math.factorial(n) / math.e), brute, range(1, 8)))
        self.bad(cb.check_count_formula(lambda n: 2 ** (n - 1), lambda n: [1, 1, 2, 4, 8, 16, 31][n], range(1, 7)))      # regions of a circle

    def test_gf_recurrence(self):
        x = sp.Symbol("x")
        self.proved(cb.check_generating_function(1 / (1 - x - x ** 2), x, [1, 1, 2, 3, 5, 8, 13])); self.bad(cb.check_generating_function(1 / (1 - x - x ** 2), x, [1, 1, 2, 3, 5, 8, 14]))
        n = sp.Symbol("n", integer=True, nonnegative=True); phi = (1 + sp.sqrt(5)) / 2; psi = (1 - sp.sqrt(5)) / 2
        rec = lambda f: f(n + 2) - f(n + 1) - f(n)
        self.proved(cb.check_recurrence((phi ** n - psi ** n) / sp.sqrt(5), n, rec, {0: 0, 1: 1}))
        self.bad(cb.check_recurrence((phi ** n + psi ** n) / sp.sqrt(5), n, rec, {0: 0, 1: 1}))
        self.bad(cb.check_recurrence(2 ** n, n, rec, {0: 1, 1: 2}))

    def test_graphs(self):
        for n in range(3, 8):
            self.proved(cb.check_spanning_trees(cb.complete_graph(n), n ** (n - 2))); self.bad(cb.check_spanning_trees(cb.complete_graph(n), n ** (n - 2) - 1))
            self.proved(cb.check_spanning_trees(cb.cycle_graph(n), n))
        self.proved(cb.check_chromatic_number(cb.cycle_graph(5), 3)); self.proved(cb.check_chromatic_number(cb.cycle_graph(6), 2)); self.bad(cb.check_chromatic_number(cb.complete_graph(4), 3))
        self.ok(cb.check_binomial_identity(lambda n, k: sp.binomial(n, k) + sp.binomial(n, k + 1), lambda n, k: sp.binomial(n + 1, k + 1), 12))
        self.bad(cb.check_binomial_identity(lambda n, k: 2 * sp.binomial(n, k), lambda n, k: sp.binomial(n + 1, k), 12))


# ---------------------------------------------------------------------------- regression: bugs found by red-teaming the toolkit itself
class TestRedTeamRegressions(Base):
    def test_integrals_with_singularities(self):
        self.bad(an.check_integral("1/x**2", "x", -1, 1, -2))                  # the naive antiderivative answer
        self.not_proved(an.check_integral("1/x", "x", -1, 1, 0))               # principal value is not an integral
        self.not_proved(an.check_integral("1/(x-1)", "x", 0, 2, 0))
        self.bad(an.check_integral("tan(x)", "x", 0, "pi", 0))
        self.bad(an.check_integral("sin(x)", "x", 0, "oo", 1))                  # oscillates, no limit
        self.proved(an.check_integral("1/sqrt(abs(x))", "x", -1, 1, 4)); self.proved(an.check_integral("abs(x)", "x", -2, 2, 4)); self.proved(an.check_integral("log(abs(x))", "x", -1, 1, -2))

    def test_divergent_and_conditional_series(self):
        self.bad(an.check_sum("(-1)**n", "n", 0, "oo", sp.Rational(1, 2)))     # Grandi: Abel sum is not the sum
        self.bad(an.check_sum("n", "n", 1, "oo", sp.Rational(-1, 12)))
        self.bad(an.check_sum("1/n", "n", 1, "oo", 3))
        self.ok(an.check_sum("(-1)**(n+1)/n", "n", 1, "oo", "log(2)"))
        for c in (True, False):                                               # conditionally convergent: the tool must NOT call it divergent
            self.not_proved(an.check_convergence("(-1)**n/sqrt(n)", "n", False))
        self.assertNotEqual(an.check_convergence("(-1)**n/sqrt(n)", "n", True).verdict, REFUTED)
        self.proved(an.check_convergence("(-1)**n", "n", False)); self.bad(an.check_convergence("(-1)**n", "n", True))
        self.proved(an.check_convergence("1/log(n+1)", "n", False)); self.proved(an.check_convergence("n**2/2**n", "n", True))

    def test_float_definiteness_is_exact_or_inconclusive(self):
        self.proved(la.check_positive_definite(np.array([[1.0, 1.0], [1.0, 1 + 1e-14]]), "pd"))   # exact arithmetic on the stored floats
        self.bad(la.check_positive_definite(np.array([[1.0, 1.0], [1.0, 1.0]]), "pd")); self.proved(la.check_positive_definite(np.array([[1.0, 1.0], [1.0, 1.0]]), "psd"))
        rng = np.random.default_rng(0); B = rng.normal(size=(15, 15))
        self.ok(la.check_positive_definite(B @ B.T + 1e-3 * np.eye(15), "pd"))
        self.bad(la.check_positive_definite(-(B @ B.T) - np.eye(15), "pd"))

    def test_input_validation_is_not_refutation(self):
        self.assertEqual(nt.check_hasse(1, 1, 9, 13).verdict, INCONCLUSIVE); self.assertEqual(nt.check_hasse(1, 1, 2, 5).verdict, INCONCLUSIVE)
        self.assertEqual(nt.find_counterexample(lambda n: True, []).verdict, INCONCLUSIVE)
        self.proved(nt.check_order_claim(1, 1, 1))
        t = sp.Symbol("t"); q = sp.Function("q")(t); m, k, w = sp.symbols("m k omega", positive=True)
        L = m * q.diff(t) ** 2 / 2 - k * q ** 2 / 2
        self.assertEqual(me.check_eom(L, [q], t, [sp.Eq(q.diff(t, 2), -w ** 2 * q)]).verdict, INCONCLUSIVE)       # omega undefined: not a refutation
        self.assertEqual(gr.check_subgroup(gr.cyclic(4), [0, 9]).verdict, INCONCLUSIVE)
        self.assertEqual(qm.hunt_state_counterexample(lambda r: float("nan"), (2,)).verdict, INCONCLUSIVE)

    def test_symbol_assumption_mismatch(self):
        xp = sp.Symbol("x", positive=True)
        self.proved(an.check_identity(sp.sqrt(xp ** 2), "x")); self.proved(an.check_identity(sp.log(2 * xp), "log(x)+log(2)"))
        t, r, th, ph, M = sp.symbols("t r theta phi M", positive=True)
        g = sp.diag(-(1 - 2 * M / r), 1 / (1 - 2 * M / r), r ** 2, r ** 2 * sp.sin(th) ** 2)
        self.proved(geo.check_curvature_invariant(g, [t, r, th, ph], "48*M**2/r**6"))                   # string symbols vs positive symbols
        self.assertEqual(an.check_identity("N*x", "x*N").verdict, VERIFIED)                                # 'N' is a symbol, not sympy's N()

    def test_isomorphism_of_relabelled_groups(self):
        def relabel(T, seed):
            perm = np.random.default_rng(seed).permutation(len(T)); T2 = np.zeros_like(T)
            for i in range(len(T)):
                for j in range(len(T)):
                    T2[perm[i], perm[j]] = perm[T[i, j]]
            return T2
        gs = [gr.symmetric(4)[1], gr.alternating(5)[1], gr.dihedral(12), gr.quaternion_group(), gr.unit_group(35)[1],
              gr.direct_product(gr.symmetric(3)[1], gr.cyclic(4))]
        for T in gs:
            self.proved(gr.check_isomorphic(T, relabel(T, 1)))
            self.bad(gr.check_isomorphic(T, relabel(T, 2), claimed=False))
        a4, d6 = gr.alternating(4)[1], gr.dihedral(6)
        for A, B in itertools.combinations([gr.cyclic(12), gr.direct_product(gr.cyclic(6), gr.cyclic(2)), a4, d6], 2):
            self.bad(gr.check_isomorphic(A, B))


# ---------------------------------------------------------------------------- algebra
class TestAlgebra(Base):
    def test_polynomial_identity(self):
        self.proved(al.check_polynomial_identity("(x+y)**3", "x**3+3*x**2*y+3*x*y**2+y**3"))
        self.proved(al.check_polynomial_identity("(x**2-1)/(x-1)", "x+1"))
        self.bad(al.check_polynomial_identity("(x+y)**3", "x**3+3*x**2*y+2*x*y**2+y**3"))
        self.bad(al.check_polynomial_identity("(x+y)**2", "x**2+y**2"))

    def test_factorisation_and_irreducibility(self):
        self.proved(al.check_factorization_poly("x**4-1", ["x-1", "x+1", "x**2+1"]))
        self.bad(al.check_factorization_poly("x**4-1", ["x**2-1", "x**2+1"]))                  # product right, not complete
        self.proved(al.check_factorization_poly("x**4-1", ["x**2-1", "x**2+1"], complete=False))
        self.bad(al.check_factorization_poly("x**4-1", ["x-1", "x+1", "x**2+2"]))
        self.proved(al.check_factorization_poly("x**4-1", ["x-1", "x+1", "x-2", "x+2"], modulus=5))
        for p_, red in [(2, True), (3, True), (5, True), (7, True), (11, True)]:               # x^4+1 is reducible mod every prime
            self.proved(al.check_irreducible("x**4+1", not red, modulus=p_))
        self.proved(al.check_irreducible("x**4+1", True)); self.bad(al.check_irreducible("x**4+1", False))
        self.proved(al.check_irreducible("x**2+1", True, modulus=3)); self.bad(al.check_irreducible("x**2+1", True, modulus=5))
        self.proved(al.check_irreducible("x**4-10*x**2+1", True))
        self.assertEqual(al.check_irreducible("a*b+c", True).verdict, INCONCLUSIVE)             # which variable?

    def test_real_roots(self):
        for P, n in [("x**3-3*x+1", 3), ("x**5-x-1", 1), ("x**2+1", 0), ("x**4-5*x**2+4", 4), ("(x-1)**3*(x+2)", 2)]:
            self.proved(al.check_real_root_count(P, n)); self.bad(al.check_real_root_count(P, n + 1))
        self.proved(al.check_real_root_count("(x-1)**3*(x+2)", 4, multiplicity=True))

    def test_algebraic_numbers(self):
        for l, r in [("sqrt(3+2*sqrt(2))", "1+sqrt(2)"), ("sqrt(5+2*sqrt(6))", "sqrt(2)+sqrt(3)"), ("(sqrt(2)+sqrt(3))**2", "5+2*sqrt(6)"),
                     ("cos(pi/5)", "(1+sqrt(5))/4"), ("sin(pi/12)", "(sqrt(6)-sqrt(2))/4")]:
            self.proved(al.check_algebraic_identity(l, r)); self.bad(al.check_algebraic_identity(l, f"({r})+1/1000"))
        self.bad(al.check_algebraic_identity("sqrt(2)+sqrt(3)", "sqrt(5)"))
        self.bad(al.check_algebraic_identity("sqrt(2)+sqrt(3)", "3.146264369941973"))        # a 16-digit approximation is not equal
        self.proved(al.check_minimal_polynomial("sqrt(2)+sqrt(3)", "x**4-10*x**2+1"))
        self.proved(al.check_minimal_polynomial("sqrt(2)+sqrt(3)", "2*x**4-20*x**2+2"))         # any rational multiple
        self.bad(al.check_minimal_polynomial("sqrt(2)+sqrt(3)", "x**4-10*x**2+2"))
        self.bad(al.check_minimal_polynomial("sqrt(2)", "x**4-4"))                              # vanishes at sqrt(2) but is not minimal
        self.proved(al.check_minimal_polynomial("2**(1/3)", "x**3-2"))
        self.assertEqual(al.check_minimal_polynomial("sqrt(2)", "x**2-y").verdict, INCONCLUSIVE)

    def test_ideals_systems_discriminants(self):
        self.proved(al.check_ideal_membership("x**2-y**2", ["x-y"], ["x", "y"]))
        self.proved(al.check_ideal_membership("x+y", ["x-y"], ["x", "y"], claimed=False))
        self.bad(al.check_ideal_membership("x+y", ["x-y"], ["x", "y"], claimed=True))
        self.proved(al.check_ideal_membership("x*y-1", ["x**2-1", "y**2-1"], ["x", "y"], claimed=False))
        S = ("x**2+y**2-1", "x-y")
        self.proved(al.check_system_solutions(S, ["x", "y"], [("sqrt(2)/2", "sqrt(2)/2"), ("-sqrt(2)/2", "-sqrt(2)/2")]))
        self.bad(al.check_system_solutions(S, ["x", "y"], [("sqrt(2)/2", "sqrt(2)/2")]))                       # missing a solution
        self.bad(al.check_system_solutions(S, ["x", "y"], [("1/2", "1/2"), ("-sqrt(2)/2", "-sqrt(2)/2")]))      # not a solution
        self.assertEqual(al.check_system_solutions(["x-y"], ["x", "y"], [("1", "1")]).verdict, INCONCLUSIVE)   # positive-dimensional
        self.proved(al.check_discriminant("x**2+b*x+c", "b**2-4*c")); self.bad(al.check_discriminant("x**2+b*x+c", "b**2-4*c+1"))
        self.proved(al.check_discriminant("x**3+p*x+q", "-4*p**3-27*q**2")); self.bad(al.check_discriminant("x**3+p*x+q", "-4*p**3+27*q**2"))


# ---------------------------------------------------------------------------- probability
class TestProbability(Base):
    def test_enumeration(self):
        dice = list(itertools.product(range(1, 7), repeat=2))
        self.proved(pb.check_probability(dice, lambda o: sum(o) == 7, "1/6"))
        self.bad(pb.check_probability(dice, lambda o: sum(o) == 7, "1/5"))
        self.bad(pb.check_probability(dice, lambda o: sum(o) == 7, 0.167))                      # decimals are read exactly
        self.proved(pb.check_expectation(dice, lambda o: max(o), "161/36")); self.bad(pb.check_expectation(dice, lambda o: max(o), "7/2"))

    def test_classic_traps(self):
        kids = list(itertools.product("BG", repeat=2))
        self.proved(pb.check_conditional(kids, lambda o: o == ("B", "B"), lambda o: "B" in o, "1/3"))            # at least one boy
        self.bad(pb.check_conditional(kids, lambda o: o == ("B", "B"), lambda o: "B" in o, "1/2"))
        self.proved(pb.check_conditional(kids, lambda o: o == ("B", "B"), lambda o: o[0] == "B", "1/2"))         # the first is a boy
        outs = [(car, opened) for car in range(3) for opened in (1, 2) if opened != car]
        w = lambda o: Fraction(1, 3) * (Fraction(1, 2) if o[0] == 0 else 1)                                       # noqa: E731
        self.proved(pb.check_probability(outs, lambda o: o[0] != 0, "2/3", weight=w))                              # switching wins
        self.bad(pb.check_probability(outs, lambda o: o[0] != 0, "1/2", weight=w))

    def test_densities_and_chains(self):
        self.proved(pb.check_pdf("2*x", "x", 0, 1, mean="2/3", variance="1/18")); self.bad(pb.check_pdf("3*x", "x", 0, 1)); self.bad(pb.check_pdf("2*x", "x", 0, 1, mean="1/2"))
        self.proved(pb.check_pdf("exp(-x)", "x", 0, "oo")); self.proved(pb.check_pdf("1/(pi*(1+x**2))", "x", "-oo", "oo"))
        self.bad(pb.check_pdf("(3*x-2)*exp(-x)", "x", 0, "oo"))                   # integrates to 1 but is negative for x < 2/3 (infinite support!)
        P = [[sp.Rational(1, 2), sp.Rational(1, 2)], [sp.Rational(1, 4), sp.Rational(3, 4)]]
        self.proved(pb.check_stochastic_matrix(P)); self.bad(pb.check_stochastic_matrix([[0.5, 0.6], [0.25, 0.75]]))
        self.proved(pb.check_stationary(P, [sp.Rational(1, 3), sp.Rational(2, 3)])); self.bad(pb.check_stationary(P, [sp.Rational(1, 2), sp.Rational(1, 2)]))

    def test_float_and_shape_handling(self):
        self.assertEqual(pb.check_stochastic_matrix([[0.1, 0.2, 0.7], [0.3, 0.3, 0.4], [1 / 3, 1 / 3, 1 / 3]]).verdict, CONSISTENT)   # floats never reach VERIFIED
        self.bad(pb.check_stochastic_matrix([[0.1, 0.2, 0.7], [0.3, 0.3, 0.4]]))                                  # not square
        self.assertEqual(pb.check_stationary([[0.5, 0.6], [0.25, 0.75]], [1 / 3, 2 / 3]).verdict, INCONCLUSIVE)    # P is not stochastic

    def test_monte_carlo_refutes_only_when_far(self):
        s = lambda rng: rng.integers(1, 7, 2)                                                                   # noqa: E731
        self.ok(pb.monte_carlo_probability(s, lambda o: o.sum() == 7, 1 / 6, n=20000)); self.bad(pb.monte_carlo_probability(s, lambda o: o.sum() == 7, 0.25, n=20000))


# ---------------------------------------------------------------------------- QFT
class TestQFT(Base):
    def test_clifford_and_generators(self):
        for rep in ("dirac", "weyl", "majorana"):
            self.proved(qft.check_clifford(rep=rep))
        g, _ = qft.dirac_matrices("dirac")
        broken = [g[0], g[1], g[2], 2 * g[3]]
        self.bad(qft.check_clifford(gammas=broken))
        self.bad(qft.check_clifford(gammas=[g[0], g[1], g[2], g[2]]))                                          # duplicated matrix
        self.proved(qft.check_lorentz_generators()); self.bad(qft.check_lorentz_generators(sign=-1))

    def test_gamma_identities(self):
        T = [("sum(gu(m)*gl(m) for m in range(4))", "4*one", ()), ("sum(gu(m)*slash(p)*gl(m) for m in range(4))", "-2*slash(p)", ("p",)),
             ("sum(gu(m)*slash(a)*slash(b)*gl(m) for m in range(4))", "4*dot(a,b)*one", ("a", "b")),
             ("sum(gu(m)*slash(a)*slash(b)*slash(c)*gl(m) for m in range(4))", "-2*slash(c)*slash(b)*slash(a)", ("a", "b", "c")),
             ("tr(slash(p)*slash(k))", "4*dot(p,k)", ("p", "k")),
             ("tr(slash(p)*slash(k)*slash(q)*slash(l))", "4*(dot(p,k)*dot(q,l)-dot(p,q)*dot(k,l)+dot(p,l)*dot(k,q))", ("p", "k", "q", "l")),
             ("tr(g5*slash(p)*slash(k)*slash(q)*slash(l))", "-4*I*eps(p,k,q,l)", ("p", "k", "q", "l")),
             ("slash(p)*slash(p)", "dot(p,p)*one", ("p",))]
        B = [("sum(gu(m)*gl(m) for m in range(4))", "2*one", ()), ("sum(gu(m)*slash(p)*gl(m) for m in range(4))", "2*slash(p)", ("p",)),
             ("sum(gu(m)*slash(a)*slash(b)*gl(m) for m in range(4))", "4*dot(a,b)*one+one", ("a", "b")),
             ("sum(gu(m)*gu(n)*gl(m)*gl(n) for m in range(4) for n in range(4))", "16*one", ()),
             ("tr(slash(p)*slash(k)*slash(q)*slash(l))", "4*(dot(p,k)*dot(q,l)+dot(p,q)*dot(k,l)+dot(p,l)*dot(k,q))", ("p", "k", "q", "l")),
             ("tr(g5*slash(p)*slash(k)*slash(q)*slash(l))", "4*I*eps(p,k,q,l)", ("p", "k", "q", "l")),
             ("tr(slash(p)*slash(k)*slash(q))", "dot(p,k)", ("p", "k", "q")), ("slash(p)*slash(p)", "2*dot(p,p)", ("p",))]
        for l, r, v in T:
            self.proved(qft.check_gamma_identity(l, r, vectors=v), l)
        for l, r, v in B:
            self.bad(qft.check_gamma_identity(l, r, vectors=v), l)
        self.assertEqual(qft.check_gamma_identity("tr(slash(p)*slash(kk))", "4*dot(p,k)", vectors=("p", "k")).verdict, INCONCLUSIVE)   # typo is not a refutation

    def test_ward_identity(self):
        amp, k = qft.compton_amplitude(); self.ok(qft.check_ward_identity(amp, k))
        amp2, k = qft.compton_amplitude(sign_u=-1.0); self.bad(qft.check_ward_identity(amp2, k))


# ---------------------------------------------------------------------------- vector calculus
class TestVectorCalc(Base):
    def test_operators(self):
        T = [(vc.check_grad, ("r**2*sin(theta)", ("2*r*sin(theta)", "r*cos(theta)", "0"), "spherical"), ("r**2*sin(theta)", ("2*r*sin(theta)", "cos(theta)", "0"), "spherical")),
             (vc.check_div, (("r**2", "0", "0"), "4*r", "spherical"), (("r**2", "0", "0"), "3*r", "spherical")),
             (vc.check_div, (("1/r**2", "0", "0"), "0", "spherical"), (("1/r**2", "0", "0"), "1", "spherical")),
             (vc.check_div, (("rho", "0", "0"), "2", "cylindrical"), (("rho", "0", "0"), "3", "cylindrical")),
             (vc.check_curl, (("0", "rho", "0"), ("0", "0", "2"), "cylindrical"), (("0", "rho", "0"), ("0", "0", "1"), "cylindrical")),
             (vc.check_laplacian, ("1/r", "0", "spherical"), ("1/r", "1", "spherical")),
             (vc.check_laplacian, ("r**2", "6", "spherical"), ("r**2", "2*r", "spherical")),
             (vc.check_laplacian, ("log(rho)", "0", "cylindrical"), ("log(rho)", "1/rho", "cylindrical")),
             (vc.check_laplacian, ("x**2+y**2+z**2", "6"), ("x**2+y**2+z**2", "3")),
             (vc.check_potential, (("y", "x", "0"), "x*y"), (("y", "x", "0"), "x*y+z")),
             (vc.check_vector_potential, (("0", "0", "2"), ("-y", "x", "0")), (("0", "0", "1"), ("-y", "x", "0")))]
        for f, good, bad in T:
            self.proved(f(*good)); self.bad(f(*bad))
        self.proved(vc.check_solenoidal(("-y", "x", "0"))); self.bad(vc.check_solenoidal(("x", "y", "z")))
        self.proved(vc.check_irrotational(("y", "x", "0"))); self.bad(vc.check_irrotational(("-y", "x", "0")))
        self.proved(vc.check_laplacian("u**2*v", "2*v", "custom", coords=("u", "v", "w"), scale_factors=("1", "1", "1")))

    def test_wrong_coordinate_names_are_not_refutations(self):
        self.assertEqual(vc.check_div(("r", "0", "0"), "2", "cylindrical").verdict, INCONCLUSIVE)         # r is not a cylindrical coordinate (rho is)
        self.assertEqual(vc.check_laplacian("x**2", "2", "spherical").verdict, INCONCLUSIVE)
        self.assertEqual(vc.check_curl(("0", "phi", "0"), ("0", "0", "1"), "cartesian").verdict, INCONCLUSIVE)

    def test_identities_for_all_fields(self):
        T = [("div(curl(A))", "0", "A", ""), ("curl(curl(A))", "grad(div(A)) - vlap(A)", "A", ""),
             ("curl(cross(A,B))", "A*div(B) - B*div(A) + adv(B,A) - adv(A,B)", "AB", ""), ("div(cross(A,B))", "dot(B,curl(A)) - dot(A,curl(B))", "AB", ""),
             ("div(f*A)", "f*div(A)+dot(A,grad(f))", "A", "f"), ("curl(f*A)", "f*curl(A)+cross(grad(f),A)", "A", "f"),
             ("lap(f*g)", "f*lap(g)+g*lap(f)+2*dot(grad(f),grad(g))", "", "fg"), ("curl(grad(f))", "0*grad(f)", "", "f"),
             ("grad(dot(A,B))", "cross(A,curl(B))+cross(B,curl(A))+adv(A,B)+adv(B,A)", "AB", "")]
        B = [("curl(cross(A,B))", "A*div(B) - B*div(A) + adv(A,B) - adv(B,A)", "AB", ""), ("div(cross(A,B))", "dot(A,curl(B)) - dot(B,curl(A))", "AB", ""),
             ("div(f*A)", "f*div(A)", "A", "f"), ("curl(f*A)", "f*curl(A)+cross(A,grad(f))", "A", "f"),
             ("lap(f*g)", "f*lap(g)+g*lap(f)+dot(grad(f),grad(g))", "", "fg"), ("curl(curl(A))", "grad(div(A)) + vlap(A)", "A", ""),
             ("grad(dot(A,B))", "cross(A,curl(B))+cross(B,curl(A))", "AB", ""), ("div(grad(f))", "grad(f)", "", "f")]
        for l, r, v, s_ in T:
            self.proved(vc.check_vector_identity(l, r, vectors=tuple(v), scalars=tuple(s_)), l)
        for l, r, v, s_ in B:
            self.bad(vc.check_vector_identity(l, r, vectors=tuple(v), scalars=tuple(s_)), l)

    def test_integrals(self):
        self.proved(vc.check_flux_sphere(("x", "y", "z"), "2", "32*pi")); self.bad(vc.check_flux_sphere(("x", "y", "z"), "2", "16*pi"))
        r3 = "(x**2+y**2+z**2)**(3/2)"
        self.proved(vc.check_flux_sphere((f"x/{r3}", f"y/{r3}", f"z/{r3}"), "3", "4*pi"))                    # Gauss's law, any radius
        self.proved(vc.check_line_integral(("-y", "x", "0"), ("cos(t)", "sin(t)", "0"), (0, "2*pi"), "2*pi")); self.bad(vc.check_line_integral(("-y", "x", "0"), ("cos(t)", "sin(t)", "0"), (0, "2*pi"), "pi"))
        self.proved(vc.check_line_integral(("y", "x", "0"), ("cos(t)", "sin(t)", "0"), (0, "2*pi"), "0"))       # conservative field, closed loop
        self.proved(vc.check_divergence_theorem_box(("x**2", "y*z", "x*y*z"), [(0, 1), (0, 2), (0, 3)]))


# ---------------------------------------------------------------------------- decision procedures
@unittest.skipUnless(smt._z3 is not None, "z3 not installed")
class TestSMT(Base):
    def test_real_inequalities(self):
        T = [("a**2+b**2 >= 2*a*b", []), ("a**3+b**3+c**3 >= 3*a*b*c", ["a>=0", "b>=0", "c>=0"]),
             ("x**4*y**2+x**2*y**4+1-3*x**2*y**2 >= 0", []),                                                   # Motzkin: nonnegative but not a sum of squares
             ("a/(b+c)+b/(c+a)+c/(a+b) >= 3/2", ["a>0", "b>0", "c>0"]), ("a+b+c >= 3", ["a>0", "b>0", "c>0", "a*b*c == 1"]),
             ("a*(a-b)*(a-c)+b*(b-a)*(b-c)+c*(c-a)*(c-b) >= 0", ["a>=0", "b>=0", "c>=0"]), ("sqrt(x) <= (1+x)/2", ["x>=0"])]
        B = [("a**3+b**3+c**3 >= 3*a*b*c", []),                                                                 # needs positivity
             ("a/(b+c)+b/(c+a)+c/(a+b) >= 151/100", ["a>0", "b>0", "c>0"]), ("a+b+c >= 305/100", ["a>0", "b>0", "c>0", "a*b*c == 1"]),
             ("a**2+b**2 > 2*a*b", []), ("sqrt(x) <= x/2", ["x>=0"]), ("x**2 > x", [])]
        for c, h in T:
            self.proved(smt.check_real_claim(c, h), c)
        for c, h in B:
            self.bad(smt.check_real_claim(c, h), c)

    def test_equality_hypotheses_are_not_vacuous(self):
        """Regression: sympify('a*b*c == 1') is the Python bool False, which made every claim 'verified' vacuously."""
        r = smt.check_real_claim("a+b+c >= 305/100", ["a>0", "b>0", "c>0", "a*b*c == 1"])
        self.bad(r)
        a_, b_, c_ = (sp.nsimplify(r.witness[k]) for k in "abc")                                                 # whichever witness z3 picked must really be one
        self.assertTrue(a_ > 0 and b_ > 0 and c_ > 0 and sp.simplify(a_ * b_ * c_ - 1) == 0 and a_ + b_ + c_ < sp.Rational(305, 100))
        w = smt.check_no_integer_solutions(["x**2 + y**2 == 25", "x > 0", "y > 0"], ["x", "y"])
        self.bad(w); self.assertEqual(sorted(int(v) for v in w.witness.values()), [3, 4])
        self.proved(smt.check_real_claim("x*y == y*x")); self.bad(smt.check_real_claim("1 < 0"))

    def test_integers_and_logic(self):
        self.proved(smt.check_real_claim("n**2 % 4 != 2", integers=("n",))); self.bad(smt.check_real_claim("n**2 % 8 == 3", ["n % 2 == 1"], integers=("n",)))
        self.proved(smt.check_no_integer_solutions(["3*x + 6*y == 1"], ["x", "y"]))
        self.bad(smt.check_no_integer_solutions(["3*x + 6*y == 3"], ["x", "y"]))
        self.assertEqual(smt.check_no_integer_solutions(["x**2 == 2*y**2", "y > 0"], ["x", "y"], timeout_ms=1500).verdict, INCONCLUSIVE)   # z3 cannot do descent: say so
        self.proved(smt.check_tautology("(a>>b)>>((~b)>>(~a))")); self.bad(smt.check_tautology("(a>>b)>>(b>>a)"))
        self.proved(smt.check_logical_equivalence("~(a&b)", "~a|~b")); self.bad(smt.check_logical_equivalence("~(a&b)", "~a&~b"))


# ---------------------------------------------------------------------------- registry
class TestRegistry(Base):
    def test_catalog_and_docs(self):
        import pfv
        txt = pfv.catalog()
        self.assertGreater(pfv.n_checks(), 90)
        for d in pfv.DOMAINS:
            self.assertIn(f"[{d}]", txt)
        import inspect
        missing = []
        for d in pfv.DOMAINS:
            mod = getattr(pfv, d)
            for n, f in pfv._public(mod):
                if (n.startswith("check_") or n.startswith("hunt_")) and not inspect.getdoc(f):
                    missing.append(f"{d}.{n}")
        self.assertEqual(missing, [], f"checks without a docstring: {missing}")


class TestDocs(Base):
    """The tool menu in references/verification-tools.md must stay in step with the code, and its examples must run."""

    DOC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "references", "verification-tools.md")

    def test_every_check_is_documented(self):
        import pfv
        if not os.path.exists(self.DOC):
            self.skipTest("doc not found")
        txt = open(self.DOC, encoding="utf-8").read()
        missing = []
        for d in pfv.DOMAINS:
            for n, _ in pfv._public(getattr(pfv, d)):
                if (n.startswith("check_") or n.startswith("hunt_")) and n not in txt:
                    missing.append(f"{d}.{n}")
        self.assertEqual(missing, [], f"checks missing from verification-tools.md: {missing}")

    def test_doc_examples_run(self):
        import re
        if not os.path.exists(self.DOC):
            self.skipTest("doc not found")
        blocks = re.findall(r"```python\n(.*?)```", open(self.DOC, encoding="utf-8").read(), re.S)
        self.assertGreaterEqual(len(blocks), 3)
        for i, b in enumerate(blocks):
            exec(compile(b, f"verification-tools.md block {i}", "exec"), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
