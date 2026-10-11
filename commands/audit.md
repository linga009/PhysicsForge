---
name: audit
description: Full audit of an uploaded physics/math paper — Pauli Protocol, anti-fabrication checks, ScholarEval scoring, and citation verification
argumentHint: [path to paper (PDF/LaTeX/text)]
---

The user wants a full audit of an uploaded or referenced research paper.

Follow the PhysicsForge skill's audit workflow:

1. Read `skills/physicsforge/references/paper-analysis.md` for the audit
   procedure, `anti-fabrication.md` for the failure modes to check for, and
   `scholar-eval.md` for the 8-dimension quantitative scoring rubric. If the
   claimed result looks extraordinary (revolutionary, "solves" a famous
   problem, defies a well-established bound), also read
   `breakthrough-red-flags.md` and `extraordinary-claims.md` before engaging
   technically.
2. Identify the paper (ask for a file path or arXiv/DOI if not given as
   `$ARGUMENTS`).
3. Run the Pauli Protocol and the Anti-Fabrication Check on the paper's central
   claims, printing both inline per `SKILL.md`'s required output format.
4. Verify every citation in the bibliography with the real tool — extract
   DOIs/arXiv IDs into a `.jsonl` file and run:
   `python ${CLAUDE_PLUGIN_ROOT}/scripts/citation_guard.py check <file>.jsonl --fail-on retracted`
   Report the PASS/HOLD/FAIL verdict from `citation-guard.md`'s thresholds, not
   just a prose impression.
5. Where the paper makes a checkable symbolic/numeric derivation claim, verify
   it directly rather than taking the paper's word for it — follow the pattern
   in `scripts/test_kerr_check.py` (derive from first principles, cross-check
   with numeric substitution, don't trust `sympy.simplify(...) == 0` alone).
6. Score the paper with ScholarEval's 8 dimensions and produce the full audit
   report per `paper-analysis.md`'s output format, including an explicit
   deliverability verdict.

Never claim a citation or derivation was verified without having actually run
the check. If a tool can't reach the network or a file is missing, say so
explicitly rather than presenting an unverified claim as verified.
