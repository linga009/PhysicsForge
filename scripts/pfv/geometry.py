"""pfv.geometry: differential geometry, general relativity and gauge-theory identities.

Conventions (printed in every result so a claim can be compared like with like):
  Gamma^a_{bc} = 1/2 g^{ad}(d_b g_dc + d_c g_db - d_d g_bc)
  R^a_{bcd}    = d_c Gamma^a_{db} - d_d Gamma^a_{cb} + Gamma^a_{ce} Gamma^e_{db} - Gamma^a_{de} Gamma^e_{cb}
  R_{bd}       = R^a_{bad},   G_{ab} = R_{ab} - 1/2 R g_{ab}   (MTW sign conventions)
Gauge theory: D = d - i A, F_{mu nu} = d_mu A_nu - d_nu A_mu - i [A_mu, A_nu]; a wrong sign on the commutator term
breaks the Bianchi identity and gauge covariance, which is how `check_yang_mills_*` catches it.
"""
from __future__ import annotations

import itertools
import random

import sympy as sp

from .core import Result, verified, consistent, inconclusive, timeout, CheckTimeout, unify, unknown_symbols
from .analysis import _S
from .core import refuted as _refuted
from functools import partial as _partial

refuted = _partial(_refuted, evidence="exact symbolic residue")

CONV = "MTW: R^a_bcd = d_c G^a_db - ..., R_bd = R^a_bad"


SAMPLED = {"used": False}


def _numeric_zero(e) -> bool:
    syms = sorted(e.free_symbols, key=lambda z: z.name)
    if not syms:
        return abs(sp.N(e, 40)) < 1e-30
    rng = random.Random(11)
    for _ in range(6):
        pt = {z: sp.Rational(rng.randint(3, 40), 7) for z in syms}
        try:
            v = sp.N(e.subs(pt), 50)
        except Exception:
            return False
        if not v.is_number or abs(complex(v)) > 1e-35 * max(1.0, abs(complex(sp.N(e.subs({z: 1 + pt[z] for z in syms}), 30)))):
            return False
    return True


def _simp(e):
    """Exact simplification with several strategies. sympy.simplify has FALSE NEGATIVES on trigonometric zeros
    (e.g. sin(2t)tan(t)+cos(2t)-1 over tan(t) is 0 but simplify leaves it). If every exact route fails but the
    expression vanishes to 50 digits at 6 rational points, it is replaced by 0 and SAMPLED['used'] is set, which
    downgrades the final verdict from VERIFIED to CONSISTENT."""
    e = sp.simplify(e)
    if e == 0 or not e.free_symbols and e.is_number:
        return e
    for alt in (lambda z: sp.trigsimp(sp.expand_trig(z)), lambda z: sp.simplify(z.rewrite(sp.exp)), lambda z: sp.cancel(sp.together(z)),
                lambda z: sp.simplify(sp.expand(sp.expand_trig(z)))):
        try:
            z = alt(e)
        except Exception:
            continue
        if z == 0:
            return sp.Integer(0)
    if _numeric_zero(e):
        SAMPLED["used"] = True
        return sp.Integer(0)
    return e


def _finish(name, claim, evidence, **data):
    """VERIFIED unless a numeric-zero substitution happened during the run."""
    if SAMPLED["used"]:
        SAMPLED["used"] = False
        return consistent(name, claim, evidence + " [some components vanished only to 50 digits at sample points; sympy could not simplify them to exact 0]",
                          caveat="Exact simplification failed for at least one trigonometric zero; the residue is zero at 6 rational points to 50 digits.", **data)
    return verified(name, claim, evidence, **data)


