# PhysicsForge — Symbolic Verification Reference

How to verify derivations computationally using sympy and numerical sanity checks.

---

## WHEN TO VERIFY

Run symbolic verification:
- After any non-trivial algebraic derivation
- After deriving a new formula or operator
- When auditing a paper (use these patterns on suspicious steps)
- Before declaring the Pauli Protocol [5] (Dimensional consistency) PASS
- Before promoting a Conjecture to a Proposition or Theorem

If code execution is unavailable, at minimum run the dimensional analysis manually
on paper and document the check.

---

## SETUP PATTERN

Standard imports for any verification session:

```python
import sympy as sp
from sympy import symbols, Symbol, Function, diff, integrate, simplify, expand
from sympy import Rational, sqrt, pi, exp, log, sin, cos, oo, limit, series
from sympy.physics.units import meter, second, kilogram, kelvin, ampere, mole
from sympy.physics.units import Quantity, convert_to
from sympy import Matrix, eye, zeros, ones
import numpy as np

# For cleaner output
sp.init_printing(use_unicode=True)
```

---

## PATTERN 1 — DIMENSIONAL ANALYSIS

### Manual approach (always works)

Define each variable with its physical dimensions [M^a L^b T^c Θ^d Q^e],
substitute, and check every term in an equation has the same dimensions.

```python
# Example: verify Einstein field equation dimensions
# G_μν + Λ g_μν = (8πG/c⁴) T_μν

# Dimensions of each quantity:
# [G_μν] = L^{-2}      (curvature)
# [Λ]    = L^{-2}      (cosmological constant)
# [g_μν] = 1           (metric, dimensionless in geometrized units)
# [G/c⁴] = L M^{-1}    (gravitational coupling, in SI)
# [T_μν] = M L^{-1} T^{-2}  (energy-momentum density)

# RHS dimensions: [G/c⁴][T_μν] = L M^{-1} · M L^{-1} T^{-2} = T^{-2}
# But L^{-2} on LHS and T^{-2} on RHS only match in c=1 units
# In SI: include c² to fix → check passes
```

### sympy units approach

```python
from sympy.physics.units import Quantity, length, mass, time, force
from sympy.physics.units.systems import SI

# Define quantities
G = Quantity('G', dimension=length**3 / (mass * time**2))   # 6.674e-11 m³/kg/s²
c = Quantity('c', dimension=length / time)
M = Quantity('M', dimension=mass)
r = Quantity('r', dimension=length)

# Schwarzschild radius: r_s = 2GM/c²
r_s = 2 * G * M / c**2

# Verify dimensions equal length
from sympy.physics.units.dimensions import Dimension
print(SI.get_dimensional_expr(r_s))  # Should print: length
```

### Output template

```
Dimensional check for Eq.(N): r_s = 2GM/c²
  [G]   = L³ M⁻¹ T⁻²
  [M]   = M
  [c²]  = L² T⁻²
  [GM/c²] = (L³ M⁻¹ T⁻²)(M) / (L² T⁻²) = L  ✓
```

---

## PATTERN 2 — LIMITING CASES

Verify a formula reduces to known results in the appropriate limits.

```python
# Example: verify relativistic energy reduces to E = mc² + (1/2)mv² for v << c

m, v, c = symbols('m v c', positive=True)
E = m * c**2 / sp.sqrt(1 - v**2/c**2)

# Taylor expand around v=0
E_expansion = series(E, v, 0, 5).removeO()
print(E_expansion)
# Expected: m·c² + (1/2)·m·v² + (3/8)·m·v⁴/c² + ...
# ✓ First term: rest energy
# ✓ Second term: classical kinetic energy
# ✓ Third term: leading relativistic correction

# Numerical sanity check: at v = 0.1c, deviation from m·c² + (1/2)mv²?
import numpy as np
m_val, c_val, v_val = 1.0, 1.0, 0.1
E_full = m_val * c_val**2 / np.sqrt(1 - v_val**2/c_val**2)
E_approx = m_val * c_val**2 + 0.5 * m_val * v_val**2
print(f"Full: {E_full:.6f}, Approx: {E_approx:.6f}, Diff: {E_full - E_approx:.2e}")
# Should be ~3.75e-5 — matches the (3/8)v⁴/c² term
```

### Output template

