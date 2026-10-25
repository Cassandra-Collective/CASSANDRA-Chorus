# 2026-10-25 · Research pools from the literature gaps

| | |
|---|---|
| PLAN step | none; research track, issue #105 |
| Branch | `research/105-research-pool-proposals` |
| SRS requirements | S0-N-07 and research pre-registration under CONTRIBUTING section 5; no requirement changed |
| Status | Verified as documentation on 2026-10-25; no research runs performed |

Research and writing only, after the #104 draft PR. No experiment is launched.

## Problem / Motivation

The literature report's section 6 contains twenty numbered gaps and a further list of questions described as requiring code. Issue #105 asks for one proposal per gap with a question, runs and pre-registered reading. Several questions overlap existing issues or depend on data not in git. The proposals must preserve those dependencies and correct feature assumptions against the current harness.

## What Changed

| File | Description |
|---|---|
| `docs/implementations/2026-10-25-research-pool-proposals.md` | Plan and later verification record. |
| `docs/research/2026-10-25-research-pool-proposals.md` | Gap-by-gap proposals, summary table and dependency map. |

## Implementation Approach

1. Start again from origin/main a30dd6a in a fresh worktree outside OneDrive. Re-read CONTRIBUTING.md and both templates. Commit this completed plan alone before the note.
2. Inventory gaps 1 through 20 and each distinct semicolon-delimited new-code item, including the final centralized-sensitivity item. Use stable G01-G20 and N01-N14 identifiers and preserve overlap rather than silently dropping items.
3. Audit actual options and script restrictions. Cross-reference #87 for B1-1 through B1-5, #88 for H and AdamW state, #103 for re-scoring, and draft [PR #128](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/pull/128) for remedies.
4. Give every proposal a question, arms, seeds, configuration changes, existing-option or new-code status, dependencies, and an explicit if/then/if-not reading that can be fixed before running. Mark every Group B proposal as needing the owner's local data. Distinguish missing historical measurements from measurements that can be recovered.
5. Do not reuse unverified literature numbers. Refer primary evidence to the checked #104 note; read a primary paper directly if adding any other empirical number. Stop if arXiv is inaccessible or the literature report is missing.
6. Verify completeness, links, configuration semantics, run arithmetic, no forbidden dash characters and two-file scope. Reuse the completed 339-test run from #104 only after proving code and tests are identical; repeat only for a changed code tree or a new concern. Complete Verification, commit, push this branch and open a draft PR with Closes #105.

No functions or classes are changed. Inputs are the report, checked source evidence, issue descriptions and repository code. Output is a proposal inventory. Side effects are two documentation commits and one draft PR; no result artifacts or owner decision documents change.

## Mathematical / Statistical Details

Use paired per-seed bpc differences dP=P-F and dM=S-P, with three seeds 7, 11 and 19 for new screens. Preserve #87's authorized seed-7 scope rather than silently expanding it. Proposed numeric grids and counts are Inference, not literature results or power calculations. Preserve worker-step totals using workers times H times rounds; do not equate them with FLOPs. For analyses, avoid interpolation outside observed validation ranges and distinguish association from causation. Each reading names an observable condition and its limited conclusion; mixed or missing data do not establish equivalence.

## Design Decisions

- Keep one proposal for every source item, even when two share an implementation or existing issue. Cross-link them; do not budget duplicates as independent work.
- Conservative default: existing options and local-data inventory first; implementation and training remain future work.
- Open for the owner: pool order, resource budgets, practical-effect thresholds, network readiness and whether to extend #87 beyond seed 7.
- Open for the owner: access to local data, approval of surrogate Task A versus new text8 skew code, compute accounting, new algorithm contracts and adoption gates.
- The objective explicitly forbids issue comments, labels and assignments. Unsettled decisions go here and in the PR's Questions for the owner, not in owner documents. Never merge.

## Verification

Observed on 2026-10-25:

- First commit `e91af05` contains this plan alone. The note was written afterward. Both branches start from main `a30dd6a`; #104's draft PR #128 was opened before this branch was created.
- Checked the source inventory: twenty numbered gaps, thirteen additional items after removing citation separators, plus the appended centralized-sensitivity question. A document audit confirmed G01-G20 and N01-N14 each appear exactly once as detailed proposals and once in the summary table. All 34 entries contain Question, Runs, Dependency and an explicit conditional Reading. G12-G17 each state that they need the owner's local data.
- Reviewed #87/#88/#103 mappings, shared controls, seeds and proposed run counts. Read the report's final new-code list item by item; no source gap is silently dropped when current code changes its classification.
- CPU configuration checks validated the H and 2/4/8-worker grids, outer lr 1.6, all forty heterogeneous rolling assignments having exactly two holders per expert, and decay schedules of 40/72/36 rounds at final H off/25/250. No training was launched for these checks.
- `git diff --check`: passed. The two written files contain no U+2013 or U+2014. All relative Markdown links resolve. Final changes are restricted to this plan and the note.
- `git diff research/104-sliced-moe-remedies HEAD -- cassandra_chorus scripts tests configs pyproject.toml` is empty. The same unchanged code and test suite passed `python -m pytest` during #104: **339 passed**, two intentional warning-capture warnings, 310.30 seconds, CPU and CUDA. Reused this observed result rather than rerunning an unchanged suite for prose. Hardware: Windows reference laptop, Intel Core i7-13650HX, NVIDIA GeForce RTX 4070 Laptop GPU; Python 3.13.14 and PyTorch 2.12.1+cu126. No claim is made that the suite implements or tests these proposed algorithms.
- Primary evidence reused by reference from #104: seven versioned arXiv HTML sources read directly. No new empirical literature number is added by this note.

Target setting unless explicitly changed: Task B text8, 46,050,432 parameters, seeds 7, 11 and 19. Task A is explicitly marked where text8 options do not exist. No research measurements are produced.

**Not tested:** proposed outcomes, new algorithms, historical artifact completeness, live network availability, hardware budgets and empirical power.

## Related Docs

- [Literature report](../research/2026-10-11-stage0-literature-report.md), section 6; [Stage 0 report](../stage0-report.md); [closeout](../stage0-closeout.md), section 4.
- [Batch 1 plan](2026-10-13-averaging-gap-batch-1.md); [CONTRIBUTING.md](../../CONTRIBUTING.md).
- Issues [#105](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/105), [#87](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/87), [#88](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/88), [#103](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/103); remedies [PR #128](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/pull/128).
