"""pfv.vectorcalc: grad, div, curl, Laplacian in Cartesian, cylindrical, spherical and custom orthogonal coordinates.

Fields are given by their PHYSICAL (orthonormal-basis) components, e.g. F = ("F_r", "F_theta", "F_phi") in spherical
coordinates (r, theta, phi) with e_r x e_theta = e_phi (right-handed), or cylindrical (rho, phi, z). Exact symbolic.

`check_vector_identity` proves identities such as curl(A x B) = A div B - B div A + (B.grad)A - (A.grad)B for ALL C^2
fields by working with undefined component functions A_x(x,y,z), ... (derivatives of undefined functions commute).
"""
from __future__ import annotations

import sympy as sp

from .core import Result, verified, consistent, inconclusive
from .core import refuted as _refuted
from .analysis import _S, check_identity

SYSTEMS = {
    "cartesian": (("x", "y", "z"), ("1", "1", "1")),
    "cylindrical": (("rho", "phi", "z"), ("1", "rho", "1")),
    "spherical": (("r", "theta", "phi"), ("1", "r", "r*sin(theta)")),
}


def _sys(system, coords=None, scale_factors=None):
    if system == "custom":
        cs, hs = coords, scale_factors
    else:
        cs, hs = SYSTEMS[system]
    u = [sp.Symbol(c) for c in cs]
    h = [_S(x) for x in hs]
    h = [x.xreplace({s: s_ for s in x.free_symbols for s_ in u if s.name == s_.name}) for x in h]
    return u, h


def _field(F, u, h):
    comps = [_S(c) for c in F]
    comps = [c.xreplace({s: s_ for s in c.free_symbols for s_ in u if s.name == s_.name}) for c in comps]
    return comps


def grad(f, system="cartesian", coords=None, scale_factors=None):
    """Gradient of scalar f (string or sympy) -> list of 3 physical components."""
    u, h = _sys(system, coords, scale_factors)
    f = _field([f], u, h)[0]
    return [sp.simplify(sp.diff(f, u[i]) / h[i]) for i in range(3)]


def div(F, system="cartesian", coords=None, scale_factors=None):
    """Divergence of a vector field given by physical components -> sympy expression."""
    u, h = _sys(system, coords, scale_factors)
    F = _field(F, u, h)
    H = h[0] * h[1] * h[2]
    return sp.simplify(sum(sp.diff(H / h[i] * F[i], u[i]) for i in range(3)) / H)


def curl(F, system="cartesian", coords=None, scale_factors=None):
    """Curl of a vector field given by physical components -> list of 3 physical components."""
    u, h = _sys(system, coords, scale_factors)
    F = _field(F, u, h)
    d = sp.diff
    return [sp.simplify((d(h[2] * F[2], u[1]) - d(h[1] * F[1], u[2])) / (h[1] * h[2])),
            sp.simplify((d(h[0] * F[0], u[2]) - d(h[2] * F[2], u[0])) / (h[2] * h[0])),
            sp.simplify((d(h[1] * F[1], u[0]) - d(h[0] * F[0], u[1])) / (h[0] * h[1]))]


def laplacian(f, system="cartesian", coords=None, scale_factors=None):
    """Scalar Laplacian div(grad f)."""
    return div(grad(f, system, coords, scale_factors), system, coords, scale_factors)


_ALL_NAMES = {"x", "y", "z", "r", "rho", "theta", "phi"}


def _guard(name, claim, system, coords, *items):
    """INCONCLUSIVE if a field or claim uses a coordinate name of a different system (e.g. `r` in cylindrical): that is a typo, not a refutation."""
    if system == "custom":
        return None
    own = set(SYSTEMS[system][0])
    stray = set()
    for it in items:
        for e in (it if isinstance(it, (list, tuple)) else [it]):
            stray |= {s_.name for s_ in _S(e).free_symbols} & (_ALL_NAMES - own)
    if stray:
        return inconclusive(name, claim, f"{sorted(stray)} are not coordinates of the {system} system {tuple(SYSTEMS[system][0])}; use those names")
    return None


def _domain(system):
    return "real" if system == "cartesian" else "positive"


def _compare(name, claim, computed, claimed, system, what):
    parts = []
    for i, (a, b) in enumerate(zip(computed, claimed)):
        r = check_identity(a, b, domain=_domain(system), claim=f"{what} component {i + 1}")
        parts.append(r)
        if r.refuted:
            return _refuted(name, claim, {"component": i + 1, "computed": str(sp.simplify(a)), "claimed": str(b)}, evidence="exact symbolic comparison", detail=r.detail)
        if r.verdict == "INCONCLUSIVE":
            return inconclusive(name, claim, f"component {i + 1}: {r.detail}")
    if all(p.verified for p in parts):
        return verified(name, claim, "exact symbolic comparison of every component")
    return consistent(name, claim, "components agree (some only at high-precision sample points)", caveat="Exact simplification failed for at least one component.")


