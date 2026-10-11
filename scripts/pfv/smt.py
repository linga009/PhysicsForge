"""pfv.smt: decision procedures. Real polynomial inequalities (complete), integer arithmetic, propositional logic.

The real-arithmetic checker uses z3's nlsat, which is a DECISION procedure for the first-order theory of real closed
fields: for polynomial constraints, "unsat" is a proof and "sat" comes with a counterexample, which this module
re-checks exactly in sympy before reporting REFUTED. z3 is optional (`pip install z3-solver`); without it the z3-based
checks return INCONCLUSIVE with an install hint. Propositional checks use sympy.logic and need no extra package.

Integer constraints (integers=...) are only semi-decided by z3: sat is a witness, unsat is a proof, "unknown" is INCONCLUSIVE.
Division and negative powers add "denominator != 0" to the domain; sqrt(x) adds x >= 0 and an auxiliary root variable.
"""
from __future__ import annotations

import itertools

import sympy as sp

from .core import Result, verified, consistent, inconclusive, unify, to_exact, cap_inexact
from .core import refuted as _refuted
from .analysis import _S

try:  # optional dependency
    import z3 as _z3
except Exception:  # pragma: no cover
    _z3 = None

_HINT = "z3 is not installed (pip install z3-solver)"


class _Unsupported(Exception):
    pass


class _Translator:
    def __init__(self, integers=()):
        self.vars = {}
        self.integers = set(integers)
        self.domain = []   # side conditions: denominators != 0, radicands >= 0, aux root definitions
        self._aux = 0

    def var(self, s):
        if s.name not in self.vars:
            self.vars[s.name] = _z3.Int(s.name) if s.name in self.integers else _z3.Real(s.name)
        return self.vars[s.name]

    def num(self, e):
        # Floats were already converted exactly by to_exact; never nsimplify here (it snaps 0.3333333333 to 1/3).
        if e.is_Integer:
            return _z3.IntVal(int(e)) if self.integers else _z3.RealVal(int(e))
        if e.is_Rational:
            return _z3.RealVal(f"{e.p}/{e.q}")
        raise _Unsupported(f"non-rational constant {e}")

    def term(self, e):
        e = sp.sympify(e)
        if e.is_Number:
            return self.num(e)
        if e.is_Symbol:
            return self.var(e)
        if e.is_Add:
            return sum((self.term(a) for a in e.args[1:]), self.term(e.args[0]))
        if e.is_Mul:
            out = self.term(e.args[0])
            for a in e.args[1:]:
                out = out * self.term(a)
            return out
        if e.is_Pow:
            b, ex = e.args
            if ex.is_Integer:
                n = int(ex)
                if n >= 0:
                    out = _z3.RealVal(1) if not self.integers else _z3.IntVal(1)
                    base = self.term(b)
                    for _ in range(n):
                        out = out * base
                    return out
                self.domain.append(self.term(b) != 0)
                t = self.term(sp.Pow(b, -n))
                return _z3.RealVal(1) / (_z3.ToReal(t) if _z3.is_int(t) else t)
            if ex == sp.Rational(1, 2):
                self._aux += 1
                r = _z3.Real(f"_sqrt{self._aux}")
                a = self.term(b)
                self.domain.extend([a >= 0, r >= 0, r * r == a])
                return r
            raise _Unsupported(f"power {e}")
        if isinstance(e, sp.Mod):
            a, b = self.term(e.args[0]), self.term(e.args[1])
            if not (_z3.is_int(a) and _z3.is_int(b)):
                raise _Unsupported("Mod needs integer operands (declare them in integers=)")
            self.domain.append(b != 0)
            return a % b
        if isinstance(e, sp.Abs):
            a = self.term(e.args[0])
            return _z3.If(a >= 0, a, -a)
        if isinstance(e, (sp.Max, sp.Min)):
            ts = [self.term(a) for a in e.args]
            out = ts[0]
            for t in ts[1:]:
                out = _z3.If(t > out, t, out) if isinstance(e, sp.Max) else _z3.If(t < out, t, out)
            return out
        raise _Unsupported(f"{type(e).__name__}: {e}")

    def formula(self, f):
        f = sp.sympify(f)
        if f is sp.true or f == True:  # noqa: E712
            return _z3.BoolVal(True)
        if f is sp.false or f == False:  # noqa: E712
            return _z3.BoolVal(False)
        if isinstance(f, sp.And):
            return _z3.And(*[self.formula(a) for a in f.args])
        if isinstance(f, sp.Or):
            return _z3.Or(*[self.formula(a) for a in f.args])
        if isinstance(f, sp.Not):
            return _z3.Not(self.formula(f.args[0]))
        if isinstance(f, sp.Implies):
            return _z3.Implies(self.formula(f.args[0]), self.formula(f.args[1]))
        if isinstance(f, sp.core.relational.Relational):
            a, b = self.term(f.lhs), self.term(f.rhs)
            return {sp.GreaterThan: a >= b, sp.LessThan: a <= b, sp.StrictGreaterThan: a > b, sp.StrictLessThan: a < b,
                    sp.Equality: a == b, sp.Unequality: a != b}[type(f)]
        raise _Unsupported(f"formula {f}")


