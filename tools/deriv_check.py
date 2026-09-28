"""PhysicsForge Derivation Checker -- real implementation of verification.md
Patterns 1 (dimensional analysis) and 2/7 (limiting cases / recovering known
formulas), using sympy.physics.units's actual DimensionSystem rather than
hand-rolled unit bookkeeping.

This does NOT replace judgment. It mechanically checks two narrow, genuinely
checkable things:
  1. Does an equation balance dimensionally?
  2. Does a formula reduce to a claimed value/limit under a stated substitution?

Both are exactly the kind of claim that should never rest on the model's
self-report ("Dimensions: PASS") -- they are checkable by code, so they are
checked by code.

Usage as a library (see __main__ below for worked, validated examples against
real claims from this project's own manuscripts):
    check_dimensions(lhs_dim, rhs_expr, quantity_dims={...})
    check_limit(expr, subs, expected, tol=1e-9)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import sympy as sp
from sympy.physics import units as u
from sympy.physics.units.systems.si import SI
from sympy.physics.units.dimensions import Dimension

log = logging.getLogger("deriv_check")


# --------------------------------------------------------------------------- dimensional check

@dataclass
class DimensionResult:
    ok: bool
    lhs_dim: Dimension
    rhs_dim: Dimension | None
    detail: str


def check_dimensions(lhs_dim: Dimension, rhs_dim: Dimension) -> DimensionResult:
    """Compare two Dimension objects via SI's dimension system (handles the
    underlying base-dimension decomposition, not string equality)."""
    ds = SI.get_dimension_system()
    lhs_dep = ds.get_dimensional_dependencies(lhs_dim)
    rhs_dep = ds.get_dimensional_dependencies(rhs_dim)
    ok = lhs_dep == rhs_dep
    detail = f"LHS base dims: {lhs_dep}\nRHS base dims: {rhs_dep}"
    return DimensionResult(ok, lhs_dim, rhs_dim, detail)


# --------------------------------------------------------------------------- limiting-case check

@dataclass
class LimitResult:
    ok: bool
    substituted_value: Any
    expected: Any
    detail: str


def check_limit(expr: sp.Expr, subs: dict, expected, *, tol: float = 1e-9,
                 symbolic_target: sp.Expr | None = None) -> LimitResult:
    """Substitute `subs` into `expr` and check it matches `expected` (a number,
    within `tol`) OR simplifies to `symbolic_target` (an exact symbolic form).
    Real derivations should use the symbolic path where possible -- matching a
    single number is weaker evidence (Polya Pattern 2: a single point can match
    by coincidence; an exact symbolic reduction cannot)."""
    val = expr.subs(subs)
    val_s = sp.simplify(val)

    if symbolic_target is not None:
        diff = sp.simplify(val_s - symbolic_target)
        ok = diff == 0
        detail = f"Substituted form: {val_s}\nTarget form:      {symbolic_target}\nDifference:       {diff}"
        return LimitResult(ok, val_s, symbolic_target, detail)

    val_f = complex(val_s.evalf())
    exp_f = complex(expected)
    ok = abs(val_f - exp_f) <= tol * max(1.0, abs(exp_f))
    detail = f"Substituted numeric value: {val_f}\nExpected: {exp_f}\n|diff| = {abs(val_f-exp_f):.3e}"
    return LimitResult(ok, val_f, exp_f, detail)


# --------------------------------------------------------------------------- reporting

def report(name: str, checks: list[tuple[str, bool, str]]) -> str:
    lines = [f"=========== DERIVATION CHECK: {name} ==========="]
    all_ok = True
    for label, ok, detail in checks:
        mark = "PASS" if ok else "FAIL"
        all_ok &= ok
        lines.append(f"[{mark}] {label}")
        for dl in detail.splitlines():
            lines.append(f"        {dl}")
    lines.append(f"OVERALL: {'PASS' if all_ok else 'FAIL'}")
    lines.append("=" * (len(lines[0])))
    return "\n".join(lines)


# =============================================================================
# VALIDATION: real claims from this project's own manuscripts, not toy examples
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    lam, wlog, mu, T, kB = sp.symbols("lambda omega_log mu_star T k_B", positive=True)

    print()
    print("### Claim 1 (Narlagiri_Superconductivity_Thesis_v4): at fixed lambda and")
    print("### mu*, T_c is EXACTLY linear in omega_log -- an exact symbolic claim,")
    print("### not a numerical coincidence. Checked via full symbolic simplification,")
    print("### which is stronger evidence than substituting one number (Polya Pattern 2).")
    f1_arg = (lam / (2.46*(1+3.8*mu)))**sp.Rational(3, 2)
    f1 = (1 + f1_arg) ** sp.Rational(1, 3)
    L2 = 1.82*(1+6.3*mu)*sp.Rational(6, 5)
    f2 = 1 + (sp.Rational(1, 5) * lam**2) / (lam**2 + L2**2)
    Tc = f1 * f2 * wlog / (sp.Rational(12, 10) * kB) * sp.exp(
        -1.04*(1+lam) / (lam - mu*(1+sp.Rational(62, 100)*lam)))
    # Tc(2*wlog) - 2*Tc(wlog) must be exactly zero if linear in wlog
    lin_check = sp.simplify(Tc.subs(wlog, 2*wlog) - 2*Tc)
    r1 = ("T_c(2*omega_log) - 2*T_c(omega_log) == 0 (exact linearity)",
          lin_check == 0, f"Result of simplification: {lin_check}")

    print()
    print("### Claim 2 (same paper): the printed constant C(1.5, 0.13) = 1.335701")
    print("### K/meV. This is the ONE place the manuscript's own text supplies a")
    print("### specific number to check against -- so unlike Claim 1 this really is")
    print("### a single-point check (Polya Pattern 2 applies: weaker than Claim 1,")
    print("### and should be read as such, not treated as equally strong evidence).")
    kB_meV_per_K = sp.Rational(8617333262, 100000000000)  # CODATA, meV/K, exact rational
    C_num = Tc.subs({lam: sp.Rational(15, 10), mu: sp.Rational(13, 100)}) / wlog
    C_val = float(C_num.subs(kB, kB_meV_per_K).evalf())
    r2_check = check_limit(C_num.subs(kB, kB_meV_per_K), {}, 1.335701, tol=1e-5)
    r2 = ("C(1.5, 0.13) == 1.335701 K/meV as printed in the manuscript",
          r2_check.ok, r2_check.detail)

    print()
    print("### Claim 3 (Narlagiri_Superconductivity_Thesis_v4, Chapter 6): the")
    print("### biaxial-to-hydrostatic reduction factor is EXACTLY 2/3, from")
    print("### (1/3)(sigma_xx + sigma_yy + 0) with sigma_xx=sigma_yy=sigma.")
    sigma = sp.symbols("sigma")
    hydrostatic = sp.Rational(1, 3) * (sigma + sigma + 0)
    r3 = check_limit(hydrostatic, {}, None, symbolic_target=sp.Rational(2, 3) * sigma)
    r3 = ("(1/3)(sigma+sigma+0) == (2/3) sigma, exactly", r3.ok, r3.detail)

    print()
    print("### Claim 4 (same chapter): with Y=600 GPa, nu=0.25, da/a=0.05, the")
    print("### earlier draft's P = Y/(1-nu) * da/a formula returns 40 GPa.")
    Y, nu, da_a = sp.symbols("Y nu da_a")
    P = Y / (1 - nu) * da_a
    r4_check = check_limit(P, {Y: 600, nu: sp.Rational(1, 4), da_a: sp.Rational(5, 100)}, 40.0)
    r4 = ("Y/(1-nu)*(da/a) at Y=600,nu=0.25,da/a=0.05 == 40 (GPa)", r4_check.ok, r4_check.detail)

    print()
    print("### Claim 5 (Narlagiri_Carbon_Capture_Thesis_v2): dimensional check of")
    print("### the thermodynamic minimum work W = R*T*ln(1/x). [energy/mole]")
    print("### on both sides -- a genuine dimensional check via sympy.physics.units,")
    print("### not string-matching unit labels.")
    R_dim = u.energy / (u.temperature * u.amount_of_substance)
    T_dim = u.temperature
    W_lhs_dim = u.energy / u.amount_of_substance
    W_rhs_dim = R_dim * T_dim  # ln(1/x) is dimensionless
    dim_check = check_dimensions(W_lhs_dim, W_rhs_dim)
    r5 = ("[W] == [R][T] for W = R*T*ln(1/x) (ln(1/x) dimensionless)",
          dim_check.ok, dim_check.detail)

    print()
    print("### Claim 6 -- a DELIBERATELY WRONG claim, to confirm this tool can")
    print("### actually fail, not just rubber-stamp everything. The earliest")
    print("### carbon-capture draft's withdrawn claim: 0.18*lambda*<omega> with")
    print("### lambda=4.5, <omega>=400 meV gives Tc=300 K directly (it does NOT --")
    print("### this is exactly the unit-conflation error Section 4.1 of the v4")
    print("### superconductivity paper documents and withdraws).")
    r6_check = check_limit(sp.Float(0.18) * sp.Float(4.5) * sp.Float(400) / kB_meV_per_K,
                            {}, 300.0, tol=1e-6)
    r6 = ("0.18*4.5*400 meV / k_B == 300 K (the WITHDRAWN claim)",
          r6_check.ok, r6_check.detail)

    checks = [r1, r2, r3, r4, r5, r6]
    print()
    print(report("Real claims from this project's own manuscripts", checks))