def check_grad(f, claimed, system="cartesian", coords=None, scale_factors=None) -> Result:
    """grad f == claimed (3 physical components)? Exact."""
    claim = f"grad({f}) = {tuple(claimed)} in {system}"
    bad = _guard("check_grad", claim, system, coords, f, claimed)
    if bad is not None:
        return bad
    g = grad(f, system, coords, scale_factors)
    u, h = _sys(system, coords, scale_factors)
    return _compare("check_grad", f"grad({f}) = {tuple(claimed)} in {system}", g, _field(claimed, u, h), system, "grad")


def check_div(F, claimed, system="cartesian", coords=None, scale_factors=None) -> Result:
    """div F == claimed (scalar)? Exact."""
    bad = _guard("check_div", f"div{tuple(F)} = {claimed} in {system}", system, coords, list(F), claimed)
    if bad is not None:
        return bad
    d = div(F, system, coords, scale_factors)
    u, h = _sys(system, coords, scale_factors)
    return _compare("check_div", f"div{tuple(F)} = {claimed} in {system}", [d], _field([claimed], u, h), system, "div")


def check_curl(F, claimed, system="cartesian", coords=None, scale_factors=None) -> Result:
    """curl F == claimed (3 physical components)? Exact."""
    bad = _guard("check_curl", f"curl{tuple(F)} = {tuple(claimed)} in {system}", system, coords, list(F), list(claimed))
    if bad is not None:
        return bad
    c = curl(F, system, coords, scale_factors)
    u, h = _sys(system, coords, scale_factors)
    return _compare("check_curl", f"curl{tuple(F)} = {tuple(claimed)} in {system}", c, _field(claimed, u, h), system, "curl")


def check_laplacian(f, claimed, system="cartesian", coords=None, scale_factors=None) -> Result:
    """Laplacian of scalar f == claimed? Exact (uses the scale-factor formula, so curvilinear Laplacians are checked correctly)."""
    bad = _guard("check_laplacian", f"laplacian({f}) = {claimed} in {system}", system, coords, f, claimed)
    if bad is not None:
        return bad
    L = laplacian(f, system, coords, scale_factors)
    u, h = _sys(system, coords, scale_factors)
    return _compare("check_laplacian", f"laplacian({f}) = {claimed} in {system}", [L], _field([claimed], u, h), system, "laplacian")


def check_solenoidal(F, system="cartesian", coords=None, scale_factors=None) -> Result:
    """div F == 0 everywhere (exact)? A REFUTED result reports the divergence."""
    r = check_div(F, "0", system, coords, scale_factors)
    r.check, r.claim = "check_solenoidal", f"div{tuple(F)} = 0 in {system}"
    return r


def check_irrotational(F, system="cartesian", coords=None, scale_factors=None) -> Result:
    """curl F == 0 everywhere (exact)? (Locally conservative; on a region that is not simply connected this does not give a global potential.)"""
    r = check_curl(F, ("0", "0", "0"), system, coords, scale_factors)
    r.check, r.claim = "check_irrotational", f"curl{tuple(F)} = 0 in {system}"
    return r


def check_potential(F, phi, system="cartesian", coords=None, scale_factors=None) -> Result:
    """Is F = grad(phi)?  (Sign convention matters: the electrostatic field is E = -grad(V).)"""
    r = check_grad(phi, F, system, coords, scale_factors)
    r.check, r.claim = "check_potential", f"F = grad({phi}) with F = {tuple(F)} in {system}"
    return r


def check_vector_potential(B, A, system="cartesian", coords=None, scale_factors=None) -> Result:
    """Is B = curl(A)? (Does not check gauge conditions such as div A = 0; use check_solenoidal(A) for that.)"""
    r = check_curl(A, B, system, coords, scale_factors)
    r.check, r.claim = "check_vector_potential", f"B = curl(A) with A = {tuple(A)}, B = {tuple(B)} in {system}"
    return r


# ---------------------------------------------------------------- identities for ALL fields --------------------------
class _V:
    """3-vector of sympy expressions with + - scalar *."""

    def __init__(self, c):
        self.c = list(c)

    def __add__(self, o):
        return _V([a + b for a, b in zip(self.c, o.c)])

    def __sub__(self, o):
        return _V([a - b for a, b in zip(self.c, o.c)])

    def __neg__(self):
        return _V([-a for a in self.c])

    def __mul__(self, s):
        return _V([a * s for a in self.c])

    __rmul__ = __mul__

    def __truediv__(self, s):
        return _V([a / s for a in self.c])


