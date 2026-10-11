"""pfv.derivation: check a derivation step by step and name the FIRST wrong step.

Two kinds of chain:
  * expression chains   e0 = e1 = e2 = ...  (each step claims equality with the previous one)
  * equation chains     E0 -> E1 -> E2 ...  (each step claims to follow from the previous one; solution sets are compared)

An equation step can be an implication (solutions may be gained, e.g. squaring) or an equivalence. Losing a solution is
always an error. Gaining one is legal for an implication but the final candidates must then be checked in the ORIGINAL equation.
"""
from __future__ import annotations

from typing import Sequence

import sympy as sp

from .core import Result, verified, consistent, inconclusive, timeout, CheckTimeout
from .core import refuted as _refuted
from functools import partial as _partial
from .analysis import check_identity, _S

refuted = _partial(_refuted, evidence="first failing step, checked symbolically then numerically at 50 digits")


def check_chain(steps: Sequence, domain="positive", labels: Sequence[str] | None = None) -> Result:
    """steps[i] == steps[i+1] for every i. Returns REFUTED naming the first step that breaks (1-based), with a point."""
    exprs = [_S(s) for s in steps]
    labels = list(labels) if labels else [f"step {i + 1}" for i in range(len(exprs))]
    claim = " = ".join(str(e) for e in exprs) if len(exprs) <= 4 else f"chain of {len(exprs)} expressions"
    weak = []
    for i in range(len(exprs) - 1):
        r = check_identity(exprs[i], exprs[i + 1], domain, claim=f"{exprs[i]} = {exprs[i + 1]}")
        if r.refuted:
            return refuted("check_chain", claim, {"first_bad_transition": f"{labels[i]} -> {labels[i + 1]}", "from": str(exprs[i]),
                                                  "to": str(exprs[i + 1]), "at": r.witness},
                           detail=r.detail)
        if r.verdict != "VERIFIED":
            weak.append(i)
    if weak:
        return consistent("check_chain", claim, f"every transition agrees at 12 rational points; {len(weak)} not closed symbolically (transitions {[w + 1 for w in weak]})",
                          caveat="Sampled for those transitions.")
    return verified("check_chain", claim, f"every transition simplifies to an exact identity (symbols assumed {'positive' if domain in ('positive', 'unit') else 'real' if domain == 'real' else 'in ' + str(domain)})")


def _parse_eq(e):
    if isinstance(e, sp.Equality):
        return e
    if isinstance(e, str):
        if "=" in e:
            l, r = e.split("=", 1)
            return sp.Eq(_S(l), _S(r))
        return sp.Eq(_S(e), 0)
    return sp.Eq(_S(e), 0)


def solution_set(eq, var, domain=sp.S.Reals):
    eq = _parse_eq(eq)
    return sp.solveset(eq, var, domain=domain)


def check_equation_chain(equations: Sequence, var, domain=sp.S.Reals, mode: str = "implies", seconds: float = 30, claimed=None) -> Result:
    """equations[0] is the original equation; each later one is claimed to follow from the previous.

    mode='implies'    : Sol(E_i) must be a subset of Sol(E_{i+1})  (nothing lost; extra roots reported)
    mode='equivalent' : Sol(E_i) == Sol(E_{i+1})
    The final solution set is compared with the original: extraneous roots are listed.
    """
    var = _S(var)
    eqs = [_parse_eq(e) for e in equations]
    claim = f"{len(eqs)}-step solution of {eqs[0]} for {var}"
    sols = []
    try:
        with timeout(seconds):
            for e in eqs:
                sols.append(solution_set(e, var, domain))
    except CheckTimeout:
        return inconclusive("check_equation_chain", claim, "solveset timed out")
    except Exception as ex:
        return inconclusive("check_equation_chain", claim, f"solveset failed: {type(ex).__name__}: {ex}")
    if any(isinstance(s, sp.ConditionSet) for s in sols):
        return inconclusive("check_equation_chain", claim, "sympy returned a ConditionSet (cannot solve exactly): " + "; ".join(str(s) for s in sols))
    extraneous = []
    for i in range(len(eqs) - 1):
        prev, nxt = sols[i], sols[i + 1]
        sub = prev.is_subset(nxt)
        if sub is None:
            return inconclusive("check_equation_chain", claim, f"cannot decide whether Sol(step {i + 1}) is contained in Sol(step {i + 2}) (infinite or symbolic solution sets): {prev} vs {nxt}")
        lost = sp.S.EmptySet if sub else (prev - nxt)
        gained = nxt - prev
        if lost != sp.S.EmptySet:
            return refuted("check_equation_chain", claim, {"step": i + 2, "equation": str(eqs[i + 1]), "solutions_lost": str(lost)},
                           detail=f"step {i + 2} loses the solution(s) {lost} of step {i + 1} (e.g. dividing by an expression that can be 0)")
        if mode == "equivalent" and gained != sp.S.EmptySet:
            return refuted("check_equation_chain", claim, {"step": i + 2, "equation": str(eqs[i + 1]), "solutions_gained": str(gained)},
                           detail=f"step {i + 2} is not an equivalence: it introduces {gained} (e.g. squaring both sides)")
        if gained != sp.S.EmptySet:
            extraneous.append((i + 2, gained))
    final_vs_orig = sols[-1] - sols[0]
    if claimed is not None:
        cl = sp.FiniteSet(*[_S(c) for c in claimed])
        extra, missing = cl - sols[0], sols[0] - cl
        if extra != sp.S.EmptySet or missing != sp.S.EmptySet:
            return refuted("check_equation_chain", claim, {"claimed_but_not_solutions": str(extra), "solutions_not_claimed": str(missing)},
                           evidence="exact solution set of the ORIGINAL equation",
                           detail=f"true solution set of the original equation is {sols[0]}; claimed {cl}")
    note = f"original solutions {sols[0]}; final {sols[-1]}"
    if final_vs_orig != sp.S.EmptySet:
        note += f"; EXTRANEOUS in the final answer: {final_vs_orig} (steps that introduced roots: {[s for s, _ in extraneous]}). Substitute candidates back into the original equation."
    return verified("check_equation_chain", claim, "no step loses a solution" + ("; every step is an equivalence" if mode == "equivalent" else ""),
                    detail=note, original=str(sols[0]), final=str(sols[-1]), extraneous=str(final_vs_orig))


def check_candidates(equation, var, candidates) -> Result:
    """Substitute candidate roots back into the ORIGINAL equation (the cure for extraneous roots)."""
    eq = _parse_eq(equation)
    var = _S(var)
    bad = []
    for c in candidates:
        c = _S(c)
        v = sp.simplify((eq.lhs - eq.rhs).subs(var, c))
        if v != 0 or v.has(sp.zoo, sp.nan, sp.oo):
            bad.append((c, v))
    claim = f"{list(candidates)} all solve {eq}"
    if bad:
        return refuted("check_candidates", claim, {str(c): f"residual {v}" for c, v in bad}, evidence="exact substitution into the original equation")
    return verified("check_candidates", claim, "exact substitution into the original equation gives 0 for every candidate")


def check_final_answer(computed_expr, claimed, domain="positive") -> Result:
    """Recompute the final answer yourself, then compare with the answer a solution/paper claims."""
    r = check_identity(computed_expr, claimed, domain, claim=f"final answer {claimed} equals recomputed {computed_expr}")
    r.check = "check_final_answer"
    return r
