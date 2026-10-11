"""pfv.lie: Lie algebra, representation and anomaly checks.

Conventions (stated once so claims can be compared): hermitian generators with
[T_a, T_b] = i f_abc T_c and Tr_fund(T_a T_b) = delta_ab / 2 for SU(N). Casimir C2(R) = sum_a T_a T_a,
Dynkin index T(R) from Tr_R(T_a T_b) = T(R) delta_ab. Sum rule: dim(R) C2(R) = dim(G) T(R).

Pitfalls handled:
  * Numerical generator tests use tolerance 1e-9 and are CONSISTENT only when a *family* is sampled;
    an explicit finite check on a named representation is exact up to floating-point and reported as VERIFIED
    only for exact (Rational) anomaly sums.
  * Weyl dimension formula is implemented from the Cartan matrix, so it holds for every classical and exceptional type.
"""
from __future__ import annotations

import itertools
from fractions import Fraction

import numpy as np
import sympy as sp
from sympy import Rational as Q

from .core import Result, verified, consistent, inconclusive, TOL
from .core import refuted as _refuted
from functools import partial as _partial
refuted = _partial(_refuted, evidence="exact rational or explicit-matrix witness (floating-point where stated)")


# --------------------------------------------------------------------------
# generators
# --------------------------------------------------------------------------
def su_generators(N: int):
    """Hermitian generators of su(N) in the fundamental, Tr(T_a T_b) = delta_ab/2."""
    gens = []
    for i in range(N):
        for j in range(i + 1, N):
            m = np.zeros((N, N), complex); m[i, j] = m[j, i] = 0.5; gens.append(m)
            m = np.zeros((N, N), complex); m[i, j] = -0.5j; m[j, i] = 0.5j; gens.append(m)
    for k in range(1, N):
        m = np.zeros((N, N), complex)
        for i in range(k):
            m[i, i] = 1
        m[k, k] = -k
        gens.append(m / np.sqrt(2 * k * (k + 1)))
    return gens


def so_generators(N: int):
    """Hermitian generators J_ij = -i(E_ij - E_ji) of so(N) in the vector representation."""
    gens = []
    for i in range(N):
        for j in range(i + 1, N):
            m = np.zeros((N, N), complex); m[i, j] = -1j; m[j, i] = 1j; gens.append(m)
    return gens


def conj_rep(gens):
    return [-g.conj() for g in gens]


def tensor_gens(g1, g2):
    d1, d2 = g1[0].shape[0], g2[0].shape[0]
    return [np.kron(a, np.eye(d2)) + np.kron(np.eye(d1), b) for a, b in zip(g1, g2)]


def su_rep(N: int, kind: str):
    """kind in {'fund','conj','sym','anti','adj'}."""
    F = su_generators(N)
    if kind == "fund":
        return F
    if kind == "conj":
        return conj_rep(F)
    if kind == "adj":
        f = structure_constants(F)
        return [(-1j * f[a]) for a in range(len(F))]
    two = tensor_gens(F, F)
    P = np.zeros((N * N, N * N))
    sign = 0.5 if kind == "sym" else -0.5
    for i in range(N):
        for j in range(N):
            P[i * N + j, i * N + j] += 0.5
            P[i * N + j, j * N + i] += sign
    w, V = np.linalg.eigh(P)
    B = V[:, w > 0.5]
    return [B.conj().T @ t @ B for t in two]


def structure_constants(gens):
    """f[a][b][c] defined by [T_a, T_b] = i f_abc T_c (projection with the Killing-type Gram matrix)."""
    n = len(gens)
    G = np.array([[np.trace(a @ b) for b in gens] for a in gens]).real
    Ginv = np.linalg.inv(G)
    f = np.zeros((n, n, n))
    for a in range(n):
        for b in range(n):
            comm = gens[a] @ gens[b] - gens[b] @ gens[a]
            proj = np.array([np.trace(comm @ gens[c]) for c in range(n)])
            coeffs = Ginv @ proj
            f[a, b, :] = (coeffs / 1j).real
    return f


