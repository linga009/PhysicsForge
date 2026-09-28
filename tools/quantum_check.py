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
    print("quantum_check.py is a library. Run: python test_quantum_check.py")
    print("for its calibration suite against canonical QM/QI facts.")
