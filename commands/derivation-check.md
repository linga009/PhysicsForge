---
name: derivation-check
description: Verify a specific derivation's dimensional consistency and limiting cases using the real deriv_check.py checks, not self-reported PASS/FAIL
argumentHint: [the equation or claim to verify]
---

The user wants a specific derivation or formula verified: `$ARGUMENTS`.

`scripts/deriv_check.py` is a library, not a CLI — the pattern is to import its
two functions and write a short script for *this specific claim*, the same way
`scripts/test_deriv_check.py` does for this project's own manuscript claims.
Do not just assert "Dimensions: PASS" from inspection; run the check.

1. Read `skills/physicsforge/references/verification.md`, especially the
   "PREFER THE REAL TESTED TOOLS" section, before writing new verification
   code.
2. Identify what's actually checkable here:
   - **Dimensional consistency**: express both sides as `sympy.physics.units`
     `Dimension` objects and call
     `check_dimensions(lhs_dim, rhs_dim)` from `scripts/deriv_check.py`.
   - **Limiting case / known-value reduction**: substitute the limit into the
     expression and call `check_limit(expr, subs, expected)` — prefer the
     `symbolic_target=` form (exact symbolic reduction) over a bare numeric
     `expected` where possible; a single numeric match is weaker evidence than
     an exact symbolic one.
3. Write and run a short Python script (in the project directory, not inline
   prose) that does this for the actual expression at hand:
   ```python
   import sys; sys.path.insert(0, "${CLAUDE_PLUGIN_ROOT}/scripts")
   from deriv_check import check_dimensions, check_limit, report
   # ... build lhs_dim/rhs_dim or expr/subs/expected for THIS claim ...
   ```
4. Report the result with `deriv_check.py`'s own `report()` formatting (PASS/FAIL
   per check, OVERALL verdict) — don't paraphrase a failure as a pass.
5. If the check fails, don't hand-wave it: identify whether it's an algebraic
   error, a sign error, a dimensional error, or a convention mismatch (see
   `verification.md`'s "INTERPRETING FAILURES"), and say which.

If the claim involves a tensor/metric derivation (GR-like), follow the pattern
in `scripts/test_kerr_check.py` instead — deriving from the actual library
representation (e.g. EinsteinPy) rather than checking against a textbook
formula alone, and cross-checking any `sympy.simplify(...) == 0` result
numerically before trusting it.
