"""pfv.linalg: exact and numerical linear-algebra checks.

Rules: use EXACT arithmetic (sympy Rational) for rank, definiteness, determinants and nullspaces of integer or
rational matrices. Floating-point rank and definiteness depend on a tolerance and are reported CONSISTENT with
the tolerance stated. Known traps: numpy.matrix_rank([[1,0],[0,1e-17]]) = 1; Cholesky fails on PSD-singular and on
ill-conditioned positive definite matrices (Hilbert 14); Sylvester's leading-minor test needs ALL principal minors
for semidefiniteness; e^(A+B) = e^A e^B only if [A,B] = 0 (sufficient, not necessary).
"""
from __future__ import annotations

import numpy as np
import sympy as sp
from sympy import Matrix, Rational

from .core import Result, verified, consistent, inconclusive, TOL, to_exact, cap_inexact, compare_claimed
from .core import refuted as _refuted
from functools import partial as _partial
refuted = _partial(_refuted, evidence="witness (exact for rational input, else floating-point beyond tolerance)")


def _exact(M):
    """(exact sympy Matrix, inexact). Float entries are read exactly as written (core.to_exact), never snapped:
    nsimplify turned [[1, 0.3333333333], [3, 1]] (det 1e-10) into a singular matrix."""
    if isinstance(M, Matrix):
        Me, inexact = to_exact(M)
        return Matrix(Me), inexact
    inexact = False
    rows = []
    for row in np.asarray(M, dtype=object).tolist():
        out = []
        for x in (row if isinstance(row, list) else [row]):
            v, i = to_exact(x)
            inexact = inexact or i
            out.append(v)
        rows.append(out)
    return Matrix(rows), inexact


def _done(res: Result, inexact: bool) -> Result:
    return cap_inexact(res, "matrix") if inexact else res


def check_rank(M, claimed: int) -> Result:
    """Exact rank (rational elimination) against a claim; shows numpy's tolerance-based rank for contrast."""
    Me, inexact = _exact(M)
    r = Me.rank()
    claim = f"rank = {claimed}"
    if r == claimed:
        return _done(verified("check_rank", claim, "exact rational elimination", rank=r), inexact)
    return _done(refuted("check_rank", claim, {"true_rank": r, "numpy_rank": int(np.linalg.matrix_rank(np.array(Me.tolist(), dtype=float)))},
                         detail="numpy.linalg.matrix_rank is tolerance dependent; the exact value is shown"), inexact)


def check_determinant(M, claimed) -> Result:
    """Exact determinant against a claimed value (a float claim within 1e-9 of the exact value is CONSISTENT, not VERIFIED)."""
    Me, inexact = _exact(M)
    d = Me.det()
    claim = f"det = {claimed}"
    status, _, _ = compare_claimed(d, claimed)
    if status == "equal":
        return _done(verified("check_determinant", claim, "exact"), inexact)
    if status == "approx":
        return _done(consistent("check_determinant", claim, f"exact det = {d}; the claimed decimal agrees within {TOL:g}",
                                caveat="the claimed value is a decimal approximation"), inexact)
    if status == "differ":
        return _done(refuted("check_determinant", claim, {"true_det": d}), inexact)
    return inconclusive("check_determinant", claim, f"could not decide whether det = {d} equals the claim")


