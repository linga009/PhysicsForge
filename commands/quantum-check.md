---
name: quantum-check
description: Verify a quantum-information/mechanics claim (unitarity, CPTP, CHSH, entanglement entropy) using the real QuTiP-backed quantum_check.py
argumentHint: [the operator, channel, or state claim to verify]
---

The user wants a quantum mechanics / quantum information claim verified:
`$ARGUMENTS`.

`scripts/quantum_check.py` is a library of real QuTiP-backed checks, not a CLI —
import what's needed for the specific claim, the way
`scripts/test_quantum_check.py` does against canonical QM/QI facts (the CHSH
bound, Bell-state entanglement entropy, the depolarizing channel's CPTP
property).

1. Identify which check applies:
   - **Unitarity** of an operator → `check_unitary(op, tol=1e-9)`
   - **Complete positivity / trace preservation** of a quantum channel given as
     Kraus operators → `check_cptp(kraus_ops, tol=1e-9)`
   - **Bell-inequality violation** → `chsh_value(state, a, ap, b, bp)` against
     the classical bound of 2 and Tsirelson's bound of 2√2
   - **Entanglement entropy** of a bipartite state → `entanglement_entropy(state, subsys)`
2. Write and run a short script building the actual `qutip.Qobj` operators/state
   for this claim, e.g.:
   ```python
   import sys; sys.path.insert(0, "${CLAUDE_PLUGIN_ROOT}/scripts")
   from quantum_check import check_unitary, check_cptp, chsh_value, entanglement_entropy, report
   ```
3. Report using `quantum_check.py`'s own `report()` formatting.
4. Be explicit about what kind of evidence this is: if no paper/claim in this
   project is being checked and you're instead calibrating against a textbook
   fact (as `test_quantum_check.py` does — there being no QI paper yet in this
   project to validate against), say so. That is calibration against an
   externally-established result, not validation of a user-supplied claim —
   keep that distinction visible rather than blurring it into "validated."

If the claim is about something QuTiP cannot directly represent (e.g. an
infinite-dimensional claim, or a purely analytic bound), say so rather than
forcing it into a finite-dimensional numerical check that doesn't actually test
the claim.
