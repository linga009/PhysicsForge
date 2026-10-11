"""pfv.quantum: quantum-mechanics and quantum-information checks (finite dimension, hbar = 1).

Evidence rules:
  * A property of ONE explicit matrix/state (is it a density matrix, unitary, a channel, entangled by PPT)
    is decided up to floating-point tolerance: reported VERIFIED/REFUTED with the numerical margin shown.
  * A claim about ALL states ("S(A|B) >= 0", "F(rho,sigma) <= ...") can be REFUTED by one witness state
    but only ever CONSISTENT when no witness is found. Random states have weak power (they are generically
    full rank and near the maximally mixed point), so `hunt_state_counterexample` mixes in structured
    states: product, Bell, GHZ, W, pure, rank-deficient and diagonal.
"""
from __future__ import annotations

import itertools
from typing import Callable, Sequence

import numpy as np
from scipy.linalg import expm, logm

from .core import Result, verified, consistent, inconclusive, TOL
from .core import refuted as _refuted
from functools import partial as _partial
refuted = _partial(_refuted, evidence="floating-point witness beyond tolerance")

I2 = np.eye(2, dtype=complex)
SX = np.array([[0, 1], [1, 0]], dtype=complex)
SY = np.array([[0, -1j], [1j, 0]], dtype=complex)
SZ = np.array([[1, 0], [0, -1]], dtype=complex)
PAULIS = [I2, SX, SY, SZ]


def comm(A, B):
    return A @ B - B @ A


def anticomm(A, B):
    return A @ B + B @ A


def dagger(A):
    return np.conj(A).T


# --------------------------------------------------------------------------
# angular momentum
# --------------------------------------------------------------------------
def spin_matrices(j):
    """(Jx, Jy, Jz) in the |j, m> basis, m = j, j-1, ..., -j. j may be an int, float (half-integer) or Fraction."""
    j = float(j)
    d = int(round(2 * j + 1))
    if abs(2 * j - round(2 * j)) > 1e-12 or d < 1:
        raise ValueError("j must be a non-negative integer or half-integer")
    m = np.array([j - k for k in range(d)])
    Jz = np.diag(m).astype(complex)
    Jp = np.zeros((d, d), complex)
    for k in range(1, d):
        mm = m[k]
        Jp[k - 1, k] = np.sqrt(j * (j + 1) - mm * (mm + 1))
    Jm = dagger(Jp)
    return (Jp + Jm) / 2, (Jp - Jm) / (2j), Jz


def check_angular_momentum_algebra(Jx, Jy, Jz, tol: float = TOL) -> Result:
    """[Jx,Jy] = i Jz (cyclic), hermiticity, and J^2 = j(j+1) with the right j for an irrep."""
    claim = "J_i satisfy the su(2) algebra"
    for name, J in (("Jx", Jx), ("Jy", Jy), ("Jz", Jz)):
        if np.abs(J - dagger(J)).max() > tol:
            return refuted("check_angular_momentum_algebra", claim, name, detail=f"{name} is not hermitian")
    for (a, A), (b, B), (c, C) in (("x", Jx), ("y", Jy), ("z", Jz)), (("y", Jy), ("z", Jz), ("x", Jx)), (("z", Jz), ("x", Jx), ("y", Jy)):
        r = np.abs(comm(A, B) - 1j * C).max()
        if r > tol:
            return refuted("check_angular_momentum_algebra", claim, f"[J{a},J{b}]", detail=f"[J{a},J{b}] - iJ{c} has max entry {r:.3e}")
    J2 = Jx @ Jx + Jy @ Jy + Jz @ Jz
    d = Jx.shape[0]
    lam = np.trace(J2).real / d
    j = (-1 + np.sqrt(1 + 4 * lam)) / 2
    irrep = np.abs(J2 - lam * np.eye(d)).max() < 1e-8 and abs(2 * j + 1 - d) < 1e-8
    return verified("check_angular_momentum_algebra", claim, f"cyclic commutators exact to {tol:g}; J^2 = {lam:.6f}",
                    detail=f"j = {j:.4f}; {'irreducible' if irrep else 'reducible (J^2 not a multiple of identity or dimension mismatch)'}")