class Spacetime:
    """Holds a metric and caches Christoffel / Riemann / Ricci."""

    def __init__(self, g: sp.Matrix, coords, simplify=_simp):
        SAMPLED["used"] = False
        self.g = sp.Matrix(g)
        self.x = list(coords)
        self.n = len(self.x)
        self.simp = simplify
        self.gi = self.g.inv().applyfunc(self.simp)
        self._Gam = self._Riem = self._Ric = self._R = None

    @property
    def Gamma(self):
        if self._Gam is None:
            n, g, gi, x = self.n, self.g, self.gi, self.x
            self._Gam = [[[self.simp(sum(gi[a, d] * (sp.diff(g[d, b], x[c]) + sp.diff(g[d, c], x[b]) - sp.diff(g[b, c], x[d])) for d in range(n)) / 2)
                           for c in range(n)] for b in range(n)] for a in range(n)]
        return self._Gam

    @property
    def Riemann(self):
        """R[a][b][c][d] = R^a_{bcd}."""
        if self._Riem is None:
            n, G, x = self.n, self.Gamma, self.x
            self._Riem = [[[[self.simp(sp.diff(G[a][d][b], x[c]) - sp.diff(G[a][c][b], x[d])
                                       + sum(G[a][c][e] * G[e][d][b] - G[a][d][e] * G[e][c][b] for e in range(n)))
                             for d in range(n)] for c in range(n)] for b in range(n)] for a in range(n)]
        return self._Riem

    @property
    def Ricci(self):
        if self._Ric is None:
            R, n = self.Riemann, self.n
            self._Ric = sp.Matrix(n, n, lambda b, d: self.simp(sum(R[a][b][a][d] for a in range(n))))
        return self._Ric

    @property
    def Rscalar(self):
        if self._R is None:
            self._R = self.simp(sum(self.gi[a, b] * self.Ricci[a, b] for a in range(self.n) for b in range(self.n)))
        return self._R

    @property
    def Einstein(self):
        return (self.Ricci - self.Rscalar * self.g / 2).applyfunc(self.simp)

    def riemann_lower(self):
        n, R, g = self.n, self.Riemann, self.g
        return [[[[self.simp(sum(g[a, e] * R[e][b][c][d] for e in range(n))) for d in range(n)] for c in range(n)] for b in range(n)] for a in range(n)]

    def kretschmann(self):
        n = self.n
        Rl = self.riemann_lower()
        gi = self.gi
        Ru = self.Riemann
        # R_{abcd} R^{abcd} with R^{abcd} = g^{bb'} g^{cc'} g^{dd'} R^a_{b'c'd'}; metric assumed diagonal here for speed
        if not all(gi[i, j] == 0 for i in range(n) for j in range(n) if i != j):
            raise NotImplementedError("kretschmann implemented for diagonal metrics")
        return self.simp(sum(Rl[a][b][c][d] * Ru[a][b][c][d] * gi[b, b] * gi[c, c] * gi[d, d] for a, b, c, d in itertools.product(range(n), repeat=4)))


def check_metric(g, coords, signature=None) -> Result:
    """Symmetric, non-degenerate, and (optionally) the (negative, positive) signature at sample points."""
    g = sp.Matrix(g)
    claim = "g is a valid metric"
    if g != g.T:
        return refuted("check_metric", claim, None, detail="metric is not symmetric")
    det = sp.simplify(g.det())
    if det == 0:
        return refuted("check_metric", claim, None, detail="metric is degenerate (det g = 0)")
    detail = f"det g = {det}"
    if signature is not None:
        syms = sorted(g.free_symbols, key=lambda s: s.name)
        pts = [{s: sp.Rational(random.Random(i).randint(2, 9), 3) for s in syms} for i in range(4)]
        for p in pts:
            try:
                gp = g.subs(p)
                ev = [sp.N(v) for v in gp.eigenvals(multiple=True)]
                sig = (sum(1 for v in ev if v < 0), sum(1 for v in ev if v > 0))
            except TypeError:
                return inconclusive("check_metric", claim, "signature depends on the sign of undefined functions; symmetric and non-degenerate, signature not checked")
            if sig != tuple(signature):
                return refuted("check_metric", claim, {"point": {str(k): str(v) for k, v in p.items()}, "signature(-,+)": sig},
                               detail=f"signature differs from the claimed {tuple(signature)}", evidence="eigenvalue signs at a point")
    return verified("check_metric", claim, "symmetric, non-degenerate" + (f", signature (-,+)={tuple(signature)} at sampled points" if signature else ""), detail=detail)


