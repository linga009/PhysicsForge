"""pfv.analysis: calculus, series, limits, integrals, ODE/PDE solutions, inequalities, complex analysis.

Evidence ladder used by every function here:
  exact symbolic zero / exact closed form            -> VERIFIED
  50-digit evaluation at rational points disagrees    -> REFUTED (the witness point is printed; repeat it by hand)
  50-digit evaluation agrees at all sample points     -> CONSISTENT (a sample, not a proof)
  sympy could not decide                             -> INCONCLUSIVE

Pitfalls handled: sympy `simplify` can return a non-zero form for an expression that is zero (false negative),
so a non-zero symbolic residue is never reported as a refutation without a numerical witness; sample points are
rational and the default domain is x > 0 to avoid branch-cut noise; state the domain you intend, an identity such as
sqrt(x^2) = x is false for x < 0.
"""
from __future__ import annotations

import itertools
from typing import Callable, Iterable, Sequence

import mpmath as mp
import sympy as sp
from sympy import Symbol, oo, S, Rational

from .core import (Result, verified, consistent, inconclusive, timeout, CheckTimeout, rational_points, unify)
from .core import refuted as _refuted
from functools import partial as _partial

refuted = _partial(_refuted, evidence="50-digit evaluation at an explicit point")

mp.mp.dps = 50


_STR_LOCALS = {n: sp.Symbol(n) for n in ("N", "S", "Q", "O")}


def _S(x):
    """sympify. In strings 'E' is Euler's number and 'I' the imaginary unit, but N, S, Q, O are plain symbols (not sympy's
    N() function etc.). Pass sympy Symbols if you need other names to stay symbols (gamma, beta, zeta are functions)."""
    if isinstance(x, str):
        return sp.sympify(x, rational=True, locals=_STR_LOCALS)
    return sp.sympify(x)


def _free(*exprs):
    out = set()
    for e in exprs:
        out |= set(sp.sympify(e).free_symbols)
    return sorted(out, key=lambda s: s.name)


def _domain_points(syms, domain, n, seed):
    if domain == "positive":
        return rational_points(syms, n, 2, 40, 13, seed)
    if domain == "real":
        return rational_points(syms, n, 1, 40, 11, seed, signed=True)
    if domain == "unit":      # (0,1)
        return rational_points(syms, n, 1, 12, 13, seed)
    if isinstance(domain, tuple) and len(domain) == 2:
        lo, hi = map(sp.Rational, domain)
        import random
        rng = random.Random(seed)
        return [{s: lo + (hi - lo) * Rational(rng.randint(1, 999), 1000) for s in syms} for _ in range(n)]
    raise ValueError("domain must be 'positive', 'real', 'unit' or a (lo, hi) tuple")


def _num(expr, pt):
    v = sp.N(expr.subs(pt), 50)
    return v


