# 2026-10-25 · Turkish pretraining sources survey

| | |
|---|---|
| PLAN step | None in Stage 0; roadmap 2.1b, issue #54 |
| Branch | `research/54-turkish-sources` |
| SRS requirements | D31, English and Turkish; D32, open-licensed human-written text; D45, owner decisions |
| Status | Verified on Windows on 2026-10-25; primary-source research, arithmetic and repository tests complete |

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

Research outcome: 13 candidate sources examined, 7 conditional keeps, 6 rejects and no unconditional training approvals. Two quantified retained leads give a gross 0.249084794 to 0.561142907B Turkish-token scenario before exclusions. The English ratio is included using remote commit `e637be6b87af34d065f95c7511e7d65ed0f5d8b1`; this is a comparison of conditional scenarios, not measured usable corpora. The note includes model-size and repetition tables for 100M, 300M and 1B parameters, with an explicitly illustrative bilingual share.

Licence verification: fetched and read primary legal texts for CC BY 4.0, BY-SA 3.0, BY-SA 4.0, BY-NC-SA 4.0, CC0 1.0, ODC-By v1.0 and Common Crawl terms. Read Turkish Law 5846 from the Ministry of Culture's linked official PDF, including articles 6, 8, 14 to 19, 26, 27, 31, 32, 46, 47 and Additional Article 2; cross-checked relevant provisions in the ministry's English counterpart. Compared those texts with each source's publisher statement. TNC's full agreement could not be read and that route is rejected. No underlying rights were inferred from a database licence. Wikipedia's stale 3.0 card versus the post-transition 4.0 source terms and ParlaMint's underlying speech-rights condition are explicitly recorded.

Unverified quantities and rights: the note's Verification section lists them per source. They include final Chorus tokenizer counts, retention fractions, overlap, human-authorship contamination, unquantified books/legal/journal volumes, source-wide dates and rights, some archive byte totals, inaccessible bulk routes, TNC terms, statutory consolidation through every amendment, territorial clearance and weight rights. The live Wikipedia aggregate mean is rounded and not commit-addressed; the pinned card's matching article count was verified. No corpus or corpus-text sample was downloaded; only primary documents and metadata were fetched outside the repository and OneDrive.

Checks run on 2026-10-25:

| Check | Observed result |
|---|---|
| `python -m pytest -q` | 339 passed in 406.27 seconds; two warnings deliberately emitted by the warning-capture test. No source-code changes preceded or followed the run. |
| Python arithmetic audit | Recomputed full-split character estimate, per-source conversion intervals, non-additive alternative, class totals, interval-ratio extremes and all repetition scenarios. Published counts stay distinct from inferred tokens. |
| Reference/structure audit | 13 source-table rows, 7 C and 6 R; 45 external reference definitions, no undefined or unused reference labels; linked local documents exist. Failed external endpoints are explicitly documented. |
| Pinned Wikipedia card | HTTP 200 at `b04c8d1ceb2f5cd4588862100d08de323dccfbaa`; text matches the card read for the published counts. |
| `rg -nP '[\x{2013}\x{2014}]'` on both written files | No matches; no em or en dashes. |
| `git diff --check` and scope inspection | No whitespace errors; only this plan and the research note differ from the base. |
| Base and first commit | Fresh external worktree based on `a30dd6a804c50d895119abf182bad5a3fcbd5360`; `b4b7b34` committed the plan alone with the requested message. |

Environment: Windows 11, Intel Core i7-13650HX, NVIDIA GeForce RTX 4070 Laptop GPU with 8,585,216,000 reported device-memory bytes, Python 3.13.14, PyTorch 2.12.1+cu126, CUDA 12.6 and pytest 9.0.2. Test run/data paths were set outside OneDrive. Model size, training dataset and seeds: not applicable, no training experiment. No RESULTS entry because this is a source survey without an experimental run.

Delivery: commit the completed plan and note with `Turkish pretraining sources survey (#54)`, push only `research/54-turkish-sources`, and open one draft PR from the repository template with `Closes #54` and the owner questions. Final remote-state and clean-worktree verification follows that commit; no merge or issue mutation is authorized.

**Not tested:** exhaustive copyright clearance, source-wide human authorship, processing/deduplication, future tokenizer counts, training, bilingual task quality, local inference, post-AI web policy (#55), or pipeline work (#56).

## Related Docs

- [Issue #54](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/54), [English survey #53](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/53).
- [CONTRIBUTING](../../CONTRIBUTING.md), sections 3, 4, 5 and 8.
- [SRS](../SRS.md), D31, D32 and D45; [assistant specification](../assistant-spec.md), sections 6, 7 and 11.
- [Roadmap](../ROADMAP.md), steps 2.1 and 4.3; [Stage 0 plan](../PLAN.md).
- [Research note](../research/2026-10-25-turkish-pretraining-sources.md), to be written after this plan commit.
- [RESULTS](../../RESULTS.md), no experimental entry planned.
