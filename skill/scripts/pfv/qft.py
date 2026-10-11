"""pfv.qft: gamma-matrix algebra, trace identities, Lorentz generators and Ward identities (metric +,-,-,-).

Gamma-matrix identities are decided EXACTLY: the two sides are evaluated with symbolic vector components (a proof of the
polynomial identity in that representation; traces and Clifford consequences do not depend on the representation).
If the symbolic evaluation is too large, the identity is tested at random rational points in exact arithmetic: a failure is
still a decisive REFUTED, a pass is only CONSISTENT.

Conventions: eta = diag(1,-1,-1,-1); slash(p) = p_mu gamma^mu; gamma5 = i g0 g1 g2 g3; sigma(m,n) = (i/2)[gamma^m, gamma^n];
eps(a,b,c,d) = eps^{mu nu rho sigma} a_mu b_nu c_rho d_sigma with eps^{0123} = `eps0123` (default +1, for which
tr(g5 a b c d slashes) = -4i eps(a,b,c,d); with eps0123 = -1 the sign is +4i). Textbooks differ on this sign, so state yours. Expressions are Python strings using: gu(m) gamma^m, gl(m) gamma_m, slash, g5, one, tr, dot,
eps, sigma, sum, range, and the names of your vectors and scalars.
"""
from __future__ import annotations

import itertools
import random

import numpy as np
import sympy as sp

from .core import Result, verified, consistent, inconclusive, timeout, CheckTimeout
from .core import refuted as _refuted
from functools import partial as _partial

refuted = _partial(_refuted, evidence="exact rational arithmetic")

ETA = sp.diag(1, -1, -1, -1)
_I = sp.I


def _blk(a, b, c, d):
    return sp.Matrix(sp.BlockMatrix([[a, b], [c, d]]))


def dirac_matrices(rep: str = "dirac"):
    """Return (gammas, g5): exact sympy 4x4 matrices gamma^0..gamma^3 and gamma5 = i g0 g1 g2 g3 for rep in {'dirac','weyl','majorana'} (Peskin conventions)."""
    s0 = sp.eye(2)
    sx = sp.Matrix([[0, 1], [1, 0]])
    sy = sp.Matrix([[0, -_I], [_I, 0]])
    sz = sp.Matrix([[1, 0], [0, -1]])
    z = sp.zeros(2)
    if rep == "dirac":
        g = [_blk(s0, z, z, -s0)] + [_blk(z, s, -s, z) for s in (sx, sy, sz)]
    elif rep == "weyl":
        g = [_blk(z, s0, s0, z)] + [_blk(z, s, -s, z) for s in (sx, sy, sz)]
    elif rep == "majorana":
        g = [_blk(z, sy, sy, z), _blk(_I * sz, z, z, _I * sz), _blk(z, -sy, sy, z), _blk(-_I * sx, z, z, -_I * sx)]
    else:
        raise ValueError("rep must be 'dirac', 'weyl' or 'majorana'")
    g5 = (_I * g[0] * g[1] * g[2] * g[3]).applyfunc(sp.simplify)
    return g, g5


def _mat(m):
    if isinstance(m, str):
        return sp.Matrix(sp.sympify(m))
    return sp.Matrix(m)


