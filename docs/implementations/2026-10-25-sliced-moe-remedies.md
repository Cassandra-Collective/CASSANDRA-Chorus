# 2026-10-25 · Candidate remedies for sliced MoE training

| | |
|---|---|
| PLAN step | none; research track, issue #104 |
| Branch | `research/104-sliced-moe-remedies` |
| SRS requirements | Evidence for S0-F-05, S0-F-10 and S0-N-07; no requirement or owner decision changed |
| Status | Planned; plan committed before the research note |

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

Planned: primary-source and numeric locator audit; option semantics and run-count review; `git diff --check`; U+2013/U+2014 scan of both written files; `python -m pytest`; first-commit and final-diff scope check. Record observed results and hardware after writing.

No experiment has run. Target: Task B text8, 46,050,432 parameters, four simulated workers unless stated, seeds 7, 11 and 19. Document verification cannot establish remedy effects.

**Not tested:** new implementations, training outcomes, network performance, external paper reproducibility and the owner's saved artifacts.

## Related Docs

- [Literature report](../research/2026-10-11-stage0-literature-report.md), sections 3.2, 3.3, 3.5, 4, 6 and 7.
- [Stage 0 report](../stage0-report.md), [closeout](../stage0-closeout.md) and [batch 1 plan](2026-10-13-averaging-gap-batch-1.md).
- [CONTRIBUTING.md](../../CONTRIBUTING.md).
- Issues [#104](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/104), [#87](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/87), [#88](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/88) and [#103](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/103).
