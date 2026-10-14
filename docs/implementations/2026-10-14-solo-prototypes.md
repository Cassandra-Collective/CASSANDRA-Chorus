# 2026-10-14 · Prototypes the owner's machine can run alone (P3, P4, P5, P6, P8, P9)

| | |
|---|---|
| PLAN step | Roadmap Phase 1, evidence for step 1.3 (`docs/ROADMAP.md`); the prototypes of `docs/research/2026-10-13-system-study-report.md` section 6 |
| Branch | `proto/solo-prototypes` |
| SRS requirements | D37, D39, D40, D41 |
| Status | In progress. Verified on the reference laptop: P0, P4 (rerun), P6, P9; P3 smoke test only; P5 and P8 not started (see Verification) |

## Problem / Motivation

The system study recommends a "bulletin board" design (Option A): all exchange goes through public file hosts, every peer computes the merge, and a signed log, appended with conditional commits, records which updates count in each round. D41 does not adopt it yet. It first asks for the prototypes that the owner's laptop can run alone:

| ID | Question it answers |
|---|---|
| P3 | How long uploads and downloads of update-sized files take from this home, and which host should carry them |
| P4 | Whether conditional commits really stop concurrent writers from overwriting each other, so one counted set per round can be agreed |
| P5 | Whether the Hub tolerates the planned commit rate for a week |
| P6 | Whether every peer computes a bitwise identical merge, so equal hashes can prove agreement |
| P8 | Whether the candidate libraries install and import natively on Windows |
| P9 | Whether an offline-signed release and configuration can be verified by a client that holds only the public key |

Each one tests an assumption the design rests on (report section 4.7, "It depends on"). The architecture document (step 1.3) is drafted in parallel and names, section by section, the prototype it waits on.

**What one machine cannot settle.** These runs come from one home, one account, one GPU and one PyTorch build:
- equality across machines and PyTorch versions (P6);
- upload times from other homes (P3);
- write permissions of a second account (P4);
- the home reachability survey (P1, P2; not scheduled, D41).

Every result says so.

## What Changed

Planned files. Code is written after this plan, in the order P6, P9, then the token prototypes.

| File | Description |
|---|---|
| `scripts/proto/__init__.py` | Makes the prototypes importable by the tests. |
| `scripts/proto/common.py` | Shared prototype helpers: canonical model hash, safetensors round trip, result writing, and the Hub token guard (see "Token rules"). |
| `scripts/proto/p6_merge_determinism.py` | P6: the same merge computed under each variant below; compares canonical hashes. |
| `scripts/proto/p9_signing_dry_run.py` | P9: Ed25519 signing of a configuration and a release manifest; verification in a fresh isolated process; tampering tests. |
| `scripts/proto/p0_hub_scope_probe.py` | Step zero of the token prototypes: what the `chorus-prototypes` token may do. |
| `scripts/proto/p3_hub_transfer.py` | P3: timed uploads and downloads of 0.2 and 0.6 GB safetensors files, and the delay until another client sees each file. |
| `scripts/proto/p4_log_writers.py` | P4: concurrent conditional-commit writers on one branch; a race to close a round; visibility of a multi-file commit. |
| `scripts/proto/p5_commit_rate.py` | P5: a week at the planned commit rate. Resumable, with gaps recorded as data. |
| `scripts/proto/hub_cleanup.py` | Deletes the Hub repositories and buckets that these prototypes created, listed in a local manifest, and nothing else. |
| `tests/test_prototypes.py` | Unit tests for the canonical hash, the token guard and the signature checks. |
| `results/prototypes/` | One JSON and one Markdown file per prototype, plus `p4_attempt1_rate_limit.md`, the record of P4's first attempt. |
| `RESULTS.md` | One entry when the prototypes are done. |
| `docs/implementations/2026-10-14-solo-prototypes.md` | This document. |

P8 adds no repository file beyond its result. Its virtual environment lives in the session scratchpad.

## Implementation Approach

### P6. Merge determinism (no token)

