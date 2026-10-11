"""pfv.groups: finite group theory checks on explicit Cayley tables.

A group is a square integer array T with T[a, b] = index of a*b. Elements are 0..n-1.
Everything here is exhaustive on the table, so a pass is a PROOF for that finite group
(VERIFIED), and a failure comes with the exact triple/pair that breaks the claim.

Pitfalls handled (each was a real failure mode):
  * sympy `PermutationGroup.is_isomorphic` can return False for isomorphic groups; `check_isomorphic`
    refutes only with an invariant that differs, and verifies only with an explicit map.
  * sympy composes permutations left-to-right (a*b = apply a, then b). `cayley_from_perm_group` uses that.
  * "Abelian" does not follow from "every element has order <= 2" being tested only on generators.
  * A Sylow count n_p is only constrained (n_p = 1 mod p, n_p | m), never determined, unless one value is left.
"""
from __future__ import annotations

import itertools
import math
from collections import Counter
from typing import Iterable, Sequence

import numpy as np
import sympy as sp
from sympy import factorint, divisors
from sympy.combinatorics import Permutation, PermutationGroup

from .core import Result, verified, consistent, inconclusive
from .core import refuted as _refuted
from functools import partial as _partial
refuted = _partial(_refuted, evidence='exact counterexample on the table')


# --------------------------------------------------------------------------
# constructing tables
# --------------------------------------------------------------------------
def cayley_from_perm_group(G: PermutationGroup):
    """(elements, T) for a sympy PermutationGroup; element 0 is the identity."""
    els = list(G.generate())
    ident = [i for i, e in enumerate(els) if e.is_Identity][0]
    els[0], els[ident] = els[ident], els[0]
    idx = {tuple(e.array_form): i for i, e in enumerate(els)}
    n = len(els)
    T = np.zeros((n, n), dtype=int)
    for i, a in enumerate(els):
        for j, b in enumerate(els):
            T[i, j] = idx[tuple((a * b).array_form)]
    return els, T


def table_from_op(elements: Sequence, op) -> np.ndarray:
    idx = {e: i for i, e in enumerate(elements)}
    n = len(elements)
    T = np.zeros((n, n), dtype=int)
    for i, a in enumerate(elements):
        for j, b in enumerate(elements):
            T[i, j] = idx[op(a, b)]
    return T


def cyclic(n: int) -> np.ndarray:
    return np.array([[(i + j) % n for j in range(n)] for i in range(n)])


def direct_product(T1, T2) -> np.ndarray:
    n1, n2 = len(T1), len(T2)
    T = np.zeros((n1 * n2, n1 * n2), dtype=int)
    for a, b, c, d in itertools.product(range(n1), range(n2), range(n1), range(n2)):
        T[a * n2 + b, c * n2 + d] = T1[a, c] * n2 + T2[b, d]
    return T


def dihedral(n: int) -> np.ndarray:
    """Order 2n. Element (k, s) = r^k s^s, composed as r^a s^e * r^b s^f = r^(a + (-1)^e b) s^(e+f)."""
    els = [(k, s) for s in (0, 1) for k in range(n)]
    def op(x, y):
        (a, e), (b, f) = x, y
        return ((a + (b if e == 0 else -b)) % n, (e + f) % 2)
    return table_from_op(els, op)


def symmetric(n: int):
    from sympy.combinatorics.named_groups import SymmetricGroup
    return cayley_from_perm_group(SymmetricGroup(n))


def alternating(n: int):
    from sympy.combinatorics.named_groups import AlternatingGroup
    return cayley_from_perm_group(AlternatingGroup(n))


def quaternion_group() -> np.ndarray:
    """Q8 = {1,-1,i,-i,j,-j,k,-k}."""
    names = ["1", "-1", "i", "-i", "j", "-j", "k", "-k"]
    base = {("i", "i"): "-1", ("j", "j"): "-1", ("k", "k"): "-1", ("i", "j"): "k", ("j", "k"): "i", ("k", "i"): "j",
            ("j", "i"): "-k", ("k", "j"): "-i", ("i", "k"): "-j"}
    def parse(x):
        return (-1 if x.startswith("-") else 1, x.lstrip("-"))
    def op(x, y):
        s1, a = parse(x)
        s2, b = parse(y)
        s = s1 * s2
        if a == "1":
            r = b
        elif b == "1":
            r = a
        else:
            q = base[(a, b)]
            s2_, r = parse(q)
            s *= s2_
        return ("-" if s < 0 else "") + r if r != "1" or s > 0 else "-1"
    return table_from_op(names, op)