def check_pauli_algebra(S=(SX, SY, SZ), tol: float = TOL) -> Result:
    """sigma_i sigma_j = delta_ij + i eps_ijk sigma_k for the given matrices."""
    claim = "sigma_i sigma_j = delta_ij + i eps_ijk sigma_k"
    eps = np.zeros((3, 3, 3))
    for i, j, k in itertools.permutations(range(3)):
        eps[i, j, k] = np.linalg.det(np.eye(3)[[i, j, k]])
    for i in range(3):
        for j in range(3):
            rhs = (i == j) * np.eye(2) + 1j * sum(eps[i, j, k] * S[k] for k in range(3))
            r = np.abs(S[i] @ S[j] - rhs).max()
            if r > tol:
                return refuted("check_pauli_algebra", claim, (i, j), detail=f"residual {r:.2e}")
    return verified("check_pauli_algebra", claim, f"all 9 products match to {tol:g}")


# --------------------------------------------------------------------------
# states and operators
# --------------------------------------------------------------------------
def check_hermitian(A, tol: float = TOL) -> Result:
    """Is A hermitian? Reports the worst entry."""
    r = np.abs(A - dagger(A)).max()
    claim = "A is hermitian"
    if r > tol:
        i, j = np.unravel_index(np.abs(A - dagger(A)).argmax(), A.shape)
        return refuted("check_hermitian", claim, (int(i), int(j)), detail=f"|A_ij - conj(A_ji)| = {r:.3e}")
    return verified("check_hermitian", claim, f"max |A - A^dagger| = {r:.1e}")


def check_unitary(U, tol: float = TOL) -> Result:
    """Is U unitary (U^dagger U = I)?"""
    r = np.abs(dagger(U) @ U - np.eye(U.shape[0])).max()
    claim = "U is unitary"
    if r > tol:
        return refuted("check_unitary", claim, None, detail=f"max |U^dagger U - I| = {r:.3e}")
    return verified("check_unitary", claim, f"max |U^dagger U - I| = {r:.1e}")


def check_density_matrix(rho, tol: float = 1e-9) -> Result:
    """Hermitian, trace 1, positive semidefinite. Reports the minimum eigenvalue."""
    rho = np.asarray(rho, dtype=complex)
    claim = "rho is a density matrix"
    if np.abs(rho - dagger(rho)).max() > tol:
        return refuted("check_density_matrix", claim, None, detail="not hermitian")
    tr = np.trace(rho).real
    if abs(tr - 1) > tol:
        return refuted("check_density_matrix", claim, tr, detail=f"trace = {tr:.10g}, not 1")
    w = np.linalg.eigvalsh((rho + dagger(rho)) / 2)
    if w.min() < -tol:
        return refuted("check_density_matrix", claim, float(w.min()), detail=f"negative eigenvalue {w.min():.3e}")
    purity = float(np.sum(w ** 2))
    return verified("check_density_matrix", claim, f"hermitian, Tr = 1, min eigenvalue {w.min():.2e}",
                    detail=f"purity Tr rho^2 = {purity:.6f}", purity=purity)


def ket(v):
    v = np.asarray(v, dtype=complex).reshape(-1)
    return v / np.linalg.norm(v)


def dm(psi):
    psi = ket(psi)
    return np.outer(psi, psi.conj())


def ptrace(rho, dims: Sequence[int], keep: Sequence[int]):
    """Partial trace keeping the subsystems in `keep` (indices into dims)."""
    n = len(dims)
    r = np.asarray(rho).reshape(list(dims) + list(dims))
    trace_out = sorted((i for i in range(n) if i not in keep), reverse=True)
    for i in trace_out:
        cur = r.ndim // 2
        r = np.trace(r, axis1=i, axis2=i + cur)
    d = int(np.prod([dims[i] for i in keep])) if keep else 1
    return r.reshape(d, d)


