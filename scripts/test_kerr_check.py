"""Validates kerr_elliptic_thesis_v2_corrected.tex's central claimed result --
the Hamilton-Jacobi separation of Kerr null geodesics -- against EinsteinPy's
actual Kerr metric tensor, from first principles. Not "does this match a
textbook formula" (which the paper itself already does, citing Carter 1968
and Gralla & Lupsasca 2020) but "does the paper's printed R(r) genuinely fall
out of the real inverse metric, derived here independently." Zero
test-framework dependency, matching the other test_*.py files.

Requires: pip install einsteinpy

THREE REAL BUGS were caught while building this, in the derivation code
itself, not the physics -- documented here because they're instructive and
easy to repeat:

1. Symbol-identity trap. `Kerr()` builds its OWN internal `r, theta` symbols
   via `sympy.symbols("t r theta phi")`. An externally-created
   `sympy.Symbol("r", positive=True)` prints identically but is a DIFFERENT
   object -- `.subs()` against it silently does nothing. Always pull the
   actual coordinate symbols via `kerr.symbols()` and use those everywhere.

2. `sympy.simplify(diff) == 0` is not a reliable zero test -- it can return
   False (or even `.equals(0)` can return None) for expressions that ARE
   exactly zero, because `simplify` is a heuristic search, not a decision
   procedure. Numeric substitution at a random point caught this immediately
   where the symbolic check gave a false negative.

3. An algebra sign error (not a metric error): EinsteinPy uses the (+,-,-,-)
   signature, giving g^rr = -Delta/Sigma and g^thth = -1/Sigma (both
   negative -- confirmed numerically before trusting either). Working through
   the Hamilton-Jacobi equation with the WRONG assumed relation (as if only
   one of the two were negative, matching a different textbook's sign
   convention) produced a derived R(r) that was the exact negative of the
   correct one -- caught by comparing against both +R_textbook and
   -R_textbook rather than assuming which sign was intended.
"""
from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sympy as sp  # noqa: E402
from einsteinpy.symbolic.predefined import Kerr  # noqa: E402

FAILURES = []


def check(name: str, cond: bool, detail: str = ""):
    mark = "PASS" if cond else "FAIL"
    print(f"[{mark}] {name}")
    if not cond and detail:
        print(f"      {detail}")
    if not cond:
        FAILURES.append(name)


@lru_cache(maxsize=1)
def build():
    """Returns the real Kerr metric quantities needed below, all derived
    from EinsteinPy's actual tensor -- nothing here is copied from a
    textbook. Cached: the symbolic matrix inversion is the expensive step,
    and four test functions would otherwise each redo it from scratch."""
    a = sp.Symbol("a", positive=True)
    rs = sp.Symbol("r_s", positive=True)  # Schwarzschild radius = 2M; kept symbolic, substituted at the end
    E, Lz, Q = sp.symbols("E L_z Q", real=True)

    kerr = Kerr(c=1, sch=rs, a=a)
    t, r, theta, phi = kerr.symbols()  # the ACTUAL symbols -- see lesson 1 above
    g = kerr.tensor()

    g_tt, g_rr, g_thth, g_phph, g_tphi = (
        sp.simplify(g[i][j]) for i, j in [(0, 0), (1, 1), (2, 2), (3, 3), (0, 3)]
    )
    M2 = sp.Matrix([[g_tt, g_tphi], [g_tphi, g_phph]])
    ginv_tt, ginv_tphi, ginv_phph = sp.simplify(M2.inv())[0, 0], sp.simplify(M2.inv())[0, 1], sp.simplify(M2.inv())[1, 1]

    Sigma = r ** 2 + a ** 2 * sp.cos(theta) ** 2
    Delta = r ** 2 - rs * r + a ** 2

    return dict(a=a, rs=rs, E=E, Lz=Lz, Q=Q, r=r, theta=theta,
                g_rr=g_rr, g_thth=g_thth,
                ginv_tt=ginv_tt, ginv_tphi=ginv_tphi, ginv_phph=ginv_phph,
                Sigma=Sigma, Delta=Delta)


def test_inverse_metric_signs():
    """g^rr and g^thth must both be negative in EinsteinPy's (+,-,-,-)
    signature -- checked numerically first (robust) then symbolically."""
    d = build()
    vals = {d["a"]: sp.Rational(1, 2), d["r"]: sp.Integer(5),
            d["theta"]: sp.pi / 3, d["rs"]: sp.Integer(2)}
    lhs = complex((1 / d["g_rr"]).subs(vals))
    rhs = complex((-d["Delta"] / d["Sigma"]).subs(vals))
    check("g^rr == -Delta/Sigma (numeric)", abs(lhs - rhs) < 1e-12, f"{lhs} vs {rhs}")

    lhs2 = complex((1 / d["g_thth"]).subs(vals))
    rhs2 = complex((-1 / d["Sigma"]).subs(vals))
    check("g^thth == -1/Sigma (numeric)", abs(lhs2 - rhs2) < 1e-12, f"{lhs2} vs {rhs2}")

    ginv_rr = sp.simplify(1 / d["g_rr"])
    ginv_thth = sp.simplify(1 / d["g_thth"])
    check("g^rr == -Delta/Sigma (symbolic .equals)",
          (ginv_rr - (-d["Delta"] / d["Sigma"])).equals(0) is True)
    check("g^thth == -1/Sigma (symbolic .equals)",
          (ginv_thth - (-1 / d["Sigma"])).equals(0) is True)


