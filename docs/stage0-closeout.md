# CASSANDRA Chorus · Stage 0 close-out record

Written 2026-10-11, when the owner parked the project after Gate B. This is the plain record of where everything stands:

- what exists;
- what went wrong along the way and how it was handled;
- what lives only on the reference laptop;
- what was deliberately left for later.

The findings themselves are in [`stage0-report.md`](stage0-report.md); this file is about the state of the work.

## 1. Where things stand

- **Stage 0 is closed as a negative result** (owner decision D28, 2026-10-11).
  - Gate A passed with a recorded finding (D24): sliced training matched centralized accuracy on the synthetic task, but its experts became interchangeable.
  - Gate B: on text8, sliced training is +10.8% in bits per character behind centralized on every seed, against an allowance of +5%.
- **The architecture is to be reconsidered before any networked stage.** That work has not started.
- **Repository:** everything is merged to `main` (PRs #1 to #14; last merge `a31d8f5`). There are no open PRs and no unmerged branches.
- **Tests:** `python -m pytest` on `a31d8f5`: 277 passed, CPU and GPU, on the reference laptop (RTX 4070 Laptop GPU).
- **Nothing is running.** The GPU is idle and no queue is active.

## 2. What exists

| Area | Where | Notes |
|---|---|---|
| Model | `cassandra_chorus/model/` | Mixture-of-experts transformer with a maskable router; sparse and dense dispatch |
| Data | `cassandra_chorus/data/` | Task A synthetic maps; text8, hash-checked |
| Coordinator | `cassandra_chorus/coordinator/` | Slice assignment (random, coverage, rolling) and merge rules. Free of simulation code, for reuse in a networked stage |
| Simulation | `cassandra_chorus/sim/` | Sequential workers in three modes (sliced, partial update, full averaging), faults, skew, resumable rounds |
| Metrics | `cassandra_chorus/metrics/` | Task A accuracy and routing measures, Gate A criteria, redundancy probe, bits per character |
| Operations | `cassandra_chorus/ops/`, `scripts/ops/` | Keep-awake, power logging, pre-start checks, visible launcher, run queues, continue-after-interruption |
| Run scripts | `scripts/` | Task A and Task B, centralized and simulated; timing pilot; analyses |
| Configurations | `configs/` | Every gated run is reproducible from a configuration and a seed |
| Records | `RESULTS.md`, `results/`, `docs/implementations/` | Every run that informed a decision, with its commit; one document per change |
| Decisions | `docs/SRS.md` section 9 | D1 to D28, each with who decided and when |

## 3. What did not go as planned, and how it was handled

### 3.1 Plan changes (all decided by the owner and recorded)

- **Gate A gained a step.** Before Gate A, a check run hinted that sliced experts were redundant. The reading of that case was registered before the Gate A runs (D23). After Gate A, the owner added a redundancy probe (step 9a, D24). Its reading was also registered before any probe number existed.
- **Task B gained a balance loss.** A learning check at the Task A setting (no balance loss) showed routing collapsing onto 3 to 5 of 8 experts per layer, so all Task B arms used a Switch balance loss of 0.01 (D27). Task A ran without it.
- **The sweeps of PLAN step 11 were never run.** Gate B was decided first (D28). The report therefore cannot say how much of the 6.1% local-averaging cost fewer local steps or an outer optimizer would remove.

### 3.2 The laptop's power supply

The mains adapter dropped out under load throughout Stage 0: hundreds of short drop-outs per Task B run. The battery handover is unreliable: unplugging once switched the laptop off. Effects:

- **Step 4:** runs froze in Modern Standby for between 21 minutes and about 5 hours. Starting runs in a visible window with the screen on and keep-awake held stopped this.
- **Task B, run 4:** an outage ran the battery to 1% and froze the run for 1.9 h.
- **Task B, run 12:** froze for 7.0 h in standby.
- **The timing pilot** ran under drop-outs, so its medians are inflated. Both medians and minima were reported.
- **The matrix was parked twice** at the owner's request (travel). One run resumed from its checkpoint.

Training is deterministic, so none of this changed a result. Each event is in its run's log. The hardware fault itself is not fixed. The owner reconnected the charger, but the adapter or the battery's handover circuit should be serviced before further long runs.

### 3.3 Mistakes made during the work, and their fixes

These were caught before they reached a reported result unless stated otherwise:

- **Routing necessity mixed two evaluation sets** in the first Gate A analysis code: trained accuracy on one set, random routing on another. Fixed before the Gate A report.
- **The probe's specialization measure** first counted maps that are simply harder as specialization. A unit test caught it before any real model was probed.
- **The Stage 0 report's first draft had five factual slips**, from a wrong range to a misattributed decision. All were found in a line-by-line check against the sources and fixed before merging. They are listed in `docs/implementations/2026-10-11-stage0-report.md`.
- **Smaller documentation slips:**
  - a wrong GPU name (RTX 4060), committed and fixed in the next commit;
  - a wrong commit hash and a wrong evaluation-set size (2,000 instead of 256 per map), both caught before committing.
- **In conversation, one claim was retracted the same turn:** that the battery was draining during the learning check. The log showed it charging.
- **An untested work-in-progress commit** was squashed into a tested one on an unpushed branch, which rewrote local history once.
- **The launcher's transcript turned out not to capture Python's output.** One wait loop relied on it and was replaced. Progress is now read from files the runs write.
- **The pre-start check's time estimate** (0.15 s per step) fits Task A, not Task B, so it could not protect a long Task B run from a scheduled task. It was not updated. The scheduled task in question (MUSAHIT) turned out to be broken and was removed from the avoid list by the owner.
- **A stacked-PR merge closed a dependent PR** (owner's merge of PR #1 deleted its branch). PR #2 was restored and retargeted. Later merges retargeted each PR to `main` first.

### 3.4 Things that are true but easy to miss

- The partial-update and full-averaging arms equal the sliced arm in steps and sequences only. Their workers hold all 8 experts, and on Task A they also did about twice the expert computation.
- One sliced Task B run (seed 11) has one expert below the 0.025 usage line. Every other expert of the 12 runs is above it.
- Validation figures (the first 1M validation characters) and test figures (the whole test split) are different sets. Only the test figures enter S0-A-04.
- The centralized Task B model reaches 1.435 to 1.439 test bits per character. It is not comparable with the parent CASSANDRA model's 1.336, which is about 4.4 times larger, dense, and trained on more characters.
- Run 4's first segment wrote no power summary because it was stopped. Its outage is recorded as a `stall` record.

## 4. What lives only on the reference laptop (not in git)

| Item | Location | Notes |
|---|---|---|
| Run logs and saved models | `C:\Users\senso\chorus-runs\` (66 run folders, 5.2 GB) | The primary record behind every number. Only on this laptop and in no backup. |
| text8 copy | `C:\Users\senso\chorus-data\text8\text8` | Copied from the parent project; its SHA-256 is in every Task B configuration |
| Queue files | `C:\Users\senso\chorus-runs\queues\` | Local resume queues. Two have `stop_on_failure = false` (set for unattended running) |
| Recovery launcher | `C:\Users\senso\chorus-runs\CONTINUE_TASK_B.cmd`, `.ps1` | Double-click to continue an interrupted Task B matrix |
| Machine settings | `ops.local.toml` (gitignored) | Avoid list emptied on 2026-10-10 (MUSAHIT's folder no longer exists) |
| Git backups | `C:\Users\senso\chorus-runs\chorus-all-*.bundle` (6) | Superseded by GitHub; safe to delete |
| Old worktree | `C:\Users\senso\chorus-dev\stage0-next` | Branch `stage0/08-metrics`, merged; safe to remove |
| Local branches | 15 | All merged into `main`; safe to delete |
| Slide deck | claude.ai artifact (private) | 26 slides, updated 2026-10-11 with Task B, the gap breakdown and the Gate B decision. Shared only when the owner shares it from the page |

The run logs are the one item whose loss would matter. A copy outside the laptop would protect them.

## 5. Left for later (owner's choice, 2026-10-11)

1. **Reconsider the architecture** (D28). The report names where the measurements point:
   - the local-averaging share;
   - the masked-routing share;
   - the modular-paths fallback.

   No study has been planned yet.
2. ~~Update the slide deck~~ Done on 2026-10-11: Task B setup, results, gap breakdown and the Gate B decision were added, and the cover, stages, next-steps and open-questions slides brought up to date.
3. **Write the proposal brief** for the owner's friend at ODTU and her academic advisor, from the report.
4. **Have someone outside the project review the report.**
5. **Housekeeping:**
   - back up the run logs off the laptop;
   - remove the old worktree, merged branches and bundles;
   - get the charger and battery checked.

## 6. Picking the work up again

1. Read [`stage0-report.md`](stage0-report.md), then this file, then the latest entries of [`../RESULTS.md`](../RESULTS.md).
2. `git switch main && git pull`, then `python -m pytest`; 277 tests are expected to pass.
3. Long runs: start them through `scripts/ops/launch_visible.ps1` with the screen on. Set `CHORUS_RUNS_DIR` and `CHORUS_DATA_DIR` (the launcher's `-RunsDir` and `-DataDir`).
4. Any new direction starts with a plan document and the owner's decisions, as every step of Stage 0 did.
