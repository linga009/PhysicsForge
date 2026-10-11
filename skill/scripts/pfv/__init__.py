"""pfv: PhysicsForge verification toolkit.

    import sys; sys.path.insert(0, "<skill>/scripts")
    from pfv import numtheory, groups, lie, quantum, linalg, analysis, derivation, dimensions, geometry, mechanics, combinat
    from pfv import algebra, probability, qft, vectorcalc, smt
    from pfv.core import report

Every check returns a Result with one of four verdicts: REFUTED (exact witness, decisive), VERIFIED (exact or exhaustive),
CONSISTENT (passed a sample or tolerance, NOT a proof), INCONCLUSIVE. `report(results, target)` prints the verification block.

    python3 -m pfv list [domain]     menu of checks
    python3 -m pfv doc <check_name>  full docstring of one check
    python3 -m pfv selftest          planted-error test suite (every check must pass a true claim and fail a false one)
"""
from importlib import import_module

from .core import (REFUTED, VERIFIED, CONSISTENT, INCONCLUSIVE, Result, overall, report, unify)  # noqa: F401

DOMAINS = {
    "numtheory": "Number theory: primes, factorization, congruences, CRT, orders, LTE, Diophantine, Pell, EC point counts, Zsigmondy",
    "groups": "Group theory: Cayley-table axioms, subgroups, homomorphisms, isomorphism, Sylow, characters, Burnside",
    "lie": "Lie algebras and representations: algebra closure, Casimir, Weyl dimension (all types), anomalies, beta coefficients",
    "quantum": "Quantum mechanics and information: spin algebra, density matrices, channels (CPTP), PPT, uncertainty, perturbation theory",
    "linalg": "Linear algebra: exact rank/det/eigenvalues, definiteness, Cayley-Hamilton, matrix exponential identities",
    "analysis": "Analysis: identities, derivatives, integrals, sums, limits, series, convergence, inequalities, ODE/PDE, complex analysis, Fourier",
    "derivation": "Derivation checking: first wrong step in an equality chain or an equation-solving chain, extraneous roots",
    "dimensions": "Dimensional analysis: SI dimensions, natural units, Buckingham pi, Planck units",
    "geometry": "Geometry and gauge theory: Riemann/Ricci/Einstein, vacuum solutions, Killing vectors, Bianchi, Maxwell, Yang-Mills",
    "mechanics": "Mechanics and thermodynamics: Euler-Lagrange, Hamiltonian, canonical maps, Noether, extensivity, Kramers-Kronig",
    "combinat": "Combinatorics: known sequences, brute-force counts, generating functions, recurrences, spanning trees, colouring",
    "algebra": "Polynomials and algebraic numbers: identities, factorisation, irreducibility, real roots, minimal polynomials, Groebner ideal membership, discriminants",
    "probability": "Probability: exact enumeration, conditional probability, expectations, densities, Markov chains, Monte Carlo cross-checks",
    "qft": "Relativistic QFT algebra: Clifford algebra, gamma-matrix and trace identities (exact), Lorentz generators, Ward identity",
    "vectorcalc": "Vector calculus: grad/div/curl/Laplacian in Cartesian, cylindrical, spherical and custom coordinates, identities for all fields, flux and line integrals",
    "smt": "Decision procedures: real polynomial inequalities (z3 nlsat, complete), integer constraints, propositional logic",
}


def __getattr__(name):
    if name in DOMAINS:
        return import_module(f".{name}", __name__)
    raise AttributeError(name)


def _public(mod):
    import inspect
    out = []
    for n, f in inspect.getmembers(mod, inspect.isfunction):
        if n.startswith("_") or f.__module__ != mod.__name__:
            continue
        out.append((n, f))
    return out


def catalog(domain: str | None = None) -> str:
    import inspect
    lines = []
    for d, desc in DOMAINS.items():
        if domain and d != domain:
            continue
        mod = import_module(f".{d}", __name__)
        lines.append(f"\n[{d}] {desc}")
        for n, f in _public(mod):
            doc = (inspect.getdoc(f) or "").strip().splitlines()
            first = doc[0] if doc else ""
            sig = str(inspect.signature(f))
            sig = sig if len(sig) < 70 else sig[:67] + "..."
            lines.append(f"  {n}{sig}\n      {first[:110]}")
    return "\n".join(lines)


def n_checks() -> int:
    total = 0
    for d in DOMAINS:
        mod = import_module(f".{d}", __name__)
        total += sum(1 for n, _ in _public(mod) if n.startswith("check_") or n.startswith("hunt_"))
    return total
