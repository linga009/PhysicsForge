"""pfv.algebra: polynomials, algebraic numbers, ideals (exact, over Q unless stated).

All answers are exact (sympy polynomial arithmetic, Groebner bases, minimal polynomials), so VERIFIED/REFUTED are decisive.
Real-root counting uses Sturm sequences; irreducibility over Q uses full factorisation; algebraic-number identities are
decided by the minimal polynomial of (lhs - rhs), which is exact for radicals and roots of unity.
"""
from __future__ import annotations

import sympy as sp

from .core import Result, verified, consistent, inconclusive, timeout, CheckTimeout, unify
from .core import refuted as _refuted
from functools import partial as _partial
from .analysis import _S

refuted = _partial(_refuted, evidence="exact polynomial arithmetic")


def check_polynomial_identity(lhs, rhs, claim: str = "") -> Result:
    """lhs == rhs as polynomials/rational functions: expand and cancel to exact zero (decisive both ways)."""
    L, R = unify(_S(lhs), _S(rhs))
    d = sp.cancel(sp.together(sp.expand(L - R)))
    claim = claim or f"{L} == {R}"
    if d == 0:
        return verified("check_polynomial_identity", claim, "expand + cancel gives exactly 0")
    if not d.is_rational_function(*d.free_symbols):
        return inconclusive("check_polynomial_identity", claim, f"not a rational function; residue {d}")
    return refuted("check_polynomial_identity", claim, {"lhs - rhs": str(sp.factor(d))})


def _pick_var(P, var):
    """The variable of a univariate question: explicit `var`, else `x` if present, else the only free symbol, else None."""
    if var is not None:
        return _S(var)
    fs = P.free_symbols
    xs = [s_ for s_ in fs if s_.name == "x"]
    if xs:
        return xs[0]
    if len(fs) == 1:
        return next(iter(fs))
    return None


def check_factorization_poly(poly, factors, var=None, modulus: int | None = None, complete: bool = True) -> Result:
    """Claimed factorisation of `poly` into `factors` over Q (or F_p if `modulus`). Product must be exact; with complete=True (default) every factor must also be irreducible, else REFUTED with the reducible factor."""
    P = _S(poly)
    claim = f"{P} = " + " * ".join(f"({f})" for f in factors)
    v = _pick_var(P, var)
    if v is None:
        return inconclusive("check_factorization_poly", claim, "several symbols and no variable given; pass var=")
    P, v, *fs = unify(P, v, *[_S(f) for f in factors])
    prod = sp.expand(sp.prod(fs))
    if modulus:
        diff = sp.Poly(prod - P, v, modulus=modulus)
        if not diff.is_zero:
            return refuted("check_factorization_poly", claim, {"product": str(prod)}, detail=f"product differs from the polynomial mod {modulus}")
    elif sp.expand(prod - P) != 0:
        return refuted("check_factorization_poly", claim, {"product": str(prod)}, detail="product of claimed factors is not the polynomial")
    if complete:
        for f in fs:
            fp = sp.Poly(f, v, modulus=modulus) if modulus else sp.Poly(f, v)
            if fp.degree() > 1 and not fp.is_irreducible:
                return refuted("check_factorization_poly", claim,
                               {"reducible_factor": str(f), "its_factorisation": str(sp.factor(f)) if not modulus else str(fp.factor_list())},
                               detail="the product is right but the factorisation is not complete")
    return verified("check_factorization_poly", claim, "product exact" + ("; every factor irreducible" if complete else "") + (f" (mod {modulus})" if modulus else " (over Q)"))


def check_irreducible(poly, claimed: bool, var=None, modulus: int | None = None) -> Result:
    """Is `poly` irreducible over Q (or F_p if `modulus`)? Decided by complete factorisation (exact)."""
    P = _S(poly)
    claim = f"{P} is {'' if claimed else 'not '}irreducible" + (f" mod {modulus}" if modulus else " over Q")
    v = _pick_var(P, var)
    if v is None:
        return inconclusive("check_irreducible", claim, "several symbols and no variable given; pass var=")
    P, v = unify(P, v)
    fp = sp.Poly(P, v, modulus=modulus) if modulus else sp.Poly(P, v)
    truth = fp.is_irreducible
    if truth == claimed:
        return verified("check_irreducible", claim, "complete factorisation computed", factors=str(sp.factor_list(P)) if not modulus else "")
    return refuted("check_irreducible", claim, {"factorisation": str(sp.factor(P)) if not modulus else str(fp.factor_list())})