def von_neumann_entropy(rho, base: float = 2.0) -> float:
    w = np.linalg.eigvalsh((rho + dagger(rho)) / 2)
    w = w[w > 1e-14]
    return float(-(w * np.log(w)).sum() / np.log(base))


def relative_entropy(rho, sigma, base: float = 2.0) -> float:
    """S(rho||sigma); +inf if supp(rho) is not inside supp(sigma)."""
    wr, Vr = np.linalg.eigh((rho + dagger(rho)) / 2)
    ws, Vs = np.linalg.eigh((sigma + dagger(sigma)) / 2)
    P = Vs[:, ws < 1e-12]
    if P.size and np.abs(P.conj().T @ rho @ P).max() > 1e-10:
        return float("inf")
    lr = Vr @ np.diag(np.log(np.where(wr > 1e-14, wr, 1.0))) @ dagger(Vr)
    ls = Vs @ np.diag(np.log(np.where(ws > 1e-14, ws, 1.0))) @ dagger(Vs)
    return float(np.real(np.trace(rho @ (lr - ls))) / np.log(base))


def fidelity(rho, sigma) -> float:
    """Uhlmann fidelity F = (Tr sqrt(sqrt(rho) sigma sqrt(rho)))^2."""
    w, V = np.linalg.eigh((rho + dagger(rho)) / 2)
    sq = V @ np.diag(np.sqrt(np.clip(w, 0, None))) @ dagger(V)
    m = sq @ sigma @ sq
    ev = np.linalg.eigvalsh((m + dagger(m)) / 2)
    return float(np.sum(np.sqrt(np.clip(ev, 0, None))) ** 2)


def trace_distance(rho, sigma) -> float:
    return 0.5 * float(np.abs(np.linalg.eigvalsh((rho - sigma + dagger(rho - sigma)) / 2)).sum())


def concurrence(rho) -> float:
    """Wootters concurrence for two qubits."""
    Y = np.kron(SY, SY)
    R = rho @ Y @ rho.conj() @ Y
    ev = np.sort(np.sqrt(np.clip(np.linalg.eigvals(R).real, 0, None)))[::-1]
    return float(max(0.0, ev[0] - ev[1] - ev[2] - ev[3]))


def partial_transpose(rho, dims, sys: int = 1):
    n = len(dims)
    r = np.asarray(rho).reshape(list(dims) + list(dims))
    axes = list(range(2 * n))
    axes[sys], axes[n + sys] = axes[n + sys], axes[sys]
    d = int(np.prod(dims))
    return r.transpose(axes).reshape(d, d)


def check_entangled(rho, dims=(2, 2), tol: float = 1e-10) -> Result:
    """PPT test. A negative partial-transpose eigenvalue PROVES entanglement in any dimension.
    PPT proves separability only for 2x2 and 2x3; otherwise a PPT state may be bound-entangled."""
    pt = partial_transpose(rho, dims, 1)
    mn = np.linalg.eigvalsh((pt + dagger(pt)) / 2).min()
    claim = "state is entangled"
    if mn < -tol:
        return verified("check_entangled", claim, f"partial transpose has eigenvalue {mn:.4f} < 0 (Peres): entangled")
    if sorted(dims) in ([2, 2], [2, 3]):
        return refuted("check_entangled", claim, float(mn), detail="PPT and dimension 2x2/2x3: separable (Horodecki)")
    return inconclusive("check_entangled", claim, f"PPT (min eig {mn:.2e}) but dims {dims}: could be separable or bound entangled")


