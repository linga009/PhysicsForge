"""pfv.mechanics: classical mechanics, Hamiltonian structure, thermodynamics and response theory.

Symbolic checks are exact. Numerical integrations report drift of a conserved quantity at TWO tolerances: a real
violation persists when the integrator is tightened, integrator error does not.
"""
from __future__ import annotations

import itertools
from typing import Callable, Sequence

import numpy as np
import sympy as sp
from sympy import diff, simplify

from .core import Result, verified, consistent, inconclusive, timeout, CheckTimeout, unify, unknown_symbols
from .core import refuted as _refuted
from functools import partial as _partial
from .analysis import _S

refuted = _partial(_refuted, evidence="exact symbolic residue")


# --------------------------------------------------------------------------
# Lagrangian / Hamiltonian mechanics
# --------------------------------------------------------------------------
def euler_lagrange(L, qs: Sequence, t) -> list:
    """List of expressions E_i = d/dt(dL/dqdot_i) - dL/dq_i (the EOM are E_i = 0). qs are sympy Functions of t."""
    out = []
    for q in qs:
        qd = diff(q, t)
        out.append(sp.expand(diff(diff(L, qd), t) - diff(L, q)))
    return out


def check_eom(L, qs, t, claimed, domain_note: str = "") -> Result:
    """claimed: list of equations (Eq or expression = 0) in the same order as qs. Each must equal the EL expression
    up to a constant non-zero factor (an overall factor like m is allowed; a wrong sign inside is not)."""
    E = euler_lagrange(L, qs, t)
    claim = "claimed equations of motion follow from L"
    for i, (e, c) in enumerate(zip(E, claimed)):
        c = c.lhs - c.rhs if isinstance(c, sp.Equality) else _S(c)
        unk = unknown_symbols(c, L, list(qs), [t])
        if unk:
            return inconclusive("check_eom", claim, f"claimed equation {i} uses symbols {unk} that are not in the Lagrangian (e.g. omega defined elsewhere): substitute them first")
        ratio = sp.simplify(c / e) if e != 0 else None
        if e == 0:
            if sp.simplify(c) != 0:
                return refuted("check_eom", claim, {"coordinate": str(qs[i]), "EL": "0", "claimed": str(c)})
            continue
        if ratio is None or ratio.free_symbols & {t} or ratio == 0 or ratio.has(sp.Derivative):
            return refuted("check_eom", claim, {"coordinate": str(qs[i]), "EL_expression": str(e), "claimed": str(c)},
                           detail="claimed equation is not a constant multiple of the Euler-Lagrange expression")
    return verified("check_eom", claim, "Euler-Lagrange expressions match the claimed equations up to constant factors", EL=[str(e) for e in E])


def legendre_hamiltonian(L, qs, t, ps=None):
    """H(q, p) for L(q, qdot): solve p = dL/dqdot for qdot, H = p qdot - L. Returns (H, p_symbols, q_symbols)."""
    qsyms = [sp.Symbol(str(q.func)) for q in qs]
    qdsyms = [sp.Symbol(str(q.func) + "_dot") for q in qs]
    sub = {}
    for q, qs_, qd_ in zip(qs, qsyms, qdsyms):
        sub[diff(q, t)] = qd_
    for q, qs_ in zip(qs, qsyms):
        sub[q] = qs_
    Ls = L.subs({diff(q, t): qd for q, qd in zip(qs, qdsyms)}).subs({q: s for q, s in zip(qs, qsyms)})
    ps = ps or [sp.Symbol("p_" + str(q.func)) for q in qs]
    eqs = [sp.Eq(p, diff(Ls, qd)) for p, qd in zip(ps, qdsyms)]
    sol = sp.solve(eqs, qdsyms, dict=True)
    if not sol:
        raise ValueError("Legendre transform failed (singular Hessian: constrained system)")
    sol = sol[0]
    H = sp.simplify(sum(p * sol[qd] for p, qd in zip(ps, qdsyms)) - Ls.subs(sol))
    return H, ps, qsyms