**Inputs.**
- The Stage 0 Task B model (`configs/task_b/sliced.toml`, 46,050,432 parameters), initialized with seed 7. This is the global state G.
- Worker results are synthetic: G plus seeded Gaussian noise with standard deviation 1e-3 on every parameter the worker holds. The merge's arithmetic does not depend on how the change arose, and synthetic results make the test fast and exactly repeatable.
- Example counts are deliberately unequal and not powers of two (for example 4,000, 4,096, 3,900, 4,100, 3,987), so the weighting is exercised.

**Two work-unit kinds (D34):**
- **sliced:** 4 workers with capacity 4 under the `rolling` policy, which gives exactly 2 holders per expert;
- **full:** 5 workers, each holding the whole model.

**Outer steps:**
- plain averaging;
- Nesterov (lr 0.7, momentum 0.9) over two consecutive rounds, so the velocity carried from round 1 enters round 2.

**Variants**, each compared with the baseline (CPU, default threads, results in member-ID order, full states, files written to disk and read back):

| Variant | What could differ | Protocol rule it informs |
|---|---|---|
| The baseline twice | run-to-run nondeterminism | none if equal |
| CPU with 1 thread | thread partitioning of reductions | thread count is free or pinned |
| GPU (CUDA), twice | device arithmetic | which device may merge |
| Results shuffled before the merge, on CPU and on GPU | `_weighted_mean` sums in the order given: a peer that orders by download time sums differently | a canonical order of the counted set, for example by member ID |
| Updates shipped as deltas Δ_i = G − W_i (float32), rebuilt as W_i = G − Δ_i before merging; and a merge written directly in deltas | float32 rounding in the rebuild | whether the network ships full states or deltas |
| Nesterov velocity saved as float64 and as float32 between rounds 1 and 2 | precision of the stored outer state | the dtype of the published outer state |
| No file round trip (in memory only) | serialization | whether the file format is lossless here |
| GPU with the division done by a float64 tensor on the device, in member and in shuffled order (added after the toy-scale run found the GPU difference) | whether true division removes the GPU difference | the division rule |

**Outputs.** For every variant:
- the canonical hash of the merged state, and of the velocity after each Nesterov round;
- whether the hash equals the baseline's;
- if it does not, per tensor: the number of differing elements, the largest absolute difference and the largest relative difference.

**Canonical model hash.** This is the identity a peer would post in the log. It is defined over the tensors, not over file bytes, so that two correct safetensors writers cannot disagree. See the math section.

### P9. Signing dry run (no token)

- **Library:** Ed25519 from `cryptography`, already installed in the reference Python. Psyche signs with Ed25519 (report, w1c S1). `cryptography` is not yet a declared project dependency, so P8's install list includes it.
- **Key:** a throwaway key pair generated in the session scratchpad, never near `~/.ssh` or the repository. The real offline key procedure is an architecture-document item.
- **What is signed:**
  1. a run configuration file (JSON);
  2. a release manifest listing the SHA-256 of a release archive. The archive is made from this commit with `git archive`.
- **The rule tested:** **the signature covers the exact bytes of the published file.** A verifier checks the bytes first and only then parses them; nothing is re-serialized before checking. This removes any dependence on how JSON or floats are written. `config_hash` (canonical JSON, `cassandra_chorus/config.py`) remains the configuration's identity, but is not what the signature covers.
- **Verification:** in a fresh subprocess that is given only the files and the 32-byte public key. As run: `python -E -P` from an empty folder, not `python -I` (see Verification).
- **Negative tests, each of which must be rejected:**
  - one flipped byte in the configuration;
  - one flipped byte in the signature;
  - a truncated signature;
  - a wrong public key;
  - a manifest whose listed hash does not match the archive.

### Token rules for P0, P3, P4 and P5

- **Which token.** The prototypes load the token named `chorus-prototypes` from the Hub's stored-token file, by name. The owner's July token ("Mert Efe Sensoy") stays the active token for every other tool on the laptop. The token is never printed, logged or written to a result file.
- **Private API.** The lookup uses `huggingface_hub._login.get_stored_tokens`, a private path in version 1.24.0. That is acceptable for prototypes and must not be copied into the real client.
- **Guard.** Before any call that writes, the guard runs `whoami` with that token and refuses to continue if:
  - any scoped entity of type `user` carries a permission containing `write`;
  - any global permission contains `write`;
  - the target organisation is not among the scoped entities.