def check_entanglement_entropy(state, dims: Sequence[int], keep: Sequence[int], claimed_bits: float, tol: float = 1e-9) -> Result:
    """Von Neumann entropy (bits) of the reduced state on the subsystems in `keep`, against a claimed value.

    `state` is a ket or a density matrix on the tensor product with local dimensions `dims`. For a pure global state
    this IS the entanglement entropy (0 for a product state, log2 d for a maximally entangled one); for a mixed global
    state it is only the entropy of the marginal, not an entanglement measure, and the result says so."""
    arr = np.asarray(state, dtype=complex)
    rho = dm(arr) if arr.ndim == 1 or 1 in arr.shape else arr
    keep = list(keep)
    claim = f"S(rho_{keep}) = {claimed_bits} bits"
    if rho.shape[0] != int(np.prod(dims)):
        return inconclusive("check_entanglement_entropy", claim, f"state dimension {rho.shape[0]} != prod(dims) = {int(np.prod(dims))}")
    valid = check_density_matrix(rho, tol=1e-8)
    if not valid.verified:
        return inconclusive("check_entanglement_entropy", claim, f"input is not a valid state: {valid.detail}")
    S = von_neumann_entropy(ptrace(rho, dims, keep), base=2.0)
    pure = abs(valid.data["purity"] - 1) < 1e-8
    caveat = "" if pure else "global state is mixed: this is the entropy of the marginal, NOT an entanglement measure"
    gap = abs(S - float(claimed_bits))
    if gap > tol:
        return refuted("check_entanglement_entropy", claim, {"computed_bits": S}, detail=f"|S - claimed| = {gap:.3e}")
    res = verified("check_entanglement_entropy", claim, f"S = {S:.12f} bits (eigenvalues of the reduced state, LAPACK), |S - claimed| = {gap:.1e}")
    res.caveat = caveat
    return res


# --------------------------------------------------------------------------
# channels
# --------------------------------------------------------------------------
def choi_from_map(Phi: Callable, d: int):
    J = np.zeros((d * d, d * d), complex)
    for i in range(d):
        for j in range(d):
            E = np.zeros((d, d), complex); E[i, j] = 1
            J += np.kron(E, Phi(E))
    return J


def choi_from_kraus(Ks, d: int):
    return choi_from_map(lambda X: sum(K @ X @ dagger(K) for K in Ks), d)


def check_channel(Phi_or_kraus, d: int, tol: float = 1e-10) -> Result:
    """CPTP test through the Choi matrix: J >= 0 (complete positivity) and Tr_out J = I (trace preservation)."""
    if callable(Phi_or_kraus):
        J = choi_from_map(Phi_or_kraus, d)
    else:
        J = choi_from_kraus(Phi_or_kraus, d)
    claim = "map is CPTP"
    herm = np.abs(J - dagger(J)).max()
    if herm > 1e-8:
        return refuted("check_channel", claim, None, detail=f"Choi matrix not hermitian ({herm:.2e}): map is not hermiticity preserving")
    mn = np.linalg.eigvalsh((J + dagger(J)) / 2).min()
    tp = np.abs(np.einsum("iaja->ij", J.reshape(d, d, d, d)) - np.eye(d)).max()
    if mn < -tol:
        return refuted("check_channel", claim, float(mn), detail=f"Choi matrix has eigenvalue {mn:.3e} < 0: not completely positive")
    if tp > tol:
        return refuted("check_channel", claim, float(tp), detail=f"trace preservation fails by {tp:.3e}")
    return verified("check_channel", claim, f"Choi min eigenvalue {mn:.2e} >= 0 and Tr_out J = I (err {tp:.1e})")


def lindbladian(H, Ls, rates, d: int):
    """Column-stacked superoperator of dX/dt = -i[H,X] + sum_k g_k (L X L^dag - 1/2 {L^dag L, X})."""
    I = np.eye(d)
    S = -1j * (np.kron(I, H) - np.kron(H.T, I))
    for g, L in zip(rates, Ls):
        LdL = dagger(L) @ L
        S = S + g * (np.kron(L.conj(), L) - 0.5 * np.kron(I, LdL) - 0.5 * np.kron(LdL.T, I))
    return S