# --------------------------------------------------------------------------
# identities
# --------------------------------------------------------------------------
def check_identity(lhs, rhs, domain="positive", n_points: int = 12, seconds: float = 20, claim: str = "") -> Result:
    """Is lhs == rhs as functions of their free symbols on `domain`?"""
    L, R = unify(_S(lhs), _S(rhs))
    claim = claim or f"{L} == {R}"
    d = L - R
    syms = _free(L, R)
    # 1. exact symbolic routes (symbols get the assumptions matching the stated domain, so sqrt(x**2) = x is provable for x > 0)
    if isinstance(domain, tuple):
        assume = {"positive": True} if min(domain) >= 0 else {"real": True}
    else:
        assume = {"positive": {"positive": True}, "unit": {"positive": True}, "real": {"real": True}}[domain]
    plain = {s_: sp.Symbol(s_.name, **assume) for s_ in syms if not s_.assumptions0.get("positive") and not s_.assumptions0.get("real")}
    d_sym = d.xreplace(plain) if plain else d
    try:
        with timeout(seconds):
            if sp.simplify(d_sym) == 0:
                return verified("check_identity", claim, f"exact: simplify(lhs - rhs) == 0 for symbols assumed {list(assume)[0]}",
                                detail="holds wherever both sides are defined, on the stated domain")
            if d.is_rational_function(*syms) and sp.cancel(sp.together(d)) == 0:
                return verified("check_identity", claim, "exact: rational functions cancel to 0")
            e2 = sp.simplify(sp.expand_trig(sp.expand(d_sym)))
            if e2 == 0:
                return verified("check_identity", claim, "exact: expand_trig + simplify gives 0")
    except CheckTimeout:
        pass
    # 2. numerical witness / sampling
    if not syms:
        v = sp.N(d, 50)
        if abs(v) > mp.mpf("1e-30"):
            return refuted("check_identity", claim, {"lhs": sp.N(L, 20), "rhs": sp.N(R, 20)}, detail=f"constants differ by {sp.N(v, 5)}")
        return consistent("check_identity", claim, f"constants agree to 50 digits (difference {sp.N(v, 3)})", caveat="Numerical equality of constants, not a proof.")
    worst = 0
    used = 0
    for pt in _domain_points(syms, domain, n_points, 2024):
        try:
            v = _num(d, pt)
        except Exception:
            continue
        if not v.is_number or v in (sp.nan, sp.zoo, sp.oo, -sp.oo):
            continue
        used += 1
        mag = abs(complex(v))
        worst = max(worst, mag)
        scale = max(1.0, abs(complex(sp.N(L.subs(pt), 20))))
        if mag > 1e-30 * scale:
            v2 = sp.N(d.subs(pt), 120)               # confirm at higher precision: a real mismatch survives, cancellation noise does not
            if not v2.is_number or abs(complex(v2)) <= 1e-30 * scale:
                continue
            return refuted("check_identity", claim, {str(k): str(val) for k, val in pt.items()},
                           detail=f"lhs - rhs = {sp.N(v, 8)} at this point (domain: {domain}). If the identity is only meant on a smaller domain, say so.")
    if used == 0:
        return inconclusive("check_identity", claim, "no sample point inside the domain of both sides")
    return consistent("check_identity", claim, f"agree to 50 digits at {used} rational points (max |diff| {worst:.1e}); symbolic simplification did not close it",
                      caveat="Sampling is not a proof. Try sp.simplify with assumptions, expand_trig, or a hand argument.")


def check_derivative(f, claimed_df, var, domain="positive") -> Result:
    """d/dx f = claimed derivative as an identity (exact, then 50-digit sampling)."""
    var = _S(var)
    return check_identity(sp.diff(_S(f), var), _S(claimed_df), domain, claim=f"d/d{var} [{_S(f)}] = {_S(claimed_df)}")


def check_antiderivative(F, f, var, domain="positive") -> Result:
    """d/dx F = f as an identity (exact simplification, then 50-digit sampling)."""
    var = _S(var)
    return check_identity(sp.diff(_S(F), var), _S(f), domain, claim=f"d/d{var} [{_S(F)}] = {_S(f)}")


# --------------------------------------------------------------------------
# integrals, sums, limits, series
# --------------------------------------------------------------------------
def _mp_quad(expr, var, a, b):
    f = sp.lambdify(var, expr, modules="mpmath")
    lo = -mp.inf if a in (-oo, -sp.oo) else mp.mpf(sp.N(a, 40))
    hi = mp.inf if b in (oo, sp.oo) else mp.mpf(sp.N(b, 40))
    return mp.quad(f, [lo, hi], error=True, maxdegree=10)


def _interior_singularities(expr, var, a, b):
    """Points strictly inside (a, b) where the integrand is singular (empty list if none found / undecidable)."""
    try:
        from sympy.calculus.singularities import singularities
        if a in (-oo, oo) or b in (-oo, oo):
            lo = -1000 if a == -oo else a
            hi = 1000 if b == oo else b
        else:
            lo, hi = a, b
        pts = singularities(expr, var, sp.Interval(lo, hi))
        out = [p for p in pts if p.is_real and a < p < b]
        return sorted(out)
    except Exception:
        return []


def _one_integral(expr, var, a, b, seconds):
    """(kind, value): kind in {'value', 'diverges', 'unknown'}."""
    try:
        with timeout(seconds):
            exact = sp.integrate(expr, (var, a, b))
    except (CheckTimeout, Exception):
        exact = None
    if exact is not None:
        if exact.has(sp.AccumBounds, sp.nan) or exact in (sp.oo, -sp.oo, sp.zoo):
            return "diverges", exact
        if not exact.has(sp.Integral) and exact.is_number and exact.is_finite:
            return "value", exact
    return "unknown", None