def check_clifford(gammas=None, rep: str = "dirac", signature: str = "+---") -> Result:
    """Do the four matrices satisfy {g^mu, g^nu} = 2 eta^{mu nu} (hermiticity of g^0 and anti-hermiticity of g^i, g5^2 = 1, {g5, g^mu} = 0)? Exact. Pass your own `gammas` (list of 4 matrices) or a standard `rep`."""
    name = "check_clifford"
    if gammas is None:
        g, g5 = dirac_matrices(rep)
        label = f"{rep} representation"
    else:
        g = [_mat(m) for m in gammas]
        if len(g) != 4 or any(m.shape != (4, 4) for m in g):
            return inconclusive(name, "custom gamma matrices", "need four 4x4 matrices")
        g5 = (_I * g[0] * g[1] * g[2] * g[3]).applyfunc(sp.simplify)
        label = "supplied matrices"
    eta = sp.diag(*[1 if c == "+" else -1 for c in signature]) if len(signature) == 4 else ETA
    claim = f"{label}: {{g^mu,g^nu}} = 2 eta^(mu nu) with signature {signature}, g5^2 = 1, {{g5,g^mu}} = 0, hermiticity"
    for m, n in itertools.product(range(4), repeat=2):
        d = (g[m] * g[n] + g[n] * g[m] - 2 * eta[m, n] * sp.eye(4)).applyfunc(sp.simplify)
        if d != sp.zeros(4):
            return refuted(name, claim, {"mu": m, "nu": n, "anticommutator_minus_2eta": str(d.tolist())})
    for m in range(4):
        herm = (g[m].H - (g[m] if eta[m, m] == 1 else -g[m])).applyfunc(sp.simplify)
        if herm != sp.zeros(4):
            return refuted(name, claim, {"gamma": m}, detail="gamma^0 must be hermitian and gamma^i anti-hermitian (for +--- ) in a unitary representation")
    if (g5 * g5 - sp.eye(4)).applyfunc(sp.simplify) != sp.zeros(4):
        return refuted(name, claim, {"g5^2": str((g5 * g5).tolist())})
    for m in range(4):
        if (g5 * g[m] + g[m] * g5).applyfunc(sp.simplify) != sp.zeros(4):
            return refuted(name, claim, {"mu": m}, detail="gamma5 does not anticommute with gamma^mu")
    return verified(name, claim, "all 16 anticommutators, hermiticity, g5^2 and {g5, g^mu} checked exactly")


def check_lorentz_generators(rep: str = "dirac", sign: int = +1) -> Result:
    """Spinor Lorentz generators S^{mu nu} = (i/4)[g^mu, g^nu]: [S^{mu nu}, g^rho] = i(eta^{nu rho} g^mu - eta^{mu rho} g^nu) and the Lorentz algebra [S^{mn}, S^{rs}] = i(...). `sign=-1` tests the opposite (wrong) convention. Exact."""
    name = "check_lorentz_generators"
    g, _ = dirac_matrices(rep)
    S = {(m, n): (_I / 4) * (g[m] * g[n] - g[n] * g[m]) for m in range(4) for n in range(4)}
    claim = f"[S^(mn), g^r] = {'+' if sign > 0 else '-'}i(eta^(nr) g^m - eta^(mr) g^n) and the Lorentz algebra ({rep})"
    for m, n, r in itertools.product(range(4), repeat=3):
        lhs = S[(m, n)] * g[r] - g[r] * S[(m, n)]
        rhs = sign * _I * (ETA[n, r] * g[m] - ETA[m, r] * g[n])
        if (lhs - rhs).applyfunc(sp.simplify) != sp.zeros(4):
            return refuted(name, claim, {"m": m, "n": n, "rho": r})
    for m, n, r, s_ in itertools.product(range(4), repeat=4):
        lhs = S[(m, n)] * S[(r, s_)] - S[(r, s_)] * S[(m, n)]
        rhs = sign * _I * (ETA[n, r] * S[(m, s_)] - ETA[m, r] * S[(n, s_)] - ETA[n, s_] * S[(m, r)] + ETA[m, s_] * S[(n, r)])
        if (lhs - rhs).applyfunc(sp.simplify) != sp.zeros(4):
            return refuted(name, claim, {"m": m, "n": n, "r": r, "s": s_}, detail="Lorentz algebra relation fails")
    return verified(name, claim, "all 64 commutators with gamma and all 256 generator commutators checked exactly")


def _env(vecs: dict, scal: dict, rep: str, eps0123: int):
    g, g5 = dirac_matrices(rep)

    def slash(v):
        return sum((ETA[i, i] * v[i] * g[i] for i in range(4)), sp.zeros(4))

    def dot(a, b):
        return sum(ETA[i, i] * a[i] * b[i] for i in range(4))

    def eps(a, b, c, d):
        lo = lambda v: [ETA[i, i] * v[i] for i in range(4)]  # noqa: E731
        la, lb, lc, ld = lo(a), lo(b), lo(c), lo(d)
        tot = 0
        for perm in itertools.permutations(range(4)):
            tot += sp.LeviCivita(*perm) * la[perm[0]] * lb[perm[1]] * lc[perm[2]] * ld[perm[3]]
        return eps0123 * tot

    def tr(M):
        return M.trace()

    def sigma(m, n):
        return (_I / 2) * (g[m] * g[n] - g[n] * g[m])

    env = {"gu": lambda m: g[m], "gl": lambda m: ETA[m, m] * g[m], "slash": slash, "g5": g5, "one": sp.eye(4), "tr": tr,
           "dot": dot, "eps": eps, "sigma": sigma, "sum": _msum, "range": range, "I": _I, "sqrt": sp.sqrt}
    env.update(vecs)
    env.update(scal)
    return env