def test_separability_from_the_real_metric():
    """The Hamilton-Jacobi bracket B'(r,theta) = Sigma * [g^tt E^2 - 2 g^tphi E Lz + g^phph Lz^2]
    must split additively into a pure-r and a pure-theta part -- tested
    directly via the mixed partial derivative, not assumed via Carter's
    ansatz (kerr_elliptic_thesis_v2_corrected.tex, Appendix A, Step 1: "The
    separability of S ... is the non-trivial step")."""
    d, Bp = _rebuild_with_Bp()
    mixed = sp.simplify(sp.diff(Bp, d["r"], d["theta"]))
    check("d^2 B'/dr dtheta == 0 (genuine additive separability, from the metric)",
          mixed == 0, f"got: {mixed}")


def test_Rr_matches_the_paper():
    """kerr_elliptic_thesis_v2_corrected.tex, Appendix A, Step 3:
    R(r) = (r^2+a^2-a*xi)^2 - Delta*[eta+(xi-a)^2], xi=Lz/E, eta=Q/E^2.
    Derived here from Delta*p_r^2 = B'(r,theta) - p_theta^2 (the corrected
    sign -- see lesson 3 above) with p_theta^2 fixed by Carter's own Q
    definition (Step 2 of the same appendix)."""
    d, Bp = _rebuild_with_Bp()
    M = sp.Symbol("M", positive=True)
    E, Lz, Q, r, theta, a = d["E"], d["Lz"], d["Q"], d["r"], d["theta"], d["a"]
    Delta_M = d["Delta"].subs(d["rs"], 2 * M)

    Theta_from_Carter_Q = Q - sp.cos(theta) ** 2 * (Lz ** 2 / sp.sin(theta) ** 2 - a ** 2 * E ** 2)
    R_derived = sp.expand(Delta_M * (Bp.subs(d["rs"], 2 * M) - Theta_from_Carter_Q))
    R_paper = sp.expand((E * (r ** 2 + a ** 2) - Lz * a) ** 2 - Delta_M * ((Lz - a * E) ** 2 + Q))

    check("R_derived == R_paper (full symbolic algebra, exact zero)",
          sp.simplify(R_derived - R_paper) == 0)

    # And in the paper's own normalized variables xi=Lz/E, eta=Q/E^2:
    xi, eta = sp.symbols("xi eta", real=True)
    R_paper_normalized = (r ** 2 + a ** 2 - a * xi) ** 2 - Delta_M * (eta + (xi - a) ** 2)
    R_derived_normalized = sp.expand((R_derived / E ** 2).subs({Lz: xi * E, Q: eta * E ** 2}))
    check("R_derived matches the paper's own (xi, eta)-normalized R(r), exactly",
          sp.simplify(R_derived_normalized - R_paper_normalized) == 0)


@lru_cache(maxsize=1)
def _rebuild_with_Bp():
    d = build()
    pt, pphi = -d["E"], d["Lz"]
    bracket = d["ginv_tt"] * pt ** 2 + 2 * d["ginv_tphi"] * pt * pphi + d["ginv_phph"] * pphi ** 2
    Bp = sp.simplify(d["Sigma"] * bracket)
    return d, Bp


def test_Rr_would_fail_with_the_wrong_sign():
    """Meta-level check on the checking method itself: confirm the OLD,
    wrong sign convention (Delta*p_r^2 = B' + p_theta^2, without correcting
    for both g^rr and g^thth being negative) is correctly detected as NOT
    matching R_paper -- i.e. this test suite can actually fail, the same
    discipline applied throughout this project's other test files."""
    d, Bp = _rebuild_with_Bp()
    M = sp.Symbol("M", positive=True)
    E, Lz, Q, r, theta, a = d["E"], d["Lz"], d["Q"], d["r"], d["theta"], d["a"]
    Delta_M = d["Delta"].subs(d["rs"], 2 * M)
    Theta_from_Carter_Q = Q - sp.cos(theta) ** 2 * (Lz ** 2 / sp.sin(theta) ** 2 - a ** 2 * E ** 2)
    R_wrong = sp.expand(Delta_M * (-Bp.subs(d["rs"], 2 * M) + Theta_from_Carter_Q))  # the original bug
    R_paper = sp.expand((E * (r ** 2 + a ** 2) - Lz * a) ** 2 - Delta_M * ((Lz - a * E) ** 2 + Q))
    check("tool correctly rejects the wrong-sign derivation (does NOT match R_paper)",
          sp.simplify(R_wrong - R_paper) != 0)


if __name__ == "__main__":
    test_inverse_metric_signs()
    test_separability_from_the_real_metric()
    test_Rr_matches_the_paper()
    test_Rr_would_fail_with_the_wrong_sign()

    print()
    if FAILURES:
        print(f"RESULT: FAIL ({len(FAILURES)} failed: {', '.join(FAILURES)})")
        raise SystemExit(1)
    print("RESULT: PASS (Kerr separability and R(r) validated from the real metric)")
