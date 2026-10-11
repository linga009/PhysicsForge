---
name: preregister
description: Freeze a prediction via git-commit-ancestry proof before checking it, or audit an existing pre-registration against its results
argumentHint: [freeze <file> [data-files...]] | [audit [--results <path>] [file...]]
---

The user wants to pre-register a prediction, or audit an existing
pre-registration: `$ARGUMENTS`.

This uses `scripts/prereg.sh` (vendored from K-Dense-AI/science-superpowers,
MIT License). It makes "the prediction preceded the result" checkable from git
commit ancestry alone — not from a timestamp comment, which is forgeable.

**To freeze a new prediction** (must happen BEFORE running the confirmatory
test, not after):

1. Write the pre-registration as a markdown file under `preregistrations/`,
   stating the prediction precisely enough to be judged right or wrong.
2. Run:
   ```
   sh ${CLAUDE_PLUGIN_ROOT}/scripts/prereg.sh freeze preregistrations/<name>.md [raw-data-file ...]
   ```
   This commits the file (its first commit IS the timestamp proof), then
   stamps the freeze commit hash into the document. If raw data files are
   given, their git blob checksums are recorded so later tampering with the
   data itself is also detectable.
3. **From this point, do not edit the pre-registration file.** Any edit, or any
   results committed at-or-before the freeze commit, will fail the audit below.

**To audit** an existing pre-registration against its results (run this before
reporting any result as confirmatory, never skip it):

```
sh ${CLAUDE_PLUGIN_ROOT}/scripts/prereg.sh audit [--results <path>] [file...]
```

This checks, from git history alone:
- **FROZEN** — the file has a genuine first-commit freeze point
- **STAMP** — the stamped commit hash matches the real freeze commit
- **INTEGRITY** — content is byte-identical to the frozen version (at HEAD and
  in the working tree)
- **CHRONOLOGY** — no commit touching the results path is at-or-before the
  freeze commit (via `git merge-base --is-ancestor`, not timestamps)
- **DATA** — frozen raw-data checksums still match the files

Report the tool's own PASS/FAIL output verbatim — do not paraphrase a FAIL as a
minor caveat. **A failed audit means the confirmatory label cannot be
defended**: tell the user to report the analysis as exploratory, or
pre-register a fresh test on unused data. Never report a result as
"confirmatory" without a passing audit backing it.
