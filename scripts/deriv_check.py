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

This is a library, not a standalone tool -- the natural caller is Claude (or
a human) writing a few lines of Python during Phase 5 Symbolic Verification
to check one specific new derivation, not a generic command-line interface
over an arbitrary expression-description format (that would be speculative
complexity with no demonstrated need: verification.md's own worked examples
are inline Python, and that's the actual usage pattern this matches).

Usage:
    from deriv_check import check_dimensions, check_limit
    check_dimensions(lhs_dim, rhs_dim)
    check_limit(expr, subs, expected, tol=1e-9)

For a validated regression suite against real claims from this project's own
manuscripts, see test_deriv_check.py (run directly: `python test_deriv_check.py`).
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


if __name__ == "__main__":
    print("deriv_check.py is a library. Run: python test_deriv_check.py")
    print("for its validated regression suite against real claims from this")
    print("project's own manuscripts.")
