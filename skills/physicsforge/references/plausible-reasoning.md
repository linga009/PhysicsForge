# PhysicsForge — Plausible Reasoning for Conjectures

A framework for *how confident to be* in an unproven conjecture, and why — used
while a claim is still being formed, before it is presented. This sits between
the Discovery Engine (`discovery.md`, which generates candidate conjectures) and
the Claim Hierarchy (`SKILL.md`, which categorically labels the result once
you've decided how to present it).

---

## WHY THIS IS A SEPARATE FILE FROM THE CLAIM HIERARCHY

The Claim Hierarchy in `SKILL.md` is **categorical**: a statement is a Theorem,
Proposition, Conjecture, or Heuristic. That labelling is a hard rule and this
file does not weaken it — a Conjecture is never presented as a Theorem, however
plausible it seems.

But "Conjecture" covers an enormous range of actual confidence, from "checked in
one special case, might well be a coincidence" to "verified independently three
different ways, survived an adversarial attempt to break it, and every known
special case confirms it." The Claim Hierarchy has no vocabulary for that
difference. George Pólya's *Mathematics and Plausible Reasoning* (Princeton
University Press, 1954, two volumes: *Induction and Analogy in Mathematics* and
*Patterns of Plausible Inference*) is specifically about how mathematicians
reason about that gradation *before* they have a proof — not as a substitute for
proof, but as an honest account of how research actually proceeds while a
question is still open. His earlier *How to Solve It* (1945) frames the same
four-phase arc this skill already uses operationally: understand → plan →
execute → **look back** — and "look back" is exactly what the Pauli Protocol and
self-audit already do. This file gives that closing phase, applied specifically
to conjectures, a more structured vocabulary.

---

## PÓLYA'S PATTERNS, ADAPTED TO PHYSICS

### Pattern 1 — Unexpected confirmation counts more than expected confirmation
If a conjecture correctly predicts something you were *not* specifically trying
to reproduce, that is much stronger evidence than a limiting case you built the
derivation to hit. This directly sharpens a concern already in
`anti-fabrication.md`: a limit that "comes out automatically" is flagged there
as a possible trivial reduction precisely because expected confirmations are
weak evidence — Pólya gives the positive version of the same insight. When
logging a limiting-case check, note whether the match was designed-in
(expected) or a genuine surprise (unexpected) — they should not be weighted the
same way when you decide how confident to be.

### Pattern 2 — A special/symmetric case is weaker evidence than a generic case
A formula that checks out at a highly symmetric or special point may be
correct there for reasons specific to that symmetry — extra cancellations that
don't occur generically. Verifying at a "typical," unremarkable point in
parameter space is stronger evidence than verifying at the point with the most
extra structure.

### Pattern 3 — Independent routes compound; repeating one route doesn't
Two structurally unrelated derivations (say, a variational argument and a
perturbative expansion) landing on the same conjecture is strong evidence.
Checking the same derivation twice, or rephrasing the same argument, is not a
second piece of evidence — it's the first piece checked again. When logging
support for a conjecture, tag each piece of evidence with which *route* it came
from, and count distinct routes, not distinct sentences.

### Pattern 4 — Analogy strength tracks shared structure, not shared notation
An analogy to a solved problem is strong evidence only to the extent that the
*assumptions* which made the original problem solvable actually hold here, not
merely that the equations look similar. This is the constructive side of
`anti-fabrication.md` Mode 3 (Wrong-System Formulas): that file flags analogy
misused to import a formula outright; this pattern is about grading how much
confidence an analogy should buy you even when it is used honestly, as a
heuristic rather than a substitute for derivation.

### Pattern 5 — A conjecture that survived an attack is stronger than one nobody tried to break
If the Devil's Advocate persona in `adversarial-review.md`, or a search for a
counterexample under `counterexample-protocol.md`, was genuinely attempted and
failed to break the conjecture, that failure to refute is itself evidence — much
stronger than a conjecture that has simply never been seriously challenged.

---