def check_integral(expr, var, a, b, claimed, seconds: float = 30, abs_tol: float = 1e-12) -> Result:
    """Check  integral_a^b expr d var = claimed.  Exact route first, then 30+ digit quadrature.
    Interior singularities split the integral into improper pieces; every piece must converge (a principal value is NOT an integral)."""
    expr, var, a, b, claimed = unify(_S(expr), _S(var), _S(a), _S(b), _S(claimed))
    claim = f"integral_{a}^{b} {expr} d{var} = {claimed}"
    sing = _interior_singularities(expr, var, a, b)
    if sing:
        edges = [a] + list(sing) + [b]
        total = 0
        for lo, hi in zip(edges, edges[1:]):
            kind, val = _one_integral(expr, var, lo, hi, seconds)
            if kind == "diverges":
                return refuted("check_integral", claim, {"singularity_at": [str(p) for p in sing], "piece": f"[{lo}, {hi}]", "sympy": str(val)},
                               evidence="exact improper pieces", detail=f"non-integrable singularity: the piece over [{lo}, {hi}] diverges, so the integral does not exist (a principal value, if it exists, is a different quantity)")
            if kind == "unknown":
                return inconclusive("check_integral", claim, f"integrand singular at {sing}; could not evaluate the improper piece [{lo}, {hi}] exactly")
            total += val
        if sp.simplify(total - claimed) == 0 or abs(sp.N(total - claimed, 40)) < mp.mpf("1e-35"):
            return verified("check_integral", claim, f"sum of exact improper pieces split at {sing}", detail=f"value = {sp.simplify(total)}")
        return refuted("check_integral", claim, {"exact_value": sp.simplify(total), "claimed": claimed}, evidence="exact improper pieces")
    kind, exact = _one_integral(expr, var, a, b, seconds)
    if kind == "diverges":
        return refuted("check_integral", claim, {"sympy_result": str(exact)}, evidence="exact symbolic integration",
                       detail="the integral does not converge (divergent or oscillating without limit)")
    if kind == "value":
        if sp.simplify(exact - claimed) == 0 or abs(sp.N(exact - claimed, 40)) < mp.mpf("1e-35"):
            return verified("check_integral", claim, "exact antiderivative evaluation agrees", detail=f"value = {exact}")
        return refuted("check_integral", claim, {"exact_value": exact, "claimed": claimed}, evidence="exact symbolic integration",
                       detail=f"difference = {sp.N(exact - claimed, 10)}")
    try:
        val, err = _mp_quad(expr, var, a, b)
    except Exception as e:
        return inconclusive("check_integral", claim, f"quadrature failed: {type(e).__name__}: {e}")
    if mp.isnan(val) or mp.isinf(val):
        return inconclusive("check_integral", claim, "integrand not finite on the interval (divergent or singular)")
    target = mp.mpf(sp.N(claimed, 40))
    diff = abs(val - target)
    if err > 1e-8 * max(1, abs(val)):
        return inconclusive("check_integral", claim, f"quadrature error estimate {mp.nstr(err, 3)} too large to decide (singular / oscillatory / divergent?)")
    if diff > max(abs_tol, 100 * err):
        return refuted("check_integral", claim, {"numeric_value": mp.nstr(val, 20), "claimed": mp.nstr(target, 20)},
                       evidence=f"mpmath quadrature, error estimate {mp.nstr(err, 2)}", detail=f"difference = {mp.nstr(diff, 5)}")
    return consistent("check_integral", claim, f"quadrature = {mp.nstr(val, 20)}, |diff| = {mp.nstr(diff, 2)}, error estimate {mp.nstr(err, 2)}",
                      caveat="Numerical agreement to the stated tolerance; symbolic integration did not close it.")


