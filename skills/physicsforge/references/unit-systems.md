# PhysicsForge — Unit-System Conflation Protocol

**The failure mode IRON RULE #9 cannot catch.**

Dimensional analysis verifies that both sides of an equation have the same *dimensions*.
It does **not** verify that both sides are expressed in the same *unit system*. When a
quantity has several conventional units that are all dimensionally identical, dimensional
analysis passes while the number is wrong by orders of magnitude.

This is not a hypothetical. It is the single most common way a physics manuscript reaches
a confident, dimensionally-consistent, numerically-absurd conclusion.

---

## THE CANONICAL FAILURE

A manuscript claims room-temperature superconductivity from

```
T_c = 0.18 · λ · ⟨ω⟩,     λ = 4.5,   ⟨ω⟩ = 400 meV   →  "T_c ≈ 300 K"
```

IRON RULE #9 passes: energy = energy. But:

```
0.18 × 4.5 × 400 meV = 324 meV
324 meV ÷ 0.08617 meV/K = 3,760 K        ← not 300 K. Off by 12.5×.
```

The stated conclusion only follows if ⟨ω⟩ is **400 K** (= 34.5 meV), not 400 meV. An
author who works alternately in meV and in K, and does not carry k_B explicitly, will
produce this error and never see it — every equation remains dimensionally valid.

**Diagnostic signature**: the claimed output is a round, desirable number (300 K), while
the inputs are round numbers in a *different* unit convention. That combination is the
tell.

---

## ENERGY — THE HIGH-RISK QUANTITY

Energy has more conventional units in active use than any other quantity, and physicists
routinely quote "energy" as a temperature, a frequency, a wavenumber, or a length.

| Unit | Conversion to eV | Typical use |
|---|---|---|
| K (via k_B) | 1 K = 8.617×10⁻⁵ eV | phonons, T_c, thermal scales |
| meV | 10⁻³ eV | phonons, magnons, gaps |
| THz (via h) | 1 THz = 4.136 meV | spectroscopy, phonon modes |
| cm⁻¹ (via hc) | 1 cm⁻¹ = 0.124 meV | vibrational spectroscopy, IR/Raman |
| Hartree | 27.211 eV | quantum chemistry, DFT output |
| Rydberg | 13.606 eV | DFT codes (Quantum ESPRESSO) |
| kcal/mol | 43.36 meV | biochemistry, protein energetics |
| kJ/mol | 10.36 meV | biochemistry |

**Anchors worth memorising** (a value far from these deserves scrutiny):

- Room temperature: 300 K = **25.9 meV** ≈ 0.026 eV
- Typical optical phonon: **20–100 meV** (≈ 230–1160 K)
- C–C / C–H stretch (stiffest common phonons): **150–400 meV**
- Debye temperature of diamond (extreme): 2230 K = **192 meV**
- Hydrogen-bond energy: **0.1–0.3 eV** (≈ 2–7 kcal/mol)
- k_B T at 300 K in biochemistry: **0.6 kcal/mol**

A phonon quoted at 400 meV (≈ 4,640 K) is at the extreme edge of what any solid supports
and requires explicit justification.

---

## OTHER HIGH-RISK CONFLATIONS

| Quantity | Conflated units | Trap |
|---|---|---|
| Magnetic field | T vs G vs A/m | 1 T = 10⁴ G. Factor 10⁴ |
| Pressure | GPa vs kbar vs atm | 1 GPa = 10 kbar. Factor 10 |
| Cross-section | barn vs cm² vs GeV⁻² | 1 barn = 10⁻²⁴ cm² |
| Angle | rad vs deg vs μas | astronomy mixes all three |
| Mass | kg vs eV/c² vs amu | natural-unit boundary |
| Length | Å vs nm vs Bohr | 1 Bohr = 0.529 Å |

**Natural units are the highest-risk boundary of all.** In ℏ = c = 1, mass, energy,
momentum, inverse length and inverse time are all numerically identical. Restoring
physical units requires reinserting ℏ and c correctly, and this is where factors escape.

---

## MANDATORY UNIT AUDIT

Run this **in addition to** the dimensional check, whenever a numerical result is stated.
Print it inline.

```
═══════════════ UNIT AUDIT ═══════════════
[1] Unit declaration:    PASS / FAIL — every numerical input carries an explicit unit
[2] Single convention:   PASS / FAIL — one unit system per equation; conversions shown
[3] k_B / ℏ / c carried: PASS / FAIL — no silent "energy = temperature" identification
[4] Anchor sanity:       PASS / FAIL — each value compared to a known physical anchor
[5] Round-number tell:   PASS / FAIL — output not suspiciously round given inputs
[6] Recomputation:       PASS / FAIL — final number recomputed independently in SI
══════════════════════════════════════════
```

**Check [6] is not optional.** Recompute the headline number from scratch, in SI, with
every constant explicit. If the recomputation disagrees with the manuscript, the
manuscript is wrong — regardless of how many equations looked correct.

---

## ENFORCEMENT

- Any numerical claim presented without units is a **malformed claim** — treat exactly
  like a claim without epistemic status (IRON RULE #7).
- Any equation mixing two unit systems must show the conversion factor **explicitly in
  the equation**, not in surrounding prose.
- When auditing someone else's manuscript, **always recompute the headline number**. Do
  not assume the author did. This one action catches more real errors than any other
  single check in this skill.

---

## WORKED AUDIT EXAMPLE

> Manuscript: "With λ ≈ 4.5 and ⟨ω⟩ ≈ 400 meV we achieve T_c ≈ 300 K."

```
═══════════════ UNIT AUDIT ═══════════════
[1] Unit declaration:    PASS — λ dimensionless, ⟨ω⟩ in meV, T_c in K
[2] Single convention:   FAIL — LHS in K, RHS in meV, no k_B shown
[3] k_B / ℏ / c carried: FAIL — "energy = temperature" used silently
[4] Anchor sanity:       FAIL — 400 meV = 4,640 K; exceeds diamond's Debye
                                temperature (2,230 K) by 2×. Not justified.
[5] Round-number tell:   FAIL — inputs 4.5 / 400 are round; output 300 K is the
                                desired result. Signature of back-fitting.
[6] Recomputation:       FAIL — 0.18 × 4.5 × 400 meV = 324 meV = 3,760 K ≠ 300 K
══════════════════════════════════════════
VERDICT: keystone result does not follow from its own stated inputs.
Downgrade to Conjecture; flag the meV/K conflation explicitly to the author.
```

---

## INTEGRATION

- Runs alongside the **Pauli Protocol** check [5] (dimensional consistency) — that check
  should now read "dimensional **and unit-system** consistency."
- Feeds **ScholarEval** Dimension 5 (Verification): any FAIL here caps Dimension 5 at 2.
- A FAIL on check [6] (recomputation) is an automatic **Anti-Fabrication** failure mode 2
  (parameter adjustment), because a number that does not follow from its inputs was
  almost always chosen rather than computed.
