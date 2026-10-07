# PhysicsForge — Writing Quality Protocol

A protocol for ensuring physics writing reads like the work of an expert physicist —
not the output of a language model.

LLMs produce certain patterns that experienced readers immediately recognize as
machine-generated: stacked transitions ("furthermore", "moreover", "additionally"),
hedging phrases ("it is important to note"), bullet-list overuse where prose is
expected, and a particular flat tone. This protocol catches these patterns before they
reach delivery.

Adapted from Imbad0202's Writing Quality Check, K-Dense's prose-first writing rules,
and 199-biotechnologies' anti-fatigue enforcement.

---

## CORE PRINCIPLE: PROSE-FIRST

Physics papers are written in **paragraphs**, not bullet points. Bullet points are
acceptable for:
- Genuinely list-like content (a list of axioms, a list of theorems, a list of references)
- Itemized procedures (a numbered methodology)
- Structured comparisons (a table-like presentation)

Bullet points are NOT acceptable for:
- Derivations (these are sequential prose)
- Discussion (this is argument, not enumeration)
- Conclusions (these are synthesis, not lists)
- Introduction (this sets context, requires connective tissue)

When LLMs produce derivation-as-bullets, the reader perceives the work as superficial
even when the content is technically correct. The protocol enforces prose-first
output.

---

## TWO-STAGE WRITING PROCESS

This pattern is adapted from K-Dense's scientific-writing skill. It produces measurably
better output than direct prose generation.

### Stage 1: OUTLINE WITH KEY POINTS

Before writing any prose, produce a structured outline:

```
SECTION OUTLINE: [section title]

OPENING (1-2 sentences):
  Key point: [the central claim of this section]
  Hook: [why the reader should care]
  
CONTEXT (1 paragraph):
  Prior work: [what has been established]
  Open question: [what this section addresses]
  Citations needed: [arXiv IDs to cite here]

CORE CONTENT (multiple paragraphs):
  Paragraph 1: [topic] — [key claim] — [evidence]
  Paragraph 2: [topic] — [key claim] — [evidence]
  Paragraph 3: [topic] — [key claim] — [evidence]
  
EQUATIONS (in derivation order):
  Eq. (N1): [statement] — [why it appears here]
  Eq. (N2): [statement] — [follows from Eq. (N1)]
  ...
  Eq. (NK): [main result of section]
  
TRANSITION TO NEXT SECTION:
  [How this section sets up the next]
```

### Stage 2: CONVERT OUTLINE TO PROSE

Only after the outline is complete and reviewed, convert it to flowing prose.

Critical: **never skip Stage 1**. Direct-to-prose generation produces structurally
weak writing. The outline is what makes the prose coherent.

---

## ANTI-AI-PATTERN DETECTION

These patterns appear frequently in LLM output and should be flagged and rewritten.

### Stacked transitions

**Pattern**: "Furthermore, ... Moreover, ... Additionally, ... In addition, ..."

**Why it fails**: Real physicists write transitions that carry meaning. Stacked
generic transitions signal that the model is structuring text without actually
reasoning about flow.

**Correct behaviour**: Use specific connectives that show logical relationship:
- "It follows that..." (logical consequence)
- "By contrast..." (contrast)
- "This implies..." (implication)
- "More generally..." (generalization)
- "However..." (genuine contradiction)

If a transition word doesn't carry meaning, delete it and let the structure speak.

### Hedging stacks

**Pattern**: "It is important to note that..." / "It is worth mentioning that..." /
"One should keep in mind that..." / "It must be emphasized that..."

**Why it fails**: These are pure throat-clearing. They signal "I am about to say
something" without actually saying it. Strip them. The next sentence is the content.

**Correct behaviour**: State the point directly. If a caveat is needed, name it
specifically: "This holds only when ε ≪ 1" rather than "It is important to note that
this requires small ε."

### Verb tics

**Pattern**: "delve into", "leverage", "navigate", "underscore", "elucidate", "shed
light on", "explore the intricacies of"

**Why it fails**: These verbs appeared in the LLM training corpus disproportionately
often. They signal AI-generated text to readers.

**Correct behaviour**: Use plain verbs:
- "examine" / "study" instead of "delve into"
- "use" instead of "leverage"
- "show" / "demonstrate" instead of "underscore"
- "explain" instead of "elucidate"

### Concluding tics

**Pattern**: "In conclusion..." / "To summarize..." / "Overall..." / "In summary..."

**Why it fails**: These signal a paragraph that the writer doesn't have a real
conclusion for. Real conclusions don't need announcing.

**Correct behaviour**: Make the closing sentence the conclusion. Cut the throat-clearing.

### List-bullet contamination

**Pattern**: Converting paragraph content into bullet points to look "structured".

**Example of the failure**:

> The Boltzmann equation has several important features:
> - It conserves particle number
> - It conserves momentum  
> - It conserves energy
> - It satisfies the H-theorem

**Why it fails**: This is a paragraph wearing bullet-point clothes. It reads as
shallow.

**Correct version**:

> The Boltzmann equation has four conservation properties: particle number, momentum,
> and energy are each conserved by the collision integral, and the H-theorem
> guarantees monotonic entropy increase. These four properties make it the canonical
> kinetic equation for systems near local equilibrium.

The prose version conveys the same content with depth that the bullets don't.

### Generic intensifiers

**Pattern**: "very important", "highly significant", "extremely complex", "tremendously
useful"

**Why it fails**: Empty modifiers. If something is important, demonstrate why; don't
assert it with intensifiers.

**Correct behaviour**: Replace intensifiers with specifics. "Very important" → "central
to the argument because [specific reason]".

