---
name: derivation-check
description: Check a derivation step by step with pfv — dimensions, limiting cases, each identity used, and the first wrong step in a chain
argumentHint: [the derivation, equation or chain of steps to verify]
---

The user wants a derivation or formula verified: `$ARGUMENTS`.

Use `scripts/pfv`. Read `skills/physicsforge/references/verification-tools.md` for the
check menu and verdict rules. Do not assert "Dimensions: PASS" from inspection: run it.

1. **Dimensions.** Give each symbol a `pfv.dimensions.Dim` (base names `M L T I Th N J`) and
   call `dimensions.check_dimensions(lhs, rhs, table)`. It also checks that every internal
   sum is homogeneous and that arguments of `exp`/`log`/`sin` are dimensionless.
2. **Each step of the chain.** For a sequence of equal expressions use
   `derivation.check_chain([...])`; for equation-solving steps use
   `derivation.check_equation_chain`. Both report the first step that is not valid, and
   flag lost or extraneous roots (`check_candidates`).
3. **Identities used along the way:** `analysis.check_identity(lhs, rhs)`. It is exact
   when sympy can decide, and otherwise CONSISTENT on sample points, never a silent pass.
4. **Limiting cases:** `analysis.check_limit(expr, var, point, claimed)` for each limit
   the result must recover. Use at least two independent ones.
5. Run it as a short script:
   ```python
   import sys; sys.path.insert(0, "${CLAUDE_PLUGIN_ROOT}/scripts")
   from pfv import dimensions, derivation, analysis
   from pfv.core import report
   print(report([...], "the derivation"))
   ```
6. Paste the report verbatim. If a check fails, name the failure type (algebra, sign,
   dimensions, convention, or a genuinely false claim) and the step where it happens.

For tensor and metric derivations (GR), use `pfv.geometry` and follow the pattern in
`scripts/test_kerr_check.py`. Derive from the library's own objects, use the library's own
symbols (`kerr.symbols()`), and cross-check any `simplify(...) == 0` numerically.