def _vec_env(xyz, vectors, scalars):
    x, y, z = xyz
    d = sp.diff

    def grad_(f):
        return _V([d(f, v) for v in xyz])

    def div_(A):
        return sum(d(A.c[i], xyz[i]) for i in range(3))

    def curl_(A):
        return _V([d(A.c[2], y) - d(A.c[1], z), d(A.c[0], z) - d(A.c[2], x), d(A.c[1], x) - d(A.c[0], y)])

    def lap_(f):
        return sum(d(f, v, 2) for v in xyz)

    def vlap_(A):
        return _V([lap_(a) for a in A.c])

    def cross_(A, B):
        return _V([A.c[1] * B.c[2] - A.c[2] * B.c[1], A.c[2] * B.c[0] - A.c[0] * B.c[2], A.c[0] * B.c[1] - A.c[1] * B.c[0]])

    def dot_(A, B):
        return sum(a * b for a, b in zip(A.c, B.c))

    def adv_(A, B):  # (A . grad) B
        return _V([sum(A.c[j] * d(B.c[i], xyz[j]) for j in range(3)) for i in range(3)])

    env = {"grad": grad_, "div": div_, "curl": curl_, "lap": lap_, "vlap": vlap_, "cross": cross_, "dot": dot_, "adv": adv_}
    for v in vectors:
        env[v] = _V([sp.Function(f"{v}_{k}")(x, y, z) for k in "xyz"])
    for s_ in scalars:
        env[s_] = sp.Function(s_)(x, y, z)
    return env


def _as_list(v):
    return v.c if isinstance(v, _V) else [v]


def check_vector_identity(lhs: str, rhs: str, vectors=(), scalars=()) -> Result:
    """Is the Cartesian vector-calculus identity lhs == rhs true for ALL C^2 fields? Fields are undefined functions of (x,y,z), so VERIFIED is a proof.
    Names: grad div curl lap vlap cross dot adv(A,B)=(A.grad)B plus your vector names (A, B ...) and scalar names (f, g ...).
    Example: lhs="curl(cross(A,B))", rhs="A*div(B) - B*div(A) + adv(B,A) - adv(A,B)", vectors=("A","B")."""
    name = "check_vector_identity"
    claim = f"{lhs} == {rhs}"
    xyz = sp.symbols("x y z", real=True)
    env = _vec_env(xyz, vectors, scalars)
    glob = {"__builtins__": {}, **env}
    try:
        L = eval(lhs, glob)  # noqa: S307
        R = eval(rhs, glob)
    except Exception as e:
        return inconclusive(name, claim, f"could not evaluate: {type(e).__name__}: {e}")
    Ls, Rs = _as_list(L), _as_list(R)
    if len(Ls) != len(Rs):
        return refuted_shape(name, claim)
    diffs = [sp.expand(a - b) for a, b in zip(Ls, Rs)]
    if all(d == 0 for d in diffs):
        return verified(name, claim, "both sides expanded in components of undefined C^2 functions: difference is identically 0")
    # concrete witness: polynomial/trig fields
    x, y, z = xyz
    samples = [x**2 * y + z**3, sp.sin(x) * y + z**2, x * y * z + y**3]
    subs = {}
    for k, v in enumerate(vectors):
        for j, ax in enumerate("xyz"):
            subs[sp.Function(f"{v}_{ax}")(x, y, z)] = [x * y + z, y**2 - x * z, z * x + sp.sin(y)][(j + k) % 3]
    for k, s_ in enumerate(scalars):
        subs[sp.Function(s_)(x, y, z)] = samples[k % 3]
    for d in diffs:
        if d != 0:
            try:
                val = sp.simplify(d.subs(subs).doit())
            except Exception:
                continue
            pt = {x: sp.Rational(1, 2), y: sp.Rational(3, 5), z: sp.Rational(2, 3)}
            v0 = sp.N(val.subs(pt), 20)
            if abs(v0) > sp.Float("1e-12"):
                return _refuted(name, claim, {"fields": {str(k): str(v) for k, v in subs.items()}, "point": "(1/2, 3/5, 2/3)", "lhs - rhs": str(v0)},
                                evidence="exact symbolic differentiation of explicit sample fields, evaluated at a rational point")
    return _refuted(name, claim, {"difference": str(diffs)[:300]}, evidence="the difference of the two sides is a nonzero expression in the field components")


def refuted_shape(name, claim):
    return _refuted(name, claim, {"shape": "one side is a vector and the other a scalar"}, evidence="type error in the claimed identity")