def check_eigenvalues_exact(M, claimed) -> Result:
    """Claimed spectrum as a list with multiplicity or a dict {eigenvalue: multiplicity} (exact).

    Float claims are read exactly as written; a spectrum that matches only within 1e-9 is CONSISTENT, not VERIFIED."""
    Me, inexact = _exact(M)
    ev = Me.eigenvals()
    items = list(claimed.items()) if isinstance(claimed, dict) else [(c, 1) for c in claimed]
    claimed_d = {}
    for c, m in items:
        claimed_d[c] = claimed_d.get(c, 0) + m
    claim = f"eigenvalues = {claimed_d}"
    if sum(claimed_d.values()) != sum(ev.values()):
        return _done(refuted("check_eigenvalues_exact", claim, {"true": ev},
                             detail=f"{sum(ev.values())} eigenvalues with multiplicity, claimed {sum(claimed_d.values())}"), inexact)
    # match each true eigenvalue to a claimed one; worst status over the matching decides
    remaining = dict(claimed_d)
    worst = "equal"
    rank = {"equal": 0, "approx": 1, "unknown": 2, "differ": 3}
    for k, mult in ev.items():
        best = None
        for c in remaining:
            if remaining[c] < mult:
                continue
            status, _, _ = compare_claimed(k, c)
            if best is None or rank[status] < rank[best[0]]:
                best = (status, c)
        if best is None:
            return _done(refuted("check_eigenvalues_exact", claim, {"true": ev}, detail=f"no claimed eigenvalue with multiplicity {mult} for {k}"), inexact)
        status, c = best
        remaining[c] -= mult
        if remaining[c] == 0:
            del remaining[c]
        worst = max(worst, status, key=rank.get)
    if worst == "equal":
        return _done(verified("check_eigenvalues_exact", claim, "exact characteristic polynomial roots with multiplicity"), inexact)
    if worst == "approx":
        return _done(consistent("check_eigenvalues_exact", claim, f"exact spectrum {ev}; the claimed decimals agree within {TOL:g}",
                                caveat="claimed eigenvalues are decimal approximations"), inexact)
    if worst == "differ":
        return _done(refuted("check_eigenvalues_exact", claim, {"true": ev}), inexact)
    return inconclusive("check_eigenvalues_exact", claim, f"could not decide equality of the exact spectrum {ev} with the claim")


def check_diagonalizable(M, claimed: bool) -> Result:
    """Is the matrix diagonalizable (exact)? Compared with the claim."""
    Me, inexact = _exact(M)
    truth = Me.is_diagonalizable()
    claim = f"matrix is {'' if claimed else 'not '}diagonalizable"
    if truth == claimed:
        return _done(verified("check_diagonalizable", claim, "exact (algebraic = geometric multiplicity)"), inexact)
    return _done(refuted("check_diagonalizable", claim, {"truth": truth}, detail="compare geometric and algebraic multiplicities"), inexact)


def check_cayley_hamilton(M) -> Result:
    """p(A) = 0 for the characteristic polynomial of A (exact rational evaluation)."""
    Me, inexact = _exact(M)
    lam = sp.Symbol("lam")
    p = Me.charpoly(lam)
    coeffs = p.all_coeffs()
    n = Me.shape[0]
    acc = sp.zeros(n)
    for c in coeffs:
        acc = acc * Me + c * sp.eye(n)
    if acc.applyfunc(sp.simplify) == sp.zeros(n):
        return _done(verified("check_cayley_hamilton", f"p(A) = 0 with p = {p.as_expr()}", "exact matrix polynomial evaluation (Horner)"), inexact)
    return _done(refuted("check_cayley_hamilton", "p(A) = 0", acc), inexact)


