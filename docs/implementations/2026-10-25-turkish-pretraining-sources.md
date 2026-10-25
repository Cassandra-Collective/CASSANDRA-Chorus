# 2026-10-25 · Turkish pretraining sources survey

| | |
|---|---|
| PLAN step | None in Stage 0; roadmap 2.1b, issue #54 |
| Branch | `research/54-turkish-sources` |
| SRS requirements | D31, English and Turkish; D32, open-licensed human-written text; D45, owner decisions |
| Status | Planned on Windows; research and verification pending |

Copied from the implementation template before research. Commit this plan alone before writing the note.

## Problem / Motivation

Issue #54 measures the risk of insufficient open-licensed Turkish text before fixing model size. It supplies evidence for OD-3 (#24), OD-4 (#25) and OD-6 (#27). The specification gives a provisional 100M to 1B parameter range; roadmap 4.3 proposes a 100M to 300M pilot. This is research, not a pipeline or owner decision.

## What Changed

| File | Description |
|---|---|
| `docs/implementations/2026-10-25-turkish-pretraining-sources.md` | Preregister the survey and verification, then record its outcome. |
| `docs/research/2026-10-25-turkish-pretraining-sources.md` | Record source rights, provenance, volumes, English ratios and model-size implications. |

## Implementation Approach

1. Start at `origin/main`, `a30dd6a804c50d895119abf182bad5a3fcbd5360`, in a fresh worktree outside OneDrive. Read CONTRIBUTING sections 3, 4, 5 and 8; commit this plan alone.
2. Examine encyclopedia text, public-domain books, official/legal texts, filtered web text and other plausible collections. Read primary licence texts, cards and papers directly, in Turkish where applicable. Search snippets are discovery only.
3. Use #53's requested fields: name, kind, URL, exact licence/version/text, obligations, dataset versus underlying rights, human-written evidence and automation risks, text dates, published size/citation, inferred tokens, acquisition and keep/reject/conditional disposition.
4. Read Law No. 5846 from an official source, cite article numbers, label interpretations `Inference:`, and state that the note is not legal advice. Missing evidence is a condition, not permission.
5. Do not download corpora. Any necessary sample must be below 100 MB, outside the repository and OneDrive, and deleted afterwards. Read-only metadata and primary documents may be retrieved.
6. Compare licence classes with the English note on the remote #53 branch if present, citing its immutable commit. Otherwise mark the ratio pending #53.
7. Read Hoffmann et al. (2022), arXiv 2203.15556, and Muennighoff et al. (2023), arXiv 2305.16264. Separate unique data, repeated presentations and bilingual mixture scenarios.
8. Audit citations, arithmetic, overlap and dash characters; run required checks; complete the plan; commit, push only this branch, and open one draft PR from the repository template with `Closes #54`. No issue comments, labels, assignments or merges.

No functions, classes, model runs or API changes are planned. Inputs are primary documents and repository requirements; outputs are two Markdown files and a draft PR. Owner decision documents and other checkouts stay unmodified.

## Mathematical / Statistical Details

Preregistered reading: distinguish published quantities and estimates. Label conversions and interpretations `Inference:`. Do not convert compressed bytes as plain text, or equate different tokenizers. State conversion assumptions and sensitivity bounds. Sum only compatible, non-overlapping estimates; unknown is unquantified, not measured zero. Separate permissive/public-domain, attribution, share-alike, restrictive and unverified rights, aligning classes with #53. Exclude ineligible sources from usable totals.

Inference: subject to confirmation in the paper, use about 20 training tokens per parameter as the compute-optimal starting point. Then 100M, 300M and 1B parameters require about 2B, 6B and 20B token presentations. For unique volume U and target D, presentations per token are D/U. Also show a stated bilingual Turkish fraction f, giving fD/U. Repetition is not new unique text. These papers do not certify Turkish task performance or device feasibility.

## Design Decisions

- Engineering default for review: retain traceable evidence; do not download corpora; flag missing counts and provenance. No novelty claims.
- Open for the owner: OD-3, public domain, attribution, share-alike, non-commercial restrictions and weight licensing. Conservative default: separate classes without clearing weights legally.
- Open for the owner: OD-4, bots, translations, post-AI text and model-based filtering. Conservative default: flag uncertainties; opaque crawls do not count as cleared human-written text.
- Open for the owner: OD-6 devices and model size, OD-7 tokenizer, and language sampling fraction. Conservative default: show scenarios without selecting these.
- Explicit task instructions override CONTRIBUTING's general start-comment and issue-question workflow. Record questions in this plan and the draft PR, without issue comments.

## Verification

Planned: count candidate sources examined and kept; record how every licence was read; enumerate unverifiable numbers; check numeric conversions and source overlap. Inspect diff and links, require no U+2013 or U+2014 in written files, and run `python -m pytest` as required by CONTRIBUTING. Confirm the plan-only first commit, only the two planned files changed, correct base, clean worktree and one draft PR.

Environment: owner's Windows laptop, hardware details to be recorded. Model size, training dataset and seeds: not applicable, no training experiment. No RESULTS entry is planned because this is a source survey without an experimental run. Results pending.

**Not tested:** exhaustive copyright clearance, source-wide human authorship, processing/deduplication, future tokenizer counts, training, bilingual task quality, local inference, post-AI web policy (#55), or pipeline work (#56).

## Related Docs

- [Issue #54](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/54), [English survey #53](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/53).
- [CONTRIBUTING](../../CONTRIBUTING.md), sections 3, 4, 5 and 8.
- [SRS](../SRS.md), D31, D32 and D45; [assistant specification](../assistant-spec.md), sections 6, 7 and 11.
- [Roadmap](../ROADMAP.md), steps 2.1 and 4.3; [Stage 0 plan](../PLAN.md).
- [Research note](../research/2026-10-25-turkish-pretraining-sources.md), to be written after this plan commit.
- [RESULTS](../../RESULTS.md), no experimental entry planned.
