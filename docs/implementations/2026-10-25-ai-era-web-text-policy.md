# 2026-10-25 AI-era web-text policy comparison

| | |
|---|---|
| PLAN step | None in the Stage 0 PLAN; ROADMAP corpus-policy task, issue #55 |
| Branch | `research/55-ai-era-web-text` |
| SRS requirements | D32 human-written, open-licensed pretraining text; D45 contribution process |
| Status | Planned; verification below is registered before the research note |

## Problem / Motivation

Issue #55 needs evidence for OD-4 (#25): compare older snapshots only, curated sources only, and a stated, accepted residual of machine-written web text. D32 forbids other models' outputs. This research records costs and uncertainty without changing that requirement or making the owner's decision.

The owner explicitly authorizes this issue, the branch, autonomous research, pushing this branch and one draft PR. The task-specific instructions override CONTRIBUTING's issue-comment and unresolved-choice procedures: make no issue comments, labels or assignments; record unsettled choices for the owner and continue conservatively.

## What Changed

| File | Description |
|---|---|
| `docs/implementations/2026-10-25-ai-era-web-text-policy.md` | This advance plan and, after research, observed verification and limits. |
| `docs/research/2026-10-25-ai-era-web-text-policy.md` | Evidence range for the cutoff, survey-based volume comparison by language and licence class, practical checks, detector limits and owner questions. |

No source code, policy specification, roadmap, architecture, assistant specification, survey branch or results artifact is changed. This plan is committed alone before writing the research note.

## Implementation Approach

1. Read CONTRIBUTING, the implementation and PR templates, D32, the roadmap and the assistant specification. Create a fresh worktree outside OneDrive from origin/main. Initial base: `a30dd6a804c50d895119abf182bad5a3fcbd5360`.
2. Verify web access and both required notes on origin. Stop and report if web access is absent or either note is absent. Both checks succeeded before this plan.
3. Read the English survey at `e637be6b87af34d065f95c7511e7d65ed0f5d8b1` and the Turkish survey at `c1db10da0fd4aa64d7b4de7b9a5e25ad0c52f9b0`. Cite immutable file URLs and access dates. Keep estimates, units, licence gates, rejected candidates and overlap exclusions intact.
4. Read dated primary announcements, original web-prevalence research and detector evaluations as raw text where available. Distinguish release, adoption, crawl, original publication and revision dates. Present a risk window rather than select an authoritative cutoff. Avoid novelty claims.
5. Compare all policy options by language and licence class. Distinguish conditional gross envelopes from measured eligible volume. Show known excluded volume and unknown portions without inventing retention percentages or adding overlapping alternatives. Rights approval and authorship checks remain separate gates.
6. Specify reproducible provenance, snapshot/revision checks, curation evidence, audits and quarantine. Describe detector errors and language/domain limitations. For a residual policy, distinguish a measured audit result from a detection score and from authorization to relax D32.
7. Explain Turkish constraints using the pinned survey's own quantities and assumptions. End the note with the trade-off, with OD-4 left to the owner.
8. Complete Verification, run the required repository tests and documentation checks, commit the note and completed plan, push only this branch and open one draft PR using the repository template with `Closes #55`. Never merge.

This is documentary research. No public function or class is added. Inputs are the pinned surveys and primary texts; outputs are the comparison note and completed plan. Side effects are those documents, commits, the branch push and the draft PR. Invariants are D32, unchanged owner-controlled specifications, explicit uncertainty, source attribution and no corpus ingestion. The generated research prose is not training data.

## Mathematical / Statistical Details

Every derived value will be labelled `Inference:` and show its inputs and units. Reuse the surveys' byte/token sensitivity assumptions; do not convert compressed bytes, XML, metadata or incompatible publisher token counts into Chorus tokens. Keep separate licence classes separate unless an explicitly conditional scenario permits combining them.

For an eligible gross envelope U and a measured retention fraction r, retained volume would be rU and excluded volume (1-r)U. No r is assumed where the surveys did not measure one. A rejected candidate's published scale is not a recoverable training-volume loss. Alternative snapshots and overlapping corpora are not additive.

Any audit upper bound must state its sampling unit, independence assumptions and confidence interpretation. Detector sensitivity, false-positive rate and prevalence estimates apply only to their measured populations. No model, seed, training run or corpus-wide contamination experiment is planned.

## Design Decisions

- Use the client date in the task environment for filenames and source access dates.
- Use the user-specified branch and worktree under `C:\Users\senso\chorus-dev\research\55-ai-era-web-text`; never switch another checkout's branch.
- Read survey branches without merging them. Their unapproved gross volumes remain conditional evidence, not approved corpus inventory.
- Conservative reporting default: exclude unresolved rights/authorship material from any claimed ready-to-train volume. Report unknowns instead of substituting zero or a guessed retained fraction.
- **Open for the owner:** the cutoff and whether original editions verified through later transcriptions count as older-snapshot evidence.
- **Open for the owner:** licence classes and territorial/edition rights, including share-alike and parliamentary speaker rights (OD-3 / OD-10).
- **Open for the owner:** the provenance and editorial evidence sufficient for human authorship, and use of models solely for classification/filtering.
- **Open for the owner:** whether any residual can be accepted under D32, and the audit scope, threshold and treatment of edited/translated AI prose. No residual permission is inferred.
- **Open for the owner:** downstream Turkish volume, language allocation and model-size decisions. This note does not choose them.

## Verification

Registered checks, to be completed with observed results before the research commit:

- Confirm only the planned documents differ from the pinned main base and the first commit contains only this plan.
- Recompute every derived table against the pinned surveys; check units, licence groups, date scopes and overlap exclusions.
- Check primary source text, URLs, access dates and the distinction between external measurements and Chorus inferences.
- Run `git diff --check` and scan every written file for U+2013 and U+2014; both must produce no findings.
- Run `python -m pytest` as required by CONTRIBUTING; record the exact environment and result, including skips or limitations.
- Verify the final commit, clean worktree, remote branch and draft PR state. Check that the PR includes owner questions, unresolved survey dependencies and the required closing reference.

Hardware/environment: the owner's Windows laptop; exact CPU, Python and PyTorch versions will be recorded with the observed test result. Model size, training dataset and seeds: not applicable to documentary research. Literature datasets and measurement scopes will be stated with the corresponding evidence.

**Not tested:** corpus downloads, complete rights clearance, true contamination, actual retained text volume, detector performance on Chorus, Turkish quality, model training or the later data pipeline. No research experiment result is created, so no RESULTS.md entry is planned.

## Related Docs

- [Issue #55](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/55) and [OD-4 #25](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/25), read 2026-10-25.
- [English survey, pinned origin commit](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/blob/e637be6b87af34d065f95c7511e7d65ed0f5d8b1/docs/research/2026-10-25-english-pretraining-sources.md), read 2026-10-25.
- [Turkish survey, pinned origin commit](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/blob/c1db10da0fd4aa64d7b4de7b9a5e25ad0c52f9b0/docs/research/2026-10-25-turkish-pretraining-sources.md), read 2026-10-25.
- [CONTRIBUTING](../../CONTRIBUTING.md), sections 3, 4, 5 and 8.
- [SRS](../SRS.md), D32 and D45; [ROADMAP](../ROADMAP.md), corpus policy and OD-4; [assistant specification](../assistant-spec.md), data policy.
