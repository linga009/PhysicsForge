"""pfv.dimensions: dimensional analysis in SI base dimensions and natural units.

A Dim is an exponent vector over (M, L, T, I, Theta, N, J). `dimension_of` walks a sympy expression:
sums need equal dimensions, arguments of exp/log/sin/... must be dimensionless, powers need dimensionless exponents.
Dimensional consistency is NECESSARY, never sufficient: a dimensionally correct formula can still be wrong by a
pure number (factors of 2, pi), a sign or a function. A failure here is decisive though.
"""
from __future__ import annotations

from fractions import Fraction

import sympy as sp

from .core import Result, verified, consistent, inconclusive
from .core import refuted as _refuted
from functools import partial as _partial

refuted = _partial(_refuted, evidence="exact dimension exponents")

BASE = ("M", "L", "T", "I", "Th", "N", "J")


class DimensionError(Exception):
    pass


class Dim:
    __slots__ = ("e",)

    def __init__(self, **kw):
        self.e = tuple(Fraction(kw.get(b, 0)) for b in BASE)

    @classmethod
    def _from(cls, tup):
        d = cls()
        d.e = tuple(Fraction(x) for x in tup)
        return d

    def __mul__(self, o):
        return Dim._from(a + b for a, b in zip(self.e, o.e))

    def __truediv__(self, o):
        return Dim._from(a - b for a, b in zip(self.e, o.e))

    def __pow__(self, p):
        return Dim._from(a * Fraction(p) for a in self.e)

    def __eq__(self, o):
        return isinstance(o, Dim) and self.e == o.e

    def __hash__(self):
        return hash(self.e)

    @property
    def dimensionless(self):
        return all(x == 0 for x in self.e)

    def __repr__(self):
        parts = [f"{b}^{x}" if x != 1 else b for b, x in zip(BASE, self.e) if x != 0]
        return "·".join(parts) if parts else "1"


ONE = Dim()
M_, L_, T_, I_, TH_, N_, J_ = Dim(M=1), Dim(L=1), Dim(T=1), Dim(I=1), Dim(Th=1), Dim(N=1), Dim(J=1)
VELOCITY = L_ / T_
ACCEL = L_ / T_ ** 2
FORCE = M_ * ACCEL
ENERGY = FORCE * L_
POWER = ENERGY / T_
PRESSURE = FORCE / L_ ** 2
CHARGE = I_ * T_
VOLTAGE = ENERGY / CHARGE
FREQUENCY = T_ ** -1
ACTION = ENERGY * T_
MOMENTUM = M_ * VELOCITY
ANGMOM = ACTION
E_FIELD = VOLTAGE / L_
B_FIELD = M_ / (I_ * T_ ** 2)

CONSTANTS = {
    "hbar": ACTION, "c": VELOCITY, "G": L_ ** 3 / (M_ * T_ ** 2), "k_B": ENERGY / TH_, "e": CHARGE,
    "epsilon_0": CHARGE ** 2 / (ENERGY * L_), "mu_0": ENERGY / (I_ ** 2 * L_), "m_e": M_, "m_p": M_,
    "N_A": N_ ** -1, "sigma_SB": POWER / (L_ ** 2 * TH_ ** 4), "alpha": ONE, "h": ACTION, "a_0": L_,
}

_DIMLESS_FUNCS = (sp.exp, sp.log, sp.sin, sp.cos, sp.tan, sp.sinh, sp.cosh, sp.tanh, sp.asin, sp.acos, sp.atan, sp.erf)


def _parse(expr, names):
    """sympify with every table name bound to a plain Symbol (so 'E', 'I', 'N', 'S', 'Q' are NOT Euler's number, i, ...)."""
    if isinstance(expr, str):
        return sp.sympify(expr, locals={n: sp.Symbol(n) for n in names})
    return sp.sympify(expr)


def dimension_of(expr, table: dict) -> Dim:
    """`table` maps symbol NAME -> Dim. Constants in CONSTANTS (hbar, c, G, k_B, e, epsilon_0, mu_0, ...) are available by name.
    Strings are parsed with every table name as a plain Symbol, so a symbol called 'E' means energy, not Euler's number."""
    full = {**CONSTANTS, **table}
    expr = _parse(expr, full)

    def walk(e):
        if e.is_Number or e in (sp.pi, sp.E, sp.I):
            return ONE
        if e.is_Symbol:
            if e.name not in full:
                raise DimensionError(f"no dimension given for symbol '{e.name}'")
            return full[e.name]
        if e.is_Add:
            ds = [walk(t) for t in e.args]
            for t, d in zip(e.args, ds):
                if d != ds[0]:
                    raise DimensionError(f"cannot add terms of different dimension: [{e.args[0]}] = {ds[0]} but [{t}] = {d}")
            return ds[0]
        if e.is_Mul:
            d = ONE
            for t in e.args:
                d = d * walk(t)
            return d
        if e.is_Pow:
            b, p = e.args
            dp = walk(p)
            if not dp.dimensionless:
                raise DimensionError(f"exponent {p} must be dimensionless, has dimension {dp}")
            if not p.is_Number:
                db = walk(b)
                if not db.dimensionless:
                    raise DimensionError(f"non-numeric exponent {p} on a dimensionful base {b} ({db})")
                return ONE
            p = sp.nsimplify(p, rational=True)
            if not p.is_Rational:
                raise DimensionError(f"irrational exponent {p} on a dimensionful base is not supported")
            return walk(b) ** Fraction(int(p.p), int(p.q))
        if isinstance(e, sp.Derivative):
            d = walk(e.expr)
            for v, k in e.variable_count:
                d = d / (walk(v) ** k)
            return d
        if isinstance(e, sp.Integral):
            d = walk(e.function)
            for lim in e.limits:
                d = d * walk(lim[0])
            return d
        if isinstance(e, sp.Abs):
            return walk(e.args[0])
        if isinstance(e, sp.Function) or isinstance(e, sp.core.function.AppliedUndef):
            if e.func in _DIMLESS_FUNCS or e.func.__name__ in ("exp", "log", "sin", "cos", "tan", "sinh", "cosh", "tanh", "erf"):
                for a in e.args:
                    da = walk(a)
                    if not da.dimensionless:
                        raise DimensionError(f"argument of {e.func.__name__} must be dimensionless: [{a}] = {da}")
                return ONE
            if e.func in (sp.sqrt,):
                return walk(e.args[0]) ** Fraction(1, 2)
            raise DimensionError(f"unknown function {e.func}: give its dimension via the table as a Symbol")
        raise DimensionError(f"cannot analyse node {type(e).__name__}: {e}")

    return walk(expr)