def unit_group(n: int):
    """(Z/nZ)^x as (elements, table)."""
    els = [a for a in range(1, n) if math.gcd(a, n) == 1] or [0]
    return els, table_from_op(els, lambda a, b: (a * b) % n)


# --------------------------------------------------------------------------
# axioms
# --------------------------------------------------------------------------
def _identity(T):
    n = len(T)
    ar = np.arange(n)
    ids = [e for e in range(n) if (T[e] == ar).all() and (T[:, e] == ar).all()]
    return ids[0] if len(ids) == 1 else None


def inverse_table(T):
    T = np.asarray(T)
    e = _identity(T)
    if e is None:
        raise ValueError("table has no (unique) identity")
    inv = np.zeros(len(T), dtype=int)
    for a in range(len(T)):
        w = np.where(T[a] == e)[0]
        if len(w) != 1:
            raise ValueError(f"element {a} has no unique inverse")
        inv[a] = w[0]
    return inv, e


def check_group_axioms(T) -> Result:
    """Closure, associativity (all n^3 triples), identity, inverses. Returns the first violation as witness."""
    T = np.asarray(T)
    n = T.shape[0]
    claim = f"table of size {n} is a group"
    if T.ndim != 2 or T.shape[0] != T.shape[1]:
        return refuted("check_group_axioms", claim, T.shape, detail="not square")
    if T.min() < 0 or T.max() >= n:
        bad = np.argwhere((T < 0) | (T >= n))[0]
        return refuted("check_group_axioms", claim, tuple(bad), detail="closure fails: product outside the set")
    ar = np.arange(n)
    L = T[T[:, :, None], ar[None, None, :]]
    R = T[ar[:, None, None], T[None, :, :]]
    if not (L == R).all():
        a, b, c = np.argwhere(L != R)[0]
        return refuted("check_group_axioms", claim, (int(a), int(b), int(c)),
                       detail=f"associativity fails: ({a}*{b})*{c} = {L[a, b, c]} but {a}*({b}*{c}) = {R[a, b, c]}")
    e = _identity(T)
    if e is None:
        return refuted("check_group_axioms", claim, None, detail="no two-sided identity (or more than one)")
    for a in range(n):
        if not ((T[a] == e).any() and (T[:, a] == e).any()):
            return refuted("check_group_axioms", claim, a, detail=f"element {a} has no two-sided inverse")
    ab = bool((T == T.T).all())
    return verified("check_group_axioms", claim, f"all {n**3} associativity triples checked; identity {e}; all inverses exist",
                    detail="abelian" if ab else "non-abelian", abelian=ab, identity=int(e), order=n)


# --------------------------------------------------------------------------
# elements, subgroups, cosets
# --------------------------------------------------------------------------
def element_order(T, a: int) -> int:
    e = _identity(T)
    x, k = a, 1
    while x != e:
        x = T[x, a]
        k += 1
        if k > len(T) + 1:
            raise ValueError("not a group")
    return k


def element_orders(T) -> list[int]:
    return [element_order(T, a) for a in range(len(T))]


def check_element_order(T, a: int, claimed: int) -> Result:
    """Order of an element of a Cayley table against a claim."""
    o = element_order(T, a)
    claim = f"ord({a}) = {claimed}"
    if o == claimed:
        return verified("check_element_order", claim, "computed by repeated multiplication")
    return refuted("check_element_order", claim, {"true_order": o})


def subgroup_closure(T, gens: Iterable[int]) -> frozenset:
    e = _identity(T)
    S = {e} | set(int(g) for g in gens)
    frontier = list(S)
    while frontier:
        new = []
        for a in frontier:
            for b in list(S):
                for c in (int(T[a, b]), int(T[b, a])):
                    if c not in S:
                        S.add(c)
                        new.append(c)
        frontier = new
    return frozenset(S)