def check_sum(term, n, lo, hi, claimed, seconds: float = 30) -> Result:
    """sum_{n=lo}^{hi} term = claimed  (hi may be oo)."""
    term, n, lo, hi, claimed = unify(_S(term), _S(n), _S(lo), _S(hi), _S(claimed))
    claim = f"sum_{{{n}={lo}}}^{{{hi}}} {term} = {claimed}"
    try:
        with timeout(seconds):
            exact = sp.summation(term, (n, lo, hi))
        if not exact.has(sp.Sum) and not exact.has(sp.nan):
            if sp.simplify(exact - claimed) == 0:
                return verified("check_sum", claim, "exact closed-form summation", detail=f"value = {exact}")
            if exact.is_number and abs(sp.N(exact - claimed, 40)) > mp.mpf("1e-30"):
                return refuted("check_sum", claim, {"exact": exact, "claimed": claimed}, evidence="exact symbolic summation")
    except Exception:
        pass
    if hi in (oo, sp.oo):
        conv = check_convergence(term, n, False)            # asks "diverges?"; VERIFIED => divergent
        if conv.verified:
            return refuted("check_sum", claim, {"series": "diverges"}, evidence="convergence test", detail=conv.evidence + ". "
                           "A regularised value (Abel, zeta) is NOT the sum of the series; mpmath.nsum would silently return one.")
    f = sp.lambdify(n, term, "mpmath")
    try:
        if hi in (oo, sp.oo):
            val = mp.nsum(f, [mp.mpf(sp.N(lo)), mp.inf])
        else:
            val = mp.fsum(f(k) for k in range(int(lo), int(hi) + 1))
    except Exception as e:
        return inconclusive("check_sum", claim, f"numerical summation failed: {e}")
    diff = abs(val - mp.mpf(sp.N(claimed, 40)))
    if diff > 1e-15:
        return refuted("check_sum", claim, {"numeric": mp.nstr(val, 20)}, evidence="mpmath nsum (Richardson/Euler-Maclaurin acceleration)")
    return consistent("check_sum", claim, f"numerical sum {mp.nstr(val, 20)} agrees (|diff| {mp.nstr(diff, 2)})",
                      caveat="Series acceleration assumes convergence, which was not established here (conditionally convergent or borderline). Prove convergence separately.")


def check_convergence(term, n, claimed: bool, seconds: float = 30) -> Result:
    """Does sum_{n>=1} term converge (absolutely)? Ratio test, root test, p-series exponent, then the integral test.
    Never decides from partial sums (the harmonic series has terms -> 0 and diverges)."""
    term, n = _S(term), _S(n)
    n = sp.Symbol(n.name, positive=True, integer=True) if n.is_Symbol else n
    term = term.subs({s_: n for s_ in term.free_symbols if s_.name == n.name})
    claim = f"sum {term} {'converges' if claimed else 'diverges'}"
    notes: list[str] = []

    def decide(truth: bool, reason: str, extra: str = "") -> Result:
        detail = "; ".join(notes + ([extra] if extra else []))
        if truth == claimed:
            return verified("check_convergence", claim, reason, detail=detail)
        return refuted("check_convergence", claim, {"truth": "converges" if truth else "diverges"}, evidence=reason, detail=detail)

    try:
        with timeout(seconds):
            # 1. divergence test (any signs): |a_n| must tend to 0
            lim_abs = sp.limit(sp.Abs(term), n, oo)
            notes.append(f"lim |a_n| = {lim_abs}")
            if lim_abs.is_number and lim_abs != 0:
                return decide(False, "divergence test: |a_n| does not tend to 0")
            # 2. ratio and root tests (valid for any signs)
            ratio = sp.limit(sp.Abs(term.subs(n, n + 1) / term), n, oo)
            notes.append(f"ratio test limit = {ratio}")
            if ratio.is_number and ratio < 1:
                return decide(True, "ratio test: L < 1 => absolutely convergent")
            if ratio.is_number and ratio > 1:
                return decide(False, "ratio test: L > 1 => terms do not tend to 0 => divergent")
            root = sp.limit(sp.Abs(term) ** (1 / n), n, oo)
            notes.append(f"root test limit = {root}")
            if root.is_number and root < 1:
                return decide(True, "root test: L < 1")
            if root.is_number and root > 1:
                return decide(False, "root test: L > 1")
            # 3. p-series comparison: p > 1 => absolutely convergent for any signs; p < 1 only for terms of eventually constant sign
            p = sp.limit(-sp.log(sp.Abs(term)) / sp.log(n), n, oo)
            notes.append(f"|a_n| ~ n^(-{p})")
            if p.is_number and p > 1:
                return decide(True, "comparison with the p-series, p > 1 (strictly: |a_n| <= n^-(p-eps) eventually)")
            far = [sp.N(term.subs(n, k), 30) for k in (10 ** 4, 10 ** 4 + 1, 10 ** 4 + 2, 10 ** 5, 10 ** 5 + 1, 10 ** 6, 10 ** 6 + 1)]
            same_sign = all(v > 0 for v in far) or all(v < 0 for v in far)
            if p.is_number and p < 1 and same_sign:
                return decide(False, "p < 1 and terms have one sign at 7 far sample points: comparison with the harmonic series")
            if p.is_number and p < 1 and not same_sign:
                notes.append("terms change sign: could be conditionally convergent (Leibniz); the tool does not decide this case")
                return inconclusive("check_convergence", claim, "alternating / sign-changing terms with |a_n| ~ n^-p, p <= 1: conditional convergence needs a hand argument (Leibniz, Dirichlet). " + "; ".join(notes))
            # 4. integral test (positive, monotone terms)
            xs = sp.Symbol("xs", positive=True)
            fx = term.subs(n, xs)
            integral = sp.integrate(fx, (xs, 2, oo))
            notes.append(f"integral test: int_2^oo f = {integral}")
            if not integral.has(sp.Integral):
                pts = [2 + i * 7 for i in range(40)]
                vals = [sp.N(fx.subs(xs, a_)) for a_ in pts]
                mono = all(v > 0 for v in vals) and all(v1 >= v2 for v1, v2 in zip(vals, vals[1:]))
                if mono and integral.is_finite is not None:
                    return decide(bool(integral.is_finite), "integral test (positivity and monotone decrease checked at 40 sample points, not proved)")
    except CheckTimeout:
        notes.append("timed out")
    except Exception as e:
        notes.append(f"{type(e).__name__}: {e}")
    return inconclusive("check_convergence", claim, "tests inconclusive (borderline p = 1 with logarithmic factors needs a hand argument, e.g. Cauchy condensation). " + "; ".join(notes))