```
Limiting case check:
  Limit v→0:        E → mc² + (1/2)mv²    ✓ recovers classical
  Limit v→c:        E → ∞                 ✓ relativistic divergence
  Limit m→0:        E → pc                ✓ photon energy
```

---

## PATTERN 3 — ALGEBRAIC IDENTITIES

Verify a claimed algebraic equality.

```python
# Example: verify Sherman-Morrison formula used in Beltrami metric paper
# (I + Kvv^T)^{-1} = I - K/(1+K) vv^T  for unit vector v

# Set up symbolically with v = (v1, v2, v3), unit vector
v1, v2, v3, K = symbols('v_1 v_2 v_3 K')
v = sp.Matrix([v1, v2, v3])

# Constraint: v is unit vector
unit_constraint = v.dot(v) - 1  # should equal 0

# g_ij = δ_ij + K v_i v_j
I = sp.eye(3)
g = I + K * v * v.T

# Proposed inverse
g_inv_claimed = I - (K / (1 + K)) * v * v.T

# Verify g · g_inv = I, modulo unit constraint
product = g * g_inv_claimed
product_simplified = sp.simplify(product.subs(v1**2 + v2**2 + v3**2, 1))
print(product_simplified)
# Should print: identity matrix (3x3)

# Check: is product == I?
diff = product_simplified - I
print(sp.simplify(diff))  # Should be 3x3 zero matrix
```

### Output template

```
Algebraic identity check: Sherman-Morrison for g = I + K·vv^T
  Claimed inverse: g⁻¹ = I − [K/(1+K)] vv^T
  Verification:    g · g⁻¹ = I (under v·v = 1)  ✓
```

---

## PATTERN 4 — SIGN AND CONVENTION CHECKS

Sign errors are silent killers. Test at numerical points.

```python
# Example: verify a Lyapunov functional decreases
# F(t) = (1/2) ∫ |ω|² Ψ(|ω|²/λ²) dx
# Claim: dF/dt ≤ 0 along Navier-Stokes flow when production is depleted

import numpy as np

# Numerical surrogate: discretize ω and check time derivative sign
# (full PDE simulation is too heavy; use a toy ODE that mimics structure)

def Psi(s):
    # Concave: Ψ(s) = s for s≤1, Ψ(s) ~ (3/2) s^{1/3} for s≫1
    return np.where(s <= 1, s, 1.5 * s**(1/3))

def Psi_prime(s):
    return np.where(s <= 1, 1.0, 0.5 * s**(-2/3))

# Bonus dissipation integrand: 2Ψ' + sΨ''
# For s ≫ 1: Ψ''(s) = -(1/3) s^{-5/3}
# 2Ψ' + sΨ'' = s^{-2/3} - (1/3)s^{-2/3} = (2/3) s^{-2/3} > 0  ✓

s_test = np.array([0.5, 1.0, 10.0, 100.0])
psi_p = Psi_prime(s_test)
# Numerical Psi'' via finite difference
ds = 1e-6
psi_pp = (Psi_prime(s_test + ds) - Psi_prime(s_test - ds)) / (2*ds)
bonus = 2 * psi_p + s_test * psi_pp

print("s\tPsi'\tPsi''\t\t2Psi'+sPsi''")
for s, pp, ppp, b in zip(s_test, psi_p, psi_pp, bonus):
    print(f"{s:.2f}\t{pp:.4f}\t{ppp:.6f}\t{b:.4f}")

# All bonus values should be positive
assert np.all(bonus >= -1e-9), "Bonus dissipation should be non-negative"
print("✓ Bonus dissipation is non-negative across test points")
```

### Output template

```
Sign / monotonicity check:
  Quantity: 2Ψ' + sΨ''  (bonus dissipation integrand)
  Claim:    ≥ 0 for all s > 0
  Tested:   s ∈ {0.5, 1.0, 10, 100}
  Result:   {1.0, 1.0, 0.215, 0.046} — all positive  ✓
```

---

## PATTERN 5 — INTEGRAL AND OPERATOR IDENTITIES

For PDE / harmonic analysis, verify L^p embeddings, integration-by-parts steps, etc.

