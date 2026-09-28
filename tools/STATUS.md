# PhysicsForge tools — implementation status

Real, tool-backed implementations of pieces of the PhysicsForge protocols,
built following `idea-to-production-tool`'s discipline: prototype the highest-
leverage insight, validate on real data (not toy examples), mine prior art
before writing anything, evaluate honestly, retract what doesn't replicate.

This is **not** "PhysicsForge is now agentic." It's the specific, narrow set
of claims that are mechanically checkable, now actually checked by code
instead of asserted in prose. The judgment-heavy protocols (Pauli reasoning
itself, ScholarEval, adversarial review, Discovery Engine) are not being
converted to hard automation — see "What stays prompt-only" below, and why.

---

## Tool 1 — `citation_guard.py`

Implements `references/citation-guard.md`'s verdict taxonomy (`VERIFIED` /
`VERIFIED_DRIFT` / `VERIFIED_RETRACTED` / `NOT_FOUND` / `AMBIGUOUS` /
`UNVERIFIABLE`). Delegates retraction/correction/expression-of-concern
detection to [`citeguard`](https://github.com/wedo911/citeguard) (existing,
MIT, 72 tests against real Crossref fixtures — not reinvented) and adds DOI
metadata-drift checking plus full arXiv support, which that library doesn't
cover.

**Validated**: 13/13 on a golden set built from DOIs/arXiv IDs already
independently verified or refuted earlier in this project's own session (real
clean citations, real retracted ones, deliberately mis-stated metadata,
fabricated identifiers). One real bug caught and fixed in the process (an
`http`→`https` redirect silently misclassifying a real paper as not-found).

**Not built yet**: retry/resilience, caching, packaging, CI wiring, fuzzy
title-search for identifier-less citations (`AMBIGUOUS`). See inline
comments; not hidden.

**From researching `gallantlab/literature-review-toolkit`** (a close relative
of what this tool does): they found search agents get roughly 1 in 4
citations wrong without verification — the concrete stat this whole exercise
is protecting against — and additionally verify against PubMed/PMC/DataCite
and do citation-count cross-checks via OpenAlex/Semantic Scholar. DataCite
(for dataset/software citations) and an `.xlsx` report option are reasonable
next extensions; not built yet.

## Tool 2 — `deriv_check.py`

Implements `verification.md` Patterns 1 (dimensional analysis) and 2/7
(limiting cases / recovering known formulas), using `sympy.physics.units`'s
real `DimensionSystem` rather than hand-rolled unit bookkeeping.

**Validated against six real claims from this project's own manuscripts**,
not toy examples:

| # | Claim | Source | Result |
|---|---|---|---|
| 1 | $T_c$ is exactly linear in $\omega_{\log}$ at fixed $\lambda,\mu^*$ | Superconductivity v4 | PASS (exact symbolic reduction, not a numeric spot-check) |
| 2 | $C(1.5, 0.13) = 1.335701$ K/meV as printed | Superconductivity v4 | PASS |
| 3 | Biaxial→hydrostatic factor is exactly 2/3 | Superconductivity v4, Ch.6 | PASS (exact symbolic) |
| 4 | $Y/(1-\nu)\cdot\Delta a/a = 40$ GPa at stated inputs | Superconductivity v4, Ch.6 | PASS |
| 5 | $[W]=[R][T]$ for $W=RT\ln(1/x)$ | Carbon Capture v2 | PASS (real dimensional check) |
| 6 | The **withdrawn** claim: $0.18\lambda\langle\omega\rangle=300$ K at $\lambda=4.5,\langle\omega\rangle=400$ meV | Earliest carbon-capture draft | **FAIL, correctly** — computes 3759.86 K, matching the by-hand derivation earlier in this session exactly |

Two real bugs were caught and fixed while building this, not swept under the
rug: a `sympy.physics.units` API misuse (`u.energy` is already a `Dimension`
object, not something with a `.dimension` attribute), and a spurious extra
`/1000` in a hand-typed CODATA constant that initially made claim 2 fail for
the wrong reason. Both are documented in the commit/session history, not
just silently patched.

## Tool 3 — `quantum_check.py`

QuTiP-backed checks for unitarity, CPTP (complete positivity + trace
preservation), and entanglement measures.

