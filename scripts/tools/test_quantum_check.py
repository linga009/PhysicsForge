"""Regression suite for quantum_check.py, calibrated against canonical,
textbook-established QM/QI facts (no quantum-information paper exists yet in
this project to validate against -- see quantum_check.py's own docstring for
why that distinction, calibration vs. validation, is kept visible rather than
blurred). Zero test-framework dependency, matching test_retry.py's pattern.

As in test_deriv_check.py: the depolarizing-channel-missing-a-term case is a
deliberately WRONG input, included to confirm the checker can actually fail,
not rubber-stamp everything. The passing test there is "the tool correctly
says NOT CPTP", a meta-level assertion about the tool, kept explicit rather
than conflated with a physics claim.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np  # noqa: E402
import qutip as qt  # noqa: E402
from quantum_check import check_cptp, chsh_value, entanglement_entropy  # noqa: E402

FAILURES = []


def check(name: str, cond: bool, detail: str = ""):
    mark = "PASS" if cond else "FAIL"
    print(f"[{mark}] {name}")
    if not cond and detail:
        print(f"      {detail}")
    if not cond:
        FAILURES.append(name)


def test_chsh_tsirelson_bound():
    """The singlet state at standard CHSH angles must violate the classical
    bound |S|<=2 and saturate Tsirelson's bound 2*sqrt(2), the textbook
    quantum-mechanical maximum."""
    singlet = (qt.tensor(qt.basis(2, 0), qt.basis(2, 1)) -
               qt.tensor(qt.basis(2, 1), qt.basis(2, 0))).unit()

    def spin_op(theta):
        return np.cos(theta) * qt.sigmaz() + np.sin(theta) * qt.sigmax()

    a, ap = spin_op(0), spin_op(np.pi / 2)
    b, bp = spin_op(np.pi / 4), spin_op(-np.pi / 4)
    S = chsh_value(singlet, a, ap, b, bp)
    target = 2 * np.sqrt(2)
    check("|S| == 2*sqrt(2) (Tsirelson's bound) at standard CHSH angles",
          abs(abs(S) - target) < 1e-6, f"S={S:.6f}, target={target:.6f}")
    check("|S| > 2 (violates the classical/local-hidden-variable bound)",
          abs(S) > 2 + 1e-9, f"|S|={abs(S):.6f}")


def test_bell_state_entanglement_entropy():
    """Von Neumann entropy of a reduced Bell state is exactly 1 bit
    (log base 2), the textbook maximally-entangled value."""
    bell = (qt.tensor(qt.basis(2, 0), qt.basis(2, 0)) +
            qt.tensor(qt.basis(2, 1), qt.basis(2, 1))).unit()
    S_ent = entanglement_entropy(bell, [0])
    check("von Neumann entropy of reduced Bell state == 1 bit",
          abs(S_ent - 1.0) < 1e-9, f"S_vN={S_ent:.9f}")


def _depolarizing_kraus(p: float):
    K0 = np.sqrt(1 - 3 * p / 4) * qt.qeye(2)
    K1 = np.sqrt(p / 4) * qt.sigmax()
    K2 = np.sqrt(p / 4) * qt.sigmay()
    K3 = np.sqrt(p / 4) * qt.sigmaz()
    return K0, K1, K2, K3


def test_depolarizing_channel_is_cptp():
    """The complete two-qubit depolarizing-channel Kraus set
    {sqrt(1-3p/4) I, sqrt(p/4) X, sqrt(p/4) Y, sqrt(p/4) Z} must be CPTP
    (sum K^dag K == I) for a physical p in [0,1]."""
    K0, K1, K2, K3 = _depolarizing_kraus(0.3)
    ok, detail = check_cptp([K0, K1, K2, K3])
    check("complete depolarizing Kraus set is trace-preserving (CPTP)", ok, detail)


def test_incomplete_kraus_set_correctly_rejected():
    """Meta-level assertion: an incomplete Kraus set (missing the Y term) is
    NOT trace-preserving, and check_cptp must correctly say so. The passing
    test here is that the tool returns NOT ok -- this input is deliberately
    unphysical, included to confirm the checker can fail, not rubber-stamp."""
    p = 0.3
    K0, K1, K2, K3 = _depolarizing_kraus(p)
    ok, detail = check_cptp([K0, K1, K3])  # K2 (the Y term) deliberately omitted
    check("tool correctly rejects the incomplete (non-CPTP) Kraus set", not ok, detail)

    # The missing term's own weight, computed independently (not by parsing
    # check_cptp's human-readable string -- that would be a brittle test):
    # sum K^dag K without K2 is short by exactly K2^dag K2 = (p/4) I_d, and
    # QuTiP's Qobj.norm() defaults to trace norm, so the deviation is
    # (p/4) * d for a d-dimensional identity, not (p/4) alone -- confirmed
    # empirically (got deviation=0.15 = 2*0.075 for d=2) rather than assumed.
    dim = K0.dims[0][0]
    missing_weight = qt.expect(K2.dag() * K2, qt.basis(2, 0))
    total = sum((k.dag() * k for k in (K0, K1, K3)),
                qt.Qobj(np.zeros(K0.shape), dims=K0.dims))
    actual_deviation = (total - qt.qeye(dim)).norm()
    check("...and the deviation (trace norm) matches dim * the missing term's weight",
          abs(actual_deviation - dim * missing_weight) < 1e-9,
          f"deviation={actual_deviation:.6f}, dim*missing_weight={dim*missing_weight:.6f}")


if __name__ == "__main__":
    test_chsh_tsirelson_bound()
    test_bell_state_entanglement_entropy()
    test_depolarizing_channel_is_cptp()
    test_incomplete_kraus_set_correctly_rejected()

    print()
    if FAILURES:
        print(f"RESULT: FAIL ({len(FAILURES)} failed: {', '.join(FAILURES)})")
        raise SystemExit(1)
    print("RESULT: PASS (all quantum checks behaved correctly)")
