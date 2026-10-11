---
name: verify
description: Try to disprove, then prove, a mathematical or physical claim with the pfv toolkit (16 domains, four honest verdicts)
argumentHint: [the claim, identity, inequality, derivation step or calculation to check]
---

The user wants a claim checked: `$ARGUMENTS`.

Read `skills/physicsforge/references/verification-tools.md` first. It maps each kind of
question to the `pfv` check that answers it, and states the verdict rules.

1. **State the claim precisely** as the statement being checked, including the domain
   (all integers? all reals with a > 0? one explicit matrix?). Say what would falsify it.
2. **Refute first.** Run the cheapest counterexample hunt that fits:
   `numtheory.find_counterexample`, a `hunt_*` function, or a `check_*` on a small case.
   One REFUTED settles it. Surviving a hunt proves nothing.
3. **Then try to prove it** with a check that can return VERIFIED: an exact symbolic
   identity (`analysis.check_identity`), an exhaustive finite check (`groups.*`), or a
   decision procedure (`smt.check_real_claim` for polynomial inequalities).
4. Write and run a short script, for example:
   ```python
   import sys; sys.path.insert(0, "${CLAUDE_PLUGIN_ROOT}/scripts")
   from pfv import numtheory, analysis, smt
   from pfv.core import report
   results = [...]
   print(report(results, "the claim"))
   ```
   Pass exact values as strings (`"1/3"`), `Fraction` or sympy `Rational` when the claim
   is exact. A float is read exactly as written, and float input reaches CONSISTENT at most.
5. Paste the `report(...)` block verbatim, including its "Not proven:" line, then map the
   overall verdict to the claim hierarchy:
   - **VERIFIED**: supports Theorem/Proposition for exactly the statement checked.
     Confirm that it is the statement the user meant.
   - **CONSISTENT**: Observation or `[NUMERICAL]` only, never "Theorem".
   - **INCONCLUSIVE**: say so and say why; do not guess a verdict.
   - **REFUTED**: show the witness; the claim must be fixed or dropped.

If `python -m pfv list <domain>` (run from `scripts/`) has no check for the question, fall
back to the sympy patterns in `verification.md` and say that no tested check covered it.
If code cannot run at all, say so rather than reporting a verdict.
