# PhysicsForge — Counterexample & Refutation Protocol

A protocol for what to do the moment a counterexample appears against a claim —
yours or another author's. This is the step most existing protocols in this skill
assume happens automatically ("downgrade the claim") without saying *how* to do it
honestly. Lakatos showed that "how" is where most intellectual dishonesty actually
happens.

---

## WHY THIS MATTERS

Every non-trivial claim eventually meets a counterexample. What happens next
determines whether the resulting work is honest or merely defensible.

**A real case, from this skill's own use.** A manuscript claimed: "the
$(\lambda, \omega_{\log})$ parameter region required for $T_c = 300\,\mathrm{K}$
is empty — no real material reaches it." An audit found that full-Eliashberg
calculations for $\mathrm{LaH_{10}}$ (Kruglov et al., *Phys. Rev. B* **101**, 024508,
2020) give $\lambda \approx 3.4$–$3.9$, $\omega_{\log} \approx 69$–$78\,\mathrm{meV}$,
$T_c \approx 246$–$271\,\mathrm{K}$ — sitting inside the region the manuscript called
empty. That is a genuine counterexample to the claim as stated.

At that moment there were several ways to respond. Only one of them is honest
science. Lakatos, in *Proofs and Refutations* (Cambridge University Press, 1976),
catalogued the responses mathematicians actually use when a conjecture meets a
counterexample — and named the dishonest ones so they can be recognized.

---

## THE LAKATOS TAXONOMY OF RESPONSES

| Response | What it does | Verdict |
|---|---|---|
| **Surrender** | Abandon the claim entirely. | Honest, but usually throws away a real partial result. |
| **Monster-barring** | Declare the counterexample "not a real instance" by silently redefining terms, with no independent justification for the redefinition. | **FORBIDDEN — see below** |
| **Exception-barring** | Keep the original claim but explicitly carve out the class of objects the counterexample belongs to, stating the exclusion openly. | Legitimate if the exclusion is principled and stated. |
| **Monster-adjustment** | Reinterpret the counterexample so it turns out to actually satisfy the claim after all, via a genuine (not ad hoc) reading of the definitions. | Legitimate only if the reinterpretation is independently motivated, not invented to save the claim. |
| **Lemma-incorporation** | Find exactly which hidden assumption the counterexample violates, make that assumption an explicit hypothesis of the claim (a new lemma), and restate. | The standard, healthy move — usually strengthens the claim by making its true domain explicit. |
| **Proofs and refutations proper** | Use the counterexample to revise *both* the claim and its proof/derivation together, arriving at a new, narrower, better-justified statement. | The target. Refines rather than merely patches. |

**Applied to the LaMgC₂ case (lemma-incorporation / proofs-and-refutations):**
the claim "$T_c = 300\,\mathrm{K}$ requires an empty parameter region" became
"that region is populated by hydrides; a hydrogen-free compound is disfavoured
because it lacks hydrogen, has a heavy framework atom, and would need
$\lambda \gtrsim 3$ — at or beyond the validity limit of the theory being used."
The hidden assumption ("no material occupies this region") was made explicit,
found false, and removed. What remained was narrower and defensible.

---

## MONSTER-BARRING IS FORBIDDEN

Monster-barring is the single most tempting response, because it requires no
rework: you just declare the inconvenient case doesn't count. It is intellectually
dishonest whenever the exclusion has no justification beyond "otherwise my claim
is false." Concretely, monster-barring looks like:

- "That's not really a counterexample because [redefinition invented on the spot,
  with no independent motivation, that happens to exclude exactly this case]."
- Silently narrowing scope in later sections without flagging that the original,
  broader claim has been abandoned.
- Calling a valid counterexample an "edge case" or "unphysical" with no argument
  for why it is either.

**Test**: would the exclusion have been written down *before* you saw the
counterexample? If not, and if it excludes nothing else of interest, it is
monster-barring. This is now `FORBIDDEN BEHAVIOR` alongside the list in
`SKILL.md`'s Claim Hierarchy section.

