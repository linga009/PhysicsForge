---
name: quantum-check
description: Check a quantum-mechanics or quantum-information claim with pfv.quantum — states, channels, entanglement, spectra, uncertainty, inequalities over all states
argumentHint: [the operator, state, channel or quantum claim to verify]
---

The user wants a quantum claim checked: `$ARGUMENTS`.

Use `scripts/pfv/quantum.py` (finite dimension, hbar = 1). Read the quantum rows of
`skills/physicsforge/references/verification-tools.md` first.

1. Pick the check:
   - one explicit object: `check_hermitian`, `check_unitary`, `check_density_matrix`,
     `check_channel` (CPTP via the Choi matrix; pass Kraus operators or a map),
     `check_lindblad_generator`, `check_entangled` (PPT test),
     `check_entanglement_entropy` (bits, for a pure bipartite state),
     `check_eigenvalues`, `check_uncertainty`, `check_perturbative_shift`
   - an algebra: `check_angular_momentum_algebra`, `check_pauli_algebra`
   - a claim about ALL states ("this entropy inequality always holds"):
     `hunt_state_counterexample`. It can refute; a pass is only CONSISTENT. It mixes
     structured states (product, Bell, GHZ, W, rank-deficient) into the random ones,
     because random states alone rarely find counterexamples.
2. Build the numpy arrays for this claim and run a short script:
   ```python
   import sys; sys.path.insert(0, "${CLAUDE_PLUGIN_ROOT}/scripts")
   import numpy as np
   from pfv import quantum as qm
   from pfv.core import report
   print(report([...], "the claim"))
   ```
3. These are floating-point checks of one explicit object, decided at the stated
   tolerance with the margin shown in `evidence`. Report them as numerical results about
   that object, not as theorems about a family of systems.
4. Be explicit about what the evidence is. A check against a textbook fact (the Tsirelson
   bound, a Bell state's 1 bit) is calibration, not validation of the user's claim.

If the claim is infinite-dimensional or purely analytic, say so instead of forcing it into
a finite numerical check that does not test the statement.
