"""PhysicsForge Quantum Verification -- real QuTiP-backed checks for claims
about unitarity, complete positivity, and entanglement measures.

No quantum-information paper exists yet in this project to validate against,
so this is validated against canonical, textbook-established facts instead --
the CHSH bound, Bell-state entanglement entropy, and the depolarizing
channel's CPTP property. These are "real data" in the sense that matters here
(independently, externally established results the field itself calibrates
against), not fabricated toy numbers -- but this is calibration, not
validation against our own messy data, and that distinction should stay
visible rather than be blurred into "validated."

Requires: pip install qutip
"""

from __future__ import annotations

import numpy as np
import qutip as qt


def check_unitary(op: qt.Qobj, tol: float = 1e-9) -> tuple[bool, str]:
    ok = op.check_isunitary() if hasattr(op, "check_isunitary") else \
        (op * op.dag() - qt.qeye(op.dims[0])).norm() < tol
    return bool(ok), f"U U^dagger == I within {tol}: {ok}"


def check_cptp(kraus_ops: list[qt.Qobj], tol: float = 1e-9) -> tuple[bool, str]:
    """Trace-preserving check: sum_k K_k^dagger K_k == I."""
    dim = kraus_ops[0].dims[0]
    total = sum((k.dag() * k for k in kraus_ops), qt.Qobj(np.zeros(kraus_ops[0].shape),
                                                            dims=kraus_ops[0].dims))
    ident = qt.qeye(dim)
    diff = (total - ident).norm()
    ok = diff < tol
    return ok, f"||sum K_k^dag K_k - I|| = {diff:.3e} (tol {tol})"


def chsh_value(state: qt.Qobj, a: qt.Qobj, ap: qt.Qobj, b: qt.Qobj, bp: qt.Qobj) -> float:
    """Standard CHSH combination S = <ab> + <ab'> + <a'b> - <a'b'>."""
    def corr(A, B):
        return qt.expect(qt.tensor(A, B), state)
    return corr(a, b) + corr(a, bp) + corr(ap, b) - corr(ap, bp)


def entanglement_entropy(state: qt.Qobj, subsys: list[int]) -> float:
    rho_A = state.ptrace(subsys)
    return qt.entropy_vn(rho_A, base=2)


def report(name: str, checks: list[tuple[str, bool, str]]) -> str:
    lines = [f"=========== QUANTUM CHECK: {name} ==========="]
    all_ok = True
    for label, ok, detail in checks:
        mark = "PASS" if ok else "FAIL"
        all_ok &= ok
        lines.append(f"[{mark}] {label}")
        lines.append(f"        {detail}")
    lines.append(f"OVERALL: {'PASS' if all_ok else 'FAIL'}")
    lines.append("=" * len(lines[0]))
    return "\n".join(lines)


if __name__ == "__main__":
    checks = []

    print("### Calibration 1: CHSH bound. Quantum mechanics permits violating the")
    print("### classical bound |S|<=2, up to Tsirelson's bound 2*sqrt(2) ~= 2.828,")
    print("### using the singlet state and the standard CHSH measurement angles.")
    singlet = (qt.tensor(qt.basis(2, 0), qt.basis(2, 1)) -
               qt.tensor(qt.basis(2, 1), qt.basis(2, 0))).unit()

    def spin_op(theta):
        return np.cos(theta) * qt.sigmaz() + np.sin(theta) * qt.sigmax()

    a, ap = spin_op(0), spin_op(np.pi / 2)
    b, bp = spin_op(np.pi / 4), spin_op(-np.pi / 4)
    S = chsh_value(singlet, a, ap, b, bp)
    target = 2 * np.sqrt(2)
    ok = abs(abs(S) - target) < 1e-6
    checks.append((f"|S| == 2*sqrt(2) (Tsirelson's bound) for the singlet at standard angles",
                    ok, f"computed S = {S:.6f}, |S| = {abs(S):.6f}, target = {target:.6f}"))
    ok2 = abs(S) > 2 + 1e-9
    checks.append(("|S| > 2 (violates the classical/local-hidden-variable bound)",
                    ok2, f"|S| = {abs(S):.6f} > 2: {ok2}"))

    print()
    print("### Calibration 2: entanglement entropy of a Bell state is exactly ln(2)")
    print("### bits (S_vN = 1 bit with base-2 log), the textbook maximally-entangled value.")
    bell = (qt.tensor(qt.basis(2, 0), qt.basis(2, 0)) +
            qt.tensor(qt.basis(2, 1), qt.basis(2, 1))).unit()
    S_ent = entanglement_entropy(bell, [0])
    ok3 = abs(S_ent - 1.0) < 1e-9
    checks.append(("von Neumann entropy of reduced Bell state == 1 bit",
                    ok3, f"S_vN = {S_ent:.9f}"))

    print()
    print("### Calibration 3: the two-qubit depolarizing channel's Kraus operators")
    print("### {sqrt(1-3p/4) I, sqrt(p/4) X, sqrt(p/4) Y, sqrt(p/4) Z} must be CPTP")
    print("### (sum K^dag K == I) for any physical value of p in [0,1].")
    p = 0.3
    K0 = np.sqrt(1 - 3 * p / 4) * qt.qeye(2)
    K1 = np.sqrt(p / 4) * qt.sigmax()
    K2 = np.sqrt(p / 4) * qt.sigmay()
    K3 = np.sqrt(p / 4) * qt.sigmaz()
    ok4, detail4 = check_cptp([K0, K1, K2, K3])
    checks.append(("depolarizing-channel Kraus set is trace-preserving (CPTP)", ok4, detail4))

    print()
    print("### Calibration 4 -- DELIBERATELY WRONG, to confirm this can actually")
    print("### fail: an incomplete Kraus set missing the Y term is NOT trace-preserving.")
    ok5, detail5 = check_cptp([K0, K1, K3])
    checks.append(("(WRONG, expected FAIL) {K0,K1,K3} without K_Y is still CPTP", ok5, detail5))

    print()
    print(report("QuTiP calibration against canonical QM/QI facts", checks))