def _msum(it):
    it = list(it)
    out = it[0]
    for x in it[1:]:
        out = out + x
    return out


def _eval(expr: str, env: dict):
    # env is passed as GLOBALS so that generator expressions (sum(... for m in range(4))) can see gu, gl, slash, ...
    return eval(expr, {"__builtins__": {}, **env})  # noqa: S307  (user-supplied algebra; builtins removed)


def _diff(L, R):
    if isinstance(L, sp.MatrixBase) or isinstance(R, sp.MatrixBase):
        L = L if isinstance(L, sp.MatrixBase) else L * sp.eye(4)
        R = R if isinstance(R, sp.MatrixBase) else R * sp.eye(4)
        return (L - R).applyfunc(sp.expand)
    return sp.expand(L - R)


def _is_zero(d):
    return d == sp.zeros(4) if isinstance(d, sp.MatrixBase) else d == 0


def check_gamma_identity(lhs: str, rhs: str, vectors=(), scalars=(), rep: str = "dirac", eps0123: int = +1, timeout_s: float = 90) -> Result:
    """Is the gamma-matrix / trace expression `lhs` equal to `rhs` for ALL values of the named 4-vectors and scalars?
    e.g. lhs="tr(slash(p)*slash(k)*slash(q)*slash(l))", rhs="4*(dot(p,k)*dot(q,l)-dot(p,q)*dot(k,l)+dot(p,l)*dot(k,q))", vectors=("p","k","q","l").
    Contractions: "sum(gu(m)*slash(p)*gl(m) for m in range(4))". A scalar compared with a matrix means scalar x identity.
    Symbolic components give a proof (VERIFIED); a failure gives an exact witness."""
    name = "check_gamma_identity"
    claim = f"{lhs} == {rhs}"
    vs = {v: [sp.Symbol(f"{v}{i}", real=True) for i in range(4)] for v in vectors}
    ss = {s: sp.Symbol(s, real=True) for s in scalars}
    try:
        with timeout(timeout_s):
            d = _diff(_eval(lhs, _env(vs, ss, rep, eps0123)), _eval(rhs, _env(vs, ss, rep, eps0123)))
        symbolic = True
    except CheckTimeout:
        symbolic = False
        d = None
    except Exception as e:
        return inconclusive(name, claim, f"could not evaluate: {type(e).__name__}: {e}")
    syms = [x for v in vs.values() for x in v] + list(ss.values())
    if symbolic:
        if _is_zero(d):
            return verified(name, claim, "both sides expanded with symbolic components: difference is identically 0" if syms else "exact evaluation (no free vectors)")
        rng = random.Random(7)
        for _ in range(20):
            pt = {x: sp.Rational(rng.randint(-9, 9), rng.randint(1, 5)) for x in syms}
            val = d.subs(pt) if not isinstance(d, sp.MatrixBase) else d.subs(pt)
            if not _is_zero(val.applyfunc(sp.simplify) if isinstance(val, sp.MatrixBase) else sp.simplify(val)):
                return refuted(name, claim, {"point": {str(k): str(v) for k, v in pt.items()}, "lhs_minus_rhs": str(val.tolist() if isinstance(val, sp.MatrixBase) else val)},
                               detail="the difference is a nonzero polynomial in the components")
        return refuted(name, claim, {"difference": str(d)[:300]}, detail="the symbolic difference is a nonzero polynomial")
    rng = random.Random(11)
    for _ in range(8):
        vp = {v: [sp.Rational(rng.randint(-6, 6), rng.randint(1, 4)) for _ in range(4)] for v in vectors}
        sp_ = {s: sp.Rational(rng.randint(1, 6), rng.randint(1, 3)) for s in scalars}
        try:
            val = _diff(_eval(lhs, _env(vp, sp_, rep, eps0123)), _eval(rhs, _env(vp, sp_, rep, eps0123)))
        except Exception as e:
            return inconclusive(name, claim, f"could not evaluate: {type(e).__name__}: {e}")
        if not _is_zero(val):
            return refuted(name, claim, {"vectors": {k: [str(x) for x in v] for k, v in vp.items()}, "scalars": {k: str(v) for k, v in sp_.items()}})
    return consistent(name, claim, "8 random rational points in exact arithmetic (symbolic proof timed out)")