_REL = {"Eq": lambda a, b: sp.Eq(a, b, evaluate=False), "NotEq": lambda a, b: sp.Ne(a, b, evaluate=False),
        "Lt": lambda a, b: sp.Lt(a, b, evaluate=False), "LtE": lambda a, b: sp.Le(a, b, evaluate=False),
        "Gt": lambda a, b: sp.Gt(a, b, evaluate=False), "GtE": lambda a, b: sp.Ge(a, b, evaluate=False)}


def _is_formula_node(n):
    import ast
    if isinstance(n, (ast.Compare, ast.BoolOp)):
        return True
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.Not, ast.Invert)):
        return _is_formula_node(n.operand)
    if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.BitAnd, ast.BitOr, ast.RShift)):
        return _is_formula_node(n.left) and _is_formula_node(n.right)
    return False


def _conv(n):
    """ast node -> sympy Boolean or expression. `==` becomes sympy Eq (a bare sympify would turn it into a Python bool)."""
    import ast
    if isinstance(n, ast.Compare):
        parts = []
        left = n.left
        for op, right in zip(n.ops, n.comparators):
            parts.append(_REL[type(op).__name__](_conv(left), _conv(right)))
            left = right
        return parts[0] if len(parts) == 1 else sp.And(*parts)
    if isinstance(n, ast.BoolOp):
        vals = [_conv(v) for v in n.values]
        return sp.And(*vals) if isinstance(n.op, ast.And) else sp.Or(*vals)
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.Not, ast.Invert)) and _is_formula_node(n.operand):
        return sp.Not(_conv(n.operand))
    if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.BitAnd, ast.BitOr, ast.RShift)) and _is_formula_node(n):
        l, r = _conv(n.left), _conv(n.right)
        return sp.And(l, r) if isinstance(n.op, ast.BitAnd) else sp.Or(l, r) if isinstance(n.op, ast.BitOr) else sp.Implies(l, r)
    return _S(ast.unparse(n))


def _as_formula(s):
    """Parse a hypothesis or claim: strings like "a*b*c == 1", "x>0 and y>0", "(a>0) >> (a**2>0)"; sympy objects pass through."""
    import ast
    if isinstance(s, str):
        f = _conv(ast.parse(s.strip(), mode="eval").body)
    else:
        f = sp.sympify(s)
    if f is sp.true or f is sp.false or isinstance(f, bool):
        raise _Unsupported(f"{s!r} collapsed to the constant {f} before reaching the solver")
    return f


def _model_value(model, v):
    val = model.eval(v, model_completion=True)
    try:
        if _z3.is_rational_value(val) or _z3.is_int_value(val):
            return sp.Rational(val.as_fraction().numerator, val.as_fraction().denominator) if hasattr(val, "as_fraction") else sp.Integer(val.as_long())
    except Exception:
        pass
    try:
        return sp.Float(val.approx(40).as_decimal(40).rstrip("?"), 40)
    except Exception:
        return sp.Symbol(str(val))


def check_real_claim(claim, hypotheses=(), integers=(), timeout_ms: int = 20000) -> Result:
    """Is `claim` implied by `hypotheses` for ALL real (or, for names in `integers`, integer) values? Complete for real polynomial arithmetic.

    claim / hypotheses are strings such as "a**2+b**2 >= 2*a*b" and ["a>0","b>0"]; combine with & | ~ >>. unsat of
    (hyps and not claim) is a proof (VERIFIED); a model is re-checked exactly in sympy (REFUTED with the witness)."""
    name = "check_real_claim"
    text = f"{claim}" + (f"  given  {', '.join(map(str, hypotheses))}" if hypotheses else "")
    if _z3 is None:
        return inconclusive(name, text, _HINT)
    res = _check_real_claim(claim, hypotheses, integers, timeout_ms, name, text)
    return cap_inexact(res, "claim") if res.data.pop("_inexact", False) and res.decisive else res


