"""pfv.numtheory: number-theory checks.

Hard rules baked in (each was found the hard way, see references/verification-tools.md):
  * A finite search can REFUTE a universal claim (one witness) or VERIFY an existential one,
    but a universal claim that passes a finite range is only CONSISTENT, unless a theorem
    bounds the range (use `complete=True` only then).
  * sympy's totient/mobius/divisor_sigma/legendre/jacobi return sympy Integers; we convert
    with int() so Python's pow(a, phi, n) works.
  * sympy EllipticCurve.order excludes the point at infinity; `ec_count` includes it (Hasse
    convention).
  * factorint(n, limit=k) can return an unfactored composite cofactor as if prime.
"""
from __future__ import annotations

import itertools
import math
from fractions import Fraction
from typing import Callable, Iterable

import sympy as sp
from sympy import factorint, isprime, divisors, primefactors
from sympy.ntheory import n_order, primitive_root, nextprime
from sympy.functions.combinatorial.numbers import totient, mobius, divisor_sigma, jacobi_symbol

from .core import (Result, verified, consistent, inconclusive)
from .core import refuted as _refuted
from functools import partial as _partial
refuted = _partial(_refuted, evidence='exact integer/rational counterexample')


# --------------------------------------------------------------------------
# claims about integers by search
# --------------------------------------------------------------------------
def find_counterexample(pred: Callable[[int], bool], domain: Iterable[int], claim: str = "",
                        complete: bool = False) -> Result:
    """Universal claim 'pred(n) holds for every n in domain'.

    complete=True only if the domain IS the whole claim (a finite statement) or a theorem
    bounds the range; then a pass is VERIFIED. Otherwise a pass is CONSISTENT.
    """
    claim = claim or "pred(n) for all n in domain"
    count = 0
    first = last = None
    for n in domain:
        if first is None:
            first = n
        last = n
        count += 1
        try:
            ok = pred(n)
        except Exception as e:  # a crash is not a refutation
            return inconclusive("find_counterexample", claim, f"pred raised {type(e).__name__} at n={n}: {e}")
        if not ok:
            return refuted("find_counterexample", claim, n, detail=f"pred({n}) is False")
    if count == 0:
        return inconclusive("find_counterexample", claim, "the domain is empty: nothing was checked")
    ev = f"checked {count} values in [{first}, {last}]"
    if complete:
        return verified("find_counterexample", claim, ev + " (finite claim / range bounded by a theorem)")
    return consistent("find_counterexample", claim, ev,
                      caveat="Finite range only. Famous failures: n^2+n+41 is prime for n=0..39 but not 40; "
                             "Mertens |M(n)|<sqrt(n) holds to 1e16 but is false.")


def check_claimed_value(computed, claimed, claim: str = "claimed value equals recomputed value") -> Result:
    """Recompute from the problem text, then compare EXACTLY with the claimed answer.

    Pass `computed` as int / Fraction / sympy Rational / sympy expression, never a float
    when the claim is exact. This is the check that refutes altered final answers.
    """
    from .core import to_exact, cap_inexact, claimed_value_result
    c, computed_inexact = to_exact(computed)
    res = claimed_value_result("check_claimed_value", claim, c, claimed, "exact equality", truth_inexact=computed_inexact, recomputed=str(c))
    return cap_inexact(res, "recomputed value") if computed_inexact else res


