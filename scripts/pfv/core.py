"""pfv.core: result type, verdict vocabulary and report formatting.

Verdict vocabulary (the only four values any check may return):

    REFUTED       A concrete witness shows the claim is false. The witness is
                  reproducible and was re-checked with exact (integer, rational,
                  symbolic) or high-precision arithmetic. This is decisive.
    VERIFIED      The claim is established by the check itself: an exact
                  symbolic identity, or an exhaustive check over a FINITE claim
                  (for example all triples of a Cayley table). Decisive.
    CONSISTENT    The claim passed on the sample, range or tolerance stated in
                  `evidence`. It is NOT a proof. A universal claim checked on a
                  finite range, or a numerical identity at random points, lands
                  here. Never promote a CONSISTENT result to "Theorem".
    INCONCLUSIVE  The tool could not decide (timeout, unsupported input,
                  sympy returned unknown). Say so; do not guess.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

REFUTED = "REFUTED"
VERIFIED = "VERIFIED"
CONSISTENT = "CONSISTENT"
INCONCLUSIVE = "INCONCLUSIVE"
VERDICTS = (REFUTED, VERIFIED, CONSISTENT, INCONCLUSIVE)

# Default numerical tolerance for floating-point residuals (see references/verification-tools.md).
TOL = 1e-9


@dataclass
class Result:
    check: str
    claim: str
    verdict: str
    evidence: str = ""
    detail: str = ""
    witness: Any = None
    caveat: str = ""
    data: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.verdict not in VERDICTS:
            raise ValueError(f"bad verdict {self.verdict!r}")

    # convenience predicates -------------------------------------------------
    @property
    def refuted(self) -> bool:
        return self.verdict == REFUTED

    @property
    def verified(self) -> bool:
        return self.verdict == VERIFIED

    @property
    def consistent(self) -> bool:
        """True if the claim survived the check (VERIFIED or CONSISTENT)."""
        return self.verdict in (VERIFIED, CONSISTENT)

    @property
    def decisive(self) -> bool:
        return self.verdict in (REFUTED, VERIFIED)

    def __bool__(self) -> bool:  # `if result:` means "claim survived"
        return self.consistent

    def __str__(self) -> str:
        sym = {REFUTED: "✗", VERIFIED: "✓", CONSISTENT: "~", INCONCLUSIVE: "?"}[self.verdict]
        lines = [f"{sym} [{self.verdict}] {self.check}: {self.claim}"]
        if self.evidence:
            lines.append(f"    evidence: {self.evidence}")
        if self.detail:
            lines.append(f"    detail:   {self.detail}")
        if self.witness is not None:
            lines.append(f"    witness:  {self.witness}")
        if self.caveat:
            lines.append(f"    caveat:   {self.caveat}")
        return "\n".join(lines)


def refuted(check, claim, witness, detail="", evidence="concrete witness (reproducible)", **data) -> Result:
    return Result(check, claim, REFUTED, evidence, detail, witness, data=data)


def verified(check, claim, evidence, detail="", **data) -> Result:
    return Result(check, claim, VERIFIED, evidence, detail, data=data)


def consistent(check, claim, evidence, caveat="Not a proof.", detail="", **data) -> Result:
    return Result(check, claim, CONSISTENT, evidence, detail, caveat=caveat, data=data)


def inconclusive(check, claim, detail, **data) -> Result:
    return Result(check, claim, INCONCLUSIVE, "", detail, data=data)


def overall(results: Iterable[Result]) -> str:
    """REFUTED if any check refuted; else INCONCLUSIVE if any is; else CONSISTENT/VERIFIED."""
    rs = list(results)
    if any(r.verdict == REFUTED for r in rs):
        return REFUTED
    if any(r.verdict == INCONCLUSIVE for r in rs):
        return INCONCLUSIVE
    if rs and all(r.verdict == VERIFIED for r in rs):
        return VERIFIED
    return CONSISTENT


def report(results: Iterable[Result], target: str = "") -> str:
    """Render the verification block used in PhysicsForge answers.

    Paste the output verbatim into the answer. It always states what was NOT
    proven, so a finite check is never mistaken for a proof.
    """
    rs = list(results)
    bar = "═══════════ SYMBOLIC VERIFICATION ═══════════"
    out = [bar]
    if target:
        out.append(f"Target:    {target}")
    out.append("Tool used: pfv (python " + _pyver() + ")")
    out.append("")
    out.append("Checks:")
    for r in rs:
        out.append("  " + str(r).replace("\n", "\n  "))
    out.append("")
    v = overall(rs)
    out.append(f"Verdict:   {v}")
    weak = [r for r in rs if r.verdict == CONSISTENT]
    if weak:
        out.append("Not proven: " + "; ".join(f"{r.check} ({r.evidence})" for r in weak))
    out.append("═" * len(bar))
    return "\n".join(out)


def _pyver() -> str:
    import sys
    return ".".join(map(str, sys.version_info[:3]))


def rand_points(symbols, n=12, lo=0.3, hi=3.0, seed=12345, positive=True):
    """Deterministic random assignments {symbol: float} for numeric spot checks."""
    import random
    rng = random.Random(seed)
    pts = []
    for _ in range(n):
        pt = {}
        for s in symbols:
            v = rng.uniform(lo, hi)
            if not positive and rng.random() < 0.5:
                v = -v
            pt[s] = v
        pts.append(pt)
    return pts


# --------------------------------------------------------------------------
# helpers shared by the modules
# --------------------------------------------------------------------------
import contextlib
import signal


class CheckTimeout(Exception):
    pass


@contextlib.contextmanager
def timeout(seconds: float):
    """Raise CheckTimeout after `seconds` (Unix main thread only; elsewhere it is a no-op)."""
    def _handler(signum, frame):
        raise CheckTimeout(f"timed out after {seconds}s")
    try:
        old = signal.signal(signal.SIGALRM, _handler)
    except (ValueError, AttributeError):  # not main thread / not Unix
        yield
        return
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def rational_points(symbols, n=10, lo=1, hi=30, denom=7, seed=2024, signed=False):
    """Deterministic RATIONAL sample points {symbol: Rational}. Rational inputs keep high-precision evaluation honest."""
    import random
    from sympy import Rational
    rng = random.Random(seed)
    pts = []
    for _ in range(n):
        pt = {}
        for s in symbols:
            v = Rational(rng.randint(lo, hi), denom)
            if signed and rng.random() < 0.5:
                v = -v
            pt[s] = v
        pts.append(pt)
    return pts


def unify(*exprs):
    """Return the expressions with every set of same-NAME symbols merged into one symbol (the one with the most assumptions).

    sympy treats Symbol('x') and Symbol('x', positive=True) as DIFFERENT symbols, so a formula typed as a string and a
    metric built with positive symbols silently fail to cancel. Call this before comparing expressions from two sources."""
    import sympy as sp
    exprs = [sp.sympify(e) if not isinstance(e, (list, tuple)) else e for e in exprs]
    flat = []
    for e in exprs:
        flat.extend(e if isinstance(e, (list, tuple)) else [e])
    by_name = {}
    for e in flat:
        for s in sp.sympify(e).free_symbols:
            by_name.setdefault(s.name, set()).add(s)
    rep = {}
    for name, syms in by_name.items():
        if len(syms) > 1:
            best = max(syms, key=lambda s: len([k for k, v in s.assumptions0.items() if v is True]))
            for s in syms:
                if s != best:
                    rep[s] = best
    if not rep:
        return exprs if len(exprs) > 1 else exprs[0]
    out = [[sp.sympify(x).xreplace(rep) for x in e] if isinstance(e, (list, tuple)) else e.xreplace(rep) for e in exprs]
    return out if len(out) > 1 else out[0]


def unknown_symbols(claimed, *known) -> list:
    """Names of free symbols in `claimed` that appear in none of `known`. A typo such as `px` for `p_x` must produce
    INCONCLUSIVE ('unknown symbol'), never a false REFUTED."""
    import sympy as sp
    names = set()
    for k in known:
        items = k if isinstance(k, (list, tuple)) else [k]
        for e in items:
            names |= {s.name for s in sp.sympify(e).free_symbols}
    return sorted({s.name for s in sp.sympify(claimed).free_symbols} - names)