def check_vacuum_solution(g, coords, Lambda=0, seconds: float = 120) -> Result:
    """Is R_{ab} = Lambda g_{ab} (vacuum Einstein equations with cosmological constant)?"""
    claim = f"metric solves vacuum Einstein equations R_ab = {Lambda} g_ab ({CONV})"
    st = Spacetime(g, coords)
    try:
        with timeout(seconds):
            res = (st.Ricci - Lambda * st.g).applyfunc(_simp)
    except CheckTimeout:
        return inconclusive("check_vacuum_solution", claim, "timed out")
    if res == sp.zeros(st.n):
        return _finish("check_vacuum_solution", claim, "Ricci - Lambda g simplifies to the zero matrix")
    bad = [(i, j, res[i, j]) for i in range(st.n) for j in range(i, st.n) if res[i, j] != 0]
    return refuted("check_vacuum_solution", claim, {f"R_{i}{j} - Lambda g_{i}{j}": str(v) for i, j, v in bad[:4]})


def check_riemann_symmetries(g, coords, seconds: float = 180) -> Result:
    """Antisymmetry in (ab) and (cd), pair exchange, first (cyclic) Bianchi identity for R_{abcd}."""
    claim = "Riemann tensor has the algebraic symmetries"
    st = Spacetime(g, coords)
    n = st.n
    try:
        with timeout(seconds):
            Rl = st.riemann_lower()
            for a, b, c, d in itertools.product(range(n), repeat=4):
                if _simp(Rl[a][b][c][d] + Rl[b][a][c][d]) != 0:
                    return refuted("check_riemann_symmetries", claim, (a, b, c, d), detail="R_abcd + R_bacd != 0")
                if _simp(Rl[a][b][c][d] + Rl[a][b][d][c]) != 0:
                    return refuted("check_riemann_symmetries", claim, (a, b, c, d), detail="R_abcd + R_abdc != 0")
                if _simp(Rl[a][b][c][d] - Rl[c][d][a][b]) != 0:
                    return refuted("check_riemann_symmetries", claim, (a, b, c, d), detail="R_abcd != R_cdab")
                if _simp(Rl[a][b][c][d] + Rl[a][c][d][b] + Rl[a][d][b][c]) != 0:
                    return refuted("check_riemann_symmetries", claim, (a, b, c, d), detail="first Bianchi R_a[bcd] != 0")
    except CheckTimeout:
        return inconclusive("check_riemann_symmetries", claim, "timed out")
    return _finish("check_riemann_symmetries", claim, f"all {n**4} index combinations simplify to zero (antisymmetry, pair exchange, cyclic identity)")


def check_contracted_bianchi(g, coords, seconds: float = 180) -> Result:
    """nabla_mu G^{mu nu} = 0 for the Einstein tensor of an ARBITRARY metric (kinematic identity)."""
    claim = "nabla_mu G^{mu nu} = 0"
    st = Spacetime(g, coords)
    n = st.n
    try:
        with timeout(seconds):
            Gup = (st.gi * st.Einstein * st.gi).applyfunc(_simp)
            G = st.Gamma
            res = []
            for nu in range(n):
                s = 0
                for m in range(n):
                    s += sp.diff(Gup[m, nu], st.x[m]) + sum(G[m][m][l] * Gup[l, nu] + G[nu][m][l] * Gup[m, l] for l in range(n))
                res.append(_simp(s))
    except CheckTimeout:
        return inconclusive("check_contracted_bianchi", claim, "timed out")
    if all(r == 0 for r in res):
        return _finish("check_contracted_bianchi", claim, "all four components simplify to 0")
    return refuted("check_contracted_bianchi", claim, [str(r) for r in res], detail="this should be an identity: the Einstein tensor or the connection is mis-computed")