def poisson_bracket(f, g, qs: Sequence, ps: Sequence):
    return sum(diff(f, q) * diff(g, p) - diff(f, p) * diff(g, q) for q, p in zip(qs, ps))


def check_poisson(f, g, qs, ps, claimed) -> Result:
    """Poisson bracket {f, g} against a claimed expression; unknown symbols in the claim give INCONCLUSIVE, not REFUTED."""
    f_, g_, c_, *_rest = unify(_S(f), _S(g), _S(claimed), list(qs) + list(ps))
    pb = simplify(poisson_bracket(f_, g_, qs, ps))
    claim = f"{{{f}, {g}}} = {claimed}"
    unk = unknown_symbols(c_, f_, g_, list(qs) + list(ps), [s_ for s_ in pb.free_symbols])
    if unk:
        return inconclusive("check_poisson", claim, f"claimed expression uses symbols {unk} that do not appear in f, g or the phase space (typo? e.g. px vs p_x)")
    if simplify(pb - c_) == 0:
        return verified("check_poisson", claim, "exact symbolic derivatives")
    return refuted("check_poisson", claim, {"computed": str(pb)})


def check_canonical(Q, P, qs, ps) -> Result:
    """The map (q,p) -> (Q,P) is canonical iff {Q_i,Q_j}={P_i,P_j}=0 and {Q_i,P_j}=delta_ij (equivalently the Jacobian is symplectic)."""
    claim = "(q,p) -> (Q,P) is a canonical transformation"
    n = len(qs)
    Q, P = [_S(x) for x in Q], [_S(x) for x in P]
    for i in range(n):
        for j in range(n):
            if simplify(poisson_bracket(Q[i], P[j], qs, ps) - (1 if i == j else 0)) != 0:
                return refuted("check_canonical", claim, {f"{{Q{i},P{j}}}": str(simplify(poisson_bracket(Q[i], P[j], qs, ps)))})
            if i < j:
                if simplify(poisson_bracket(Q[i], Q[j], qs, ps)) != 0 or simplify(poisson_bracket(P[i], P[j], qs, ps)) != 0:
                    return refuted("check_canonical", claim, {"bracket": f"{{Q{i},Q{j}}} or {{P{i},P{j}}} != 0"})
    return verified("check_canonical", claim, "all fundamental Poisson brackets verified exactly")


def check_conserved_hamiltonian(F, H, qs, ps, t=None) -> Result:
    """dF/dt = {F, H} + dF/dt|explicit = 0."""
    dFdt = poisson_bracket(_S(F), _S(H), qs, ps) + (diff(_S(F), t) if t is not None else 0)
    claim = f"{F} is conserved under H"
    r = simplify(dFdt)
    if r == 0:
        return verified("check_conserved_hamiltonian", claim, "{F,H} + dF/dt = 0 exactly")
    return refuted("check_conserved_hamiltonian", claim, {"dF/dt": str(r)})


def check_conserved_on_shell(Q, L, qs, t) -> Result:
    """Q(q, qdot, t) is conserved on solutions: dQ/dt vanishes after eliminating second derivatives with the EL equations."""
    E = euler_lagrange(L, qs, t)
    qdd = [diff(q, t, 2) for q in qs]
    sol = sp.solve(E, qdd, dict=True)
    claim = f"{Q} is conserved on shell"
    if not sol:
        return inconclusive("check_conserved_on_shell", claim, "could not solve the EL equations for the accelerations")
    dQ = diff(_S(Q), t).subs(sol[0])
    r = simplify(dQ)
    if r == 0:
        return verified("check_conserved_on_shell", claim, "dQ/dt = 0 once the EL equations are imposed")
    return refuted("check_conserved_on_shell", claim, {"dQ/dt on shell": str(r)})


