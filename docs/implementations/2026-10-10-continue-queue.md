# 2026-10-10 · Continue a run matrix after an interruption

| | |
|---|---|
| PLAN step | 10 (supports the Task B matrix); operations tooling |
| Branch | `stage0/10-task-b` |
| SRS requirements | S0-N-04 (resumable runs), S0-N-08 (every run logged) |
| Status | Planned |

## Problem / Motivation

The Task B matrix runs unattended for about 20 hours while the owner travels, possibly without internet, so no one can restart it by hand with help. Interruptions have already happened:

- the mains supply failed and the battery ran down to 1%;
- the matrix was parked twice.

Each restart so far needed a queue file written by hand: resume the unfinished run, then the remaining entries. After a shutdown or a Windows restart, the owner needs one action that works out what is left and continues it. This must not depend on Claude being reachable.

## What Changed

To be completed after implementation. Planned:

| File | Description |
|---|---|
| `scripts/ops/continue_queue.py` | Reads a matrix queue file, works out from the runs folder what is finished, writes the remaining work as a queue, and runs it. |
| `tests/test_continue_queue.py` | The planning logic on synthetic run folders. |
| `C:\Users\senso\chorus-runs\CONTINUE_TASK_B.cmd` | Local only, not committed: a double-click launcher for the Task B matrix. |

## Implementation Approach

For each entry of the committed matrix queue, in order:

1. Its run name and seed come from its configuration file plus its `--set` overrides, read with the same functions the scripts use (`read_config_file`, `apply_overrides`).
2. Its run folders are those named `<time>_<name>_s<seed>` (`make_run_id`).
3. **Completed** (the log's last `end` record has status `completed`): skipped.
4. **Unfinished** (no completed end) with a `checkpoint.pt`, and a script that accepts `--resume` (the `*_sliced` scripts): the newest such folder is resumed (`--resume <folder>`).
5. **Otherwise:** run from the start. An unfinished centralized run cannot resume. Its folder stays as a record and has no completed end record, so the analysis ignores it.

The remaining entries go to `<runs>/queues/<queue name>_continue_<time>.toml` with `stop_on_failure = false`, so one failed run does not stop the rest, and the queue runner runs it.

The tool refuses to start while any process is computing on the GPU, so it cannot resume a run that is still running. `--dry-run` prints the plan without running it.

## Design Decisions

| Decision | Chosen | Alternatives | Decided by |
|---|---|---|---|
| Source of truth | The committed matrix plus the run logs | A state file kept by the queue runner | Engineering default: the run logs already say what finished; no new state to keep consistent |
| On failure | Continue with the next entry | Stop the queue | Owner's request on 2026-10-10: runs must continue unattended |
| Start trigger | The owner double-clicks the launcher after a restart | A scheduled task that starts at logon | Engineering default: a scheduled task is persistent system configuration, the owner's to choose |

## Verification

To be completed after implementation.

## Related Docs

- `docs/implementations/2026-10-08-run-operations.md` (launcher, preflight)
- `docs/implementations/2026-10-09-task-b-runs.md` (the matrix)