# --------------------------------------------------------------------------
# algebra axioms
# --------------------------------------------------------------------------
def check_lie_algebra(gens, tol: float = TOL) -> Result:
    """Closure of the commutator on the span, real antisymmetric structure constants, Jacobi."""
    n = len(gens)
    claim = f"{n} matrices span a (compact, hermitian-basis) Lie algebra"
    for a in range(n):
        if np.abs(gens[a] - gens[a].conj().T).max() > tol:
            return refuted("check_lie_algebra", claim, a, detail=f"generator {a} is not hermitian")
    basis = np.array([g.reshape(-1) for g in gens]).T
    worst = 0.0
    for a in range(n):
        for b in range(a + 1, n):
            comm = (gens[a] @ gens[b] - gens[b] @ gens[a]).reshape(-1)
            x, *_ = np.linalg.lstsq(basis, comm, rcond=None)
            res = np.abs(basis @ x - comm).max()
            if res > tol:
                return refuted("check_lie_algebra", claim, (a, b), detail=f"[T_{a},T_{b}] is not in the span (residual {res:.2e}); the set is not closed")
            worst = max(worst, res)
    f = structure_constants(gens)
    if np.abs(f + f.transpose(1, 0, 2)).max() > 1e-8:
        return refuted("check_lie_algebra", claim, None, detail="f_abc not antisymmetric in (a,b)")
    jac = max(np.abs(sum(f[a, b, e] * f[e, c, d] + f[b, c, e] * f[e, a, d] + f[c, a, e] * f[e, b, d] for e in range(n))).max()
              for a in range(n) for b in range(n) for c in range(n) for d in range(n)) if n <= 16 else None
    if jac is not None and jac > 1e-8:
        return refuted("check_lie_algebra", claim, None, detail=f"Jacobi identity violated by {jac:.2e}")
    return verified("check_lie_algebra", claim, f"closure residual {worst:.1e}, f real+antisymmetric" + (f", Jacobi residual {jac:.1e}" if jac is not None else ""),
                    detail="floating-point exact to the stated residual")


def casimir_index(gens, tol: float = 1e-9):
    """(C2, T, dim) for an irreducible rep; raises if the quadratic Casimir is not proportional to the identity."""
    C = sum(g @ g for g in gens)
    d = gens[0].shape[0]
    c2 = np.trace(C).real / d
    if np.abs(C - c2 * np.eye(d)).max() > tol:
        raise ValueError("quadratic Casimir is not a multiple of identity: representation is reducible")
    T = np.trace(gens[0] @ gens[0]).real
    return float(c2), float(T), d


def check_casimir_sum_rule(gens, dim_G: int | None = None, tol: float = 1e-9) -> Result:
    """dim(R) C2(R) = dim(G) T(R) for an irreducible R (reducible reps need the per-block version)."""
    dG = dim_G if dim_G is not None else len(gens)
    claim = "dim(R) C2(R) = dim(G) T(R)"
    try:
        c2, T, d = casimir_index(gens)
    except ValueError as e:
        return inconclusive("check_casimir_sum_rule", claim, str(e))
    resid = d * c2 - dG * T
    if abs(resid) > tol:
        return refuted("check_casimir_sum_rule", claim, {"dimR*C2": d * c2, "dimG*T": dG * T}, detail=f"residual {resid:.2e}")
    return verified("check_casimir_sum_rule", claim, f"C2={c2:.6f}, T={T:.6f}, dim={d}; residual {resid:.1e}")


def casimir_spectrum(gens, decimals: int = 6) -> dict:
    """{C2 eigenvalue: total multiplicity} of the quadratic Casimir on a (reducible) rep.
    Different irreps can share a Casimir value; use dimension counts together with it."""
    C = sum(g @ g for g in gens)
    w = np.linalg.eigvalsh((C + C.conj().T) / 2)
    out = {}
    for x in np.round(w, decimals):
        out[float(x)] = out.get(float(x), 0) + 1
    return out


def check_decomposition(gens, expected: dict, decimals: int = 6) -> Result:
    """Check a claimed decomposition via Casimir eigenvalues, e.g. 3 x 3bar = 1 + 8 -> {0.0: 1, 3.0: 8}.
    Caveat built in: distinct irreps with equal C2 are lumped together."""
    spec = casimir_spectrum(gens, decimals)
    exp = {round(float(k), decimals): v for k, v in expected.items()}
    claim = f"Casimir spectrum {exp}"
    if spec == exp:
        return consistent("check_decomposition", claim, "Casimir eigenvalues and multiplicities match",
                          caveat="Irreps sharing a quadratic Casimir are indistinguishable by this test.")
    return refuted("check_decomposition", claim, {"actual": spec}, detail="Casimir spectrum differs from the claimed decomposition")


