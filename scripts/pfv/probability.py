"""pfv.probability: exact probability, expectation and Markov chains (Fractions; no sampling unless stated).

Exhaustive enumeration over a finite sample space gives EXACT rational probabilities, so a wrong claimed probability is
REFUTED by the exact value. Monte Carlo is CONSISTENT only and never refutes unless the gap is many standard errors.
"""
from __future__ import annotations

import itertools
import math
from fractions import Fraction
from typing import Callable, Iterable, Sequence

import numpy as np
import sympy as sp

from .core import Result, verified, consistent, inconclusive, claimed_value_result
from .core import refuted as _refuted
from functools import partial as _partial

refuted = _partial(_refuted, evidence="exact rational enumeration")


def enumerate_probability(outcomes: Iterable, event: Callable, weight: Callable | None = None) -> Fraction:
    """P(event) over a finite space; outcomes equally likely unless weight(outcome) is given (Fractions)."""
    tot = Fraction(0); hit = Fraction(0)
    for o in outcomes:
        w = Fraction(1) if weight is None else Fraction(weight(o))
        tot += w
        if event(o):
            hit += w
    return hit / tot


def check_probability(outcomes: Iterable, event: Callable, claimed, weight: Callable | None = None, claim: str = "") -> Result:
    """Exact P(event) by exhaustive enumeration of a finite outcome space. `claimed` may be '1/6', a Fraction or an int
    (VERIFIED/REFUTED are decisive), or a float: a float within 1e-9 of the exact value is CONSISTENT (it is an
    approximation, not the exact value), one further away is REFUTED (0.167 is REFUTED for 1/6)."""
    outcomes = list(outcomes)
    p = enumerate_probability(outcomes, event, weight)
    claim = claim or f"P(event) = {claimed}"
    return claimed_value_result("check_probability", claim, sp.Rational(p.numerator, p.denominator), claimed,
                                f"exhaustive enumeration of {len(outcomes)} outcomes", exact=str(p), as_float=float(p))


def check_conditional(outcomes: Iterable, event: Callable, given: Callable, claimed, weight: Callable | None = None) -> Result:
    """P(event | given) by enumeration. The classic error is to condition on the wrong event (two-children, Monty Hall)."""
    outcomes = [o for o in outcomes]
    sub = [o for o in outcomes if given(o)]
    if not sub:
        return inconclusive("check_conditional", "P(A|B)", "the conditioning event has probability 0")
    p = enumerate_probability(sub, event, weight)
    claim = f"P(A | B) = {claimed}"
    return claimed_value_result("check_conditional", claim, sp.Rational(p.numerator, p.denominator), claimed,
                                f"enumerated {len(sub)} of {len(outcomes)} outcomes satisfying B", exact=str(p), as_float=float(p))


def check_expectation(outcomes: Iterable, value: Callable, claimed, weight: Callable | None = None) -> Result:
    """Exact E[value] over a finite outcome space by enumeration (rational arithmetic); `claimed` is read as an exact rational."""
    outcomes = list(outcomes)
    tot = Fraction(0); acc = Fraction(0)
    for o in outcomes:
        w = Fraction(1) if weight is None else Fraction(weight(o))
        tot += w; acc += w * Fraction(value(o))
    e = acc / tot
    claim = f"E[X] = {claimed}"
    return claimed_value_result("check_expectation", claim, sp.Rational(e.numerator, e.denominator), claimed,
                                f"exhaustive over {len(outcomes)} outcomes", exact=str(e), as_float=float(e))


