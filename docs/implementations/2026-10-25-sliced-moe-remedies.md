# 2026-10-25 · Candidate remedies for sliced MoE training

| | |
|---|---|
| PLAN step | none; research track, issue #104 |
| Branch | `research/104-sliced-moe-remedies` |
| SRS requirements | Evidence for S0-F-05, S0-F-10 and S0-N-07; no requirement or owner decision changed |
| Status | Verified as documentation on 2026-10-25; no research runs performed |

Research and writing only. No training runs are part of this task.

## Problem / Motivation

Issue #104 asks which literature remedies could address the partial-update and masked-routing costs measured in Stage 0. Published settings differ from ours. Each proposed pool needs a checked source, a feasible intervention, controlled runs and a reading fixed before running.

## What Changed

| File | Description |
|---|---|
| `docs/implementations/2026-10-25-sliced-moe-remedies.md` | This plan and its later verification record. |
| `docs/research/2026-10-25-sliced-moe-remedies.md` | Planned shortlist, primary-source evidence, harness audit and proposed pool split. |

## Implementation Approach

1. Start from origin/main a30dd6a in a fresh worktree outside OneDrive. Read CONTRIBUTING.md, the templates, literature report and overlapping issues.
2. Read primary arXiv HTML or PDFs for shortlisted papers. Record version, locator, setting, scale and raw effect. Label derived numbers `Inference:`. Stop if the report is missing or arXiv is inaccessible.
3. Audit SimSection, assignment, worker training, model configuration and Task B scripts. Name existing options and files that would need new code.
4. Specify arms, seeds 7, 11 and 19, configuration changes, dependencies, pre-registered readings and estimated run counts. Itemize any shared controls.
5. Write the note, complete verification, commit, push this branch and open a draft PR from the repository template with Closes #104. Never merge.

No functions or classes change. Inputs are primary papers and repository evidence at the stated base. Output is proposals, not results. Side effects are documentation commits and a draft PR.

## Mathematical / Statistical Details

Use paired per-seed bpc differences. State whether a relative cost uses centralized bpc or the preceding arm as denominator. Convert published perplexity only as `Inference: 100 * (ln(P_new) / ln(P_control) - 1)`. This is not a transferable effect across datasets. Run estimates are arm configurations times three seeds, with control reuse explicit. A consistent direction in three seeds is a screening reading, not a significance test or equivalence claim. Missing or failed seeds make the comparison incomplete.

## Design Decisions

- Conservative scope: shortlist partial-update and masking remedies; refer averaging-only work to #87 and #88.
- Prefer existing options for the first pool. New algorithms need separate implementation plans and tests.
- Open for the owner: priority, budget, acceptable memory and extra-compute costs, and new-code work to commission.
- Open for the owner: practical-effect thresholds and adoption gates. Proposals use directional screening only.
- The objective overrides contribution rules on issue comments and questions: do not comment, label or assign; put unresolved choices here and in the PR's Questions for the owner. Do not change SRS, ROADMAP, ARCHITECTURE or the literature report.

## Verification

Observed on 2026-10-25:

- First commit `6c01042` contains this plan alone, before the note was created. The final scope is the two files listed above.
- Read seven primary arXiv HTML documents directly, including setup, methods and the cited tables; checked that all seven cited table anchors exist in the fetched HTML. The note names versions and source limits. No search snippet supplies a number.
- Audited configuration fields and worker, assignment, merge and gate semantics. A CPU check validated 48 combinations of capacity, mode and assignment; confirmed pinned rolling assignments match from round 0 to 39; and validated the 2/4/8-worker fixed-step settings. This checks configuration feasibility, not training behavior.
- Reviewed every run estimate as configurations times three seeds and itemized shared controls. SPES score arithmetic is 50.95 - 48.99 = 1.96 points.
- `git diff --check`: passed. `rg -n -P '[\x{2013}\x{2014}]'` on both written files: no matches. All relative Markdown links resolve.
- `python -m pytest`: **339 passed**, two intentional warnings from the warning-capture test, 310.30 seconds. Windows reference laptop, Intel Core i7-13650HX and NVIDIA GeForce RTX 4070 Laptop GPU; Python 3.13.14, PyTorch 2.12.1+cu126. The suite includes CPU and CUDA tests, including synthetic model training; it is not a Task B remedy experiment.

No experiment has run. Target: Task B text8, 46,050,432 parameters, four simulated workers unless stated, seeds 7, 11 and 19. Document verification cannot establish remedy effects.

**Not tested:** new implementations, training outcomes, network performance, external paper reproducibility and the owner's saved artifacts.

Unverified source details: SPES released-code defaults and their relation to Table 4, FoMoE random-placement timing, and figure-only effects. They are not used as measured support for a selected setting.

## Related Docs

- [Literature report](../research/2026-10-11-stage0-literature-report.md), sections 3.2, 3.3, 3.5, 4, 6 and 7.
- [Stage 0 report](../stage0-report.md), [closeout](../stage0-closeout.md) and [batch 1 plan](2026-10-13-averaging-gap-batch-1.md).
- [CONTRIBUTING.md](../../CONTRIBUTING.md).
- Issues [#104](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/104), [#87](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/87), [#88](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/88) and [#103](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/103).