def check_real_root_count(poly, claimed: int, var=None, multiplicity: bool = False) -> Result:
    """Number of real roots of `poly`, counted as DISTINCT roots (Sturm, exact) or with multiplicity if multiplicity=True."""
    P = _S(poly)
    v = _pick_var(P, var)
    claim = f"{P} has {claimed} real roots" + (" (with multiplicity)" if multiplicity else " (distinct)")
    if v is None:
        return inconclusive("check_real_root_count", claim, "several symbols and no variable given; pass var=")
    P, v = unify(P, v)
    pp = sp.Poly(P, v)
    n = len(pp.real_roots()) if multiplicity else pp.count_roots()
    if n == claimed:
        return verified("check_real_root_count", claim, "Sturm sequence (exact)")
    return refuted("check_real_root_count", claim, {"true_count": n, "roots": [str(r) for r in pp.real_roots()]})


def check_algebraic_identity(lhs, rhs) -> Result:
    """Is lhs == rhs for algebraic numbers (radicals, roots of unity)? Decided exactly: minimal polynomial of lhs - rhs is x iff equal."""
    L, R = _S(lhs), _S(rhs)
    claim = f"{L} == {R}"
    d = L - R
    try:
        with timeout(30):
            if sp.simplify(d) == 0:
                return verified("check_algebraic_identity", claim, "exact simplification to 0")
            x = sp.Symbol("x")
            mp = sp.minimal_polynomial(d, x)
        if mp == x:
            return verified("check_algebraic_identity", claim, "minimal polynomial of (lhs - rhs) is x, so it is 0")
        return refuted("check_algebraic_identity", claim, {"lhs - rhs": str(sp.N(d, 20)), "minimal_polynomial": str(mp)})
    except CheckTimeout:
        return inconclusive("check_algebraic_identity", claim, "timed out")
    except Exception as e:
        v = sp.N(d, 60)
        if abs(v) > sp.Float("1e-40"):
            return refuted("check_algebraic_identity", claim, {"lhs - rhs": str(sp.N(d, 20))}, evidence="60-digit evaluation")
        return inconclusive("check_algebraic_identity", claim, f"minimal polynomial unavailable ({type(e).__name__}); 60-digit evaluation is {sp.N(d, 3)}")


def check_minimal_polynomial(alpha, claimed, var="x") -> Result:
    """Is `claimed` the minimal polynomial over Q of the algebraic number `alpha`? Decided exactly (up to a constant factor)."""
    x = sp.Symbol(str(var))
    a = _S(alpha)
    c = _S(claimed)
    claim = f"minimal polynomial of {a} is {c}"
    c = c.xreplace({s_: x for s_ in c.free_symbols if s_.name == x.name})
    if c.free_symbols - {x}:
        return inconclusive("check_minimal_polynomial", claim, f"claimed polynomial has symbols other than {x}: {sorted(map(str, c.free_symbols - {x}))}")
    try:
        with timeout(60):
            mp = sp.minimal_polynomial(a, x)
            cp = sp.Poly(c, x)
    except CheckTimeout:
        return inconclusive("check_minimal_polynomial", claim, "timed out")
    except Exception as e:
        return inconclusive("check_minimal_polynomial", claim, f"{type(e).__name__}: {e}")
    if cp.is_zero:
        return refuted("check_minimal_polynomial", claim, {"true_minimal_polynomial": str(mp)}, detail="the zero polynomial")
    if sp.expand(mp - cp.monic().as_expr()) == 0:
        return verified("check_minimal_polynomial", claim, "exact (sympy minimal_polynomial, compared as monic polynomials)")
    return refuted("check_minimal_polynomial", claim, {"true_minimal_polynomial": str(mp)},
                   detail="claimed polynomial differs from the minimal polynomial (it may still vanish at alpha but not be minimal)")


def check_ideal_membership(f, generators, variables, claimed: bool = True, order: str = "grevlex") -> Result:
    """f in <g1,...,gk> over Q? Decided by reducing f modulo a Groebner basis (exact)."""
    vs = [_S(v) for v in variables]
    f_, *gs = unify(_S(f), *[_S(g) for g in generators])
    G = sp.groebner(gs, *vs, order=order)
    _, rem = G.reduce(f_)
    member = sp.expand(rem) == 0
    claim = f"{f_} {'in' if claimed else 'not in'} <{', '.join(str(g) for g in gs)}>"
    if member == claimed:
        return verified("check_ideal_membership", claim, "remainder modulo the Groebner basis " + ("is 0" if member else f"is {rem} != 0"), basis=[str(g) for g in G.exprs])
    return refuted("check_ideal_membership", claim, {"remainder": str(rem)})