def check_lindblad_generator(Lsup, d: int, tol: float = 1e-9) -> Result:
    """GKSL theorem: a hermiticity-preserving, trace-annihilating generator generates a CP semigroup
    iff its Choi matrix is positive semidefinite on the complement of the maximally entangled vector."""
    claim = "generator is of Lindblad (GKSL) form: e^{Lt} is CPTP for all t >= 0"
    def act(X):
        return (Lsup @ X.reshape(-1, order="F")).reshape(d, d, order="F")
    J = np.zeros((d * d, d * d), complex)
    for i in range(d):
        for j in range(d):
            E = np.zeros((d, d), complex); E[i, j] = 1
            J += np.kron(E, act(E))
    tr_ann = max(abs(np.trace(act(np.eye(d)[:, [i]] @ np.eye(d)[[j], :]))) for i in range(d) for j in range(d))
    if tr_ann > tol:
        return refuted("check_lindblad_generator", claim, float(tr_ann), detail="generator does not annihilate the trace")
    omega = np.eye(d).reshape(-1) / np.sqrt(d)
    P = np.eye(d * d) - np.outer(omega, omega)
    # restrict J to the orthogonal complement of omega (P J P would add a spurious 0 eigenvalue)
    w, V = np.linalg.eigh(P)
    B = V[:, w > 0.5]
    mn = np.linalg.eigvalsh(B.conj().T @ J @ B).min()
    if mn < -tol:
        return refuted("check_lindblad_generator", claim, float(mn),
                       detail=f"Choi matrix restricted to omega-perp has eigenvalue {mn:.3e} < 0: some rate is negative (not CP)")
    return verified("check_lindblad_generator", claim, f"Choi matrix on omega-perp is PSD (min eigenvalue {mn:.2e}), trace annihilated")


# --------------------------------------------------------------------------
# uncertainty, spectra, perturbation theory
# --------------------------------------------------------------------------
def robertson_schrodinger_slack(A, B, psi):
    psi = ket(psi)
    ev = lambda M: psi.conj() @ M @ psi
    vA = (ev(A @ A) - ev(A) ** 2).real
    vB = (ev(B @ B) - ev(B) ** 2).real
    cov = 0.5 * ev(A @ B + B @ A) - ev(A) * ev(B)
    c = ev(comm(A, B)) / 2j
    return vA * vB - (abs(cov) ** 2 + abs(c) ** 2)


def check_uncertainty(A, B, psi, claimed_bound: str = "robertson", tol: float = 1e-10) -> Result:
    """Var A Var B >= |<[A,B]>/2i|^2 (Robertson) or + |cov|^2 (Schrodinger) at the given state."""
    psi = ket(psi)
    ev = lambda M: psi.conj() @ M @ psi
    vA = (ev(A @ A) - ev(A) ** 2).real
    vB = (ev(B @ B) - ev(B) ** 2).real
    c = ev(comm(A, B)) / 2j
    cov = 0.5 * ev(anticomm(A, B)) - ev(A) * ev(B)
    rhs = abs(c) ** 2 + (abs(cov) ** 2 if claimed_bound == "schrodinger" else 0)
    claim = f"Var(A) Var(B) >= {claimed_bound} bound"
    if vA * vB < rhs - tol:
        return refuted("check_uncertainty", claim, {"VarA*VarB": vA * vB, "bound": rhs}, detail="inequality violated: A or B or psi is not valid (non-hermitian operator?)")
    return verified("check_uncertainty", claim, f"Var A Var B = {vA * vB:.6f} >= {rhs:.6f}")


