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

from .core import Result, verified, consistent, inconclusive, TOL
from .core import refuted as _refuted
from functools import partial as _partial
refuted = _partial(_refuted, evidence="witness (exact for rational input, else floating-point beyond tolerance)")


def _exact(M) -> Matrix:
    if isinstance(M, Matrix):
        return M
    rows = np.asarray(M).tolist()
    return Matrix(rows).applyfunc(lambda x: sp.nsimplify(x, rational=True))


def check_rank(M, claimed: int) -> Result:
    """Exact rank (rational elimination) against a claim; shows numpy's tolerance-based rank for contrast."""
    Me = _exact(M)
    r = Me.rank()
    claim = f"rank = {claimed}"
    if r == claimed:
        return verified("check_rank", claim, "exact rational elimination", rank=r)
    return refuted("check_rank", claim, {"true_rank": r, "numpy_rank": int(np.linalg.matrix_rank(np.array(Me.tolist(), dtype=float)))},
                   detail="numpy.linalg.matrix_rank is tolerance dependent; the exact value is shown")


def check_determinant(M, claimed) -> Result:
    """Exact determinant against a claimed value."""
    d = _exact(M).det()
    claim = f"det = {claimed}"
    if sp.simplify(d - sp.sympify(claimed)) == 0:
        return verified("check_determinant", claim, "exact")
    return refuted("check_determinant", claim, {"true_det": d})


def check_eigenvalues_exact(M, claimed) -> Result:
    """Claimed spectrum as a list with multiplicity or a dict {eigenvalue: multiplicity} (exact)."""
    Me = _exact(M)
    ev = Me.eigenvals()
    if not isinstance(claimed, dict):
        claimed_d = {}
        for c in claimed:
            c = sp.nsimplify(c)
            claimed_d[c] = claimed_d.get(c, 0) + 1
    else:
        claimed_d = {sp.nsimplify(k): v for k, v in claimed.items()}
    claim = f"eigenvalues = {claimed_d}"
    ok = len(ev) == len(claimed_d) and all(any(sp.simplify(k - c) == 0 and v == claimed_d[c] for c in claimed_d) for k, v in ev.items())
    if ok:
        return verified("check_eigenvalues_exact", claim, "exact characteristic polynomial roots with multiplicity")
    return refuted("check_eigenvalues_exact", claim, {"true": ev})


def check_diagonalizable(M, claimed: bool) -> Result:
    """Is the matrix diagonalizable (exact)? Compared with the claim."""
    Me = _exact(M)
    truth = Me.is_diagonalizable()
    claim = f"matrix is {'' if claimed else 'not '}diagonalizable"
    if truth == claimed:
        return verified("check_diagonalizable", claim, "exact (algebraic = geometric multiplicity)")
    return refuted("check_diagonalizable", claim, {"truth": truth}, detail="compare geometric and algebraic multiplicities")


def check_cayley_hamilton(M) -> Result:
    """p(A) = 0 for the characteristic polynomial of A (exact rational evaluation)."""
    Me = _exact(M)
    lam = sp.Symbol("lam")
    p = Me.charpoly(lam)
    coeffs = p.all_coeffs()
    n = Me.shape[0]
    acc = sp.zeros(n)
    for c in coeffs:
        acc = acc * Me + c * sp.eye(n)
    if acc == sp.zeros(n):
        return verified("check_cayley_hamilton", f"p(A) = 0 with p = {p.as_expr()}", "exact matrix polynomial evaluation (Horner)")
    return refuted("check_cayley_hamilton", "p(A) = 0", acc)


def check_positive_definite(M, kind: str = "pd") -> Result:
    """kind in {'pd','psd','nd','nsd'}. Exact for rational input (all principal minors / LDL), tolerance-based otherwise."""
    claim = f"matrix is {kind}"
    arr = np.asarray(M)
    exact_input = isinstance(M, Matrix) or np.issubdtype(arr.dtype, np.integer) or arr.dtype == object
    if exact_input:
        Me = _exact(M)
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
                return verified("check_positive_definite", claim, note)
            return refuted("check_positive_definite", claim, {"min_eigenvalue_float": float(np.linalg.eigvalsh((A + A.T) / 2).min())}, evidence=note)
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
