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

A property of ONE explicit floating-point object (is this numeric matrix
unitary, is this state entangled) is decided at the tolerance stated in
`evidence`, with the margin shown; see pfv.quantum.

Inexact numbers (Python floats, sympy Floats) follow one rule everywhere, via
`to_exact`, `compare_claimed` and `cap_inexact` below:

    * They are read exactly as written (0.3333333333 is 3333333333/10^10) and
      NEVER snapped to a nearby simple rational. nsimplify would turn it into
      1/3 and let a false claim be VERIFIED.
    * A claimed VALUE given as a float is compared with the exact truth: exact
      equality is VERIFIED, agreement within tolerance is CONSISTENT, and a gap
      beyond tolerance is REFUTED (float representation error is ~1e-16, so a
      larger gap is real).
    * INPUT data given as floats cannot support a proof about the numbers they
      approximate: VERIFIED is capped at CONSISTENT, and a REFUTED witness is
      kept with a caveat that it holds for the decimals as written.

Strings are what the user wrote: "0.5" in a claim string is the exact decimal.
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
        return console_safe("\n".join(lines))


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
    return console_safe("\n".join(out))


_ASCII = str.maketrans({"═": "=", "─": "-", "✓": "+", "✗": "x", "≥": ">=", "≤": "<=", "≠": "!=", "→": "->",
                        "−": "-", "·": "*", "…": "...", "×": "x", "√": "sqrt"})


def console_safe(text: str) -> str:
    """`text` unchanged if sys.stdout can encode it, else with the report symbols spelled in ASCII.

    A Windows console or pipe often uses cp1252, which has no box-drawing or check-mark characters; printing a report
    there raised UnicodeEncodeError. Anything still unencodable becomes '?' rather than crashing the caller."""
    import sys
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        text.encode(enc)
        return text
    except UnicodeEncodeError:
        return text.translate(_ASCII).encode(enc, "replace").decode(enc)
    except LookupError:
        return text.translate(_ASCII).encode("ascii", "replace").decode("ascii")


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
    """Raise CheckTimeout after `seconds` in the main thread, on every platform.

    Unix uses SIGALRM. Windows has no SIGALRM, so a timer thread calls _thread.interrupt_main(), which raises
    KeyboardInterrupt at the next bytecode boundary; sympy is pure Python, so a long simplify/integrate is interrupted.
    A KeyboardInterrupt that the timer did not cause (a real Ctrl-C) is re-raised unchanged. Outside the main thread
    this is a no-op, as no portable mechanism can interrupt another thread."""
    import threading
    if threading.current_thread() is not threading.main_thread():
        yield
        return
    if hasattr(signal, "SIGALRM"):
        def _handler(signum, frame):
            raise CheckTimeout(f"timed out after {seconds}s")
        old = signal.signal(signal.SIGALRM, _handler)
        signal.setitimer(signal.ITIMER_REAL, seconds)
        try:
            yield
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, old)
        return
    import _thread
    fired = threading.Event()

    def _fire():
        fired.set()
        _thread.interrupt_main()

    timer = threading.Timer(seconds, _fire)
    timer.daemon = True
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        if fired.is_set():
            raise CheckTimeout(f"timed out after {seconds}s") from None
        raise
    finally:
        timer.cancel()
        if fired.is_set():
            # the timer fired after the body finished: absorb its pending interrupt here, not in the caller
            try:
                for _ in range(1000):
                    pass
            except KeyboardInterrupt:
                pass