Exception-barring and monster-adjustment are legitimate cousins of
monster-barring and are easy to confuse with it. The dividing line is whether the
exclusion or reinterpretation is *principled and would survive being checked by
someone hostile to your conclusion* — not whether it is convenient.

---

## PROCEDURE

### Step 1 — Verify the counterexample is real
Before responding at all, check the counterexample itself the way you would check
any claim: primary source, correct reading of the numbers, correct comparison of
units/regime. A fabricated or misread "counterexample" is not a reason to weaken
a true claim. (This cuts both ways — do not wave away a real counterexample by
disputing it without checking, and do not accept a fake one out of excessive
caution.)

### Step 2 — Classify what it refutes
Does it refute:
- the claim as stated in full generality → the claim was too strong;
- one special case, with the general structure intact → exception-barring or
  lemma-incorporation is likely the right move;
- a hidden assumption that was never stated → lemma-incorporation, making the
  assumption explicit.

### Step 3 — Choose a response, in this preference order
1. Proofs-and-refutations (revise claim and derivation together) — preferred.
2. Lemma-incorporation (name the missing hypothesis explicitly).
3. Exception-barring (state the excluded class openly).
4. Surrender (if nothing defensible remains).
5. Monster-adjustment — only with an independently motivated reinterpretation;
   flag it for extra scrutiny even when used.
6. Monster-barring — never. If a response looks like this, it is wrong.

### Step 4 — Re-run the affected checks
A refined claim needs the Pauli Protocol and, if a derivation changed, the
Anti-Fabrication Check re-run against the new statement, not the old one.

### Step 5 — Document the refinement openly
State explicitly: what the original claim was, what the counterexample showed,
which response was chosen and why, and what the claim now says. This is not an
admission of failure — **downgrading or narrowing a claim under a real
counterexample is the protocol working correctly**, consistent with the
self-audit principle already in `SKILL.md`.

---

## OUTPUT FORMAT

```
═══════════ COUNTEREXAMPLE RESPONSE ═══════════
Original claim: <as stated>
Counterexample: <what it is, source, verified how>
Refutes: <full claim / special case / hidden assumption>
Response chosen: <Surrender / Exception-barring / Monster-adjustment /
                   Lemma-incorporation / Proofs-and-refutations>
Justification for this response (not monster-barring): <why the exclusion
  or revision is principled, not ad hoc>
Revised claim: <new statement>
Re-verification: Pauli Protocol re-run?  PASS / FAIL
                 Anti-Fabrication re-run (if derivation changed)? PASS / FAIL / N-A
════════════════════════════════════════════════
```

---

## INTEGRATION WITH OTHER PROTOCOLS

- **Anti-Fabrication Protocol, Mode 1 (Fake Results)**: a monster-barred claim is
  a specific way of producing a fake result — the counterexample was real, the
  exclusion was not.
- **Pauli Protocol, check [3] (Hidden assumption audit)**: lemma-incorporation is
  literally the act of finding the hidden assumption Pauli check [3] asks about,
  after the fact instead of before it. Running this protocol should feed back
  into writing better hidden-assumption audits next time.
- **Self-audit (`SKILL.md` Phase 4)**: "downgrading is success, not failure" is
  the same principle this protocol operationalizes for the specific case of an
  external or self-discovered counterexample.
- **Breakthrough red flags (`breakthrough-red-flags.md`)**: an author who
  responds to every objection with monster-barring, rather than any of the
  legitimate responses above, is itself one of the sociological red flags in
  that file.
- **Adversarial review (`adversarial-review.md`)**: the Devil's Advocate persona
  should actively try to construct counterexamples; this protocol is what
  happens on the other side once one lands.

---

## CRITICAL: WHAT THIS PROTOCOL IS NOT

This is not a license to abandon a claim at the first objection, and it is not a
license to keep a claim alive indefinitely through successive narrow patches
either. Exception-barring and lemma-incorporation are normal, healthy parts of
how real theorems get their final, correct statement — most published theorems
went through several rounds of this before publication. The failure mode this
protocol targets is specifically the *dishonest* response (monster-barring), not
the *iterative* nature of refining a claim under pressure from evidence.
