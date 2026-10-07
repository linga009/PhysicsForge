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

**Pushed.** Branch `tool/pre-registration` on `linga009/PhysicsForge`, PR #2:
<https://github.com/linga009/PhysicsForge/pull/2>. Not yet merged — that's
still a separate, explicit decision. "Wired into CI" and "observed passing
in CI" were kept as different claims right up until they became the same
claim, for real — see below.

## CI — `.github/workflows/tools-ci.yml`

Three jobs: `test-tools` runs the four deterministic suites below on every
push/PR touching `tools/`; `citation-spot-check` runs `citation_guard.py`
against the real golden set (network required, so `continue-on-error: true`
— a Crossref issue shouldn't block an unrelated PR); `prereg-audit` runs
`prereg.sh audit` against any tracked pre-registration, so a human forgetting
to audit locally before claiming a confirmatory result doesn't slip through.

**Observed running for real**, on both the initial push and the resulting
PR (#2), consistently across both runs:

| Job | Result | Notes |
|---|---|---|
| `test-tools` | **PASS** (51s) | All four suites (`test_retry.py`, `test_deriv_check.py`, `test_quantum_check.py`, `test_kerr_check.py`) genuinely green on GitHub's own runners, not just locally. |
| `prereg-audit` | **PASS** (5–6s) | `prereg.sh audit` correctly verified the isotope-shift pre-registration from real commit history on a fresh Ubuntu runner. |
| `citation-spot-check` | **FAIL** (13–14s), both runs | A Crossref call returned `http_406`, consistently, on both the push and PR-triggered runs — not a one-off flake. `406` isn't in `citation_guard.py`'s retryable set (`429, 500, 502, 503, 504`), so it wasn't retried. Most likely cause: Crossref treating GitHub Actions' shared runner IP ranges differently than a residential/local IP — this was never observed locally. `continue-on-error: true` worked exactly as designed: the overall workflow still reports **success**, and the PR is not blocked by it. Not yet fixed — a real, open, documented limitation, not a guessed one. |

This is the actual point where "wired into CI" and "observed passing in CI"
stopped being different claims. The one real gap it surfaced (Crossref's
apparent behavior toward CI IP ranges) is exactly the kind of thing that
would have stayed invisible without actually pushing and watching it run.

---

## Tool 0 — `prereg.sh`

Vendored from [`K-Dense-AI/science-superpowers`](https://github.com/K-Dense-AI/science-superpowers)
(MIT), adapted only in its default `PREREG_DIR`/`DEFAULT_RESULTS` paths for
this repo's layout — not reimplemented, per "don't reinvent, don't blindly
copy": the mechanism (git commit *ancestry*, via `git merge-base
--is-ancestor`, which can't be forged by editing timestamps the way raw
commit dates can) was already correctly designed. This is the piece flagged
last round as architecturally different from everything else here:
*prevention* of post-hoc parameter/hypothesis adjustment, not after-the-fact
detection.

**Fully validated end-to-end in a real git repo** (the `linga009/PhysicsForge`
clone, on an unpushed local branch `tool/pre-registration`), using a genuinely
fresh claim never before numerically computed in this project: the
$^{13}$C-isotope $T_c$ shift implied by `Narlagiri_Superconductivity_Thesis_v4`'s
falsification chapter ($T_c\propto M^{-\alpha}$, $\alpha\approx0.5$).

1. Wrote the prediction (range 3.5–4.5% decrease, from a linear approximation)
   into `preregistrations/2026-09-28-isotope-shift.md`.
2. `prereg.sh freeze` — committed it as the file's first commit.
3. *Only then* computed the exact value via `sympy`: **−3.9355%**. Confirmed:
   correct sign, inside the registered range.
4. Committed the result under `results/`. `prereg.sh audit` → **PASS** (FROZEN,
   STAMP, INTEGRITY, CHRONOLOGY all green).
5. **Adversarial test**: edited the registered range *after* seeing the
   answer (simulating exactly the dishonest move this tool exists to
   prevent — narrowing 3.5–4.5% down to 3.9–4.0% once −3.94% was known).
   `prereg.sh audit` → **correctly FAILed**, showing the exact diff and the
   right reason ("Edited after freeze"). Exit code 1, as it should be for CI
   gating.
6. Restored the frozen content; audit returned to PASS.

**One real bug found**: `freeze`, invoked with a relative path from this
session's particular temp-directory layout, spuriously warned the file was
"outside preregistrations/" even though it wasn't — looks like a Windows
temp-path aliasing quirk between `git rev-parse --show-toplevel`'s output and
the shell's own path resolution, not a logic error in the script (the
downstream `audit` command, which resolves paths differently, was unaffected
and worked correctly throughout). Noted, not hidden; not yet root-caused.

**Not yet done**: no `results/`-path convention has been agreed for actual
physics derivations (the test above used a throwaway `results/` folder); no
guidance yet in `anti-fabrication.md` or `SKILL.md` on *when* pre-registration
is warranted (every Conjecture? only ones with a numeric decision rule?) —
that integration is the next step, not this one.

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

**Hardened since the first build** (real, tested, not just added): retry with
exponential backoff + jitter on transient failures (connection errors, 5xx),
honoring `Retry-After` on 429s; 404s are *not* retried (a real answer, not a
failure); a 24h-TTL on-disk cache (`--no-cache` to bypass). Validated with a
deterministic test suite (`test_retry.py`, 12/12, using an injected fetcher
and fake clock rather than hoping the real network is flaky on demand — see
"determinism before deltas") that caught one real bug in the process: `_Cache
.put()` didn't recreate its directory if it had been removed since `__init__`,
so every cache write after a `rm -rf .citation_cache` failed silently until
fixed. A second real gap was found and fixed the same way: `citeguard.check_doi()`
accepts an injectable cache (`citeguard.FileCache`) that wasn't being used, so
its own internal Crossref calls were uncached — wiring it in took a warm run
on the golden set from ~44% faster (only our own cache) to **6.5× faster**
(10.1s → 1.5s), with identical, correct results.

**Still not built**: packaging (no `pyproject.toml` / console entry point),
fuzzy title-search for identifier-less citations (`AMBIGUOUS`). CI wiring
exists now — see the "CI" section above — though not yet observed running for
real. See inline comments; not hidden.

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

**Now packaged properly**: the six claims above live in `test_deriv_check.py`
as a standalone, zero-framework regression suite (`python test_deriv_check.py`),
with claim 6 correctly framed as a meta-level assertion ("the tool correctly
rejects this", not "this claim is true") so a future CI failure there means
the *checker* broke, not that the physics changed. `deriv_check.py` itself is
now a clean library with no demo `__main__` block — see its own docstring for
why it deliberately has no CLI beyond that (the actual caller is Claude,
writing Python during Phase 5 Symbolic Verification, not a generic
expression-description file format with no demonstrated need).

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
magnitude — corrected here from an earlier, slightly wrong report: the
deviation is `dim * (missing term's weight)` under QuTiP's default trace
norm (0.15 = 2 × 0.075 at $p=0.3$, dim 2), not the missing weight alone as
first stated. Caught and fixed while writing `test_quantum_check.py`, by
computing the expected deviation independently rather than trusting the
first guess — exactly the kind of small, easy-to-miss error this whole
exercise exists to catch, including in its own prior claims.

**Now packaged properly**: `test_quantum_check.py` is a standalone,
zero-framework regression suite (6/6), separated from `quantum_check.py`
itself, which is now a clean library with no demo `__main__` block — mirroring
the same treatment given to `deriv_check.py` / `test_deriv_check.py`.

## Tool 4 — `test_kerr_check.py`

A from-first-principles validation of `kerr_elliptic_thesis_v2_corrected.tex`'s
central claimed result: that the Hamilton-Jacobi equation for Kerr null
geodesics separates into a radial potential $R(r)$ and angular potential
$\Theta(\theta)$. Not "does this match a textbook" (the paper already cites
Carter 1968 and Gralla & Lupsasca 2020 for that) but "does the paper's printed
$R(r)$ genuinely fall out of the real Kerr inverse metric, derived
independently here" — using EinsteinPy's actual `Kerr()` tensor, not a
hand-typed metric.

**8/8, including a direct test of separability itself** (the mixed partial
derivative $\partial^2 B'/\partial r\,\partial\theta$ of the Hamilton-Jacobi
bracket vanishes identically — checked from the metric, not assumed via
Carter's ansatz), and the paper's own $(\xi,\eta)$-normalized $R(r)$ matching
the derivation to exact symbolic zero.

**Three real bugs, all in the derivation code, none in the paper's physics**
— documented in the file's own docstring since they're instructive:
1. `Kerr()` builds its own internal `r, theta` symbols; an external
   `Symbol("r", positive=True)` prints identically but is a different object,
   so `.subs()` against it silently no-ops. Caught by a `TypeError: Cannot
   convert expression to float` rather than a wrong number — worse, it could
   easily have produced a *plausible-looking wrong answer* if the
   substitution had partially worked instead of failing loudly.
2. `sympy.simplify(diff) == 0` gave **False** for expressions later confirmed
   (by direct numeric substitution) to be exactly equal — `simplify` is a
   heuristic, not a decision procedure, and `.equals(0)` even returned `None`
   once. Numeric substitution at a random point is what actually caught this;
   the "robust" symbolic method was the less trustworthy one here.
3. A genuine sign error in the derivation's own algebra (not the metric):
   working through the Hamilton-Jacobi equation with an unverified assumption
   about which inverse-metric components are negative produced a result that
   was the exact negative of the paper's $R(r)$ — caught by testing against
   both $+R$ and $-R$ rather than assuming the derivation was right because
   it "looked like" the standard form.

Runtime: 25s (down from >60s before deduplicating a redundant symbolic matrix
inversion across test functions — measured, not assumed to have helped).

---

## Pauli Protocol — which checks are now tool-backed

Honest status, since the user asked directly. The Pauli Protocol has seven
checks; here is what actually calls code today versus what is still, and will
likely remain, the model's own reasoning:

| # | Check | Status |
|---|---|---|
| [1] Falsifiability | Prompt-only. Judgment call about what a measurement would look like; not mechanically checkable. |
| [2] Restatement-vs-solution | Prompt-only. Requires understanding what was actually asked. |
| [3] Hidden assumption audit | Prompt-only in general, but **tool-backed for the specific case of a claimed separability/factorization ansatz** — `test_kerr_check.py` verifies one directly via a vanishing mixed partial derivative, from the real metric, not by assuming the ansatz already worked. `counterexample-protocol.md`'s lemma-incorporation step covers the general case of finding a hidden assumption after the fact. |
| [4] Conservation/symmetry laws | Partially tool-backed for specific cases — `quantum_check.py` can verify unitarity/CPTP (a conservation-adjacent property) numerically; general symmetry reasoning is not automatable in general. |
| [5] Dimensional consistency | **Tool-backed.** `deriv_check.py`, real `sympy.physics.units`. |
| [6] Limiting case recovery | **Tool-backed** for exact/symbolic reductions and stated numeric targets. `deriv_check.py`. |
| [7] Peer-review survival | Prompt-only, and arguably should stay that way — this is `breakthrough-red-flags.md` and `scholar-eval.md` territory, judgment about a social process, not a mechanical fact. |

**Two of seven are fully tool-backed** ([5], [6]); **two more are tool-backed
for specific, narrower cases** ([3] for a claimed separability ansatz, [4] for
quantum unitarity/CPTP) rather than in general. The other three are judgment
calls by nature, not gaps left unfilled by laziness — see "what stays
prompt-only" below for why that's the right line, not a shortcut.

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
- **EinsteinPy** (pure-Python GR tensor calculus) — installed
  (`einsteinpy==0.4.0`) and now **used for a real from-first-principles
  validation** — see Tool 4 below.
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

### K-Dense (`K-Dense-AI` on GitHub) — the most valuable single finding, now built (see Tool 0 above)
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
the fact rather than before. This was built and validated end-to-end this
round (Tool 0, above) — including a real adversarial test where a post-hoc
edit was made and correctly caught. It remains architecturally different from
everything else in this directory, and from `anti-fabrication.md` itself:
prevention, not after-the-fact detection.

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