def compton_amplitude(m: float = 1.3, sign_u: float = +1.0, k3=(0.3, 0.5, 0.4), p3=(0.2, -0.4, 0.3), n_out=(0.2, -0.7, 0.5), s_in: int = 0, s_out: int = 0):
    """Tree-level e(p) + photon(k) -> e(p') + photon(k') amplitude as a function of the incoming polarisation vector eps (4-vector, contravariant).
    `sign_u=-1` flips the relative sign of the u-channel diagram (a classic derivation error). Returns (amplitude, k)."""
    eta = np.diag([1.0, -1, -1, -1])
    dot = lambda a, b: a @ eta @ b  # noqa: E731
    sx = np.array([[0, 1], [1, 0]], complex)
    sy = np.array([[0, -1j], [1j, 0]])
    sz = np.array([[1, 0], [0, -1]], complex)
    g0 = np.block([[np.eye(2), np.zeros((2, 2))], [np.zeros((2, 2)), -np.eye(2)]]).astype(complex)
    gam = [g0] + [np.block([[np.zeros((2, 2)), s], [-s, np.zeros((2, 2))]]) for s in (sx, sy, sz)]
    slash = lambda v: sum(eta[i, i] * v[i] * gam[i] for i in range(4))  # noqa: E731
    onshell = lambda v3, mass: np.array([np.sqrt(mass * mass + np.dot(v3, v3)), *v3])  # noqa: E731
    p = onshell(np.array(p3, float), m)
    k3 = np.array(k3, float)
    k = np.array([np.linalg.norm(k3), *k3])
    n = np.array(n_out, float)
    n /= np.linalg.norm(n)
    tot = p + k
    w = (dot(tot, tot) - m * m) / (2 * (tot[0] - tot[1:] @ n))
    kp = w * np.array([1.0, *n])
    pp = tot - kp

    def u(pv, s):
        E, pvec = pv[0], pv[1:]
        chi = np.array([1, 0], complex) if s == 0 else np.array([0, 1], complex)
        sp_ = pvec[0] * sx + pvec[1] * sy + pvec[2] * sz
        return np.sqrt(E + m) * np.concatenate([chi, (sp_ @ chi) / (E + m)])

    ubar = u(pp, s_out).conj() @ g0
    uin = u(p, s_in)
    pol_out = np.array([0, *np.cross(n, [0, 0, 1.0])])
    pol_out[1:] /= np.linalg.norm(pol_out[1:])
    s_, u_ = p + k, p - kp

    def amp(eps):
        t1 = slash(pol_out) @ (slash(s_) + m * np.eye(4)) @ slash(eps) / (dot(s_, s_) - m * m)
        t2 = slash(eps) @ (slash(u_) + m * np.eye(4)) @ slash(pol_out) / (dot(u_, u_) - m * m) * sign_u
        return complex(ubar @ (t1 + t2) @ uin)

    return amp, k


def check_ward_identity(amplitude, k, trials: int = 3, tol: float = 1e-9, seed: int = 3) -> Result:
    """Ward identity: replacing the photon polarisation by its momentum, M(eps -> k), must vanish (gauge invariance).
    `amplitude(eps)` is a callable on 4-vectors; compared against |M| at random physical polarisations. Floating point, so a pass is CONSISTENT."""
    name = "check_ward_identity"
    claim = "M(eps -> k) = 0 (gauge invariance / current conservation)"
    k = np.asarray(k, float)
    rng = np.random.default_rng(seed)
    try:
        scale = max(abs(amplitude(np.array([0, *rng.normal(size=3)]))) for _ in range(trials))
        resid = abs(amplitude(k))
    except Exception as e:
        return inconclusive(name, claim, f"amplitude callable failed: {type(e).__name__}: {e}")
    if scale == 0:
        return inconclusive(name, claim, "the amplitude vanishes for generic polarisations; the test is empty")
    rel = resid / scale
    if rel > 1e-6:
        return refuted(name, claim, {"|M(eps->k)|": resid, "typical |M|": scale, "ratio": rel}, evidence="floating-point evaluation, ratio far above rounding error")
    if rel < tol:
        return consistent(name, claim, f"|M(eps->k)|/|M| = {rel:.1e} at one kinematic point", caveat="One phase-space point; not a proof for all kinematics.")
    return inconclusive(name, claim, f"ratio {rel:.1e} is between rounding error and a clear violation")