def to_exact(x):
    """(exact sympy value of x as written, inexact) -- see the module docstring for the rule.

    int / Fraction / sympy Rational / exact sympy expression -> unchanged, inexact=False.
    str -> sympify with rational=True (the decimals as typed), inexact=False.
    Python float -> its shortest round-trip decimal (repr), so 0.1 -> 1/10 and 0.3333333333 -> 3333333333/10^10.
    sympy Float atoms inside an expression -> their printed decimal digits. Both set inexact=True."""
    import math
    import sympy as sp
    from fractions import Fraction
    if type(x).__module__ == "numpy" and hasattr(x, "item"):
        x = x.item()
    if isinstance(x, bool):
        return sp.Integer(int(x)), False
    if isinstance(x, Fraction):
        return sp.Rational(x.numerator, x.denominator), False
    if isinstance(x, int):
        return sp.Integer(x), False
    if isinstance(x, float):
        if math.isnan(x):
            return sp.nan, True
        if math.isinf(x):
            return (sp.oo if x > 0 else -sp.oo), True
        return sp.Rational(repr(x)), True
    if isinstance(x, complex):
        re, _ = to_exact(x.real)
        im, _ = to_exact(x.imag)
        return re + sp.I * im, True
    if isinstance(x, str):
        return sp.sympify(x, rational=True), False
    e = sp.sympify(x)
    floats = e.atoms(sp.Float)
    if not floats:
        return e, False
    return e.xreplace({f: sp.Rational(str(f)) if f.is_finite else f for f in floats}), True


def _is_zero(d):
    """True / False / None for an exact sympy expression d. simplify() is a heuristic, so a symbolic d that does not
    simplify to 0 is sampled at rational points before it is declared nonzero (the simplify-as-zero-test trap)."""
    import sympy as sp
    d = sp.sympify(d)
    if d == 0:
        return True
    try:
        ds = sp.simplify(d)
    except Exception:
        ds = d
    if ds == 0:
        return True
    eq = ds.equals(0)
    if eq is not None:
        return eq
    if ds.is_number:
        v = sp.N(ds, 60)
        return None if v == 0 or abs(v) < sp.Float("1e-50") else False
    syms = sorted(ds.free_symbols, key=lambda s: s.name)
    for pt in rational_points(syms, n=6, signed=True):
        try:
            v = sp.N(ds.subs(pt), 60)
        except Exception:
            continue
        if v.is_finite and v.is_real is not False and abs(v) > sp.Float("1e-40"):
            return False
    return None


def compare_claimed(truth, claimed, tol: float = TOL, truth_inexact: bool = False):
    """Compare `truth` with a `claimed` value. Returns (status, claimed_exact, inexact) where status is
    "equal" (exactly), "approx" (one side is a float and they agree within tol relative to |truth|, not exact),
    "differ" (decidably different) or "unknown" (equality could not be decided). Pass truth_inexact=True when `truth`
    itself came from floating-point computation."""
    import sympy as sp
    c, inexact = to_exact(claimed)
    t = sp.sympify(truth)
    z = _is_zero(t - c)
    if z is True:
        return "equal", c, inexact
    if (inexact or truth_inexact) and (t - c).is_number:
        gap = abs(sp.N(t - c, 30))
        if gap <= tol * max(1, abs(sp.N(t, 30))):
            return "approx", c, inexact
    if z is False:
        return "differ", c, inexact
    return "unknown", c, inexact


def cap_inexact(result: Result, what: str = "input") -> Result:
    """Apply the inexact-input rule: VERIFIED becomes CONSISTENT; any other verdict keeps a caveat."""
    note = (f"the {what} contained floating-point numbers, read exactly as written; a decisive result about "
            f"approximate numbers is not a result about the exact values they stand for (pass Rationals or strings)")
    if result.verdict == VERIFIED:
        result.verdict = CONSISTENT
    result.caveat = f"{result.caveat}; {note}" if result.caveat else note
    return result


def claimed_value_result(check, claim, truth, claimed, evidence, tol: float = TOL, truth_inexact: bool = False, **data) -> Result:
    """Standard verdict for "the value is `truth`; someone claimed `claimed`"."""
    status, c, inexact = compare_claimed(truth, claimed, tol, truth_inexact)
    if status == "equal":
        return verified(check, claim, evidence, **data)
    if status == "approx":
        return consistent(check, claim, evidence + f"; the claimed decimal agrees with the exact value {truth} to within {tol:g}",
                          caveat="the claimed value is a decimal approximation, not the exact value", **data)
    if status == "differ":
        return refuted(check, claim, {"exact": str(truth), "claimed": str(c)}, evidence=evidence, **data)
    return inconclusive(check, claim, f"could not decide whether {truth} equals the claimed {c}", **data)


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
