"""Regression suite for deriv_check.py, run against real claims from this
project's own manuscripts -- not toy examples. Zero test-framework dependency
(plain `python test_deriv_check.py`), matching test_retry.py's pattern.

Two kinds of assertion, kept explicit rather than conflated:
  - Claims 1-5 are real physics/math facts from our papers and SHOULD verify
    as true. Here "the check returns ok=True" and "the tool works correctly"
    are the same statement.
  - Claim 6 is the earliest carbon-capture draft's WITHDRAWN, wrong claim.
    Here the passing test is "the checker correctly reports this as FALSE" --
    a meta-level assertion about the tool's behavior, not about the physics.
    Conflating these two would make a CI failure ambiguous (did the tool
    break, or did a real claim stop holding?) -- so this file's `check()`
    calls always assert what the TOOL should do, never the content directly.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sympy as sp  # noqa: E402
from deriv_check import check_dimensions, check_limit  # noqa: E402
from sympy.physics import units as u  # noqa: E402

FAILURES = []


def check(name: str, cond: bool, detail: str = ""):
    mark = "PASS" if cond else "FAIL"
    print(f"[{mark}] {name}")
    if not cond and detail:
        print(f"      {detail}")
    if not cond:
        FAILURES.append(name)


def _build_tc():
    """The Allen-Dynes T_c formula from Narlagiri_Superconductivity_Thesis_v4,
    Eq. (AD), shared by the two tests below so it's defined in exactly one
    place."""
    lam, wlog, mu, kB = sp.symbols("lambda omega_log mu_star k_B", positive=True)
    f1 = (1 + (lam / (2.46 * (1 + 3.8 * mu))) ** sp.Rational(3, 2)) ** sp.Rational(1, 3)
    L2 = 1.82 * (1 + 6.3 * mu) * sp.Rational(6, 5)
    f2 = 1 + (sp.Rational(1, 5) * lam ** 2) / (lam ** 2 + L2 ** 2)
    Tc = f1 * f2 * wlog / (sp.Rational(12, 10) * kB) * sp.exp(
        -1.04 * (1 + lam) / (lam - mu * (1 + sp.Rational(62, 100) * lam)))
    return Tc, lam, wlog, mu, kB


def test_tc_exactly_linear_in_omega_log():
    """Narlagiri_Superconductivity_Thesis_v4: at fixed lambda and mu*, T_c is
    exactly linear in omega_log -- checked by full symbolic simplification of
    T_c(2w) - 2*T_c(w), not a numeric spot-check (stronger evidence per
    Polya Pattern 2, plausible-reasoning.md)."""
    Tc, lam, wlog, mu, kB = _build_tc()
    lin_check = sp.simplify(Tc.subs(wlog, 2 * wlog) - 2 * Tc)
    check("T_c(2*omega_log) - 2*T_c(omega_log) == 0 (exact linearity)",
          lin_check == 0, f"got: {lin_check}")


def test_printed_constant_matches():
    """The manuscript's own printed constant C(1.5, 0.13) = 1.335701 K/meV --
    a single-point check (Polya Pattern 2: weaker evidence than the exact
    symbolic reduction above, and should be read as such)."""
    Tc, lam, wlog, mu, kB = _build_tc()
    kB_meV_per_K = sp.Rational(8617333262, 100000000000)
    C_num = Tc.subs({lam: sp.Rational(15, 10), mu: sp.Rational(13, 100)}) / wlog
    r = check_limit(C_num.subs(kB, kB_meV_per_K), {}, 1.335701, tol=1e-5)
    check("C(1.5, 0.13) == 1.335701 K/meV as printed in the manuscript", r.ok, r.detail)


def test_biaxial_to_hydrostatic_factor():
    """Superconductivity v4, Ch.6: (1/3)(sigma+sigma+0) == (2/3) sigma, exactly."""
    sigma = sp.symbols("sigma")
    hydrostatic = sp.Rational(1, 3) * (sigma + sigma + 0)
    r = check_limit(hydrostatic, {}, None, symbolic_target=sp.Rational(2, 3) * sigma)
    check("(1/3)(sigma+sigma+0) == (2/3) sigma, exactly", r.ok, r.detail)


def test_epitaxial_pressure_formula():
    """Superconductivity v4, Ch.6: Y/(1-nu)*(da/a) at Y=600,nu=0.25,da/a=0.05 == 40 (GPa)."""
    Y, nu, da_a = sp.symbols("Y nu da_a")
    P = Y / (1 - nu) * da_a
    r = check_limit(P, {Y: 600, nu: sp.Rational(1, 4), da_a: sp.Rational(5, 100)}, 40.0)
    check("Y/(1-nu)*(da/a) at Y=600,nu=0.25,da/a=0.05 == 40 (GPa)", r.ok, r.detail)


def test_thermodynamic_work_dimensions():
    """Carbon Capture v2: [W] == [R][T] for W = R*T*ln(1/x) (ln(1/x) dimensionless),
    a real dimensional check via sympy.physics.units.DimensionSystem, not
    string-matching unit labels."""
    R_dim = u.energy / (u.temperature * u.amount_of_substance)
    W_lhs_dim = u.energy / u.amount_of_substance
    W_rhs_dim = R_dim * u.temperature
    r = check_dimensions(W_lhs_dim, W_rhs_dim)
    check("[W] == [R][T] for W = R*T*ln(1/x)", r.ok, r.detail)


def test_withdrawn_claim_is_correctly_rejected():
    """Meta-level assertion: the earliest carbon-capture draft's WITHDRAWN
    claim (0.18*lambda*<omega> with lambda=4.5, <omega>=400 meV "gives"
    Tc=300 K -- the exact unit-conflation error Superconductivity v4 Sec 4.1
    documents) must be correctly identified as FALSE by check_limit. The
    passing test here is that the tool says NOT ok -- not that the physics
    claim is true, which it isn't."""
    kB_meV_per_K = sp.Rational(8617333262, 100000000000)
    r = check_limit(sp.Float(0.18) * sp.Float(4.5) * sp.Float(400) / kB_meV_per_K,
                     {}, 300.0, tol=1e-6)
    check("tool correctly rejects the withdrawn 300 K claim (computes ~3759.86 K instead)",
          not r.ok, r.detail)
    check("...and the rejected value matches the hand-derivation from earlier this session",
          abs(r.substituted_value.real - 3759.8638714455697) < 1e-6,
          f"got {r.substituted_value}")


if __name__ == "__main__":
    test_tc_exactly_linear_in_omega_log()
    test_printed_constant_matches()
    test_biaxial_to_hydrostatic_factor()
    test_epitaxial_pressure_formula()
    test_thermodynamic_work_dimensions()
    test_withdrawn_claim_is_correctly_rejected()

    print()
    if FAILURES:
        print(f"RESULT: FAIL ({len(FAILURES)} failed: {', '.join(FAILURES)})")
        raise SystemExit(1)
    print("RESULT: PASS (all derivation checks behaved correctly)")