def check_pdf(pdf, var, lo, hi, mean=None, variance=None) -> Result:
    """A density on [lo, hi]: non-negative, integrates to 1; optional exact mean/variance (symbolic integrals)."""
    from .analysis import _S, check_inequality, check_integral
    f, x = _S(pdf), _S(var)
    lo, hi = _S(lo), _S(hi)
    claim = f"{f} is a probability density on [{lo}, {hi}]"
    norm = check_integral(f, x, lo, hi, 1)
    if norm.refuted:
        return refuted("check_pdf", claim, norm.witness, evidence=norm.evidence, detail="does not integrate to 1")
    if norm.verdict not in ("VERIFIED", "CONSISTENT"):
        return inconclusive("check_pdf", claim, "normalisation undecided: " + norm.detail)
    nonneg, wit = _nonnegative(f, x, lo, hi)
    if nonneg is False:
        return refuted("check_pdf", claim, wit, evidence="exact evaluation at the witness point", detail="takes negative values")
    sampled_only = nonneg is None
    out = []
    if mean is not None:
        m = check_integral(x * f, x, lo, hi, mean)
        if m.refuted:
            return refuted("check_pdf", claim, m.witness, evidence=m.evidence, detail="wrong mean")
        out.append("mean ok")
    if variance is not None:
        mu = sp.integrate(x * f, (x, lo, hi))
        v = check_integral((x - mu) ** 2 * f, x, lo, hi, variance)
        if v.refuted:
            return refuted("check_pdf", claim, v.witness, evidence=v.evidence, detail="wrong variance")
        out.append("variance ok")
    note = "normalised" + (" (non-negativity only sampled)" if sampled_only else " and non-negative") + ("; " + ", ".join(out) if out else "")
    if norm.verified and not sampled_only:
        return verified("check_pdf", claim, note)
    return consistent("check_pdf", claim, note, caveat="Part of the check was numerical." if sampled_only else "Normalisation was numerical.")


def _nonnegative(f, x, lo, hi):
    """(True, None) proven f >= 0 on [lo, hi]; (False, witness) f < 0 somewhere; (None, None) undecided exactly but no negative sample found."""
    dom = sp.Interval(lo, hi)
    try:
        neg = sp.solveset(f < 0, x, dom)
    except Exception:
        neg = None
    if neg is sp.S.EmptySet:
        return True, None
    if neg is not None and not isinstance(neg, sp.ConditionSet):
        pts = []
        for part in (neg.args if isinstance(neg, sp.Union) else [neg]):
            if isinstance(part, sp.Interval):
                a, b = part.start, part.end
                pts.append((a + b) / 2 if a.is_finite and b.is_finite else (a + 1 if a.is_finite else (b - 1 if b.is_finite else sp.Integer(0))))
            elif isinstance(part, sp.FiniteSet):
                continue
        for q in pts:
            try:
                v = f.subs(x, q)
                if sp.simplify(v) < 0:
                    return False, {str(x): str(q), "pdf_value": str(sp.simplify(v))}
            except Exception:
                pass
    # sampled fallback: map the support to a finite grid
    import random
    rng = random.Random(5)
    for _ in range(400):
        u = sp.Rational(rng.randint(1, 999), 1000)
        if lo.is_finite and hi.is_finite:
            q = lo + (hi - lo) * u
        elif lo.is_finite:
            q = lo + u / (1 - u)
        elif hi.is_finite:
            q = hi - u / (1 - u)
        else:
            q = (2 * u - 1) / (u * (1 - u))
        try:
            v = sp.N(f.subs(x, q), 40)
            if v.is_real and v < -sp.Float("1e-30"):
                return False, {str(x): str(q), "pdf_value": str(v)}
        except Exception:
            continue
    return None, None


def _exactify(M):
    """(Matrix with Floats replaced by nearby simple rationals, had_floats)."""
    M = sp.Matrix(M)
    had = any(isinstance(x, sp.Float) for x in M)
    if had:
        M = M.applyfunc(lambda x: sp.nsimplify(x, rational=True, tolerance=1e-12) if isinstance(x, sp.Float) else x)
    return M, had