def check_positive_definite(M, kind: str = "pd") -> Result:
    """kind in {'pd','psd','nd','nsd'}. Exact for rational input (all principal minors / LDL), tolerance-based otherwise."""
    claim = f"matrix is {kind}"
    arr = np.asarray(M)
    exact_input = isinstance(M, Matrix) or np.issubdtype(arr.dtype, np.integer) or arr.dtype == object
    if exact_input:
        Me, inexact = _exact(M)
        if inexact:  # object array holding floats: use the floating-point path below
            exact_input = False
    if exact_input:
        if Me != Me.T:
            return refuted("check_positive_definite", claim, None, detail="not symmetric (definiteness is about the symmetric part)")
        truth = {"pd": Me.is_positive_definite, "psd": Me.is_positive_semidefinite,
                 "nd": Me.is_negative_definite, "nsd": Me.is_negative_semidefinite}[kind]
        if truth:
            return verified("check_positive_definite", claim, "exact (sympy rational test)")
        return refuted("check_positive_definite", claim, {"eigenvalues": Me.eigenvals()}, detail="exact; a negative (or zero for strict) eigenvalue exists")
    A = np.asarray(M, dtype=float)
    if A.shape[0] <= 10 and np.isfinite(A).all():
        # every float64 is an exact dyadic rational: decide definiteness EXACTLY for the matrix as stored
        Me = Matrix(A.shape[0], A.shape[1], lambda i, j: sp.Rational(float(A[i, j])))
        if Me == Me.T:
            truth = {"pd": Me.is_positive_definite, "psd": Me.is_positive_semidefinite, "nd": Me.is_negative_definite, "nsd": Me.is_negative_semidefinite}[kind]
            note = "exact arithmetic on the float64 values as stored (e.g. 0.1 is 0.1000000000000000055...)"
            if truth:
                return cap_inexact(verified("check_positive_definite", claim, note), "matrix")
            return cap_inexact(refuted("check_positive_definite", claim, {"min_eigenvalue_float": float(np.linalg.eigvalsh((A + A.T) / 2).min())}, evidence=note), "matrix")
    w = np.linalg.eigvalsh((A + A.T) / 2)
    tol = 1e-12 * max(1.0, np.abs(w).max()) * len(w)
    if kind in ("pd", "psd"):
        lo = w.min()
        if lo > tol:
            return consistent("check_positive_definite", claim, f"smallest eigenvalue {lo:.3e} > tol {tol:.1e}", caveat="floating point; convert to Rational for an exact certificate")
        if lo < -tol:
            return refuted("check_positive_definite", claim, {"min_eig": float(lo)}, evidence="eigenvalue beyond floating-point tolerance")
        return inconclusive("check_positive_definite", claim, f"smallest eigenvalue {lo:.2e} is within tolerance {tol:.1e} of 0: cannot separate PD / PSD-singular / slightly indefinite in floating point; pass exact Rationals")
    hi = w.max()
    if hi < -tol:
        return consistent("check_positive_definite", claim, f"largest eigenvalue {hi:.3e} < -tol", caveat="floating point")
    if hi > tol:
        return refuted("check_positive_definite", claim, {"max_eig": float(hi)}, evidence="eigenvalue beyond floating-point tolerance")
    return inconclusive("check_positive_definite", claim, f"largest eigenvalue {hi:.2e} within tolerance of 0; pass exact Rationals")


def check_expm_identity(A, B, tol: float = 1e-9) -> Result:
    """Does e^(A+B) = e^A e^B hold for these matrices? Holds when [A,B] = 0; generally false otherwise."""
    from scipy.linalg import expm
    A, B = np.asarray(A, dtype=complex), np.asarray(B, dtype=complex)
    c = np.abs(A @ B - B @ A).max()
    lhs, rhs = expm(A + B), expm(A) @ expm(B)
    diff = np.abs(lhs - rhs).max()
    claim = "e^(A+B) = e^A e^B"
    if diff > tol:
        return refuted("check_expm_identity", claim, {"max_diff": float(diff), "|[A,B]|": float(c)},
                       detail="fails because A and B do not commute" if c > tol else "unexpected: commuting but unequal")
    return verified("check_expm_identity", claim, f"max |difference| = {diff:.1e}", detail=f"|[A,B]|_max = {c:.1e}")


def hunt_matrix_counterexample(pred, shape=(3, 3), n: int = 5000, claim: str = "pred(A) for all A", seed: int = 0,
                               families=("gaussian", "symmetric", "psd", "orthogonal", "nilpotent", "singular", "integer")) -> Result:
    """Claim: pred(A) is True for every matrix (of the given families). Returns REFUTED with the witness matrix."""
    rng = np.random.default_rng(seed)
    r, c = shape
    for t in range(n):
        fam = families[t % len(families)]
        A = rng.normal(size=shape)
        if fam == "symmetric":
            A = (A + A.T) / 2
        elif fam == "psd":
            A = A @ A.T
        elif fam == "orthogonal":
            A = np.linalg.qr(rng.normal(size=(r, r)))[0]
        elif fam == "nilpotent":
            A = np.triu(A, 1)
        elif fam == "singular":
            A[:, -1] = A[:, 0]
        elif fam == "integer":
            A = rng.integers(-3, 4, size=shape).astype(float)
        try:
            ok = pred(A)
        except Exception as e:
            return inconclusive("hunt_matrix_counterexample", claim, f"pred raised {type(e).__name__}: {e}")
        if not ok:
            return refuted("hunt_matrix_counterexample", claim, {"family": fam, "A": np.round(A, 4).tolist()})
    return consistent("hunt_matrix_counterexample", claim, f"{n} matrices over families {list(families)}",
                      caveat="Random search does not prove a universal matrix inequality.")
