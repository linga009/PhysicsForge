# Contributing to PhysicsForge

Thanks for your interest. PhysicsForge improves through contributions, and the bar for engagement is low — open an issue, send a PR, or fork and adapt freely.

## Ways to contribute

### 1. Report a rule violation

The most valuable bug report is a concrete prompt where the model breaks one of the framework's rules. Please include:

- **Model and version** (e.g. Claude 3.5 Sonnet, Gemini 1.5 Pro, GPT-4o, Llama 3.1 70B).
- **Which version of the framework** (commit SHA from this repo, or "Anthropic Skill" / "Gemini Gem" if you're using a published copy).
- **The exact prompt** that triggered the failure.
- **The model's response** (verbatim, in a fenced code block).
- **Which rule was violated** — quote the section number from `SKILL.md` or `gemini-gem/instructions.md` (e.g. "§4 Claim Hierarchy: model labelled an unproven step as Theorem").
- **Severity**: rule violations on Millennium-class problems are highest priority. Cosmetic issues (e.g. missed Pauli protocol header on a casual question) are lower.

Open an issue using the **Bug report** template.

### 2. Add a verification pattern

If you have a `sympy` or numerical pattern that catches a class of errors not covered by `verification.md`, contributions are welcome. Format:

```markdown
## PATTERN N — [NAME]

[One-paragraph description of what this catches.]

```python
# Working example
import sympy as sp
...
```

### Output template

```
[show the inline output format]
```
```

### 3. Add a domain module

`domains.md` covers eleven domains. If you're a working researcher in a domain not yet represented (biophysics, plasma physics, ML theory, axiomatic QFT, quantum thermodynamics, etc.), a 30–80-line module covering:

- **Key open gaps** — 4–8 bullets, each a concrete unresolved problem.
- **Key mathematical tools** — what an expert reaches for first.
- **Key references** — 3–6 canonical books or papers.

would be a real contribution.

### 4. Add a worked example

`examples.md` has three calibration targets. New examples should:

- **Demonstrate a specific behaviour** the model needs to learn (a derivation engine output, a critique of a published-but-flawed paper, a verification trace, a Millennium-protocol invocation).
- **Be self-contained** — readable without external context.
- **Match the density and rigour** of the existing examples (real numerical values, real citations, no placeholders).

### 5. Improve the rules themselves

Suggestions for new rules, sharper criteria for existing ones, or better refusal templates are welcome. Submit as a PR with:

- The rule change (additions, modifications, deletions).
- **A failure-mode analysis**: what failure does this address?
- **A smoke test**: a prompt that, after the change, should produce a specific behaviour. Add it to the smoke-test table in `gemini-gem/instructions.md`.

## PR checklist

- [ ] Changes are scoped to a single concern (one PR per logical change).
- [ ] If you touched `SKILL.md` or `gemini-gem/instructions.md` rules, you updated **both** (the Anthropic Skill and the Gemini Gem versions stay in sync where possible).
- [ ] If you added a new section, you updated the table of contents in `README.md`.
- [ ] If your change addresses a specific failure mode, you added a smoke-test prompt in `gemini-gem/instructions.md`.
- [ ] No unrelated formatting changes (don't reformat unrelated paragraphs).

## Style

- **Markdown is the lingua franca.** Plain Markdown, no HTML except where unavoidable.
- **Prefer prose over bullets** for explanatory content. Use tables for comparisons.
- **Cite real papers.** Fabricated citations are a hard rejection. If you're not sure a paper exists, write `[VERIFY]` instead.
- **Keep tone direct.** PhysicsForge is opinionated; the documentation should match.
- **Don't soften the rules.** If a rule says "must" or "never", don't relax it to "should consider" without an explicit failure-mode analysis.

## Code of conduct

Be civil. Disagree with arguments, not people. The framework exists to interrogate claims rigorously — extend the same standard to fellow contributors.

## Licensing

By contributing, you agree your contributions will be licensed under the same MIT license that covers this repository.
