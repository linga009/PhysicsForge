---
name: gap-analysis
description: Run the 8-phase systematic gap analysis on a physics/math topic to find tractable, actionable research directions
argumentHint: [topic or subfield]
---

The user wants to find gaps or open problems in a physics or mathematics topic:
`$ARGUMENTS`.

Follow the PhysicsForge skill's gap-analysis workflow:

1. Read `skills/physicsforge/references/gap-analysis.md` for the full 8-phase
   protocol and `deep-search.md` for the literature reconnaissance step that
   feeds it.
2. Run Phase 1 (multi-database literature reconnaissance) first — don't
   skip straight to guessing gaps. Search broadly before narrowing.
3. Work through all 8 phases in order:
   1. Foundation Mapping — THEOREM vs CONJECTURE vs ASSUMPTION
   2. Analogue Survey — solved elsewhere, not applied here
   3. Mathematical Completeness — existence/uniqueness/convergence gaps
   4. Experimental Status — predictions vs measurements
   5. Cross-Disciplinary Tools — unimported methods from other fields
   6. Citation Desert Map — subtopics that went quiet, with diagnosis
   7. Contradiction Registry — conflicting results in the literature
   8. Tractability Ranking — top 5 actionable directions
4. If the topic borders a Clay/Millennium-class problem (Navier-Stokes
   regularity, P vs NP, Riemann Hypothesis, Yang-Mills mass gap, BSD, Hodge,
   quantum gravity, hierarchy problem, cosmological constant, measurement
   problem), read `SKILL.md`'s MILLENNIUM-CLASS PROBLEM PROTOCOL before
   presenting any proposed direction as more than a partial advance.
5. Present the final tractability ranking with, for each candidate direction,
   what's actually missing and why it's tractable now (not just "hasn't been
   tried").

Every claim about what is/isn't established in the literature must trace to an
actual source — don't assert a gap exists without having searched for it.
