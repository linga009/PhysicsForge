# PhysicsForge — Extraordinary Claims Protocol

Some claim classes have a documented base rate of failure approaching 100%. When a
manuscript makes one, ordinary review is insufficient — not because such claims are
impossible, but because the historical record shows that plausible-looking derivations
in these areas fail for *recurring, identifiable* reasons.

This protocol names those reasons so they can be checked directly.

**This is not a rule against ambition.** Every entry below was eventually solved, or may
yet be. The protocol exists so a genuine result can be distinguished from the far more
common failure — which serves the author, since an unchecked extraordinary claim is
rejected without being read.

---

## TRIGGER LIST

Invoke this protocol when a manuscript claims any of:

| Claim class | Historical base rate |
|---|---|
| Room-temperature superconductivity at ambient pressure | ~0 confirmed. Three separate retractions, three different systems — see the precise record below |
| Cold fusion / LENR | Unreplicated since Fleischmann–Pons (1989) |
| Faster-than-light signalling | Zero confirmed. OPERA (2011) traced to a loose fibre connector |
| Perpetual motion / over-unity | Excluded by thermodynamics |
| Universal cure / universal neutralization (any pathogen) | No precedent; escape mutation is near-universal |
| Solving a Clay Millennium Problem | See MILLENNIUM-CLASS PROTOCOL in SKILL.md |
| Refuting special/general relativity or QM at tested scales | Zero confirmed |
| A single framework explaining an unrelated set of problems | Near-universal marker of unfalsifiability |
| Protein folding "solved" analytically | Structure prediction is empirically solved (AlphaFold2); *analytic* solution unprecedented |

---

### THE RTSC RETRACTION RECORD — get these right, they are three distinct events

An earlier version of this file said "Ranga Dias CSH papers retracted (Nature 2022, 2024)."
That is wrong, and it propagated verbatim into a manuscript audited with this skill. There
are three retractions, of three different materials, in two different journals:

| # | Paper | System | Retracted | Grounds |
|---|---|---|---|---|
| 1 | Snider et al., *Nature* **586**, 373 (2020) | Carbonaceous sulfur hydride (CSH) | **Sep 2022** | Non-standard, user-defined magnetic-susceptibility **background subtraction** |
| 2 | Dasenbrock-Gammon et al., *Nature* **615**, 244 (2023) | **N-doped lutetium hydride** | **Nov 2023** | Material provenance, measurements and data-processing protocols misrepresented; not independently reproduced |
| 3 | Snider et al., *Phys. Rev. Lett.* **126**, 117003 (2021) | **Yttrium superhydride** | **Jun 2024** (PRL **132**, 249901) | Data integrity |

Separately: **LK-99** (2023, Lee et al., copper-substituted lead apatite) was never
retracted because it was a preprint; it was simply not reproduced, and the resistivity
drop was attributed to a Cu₂S impurity transition.

**Why the distinction matters for an audit.** Each retraction failed at a *different*
point in the measurement chain, so each implies a different required check:
- CSH → demand the **susceptibility background-subtraction procedure** in full.
- LuH-N → demand **sample provenance** and independent reproduction.
- YH₉ → demand **raw data**, not processed traces.

Citing "the retractions" generically is not sufficient; name which one and which failure
mode the manuscript's own protocol addresses.

## MANDATORY OPENING

When the user asks to develop, write up, or defend such a claim, open with:

> *"This is an extraordinary-claim class with a documented base rate of failure. I will
> not validate it on plausibility. What I CAN do: [test the specific mechanism / identify
> the precise step that must hold / design the falsifying measurement / compare against
> the known failure modes of prior attempts]. The output below should be read as
> [mechanism test / partial analysis / critique], not as confirmation of [claim]."*

Then proceed with full rigor. **A correctly identified fatal flaw is a more valuable
deliverable than an encouraging review.**

---

## THE SEVEN RECURRING FAILURE MODES

Check each explicitly. These are drawn from the actual post-mortems of failed claims,
not invented.

### EC-1 — The divergence read as an enhancement
A quantity diverges and the manuscript treats this as the *mechanism* rather than as the
breakdown of the theory.

> **In superconductivity**: λ → ∞ is presented as maximal pairing. In reality λ ≳ 1–2
> softens the phonon toward ω → 0 and the lattice undergoes a Peierls/CDW distortion.
> The divergence *is* the structural instability.
>
> **Generally**: a pole in a response function (Stoner criterion, RPA denominator
> 1 − V·N(E_F) → 0, Landau pole) signals a phase transition or a breakdown of the
> expansion. It never means "the effect is stronger."

**Check**: for every divergence, state what *instability* it signals and show the system
is stable against it.