def check_dimensions(lhs, rhs, table: dict, claim: str = "") -> Result:
    """Both sides of an equation must have the same dimension, and every internal sum must be homogeneous."""
    names = {**CONSTANTS, **table}
    L, R = _parse(lhs, names), _parse(rhs, names)
    claim = claim or f"[{L}] = [{R}]"
    try:
        dl, dr = dimension_of(L, table), dimension_of(R, table)
    except DimensionError as e:
        return refuted("check_dimensions", claim, str(e), detail="inhomogeneous or ill-formed expression")
    if dl != dr:
        return refuted("check_dimensions", claim, {"lhs": repr(dl), "rhs": repr(dr)}, detail=f"lhs has dimension {dl}, rhs has {dr}")
    return consistent("check_dimensions", claim, f"both sides have dimension {dl}", caveat="Dimensional consistency is necessary, not sufficient: factors of 2, pi and signs are not checked.")


def check_expected_dimension(expr, table: dict, expected: Dim, name: str = "") -> Result:
    """Does the expression have the stated dimension (e.g. Planck length = L)?"""
    claim = f"[{name or expr}] = {expected}"
    try:
        d = dimension_of(expr, table)
    except DimensionError as e:
        return refuted("check_expected_dimension", claim, str(e))
    if d == expected:
        return consistent("check_expected_dimension", claim, f"dimension is {d}", caveat="Necessary condition only.")
    return refuted("check_expected_dimension", claim, {"actual": repr(d), "expected": repr(expected)})


def to_natural(d: Dim) -> Fraction:
    """Mass-dimension in natural units hbar = c = k_B = 1: [M] = E, [L] = [T] = E^-1, [Theta] = E. Returns the exponent of energy.
    Electromagnetic units (I, N, J) are not converted (returns NotImplemented-style ValueError)."""
    M, L, T, I, Th, N, J = d.e
    if I != 0 or N != 0 or J != 0:
        raise ValueError("charge/amount/luminosity not converted (convention-dependent)")
    return M - L - T + Th


def buckingham_pi(variables: dict) -> list[dict]:
    """Dimensionless groups from {name: Dim}: nullspace of the dimension matrix (exact rationals).
    Returns a basis as a list of {name: exponent}; len(basis) = n_vars - rank (Buckingham pi theorem)."""
    names = list(variables)
    A = sp.Matrix([[sp.Rational(variables[n].e[i].numerator, variables[n].e[i].denominator) for n in names] for i in range(len(BASE))])
    basis = []
    for v in A.nullspace():
        den = sp.ilcm(*[sp.fraction(x)[1] for x in v])
        v = v * den
        basis.append({n: sp.nsimplify(x) for n, x in zip(names, v) if x != 0})
    return basis


def check_pi_count(variables: dict, claimed: int) -> Result:
    """Number of independent dimensionless groups = n_variables - rank of the dimension matrix (Buckingham)."""
    groups = buckingham_pi(variables)
    claim = f"{claimed} independent dimensionless groups"
    if len(groups) == claimed:
        return verified("check_pi_count", claim, f"n_vars - rank = {len(groups)} (Buckingham)", groups=groups)
    return refuted("check_pi_count", claim, {"true_count": len(groups), "groups": groups}, evidence="exact nullspace of the dimension matrix")


def planck_units() -> dict:
    """Which combinations of hbar, c, G are a length, time, mass (exact exponents)."""
    out = {}
    for name, target in (("length", L_), ("time", T_), ("mass", M_)):
        sol = None
        import itertools
        for a, b, c in itertools.product([Fraction(k, 2) for k in range(-6, 7)], repeat=3):
            if (CONSTANTS["hbar"] ** a) * (CONSTANTS["c"] ** b) * (CONSTANTS["G"] ** c) == target:
                sol = (a, b, c)
        out[name] = sol
    return out