def check_stochastic_matrix(P, kind: str = "row") -> Result:
    """Is P a square row- (or column-) stochastic matrix: nonnegative entries and every row (column) summing to exactly 1? Float input is read as the nearby simple rationals and can then only reach CONSISTENT."""
    P, inexact = _exactify(P)
    claim = f"matrix is {kind}-stochastic"
    if P.rows != P.cols:
        return refuted("check_stochastic_matrix", claim, {"shape": list(P.shape)}, detail="a transition matrix must be square")
    if any(x < 0 for x in P):
        return refuted("check_stochastic_matrix", claim, "negative entry")
    sums = [sum(P.row(i)) for i in range(P.rows)] if kind == "row" else [sum(P.col(j)) for j in range(P.cols)]
    if any(sp.simplify(s - 1) != 0 for s in sums):
        return refuted("check_stochastic_matrix", claim, {"sums": [str(s) for s in sums]})
    if inexact:
        return consistent("check_stochastic_matrix", claim, "non-negative entries, sums equal 1 after reading the floats as simple rationals", caveat="Floating-point input; not exact.")
    return verified("check_stochastic_matrix", claim, "non-negative entries and all sums equal 1 (exact)")


def stationary_distribution(P):
    """The unique stationary row vector pi (pi P = pi, sum pi = 1) of an irreducible chain, exactly; raises if the solution is not unique."""
    P = sp.Matrix(P)
    n = P.rows
    A = (P.T - sp.eye(n)).col_join(sp.ones(1, n))
    b = sp.zeros(n, 1).col_join(sp.Matrix([1]))
    sol = A.gauss_jordan_solve(b)[0]
    return sol


def check_stationary(P, pi, claimed_unique: bool | None = None) -> Result:
    """pi P = pi, sum pi = 1, pi >= 0 (exact); optionally also uniqueness (the eigenvalue-1 eigenspace is one-dimensional). P must be a stochastic matrix, else INCONCLUSIVE. Float input can only reach CONSISTENT."""
    P, inx1 = _exactify(P)
    pi, inx2 = _exactify(pi)
    inexact = inx1 or inx2
    claim = f"pi = {list(pi)} is stationary"
    st = check_stochastic_matrix(P)
    if not st.consistent:
        return inconclusive("check_stationary", claim, "P is not a stochastic matrix: " + (st.detail or str(st.witness)))
    pi = pi.reshape(1, P.rows)
    if sp.simplify(sum(pi) - 1) != 0 or any(sp.simplify(x) < 0 for x in pi):
        return refuted("check_stationary", claim, "not a probability vector")
    resid = (pi * P - pi).applyfunc(sp.simplify)
    if resid != sp.zeros(1, P.rows):
        return refuted("check_stationary", claim, {"pi P - pi": str(resid)})
    dim = len((P.T - sp.eye(P.rows)).nullspace())
    if claimed_unique is not None and (dim == 1) != claimed_unique:
        return refuted("check_stationary", claim, {"dimension_of_stationary_space": dim}, detail="uniqueness claim wrong (reducible chain has several stationary distributions)")
    if inexact:
        return consistent("check_stationary", claim, f"pi P = pi after reading floats as simple rationals; stationary space has dimension {dim}", caveat="Floating-point input; not exact.")
    return verified("check_stationary", claim, f"pi P = pi exactly; stationary space has dimension {dim}")


def monte_carlo_probability(sampler: Callable, event: Callable, claimed: float, n: int = 200000, seed: int = 0, z: float = 6.0) -> Result:
    """CONSISTENT unless the estimate is more than z standard errors from the claim (then REFUTED with the numbers)."""
    rng = np.random.default_rng(seed)
    hits = sum(1 for _ in range(n) if event(sampler(rng)))
    p = hits / n
    se = math.sqrt(max(p * (1 - p), 1e-12) / n)
    claim = f"P = {claimed}"
    if abs(p - claimed) > z * se:
        return refuted("monte_carlo_probability", claim, {"estimate": p, "std_error": se, "z": abs(p - claimed) / se}, evidence=f"{n} Monte Carlo samples")
    return consistent("monte_carlo_probability", claim, f"estimate {p:.5f} +- {se:.5f} ({n} samples)", caveat="Sampling error; use exact enumeration when the space is finite.")