def check_limit(expr, var, point, claimed, direction: str = "+-", seconds: float = 20) -> Result:
    """Limit claim: exact sympy limit from both sides (one-sided if direction given), with a 1e-18 numerical fallback."""
    expr, var, point, claimed = unify(_S(expr), _S(var), _S(point), _S(claimed))
    claim = f"lim_{{{var}->{point}{'' if direction == '+-' else direction}}} {expr} = {claimed}"
    dirs = ["+", "-"] if direction == "+-" else [direction]
    vals = []
    try:
        with timeout(seconds):
            for dr in dirs:
                vals.append(sp.limit(expr, var, point, dr))
    except CheckTimeout:
        vals = []
    if vals and not any(isinstance(v, sp.Limit) for v in vals):
        if len(dirs) == 2 and sp.simplify(vals[0] - vals[1]) != 0:
            return refuted("check_limit", claim, {"limit_from_right": vals[0], "limit_from_left": vals[1]}, evidence="exact one-sided limits",
                           detail="the two-sided limit does not exist")
        if sp.simplify(vals[0] - claimed) == 0:
            return verified("check_limit", claim, "exact sympy limit (both sides)" if len(dirs) == 2 else "exact sympy one-sided limit")
        return refuted("check_limit", claim, {"true_limit": vals[0]}, evidence="exact sympy limit")
    # numerical fallback
    try:
        f = sp.lambdify(var, expr, "mpmath")
        seq = []
        for k in (6, 12, 18):
            h = mp.mpf(10) ** (-k)
            for dr in dirs:
                x0 = mp.mpf(sp.N(point, 40)) + (h if dr == "+" else -h)
                seq.append(f(x0))
        target = mp.mpf(sp.N(claimed, 40)) if claimed.is_number and claimed.is_finite else None
        if target is not None and abs(seq[-1] - target) < 1e-8 and abs(seq[-2] - target) < 1e-5:
            return consistent("check_limit", claim, f"numerical values at distance 1e-6,1e-12,1e-18 approach {mp.nstr(target, 8)}", caveat="Numerical only.")
        if target is not None:
            return refuted("check_limit", claim, {"f_near_point": mp.nstr(seq[-1], 12)}, evidence="evaluation at 1e-18 from the point")
    except Exception as e:
        return inconclusive("check_limit", claim, f"could not evaluate: {e}")
    return inconclusive("check_limit", claim, "sympy returned an unevaluated limit")


