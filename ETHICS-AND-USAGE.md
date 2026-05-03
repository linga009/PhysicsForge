# Ethics & Usage Guidelines

> **TL;DR:** PhysicsForge is a research aid, not an oracle. You are responsible for everything you publish under your name. **Disclose substantive AI use** to the venue you're submitting to. **Verify every citation, derivation, and numerical value** independently. **Never list a model as an author.** **Never claim resolution of an open problem** based on AI output. **Never upload another person's manuscript-under-review to an AI tool** — that is a confidentiality breach. The framework's structural rules (claim hierarchy, Pauli Protocol, Millennium Protocol) reduce — but do not eliminate — the risks.

---

## Table of contents

- [Scope of this document](#scope-of-this-document)
- [Three universal principles](#three-universal-principles)
- [What you can do ethically](#what-you-can-do-ethically)
- [What you must not do](#what-you-must-not-do)
- [Verification: the non-negotiable layer](#verification-the-non-negotiable-layer)
- [Disclosure: when, where, and how](#disclosure-when-where-and-how)
  - [Sample disclosure statements](#sample-disclosure-statements)
- [Authorship](#authorship)
- [Peer review and confidentiality](#peer-review-and-confidentiality)
- [Specific risks of PhysicsForge](#specific-risks-of-physicsforge)
- [Major publisher policies at a glance](#major-publisher-policies-at-a-glance)
- [Educational use](#educational-use)
- [Pre-submission checklist](#pre-submission-checklist)
- [Reporting misuse](#reporting-misuse)
- [References and further reading](#references-and-further-reading)

---

## Scope of this document

This document covers the ethical and policy considerations that apply when **using PhysicsForge** as part of research, manuscript preparation, peer review, or teaching. It does *not* cover the legal status of the framework itself (released under MIT — see [`LICENSE`](./LICENSE) — and freely usable, modifiable, and redistributable, including commercially).

The guidance below reflects the policy landscape as of 2026, in which substantive consensus has formed across major publishers. Specific journal policies continue to evolve; **always check the current author guidelines of the venue you are submitting to** before relying on the summaries below.

## Three universal principles

Across every major publisher and standards body that has weighed in on AI use in research — Nature Portfolio, Science / AAAS, Elsevier, Wiley, Taylor & Francis, SAGE, Springer, IEEE, ACM, arXiv, the International Committee of Medical Journal Editors (ICMJE), and the Committee on Publication Ethics (COPE) — three principles are non-negotiable and identical:

1. **AI tools are not authors.** No LLM, no chatbot, no agent, no PhysicsForge instance can be listed as an author or co-author. Authorship requires the ability to take responsibility for the work, sign legal agreements, and approve the final manuscript. Only humans (and in some cases legal persons) can do these things.

2. **Substantive use must be disclosed.** Routine grammar/spelling polishing is generally exempt, but anything beyond that — drafting sections, suggesting derivation steps, generating figures, writing code, summarising literature — must be disclosed. The exact wording and location of the disclosure varies by publisher (see [the table below](#major-publisher-policies-at-a-glance)).

3. **The human author retains full responsibility.** Errors, hallucinations, fabricated citations, plagiarised passages, mislabelled claims — all of these are the author's responsibility regardless of whether an LLM produced them. *"The AI did it"* is not a defence.

Internalise these three. The rest of this document is just operational detail.

## What you can do ethically

PhysicsForge is built to make these uses safer and more rigorous. With proper verification and disclosure, the following are uncontroversial:

- **Drafting and structuring manuscripts.** Producing a first draft of an introduction, theoretical-background section, or LaTeX preamble that you then edit, verify, and rewrite as needed.
- **Sanity-checking your own derivations.** Running symbolic verification on equations you have derived to catch sign errors, dimensional mismatches, and missed limiting cases.
- **Auditing your own work for hidden assumptions.** Using the eight-step paper-analysis workflow on your own draft before submission, to catch the kind of *"by standard arguments"* hand-waving that referees flag.
- **Mapping the gap landscape of a subfield** before choosing a research direction. Treat the output as a starting bibliography to be verified against the actual literature.
- **Generating LaTeX scaffolding** — preambles, theorem environments, table templates, BibTeX skeletons — that you then populate with verified content.
- **Stress-testing argument chains.** Asking the framework to identify the load-bearing assumption in your argument, or the limiting case where your construction breaks.
- **Producing numerical estimates** for predictions, with the understanding that the underlying constants and formulas need independent verification.
- **Teaching.** Demonstrating to students what claim classification, dimensional analysis, and limiting-case verification actually look like in practice.

## What you must not do

The following are misconduct under standard publication ethics, regardless of what the framework's output looks like:

- **List PhysicsForge, Claude, Gemini, GPT, or any AI tool as an author or co-author.** Universal prohibition across all major publishers.
- **Submit work without disclosing substantive AI use.** This violates Nature, Science, Elsevier, Springer, Wiley, IEEE, ACM, ICMJE, and most journal policies. At Science / AAAS journals, undisclosed AI-generated content has historically been classified as scientific misconduct.
- **Submit fabricated citations.** LLMs hallucinate references. PhysicsForge marks uncertain ones with `[VERIFY]`, but this is a soft barrier. Every `\bibitem` in a manuscript is your responsibility. Submitting fake references — even unintentionally — is misconduct.
- **Submit a "proof" of an open problem produced via PhysicsForge.** The framework's Millennium-Class Protocol explicitly refuses to claim proofs for Clay-prize-tier problems; do not relabel its conditional partial advances as full resolutions when you write up the result. If you genuinely advance a Millennium problem, the proof must be human-derived, peer-reviewed, and verified through the standard channels (typically the Clay institute's own protocol takes years).
- **Upload another author's manuscript-under-review to PhysicsForge or any LLM.** Almost universally classified as a confidentiality breach. ACM, IEEE, NIH, and most publishers explicitly prohibit it. If you are reviewing a paper, do not paste it into a chat interface — the model provider may log the input.
- **Use the framework to manufacture controversy** (e.g., "PhysicsForge proves Einstein wrong about X"). The framework's Pauli Protocol and claim hierarchy will resist this, but they can be circumvented by a determined user. Doing so is intellectually dishonest and damages the broader research community's trust in AI-assisted work.
- **Submit AI-generated figures or images** without checking the venue's policy. Many publishers (Nature, Springer Nature broadly) prohibit AI-generated figures outright; others (PLOS) allow them with disclosure. Diagrams and `tikz-feynman` code generated by PhysicsForge are usually fine because they are deterministic LaTeX, not generative imagery — but check.

## Verification: the non-negotiable layer

PhysicsForge is built around verification, but **the framework's verification is not enough by itself**. Three independent checks must be performed by you, the human author, before any output enters a manuscript:

1. **Citation verification.** Every reference in a PhysicsForge-assisted manuscript must be checked against the actual paper — author names, journal, year, DOI, and (most importantly) what the cited paper actually says. LLM-fabricated citations are the single most common form of AI-induced misconduct in 2026. Tools like INSPIRE-HEP, arXiv search, Google Scholar, and your library's catalogue should be used to confirm every entry.

2. **Derivation re-derivation.** If a derivation is going into your manuscript, you should be able to reproduce it on paper, independently, end-to-end, without the framework's output in front of you. If you cannot, you do not understand it well enough to publish it.

3. **Numerical cross-check.** Any numerical estimate the framework produces must be independently computed using a calculator or `numpy`/`scipy` from constants you look up yourself. The framework can confidently produce a value that's off by a factor of $4\pi$, a power of $10$, or a sign.

If you skip these three checks, you are not using PhysicsForge — you are gambling.

## Disclosure: when, where, and how

### When to disclose

You must disclose if PhysicsForge (or any LLM) was used to:

- Draft, rewrite, or substantially edit any section of the manuscript
- Suggest or produce any derivation step that appears in the final paper
- Generate any LaTeX code that survives into the manuscript
- Produce numerical estimates that are reported as results
- Audit, summarise, or critique any cited paper in the discussion
- Generate any portion of the bibliography
- Generate any figure, diagram, or visual element

You generally do **not** need to disclose if PhysicsForge was used only for:

- Grammar, spelling, or punctuation polishing (Springer Nature explicitly exempts this; check your venue)
- Formatting assistance unrelated to content
- Personal note-taking that did not enter the submitted manuscript

When in doubt, disclose. Over-disclosure is harmless; under-disclosure is misconduct.

### Where to disclose

This varies by venue. The most common locations:

| Location | Used by |
|---|---|
| **Methods section** | Nature Portfolio (and all Springer Nature journals) |
| **Acknowledgements** | Springer (some imprints), IEEE, ACM, Wiley, Elsevier (often) |
| **Methods + Acknowledgements** | Science / AAAS |
| **Cover letter + manuscript** | ICMJE-following medical journals |
| **Dedicated AI Disclosure section** | A growing number of journals are adopting Resnik et al.'s three-tier framework |

When in doubt, follow the venue's most recent author guidelines. If the guidelines are silent, default to **a clear statement in both the Methods section and the Acknowledgements** — both visible, both unambiguous.

### Sample disclosure statements

The following templates are starting points; adapt to your venue's required wording.

#### Minimal disclosure (sanity-checking only)

> *"During the preparation of this work, the author(s) used PhysicsForge — an open-source structured prompting framework (https://github.com/&lt;your-username&gt;/physicsforge) running on top of [model name and version, e.g. Claude 3.5 Sonnet / Gemini 1.5 Pro] — to verify dimensional consistency and limiting-case behaviour of the derivations in Section X. After using this tool, the author(s) reviewed and re-derived the relevant equations independently, and take full responsibility for the content of the publication."*

#### Moderate disclosure (drafting + auditing)

> *"During the preparation of this work, the author(s) used PhysicsForge (https://github.com/&lt;your-username&gt;/physicsforge), a structured prompting framework, running on [model name and version], to (i) draft initial versions of Sections 2 and 4, (ii) audit the derivation in Appendix B for hidden assumptions, and (iii) generate the LaTeX preamble. All AI-assisted output was independently verified, edited, and re-derived by the author(s), who reviewed and revised the content as needed and take full responsibility for the final manuscript. No AI tool is listed as an author. All cited references were independently confirmed against the original sources."*

#### Heavy disclosure (substantive content generation)

> *"This work made substantial use of PhysicsForge (https://github.com/&lt;your-username&gt;/physicsforge), an open-source structured prompting framework for physics and mathematics research, running on [model name and version]. Specifically, the framework was used to: identify the gap analysis in Section 1.2, propose the postulate-driven framework structure in Section 3, generate first-draft LaTeX for Sections 2–5, and produce the symbolic verification reported in Appendix C. The author(s) independently re-derived all equations appearing in the final manuscript, verified all cited references against original sources, and take full responsibility for the content. The framework declined to claim resolution of [open problem name]; the partial advance reported here is presented as a [Conjecture / Proposition / framework], consistent with the framework's claim-hierarchy classification."*

#### Negative disclosure (where applicable, e.g. Science)

For venues that prohibit certain AI uses outright, you may need to disclose what was *not* done:

> *"PhysicsForge and other AI tools were not used to generate any text, equations, or figures appearing in this manuscript. Use of these tools was limited to language polishing of an early draft, in line with [Venue]'s policy."*

## Authorship

This is the simplest section because the rule is universal:

> **AI tools cannot be authors. PhysicsForge cannot be an author. Period.**

There is no exception, no edge case, no clever workaround. Every major publisher — Nature Portfolio, Science / AAAS, Springer Nature, Elsevier, Wiley, Taylor & Francis, SAGE, IEEE, ACM, arXiv, ICMJE, COPE — has stated this explicitly. The reasoning is that authorship requires accountability, and only legal persons (humans, sometimes corporations) can be held accountable.

Listing PhysicsForge, the underlying model, or any AI tool as an author is a violation of publication ethics that can result in:

- Manuscript rejection
- Retraction post-publication
- Reporting to your institution's research integrity office
- Reputational damage to all listed human authors

The correct attribution is in the disclosure statement, not the author list.

## Peer review and confidentiality

If you are reviewing a manuscript for a journal or conference, **do not paste it into PhysicsForge or any LLM interface.**

The reasoning is that manuscripts under review are confidential documents. Most LLM providers log inputs for training, debugging, or both. Uploading a confidential manuscript to such a service may:

- Violate the confidentiality agreement you signed when accepting the review
- Constitute a breach of the author's intellectual property rights
- Be classified as research misconduct by your institution

ICMJE, Nature, Science, IEEE, ACM, NIH, and most major venues have stated this explicitly. Some venues (e.g. Nature) require reviewers to disclose any AI tool use during review, even if the manuscript itself was not uploaded.

PhysicsForge can ethically be used during review only in this narrow way: to look up general background knowledge, recall standard inequalities, or sanity-check your own thinking — never with any text from the manuscript itself in the prompt.

## Specific risks of PhysicsForge

The framework's structural rules reduce the probability of common LLM failure modes, but they do not eliminate them. Specific residual risks:

### Confident-but-wrong derivations
The model can produce output that passes the Pauli Protocol *as the model interprets it* but is nonetheless wrong. The protocol is a checklist run by the same model that produced the result — circularity is unavoidable. Mitigation: independent re-derivation by you (see [Verification](#verification-the-non-negotiable-layer)).

### Fabricated citations
Despite the framework's `[VERIFY]` tagging instruction, the model may produce citations that look correct but reference nonexistent papers, or real papers with subtly wrong details (wrong year, wrong journal, wrong page numbers, or — most insidiously — a real paper that does not actually say what the model claims). Mitigation: every reference goes through arXiv, INSPIRE-HEP, Google Scholar, or library catalogue verification.

### Hidden assumption smuggling
The eight-step paper-analysis workflow is designed to surface hidden assumptions, but the model can also *introduce* hidden assumptions in its own derivations and then fail to flag them in its own Pauli Protocol output. Mitigation: a third-party human reviewer with no exposure to the AI output is the gold standard.

### Millennium-protocol drift over long sessions
The framework's Millennium-class refusal is robust on the first turn, but in long conversations users can sometimes coax the model toward stronger claims through repeated reframing. Mitigation: never report a Millennium-class result without a fresh-context re-derivation, and never let session pressure persuade you to relabel a Conjecture as a Theorem in your manuscript.

### Style mimicry of authority
The framework's output looks rigorous: numbered equations, dimensional checks, theorem environments, references. This formatting can lend false credibility to claims that have not been independently verified. Mitigation: treat formatting as separate from validity — the LaTeX is meaningless if the content is wrong.

### Plagiarism risk
LLMs trained on copyrighted text can produce passages that are close paraphrases of, or in rare cases verbatim from, training material — including from papers you have not read. Mitigation: run any text the framework generates through your institution's plagiarism detector (Turnitin, iThenticate) before submission.

## Major publisher policies at a glance

The table below summarises the policies of major publishers as of early 2026. **These policies change frequently — verify with the venue's current author guidelines before submission.**

| Publisher / Venue | AI authorship | Disclosure required | Disclosure location | Restrictions on AI-generated content |
|---|---|---|---|---|
| **Nature Portfolio** (incl. all Springer Nature journals) | Prohibited | Yes, for substantive use | Methods section (Springer Nature broadly: Introduction or Acknowledgements) | AI-generated images prohibited (case-by-case exceptions); copy-editing exempt |
| **Science / AAAS** | Prohibited | Yes, mandatory | Methods + Acknowledgements; full prompt disclosure expected | Historically banned AI-generated text outright as misconduct; current policy allows disclosed use with strict scrutiny |
| **Cell Press / Elsevier** | Prohibited | Yes, for substantive use | Declaration statement at end of manuscript | Use limited to readability and language; substantive content generation discouraged |
| **Wiley** | Prohibited | Yes, with detailed declaration | Acknowledgements or dedicated section | Detailed declaration required |
| **Taylor & Francis** | Prohibited | Yes | Acknowledgements | — |
| **SAGE** | Prohibited | Yes | Acknowledgements | — |
| **IEEE** | Prohibited | Yes | Acknowledgements; must state AI system, sections affected, level of use | Reviewers prohibited from using public AI platforms |
| **ACM** | Prohibited | Yes | Authors' contributions or Acknowledgements | — |
| **APS journals** (Physical Review Letters, Physical Review D, etc.) | Prohibited | Yes, for substantive use | Acknowledgements | Verify current policy at journals.aps.org |
| **arXiv** | Prohibited | Authors take full responsibility for all content; disclosure encouraged | Author's discretion | The author is responsible for all errors, mistakes, incorrect references, or misleading content, regardless of AI use |
| **JHEP / SISSA** | Prohibited | Follow Springer's policy | Per Springer | — |
| **ICMJE-following medical journals** | Prohibited | Yes, mandatory | Cover letter and manuscript | Detailed elucidation of usage required |
| **PLOS** | Prohibited | Yes | Authors' contributions section | Comparatively permissive on AI-generated figures with disclosure |

When the venue is not on this list, default behaviour: **disclose, list no AI as author, take full responsibility, verify everything**. You will be in compliance with virtually every major publisher's policy by following these defaults.

## Educational use

Using PhysicsForge in teaching or learning settings has its own considerations.

**Generally appropriate:**
- Demonstrating to students what rigorous claim classification looks like
- Producing worked examples of dimensional analysis and limiting-case verification
- Showing students how to audit a paper for hidden assumptions
- Letting students stress-test their own derivations before submitting homework

**Generally inappropriate:**
- Letting students submit AI-generated work as their own (this is plagiarism / academic dishonesty in nearly every institution's policy)
- Using AI to grade student work without disclosure to students and the institution
- Using AI to write recommendation letters without disclosure to the receiving institution

If you teach, **publish your AI-use policy at the start of every course**. Students need clear guidance, not retroactive accusations.

## Pre-submission checklist

Before submitting any PhysicsForge-assisted manuscript to any venue, work through this checklist:

- [ ] I have read the **current** author guidelines of my target venue (re-checked within the last 30 days).
- [ ] I have verified the venue's specific AI-use policy.
- [ ] No AI tool is listed as an author.
- [ ] I have written a clear disclosure statement in the location the venue requires.
- [ ] Every citation in my bibliography has been independently verified against the actual paper (not just the existence of the paper, but what it claims).
- [ ] I can re-derive every equation in my manuscript on paper, independently, without the AI output in front of me.
- [ ] Every numerical value reported as a result has been independently computed from look-up constants.
- [ ] Every claim is correctly classified per the framework's hierarchy: Theorem / Proposition / Lemma / Corollary / Conjecture / Heuristic / Observation.
- [ ] No Clay-class or Millennium-class problem is claimed as resolved.
- [ ] I have run the manuscript through a plagiarism detector (Turnitin, iThenticate, etc.).
- [ ] Any figures generated with AI assistance comply with the venue's image policy.
- [ ] I have read this document in full.

If any box is unchecked, do not submit.

## Reporting misuse

If you become aware of someone using PhysicsForge — or any prompting framework derived from it — in a way that constitutes research misconduct (fabricated citations, undisclosed substantive AI use, AI listed as author, fake proofs of open problems claimed as genuine), the appropriate channels are:

1. **The venue's editor or programme chair**, if the work is in submission or recently published. All major publishers have ethics escalation paths.
2. **The research-integrity office** of the relevant author's institution.
3. **The Committee on Publication Ethics (COPE)** for cross-publisher guidance: [publicationethics.org](https://publicationethics.org).
4. **Retraction Watch** for high-profile cases that warrant public attention: [retractionwatch.com](https://retractionwatch.com).

Issues with the framework *itself* (e.g. a rule that produces a misleading output pattern) belong in [GitHub Issues](../../issues), using the bug-report template.

## References and further reading

The guidance in this document is grounded in the following primary sources, all current as of 2026. Always verify against the publisher's most recent guidelines before submission.

- **Nature Portfolio AI policy:** [nature.com/nature-portfolio/editorial-policies/ai](https://www.nature.com/nature-portfolio/editorial-policies/ai)
- **Springer Nature AI guidance:** [group.springernature.com/gp/group/ai](https://group.springernature.com/gp/group/ai/ai-guidance-for-our-researchers-and-communities)
- **Science / AAAS authorship policy:** [science.org/content/page/science-journals-editorial-policies](https://www.science.org/content/page/science-journals-editorial-policies)
- **Elsevier publishing ethics:** [elsevier.com/about/policies-and-standards/publishing-ethics](https://www.elsevier.com/about/policies-and-standards/publishing-ethics)
- **Wiley AI disclosure policy:** [authorservices.wiley.com/ethics-guidelines](https://authorservices.wiley.com/ethics-guidelines/index.html)
- **IEEE author guidelines on AI:** [ieee.org/publications/services/author-services-templates-guidelines](https://www.ieee.org/publications/services/author-services-templates-guidelines.html)
- **ACM authorship policy:** [acm.org/publications/policies/authorship-policy](https://www.acm.org/publications/policies/authorship-policy)
- **arXiv AI policy:** [blog.arxiv.org/2023/01/31/arxiv-announces-new-policy-on-chatgpt-and-similar-tools](https://blog.arxiv.org/2023/01/31/arxiv-announces-new-policy-on-chatgpt-and-similar-tools/)
- **ICMJE recommendations:** [icmje.org/recommendations](https://www.icmje.org/recommendations/)
- **COPE guidance on AI:** [publicationethics.org/cope-position-statements/ai-author](https://publicationethics.org/cope-position-statements/ai-author)
- **STM Association guidance:** [stm-assoc.org/standards-technology/ai-and-scholarly-communication](https://www.stm-assoc.org/standards-technology/ai-and-scholarly-communication/)

For a synthesis of the academic literature on AI disclosure frameworks, see Weaver (2026), *"Artificial intelligence and transparency: Toward a framework for disclosure of AI use in learning, research, and publication"*, SAGE; and Resnik et al. (2025), the three-tier disclosure framework now adopted by several journals.

---

## Final note

PhysicsForge exists because LLMs, used naively, are dangerous to the integrity of physics and mathematics literature. The framework's design is explicitly defensive: claim hierarchy, Pauli Protocol, Millennium Protocol, anti-sycophancy rules, refusal of fake proofs.

But no framework can substitute for the user's own judgement and ethical commitment. Every guard rail in PhysicsForge can be circumvented by a determined user willing to misrepresent the output. The framework reduces the probability of accidental misconduct; it cannot eliminate intentional misconduct.

The decision to use these tools ethically is yours. The framework supports that decision; it does not make it for you.

*Genuine partial progress beats fake completeness, every time.*
