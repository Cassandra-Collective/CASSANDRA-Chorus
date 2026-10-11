# 2026-10-11 · Stage 0 technical report: a negative result (PLAN step 12)

| | |
|---|---|
| PLAN step | 12 · Decision gate B: write-up of Stage 0 |
| Branch | `stage0/12-report` |
| SRS requirements | S0-N-07 (results state their limits); decisions D24, D28 |
| Status | Planned |

## Problem / Motivation

The owner decided Gate B on 2026-10-11 (D28): a large gap. Stage 0 is to be written up as a negative result, and the architecture reconsidered before any Stage 1 work. PLAN section 5 asks for a negative result written with the same care as a positive one.

The evidence is spread over:

- `RESULTS.md` (dated entries);
- three results files;
- the SRS decision log;
- about twenty implementation documents.

A reader outside the project, such as an academic advisor, needs one short document. It must say what was asked, what was done, what was found and what it does not show.

## What Changed

To be completed after writing. Planned:

| File | Description |
|---|---|
| `docs/stage0-report.md` | The report, about 3,000 words, English, for an academic reader. |
| `README.md` | A pointer to the report. |

## Implementation Approach

The report is written from the committed record only (`RESULTS.md`, `results/*.md`, the SRS and PLAN). Every number carries its source, and nothing is restated from memory. Outline:

1. **Summary:** the question, the method in two sentences, the two gates and their outcomes.
2. **Question and setting:** the Chorus goal; sliced local training; why Stage 0 simulates it on one machine.
3. **Method:** the model, the protocol and merge rules, the arms, equal compute, the two tasks, the measures, and the criteria and readings registered before the runs.
4. **Results:**
   - Gate A on Task A (criteria, the redundancy finding, comparison arms, probe);
   - Task B on text8 (per-seed table, verdict, decomposition).
5. **Discussion:** the two measured costs and what each points to. Relation to prior work, with the survey's provenance caveats and no novelty claim.
6. **Limits and what was not tested** (S0-N-07).
7. **Reproducing the results:** commits, configurations, scripts.
8. **What comes next:** the architecture is to be reconsidered. This section gives pointers only; no design decision is made in the report.

## Design Decisions

| Decision | Chosen | Alternatives | Decided by |
|---|---|---|---|
| Write up as a negative result | Yes | Moderate-gap report | Owner, 2026-10-11 (D28) |
| Form and place | Markdown in the repository, `docs/stage0-report.md` | A shared document outside the repository | Engineering default, stated to the owner: it lives with the results it cites. A shareable copy can be made from it |
| Audience and length | Academic reader, about 3,000 words | Internal notes; a full paper | Engineering default from the project's purpose (a proposal to an academic collaborator), stated to the owner |
| Claims | Results with their limits; no novelty claim | | Owner's working rules (no novelty claims; S0-N-07) |

## Verification

To be completed after writing: every number in the report checked against its source file.

## Related Docs

- `RESULTS.md`, `results/task_a_gate_a.md`, `results/task_a_redundancy_probe.md`, `results/task_b_gate_b.md`
- `docs/SRS.md` (section 4.4, decisions D10 to D28), `docs/PLAN.md` (section 5)
- `docs/prior-work.md` (survey and its caveats)