def check_series(expr, var, point, order, claimed, seconds: float = 30) -> Result:
    """Taylor/Laurent expansion about `point` up to and including O(var^order) excluded, compared EXACTLY."""
    expr, var, point, claimed = unify(_S(expr), _S(var), _S(point), _S(claimed))
    claim = f"{expr} = {claimed} + O(({var}-{point})^{order})"
    try:
        with timeout(seconds):
            ser = sp.series(expr, var, point, order).removeO()
    except CheckTimeout:
        return inconclusive("check_series", claim, "series timed out")
    diff = sp.simplify(sp.expand(ser - claimed))
    if diff == 0:
        return verified("check_series", claim, "exact series coefficients agree")
    return refuted("check_series", claim, {"true_series": ser, "difference": diff}, evidence="exact series expansion")


# --------------------------------------------------------------------------
# inequalities
# --------------------------------------------------------------------------
def check_inequality(lhs, rhs, domain: dict, strict: bool = False, grid: int = 41, restarts: int = 40, seconds: float = 20) -> Result:
    """Claim: lhs <= rhs (or < if strict) for all variables in the box `domain = {x: (lo, hi), ...}`.

    1 variable and polynomial/rational: decided EXACTLY (solve_univariate_inequality).
    Otherwise: grid + multi-start local minimisation of rhs - lhs, any violation re-evaluated at 50 digits.
    """
    L, R = unify(_S(lhs), _S(rhs))
    syms = [_S(k) for k in domain]
    claim = f"{L} {'<' if strict else '<='} {R} on {domain}"
    gap = R - L
    # exact certificate: gap is a quadratic polynomial that is positive semidefinite on all of R^n
    try:
        poly = sp.Poly(sp.expand(gap), *syms)
        if poly.total_degree() <= 2 and not gap.has(sp.Float):
            n = len(syms)
            M = sp.zeros(n + 1, n + 1)
            for monom, coeff in poly.terms():
                idx = [i for i, e in enumerate(monom) for _ in range(e)]
                idx = idx + [n] * (2 - len(idx))
                i, j = idx
                if i == j:
                    M[i, i] += coeff
                else:
                    M[i, j] += coeff / 2
                    M[j, i] += coeff / 2
            if M.is_positive_semidefinite and not strict:
                return verified("check_inequality", claim, "exact: rhs - lhs is a quadratic form [x;1]^T M [x;1] with M positive semidefinite (holds on all of R^n)")
    except Exception:
        pass
    if len(syms) == 1 and gap.is_rational_function(syms[0]):
        x = syms[0]
        lo, hi = map(sp.nsimplify, domain[str(x)] if str(x) in domain else domain[x])
        try:
            with timeout(seconds):
                bad = sp.solve_univariate_inequality(gap < 0 if not strict else gap <= 0, x, relational=False, domain=sp.Interval(lo, hi))
            if bad == sp.S.EmptySet:
                return verified("check_inequality", claim, "exact: solve_univariate_inequality finds no violating x in the interval (at points where both sides are defined)")
            pt = None
            if hasattr(bad, "inf"):
                a, b = bad.inf, bad.sup
                pt = (a + b) / 2 if a != b else a
            return refuted("check_inequality", claim, {"violating_set": bad, "example_x": pt}, evidence="exact solution set of the reversed inequality")
        except CheckTimeout:
            pass
        except Exception:
            pass
    import numpy as np
    from scipy.optimize import minimize
    f = sp.lambdify(syms, gap, "numpy")
    bounds = [tuple(map(float, domain[str(s)] if str(s) in domain else domain[s])) for s in syms]
    axes = [np.linspace(lo, hi, grid if len(syms) <= 3 else 9) for lo, hi in bounds]
    mesh = np.meshgrid(*axes, indexing="ij")
    with np.errstate(all="ignore"):
        vals = f(*mesh)
    vals = np.where(np.isfinite(vals), vals, np.inf)
    idx = np.unravel_index(np.argmin(vals), vals.shape)
    best_pt = np.array([m[idx] for m in mesh], dtype=float)
    best_val = float(vals[idx])
    rng = np.random.default_rng(0)
    for _ in range(restarts):
        x0 = np.array([rng.uniform(lo, hi) for lo, hi in bounds])
        try:
            r = minimize(lambda v: float(f(*v)), x0, bounds=bounds, method="L-BFGS-B")
            if np.isfinite(r.fun) and r.fun < best_val:
                best_val, best_pt = float(r.fun), r.x
        except Exception:
            continue
    exact_pt = {s: sp.nsimplify(round(float(v), 10), rational=True) for s, v in zip(syms, best_pt)}
    hp = sp.N(gap.subs(exact_pt), 50)
    violated = hp < 0 if not strict else hp <= 0
    if violated and abs(hp) > mp.mpf("1e-30"):
        return refuted("check_inequality", claim, {str(k): str(v) for k, v in exact_pt.items()},
                       detail=f"rhs - lhs = {sp.N(hp, 8)} there (50-digit re-evaluation at a rational point)")
    return consistent("check_inequality", claim, f"min of (rhs - lhs) found = {best_val:.3e} over a {grid}-point grid and {restarts} local searches",
                      caveat="Numerical global search on a box; not a proof. For a proof use an SOS/AM-GM argument or a monotonicity/convexity argument.")