def _is_zero(e):
    """True / False / None (unknown). Exact for rational functions and algebraic numbers; never trusts a float alone to say True."""
    e = sp.sympify(e)
    if e == 0:
        return True
    try:
        if sp.simplify(e) == 0:
            return True
    except Exception:
        pass
    if e.free_symbols:
        return None
    try:
        v = sp.N(e, 60)
        if abs(v) > sp.Float("1e-40"):
            return False
        x_ = sp.Symbol("_z")
        return True if sp.minimal_polynomial(e, x_) == x_ else None
    except Exception:
        return None


def check_system_solutions(equations, variables, claimed_solutions) -> Result:
    """Is `claimed_solutions` (list of points) exactly the set of COMPLEX solutions of a zero-dimensional polynomial system? Every point must satisfy the system and the solution count must match (exact, via solve)."""
    vs = [_S(v) for v in variables]
    raw = [_S(e) for e in equations]
    eqs = unify(*[e.lhs - e.rhs if isinstance(e, sp.Equality) else e for e in raw])
    eqs = eqs if isinstance(eqs, list) else [eqs]
    claim = f"solution set of the system = {claimed_solutions}"
    from .core import to_exact
    inexact = False
    pts = []
    for pt in claimed_solutions:
        row = []
        for x in pt:
            v, i = to_exact(x) if not isinstance(x, str) else (_S(x), False)
            inexact = inexact or i
            row.append(v)
        pts.append(row)
    if inexact:
        from .core import cap_inexact
        res = _check_system_solutions_exact(eqs, vs, pts, claim)
        return cap_inexact(res, "claimed solutions")
    return _check_system_solutions_exact(eqs, vs, pts, claim)


def _check_system_solutions_exact(eqs, vs, pts, claim) -> Result:
    unknown = False
    for pt in pts:
        sub = dict(zip(vs, pt))
        for e in eqs:
            z = _is_zero(e.subs(sub))
            if z is False:
                return refuted("check_system_solutions", claim, {"point_not_a_solution": [str(x) for x in pt], "equation": str(e)})
            if z is None:
                unknown = True
    try:
        with timeout(60):
            sols = sp.solve(eqs, vs, dict=True)
    except CheckTimeout:
        return inconclusive("check_system_solutions", claim, "solve timed out")
    except Exception as e:
        return inconclusive("check_system_solutions", claim, f"{type(e).__name__}: {e}")
    if any(set(vs) & set(sp.sympify(val).free_symbols) for sl in sols for val in sl.values()) or any(len(sl) < len(vs) for sl in sols):
        return inconclusive("check_system_solutions", claim, "the system has a positive-dimensional solution set; a finite list cannot be compared")
    n_claimed = len({tuple(sp.simplify(x) for x in pt) for pt in pts})
    if len(sols) != n_claimed:
        return refuted("check_system_solutions", claim, {"all_solutions": [{str(k): str(v) for k, v in sl.items()} for sl in sols]},
                       detail=f"the claimed set has {n_claimed} distinct points, the system has {len(sols)} (complex solutions counted)")
    if unknown:
        return inconclusive("check_system_solutions", claim, "could not decide exactly that every claimed point satisfies the system")
    return verified("check_system_solutions", claim, "every claimed point satisfies the system and the number of distinct solutions matches")


def check_discriminant(poly, claimed, var=None) -> Result:
    """Is disc(poly) w.r.t. `var` equal to `claimed`? If `var` is omitted, `x` is used when present, else the only symbol; otherwise INCONCLUSIVE."""
    P = _S(poly)
    claim = f"disc({P}) = {claimed}"
    if var is not None:
        v = _S(var)
    else:
        fs = P.free_symbols
        xs = [s_ for s_ in fs if s_.name == "x"]
        if xs:
            v = xs[0]
        elif len(fs) == 1:
            v = next(iter(fs))
        else:
            return inconclusive("check_discriminant", claim, "several symbols and no variable given; pass var=")
    P, v, C = unify(P, v, _S(claimed))
    try:
        d = sp.discriminant(P, v)
    except Exception as e:
        return inconclusive("check_discriminant", claim, f"{type(e).__name__}: {e}")
    if sp.expand(sp.simplify(d - C)) == 0:
        return verified("check_discriminant", claim, "exact")
    return refuted("check_discriminant", claim, {"true_discriminant": str(d)})