**No quantum-information paper exists yet in this project**, so this is
**calibration against canonical, textbook-established facts** (CHSH/Tsirelson
bound, Bell-state entanglement entropy, the depolarizing channel's CPTP
property), not validation against our own messy data. That distinction is
kept visible deliberately — calibration and validation are not the same
evidentiary strength (Pólya Pattern 2, `plausible-reasoning.md`). A
deliberately incomplete Kraus set was included to confirm the tool can
actually fail, not just rubber-stamp: it failed by exactly the expected
magnitude (the missing term's own weight, 0.15 = p/4 at p=0.3).

---

## Pauli Protocol — which checks are now tool-backed

Honest status, since the user asked directly. The Pauli Protocol has seven
checks; here is what actually calls code today versus what is still, and will
likely remain, the model's own reasoning:

| # | Check | Status |
|---|---|---|
| [1] Falsifiability | Prompt-only. Judgment call about what a measurement would look like; not mechanically checkable. |
| [2] Restatement-vs-solution | Prompt-only. Requires understanding what was actually asked. |
| [3] Hidden assumption audit | Prompt-only, but `counterexample-protocol.md`'s lemma-incorporation step is a structured way to *find* one after the fact. |
| [4] Conservation/symmetry laws | Partially tool-backed for specific cases — `quantum_check.py` can verify unitarity/CPTP (a conservation-adjacent property) numerically; general symmetry reasoning is not automatable in general. |
| [5] Dimensional consistency | **Tool-backed.** `deriv_check.py`, real `sympy.physics.units`. |
| [6] Limiting case recovery | **Tool-backed** for exact/symbolic reductions and stated numeric targets. `deriv_check.py`. |
| [7] Peer-review survival | Prompt-only, and arguably should stay that way — this is `breakthrough-red-flags.md` and `scholar-eval.md` territory, judgment about a social process, not a mechanical fact. |

**Two of seven** are now genuinely tool-backed rather than self-reported; one
more is partially covered in the quantum-mechanics case. The other four are
judgment calls by nature, not gaps left unfilled by laziness — see "what
stays prompt-only" below for why that's the right line, not a shortcut.

---

## Researched, not built — with honest reasoning for each

### Open-source CAS landscape beyond sympy
- **SymEngine** — installed successfully (`pip install symengine`, real C++
  speed backend for sympy). Not currently needed: correctness, not speed, is
  our bottleneck, and every check above ran in well under a second on plain
  sympy.
- **Cadabra2** (tensor/Grassmann algebra, purpose-built for GR/QFT — would be
  a better fit than `sympy.diffgeom` for genuinely verifying the Kerr paper's
  tensor identities) — **not installable**: no PyPI wheel exists for this
  platform at all (`pip install cadabra2` returns "no matching distribution").
  It ships primarily via conda or Linux binaries. Real negative result, not
  chased further given this session's repeated first-hand experience of how
  costly toolchain installs get on this platform.
- **EinsteinPy** (pure-Python GR tensor calculus, directly relevant to the
  Kerr geodesics paper) — install attempted, in progress; report pending.
- **SageMath, Maxima, GAP** — researched, not attempted. SageMath in
  particular is known to be very difficult to install natively on Windows
  without WSL; given this session's own LaTeX-toolchain saga, installing it
  speculatively (with no specific claim queued up to validate against it yet)
  would be exactly the "build the complex version before a simple baseline
  failed a measured test" red flag this discipline warns against. Revisit if
  a specific need arises (e.g. GAP for a group-theory-heavy derivation).

### Lean 4 / `physlib` (formerly HepLean + Lean-QuantumInfo)
Real, active, community-run (`leanprover-community/physlib`) formalization
covering classical mechanics, GR, condensed matter, QFT, and **over a
thousand** quantum-information theorems. This is a genuinely stronger
guardrail than sympy for the narrow cases where a derivation reduces to a
pure algebraic identity — sympy's `simplify()` is a trusted heuristic, not a
proof; Lean's kernel is. Not installed or attempted this round: the Lean
toolchain (`elan`/`lake`) needs setting up from scratch here, and this
session has first-hand, repeated evidence that toolchain installs on this
machine are slow and failure-prone (the LaTeX/biber saga earlier ran over an
hour). Installing it speculatively, with no specific lemma queued, would
repeat that risk for no validated payoff yet.

**Concrete proposed first target, if/when this is worth doing**: the
superconductivity paper's exact-linearity claim ($T_c$ linear in
$\omega_{\log}$ at fixed $\lambda,\mu^*$) is a pure algebraic fact with no
physics semantics required to state — the smallest possible first Lean lemma,
already proven via `deriv_check.py`'s symbolic route above. Formalizing that
one claim would be a real, bounded pilot before deciding whether the
toolchain cost is worth paying for more.

### K-Dense (`K-Dense-AI` on GitHub) — the most valuable single finding
`science-superpowers`' methodology replaces **detecting** bad practice after
the fact with **preventing** it structurally: predictions, hypotheses, and
decision rules are locked *before* results are seen ("pre-registration over
TDD"), and `prereg.sh` is described as "a zero-dependency freeze/audit script
that proves from git history alone that predictions preceded outputs."

This is a different *kind* of guardrail than anything else here. Every tool
in this directory, and `anti-fabrication.md` itself, catches bad results
*after* they're produced. Pre-registration prevents the specific failure mode
`anti-fabrication.md` Mode 2 (Parameter Adjustment) exists to catch, by making
it structurally visible in git history if a prediction was written down after
the fact rather than before. **This is the strongest candidate for what to
build next** — stronger than another verification library, because it's
architecturally different from everything built so far, not just more
coverage of the same kind.

`scientific-agent-skills` also confirmed something useful in the negative:
its 165 skills cover citation/literature management and domain databases
(chemistry, biology, medicine) extensively, but explicitly do **not**
overlap with derivation-rigor or claim-verification territory — confirming
PhysicsForge and K-Dense's skill sets are complementary, not duplicative,
exactly as `SKILL.md`'s existing "from K-Dense" attribution implied.

---

## What stays prompt-only, and why that's not a gap

Falsifiability, restatement-checking, and peer-review-survival judgment
cannot be reduced to a deterministic check without losing what makes them
useful — they require understanding *meaning*, not just *form*. The right
lever for that category was already identified in `plausible-reasoning.md`
and `breakthrough-red-flags.md`: a fixed golden set of test papers with known
flaws, re-run when the skill file changes, to catch regressions — not a
guardrail. That eval suite does not exist yet; it is the next major piece
after pre-registration, not before it.