# --------------------------------------------------------------------------
# Cartan matrices and the Weyl dimension formula
# --------------------------------------------------------------------------
def cartan_matrix(kind: str, rank: int | None = None):
    """Cartan matrix C[i][j] = 2 (a_i, a_j) / (a_i, a_i), Bourbaki labelling. kind in A,B,C,D,E,F,G."""
    kind = kind.upper()
    if kind in "ABCD":
        n = rank
        C = [[0] * n for _ in range(n)]
        for i in range(n):
            C[i][i] = 2
        for i in range(n - 1):
            C[i][i + 1] = C[i + 1][i] = -1
        if kind == "B":
            C[n - 1][n - 2] = -2          # alpha_n is short
        if kind == "C":
            C[n - 2][n - 1] = -2          # alpha_n is long
        if kind == "D":
            C[n - 2][n - 1] = C[n - 1][n - 2] = 0
            C[n - 3][n - 1] = C[n - 1][n - 3] = -1
        return C
    if kind == "E":
        n = rank
        edges = [(1, 3), (3, 4), (4, 5), (5, 6), (2, 4)] + ([(6, 7)] if n >= 7 else []) + ([(7, 8)] if n == 8 else [])
        C = [[0] * n for _ in range(n)]
        for i in range(n):
            C[i][i] = 2
        for a, b in edges:
            C[a - 1][b - 1] = C[b - 1][a - 1] = -1
        return C
    if kind == "F":
        return [[2, -1, 0, 0], [-1, 2, -1, 0], [0, -2, 2, -1], [0, 0, -1, 2]]
    if kind == "G":
        return [[2, -3], [-1, 2]]   # alpha_1 short, alpha_2 long (Bourbaki)
    raise ValueError(kind)


def _root_lengths(C):
    n = len(C)
    ell = [None] * n
    ell[0] = Fraction(2)
    changed = True
    while changed:
        changed = False
        for i in range(n):
            for j in range(n):
                if C[i][j] != 0 and ell[i] is not None and ell[j] is None:
                    # C[i][j] ell_i = C[j][i] ell_j
                    ell[j] = Fraction(C[i][j]) * ell[i] / Fraction(C[j][i])
                    changed = True
    return ell


def positive_roots(C):
    n = len(C)
    level = [tuple(1 if i == j else 0 for j in range(n)) for i in range(n)]
    roots = set(level)
    all_levels = [level]
    while level:
        nxt = set()
        for beta in level:
            for i in range(n):
                q = 0
                cur = list(beta)
                while True:
                    cur[i] -= 1
                    if tuple(cur) in roots:
                        q += 1
                    else:
                        break
                pair = sum(C[i][j] * beta[j] for j in range(n))
                p = q - pair
                if p > 0:
                    new = list(beta); new[i] += 1
                    nxt.add(tuple(new))
        roots |= nxt
        level = sorted(nxt)
        if level:
            all_levels.append(level)
    return sorted(roots, key=lambda r: (sum(r), r))


def weyl_dimension(kind: str, rank: int, labels) -> int:
    """Dimension of the irrep with Dynkin labels `labels` (Bourbaki order) of simple Lie algebra kind+rank."""
    C = cartan_matrix(kind, rank)
    ell = _root_lengths(C)
    num = Fraction(1)
    for beta in positive_roots(C):
        top = sum(Fraction(b) * (lab + 1) * l for b, lab, l in zip(beta, labels, ell))
        bot = sum(Fraction(b) * l for b, l in zip(beta, ell))
        num *= top / bot
    assert num.denominator == 1
    return int(num)


def check_irrep_dimension(kind: str, rank: int, labels, claimed: int) -> Result:
    """Dimension of a Lie-algebra irrep from Dynkin labels by the Weyl dimension formula (types A,B,C,D,E,F,G), exact."""
    d = weyl_dimension(kind, rank, labels)
    claim = f"dim {kind}{rank}{list(labels)} = {claimed}"
    if d == claimed:
        return verified("check_irrep_dimension", claim, "Weyl dimension formula over all positive roots (exact rational arithmetic)")
    return refuted("check_irrep_dimension", claim, {"true_dimension": d})


def lie_algebra_dimension(kind: str, rank: int) -> int:
    return 2 * len(positive_roots(cartan_matrix(kind, rank))) + rank


# --------------------------------------------------------------------------
# anomalies (exact rational arithmetic)
# --------------------------------------------------------------------------
def T_su2(d: int) -> Q:
    return Q(d * (d * d - 1), 12)


_T_SU3 = {1: Q(0), 3: Q(1, 2), 6: Q(5, 2), 8: Q(3), 10: Q(15, 2)}


def T_su3(d: int) -> Q:
    if d not in _T_SU3:
        raise ValueError(f"no Dynkin index table entry for SU(3) dimension {d}")
    return _T_SU3[d]