# --------------------------------------------------------------------------
# primes and factorization
# --------------------------------------------------------------------------
def check_factorization(n: int, factors) -> Result:
    """`factors` is a dict {p: e} or a list of primes (with repetition)."""
    if not isinstance(factors, dict):
        d = {}
        for p in factors:
            d[p] = d.get(p, 0) + 1
        factors = d
    prod = 1
    for p, e in factors.items():
        prod *= p ** e
    if prod != n:
        return refuted("check_factorization", f"{n} = {factors}", {"product": prod},
                       detail=f"product of claimed factors is {prod}, not {n}")
    composite = [p for p in factors if not isprime(p)]
    if composite:
        return refuted("check_factorization", f"{n} = {factors}", composite[0],
                       detail=f"{composite[0]} is not prime (factor {composite[0]} = {factorint(composite[0])})")
    big = [p for p in factors if p >= 2 ** 64]
    if big:
        return consistent("check_factorization", f"{n} = {factors}",
                          "product exact; primality of large factors by BPSW",
                          caveat="isprime is a strong probable-prime test above 2^64; no counterexample known, "
                                 "but not a certificate.")
    return verified("check_factorization", f"{n} = {factors}", "product exact; every factor prime (deterministic < 2^64)")


def _pratt(p: int, depth: int = 0, cache=None) -> bool | None:
    """Pratt certificate: True if certified, False if p composite, None if undecidable here."""
    cache = {} if cache is None else cache
    if p in cache:
        return cache[p]
    if p < 2:
        return False
    if p in (2, 3):
        return True
    if depth > 60 or p > 10 ** 40:
        return None
    fac = factorint(p - 1, limit=10 ** 6)
    prod = 1
    for q, e in fac.items():
        prod *= q ** e
    if prod != p - 1:
        return None  # incomplete factorization
    for g in range(2, min(p, 2000)):
        if pow(g, p - 1, p) != 1:
            cache[p] = False
            return False
        if all(pow(g, (p - 1) // q, p) != 1 for q in fac):
            ok = all(_pratt(q, depth + 1, cache) for q in fac)
            cache[p] = ok
            return ok
    return None


def certify_prime(n: int) -> Result:
    """Pratt certificate when feasible; else the deterministic/BPSW answer, labelled as such."""
    claim = f"{n} is prime"
    if n < 2:
        return refuted("certify_prime", claim, n, detail="n < 2")
    if not isprime(n):
        f = factorint(n, limit=10 ** 6)
        return refuted("certify_prime", claim, {"factorisation_found": f})
    c = _pratt(n)
    if c is True:
        return verified("certify_prime", claim, "Pratt certificate (recursive primitive-root witnesses)")
    if n < 2 ** 64:
        return verified("certify_prime", claim, "deterministic Miller-Rabin set valid below 2^64")
    return consistent("certify_prime", claim, "strong BPSW probable prime",
                      caveat="No Pratt certificate (p-1 not fully factored in budget). BPSW has no known counterexample.")


# --------------------------------------------------------------------------
# congruences, CRT, symbols
# --------------------------------------------------------------------------
def check_congruence(f: Callable[[int], int], modulus: int, domain: Iterable[int], residue: int = 0) -> Result:
    """Claim: f(n) = residue (mod modulus) for all n in domain."""
    return find_counterexample(lambda n: (f(n) - residue) % modulus == 0, domain,
                               claim=f"f(n) = {residue} (mod {modulus})")


def check_crt(residues, moduli, claimed=None) -> Result:
    """Solve x = r_i (mod m_i). Reports non-coprime moduli (a classic mistake) and inconsistency."""
    from sympy.ntheory.modular import solve_congruence
    claim = f"x = {list(residues)} mod {list(moduli)}"
    g = 1
    for a, b in itertools.combinations(moduli, 2):
        g = max(g, math.gcd(a, b))
    sol = solve_congruence(*[(r, m) for r, m in zip(residues, moduli)])
    if sol is None:
        return refuted("check_crt", claim, None, detail="system is inconsistent: no solution exists")
    x, M = int(sol[0]), int(sol[1])
    note = "" if g == 1 else f"moduli are not pairwise coprime (max gcd {g}); solution modulus is lcm = {M}"
    if claimed is not None:
        ok = all((claimed - r) % m == 0 for r, m in zip(residues, moduli))
        if not ok:
            return refuted("check_crt", claim, {"claimed": claimed, "true_solution": f"{x} mod {M}"}, detail=note)
    return verified("check_crt", claim, "exact modular arithmetic", detail=f"x = {x} (mod {M}). {note}".strip())


def check_symbol_claims(p: int, q: int) -> Result:
    """Quadratic reciprocity and Euler's criterion for odd primes p, q."""
    if p == q or not (isprime(p) and isprime(q)) or p == 2 or q == 2:
        return inconclusive("check_symbol_claims", f"({p}|{q})", "need distinct odd primes")
    def leg(a, m):
        return int(jacobi_symbol(a % m, m))
    lhs = leg(p, q) * leg(q, p)
    rhs = (-1) ** (((p - 1) // 2) * ((q - 1) // 2))
    euler = all(leg(a, p) == (1 if pow(a, (p - 1) // 2, p) == 1 else -1) for a in range(1, p))
    if lhs != rhs or not euler:
        return refuted("check_symbol_claims", f"reciprocity for ({p},{q})", {"lhs": lhs, "rhs": rhs, "euler_ok": euler})
    return verified("check_symbol_claims", f"quadratic reciprocity and Euler criterion for p={p}, q={q}",
                    "exact", detail="Note: Jacobi symbol +1 does NOT imply a square for composite modulus.")


def is_quadratic_residue_claim(a: int, n: int, claimed: bool) -> Result:
    """Is a a square mod n? Brute force (exact), compared with the claim."""
    truth = any((x * x - a) % n == 0 for x in range(n))
    claim = f"{a} is {'' if claimed else 'not '}a square mod {n}"
    if truth == claimed:
        return verified("is_quadratic_residue_claim", claim, f"exhaustive over x in [0,{n})")
    return refuted("is_quadratic_residue_claim", claim, {"truth": truth},
                   detail=f"jacobi({a}|{n}) = {int(jacobi_symbol(a % n, n)) if n % 2 else 'n/a'} (not a residue test when n is composite)")


# --------------------------------------------------------------------------
# multiplicative functions, orders, LTE
# --------------------------------------------------------------------------
def dirichlet_convolution(f: Callable[[int], int], g: Callable[[int], int], n: int) -> int:
    return sum(f(d) * g(n // d) for d in divisors(n))


def check_arithmetic_identity(lhs: Callable[[int], object], rhs: Callable[[int], object], N: int = 500,
                              claim: str = "") -> Result:
    """lhs(n) == rhs(n) for 1 <= n <= N, e.g. sum_{d|n} phi(d) = n. Finite evidence only."""
    claim = claim or "lhs(n) = rhs(n)"
    return find_counterexample(lambda n: sp.simplify(sp.sympify(lhs(n)) - sp.sympify(rhs(n))) == 0,
                               range(1, N + 1), claim=claim)


def check_multiplicative(f: Callable[[int], object], N: int = 300) -> Result:
    """Is f multiplicative: f(ab)=f(a)f(b) whenever gcd(a,b)=1 (and f(1)=1)?"""
    claim = "f multiplicative"
    if sp.sympify(f(1)) != 1:
        return refuted("check_multiplicative", claim, {"f(1)": f(1)})
    for a in range(2, N):
        for b in range(2, N // a + 1):
            if math.gcd(a, b) == 1 and sp.sympify(f(a * b)) != sp.sympify(f(a)) * sp.sympify(f(b)):
                return refuted("check_multiplicative", claim, (a, b), detail=f"f({a*b}) != f({a}) f({b})")
    return consistent("check_multiplicative", claim, f"coprime pairs with ab <= {N}")


def check_order_claim(a: int, n: int, claimed: int) -> Result:
    """Multiplicative order of a modulo n against a claimed value (exact)."""
    claim = f"ord_{n}({a}) = {claimed}"
    if n == 1:
        return verified("check_order_claim", claim, "trivial group (Z/1Z): every element has order 1") if claimed == 1 else refuted("check_order_claim", claim, {"true_order": 1})
    if math.gcd(a, n) != 1:
        return refuted("check_order_claim", claim, None, detail="gcd(a, n) != 1, order undefined")
    true = int(n_order(a, n))
    if true == claimed:
        return verified("check_order_claim", claim, "exact (sympy n_order, confirmed by pow)")
    return refuted("check_order_claim", claim, {"true_order": true})


def padic_valuation(p: int, n: int) -> int:
    if n == 0:
        raise ValueError("valuation of 0")
    v = 0
    n = abs(n)
    while n % p == 0:
        n //= p
        v += 1
    return v


def check_lte(p: int, x: int, y: int, n: int, claimed: int | None = None) -> Result:
    """Lifting the exponent: v_p(x^n - y^n) = v_p(x-y) + v_p(n), valid for odd p with p | x-y, p not dividing xy.
    Reports whether the hypotheses hold, then compares the formula with the true valuation."""
    true = padic_valuation(p, x ** n - y ** n)
    hyp = (p % 2 == 1 and (x - y) % p == 0 and x % p != 0 and y % p != 0)
    pred = padic_valuation(p, x - y) + padic_valuation(p, n) if hyp else None
    shown = claimed if claimed is not None else (pred if pred is not None else true)
    claim = f"v_{p}({x}^{n} - {y}^{n}) = {shown}"
    if claimed is not None and claimed != true:
        return refuted("check_lte", claim, {"true_valuation": true},
                       detail=f"LTE hypotheses {'hold' if hyp else 'FAIL (need odd p, p|x-y, p not dividing xy)'}")
    if pred is not None and pred != true:
        return refuted("check_lte", claim, {"true": true, "lte_prediction": pred})
    if not hyp:
        return verified("check_lte", claim, f"true valuation {true} computed exactly",
                        detail="LTE hypotheses do not hold (need odd p, p | x-y, p not dividing xy), so the LTE formula was NOT used.")
    return verified("check_lte", claim, f"true valuation {true} matches LTE")


# --------------------------------------------------------------------------
# Diophantine, Pell, sums of squares, elliptic curves, Zsigmondy
# --------------------------------------------------------------------------
def diophantine_search(f: Callable[..., int], nvars: int, bound: int, claim_no_solution: bool = False,
                       nonneg: bool = False, limit_nodes: int = 3_000_000) -> Result:
    """Search integer solutions of f(x1,..,xk) == 0 with |xi| <= bound.

    Found solutions are exact witnesses. 'No solution found' is only CONSISTENT with 'no
    solutions': a bounded search never proves non-existence (Pell x^2-61y^2=1 needs y > 2e8).
    """
    rng = range(0, bound + 1) if nonneg else range(-bound, bound + 1)
    sols = []
    nodes = 0
    for t in itertools.product(rng, repeat=nvars):
        nodes += 1
        if nodes > limit_nodes:
            return inconclusive("diophantine_search", "f=0", f"node limit {limit_nodes} reached")
        if f(*t) == 0:
            sols.append(t)
            if len(sols) >= 20:
                break
    if claim_no_solution:
        if sols:
            return refuted("diophantine_search", "f = 0 has no integer solutions", sols[0],
                           detail=f"{len(sols)}+ solutions found")
        return consistent("diophantine_search", "f = 0 has no integer solutions", f"no solution with |x_i| <= {bound}",
                          caveat="Bounded search; absence is not proof (needs a modular obstruction, descent, or bound).")
    return Result("diophantine_search", "solutions of f=0", "VERIFIED" if sols else "INCONCLUSIVE",
                  f"|x_i| <= {bound}", detail=f"{len(sols)} solutions" if sols else "none found", witness=sols[:5] or None)


def check_pell(D: int, x: int, y: int, N: int = 1) -> Result:
    """Verify x^2 - D y^2 = N for a claimed solution (exact integer arithmetic)."""
    claim = f"{x}^2 - {D}*{y}^2 = {N}"
    v = x * x - D * y * y
    if v == N:
        return verified("check_pell", claim, "exact integer arithmetic")
    return refuted("check_pell", claim, {"lhs": v})


def sum_of_squares_count(n: int, k: int) -> int:
    """r_k(n): number of integer representations n = x1^2+...+xk^2 (ordered, signed)."""
    from sympy.solvers.diophantine.diophantine import sum_of_squares
    total = 0
    for sol in sum_of_squares(n, k, zeros=True):
        # expand signs and permutations
        from sympy.utilities.iterables import multiset_permutations
        seen = set()
        for perm in multiset_permutations(list(sol)):
            for signs in itertools.product((1, -1), repeat=len(perm)):
                seen.add(tuple(s * v for s, v in zip(signs, perm)))
        total += len(seen)
    return total


def check_two_squares(n: int, claimed: bool) -> Result:
    """n is a sum of two squares iff every prime = 3 mod 4 occurs to an even power (Fermat/Euler)."""
    truth = all(p % 4 != 3 or e % 2 == 0 for p, e in factorint(n).items()) if n > 0 else True
    brute = any(int(math.isqrt(n - a * a)) ** 2 == n - a * a for a in range(0, math.isqrt(n) + 1)) if n >= 0 else False
    claim = f"{n} {'is' if claimed else 'is not'} a sum of two squares"
    assert truth == brute
    if claimed == truth:
        return verified("check_two_squares", claim, "exact; criterion and brute force agree")
    return refuted("check_two_squares", claim, {"truth": truth})


def ec_count(a: int, b: int, p: int) -> int:
    """#E(F_p) for y^2 = x^3 + a x + b over a prime p > 3, INCLUDING the point at infinity."""
    if p <= 3 or not isprime(p):
        raise ValueError("ec_count needs a prime p > 3 (short Weierstrass form is not valid in characteristic 2, 3; prime powers need F_q arithmetic)")
    if (4 * a ** 3 + 27 * b ** 2) % p == 0:
        raise ValueError("singular curve")
    sq = [0] * p
    for y in range(p):
        sq[(y * y) % p] += 1
    n = 1
    for x in range(p):
        n += sq[(x ** 3 + a * x + b) % p]
    return n


def check_hasse(a: int, b: int, p: int, claimed_count: int | None = None) -> Result:
    """Count points of y^2 = x^3 + a x + b over F_p (including infinity), check Hasse's bound, and compare with a claimed count."""
    try:
        n = ec_count(a, b, p)
    except ValueError as e:
        return inconclusive("check_hasse", f"#E(F_{p}) for y^2=x^3+{a}x+{b}", str(e))
    claim = f"#E(F_{p}) for y^2=x^3+{a}x+{b}" + (f" = {claimed_count}" if claimed_count is not None else " obeys Hasse")
    if abs(n - (p + 1)) > 2 * math.sqrt(p) + 1e-12:
        return refuted("check_hasse", claim, {"count": n}, detail="Hasse bound |N-(p+1)| <= 2 sqrt(p) violated (computation bug?)")
    if claimed_count is not None and claimed_count != n:
        return refuted("check_hasse", claim, {"true_count": n},
                       detail="Convention: the count includes the point at infinity (sympy's .order excludes it).")
    return verified("check_hasse", claim, "exhaustive over F_p", detail=f"N = {n}, |N-(p+1)| = {abs(n-p-1)} <= {2*math.sqrt(p):.3f}")


def zsigmondy_primitive_divisor(a: int, n: int) -> Result:
    """Does a^n - 1 have a prime divisor not dividing a^k - 1 for any k < n? (exists except (2,6) and n=2 with a+1 a power of 2)"""
    claim = f"a^n-1 has a primitive prime divisor, a={a}, n={n}"
    val = a ** n - 1
    prim = [q for q in primefactors(val) if int(n_order(a, q)) == n]
    if prim:
        return verified("zsigmondy_primitive_divisor", claim, f"found {prim[0]}")
    return refuted("zsigmondy_primitive_divisor", claim, None, detail="no primitive prime divisor (Zsigmondy exception)")


def modular_obstruction(f: Callable[..., int], nvars: int, moduli: Iterable[int] = (2, 3, 4, 5, 7, 8, 9, 11, 13, 16)) -> Result:
    """PROVE that f(x1..xk) = 0 has no integer solution: find a modulus m such that
    f(x) = 0 (mod m) has no solution in (Z/m)^k. Exhaustive, hence VERIFIED when it fires.
    If no modulus works the result is INCONCLUSIVE (a local solution everywhere does not give a global one)."""
    tried = []
    for m in moduli:
        tried.append(m)
        if m ** nvars > 3_000_000:
            continue
        if not any(f(*t) % m == 0 for t in itertools.product(range(m), repeat=nvars)):
            return verified("modular_obstruction", "f = 0 has no integer solutions",
                            f"no solution of f = 0 (mod {m}) among all {m ** nvars} residue tuples",
                            detail="a modular obstruction is a proof of non-existence over Z")
    return inconclusive("modular_obstruction", "f = 0 has no integer solutions",
                        f"no obstruction modulo {tried}; Hasse principle can fail, so this does not decide")


def check_lucas_binomial(n: int, k: int, p: int, claimed: int | None = None) -> Result:
    """C(n,k) mod p by Lucas' theorem, compared with direct computation (and an optional claim)."""
    if not isprime(p):
        return inconclusive("check_lucas_binomial", f"C({n},{k}) mod {p}", "Lucas needs a prime modulus")
    direct = math.comb(n, k) % p
    res, nn, kk = 1, n, k
    while nn or kk:
        res = res * math.comb(nn % p, kk % p) % p
        nn //= p
        kk //= p
    claim = f"C({n},{k}) = {claimed if claimed is not None else direct} (mod {p})"
    if res != direct:
        return refuted("check_lucas_binomial", claim, {"lucas": res, "direct": direct}, detail="internal inconsistency")
    if claimed is not None and claimed % p != direct:
        return refuted("check_lucas_binomial", claim, {"true_value": direct})
    return verified("check_lucas_binomial", claim, "exact; Lucas and direct computation agree")


def check_wilson_fermat(n: int) -> Result:
    """Primality via Wilson ((n-1)! = -1 mod n) and the Fermat pseudoprime trap (Carmichael numbers)."""
    wilson = (math.factorial(n - 1) + 1) % n == 0 if n > 1 else False
    prime = bool(isprime(n))
    fermat_all = n > 2 and all(pow(a, n - 1, n) == 1 for a in range(2, n) if math.gcd(a, n) == 1) if n < 10 ** 5 else None
    claim = f"{n}: Wilson <=> prime"
    if wilson != prime:
        return refuted("check_wilson_fermat", claim, {"wilson": wilson, "isprime": prime})
    note = ""
    if fermat_all and not prime:
        note = f"{n} is a Carmichael number: passes the Fermat test for every coprime base but is composite."
    return verified("check_wilson_fermat", claim, "exact (Wilson's theorem is an iff)", detail=note)


# --------------------------------------------------------------------------
# convenience: finite statements that ARE complete
# --------------------------------------------------------------------------
def divisors_with(n: int, pred: Callable[[int], bool]) -> list[int]:
    return [d for d in divisors(n) if pred(d)]


def traps() -> str:
    return ("Finite-check traps: n^2+n+41 prime for n=0..39 (fails at 40); Mertens |M(n)|<sqrt(n) true to 1e16, false; "
            "Fermat primes 2^(2^k)+1 prime only for k<=4; pi(x)<li(x) fails near 1.4e316; 561 passes the Fermat test for every coprime base.")