def all_subgroups(T, limit: int = 20000) -> set[frozenset]:
    n = len(T)
    subs = {subgroup_closure(T, [])}
    subs |= {subgroup_closure(T, [a]) for a in range(n)}
    changed = True
    while changed:
        changed = False
        for H in list(subs):
            for a in range(n):
                if a not in H:
                    K = subgroup_closure(T, list(H) + [a])
                    if K not in subs:
                        subs.add(K)
                        changed = True
                        if len(subs) > limit:
                            raise RuntimeError("too many subgroups")
    return subs


def check_subgroup(T, subset: Iterable[int]) -> Result:
    """Is `subset` a subgroup? Reports the failing product/inverse and Lagrange's theorem."""
    T = np.asarray(T)
    H = set(int(x) for x in subset)
    inv, e = inverse_table(T)
    claim = f"{sorted(H)} is a subgroup of a group of order {len(T)}"
    if not H or min(H) < 0 or max(H) >= len(T):
        return inconclusive("check_subgroup", claim, "subset is empty or contains indices outside 0..n-1")
    if e not in H:
        return refuted("check_subgroup", claim, e, detail="identity missing")
    for a in H:
        if int(inv[a]) not in H:
            return refuted("check_subgroup", claim, a, detail=f"inverse {inv[a]} of {a} missing")
        for b in H:
            if int(T[a, b]) not in H:
                return refuted("check_subgroup", claim, (a, b), detail=f"{a}*{b} = {T[a, b]} is outside the set")
    if len(T) % len(H):
        return refuted("check_subgroup", claim, len(H), detail="Lagrange violated; the table is not a group")
    return verified("check_subgroup", claim, f"closed, has identity and inverses; |H| = {len(H)} divides {len(T)}",
                    index=len(T) // len(H))


def check_normal(T, subset: Iterable[int]) -> Result:
    """Is the subset a normal subgroup? Reports the conjugate g h g^-1 that escapes."""
    T = np.asarray(T)
    H = set(int(x) for x in subset)
    inv, _ = inverse_table(T)
    claim = f"{sorted(H)} is normal"
    sub = check_subgroup(T, H)
    if sub.refuted:
        return sub
    for g in range(len(T)):
        for h in H:
            c = int(T[T[g, h], inv[g]])
            if c not in H:
                return refuted("check_normal", claim, (g, h), detail=f"g h g^-1 = {c} is outside H (g={g}, h={h})")
    return verified("check_normal", claim, "every conjugate of every element stays in H")


def quotient_table(T, subset: Iterable[int]):
    """Cayley table of G/N for a normal subgroup N (cosets ordered by smallest element)."""
    T = np.asarray(T)
    N = frozenset(int(x) for x in subset)
    r = check_normal(T, N)
    if r.refuted:
        raise ValueError("subgroup is not normal: " + r.detail)
    cosets = []
    seen = set()
    for a in range(len(T)):
        if a in seen:
            continue
        c = frozenset(int(T[a, h]) for h in N)
        cosets.append(c)
        seen |= c
    which = {x: i for i, c in enumerate(cosets) for x in c}
    k = len(cosets)
    Q = np.zeros((k, k), dtype=int)
    for i, ci in enumerate(cosets):
        for j, cj in enumerate(cosets):
            Q[i, j] = which[int(T[min(ci), min(cj)])]
    return cosets, Q


def conjugacy_classes(T) -> list[list[int]]:
    T = np.asarray(T)
    inv, _ = inverse_table(T)
    n = len(T)
    seen, classes = set(), []
    for a in range(n):
        if a in seen:
            continue
        c = frozenset(int(T[T[g, a], inv[g]]) for g in range(n))
        classes.append(sorted(c))
        seen |= c
    classes.sort(key=lambda c: (len(c), c))
    return classes


def center(T) -> list[int]:
    T = np.asarray(T)
    return [a for a in range(len(T)) if (T[a] == T[:, a]).all()]


def check_class_equation(T) -> Result:
    """|G| = |Z(G)| + sum of non-central class sizes, every class size divides |G|."""
    T = np.asarray(T)
    n = len(T)
    cl = conjugacy_classes(T)
    sizes = [len(c) for c in cl]
    Z = center(T)
    noncentral = [s for s in sizes if s > 1]
    claim = f"class equation: {n} = {len(Z)} + {noncentral}"
    if len(Z) + sum(noncentral) != n or any(n % s for s in sizes):
        return refuted("check_class_equation", claim, sizes)
    return verified("check_class_equation", claim, "computed from the table; each class size divides |G|",
                    class_sizes=sizes, center_size=len(Z))


# --------------------------------------------------------------------------
# homomorphisms and isomorphism
# --------------------------------------------------------------------------
def check_homomorphism(T1, T2, phi: Sequence[int]) -> Result:
    """phi: G1 -> G2 given as a list of images. Checks phi(ab) = phi(a)phi(b) for all pairs; reports kernel/image."""
    T1, T2 = np.asarray(T1), np.asarray(T2)
    phi = np.asarray(phi)
    n = len(T1)
    claim = "phi is a homomorphism"
    if len(phi) != n or phi.min() < 0 or phi.max() >= len(T2):
        return refuted("check_homomorphism", claim, None, detail="phi is not a well-defined map into G2")
    lhs = phi[T1]
    rhs = T2[phi[:, None], phi[None, :]]
    if not (lhs == rhs).all():
        a, b = np.argwhere(lhs != rhs)[0]
        return refuted("check_homomorphism", claim, (int(a), int(b)),
                       detail=f"phi({a}*{b}) = {lhs[a, b]} but phi({a})*phi({b}) = {rhs[a, b]}")
    e2 = _identity(T2)
    ker = [a for a in range(n) if phi[a] == e2]
    img = sorted(set(int(x) for x in phi))
    return verified("check_homomorphism", claim, f"all {n*n} pairs checked",
                    detail=f"|ker| = {len(ker)}, |im| = {len(img)}, |G1| = |ker||im| = {len(ker)*len(img)} "
                           f"(first isomorphism theorem {'holds' if n == len(ker) * len(img) else 'FAILS'})",
                    kernel=ker, image=img, injective=len(ker) == 1, surjective=len(img) == len(T2))


def group_invariants(T) -> dict:
    T = np.asarray(T)
    return {
        "order": len(T),
        "element_orders": tuple(sorted(Counter(element_orders(T)).items())),
        "abelian": bool((T == T.T).all()),
        "center_size": len(center(T)),
        "class_sizes": tuple(sorted(Counter(len(c) for c in conjugacy_classes(T)).items())),
        "n_subgroups_by_order": None,
    }


def _find_isomorphism(T1, T2):
    n = len(T1)
    o1, o2 = element_orders(T1), element_orders(T2)
    _, e1 = inverse_table(T1)
    _, e2 = inverse_table(T2)
    # greedy generating set of G1, largest-order first
    gens, cur = [], frozenset([e1])
    for a in sorted(range(n), key=lambda x: -o1[x]):
        if a not in cur:
            gens.append(a)
            cur = subgroup_closure(T1, gens)
            if len(cur) == n:
                break
    cands = [[b for b in range(n) if o2[b] == o1[g]] for g in gens]

    def extend(phi_gens):
        phi = {e1: e2}
        stack = [e1]
        # BFS: multiply known elements by generators
        known = {e1}
        order = [e1]
        while order:
            x = order.pop()
            for g, h in zip(gens, phi_gens):
                y = int(T1[x, g])
                v = int(T2[phi[x], h])
                if y in phi:
                    if phi[y] != v:
                        return None
                else:
                    phi[y] = v
                    order.append(y)
        if len(phi) != n or len(set(phi.values())) != n:
            return None
        return [phi[a] for a in range(n)]

    for choice in itertools.product(*cands):
        phi = extend(choice)
        if phi is not None and check_homomorphism(T1, T2, phi).verified:
            return phi
    return None


def check_isomorphic(T1, T2, claimed: bool | None = None) -> Result:
    """Are two finite groups isomorphic? REFUTED-iso needs an invariant that differs (exact);
    VERIFIED-iso comes with an explicit isomorphism that is re-checked on all pairs."""
    T1, T2 = np.asarray(T1), np.asarray(T2)
    claim = "groups are isomorphic" if claimed is None else f"groups are {'isomorphic' if claimed else 'NOT isomorphic'}"
    i1, i2 = group_invariants(T1), group_invariants(T2)
    for k in ("order", "element_orders", "abelian", "center_size", "class_sizes"):
        if i1[k] != i2[k]:
            detail = f"{k}: {i1[k]} vs {i2[k]} (an isomorphism preserves this, so the groups are NOT isomorphic)"
            if claimed is False:
                return verified("check_isomorphic", claim, f"invariant '{k}' differs", detail=detail)
            return refuted("check_isomorphic", claim, k, detail=detail)
    phi = _find_isomorphism(T1, T2)
    if phi is not None:
        if claimed is False:
            return refuted("check_isomorphic", claim, phi, detail="explicit isomorphism found and re-checked")
        return verified("check_isomorphic", claim, "explicit isomorphism found and re-checked on all pairs", iso=phi)
    return inconclusive("check_isomorphic", claim, "all invariants agree but no isomorphism was found by search")


# --------------------------------------------------------------------------
# abelian groups and structure
# --------------------------------------------------------------------------
def partitions_count(k: int) -> int:
    from sympy.utilities.iterables import partitions
    return sum(1 for _ in partitions(k))


def count_abelian_groups(n: int) -> int:
    """Number of abelian groups of order n up to isomorphism: product over p^e || n of p(e)."""
    c = 1
    for p, e in factorint(n).items():
        c *= partitions_count(e)
    return c


def check_abelian_count(n: int, claimed: int) -> Result:
    """Number of abelian groups of order n (product of partition numbers over prime-power exponents) against a claim."""
    true = count_abelian_groups(n)
    claim = f"{n} has {claimed} abelian groups of that order"
    if true == claimed:
        return verified("check_abelian_count", claim, "product of partition numbers over prime powers", factorization=factorint(n))
    return refuted("check_abelian_count", claim, {"true": true, "factorization": factorint(n)})


def check_cyclic(T, claimed: bool) -> Result:
    """Is the group cyclic (some element of order |G|)? Compared with the claim."""
    T = np.asarray(T)
    n = len(T)
    is_cyc = any(o == n for o in element_orders(T))
    claim = f"group of order {n} is {'' if claimed else 'not '}cyclic"
    if is_cyc == claimed:
        return verified("check_cyclic", claim, "searched all elements for one of order |G|")
    return refuted("check_cyclic", claim, {"cyclic": is_cyc})


# --------------------------------------------------------------------------
# Sylow
# --------------------------------------------------------------------------
def sylow_allowed(n: int, p: int) -> list[int]:
    m = n
    while m % p == 0:
        m //= p
    return [d for d in divisors(m) if d % p == 1 % p]


def check_sylow_count(T, p: int) -> Result:
    """Count Sylow p-subgroups of the actual group and compare with Sylow III constraints."""
    T = np.asarray(T)
    n = len(T)
    pe = 1
    while n % (pe * p) == 0:
        pe *= p
    subs = [H for H in all_subgroups(T) if len(H) == pe]
    allowed = sylow_allowed(n, p)
    claim = f"n_{p} of group of order {n}"
    if len(subs) not in allowed:
        return refuted("check_sylow_count", claim, len(subs), detail=f"count {len(subs)} violates Sylow III; allowed {allowed}")
    return verified("check_sylow_count", claim, f"found {len(subs)} Sylow {p}-subgroups of order {pe}; allowed by Sylow III: {allowed}",
                    count=len(subs))


def simplicity_by_sylow(n: int) -> Result:
    """Try to PROVE that no group of order n is simple, by Sylow counting. Never proves simplicity.

    In a simple group G of non-prime order n, for every prime p | n:
      (a) n_p > 1 and n_p = 1 (mod p), n_p | n/p^a   (Sylow III, plus no normal Sylow);
      (b) G embeds in A_{n_p} (action on Sylow p-subgroups), so n | n_p!/2;
      (c) if p || n, Sylow p-subgroups meet trivially, giving n_p (p-1) elements of order p;
          the elements of prime-power order for different primes are distinct, so
          1 + sum_{p || n} n_p (p-1) + sum_{q^e || n, e>=2} (q^e - 1) <= n,
          with equality forcing every non-exponent-1 Sylow to be normal.
    If no assignment of the n_p survives (a)-(c), no simple group of order n exists.
    """
    claim = f"no simple group of order {n}"
    f = factorint(n)
    if n == 1:
        return inconclusive("simplicity_by_sylow", claim, "trivial group")
    if len(f) == 1:
        p, e = next(iter(f.items()))
        if e == 1:
            return inconclusive("simplicity_by_sylow", claim, f"{n} is prime: Z_{n} IS simple")
        return verified("simplicity_by_sylow", claim, "a p-group of order p^k (k>=2) has a nontrivial centre, hence a proper normal subgroup")
    per_prime = {}
    for p in f:
        allowed = sylow_allowed(n, p)
        if allowed == [1]:
            return verified("simplicity_by_sylow", claim, f"n_{p} = 1 is forced, so the Sylow {p}-subgroup is a proper normal subgroup")
        feas = [k for k in allowed if k > 1 and (math.factorial(k) // 2) % n == 0]
        if not feas:
            return verified("simplicity_by_sylow", claim,
                            f"for p={p} every allowed n_p>1 in {allowed} fails n | n_p!/2 (no embedding into A_k)")
        per_prime[p] = feas
    primes = list(per_prime)
    survivors = []
    for combo in itertools.product(*[per_prime[p] for p in primes]):
        n_p = dict(zip(primes, combo))
        L = 1 + sum(n_p[p] * (p - 1) for p in primes if f[p] == 1) + sum(p ** f[p] - 1 for p in primes if f[p] > 1)
        has_big = any(f[p] > 1 for p in primes)
        if L > n or (L == n and has_big):
            continue
        survivors.append(n_p)
    if not survivors:
        return verified("simplicity_by_sylow", claim, "every admissible choice of (n_p) violates the element count or the A_k embedding",
                        detail=f"admissible n_p per prime: {per_prime}")
    return inconclusive("simplicity_by_sylow", claim,
                        f"Sylow counting leaves {len(survivors)} admissible assignments, e.g. {survivors[0]}; it cannot decide "
                        "(A_5 of order 60 is simple)")


# --------------------------------------------------------------------------
# Burnside counting, characters
# --------------------------------------------------------------------------
def burnside_orbits(gens: Sequence[Sequence[int]], n_points: int) -> int:
    """Number of orbits of <gens> on {0..n_points-1}, computed as the mean number of fixed points (Burnside)."""
    G = PermutationGroup([Permutation(list(g), size=n_points) for g in gens])
    els = list(G.generate())
    tot = sum(sum(1 for i in range(n_points) if e.array_form[i] == i) if e.size == n_points else 0 for e in els)
    return tot // len(els)


def check_burnside(gens: Sequence[Sequence[int]], n_points: int, claimed: int | None = None) -> Result:
    """Orbit count of a permutation group by Burnside's lemma, cross-checked by union-find, against a claim."""
    G = PermutationGroup([Permutation(list(g), size=n_points) for g in gens])
    els = list(G.generate())
    fixsum = sum(sum(1 for i in range(n_points) if e.array_form[i] == i) for e in els)
    # independent orbit count by union-find
    parent = list(range(n_points))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for g in gens:
        for i, j in enumerate(g):
            parent[find(i)] = find(j)
    orbits = len({find(i) for i in range(n_points)})
    claim = f"number of orbits = {claimed if claimed is not None else orbits}"
    if fixsum % len(els) or fixsum // len(els) != orbits:
        return refuted("check_burnside", claim, {"fixsum": fixsum, "|G|": len(els), "orbits": orbits}, detail="Burnside disagrees with union-find (bug)")
    if claimed is not None and claimed != orbits:
        return refuted("check_burnside", claim, {"true_orbits": orbits})
    return verified("check_burnside", claim, f"(1/{len(els)}) * {fixsum} = {orbits}; matches union-find orbit count")


def necklace_count(n: int, k: int, bracelets: bool = False) -> int:
    """Colourings of an n-cycle by k colours up to rotation (and reflection if bracelets), by Burnside."""
    rot = sum(k ** math.gcd(n, r) for r in range(n))
    if not bracelets:
        return rot // n
    refl = (n * k ** ((n + 1) // 2)) if n % 2 else (n // 2) * (k ** (n // 2 + 1) + k ** (n // 2))
    return (rot + refl) // (2 * n)


def character_table(T):
    """Burnside-Dixon: character table of a finite group from its Cayley table.
    Returns (classes, class_sizes, X) with X[i, j] = chi_i(class j); trivial character first. Numerical (complex)."""
    T = np.asarray(T)
    inv, e = inverse_table(T)
    n = len(T)
    cl = conjugacy_classes(T)
    r = len(cl)
    cls_of = {a: i for i, c in enumerate(cl) for a in c}
    sizes = np.array([len(c) for c in cl], dtype=float)
    a = np.zeros((r, r, r))
    for i in range(r):
        for j in range(r):
            for k in range(r):
                z = cl[k][0]
                a[i, j, k] = sum(1 for x in cl[i] if cls_of[int(T[inv[x], z])] == j)
    rng = np.random.default_rng(1)
    coef = rng.normal(size=r)
    A = sum(coef[j] * a[:, j, :] for j in range(r))
    vals, vecs = np.linalg.eig(A)
    e_cls = cls_of[e]
    chis = []
    for v in range(r):
        w = vecs[:, v] / vecs[e_cls, v]
        d2 = n / np.sum(np.abs(w) ** 2 / sizes)
        d = np.sqrt(d2.real)
        chis.append(d * w / sizes)
    X = np.array(chis)
    X = X[np.argsort(X[:, e_cls].real, kind="stable")]
    # put trivial character first among dimension-1 rows
    triv = [i for i in range(r) if np.allclose(X[i], 1)]
    if triv:
        order = [triv[0]] + [i for i in range(r) if i != triv[0]]
        X = X[order]
    return cl, sizes, X


def check_character_table(X, class_sizes, order: int, tol: float = 1e-8) -> Result:
    """Row orthogonality <chi_i,chi_j> = delta_ij, column orthogonality, sum d_i^2 = |G|, #irreps = #classes."""
    X = np.asarray(X, dtype=complex)
    sizes = np.asarray(class_sizes, dtype=float)
    r = len(sizes)
    claim = f"X is the character table of a group of order {order}"
    if X.shape != (r, r):
        return refuted("check_character_table", claim, X.shape, detail=f"need a square table with {r} rows (number of classes)")
    e_cls = int(np.argmax(sizes == 1)) if (sizes == 1).any() else 0
    dims = X[:, e_cls].real
    if abs(sum(dims ** 2) - order) > 1e-6:
        return refuted("check_character_table", claim, {"sum_d2": float(sum(dims ** 2))}, detail=f"sum of squared dimensions must be {order}")
    G = (X * sizes) @ X.conj().T / order
    if np.abs(G - np.eye(r)).max() > tol:
        i, j = np.unravel_index(np.abs(G - np.eye(r)).argmax(), G.shape)
        return refuted("check_character_table", claim, (int(i), int(j)), detail=f"row orthogonality fails: <chi_{i},chi_{j}> = {G[i, j]:.6g}")
    H = X.conj().T @ X
    target = np.diag(order / sizes)
    if np.abs(H - target).max() > tol * order:
        return refuted("check_character_table", claim, None, detail="column orthogonality fails")
    return verified("check_character_table", claim, "row and column orthogonality, sum d^2 = |G|, #irreps = #classes", dims=dims.tolist())


def check_burnside_lemma_on_table(T) -> Result:
    """Sanity: sum over irreps of d_i^2 = |G| and #irreps = #classes for the computed character table."""
    cl, sizes, X = character_table(T)
    return check_character_table(X, sizes, len(T))