# ---------------------------------------------------------------- integral theorems ------------------------------------
def check_flux_sphere(F, R, claimed, center=(0, 0, 0)) -> Result:
    """Outward flux of the Cartesian field F=(Fx,Fy,Fz) through the sphere of radius R about `center` equals `claimed`? Exact surface integral."""
    name = "check_flux_sphere"
    x, y, z = sp.symbols("x y z", real=True)
    th, ph = sp.symbols("theta phi", real=True)
    Rr = sp.Symbol("R", positive=True) if isinstance(R, str) and R == "R" else _S(R)
    cx, cy, cz = [_S(c) for c in center]
    claim = f"flux of {tuple(F)} through the sphere |r - c| = {R} is {claimed}"
    comps = [_S(c).xreplace({s: {"x": x, "y": y, "z": z}[s.name] for s in _S(c).free_symbols if s.name in "xyz"}) for c in F]
    nx, ny, nz = sp.sin(th) * sp.cos(ph), sp.sin(th) * sp.sin(ph), sp.cos(th)
    sub = {x: cx + Rr * nx, y: cy + Rr * ny, z: cz + Rr * nz}
    integrand = sp.simplify(sum(c.subs(sub) * n for c, n in zip(comps, (nx, ny, nz))) * Rr**2 * sp.sin(th))
    try:
        val = sp.simplify(sp.integrate(sp.integrate(integrand, (ph, 0, 2 * sp.pi)), (th, 0, sp.pi)))
    except Exception as e:
        return inconclusive(name, claim, f"integration failed: {type(e).__name__}")
    if val.has(sp.Integral):
        return inconclusive(name, claim, "sympy could not evaluate the surface integral in closed form")
    c = _S(claimed)
    if sp.simplify(val - c) == 0:
        return verified(name, claim, f"surface integral evaluated exactly: {val}")
    return _refuted(name, claim, {"true_flux": str(val)}, evidence="exact surface integral")


def check_line_integral(F, path, t_range, claimed, var="t") -> Result:
    """Line integral of the Cartesian field F along the parametrised path r(t) over t_range=(t0,t1) equals `claimed`? Exact."""
    name = "check_line_integral"
    t = sp.Symbol(var, real=True)
    x, y, z = sp.symbols("x y z", real=True)
    claim = f"integral of {tuple(F)} . dr along {tuple(path)}, {var} in {t_range} is {claimed}"
    r = [_S(p).xreplace({s: t for s in _S(p).free_symbols if s.name == var}) for p in path]
    Fc = [_S(c) for c in F]
    sub = {x: r[0], y: r[1], z: r[2]}
    sub = {sp.Symbol(k.name): v for k, v in sub.items()}
    integrand = sum(c.xreplace({s: sub[sp.Symbol(s.name)] for s in c.free_symbols if s.name in "xyz"}) * sp.diff(ri, t) for c, ri in zip(Fc, r))
    try:
        val = sp.simplify(sp.integrate(sp.simplify(integrand), (t, _S(t_range[0]), _S(t_range[1]))))
    except Exception as e:
        return inconclusive(name, claim, f"integration failed: {type(e).__name__}")
    if val.has(sp.Integral):
        return inconclusive(name, claim, "sympy could not evaluate the integral in closed form")
    if sp.simplify(val - _S(claimed)) == 0:
        return verified(name, claim, f"line integral evaluated exactly: {val}")
    return _refuted(name, claim, {"true_value": str(val)}, evidence="exact line integral")


def check_divergence_theorem_box(F, bounds) -> Result:
    """Gauss: the volume integral of div F over the box [x0,x1]x[y0,y1]x[z0,z1] equals the outward flux through its six faces (exact; a mismatch means F is not C^1 on the box or sympy mis-integrated)."""
    name = "check_divergence_theorem_box"
    x, y, z = sp.symbols("x y z", real=True)
    Fc = [_S(c).xreplace({s: {"x": x, "y": y, "z": z}[s.name] for s in _S(c).free_symbols if s.name in "xyz"}) for c in F]
    (x0, x1), (y0, y1), (z0, z1) = [(_S(a), _S(b)) for a, b in bounds]
    claim = f"Gauss theorem for {tuple(F)} on box {bounds}"
    d = sum(sp.diff(Fc[i], v) for i, v in enumerate((x, y, z)))
    try:
        vol = sp.integrate(d, (x, x0, x1), (y, y0, y1), (z, z0, z1))
        flux = (sp.integrate((Fc[0].subs(x, x1) - Fc[0].subs(x, x0)), (y, y0, y1), (z, z0, z1))
                + sp.integrate((Fc[1].subs(y, y1) - Fc[1].subs(y, y0)), (x, x0, x1), (z, z0, z1))
                + sp.integrate((Fc[2].subs(z, z1) - Fc[2].subs(z, z0)), (x, x0, x1), (y, y0, y1)))
    except Exception as e:
        return inconclusive(name, claim, f"integration failed: {type(e).__name__}")
    if sp.simplify(vol - flux) == 0:
        return verified(name, claim, f"volume integral = flux = {sp.simplify(vol)} (exact)")
    return _refuted(name, claim, {"volume_integral": str(sp.simplify(vol)), "flux": str(sp.simplify(flux))}, evidence="exact integration of both sides")