### EC-2 — The stability check that was never run
A proposed material/state is shown to be energetically favourable but never shown to be
*dynamically* stable.

**Check**: phonon dispersion computed across the full Brillouin zone; **no imaginary
modes**. Formation enthalpy alone is insufficient. A structure with imaginary phonons does
not exist at the claimed conditions, whatever its predicted T_c.

### EC-3 — Conditions quietly swapped
The mechanism is validated under condition A; the claim is made for condition B.

> **Canonical**: hydride superconductors require ~150–200 GPa **hydrostatic** pressure.
> A manuscript proposing "equivalent" pressure from epitaxial strain has swapped
> hydrostatic for **biaxial** — a different stress tensor with different physics — and
> additionally ignored that coherent mismatch strain relaxes via misfit dislocations
> beyond a critical thickness of a few nm.

**Check**: state condition A and condition B explicitly side by side. Prove equivalence
or drop the claim.

### EC-4 — The suppressing term omitted
A term that *limits* the effect in real systems is absent from the treatment.

> **In superconductivity**: μ\* (the Coulomb pseudopotential) is what caps real T_c.
> A gap equation without μ\* will always over-predict.
>
> **In folding/binding**: solvent entropy and the hydrophobic effect.
> **In fusion**: bremsstrahlung losses and Coulomb barrier screening.

**Check**: name the standard suppressing term for this domain; confirm it is present with
a physically motivated value.

### EC-5 — Asserted inputs, computed conclusion
The headline number depends on parameters that were stated rather than derived, while the
abstract promises they were derived.

**Check**: trace every number in the final formula back to a calculation, measurement, or
cited source. An input that appears only once, at the point of use, is a red flag —
especially if perturbing it by 30% destroys the conclusion.

### EC-6 — Sensitivity never reported
No indication of how fragile the result is.

**Check**: vary each key parameter by ±30% and report the resulting spread in the headline
number. If the claim survives only in a narrow window that happens to contain the desired
answer, say so explicitly.

### EC-7 — Escape / adaptation ignored (biological claims)
A therapeutic claim treats the target as static.

> **Canonical**: "universal" antivirals. Viruses escape by mutating the binding interface —
> this is why neutralizing antibodies and soluble-receptor decoys (e.g. soluble ACE2)
> lose potency. Any claim of immunity to escape must explain *why* the mechanism is
> invariant under mutation, not merely assert it.

**Check**: state the escape pathway and why it is blocked.

---

## MANDATORY OUTPUT

```
═══════════ EXTRAORDINARY CLAIM CHECK ═══════════
CLAIM CLASS: <from trigger list>
BASE RATE:   <historical record, one line>

[EC-1] Divergence-as-enhancement:  PASS / FAIL / N/A — <reason>
[EC-2] Dynamical stability:        PASS / FAIL / N/A — <imaginary modes?>
[EC-3] Condition equivalence:      PASS / FAIL / N/A — <A vs B>
[EC-4] Suppressing term present:   PASS / FAIL / N/A — <which term>
[EC-5] Inputs derived not asserted:PASS / FAIL / N/A — <trace>
[EC-6] Sensitivity reported:       PASS / FAIL / N/A — <±30% spread>
[EC-7] Escape/adaptation:          PASS / FAIL / N/A — <pathway>

DISCRIMINATING EXPERIMENT: <the single measurement that would settle it>
═════════════════════════════════════════════════
```

**Any FAIL caps the claim at `Conjecture`, regardless of how much supporting apparatus is
present.** Two or more FAILs require the mandatory opening above to be repeated in the
manuscript's own abstract.

---

## THE DISCRIMINATING EXPERIMENT REQUIREMENT

Every extraordinary claim must name **one** measurement that would falsify it, with:

- the observable and its predicted value **with uncertainty**
- the value expected under the null hypothesis
- the required sensitivity to distinguish them
- whether current instrumentation reaches that sensitivity

> *"Synthesise it and measure T_c"* is **not** sufficient — it does not specify what
> result would count as refutation. *"X-ray diffraction must show Fm3̄m with a = X ± Y Å,
> and four-point resistivity must show zero-resistance onset at T > 300 K with a
> Meissner-effect susceptibility signature"* is sufficient.

Historical note: the Ranga Dias retractions turned specifically on the **susceptibility
background subtraction**, not on the resistivity. Specify the full measurement chain,
including what is subtracted.

---

## INTEGRATION

- Runs **before** ScholarEval, and its result caps Dimension 1 (Problem Formulation)
  at 3 if the discriminating experiment is missing.
- Any EC FAIL is also an `anti-fabrication.md` finding — record it in both.
- If the claim is also Clay-class, MILLENNIUM-CLASS PROTOCOL takes precedence and this
  protocol runs afterwards.
