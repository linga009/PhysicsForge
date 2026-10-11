"""pfv.combinat: counting, sequences, generating functions, recurrences, graph counts.

Brute force over small cases REFUTES a counting formula with an exact (n, brute, formula) witness. A match on small n
is CONSISTENT, except when a closed form is shown to satisfy a recurrence symbolically (VERIFIED by induction principle).
"""
from __future__ import annotations

import itertools
import math
from typing import Callable, Iterable, Sequence

import sympy as sp
from sympy import Rational

from .core import Result, verified, consistent, inconclusive
from .core import refuted as _refuted
from functools import partial as _partial
from .analysis import _S

refuted = _partial(_refuted, evidence="exact integer counterexample")

KNOWN = {
    "catalan": lambda n: int(sp.catalan(n)),
    "bell": lambda n: int(sp.bell(n)),
    "fibonacci": lambda n: int(sp.fibonacci(n)),
    "derangements": lambda n: int(sp.subfactorial(n)),
    "partitions": lambda n: int(sp.functions.combinatorial.numbers.partition(n)),
    "motzkin": lambda n: int(sum(math.comb(n, 2 * k) * int(sp.catalan(k)) for k in range(n // 2 + 1))),
    "factorial": lambda n: math.factorial(n),
    "central_binomial": lambda n: math.comb(2 * n, n),
}


def check_known_sequence(name: str, n: int, claimed: int) -> Result:
    """Catalan, Bell, Fibonacci, derangements, partitions, Motzkin, factorial or central binomial value against a claim."""
    true = KNOWN[name](n)
    claim = f"{name}({n}) = {claimed}"
    if true == claimed:
        return verified("check_known_sequence", claim, f"computed exactly ({name}({n}) = {true})")
    return refuted("check_known_sequence", claim, {"true_value": true})


def check_count_formula(formula: Callable[[int], int], brute: Callable[[int], int], ns: Iterable[int], claim: str = "") -> Result:
    """A counting formula against brute-force enumeration for the given n; one mismatch refutes."""
    claim = claim or "formula(n) = brute-force count(n)"
    ns = list(ns)
    for n in ns:
        f, b = formula(n), brute(n)
        if f != b:
            return refuted("check_count_formula", claim, {"n": n, "formula": f, "brute_force": b})
    return consistent("check_count_formula", claim, f"formula equals exhaustive enumeration for n in {ns}",
                      caveat="Small cases only. 1,2,4,8,16,31 (regions of a circle) looks like 2^(n-1) until n=6.")


def check_generating_function(gf, x, seq: Sequence, order: int | None = None) -> Result:
    """Coefficients of the power series of gf about 0 equal `seq` (exact, up to len(seq))."""
    gf, x = _S(gf), _S(x)
    order = order or len(seq)
    ser = sp.series(gf, x, 0, order).removeO()
    coeffs = [ser.coeff(x, k) for k in range(order)]
    claim = f"[x^n] {gf} = {list(seq)[:order]}"
    for k in range(order):
        if sp.simplify(coeffs[k] - sp.sympify(seq[k])) != 0:
            return refuted("check_generating_function", claim, {"n": k, "series_coefficient": coeffs[k], "claimed": seq[k]})
    return verified("check_generating_function", claim, f"series coefficients agree exactly for n < {order}", detail="exact for these coefficients; a statement for all n needs a proof")


def check_recurrence(closed, n, recurrence_residual: Callable, initial: dict) -> Result:
    """Closed form f(n) satisfies a recurrence for ALL n (symbolic) and the initial values: then f is THE sequence.
    `recurrence_residual(f)` returns the expression that must vanish, e.g. lambda f: f(n+2) - f(n+1) - f(n)."""
    n = _S(n)
    f = sp.Lambda(n, _S(closed))
    claim = f"{closed} satisfies the recurrence and initial conditions"
    for k, v in initial.items():
        if sp.simplify(f(k) - v) != 0:
            return refuted("check_recurrence", claim, {"n": k, "closed_form": sp.simplify(f(k)), "initial_value": v}, detail="initial condition fails")
    res = sp.simplify(sp.expand_func(recurrence_residual(f)))
    if res == 0:
        return verified("check_recurrence", claim, "residue of the recurrence simplifies to 0 for symbolic n; initial values match (induction principle)")
    for k in range(0, 12):
        val = sp.simplify(res.subs(n, k))
        if val != 0:
            return refuted("check_recurrence", claim, {"n": k, "residue": val})
    return inconclusive("check_recurrence", claim, f"symbolic residue {res} did not simplify to 0, but vanishes for n < 12")


def spanning_tree_count(adj) -> int:
    """Kirchhoff matrix-tree theorem: any cofactor of the Laplacian (exact integer)."""
    A = sp.Matrix(adj)
    L = sp.diag(*[sum(A[i, :]) for i in range(A.shape[0])]) - A
    return int(L[1:, 1:].det())


def check_spanning_trees(adj, claimed: int) -> Result:
    """Number of spanning trees by the matrix-tree theorem (exact determinant) against a claim."""
    true = spanning_tree_count(adj)
    claim = f"graph has {claimed} spanning trees"
    if true == claimed:
        return verified("check_spanning_trees", claim, "Kirchhoff matrix-tree theorem (exact determinant)")
    return refuted("check_spanning_trees", claim, {"true_count": true})


def complete_graph(n: int):
    return sp.Matrix(n, n, lambda i, j: 0 if i == j else 1)


def cycle_graph(n: int):
    return sp.Matrix(n, n, lambda i, j: 1 if (i - j) % n in (1, n - 1) and i != j else 0)


def chromatic_number_bruteforce(adj, kmax: int = 6) -> int:
    A = [list(map(int, adj.row(i))) for i in range(adj.shape[0])]
    n = len(A)
    for k in range(1, kmax + 1):
        def extend(i, col):
            if i == n:
                return True
            for c in range(k):
                if all(not (A[i][j] and col[j] == c) for j in range(i)):
                    col.append(c)
                    if extend(i + 1, col):
                        return True
                    col.pop()
            return False
        if extend(0, []):
            return k
    return kmax + 1


def check_chromatic_number(adj, claimed: int) -> Result:
    """Chromatic number by exhaustive backtracking against a claim."""
    true = chromatic_number_bruteforce(adj)
    claim = f"chromatic number = {claimed}"
    if true == claimed:
        return verified("check_chromatic_number", claim, "exhaustive backtracking colouring search (exact)")
    return refuted("check_chromatic_number", claim, {"true_chromatic_number": true})


def check_binomial_identity(lhs: Callable[[int, int], int], rhs: Callable[[int, int], int], nmax: int = 30, claim: str = "") -> Result:
    """lhs(n,k) = rhs(n,k) for all 0 <= k <= n <= nmax with exact integers."""
    claim = claim or "lhs(n,k) = rhs(n,k)"
    for n in range(0, nmax + 1):
        for k in range(0, n + 1):
            if lhs(n, k) != rhs(n, k):
                return refuted("check_binomial_identity", claim, {"n": n, "k": k, "lhs": lhs(n, k), "rhs": rhs(n, k)})
    return consistent("check_binomial_identity", claim, f"exact for all 0<=k<=n<={nmax}", caveat="Finite range; combine with a proof (induction / generating function).")