- **Target organisation.** A parameter (`--org`), set to `cassandra-chorus` (owner, 2026-10-14). The owner's account is an admin there.
- **Naming.** Every repository and bucket a prototype creates is private and named `proto-*`.
- **Clean-up.** Each creation is recorded in a local manifest under the runs folder. `hub_cleanup.py` deletes only what that manifest lists and only names starting with `proto-`. It runs at the end, after the owner has seen the results.

### P0. Scope probe (token)

The token's single organisation permission is `repo.contribute.write`, a name the Hub documentation does not define. (The closest documented term is the OAuth scope `contribute-repos`: "create repositories and access those created by this app".) The probe establishes, in order:
1. create a private repository `cassandra-chorus/proto-scope-probe`;
2. upload a small file;
3. read it back and list the files;
4. create a branch;
5. commit with `parent_commit`;
6. create a private Storage Bucket `cassandra-chorus/proto-bucket-probe` (does a free organisation get one?);
7. delete both.

Then one check that must fail: creating a repository in the owner's personal namespace. If it unexpectedly succeeds, the script deletes that repository at once and stops.

The probe cannot answer one question: whether this kind of token can write to a repository created by **another** account. D40's shared round log needs exactly that. It waits for a second account (a pilot friend).

### P3. Transfer from this home (token)