def check_eigenvalues(H, claimed: Sequence[float], tol: float = 1e-8) -> Result:
    """Spectrum of a hermitian matrix against a claimed list (LAPACK, tolerance 1e-8)."""
    w = np.linalg.eigvalsh((H + dagger(H)) / 2)
    c = np.sort(np.asarray(claimed, dtype=float))
    claim = f"spectrum = {[round(float(x), 6) for x in c]}"
    if len(w) != len(c):
        return refuted("check_eigenvalues", claim, {"computed": np.round(w, 8).tolist()}, detail=f"{len(w)} eigenvalues, claimed {len(c)}")
    if np.abs(w - c).max() > tol:
        return refuted("check_eigenvalues", claim, {"computed": np.round(w, 8).tolist()})
    return verified("check_eigenvalues", claim, f"max deviation {np.abs(w - c).max():.1e} (LAPACK, hermitian)")


def perturbation_series(H0, V, n: int):
    """(E0, E1, E2) for a NON-degenerate level n of H0 + lam V: E1 = V_nn, E2 = sum_{m!=n} |V_mn|^2/(E_n - E_m)."""
    E, U = np.linalg.eigh(H0)
    Vm = dagger(U) @ V @ U
    E1 = Vm[n, n].real
    E2 = sum(abs(Vm[m, n]) ** 2 / (E[n] - E[m]) for m in range(len(E)) if m != n)
    return float(E[n]), float(E1), float(E2)


def check_perturbative_shift(H0, V, n: int, claimed_E1=None, claimed_E2=None, tol: float = 1e-6) -> Result:
    """Compare claimed 1st/2nd order shifts with the formula AND with exact diagonalisation at small lambda."""
    E0, E1, E2 = perturbation_series(H0, V, n)
    E = np.linalg.eigvalsh(H0)
    gap = np.min(np.abs(np.delete(E, n) - E[n]))
    claim = f"E_n(lam) = {E0:.6g} + lam*{claimed_E1 if claimed_E1 is not None else E1:.6g} + lam^2*{claimed_E2 if claimed_E2 is not None else E2:.6g}"
    if gap < 1e-9:
        return inconclusive("check_perturbative_shift", claim, "level n is degenerate: non-degenerate perturbation theory does not apply")
    for lam in (1e-3, 2e-3):
        ex = np.linalg.eigvalsh(H0 + lam * V)
        k = int(np.argmin(np.abs(ex - E0 - lam * E1)))
        series = E0 + lam * E1 + lam ** 2 * E2
        if abs(ex[k] - series) > 50 * lam ** 3 * (1 + abs(E2)):
            return refuted("check_perturbative_shift", claim, {"lambda": lam, "exact": float(ex[k]), "series": series}, detail="formula disagrees with exact diagonalisation")
    if claimed_E1 is not None and abs(claimed_E1 - E1) > tol:
        return refuted("check_perturbative_shift", claim, {"true_E1": E1})
    if claimed_E2 is not None and abs(claimed_E2 - E2) > tol:
        return refuted("check_perturbative_shift", claim, {"true_E2": E2})
    return verified("check_perturbative_shift", claim, "matches formula and exact diagonalisation at lambda=1e-3,2e-3", E1=E1, E2=E2)


def check_trace_obstruction(n: int, hbar: float = 1.0) -> Result:
    """[X,P] = i hbar I has no solution with n x n matrices: Tr[X,P] = 0 but Tr(i hbar I) = i hbar n != 0."""
    return refuted("check_trace_obstruction", f"[X,P] = i hbar I realised by {n}x{n} matrices", {"Tr[X,P]": 0, "Tr(i hbar I)": f"{n}i*hbar"},
                   detail="trace of a commutator is always 0 in finite dimension; canonical commutation needs infinite dimension (Wintner)",
                   evidence="exact trace identity")