# --------------------------------------------------------------------------
# differential equations
# --------------------------------------------------------------------------
def check_solves(equation, func, solution, ics: Sequence[tuple] = (), seconds: float = 30) -> Result:
    """Substitute `solution` for the undefined function in `equation` (an Eq or an expression equal to 0).

    `func` is an applied function like y(x) or u(x, t); `solution` is an expression in the same variables.
    `ics` is a list of (expression_in_solution_variables, value) pairs such as (y(0), 1) or (Derivative(y(x),x).subs(x,0), 0)
    given as callables on the solution: (lambda sol: sol.subs(x, 0), 1).
    """
    func, sol, eq = unify(_S(func), _S(solution), _S(equation))
    claim = f"{func} = {sol} solves {equation}"
    expr = eq.lhs - eq.rhs if isinstance(eq, sp.Equality) else eq
    try:
        with timeout(seconds):
            sub = expr.subs(func.func(*func.args), sol).doit()
            res = sp.simplify(sub)
    except CheckTimeout:
        return inconclusive("check_solves", claim, "simplification timed out")
    if res != 0:
        syms = _free(res)
        for pt in _domain_points(syms, "positive", 6, 7):
            try:
                v = sp.N(res.subs(pt), 40)
            except Exception:
                continue
            if v.is_number and abs(complex(v)) > 1e-25:
                return refuted("check_solves", claim, {str(k): str(val) for k, val in pt.items()}, detail=f"residual = {sp.N(v, 8)} (symbolic residual {res})")
        return inconclusive("check_solves", claim, f"symbolic residual {res} did not simplify to 0 but also did not evaluate nonzero at samples")
    for fn, val in ics:
        got = sp.simplify(fn(sol))
        if sp.simplify(got - _S(val)) != 0:
            return refuted("check_solves", claim, {"initial/boundary condition": f"{got} != {val}"}, evidence="exact substitution")
    return verified("check_solves", claim, "residual simplifies to exactly 0" + (" and all initial/boundary conditions hold" if ics else ""))


def check_harmonic(u, variables) -> Result:
    """Is u harmonic (Laplacian = 0)?"""
    u = _S(u)
    lap = sum(sp.diff(u, _S(v), 2) for v in variables)
    r = check_identity(lap, 0, claim=f"Laplacian({u}) = 0")
    r.check = "check_harmonic"
    return r


