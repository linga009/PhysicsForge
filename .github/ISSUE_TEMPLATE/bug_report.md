---
name: Bug report (rule violation)
about: The model broke one of PhysicsForge's rules
title: "[RULE VIOLATION] "
labels: bug
---

**Model and version**
(e.g. Claude Sonnet 5, Gemini 2.5 Pro, GPT-4o, Llama 3.1 70B)

**Which version of the framework**
(commit SHA from this repo, plugin version, or "Anthropic Skill" / "Gemini Gem" if using a published copy)

**The exact prompt that triggered the failure**

```
...
```

**The model's response (verbatim)**

```
...
```

**Which rule was violated**
Quote the section from `SKILL.md`, a `references/*.md` file, or `gemini-gem/instructions.md` (e.g. "Claim Hierarchy: model labelled an unproven step as Theorem").

**Severity**
- [ ] High — Millennium-class problem, fabricated citation, or fabricated derivation
- [ ] Medium — claim misclassified, self-audit skipped, Pauli Protocol not printed
- [ ] Low — cosmetic (e.g. missed header on a casual question)