- **Sizes:**
  - 0.2 GB (Stage 0's model in float32 is 184 MB);
  - 0.6 GB (the report's update size).
- **Hosts:**
  - a private Hub repository (Xet storage);
  - a Storage Bucket, if P0 shows a free organisation can create one;
  - a GitHub release asset, only with the owner's separate approval, because it needs a throwaway GitHub repository on the owner's account.
- **Repeats:** 3 per size and host.
- **Measured:**
  - **upload time:** from the call until the commit or upload returns;
  - **visibility delay:** from that return until a separate process, with no cache, first sees the file in a listing, polling every 2 s;
  - **download time:** into an empty folder with the cache bypassed;
  - every HTTP 429 response and retry.
- **Xet deduplication**, on the Hub repository only. The 0.2 GB file is uploaded three ways:
  - identical to an earlier upload;
  - with every value perturbed slightly, as successive training updates are;
  - fresh random.

  This gives a first measurement of the report's open question whether Xet saves anything on successive updates.
- **Total upload volume:** about 7 GB, spread over a few sessions.

### P4. Concurrent log writers (token)

The sizes below are the original plan. After the first attempt hit the Hub's commit rate limit, the rerun puts the races first and fits about 82 attempts (see Verification).

- **Repository:** `cassandra-chorus/proto-log`. Writers are separate processes on this machine, all using the same token. Each process stands for a pilot member.
- **Append test:**
  - 3 writers, then 5; each appends 20 entries;
  - each entry is a new file whose name and content carry the writer and a sequence number;
  - each commit is made with `parent_commit` set to the head the writer last read;
  - on a rejection the writer re-reads the head and retries, counting the retries.

  Pass condition: every entry the writers were told succeeded is in the final tree exactly once, and no entry appears that a writer was told failed.
- **Stale-parent test:**
  - read head H;
  - let another commit land;
  - commit with `parent_commit = H`.

  The Hub must reject it. This is the report's open question whether `parent_commit` is enforced by the server.
- **Close race:**
  - all writers read the same head;
  - at the same moment, each commits `round-0001/close.json` with different content and that same parent.

  Pass condition: exactly one succeeds, and the file's content is that writer's. Run 20 times.
- **Multi-file visibility:**
  - one commit adds 50 files;
  - a reader process polls the file listing as fast as the rate limit allows;
  - recorded: whether it ever saw only some of the 50.
- **Not tested here:**
  - the report's wrong-clock test (whether bucket timestamps are assigned by the server). Changing the system clock needs administrator rights and would affect everything on the laptop, so the server's timestamps are only recorded next to the local clock;
  - writes by a second account (see P0).

### P5. A week at the planned commit rate (token)

**The planned rate**, from the report's 30-minute round and 5 members:
- **The round log:** per round, one combined entry per member (ready for the next round, update posted, hash of the last merge), one close entry and one checkpoint pointer: 7 commits per round, **336 per day** to one repository. The combined entry is this plan's proposal, to be fixed in the architecture document. The report's own figure was 288 per day, counting the 5 update commits and 1 log commit per round in one repository.
- **Updates:** 5 member repositories with 1 commit per round each, **48 per day** per repository.
- **On one account:** 576 commits per day in all, more than any single pilot member would make. This is a deliberately harder test of any per-account limit.

**Files.** Updates are 1 MB of seeded random bytes, not 0.2 to 0.6 GB. P5 measures the commit count and P3 measures bandwidth. A week of full-size updates (about 50 GB a day from one home) would itself risk "excessive bulk activity".

**Measured, per commit:**
- time, HTTP status and latency;
- any 429 or other refusal;
- commit latency and listing latency against the number of commits in the repository, to look for the "few thousand commits" slowdown (the log reaches about 2,000 commits after six days).

**At the end:** squash the log repository's history (`super_squash_history`) as the recovery the report suggests, and time it.

**Operations:**
- The laptop has AC drop-outs and a weak battery (memory: laptop power), so P5:
  - holds keep-awake (`cassandra_chorus.ops.power.keep_awake`);
  - writes every attempt to a JSON-lines log under the runs folder before acting on its result;
  - resumes from that log after a restart.
- Hours the laptop was off are gaps in the schedule, recorded and reported, not filled in.
- The owner may also write to Hugging Face about "excessive bulk activity" (report section 6). That message is theirs to send.

### P8. Windows installs (no token, but installs from PyPI)

- **Environment:** a new virtual environment in the session scratchpad, made with `python -m venv` from the Store Python 3.13, or from `C:\Users\senso\AppData\Local\Programs\Python\Python312` if the Store build misbehaves. Nothing is installed into either base interpreter.
- **Candidate packages:**
  - `huggingface_hub` with its Xet extra;
  - `safetensors`;
  - `cryptography`;
  - `iroh` (the Python bindings, alpha);
  - `libp2p` (py-libp2p).
- **For each:**
  - whether a Windows wheel exists or a build was attempted;
  - the installed version;
  - whether it imports.

  iroh and libp2p are only imported, not started: started with defaults, they would contact third-party relays and DHTs (class (c)), which D37 rules out.
- **Runs only after the owner approves the exact package list**, because it downloads and installs third-party code.

## Mathematical / Statistical Details

**Merge (as implemented in `cassandra_chorus/coordinator/merge.py`).**
- For a parameter tensor with contributor set C (every returning worker for the shared part; the holders, for an expert and its router row), the averaged value is A = (Σ_{i ∈ C} n_i W_i) / (Σ_{i ∈ C} n_i), where n_i is worker i's example count.
- The accumulation is in float64, in the order the results are given, then cast to the parameter's dtype.
- **Plain averaging:** the new value is A.
- **Nesterov:** with Δ = A − G (the change the average proposes, not the per-worker Δ_i of the delta variant), velocity v' = μ v + Δ and new value G + η (Δ + μ v'). Here μ = 0.9 and η = 0.7 in P6, computed in float64 and cast back. Entries without contributors keep both their value and their velocity.

**Why the order of results can matter.** Floating-point addition is not associative: (a + b) + c and a + (b + c) can differ in the last bit. In float64 such a difference is about 1e-16 relative. It usually disappears when the result is rounded to float32, but not always. P6 measures whether it ever survives.

**Delta variant.**
- A worker ships Δ_i = G − W_i, computed in float32; a peer rebuilds W_i = G − Δ_i.
- Each of the two subtractions rounds once, so the rebuilt W_i may differ from the true W_i in the last bit.
- The direct delta merge computes G − (Σ n_i Δ_i)/(Σ n_i) instead. In exact arithmetic it equals A; in floating point it may not.

**Canonical model hash.**
- SHA-256 over a byte string built tensor by tensor, in ascending order of parameter name (Python string order, which for these ASCII names is byte order).
- For each tensor:
  - the name in UTF-8, a 0x00 byte;
  - the dtype name (for example `float32`), a 0x00 byte;
  - the shape as decimal integers joined by commas, a 0x00 byte;
  - the data length in bytes as an 8-byte little-endian integer;
  - the data itself: C-contiguous, little-endian, on the CPU.
- Two states have equal hashes exactly when they have the same names, dtypes, shapes and bit patterns (barring a SHA-256 collision).

**Difference metrics**, reported when hashes differ, per tensor:
- the count of elements whose bit patterns differ;
- max |x − y|;
- max |x − y| / max(|x|, 1e-30).

**Throughput (P3):** megabits per second = 8 × bytes / 10^6 / seconds. Repeats are reported as a minimum, a median and a maximum, without further statistics, since n = 3.

**P5 rate arithmetic:** 30-minute rounds give 48 rounds per day. The log takes 48 × 7 = 336 commits per day; each member repository takes 48; 5 member repositories plus the log take 5 × 48 + 336 = 576.

## Design Decisions

- **Synthetic worker results in P6.** Merge arithmetic depends only on the tensors' values, dtypes and order. Real training would add hours and no new cases. Engineering default, for review.
- **Signatures over file bytes, not over a re-serialized canonical form (P9).** Canonical JSON has edge cases across languages, floats above all. Signing the exact bytes avoids them. The alternative, SSH signatures (`ssh-keygen -Y sign`, available on Windows), would still need Ed25519 verification code in the client. Engineering default, for review.
- **The real organisation for prototypes.** The owner chose `cassandra-chorus` over a separate test organisation (2026-10-14). The prototypes therefore use private `proto-*` names and a manifest-driven clean-up.
- **Keeping the July token active.** The prototypes take their token by name, so no other tool on the laptop changes behaviour. The owner was told this would be done; it was done on 2026-10-14.
- **One token standing for all writers in P4.** This tests the Hub's concurrency semantics, which do not depend on who writes. Permissions across accounts are a separate question, left for a friend's account.
- **P5's harder per-account load.** All 576 commits a day come from one account. If that passes, a pilot member's share passes too; if it fails, the per-repository numbers show whether the limit is per account or per repository.
- **Order: P6 and P9 first.** They need neither the token nor installs, and their findings (canonical order, outer-state dtype, deltas, signature rule) become protocol rules in the architecture document.
- **P8 and the GitHub arm of P3 wait for the owner's approval**, because they install third-party code and create a repository on the owner's GitHub account.

## Verification

**Setup.** All runs: the reference laptop (RTX 4070 Laptop GPU, 8 GB; Windows 11; the Store Python 3.13 with PyTorch 2.12.1+cu126, `huggingface_hub` 1.24.0, safetensors, `cryptography` 46.0.3); `CHORUS_RUNS_DIR=C:\Users\senso\chorus-runs`. The token prototypes ran against the `cassandra-chorus` organisation on the free plan.

**Unit tests.** `python -m pytest tests/test_prototypes.py tests/test_coordinator.py` passed, 44 tests, of which 13 are in `tests/test_prototypes.py` (run 2026-10-14 after the P4 rerun). The prototype tests cover:
- the canonical hash;
- `bit_diff`;
- the token guard, on `whoami` shapes;
- P6 at toy scale, including GPU true division;
- P9's cases;
- P5's schedule and resume logic.

`tests/test_coordinator.py` still passes, which shows the P6 swap of `_weighted_mean` is undone after use.

### P6. Merge determinism: done

- **Command:** `python scripts/proto/p6_merge_determinism.py --work-dir C:\Users\senso\chorus-runs\proto-p6`.
- **Run:** 1,172.8 s; 46,050,432 parameters; seed 7; one machine; deterministic algorithms off.
- **Results:** `results/prototypes/p6_merge_determinism.md` and `.json`.

| Variant against the baseline | Sliced (4 workers, 2 holders per expert) | Full (5 workers) |
|---|---|---|
| Repeat; 1 CPU thread against 14; results reversed; results shuffled | bitwise equal | bitwise equal |
| In memory against through files | bitwise equal | bitwise equal |
| GPU, current code (twice; also shuffled) | **differs**: 472 elements after plain averaging, 526 after Nesterov round 2; largest 5.96e-08 | bitwise equal |
| GPU with the division by a device tensor (also shuffled) | **bitwise equal** | bitwise equal |
| Nesterov velocity stored as float32 between rounds | **differs**: 204,432 elements in round 2's model | **differs**: 132,276 |
| Deltas rebuilt as W = G − Δ before merging (CPU) | bitwise equal | bitwise equal |
| Deltas merged directly (G − mean Δ) | **differs**: 355,790 elements | **differs**: 499,977 |

**Cause of the GPU difference.** `_weighted_mean` ends with `acc / total`, where `total` is a Python number. On CUDA, PyTorch performs that division as a multiplication by the reciprocal.
- On 10 million random float64 values, the GPU result equalled the CPU's `x * (1/s)` exactly, and differed from the CPU's `x / s` in 6,679,936 values.
- Dividing by a float64 tensor on the GPU matched the CPU exactly.

Why the full kind survived the cast to float32 while the sliced kind did not was not investigated.

**The result order made no difference.** Inference: products of float32 values and integer example counts below 2^13 are exact in float64, and sums of 4 or 5 of them, with nearby exponents, mostly are too. The proposed canonical-order rule is still kept as a protocol rule, because a peer's arithmetic should not depend on that.

**Merge time on the CPU**, measured separately, `merge()` alone with its input files in the OS cache: 0.32 to 1.11 s per merge.

**Not covered:** other machines, GPUs, drivers and PyTorch builds; real training updates instead of seeded noise.

### P9. Signing dry run: done

- **Command:** `python scripts/proto/p9_signing_dry_run.py --work-dir C:\Users\senso\chorus-runs\proto-p9`.
- **Results:** `results/prototypes/p9_signing_dry_run.md`. All 7 cases were as expected:
  - the genuine files were accepted;
  - one flipped byte in the configuration was rejected;
  - a flipped signature was rejected;
  - a truncated signature was rejected;
  - a wrong public key was rejected;
  - a modified archive was rejected;
  - the configuration's signature presented as the manifest's was rejected by the domain prefix.
- The work folder, which held the throwaway key, was deleted.
- **Deviation from the plan:** the verifier ran as `python -E -P`, from an empty folder, not as `python -I`. `-I` also hides the user site-packages, where this machine's `cryptography` is installed. `-E -P` still ignores `PYTHON*` variables and keeps the script's folder and the repository off the import path.

**Not covered:** a second machine; the key's real offline storage; configuration rollback (the serial rule).

### P0. Token scope probe: done

- **Command:** `python scripts/proto/p0_hub_scope_probe.py --org cassandra-chorus`, run 2026-10-14 05:13 UTC.
- **Results:** `results/prototypes/p0_hub_scope_probe.md`. Every step was as expected:
  - with only `repo.contribute.write` on the organisation, the token created a private repository, uploaded, read back, listed, branched, committed and deleted it;
  - it created, used and deleted a private Storage Bucket;
  - creating a repository in the personal namespace was refused (HTTP 403).
- **A commit with a stale `parent_commit` was refused by the server with HTTP 412 Precondition Failed.**
- Bucket listings carry both `mtime` and `uploaded_at`; here `uploaded_at` was 2.1 s later. Whether the server assigns it is still not shown.

**Not covered:** writes by a second account to a repository this one created.

### P4. Concurrent log writers: first attempt stopped by a rate limit

`results/prototypes/p4_attempt1_rate_limit.md` records the first attempt.
- The free plan allows **128 commit-creation requests per hour** (text of the HTTP 429 response). The limit was reached after about 41 to 45 accepted commits, so rejected conditional commits very likely count.
- Every response also carries the general API limit: 1,000 requests per 300 s, fixed window.
- What was rebuilt from the repository: 38 accepted append commits, giving 38 distinct files, all present.
- The first version of the script lost its own results when the 429 stopped it. It now saves after every phase, records every attempt's status and stops a phase cleanly on a 429.
- The rerun's budget was cut to about 82 attempts: 10 races, 2 visibility trials, 3 writers with 4 entries each.

### P4. Concurrent log writers: rerun done

- **Command:** `python scripts/proto/p4_log_writers.py --org cassandra-chorus --run r2`, started 06:19:06 UTC.
- **Results:** `results/prototypes/p4_log_writers.md`. All checks passed.
- **Commit attempts:** 76 in all, no 429: 22 accepted, 48 refused with 409, 6 refused with 412.

**Close races** (5 writers, same parent):
- 10 of 10 trials had exactly one success, and the file held the winner's content.
- Losers were refused with **409 Conflict**, or with 412 once (trial 0, whose send times spread over 947 ms while the processes started).
- In the other trials the send times were within 0.1 to 4.7 ms of each other.

**Multi-file visibility:**
- In both trials, every listing showed either 0 or all 50 files of the commit, never part (6 listings each).
- The full set was listed about 0.2 s before the commit call returned.

**Appends** (3 writers, 4 entries each):
- 10 told success, all present; 2 told failed, neither present; nothing unexpected.
- 24 attempts: 10 accepted, 9 refused with 409, 5 with 412, about 2.4 attempts per accepted entry under contention.
- The script retried only on 412 and gave up on an entry after 3 other errors. Both "failed" entries are such 409 sequences, not lost writes.
- **Finding:** a client must treat 409 like 412, as "lost the race: re-read the head and retry". The script was left as run, so the result stays reproducible.

**Not covered:**
- writers on different accounts and homes;
- whether 409 and 412 refusals count toward the 128-per-hour limit (no 429 at 76 attempts; the first attempt's arithmetic suggests they do).

### P3. Transfers: smoke test only

Bucket, one file each:
- 10 MB (numbers from the console output; the 0.1 GB run overwrote its result file): upload 9.06 s (8.8 Mbit/s); visible to a separate process after 0.55 s; download 7.43 s (10.8 Mbit/s); SHA-256 matched.
- 0.1 GB: upload 95.1 s (8.4 Mbit/s); download 60.4 s (13.2 Mbit/s).

At these rates the full plan, about 5.6 GB each way, would occupy the home connection for about 2.5 hours, so its size waits for the owner.

### Not started

- P5: a week of the laptop online; waits for the owner.
- P8: installs third-party packages; waits for the owner's approval of the list. What PyPI lists (queried 2026-10-14, about 06:10 UTC, metadata only, nothing installed):
  - `iroh` 1.1.0 (2026-07-16): one Windows wheel, `py3-none-win_amd64`;
  - `libp2p` 0.8.0 (2026-09-26): **no wheel, source package only**, so a Windows install builds from source;
  - `huggingface_hub` 2.2.0 (2026-10-08): pure Python, **one major version ahead of the 1.24.0 the prototypes use**;
  - `hf_xet` 1.7.0, `safetensors` 0.8.0, `cryptography` 50.0.2: Windows wheels.
- `scripts/proto/hub_cleanup.py` is written and was dry-run on 2026-10-14. It lists 4 organisation resources and skips the personal-namespace probe, which was never created. Nothing is deleted until the owner has seen the results, and not before P3, which reuses the transfer bucket.
  - **The manifest is found through `CHORUS_RUNS_DIR`.** Without that variable, the script looks in the repository's `runs/` folder, finds no manifest and deletes nothing. The command, in PowerShell:

    ```
    $env:CHORUS_RUNS_DIR = "C:\Users\senso\chorus-runs"
    python scripts/proto/hub_cleanup.py --org cassandra-chorus          # lists only
    python scripts/proto/hub_cleanup.py --org cassandra-chorus --yes    # deletes
    ```

    Use the Store Python's full path for `python` on the reference laptop.
- **Side effect of P4's first attempt:** the burst used up the account's commit budget. For about an hour, from about 05:17 to 06:17 UTC on 2026-10-14, **no commit from the owner's account could be created with any token**. The limit is per account, not per token (inference from the 429 text). The rerun was sized to avoid this.
- `scripts/proto/p5_commit_rate.py` is written; its schedule and resume logic is unit-tested (`test_p5_*`). It is not started.

**Not tested (known in advance):**
- equality across machines and PyTorch builds;
- transfers from other homes;
- a second account's write permissions;
- server-assigned timestamps under a wrong clock;
- home reachability (P1, P2).

## Related Docs

- `docs/research/2026-10-13-system-study-report.md`: sections 4.1, 4.5, 4.7 and 6, and Q5 for the host limits.
- `docs/ROADMAP.md`: steps 1.3 and 3.5, principle 6.
- `docs/SRS.md`: D37 to D41.
- `docs/implementations/2026-10-08-coordinator.md`: the merge formulas.