## A LIGHTWEIGHT PLAUSIBILITY NOTE

Attach this to any claim labelled Conjecture or Heuristic before presenting it.
It is deliberately not a numeric score — a fabricated-looking number (e.g.
"73% confident") would itself be exactly the kind of false precision this skill
exists to avoid. Confidence is reported qualitatively, tied explicitly to which
Pólya patterns are actually satisfied.

```
═══════════ PLAUSIBILITY NOTE ═══════════
Conjecture: <statement>

Evidence for it:
  [Pattern 1] Unexpected confirmations:  <list, or "none — only designed-in checks">
  [Pattern 2] Generic-point checks:      <list, or "only special/symmetric points checked">
  [Pattern 3] Independent routes:        <count of genuinely distinct routes, and what they are>
  [Pattern 4] Analogy basis:             <what structure is actually shared with the
                                           analogous solved problem, if any>
  [Pattern 5] Survived an attack:        <was a counterexample search genuinely
                                           attempted? by what method? result?>

CONFIDENCE: Low / Moderate / High
  Reasoning: <one or two sentences — which patterns above are doing the work>

This is NOT: a claim classification upgrade. The Claim Hierarchy label
(Conjecture / Heuristic) is unchanged regardless of confidence level.
══════════════════════════════════════════
```

**Worked micro-example.** Conjecture: "the weighted-mean bound
$1-f \ge \ln(\omega_{\log}/\omega_L)/\ln(\omega_{\max}/\omega_L)$ correctly
identifies which $\lambda$ rows are excluded for a hydrogen-free
phonon-superconductor candidate." Evidence: it is an *exact* inequality from the
definition of a weighted geometric mean (not empirical, so Patterns 1–3 don't
apply in the usual sense — this is closer to a Proposition than a Conjecture, and
should be labelled accordingly); the physical content — whether $\omega_{\max}$
for a real $\mathrm{LaMgC_2}$ crystal is really set by a C≡C-type dimer stretch —
is a genuine Conjecture, supported only by analogy to $\mathrm{CaC_2}$ (Pattern
4: the shared structure is "carbon dimer in a carbide-like lattice," which is a
real but not tight analogy — no DFT phonon calculation on the actual candidate
has been done). CONFIDENCE: Low, and the manuscript should say so, which is
exactly what the revised version does (`OPEN` tag on the compound-specific
assumption).

---

## INTEGRATION WITH OTHER PROTOCOLS

- **Claim Hierarchy (`SKILL.md`)**: unchanged and authoritative for the label.
  This file only adds texture to what "Conjecture" means in a given case.
- **`anti-fabrication.md`**: Pattern 1 sharpens the Trivial Reduction Test;
  Pattern 4 is the constructive complement to the Wrong-System-Formula failure
  mode.
- **`adversarial-review.md`** and **`counterexample-protocol.md`**: Pattern 5's
  evidence comes directly from those protocols having been actually run, not
  merely available.
- **`formula-prediction.md`**: Stage 4 (Literature Analogy) should report which
  Pólya pattern its analogy evidence corresponds to, rather than treating "found
  a similar equation in the literature" as uniformly strong support.
- **`scholar-eval.md`**: when auditing someone else's conjecture, check whether
  *they* distinguish expected from unexpected confirmations, or generic from
  special-case checks — a paper that treats all confirmations as equally strong
  evidence is itself a mild red flag, feeding Dimension 4 (Derivation Rigor).

---

## CRITICAL: WHAT THIS IS NOT

Plausible reasoning is not proof, and high plausibility never licenses writing
"Theorem," "Proposition," or dropping the Conjecture/Heuristic label. Its only
function is to let a Conjecture be described honestly — "well-supported but
unproven" reads very differently from "one designed-in check, nothing else" —
and to help decide where further effort is best spent: a Low-confidence
conjecture resting on one special-case check is exactly where the Discovery
Engine's contradiction-hunt mode, or a deliberate `adversarial-review.md` pass,
is most likely to be productive.
