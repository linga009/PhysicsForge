# Pre-registration: ¹³C isotope shift of the falsification test in Narlagiri_Superconductivity_Thesis_v4

## Source claim
`Narlagiri_Superconductivity_Thesis_v4.tex`, Falsification chapter, item 6:
"a phonon mechanism predicts $T_c \propto M^{-\alpha}$ with $\alpha \approx 0.5$.
Substituting $^{13}$C for $^{12}$C ... provides a direct test."

This fractional shift has not been numerically computed anywhere in this
project before this file was written. This is a genuine prediction, not a
retrofit of a known answer.

## Hypothesis
Under the stated mechanism ($T_c \propto M^{-\alpha}$, $\alpha = 0.5$),
substituting $^{13}$C ($M = 13.003355$ u) for $^{12}$C ($M = 12.000000$ u)
in the framework's stiff carbon mode predicts a **fractional decrease** in
$T_c$ (heavier isotope, lower phonon frequency, lower $T_c$).

## Primary analysis (exact specification)
```
shift = (M13 / M12) ** (-alpha) - 1,   alpha = 0.5 exactly
M13 = 13.003355 (IUPAC standard atomic weight of carbon-13)
M12 = 12.000000 (exact, by definition of the unified atomic mass unit)
```
No other transformation, correction, or fitting. Computed via `deriv_check.py`
(exact `sympy` arithmetic, not floating-point approximation, so no numerical
tolerance is needed — the decision rule below is exact equality of sign and a
bound on magnitude).

## Prediction (locked before computation)
Using the small-shift approximation $(1+x)^{-1/2} \approx 1 - x/2$ with
$x = M_{13}/M_{12} - 1 \approx 0.0836$: the exact value should be a decrease of
**between 3.5% and 4.5%** (I expect close to 4.0%, but am registering a range
because the approximation is linear and the true value includes higher-order
terms I have not carried through by hand).

## Decision rule
- **Confirmed** if the exact computed shift is negative (a decrease) and its
  magnitude falls in [3.5%, 4.5%].
- **Disconfirmed** if the sign is wrong, or the magnitude falls outside that
  range — in which case the linear approximation above was misleading enough
  to be worth flagging, not just quietly correcting.

## Falsifiability
A computed shift outside [3.5%, 4.5%] in magnitude, or of the wrong sign,
disconfirms this specific prediction (though not the underlying $\alpha=0.5$
claim itself, which is the manuscript's, not this registration's).

## Stopping rule
One computation, via `tools/deriv_check.py`, no optional re-runs.

**Frozen at commit:** 859d29b1fba6dc1a8f336caad5169290bc6328bf
