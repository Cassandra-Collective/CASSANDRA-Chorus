<p><a href="https://github.com/Cassandra-Collective"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Cassandra-Collective/.github/main/brand/svg/cassandra-mark-small-on-dark.svg"><img src="https://raw.githubusercontent.com/Cassandra-Collective/.github/main/brand/svg/cassandra-mark-small-on-light.svg" alt="Cassandra Collective mark" width="20" height="20" align="absmiddle"></picture></a>&nbsp; Part of the <a href="https://github.com/Cassandra-Collective">Cassandra Collective</a></p>

# CASSANDRA Chorus

CASSANDRA Chorus is the next phase of the [CASSANDRA](https://github.com/Cassandra-Collective/CASSANDRA) low-hardware language-model research program. The long-term goal is a language model trained by a pool of volunteer machines, where no machine holds the whole model during training, and where the full pipeline, logs and weights are open. No token or cryptocurrency is involved; contribution is tracked in a plain credit ledger.

The model is a mixture-of-experts transformer. Each worker trains the shared part of the model plus a subset of the experts locally, and a coordinator merges the results ("sliced local training"). Whether this works for a language model is the open question that Stage 0 tests, on a single machine, before any pool infrastructure is built.

## Status

Stage 0 is complete and closes as a negative result (decision D28, 2026-10-11).

- **Synthetic task (Gate A): passed.** Sliced training matched centralized accuracy, but its experts became interchangeable.
- **Text8: the 5% criterion is missed on every seed.** Sliced training is +10.8% in bits per character behind a centralized model of the same size at equal compute. About 6 points of that come from local averaging itself, about 3 from routing restricted to each worker's slice, and about 1.4 from partial expert updates.

The architecture is to be reconsidered before any networked stage. Read [`docs/stage0-report.md`](docs/stage0-report.md) first.

## Documents

- [`docs/stage0-report.md`](docs/stage0-report.md): the Stage 0 technical report (start here)
- [`docs/stage0-closeout.md`](docs/stage0-closeout.md): close-out record. Where the work stands, what went wrong and how it was handled, what is left for later
- [`docs/SRS.md`](docs/SRS.md): software requirements specification
- [`docs/PLAN.md`](docs/PLAN.md): plan memo, stages and Stage 0 work breakdown
- [`docs/implementations/`](docs/implementations/): one document per change
- [`RESULTS.md`](RESULTS.md): hand-written record of runs that inform decisions
- [`results/`](results/): generated tables (Gate A, redundancy probe, Task B)

## Running

Requirements: Python 3.13, PyTorch 2.12 with CUDA, NumPy 2.4, and pytest for the tests. Everything runs from the repository root without installing the package.

Raw run logs and checkpoints are not committed. They go to the folder named by the `CHORUS_RUNS_DIR` environment variable, or to `runs/` in the repository if it is not set. Keep that folder outside OneDrive and, with the Microsoft Store build of Python, outside `AppData`. To set it permanently for your Windows user (PowerShell, then open a new terminal):

```powershell
[Environment]::SetEnvironmentVariable("CHORUS_RUNS_DIR", "C:\Users\senso\chorus-runs", "User")
```

Run the tests (the GPU tests are skipped when CUDA is not available):

```powershell
python -m pytest
```

Machine-level run settings (keep-awake, power logging, pre-start checks such as "runs folder not in OneDrive", "GPU idle" and scheduled tasks to avoid) live in an optional, gitignored `ops.local.toml`. Copy `ops.example.toml` to `ops.local.toml` and adjust it. Long runs should be started in a visible window, which also keeps a transcript under `<runs folder>\launcher_logs`:

```powershell
powershell -File scripts\ops\launch_visible.ps1 -Module scripts.train_task_a_centralized -Arguments "--config configs/task_a/centralized.toml --set run.seed=11" -RunsDir C:\Users\senso\chorus-runs
```

Keep the screen on when starting a long run. The run holds a keep-awake request from launch, which stops Windows from going into standby, but cannot wake the machine once it is already in standby.

Smoke check of the run pipeline (prints the run folder and a checksum; the same seed gives the same checksum):

```powershell
python -m scripts.smoke --config configs/smoke.toml
python -m scripts.smoke --config configs/smoke.toml --set run.seed=11
```

## Licence

Apache License 2.0. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).