def check_conserved_numeric(rhs: Callable, y0, T: float, invariant: Callable, claim: str = "invariant is conserved",
                            tol: float = 1e-7, args=()) -> Result:
    """Integrate dy/dt = rhs(t, y) with DOP853 at rtol 1e-10 and 1e-13 and report the max drift of invariant(y)."""
    from scipy.integrate import solve_ivp
    drifts = []
    for rtol in (1e-10, 1e-13):
        sol = solve_ivp(rhs, (0, T), np.asarray(y0, float), method="DOP853", rtol=rtol, atol=rtol * 1e-2, dense_output=False, args=args,
                        t_eval=np.linspace(0, T, 400))
        if not sol.success:
            return inconclusive("check_conserved_numeric", claim, f"integration failed: {sol.message}")
        vals = np.array([invariant(sol.y[:, k]) for k in range(sol.y.shape[1])])
        drifts.append(float(np.abs(vals - vals[0]).max() / max(1.0, abs(vals[0]))))
    if drifts[1] > tol:
        return refuted("check_conserved_numeric", claim, {"relative_drift_rtol1e-10": drifts[0], "relative_drift_rtol1e-13": drifts[1]},
                       evidence="drift persists when the integrator tolerance is tightened", detail="not conserved (integrator error would shrink)")
    return consistent("check_conserved_numeric", claim, f"max relative drift {drifts[1]:.2e} over t in [0,{T}] at rtol 1e-13 (and {drifts[0]:.2e} at 1e-10)",
                      caveat="One trajectory only.")


# --------------------------------------------------------------------------
# thermodynamics
# --------------------------------------------------------------------------
def check_homogeneous(f, variables, degree, lam=None) -> Result:
    """f(lambda x) = lambda^degree f(x). Extensivity of S(U,V,N) is degree 1. Catches a Sackur-Tetrode missing 1/N inside the log."""
    f = _S(f)
    lam = lam or sp.Symbol("lambda", positive=True)
    syms = [_S(v) for v in variables]
    scaled = f.subs({v: lam * v for v in syms}, simultaneous=True)
    claim = f"homogeneous of degree {degree} in {syms}"
    # work with positive symbols so logs expand
    pos = {v: sp.Symbol(v.name, positive=True) for v in syms}
    d = sp.simplify(sp.expand_log(sp.expand((scaled - lam ** degree * f).xreplace(pos)), force=True))
    if d == 0:
        return verified("check_homogeneous", claim, "f(lambda x) - lambda^d f(x) simplifies to 0 exactly (positive variables)")
    return refuted("check_homogeneous", claim, {"f(lambda x) - lambda^d f(x)": str(d)}, detail="e.g. an extensive entropy must be degree 1; a leftover log(lambda) term means a missing N in the argument")


def check_euler_relation(U, S, V, N=None, mu=None) -> Result:
    """For U(S,V,N) homogeneous of degree 1: U = T S - P V + mu N with T = U_S, P = -U_V, mu = U_N."""
    U = _S(U); S_, V_ = _S(S), _S(V)
    terms = diff(U, S_) * S_ + diff(U, V_) * V_          # T S + V dU/dV, and dU/dV = -P
    if N is not None:
        terms += diff(U, _S(N)) * _S(N)
    claim = "U = T S - P V + mu N   (T = U_S, P = -U_V, mu = U_N)"
    d = simplify(terms - U)
    if d == 0:
        return verified("check_euler_relation", claim, "exact (U is homogeneous of degree 1)")
    return refuted("check_euler_relation", claim, {"U - (TS - PV + mu N)": str(-d)}, detail="U is not extensive, or a variable is missing")