```python
# Example: Hardy-Littlewood-Sobolev exponent check
# I_α: L^p → L^q with 1/q = 1/p − α/n

p_val, q_val, alpha, n = sp.symbols('p q α n', positive=True)
hls_relation = sp.Eq(1/q_val, 1/p_val - alpha/n)

# For p=2, α=1/2, n=3:
substituted = hls_relation.subs({p_val: 2, alpha: sp.Rational(1,2), n: 3})
solution = sp.solve(substituted, q_val)
print(f"q = {solution}")  # Should give q = 3
```

### Common PDE checks

```python
# Integration by parts: ∫ ∇f · ∇g dx = -∫ f Δg dx (no boundary terms)
# Verify by substituting trial functions in 1D
from sympy import symbols, integrate, oo, exp, Function

x = symbols('x', real=True)
f = exp(-x**2)
g = x * exp(-x**2)

lhs = integrate(sp.diff(f, x) * sp.diff(g, x), (x, -oo, oo))
rhs = -integrate(f * sp.diff(g, x, 2), (x, -oo, oo))
print(f"LHS: {lhs}, RHS: {rhs}, Equal: {sp.simplify(lhs - rhs) == 0}")
```

---

## PATTERN 6 — TENSOR / INDEX CONTRACTION CHECKS

For GR, gauge theory, etc., verify tensor identities.

```python
# Example: verify Bianchi identity numerically for Schwarzschild metric
import numpy as np
import sympy as sp
from sympy.diffgeom import Manifold, Patch, CoordSystem
from sympy.diffgeom import metric_to_Christoffel_2nd, metric_to_Ricci_components

# (Full implementation is verbose; sympy.diffgeom or einsteinpy or symbolic
# tensor packages provide these checks. For most paper audits, manual
# component-by-component check is sufficient.)
```

For routine work, use index notation explicitly with sympy IndexedBase,
or just manual component-by-component verification.

---

## PATTERN 7 — RECOVERING KNOWN FORMULAS

Always verify a new derivation reduces to a known formula in the right limit.

```python
# Example: a new "modified Friedmann equation" must reduce to standard Friedmann
# when the modification parameter ε → 0

H, rho, G, c, eps, k, a = sp.symbols('H rho G c epsilon k a', positive=True)

# Hypothetical modified Friedmann:
H_mod_squared = (8*sp.pi*G/3) * rho - k*c**2/a**2 + eps*rho**2

# Standard Friedmann:
H_std_squared = (8*sp.pi*G/3) * rho - k*c**2/a**2

# Verify reduction
limit_check = sp.limit(H_mod_squared, eps, 0)
assert sp.simplify(limit_check - H_std_squared) == 0, "Failed to recover Friedmann"
print("✓ Modified Friedmann recovers standard Friedmann as ε → 0")
```

---

## INTERPRETING FAILURES

If a verification check fails:

1. **Don't hide it.** Report the failure inline in the response.
2. **Identify the type of failure**:
   - Algebraic error (re-derive)
   - Sign error (track signs through every step)
   - Dimensional error (re-check definitions)
   - Convention mismatch (check signature, factor of 2π, etc.)
   - The claim is genuinely wrong (downgrade to Conjecture, or retract)
3. **If failure is genuine**: explicitly tell the user. Downgrade the claim
   classification. Propose the corrected version.

---

## WHEN SYMPY CAN'T HELP

Symbolic verification has limits. It cannot verify:

- Functional analysis estimates (operator norms, embeddings between Banach spaces)
- Existence of weak solutions to PDE
- Convergence of approximation schemes
- Topological / geometric claims (homotopy, cohomology)
- Compactness arguments
- Spectral gaps

For these, fall back to:
- Citing established results from the literature
- Numerical experimentation on toy problems
- Checking necessary conditions (e.g., trace inequalities, Sobolev embeddings)
- Lower-dimensional analogs

For Millennium-class claims, the absence of a sympy verification path is itself
informative: it means the gap is genuinely analytical and not algebraic.

---

## OUTPUT FORMAT

Always wrap a verification trace in a clear block:

```
═══════════ SYMBOLIC VERIFICATION ═══════════
Target:    [equation or claim being verified]
Tool used: [sympy / numpy / manual]

Checks:
  ✓ [check 1] — [brief result]
  ✓ [check 2] — [brief result]
  ✗ [check 3] — [failure mode + investigation]

Verdict:   [PASS / PASS WITH CAVEATS / FAIL]
═════════════════════════════════════════════
```

Always include this block before claiming a derivation is verified.
