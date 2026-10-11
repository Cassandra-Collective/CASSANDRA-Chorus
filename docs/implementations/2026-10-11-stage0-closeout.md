# 2026-10-11 · Stage 0 close-out record

| | |
|---|---|
| PLAN step | After step 12; the project is parked by the owner |
| Branch | `stage0/closeout` |
| SRS requirements | S0-N-07 (state limits); decision D28 |
| Status | Written and checked |

## Problem / Motivation

The owner parked the project after Gate B and asked for everything to be documented honestly before work resumes later. The report (`docs/stage0-report.md`) covers the findings. Several other things would otherwise exist only in conversation or on the laptop:

- what went wrong during the work;
- which state is not in git;
- what was deliberately deferred.

## What Changed

| File | Description |
|---|---|
| `docs/stage0-closeout.md` | The close-out record. It covers where things stand and what exists. It records the plan changes, the power problems and the mistakes made during the work with their fixes. It also covers what lives only on the laptop, what is left for later, and how to pick the work up again. |
| `README.md` | Links the close-out record next to the report. |

## Implementation Approach

The record states facts from the committed record, the run logs and a fresh inventory of the laptop:

- the run, data, queue, backup and worktree folders;
- the local branches;
- `ops.local.toml`.

It does not restate memory. The mistakes are listed whether or not they reached a result, with where each was caught.

## Design Decisions

| Decision | Chosen | Alternatives | Decided by |
|---|---|---|---|
| A separate close-out file | Yes, next to the report | Fold it into the report | Engineering default: the report is for outside readers; the close-out is for whoever resumes the work |
| List mistakes that never reached a result | Yes | Only those that did | Owner's request for an honest record |

## Verification

- `python -m pytest` on `main` at `a31d8f5`: 277 passed (CPU and GPU), run on 2026-10-11 for this record.
- **Inventory:** 66 run folders (5.2 GB), 4 local queue files, 2 recovery files, 6 bundles, 1 old worktree, 15 local branches, all merged into `main`.
- **Every claim checked against its source.** The check corrected two statements in the draft:
  - the parent model's size ratio (about 4.4, not 4);
  - which documentation slips had been committed.

## Related Docs

- `docs/stage0-report.md`
- `RESULTS.md`
- `docs/SRS.md` section 9 (decisions D1 to D28)