def check_covariant_conservation(T_up, g, coords, seconds: float = 120) -> Result:
    """nabla_mu T^{mu nu} = 0 for a given contravariant stress tensor on the given metric."""
    claim = "nabla_mu T^{mu nu} = 0"
    st = Spacetime(g, coords)
    T = sp.Matrix(T_up)
    n = st.n
    G = st.Gamma
    try:
        with timeout(seconds):
            res = []
            for nu in range(n):
                s = 0
                for m in range(n):
                    s += sp.diff(T[m, nu], st.x[m]) + sum(G[m][m][l] * T[l, nu] + G[nu][m][l] * T[m, l] for l in range(n))
                res.append(_simp(s))
    except CheckTimeout:
        return inconclusive("check_covariant_conservation", claim, "timed out")
    if all(r == 0 for r in res):
        return _finish("check_covariant_conservation", claim, "all components vanish identically")
    return refuted("check_covariant_conservation", claim, {f"nu={i}": str(r) for i, r in enumerate(res) if r != 0})


def check_killing(xi_up, g, coords, seconds: float = 120) -> Result:
    """nabla_(a xi_b) = 0, i.e. d_a xi_b + d_b xi_a - 2 Gamma^c_{ab} xi_c = 0 for xi^a given."""
    claim = f"xi = {list(xi_up)} is a Killing vector"
    st = Spacetime(g, coords)
    n = st.n
    xi_lo = [sum(st.g[a, b] * xi_up[b] for b in range(n)) for a in range(n)]
    G = st.Gamma
    try:
        with timeout(seconds):
            M = sp.Matrix(n, n, lambda a, b: _simp(sp.diff(xi_lo[b], st.x[a]) + sp.diff(xi_lo[a], st.x[b]) - 2 * sum(G[c][a][b] * xi_lo[c] for c in range(n))))
    except CheckTimeout:
        return inconclusive("check_killing", claim, "timed out")
    if M == sp.zeros(n):
        return _finish("check_killing", claim, "Killing equation residue is identically zero")
    a, b = [(i, j) for i in range(n) for j in range(n) if M[i, j] != 0][0]
    return refuted("check_killing", claim, {f"(L_xi g)_{a}{b}": str(M[a, b])}, detail="Lie derivative of the metric along xi is non-zero")


def check_curvature_invariant(g, coords, expected, which: str = "kretschmann") -> Result:
    """Kretschmann scalar or Ricci scalar of a (diagonal) metric against a claimed closed form."""
    st = Spacetime(g, coords)
    val = st.kretschmann() if which == "kretschmann" else st.Rscalar
    claim = f"{which} = {expected}"
    val, exp_ = unify(val, _S(expected))
    unk = unknown_symbols(exp_, val, g, coords)
    if unk:
        return inconclusive("check_curvature_invariant", claim, f"expected value uses symbols {unk} not present in the metric")
    if _simp(val - exp_) == 0:
        return _finish("check_curvature_invariant", claim, "exact symbolic comparison", value=str(val))
    return refuted("check_curvature_invariant", claim, {"computed": str(val)})


# --------------------------------------------------------------------------
# gauge theory
# --------------------------------------------------------------------------
def field_strength_abelian(A, coords):
    n = len(coords)
    return sp.Matrix(n, n, lambda m, v: sp.diff(A[v], coords[m]) - sp.diff(A[m], coords[v]))