def anomaly_sums(fields) -> dict:
    """fields = [(name, dim_SU3, dim_SU2, Y)], all LEFT-handed Weyl (flip right-handed ones to conjugates).
    Returns exact sums for U(1)^3, gravity^2-U(1), SU(3)^2-U(1), SU(2)^2-U(1), and the SU(2) Witten parity."""
    Y3 = grav = s3 = s2 = Q(0)
    witten2T = Q(0)
    for _, d3, d2, Y in fields:
        Y = Q(Y)
        Y3 += d3 * d2 * Y ** 3
        grav += d3 * d2 * Y
        s3 += T_su3(d3) * d2 * Y
        s2 += T_su2(d2) * d3 * Y
        witten2T += 2 * T_su2(d2) * d3
    return {"U1^3": Y3, "grav^2 U1": grav, "SU3^2 U1": s3, "SU2^2 U1": s2, "Witten 2T total": witten2T}


def check_anomaly_free(fields, name: str = "gauge theory") -> Result:
    """Exact gauge and gravitational anomaly sums plus the SU(2) Witten parity for a list of left-handed Weyl fields (name, dim SU3, dim SU2, Y)."""
    s = anomaly_sums(fields)
    claim = f"{name} is anomaly free"
    bad = {k: v for k, v in s.items() if k != "Witten 2T total" and v != 0}
    if s["Witten 2T total"] % 2 != 0:
        bad["Witten SU(2) parity"] = s["Witten 2T total"]
    if bad:
        return refuted("check_anomaly_free", claim, {k: str(v) for k, v in bad.items()},
                       detail="nonzero anomaly coefficient(s); these are exact rationals")
    return verified("check_anomaly_free", claim, "all perturbative coefficients vanish exactly; Witten parity even", sums={k: str(v) for k, v in s.items()})


STANDARD_MODEL_GEN = [("Q_L", 3, 2, Q(1, 6)), ("u^c", 3, 1, Q(-2, 3)), ("d^c", 3, 1, Q(1, 3)), ("L_L", 1, 2, Q(-1, 2)), ("e^c", 1, 1, Q(1))]


def su_cubic_coefficient(N: int, kind: str) -> float:
    """A(R) in Tr_R(T^a {T^b, T^c}) = A(R) d^abc (normalised to the fundamental), from explicit matrices."""
    ref = su_rep(N, "fund")
    rep = su_rep(N, kind)
    for a, b, c in itertools.combinations_with_replacement(range(len(ref)), 3):
        v = np.trace(ref[a] @ (ref[b] @ ref[c] + ref[c] @ ref[b]))
        if abs(v) > 1e-8:
            num = np.trace(rep[a] @ (rep[b] @ rep[c] + rep[c] @ rep[b]))
            return float((num / v).real)
    raise ValueError("SU(2) has no cubic invariant")


def su_cubic_formula(N: int, kind: str) -> int:
    return {"fund": 1, "conj": -1, "sym": N + 4, "anti": N - 4, "adj": 0}[kind]


def check_su_cubic(N: int, kind: str, claimed: float) -> Result:
    """Cubic anomaly coefficient A(R) of SU(N) reps (fund, conj, sym, anti) from explicit generators against a claim."""
    true = su_cubic_coefficient(N, kind)
    claim = f"A({kind}) of SU({N}) = {claimed}"
    if abs(true - claimed) < 1e-7:
        return verified("check_su_cubic", claim, f"explicit generators give {true:.6f} (formula {su_cubic_formula(N, kind)})")
    return refuted("check_su_cubic", claim, {"computed": round(true, 6)})


def beta0(C_A: Q, weyl_T: Q = Q(0), scalar_T: Q = Q(0)) -> Q:
    """One-loop coefficient b0 = 11/3 C_A - 2/3 sum_Weyl T - 1/3 sum_complex-scalars T (asymptotic freedom iff b0 > 0).
    Weyl fermions count with 2/3 each (a Dirac fermion is two Weyl)."""
    return Q(11, 3) * Q(C_A) - Q(2, 3) * Q(weyl_T) - Q(1, 3) * Q(scalar_T)


def sm_beta_coefficients(n_gen: int = 3):
    """Exact one-loop b_i (convention dg/dlnmu = -b g^3/16pi^2; b = -41/10, 19/6, 7 for U(1)_GUT, SU(2), SU(3))."""
    f = STANDARD_MODEL_GEN
    weyl3 = sum(T_su3(d3) * d2 for _, d3, d2, _ in f) * n_gen
    weyl2 = sum(T_su2(d2) * d3 for _, d3, d2, _ in f) * n_gen
    b3 = beta0(3, weyl3)
    b2 = beta0(2, weyl2, Q(1, 2))
    Yw = sum(d3 * d2 * Y ** 2 for _, d3, d2, Y in f) * n_gen
    b1 = -Q(3, 5) * (Q(2, 3) * Yw + Q(1, 3) * 2 * Q(1, 4))
    return {"b3": b3, "b2": b2, "b1_GUT": b1}