def check_analytic(f, z, domain="positive") -> Result:
    """Cauchy-Riemann for f(z) written with z = x + i y: u_x = v_y, u_y = -v_x."""
    x, y = sp.symbols("x y", real=True)
    expr = _S(f).subs(_S(z), x + sp.I * y)
    expr = sp.expand_complex(expr)
    u, v = sp.re(expr), sp.im(expr)
    r1 = check_identity(sp.diff(u, x) - sp.diff(v, y), 0, domain, claim="u_x = v_y")
    r2 = check_identity(sp.diff(u, y) + sp.diff(v, x), 0, domain, claim="u_y = -v_x")
    claim = f"{_S(f)} is analytic (Cauchy-Riemann) away from singularities"
    for r in (r1, r2):
        if r.refuted:
            return refuted("check_analytic", claim, r.witness, detail=f"Cauchy-Riemann fails: {r.claim}; {r.detail}", evidence=r.evidence)
    if r1.verified and r2.verified:
        return verified("check_analytic", claim, "both Cauchy-Riemann equations simplify to 0 exactly")
    return consistent("check_analytic", claim, "Cauchy-Riemann residuals vanish at sampled points", caveat="Sampled, not symbolic.")


def check_residue(f, z, z0, claimed) -> Result:
    """Residue of f at z0 (exact Laurent expansion) against a claim."""
    f, z, z0, claimed = _S(f), _S(z), _S(z0), _S(claimed)
    claim = f"Res_(z={z0}) {f} = {claimed}"
    r = sp.residue(f, z, z0)
    if sp.simplify(r - claimed) == 0:
        return verified("check_residue", claim, "exact Laurent expansion (sympy residue)", detail=f"value = {r}")
    return refuted("check_residue", claim, {"true_residue": r}, evidence="exact Laurent expansion")


def check_contour_circle(f, z, centre, radius, claimed, abs_tol: float = 1e-10) -> Result:
    """Numerically integrate f around the circle |z - centre| = radius (counter-clockwise) and compare with the claim."""
    fz = sp.lambdify(_S(z), _S(f), "mpmath")
    c = mp.mpc(complex(sp.N(_S(centre))))
    r = mp.mpf(sp.N(_S(radius)))
    val = mp.quad(lambda t: fz(c + r * mp.e ** (1j * t)) * 1j * r * mp.e ** (1j * t), [0, mp.pi, 2 * mp.pi])
    target = mp.mpc(complex(sp.N(_S(claimed))))
    claim = f"contour integral over |z-{centre}|={radius} = {claimed}"
    if abs(val - target) > abs_tol:
        return refuted("check_contour_circle", claim, {"numeric": mp.nstr(val, 15), "claimed": mp.nstr(target, 15)}, evidence="mpmath quadrature on the circle")
    return consistent("check_contour_circle", claim, f"numeric {mp.nstr(val, 12)}", caveat="Contour must not pass through a singularity; use residues for an exact value.")


def check_fourier_pair(f, F, x, k, convention: str = "unitary", test_k=(0, 1, 2.5)) -> Result:
    """F(k) = N * int f(x) e^{-i s k x} dx with the stated convention:
       'unitary'  : N = 1/sqrt(2pi), s = 1        'physics' : N = 1,       s = 1  (inverse has 1/2pi)
       'angular'  : N = 1,           s = 1        'ordinary': N = 1,       s = 2pi (F(xi) = int f e^{-2 pi i xi x})
    Numerical comparison at a few k. Normalisation conventions are the usual source of factor-2pi errors."""
    f, F, x, k = _S(f), _S(F), _S(x), _S(k)
    N, s = {"unitary": (1 / mp.sqrt(2 * mp.pi), 1), "physics": (1, 1), "angular": (1, 1), "ordinary": (1, 2 * mp.pi)}[convention]
    claim = f"F({k}) is the Fourier transform of f({x}) in the '{convention}' convention"
    fx = sp.lambdify(x, f, "mpmath")
    Fk = sp.lambdify(k, F, "mpmath")
    for kv in test_k:
        kv = mp.mpf(kv)
        val = N * mp.quad(lambda t: fx(t) * mp.e ** (-1j * s * kv * t), [-mp.inf, 0, mp.inf])
        want = Fk(kv)
        if abs(val - want) > 1e-10 * max(1, abs(val)):
            return refuted("check_fourier_pair", claim, {"k": float(kv), "numeric_transform": mp.nstr(val, 12), "claimed_F": mp.nstr(want, 12)},
                           evidence="mpmath quadrature", detail="check the normalisation convention (factors of 2 pi, sqrt(2 pi)) and the sign in the exponent")
    return consistent("check_fourier_pair", claim, f"agrees at k = {list(test_k)} to 1e-10", caveat="Sampled k values; f must be integrable.")