def check_abelian_gauge_invariance(A, coords, lam) -> Result:
    """F_{mu nu}[A + d lambda] = F_{mu nu}[A]  (needs only equality of mixed partials)."""
    claim = "F = dA is invariant under A -> A + d(lambda)"
    A2 = [A[m] + sp.diff(lam, coords[m]) for m in range(len(coords))]
    F1, F2 = field_strength_abelian(A, coords), field_strength_abelian(A2, coords)
    if (F1 - F2).applyfunc(sp.simplify) == sp.zeros(len(coords)):
        return verified("check_abelian_gauge_invariance", claim, "exact")
    return refuted("check_abelian_gauge_invariance", claim, str((F1 - F2).applyfunc(sp.simplify)))


def check_maxwell_from_potential(A, coords, J=None, eta=None) -> Result:
    """Homogeneous Maxwell: dF = 0 (Bianchi) for F from any potential; with J, also d_mu F^{mu nu} = J^nu."""
    n = len(coords)
    F = field_strength_abelian(A, coords)
    claim = "dF = 0 (homogeneous Maxwell equations)"
    for a, b, c in itertools.combinations(range(n), 3):
        r = sp.simplify(sp.diff(F[b, c], coords[a]) + sp.diff(F[c, a], coords[b]) + sp.diff(F[a, b], coords[c]))
        if r != 0:
            return refuted("check_maxwell_from_potential", claim, (a, b, c), detail=f"d_[a F_bc] = {r}")
    if J is not None:
        eta = sp.diag(1, -1, -1, -1) if eta is None else eta
        Fup = eta * F * eta
        for nu in range(n):
            r = sp.simplify(sum(sp.diff(Fup[m, nu], coords[m]) for m in range(n)) - J[nu])
            if r != 0:
                return refuted("check_maxwell_from_potential", "d_mu F^{mu nu} = J^nu", nu, detail=f"residue {r} (metric {eta.tolist()})")
    return verified("check_maxwell_from_potential", claim + ("; and d_mu F^{mu nu} = J^nu" if J is not None else ""), "exact")


def _rand_poly(x, rng):
    return sum(rng.randint(-3, 3) * x[i] * x[j] for i in range(len(x)) for j in range(i, len(x))) + rng.randint(-2, 2) * x[0]


def check_yang_mills_bianchi(gens, coords, sign: int = -1, seed: int = 1, n_trials: int = 2) -> Result:
    """For random polynomial A_mu = A_mu^a T_a, check D_[lam F_{mu nu]} = 0 with F = dA - i*(-sign)... .

    `sign=-1` uses F = d_mu A_nu - d_nu A_mu - i [A_mu, A_nu] with D = d - iA (the consistent pair).
    `sign=+1` uses +i [A,A] with D = d - iA: this is a COMMON SIGN ERROR and must be REFUTED.
    gens: list of sympy matrices (hermitian generators, e.g. sigma/2)."""
    n = len(coords)
    rng = random.Random(seed)
    claim = f"D_[l F_mn] = 0 with F = dA {'-' if sign < 0 else '+'} i[A,A], D = d - iA"
    for _ in range(n_trials):
        A = [sum((_rand_poly(coords, rng) * T for T in gens), sp.zeros(*gens[0].shape)) for _ in range(n)]
        def F(m, v):
            return sp.diff(A[v], coords[m]) - sp.diff(A[m], coords[v]) + sign * sp.I * (A[m] * A[v] - A[v] * A[m])
        def D(m, X):
            return sp.diff(X, coords[m]) - sp.I * (A[m] * X - X * A[m])
        for l, m, v in itertools.combinations(range(n), 3):
            res = (D(l, F(m, v)) + D(m, F(v, l)) + D(v, F(l, m))).applyfunc(sp.expand)
            if res != sp.zeros(*gens[0].shape):
                return refuted("check_yang_mills_bianchi", claim, (l, m, v), detail="Bianchi identity fails: sign of the commutator term inconsistent with the covariant derivative")
    return verified("check_yang_mills_bianchi", claim, f"{n_trials} random polynomial gauge fields, every index triple: exact zero")