---

## WORD-LEVEL PRECISION AUDIT

Before delivery, scan the text for these specific failure patterns:

### Audit checklist

```
═══ WRITING QUALITY AUDIT ═══

[1] STACKED TRANSITIONS:
    Count occurrences of {furthermore, moreover, additionally, in addition} per page.
    Target: ≤ 2 per page.
    Action if exceeded: Rewrite transitions to carry specific meaning.

[2] HEDGING STACKS:
    Count occurrences of {it is important to note, it is worth mentioning, one should keep in mind, it must be emphasized}.
    Target: 0.
    Action: Strip and restate directly.

[3] VERB TICS:
    Count occurrences of {delve, leverage, navigate, underscore, elucidate, shed light on}.
    Target: 0.
    Action: Replace with plain verbs.

[4] CONCLUDING TICS:
    Count occurrences of {in conclusion, to summarize, overall, in summary} at paragraph or section starts.
    Target: 0.
    Action: Cut the announcement; make the next sentence the conclusion.

[5] BULLET CONTAMINATION:
    Bullet lists in derivation, discussion, or introduction sections: 0.
    Action: Convert to prose.

[6] GENERIC INTENSIFIERS:
    Count {very important, highly significant, extremely complex, tremendously useful}.
    Target: 0.
    Action: Replace with specifics.

[7] PARAGRAPH-LENGTH SENTENCES:
    Sentences > 50 words: flag for review.
    Action: Split into multiple sentences if possible.

[8] MISSING CITATIONS:
    Claims like "it is well known", "as is standard", "by classical results" without
    a specific citation.
    Action: Cite the specific paper or downgrade to "we observe that" / "we conjecture that".
```

---

## STYLE CALIBRATION

If the user has provided prior writing (their own published papers, their thesis,
their preferred journals), calibrate to their style:

1. Read 2-3 paragraphs of their prior work
2. Identify their preferences:
   - Sentence length (short/medium/long)
   - Use of first person ("we"/"I"/none)
   - Equation density (heavy/light)
   - Tone (formal/conversational/somewhere in between)
3. Match these patterns in the generated text

Without sample writing, default to:
- Medium sentence length
- "We" for first person (standard physics convention)
- Equation density appropriate to the section
- Formal but not stiff tone

---

## VENUE-SPECIFIC CONVENTIONS

Different journals have different style preferences:

| Journal | First person | Sentence length | Tone | Equations |
|---|---|---|---|---|
| PRL | "We" | Short, punchy | Compressed | Numbered, in display |
| PRD | "We" | Medium | Standard | Numbered, in display |
| JHEP | "We" | Medium-long | Formal | Numbered, in display |
| CQG | "We" | Medium | Formal | Numbered, in display |
| Nature Physics | "We" | Short, broad accessibility | Less technical | Few, all critical |
| Phys. Rep. | "We" | Long, comprehensive | Authoritative | Many, fully derived |

When writing for a specific venue, match its conventions. The acquired tone of a
journal is part of what makes a paper feel native to it.

---

## ANTI-FATIGUE ENFORCEMENT

A long writing session degrades into shorter, more bulleted, more hedged prose. This
is the "fatigue pattern" 199-biotechnologies identified in their deep research skill.

To prevent fatigue:

1. **Periodic re-reading**: Every 1500 words, re-read the previous 500 words. Check
   that quality has not degraded.

2. **Anti-bullet vigilance**: If bullet usage has been creeping up, pause. The next
   500 words should be fully prose.

3. **Citation density check**: If recent paragraphs have fewer citations than earlier
   ones, the paper is becoming less defensible. Add citations or downgrade claims.

4. **Sentence variety**: If the last 5 sentences have similar structure, vary the
   next ones.

5. **Concluding-tic check**: If "in conclusion", "to summarize", or "overall" has
   appeared in the last 500 words, the writer is signalling fatigue. Take a break or
   reset.

---

## INTEGRATION WITH OTHER PROTOCOLS

- After Phase 4 (derivation generation): run writing-quality audit on the prose around
  the derivation
- Before Phase 7 (Citation Guard): clean up the writing quality so the citation
  verification has good prose to work with
- After adversarial review: when revising, maintain writing quality standards
- Final delivery: writing-quality audit is mandatory before delivery

---

## QUICK REFERENCE — WORDS TO AVOID

Cut these on sight unless they carry specific meaning:

```
delve into, leverage, navigate (verb), underscore, elucidate, shed light on,
explore the intricacies of, in the realm of, the fact that, it is worth noting,
it is important to note, one should keep in mind, it must be emphasized,
furthermore (when stacked), moreover (when stacked), additionally (when stacked),
in addition (when stacked), in conclusion, to summarize, overall (concluding),
in summary, very important, highly significant, extremely complex, tremendously useful,
profound implications, profound understanding, intricate workings,
play a crucial role, play a pivotal role, play a key role,
unprecedented, paradigm-shifting, game-changing, cutting-edge,
state-of-the-art (overused), revolutionary
```

This list is illustrative not exhaustive. The principle: if a word looks like it
came from an AI-generated text and doesn't carry specific meaning, cut it.

---

## CRITICAL: WHAT WRITING QUALITY IS NOT

This protocol does NOT:
- Mandate a particular writing style
- Replace good editing
- Make a paper good if its content is bad

It DOES:
- Catch surface patterns that signal AI generation to expert readers
- Enforce prose-first structure where prose is expected
- Force specific meaning into transitions and modifiers
- Apply venue-appropriate conventions

Good physics writing is about substance. This protocol just ensures the substance
isn't obscured by surface tics.