def check_equation_of_state(S, U, V, N, claimed_P_over_T=None, claimed_inv_T=None) -> Result:
    """From an entropy S(U,V,N): 1/T = dS/dU, P/T = dS/dV; compare claimed forms (e.g. P V = N k T for the ideal gas)."""
    S, U, V, N = unify(_S(S), _S(U), _S(V), _S(N))
    invT, PoT = simplify(diff(S, U)), simplify(diff(S, V))
    claim = "equation of state from entropy"
    claimed_inv_T = None if claimed_inv_T is None else unify(_S(claimed_inv_T), S)[0]
    claimed_P_over_T = None if claimed_P_over_T is None else unify(_S(claimed_P_over_T), S)[0]
    for nm, cl in (("claimed_inv_T", claimed_inv_T), ("claimed_P_over_T", claimed_P_over_T)):
        if cl is not None:
            unk = unknown_symbols(cl, S)
            if unk:
                return inconclusive("check_equation_of_state", claim, f"{nm} uses symbols {unk} that are not in S (typo?)")
    if claimed_inv_T is not None and simplify(invT - claimed_inv_T) != 0:
        return refuted("check_equation_of_state", claim, {"1/T": str(invT), "claimed": str(claimed_inv_T)})
    if claimed_P_over_T is not None and simplify(PoT - claimed_P_over_T) != 0:
        return refuted("check_equation_of_state", claim, {"P/T": str(PoT), "claimed": str(claimed_P_over_T)})
    return verified("check_equation_of_state", claim, "derivatives of S agree exactly", invT=str(invT), PoverT=str(PoT))


def check_concavity(S, variables, point: dict) -> Result:
    """Thermodynamic stability: Hessian of S(U,V,N) negative semidefinite at the point (exact eigenvalue signs)."""
    S = _S(S)
    syms = [_S(v) for v in variables]
    H = sp.hessian(S, syms).subs({_S(k): _S(v) for k, v in point.items()})
    ev = [sp.N(e) for e in H.eigenvals(multiple=True)]
    claim = "S is concave (stable) at the point"
    if all(e <= 1e-12 for e in ev):
        return verified("check_concavity", claim, f"Hessian eigenvalues {[float(e) for e in ev]} <= 0")
    return refuted("check_concavity", claim, {"positive_eigenvalue": float(max(ev))}, evidence="Hessian eigenvalues at the point")


# --------------------------------------------------------------------------
# causality / response
# --------------------------------------------------------------------------
def check_kramers_kronig(chi: Callable[[float], complex], omegas: Sequence[float], cutoff: float = 400.0, tol: float = 1e-5) -> Result:
    """Re chi(w) = (1/pi) P int Im chi(w')/(w' - w) dw' for a causal response function (poles only in the lower half plane).
    Compares the real part computed from Im chi with the stated Re chi at the given frequencies (principal value by
    scipy QUAD weight='cauchy'). A response with an UPPER half-plane pole (acausal / growing) fails."""
    from scipy.integrate import quad
    worst = 0.0
    wbad = None
    for w in omegas:
        f = lambda wp: chi(wp).imag
        a, b = max(-cutoff, w - 50.0), min(cutoff, w + 50.0)
        pv = 0.0
        # split into pieces with the singular point at w handled by 'cauchy' weight on a symmetric window
        win = 40.0
        val1, _ = quad(f, w - win, w + win, weight="cauchy", wvar=w, limit=400)
        val2, _ = quad(lambda x: f(x) / (x - w), -cutoff, w - win, limit=400)
        val3, _ = quad(lambda x: f(x) / (x - w), w + win, cutoff, limit=400)
        re_kk = (val1 + val2 + val3) / np.pi
        err = abs(re_kk - chi(w).real)
        if err > worst:
            worst, wbad = err, w
    claim = "response function satisfies the Kramers-Kronig relations (causal)"
    if worst > tol:
        return refuted("check_kramers_kronig", claim, {"omega": wbad, "max_|Re_KK - Re_chi|": worst}, evidence="numerical principal-value integral",
                       detail="not causal, or the response does not decay fast enough for the finite cutoff (check tails)")
    return consistent("check_kramers_kronig", claim, f"max |Re chi - KK(Im chi)| = {worst:.1e} at {len(omegas)} frequencies",
                      caveat="Finite cutoff and sampled frequencies; chi must decay at infinity (else subtract a constant).")