def _check_real_claim(claim, hypotheses, integers, timeout_ms, name, text) -> Result:
    inexact = False
    try:
        c = _as_formula(claim)
        hs = [_as_formula(h) for h in hypotheses]
        c, inexact = to_exact(c)
        exact_hs = []
        for h in hs:
            h, i = to_exact(h)
            inexact = inexact or i
            exact_hs.append(h)
        hs = exact_hs
        allf = unify(c, *hs) if hs else [unify(c)]
        allf = allf if isinstance(allf, list) else [allf]
        c, hs = allf[0], allf[1:]
        tr = _Translator(integers)
        zc = tr.formula(c)
        zh = [tr.formula(h) for h in hs]
    except _Unsupported as e:
        return inconclusive(name, text, f"unsupported construct: {e}")
    except Exception as e:
        return inconclusive(name, text, f"could not parse: {type(e).__name__}: {e}")
    s = _z3.Solver()
    s.set("timeout", int(timeout_ms))
    s.add(*zh, *tr.domain, _z3.Not(zc))
    r = s.check()
    if r == _z3.unsat:
        return verified(name, text, f"z3 {_z3.get_version_string()}: hypotheses and not(claim) is unsatisfiable"
                        + (" (real closed field decision procedure)" if not integers else " (integer reasoning is sound but incomplete)")
                        + ("; holds on the domain where every denominator is nonzero and every square root is real" if tr.domain else ""),
                        solver="z3", _inexact=inexact)
    if r == _z3.unknown:
        hint = "; nonlinear integer/modular claims are often beyond z3: try pfv.numtheory (check_congruence, modular_obstruction, check_lte) or a proof by descent" if integers else ""
        return inconclusive(name, text, f"z3 returned unknown ({s.reason_unknown()}){hint}")
    m = s.model()
    syms = {n: sp.Symbol(n) for n in tr.vars}
    # exact re-check in sympy
    wit = {}
    exact = True
    for n, v in tr.vars.items():
        val = _model_value(m, v)
        wit[n] = val
        exact = exact and val.is_Rational
    sub = {s_: wit[s_.name] for s_ in set().union(*[f.free_symbols for f in [c, *hs]]) if s_.name in wit}
    try:
        hyp_ok = all(bool(sp.simplify(h.subs(sub))) if exact else bool(h.subs(sub).evalf(30)) for h in hs)
        claim_val = c.subs(sub)
        claim_ok = bool(sp.simplify(claim_val)) if exact else bool(claim_val.evalf(30))
    except Exception as e:
        return inconclusive(name, text, f"z3 model could not be re-checked in sympy ({type(e).__name__}); model {wit}")
    if hyp_ok and not claim_ok:
        ev = "z3 model re-checked in exact rational arithmetic" if exact else "z3 model (algebraic numbers) re-checked at 30 digits"
        return _refuted(name, text, {k: str(v) for k, v in wit.items()}, evidence=ev, _inexact=inexact)
    return inconclusive(name, text, f"z3 reported a model that sympy does not confirm (division-by-zero or sqrt convention?): {wit}")


def check_no_integer_solutions(constraints, variables, bound: int | None = None, timeout_ms: int = 20000) -> Result:
    """Do the integer constraints have NO solution (optionally only with |v| <= bound)? z3 unsat is a proof (VERIFIED); a solution is re-checked exactly and returned (REFUTED)."""
    name = "check_no_integer_solutions"
    text = f"no integers {', '.join(map(str, variables))} satisfy " + " and ".join(map(str, constraints)) + (f" with |v| <= {bound}" if bound is not None else "")
    cs = list(constraints)
    if bound is not None:
        cs += [f"{v} >= {-bound}" for v in variables] + [f"{v} <= {bound}" for v in variables]
    claim = "~(" + " & ".join(f"({c})" for c in cs) + ")"
    res = check_real_claim(claim, integers=tuple(str(v) for v in variables), timeout_ms=timeout_ms)
    if res.verified:
        return verified(name, text, res.evidence.replace("hypotheses and not(claim) is unsatisfiable", "the constraints are unsatisfiable over the integers"))
    if res.refuted:
        return _refuted(name, text, res.witness, evidence=res.evidence)
    return inconclusive(name, text, res.detail)


def check_tautology(formula, symbols=None) -> Result:
    """Is the propositional formula (symbols are booleans; use & | ~ >> and Equivalent) true under every assignment? Exhaustive truth table via sympy.logic."""
    from sympy.logic.boolalg import Equivalent, Implies, And, Or, Not, Xor
    from sympy.logic.inference import satisfiable
    name = "check_tautology"
    try:
        f = sp.sympify(formula, locals={"Equivalent": Equivalent, "Implies": Implies, "And": And, "Or": Or, "Not": Not, "Xor": Xor}) if isinstance(formula, str) else formula
    except Exception as e:
        return inconclusive(name, str(formula), f"could not parse: {e}")
    text = f"{f} is a tautology"
    m = satisfiable(Not(f))
    if m is False:
        return verified(name, text, "negation is unsatisfiable (complete SAT search)")
    return _refuted(name, text, {str(k): bool(v) for k, v in m.items()}, evidence="falsifying assignment (exact, boolean)")


def check_logical_equivalence(f, g) -> Result:
    """Are two propositional formulas equivalent? Decided exactly by SAT on f XOR g."""
    from sympy.logic.boolalg import Equivalent
    F = sp.sympify(f) if isinstance(f, str) else f
    G = sp.sympify(g) if isinstance(g, str) else g
    r = check_tautology(Equivalent(F, G))
    r.check = "check_logical_equivalence"
    r.claim = f"{F}  <=>  {G}"
    return r