# --------------------------------------------------------------------------
# counterexample search over states
# --------------------------------------------------------------------------
def structured_states(dims: Sequence[int]):
    """Named states on a multipartite system: product, Bell/GHZ/W when dims are qubits, diagonal and rank-deficient."""
    D = int(np.prod(dims))
    out = {}
    for k in range(min(D, 4)):
        e = np.zeros(D, complex); e[k] = 1
        out[f"basis|{k}>"] = dm(e)
    out["maximally mixed"] = np.eye(D, dtype=complex) / D
    if all(d == dims[0] for d in dims):
        d, n = dims[0], len(dims)
        ghz = np.zeros(D, complex)
        for k in range(d):
            ghz[sum(k * d ** i for i in range(n))] = 1
        out["GHZ/Bell"] = dm(ghz)
        if d == 2:
            w = np.zeros(D, complex)
            for i in range(n):
                w[1 << i] = 1
            out["W"] = dm(w)
            psi_m = np.zeros(D, complex)
            psi_m[1] = 1; psi_m[2 if D > 2 else 1] += -1
            out["singlet-like"] = dm(psi_m) if np.linalg.norm(psi_m) > 0 else out["maximally mixed"]
    return out


def random_states(dims: Sequence[int], n: int, seed: int = 0):
    rng = np.random.default_rng(seed)
    D = int(np.prod(dims))
    for _ in range(n):
        rank = int(rng.integers(1, D + 1))
        G = rng.normal(size=(D, rank)) + 1j * rng.normal(size=(D, rank))
        r = G @ dagger(G)
        yield r / np.trace(r).real


def hunt_state_counterexample(f: Callable, dims: Sequence[int], claim: str = "f(rho) >= 0 for all states", n: int = 1500,
                              tol: float = 1e-9, seed: int = 0) -> Result:
    """Claim: f(rho) >= 0 for every density matrix on `dims`. Searches structured + random states (+ pure states).
    A witness (printed with its f value) REFUTES; no witness gives CONSISTENT only."""
    cases = list(structured_states(dims).items())
    cases += [(f"random#{i}", r) for i, r in enumerate(random_states(dims, n, seed))]
    D = int(np.prod(dims))
    rng = np.random.default_rng(seed + 1)
    for i in range(n // 3):
        v = rng.normal(size=D) + 1j * rng.normal(size=D)
        cases.append((f"pure#{i}", dm(v)))
    worst, worst_name = np.inf, ""
    for name, rho in cases:
        try:
            val = float(np.real(f(rho)))
        except Exception as e:
            return inconclusive("hunt_state_counterexample", claim, f"f raised {type(e).__name__} on {name}: {e}")
        if not np.isfinite(val):
            return inconclusive("hunt_state_counterexample", claim, f"f returned {val} on {name}: cannot compare")
        if val < worst:
            worst, worst_name = val, name
        if val < -tol:
            return refuted("hunt_state_counterexample", claim, {"state": name, "f": val, "rho": np.round(rho, 4).tolist() if D <= 4 else name})
    return consistent("hunt_state_counterexample", claim, f"{len(cases)} states (structured + random + pure); min f = {worst:.3e} at {worst_name}",
                      caveat="Random search; a universal quantum-information inequality is not proven by it.")


def entropy_inequalities(rho, dims=(2, 2, 2)) -> dict:
    """Slacks (all must be >= 0): subadditivity, Araki-Lieb, and for 3 parties strong subadditivity."""
    S = von_neumann_entropy
    out = {}
    n = len(dims)
    if n >= 2:
        A, B = ptrace(rho, dims, [0]), ptrace(rho, dims, [1])
        AB = ptrace(rho, dims, [0, 1])
        out["subadditivity S(A)+S(B)-S(AB)"] = S(A) + S(B) - S(AB)
        out["Araki-Lieb S(AB)-|S(A)-S(B)|"] = S(AB) - abs(S(A) - S(B))
    if n >= 3:
        AB, BC, Bm = ptrace(rho, dims, [0, 1]), ptrace(rho, dims, [1, 2]), ptrace(rho, dims, [1])
        out["strong subadditivity S(AB)+S(BC)-S(ABC)-S(B)"] = S(AB) + S(BC) - S(rho) - S(Bm)
    return out
