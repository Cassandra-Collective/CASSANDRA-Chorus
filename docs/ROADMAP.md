# CASSANDRA Chorus · Roadmap for the real project

| | |
|---|---|
| Status | Draft for the owner's review |
| Date | 2026-10-13 |
| Decisions | SRS section 9, D29 to D38 (owner, 2026-10-13) |
| Replaces | Nothing yet. `docs/PLAN.md` remains the record of Stage 0. The SRS and PLAN are rewritten around this roadmap in step 1.4 |

## 1. Where we are

- **Stage 0 closed as a negative result** (D28). In simulation, sliced training of a mixture-of-experts model ended +10.8% in test bits per character behind centralized training on text8. The gap splits into three steps:
  - local averaging, +6.1%;
  - partial updates, +1.4%;
  - masked routing, +3.2%.

  Sources: `docs/stage0-report.md`, `docs/stage0-closeout.md`.
- **The literature investigation** (`docs/research/2026-10-11-stage0-literature-report.md`) found every published averaging gap near our setting smaller than ours. It names the likely handicaps:
  - our harder baseline;
  - plain averaging with no outer optimizer;
  - a small model;
  - H = 125;
  - AdamW reset every round.

  FoMoE is the closest method found to slicing. No paper isolates the masked-routing cost.
- **The existing logs show when the gap opens** (`results/task_b_gap_curves.md`, 2026-10-13). On validation, the averaging gap narrows while the learning rate is constant, then widens during the final decay on every seed. The masked-routing step grows as training goes on.
- **The code base is ready to reuse.**
  - The coordinator (slice assignment, merging, outer optimizer) was kept free of simulation code for Stage 1.
  - The training loop now supports gradient accumulation and per-step losses.
  - The simulation harness supports a shorter H during the decay.

## 2. What the project is now (D29 to D32)

- **Product:** a small **local assistant** for calendar, email and reminders, in **English and Turkish**.
- **From scratch:** Chorus pretrains the base model with volunteer compute, then runs SFT and reinforcement learning. Using someone else's base model would defeat the purpose.
- **Data:** no other models' outputs.
  - Pretraining uses open-licensed, human-written text.
  - SFT and RL data come from our own code: an **assistant sandbox** of simulated calendars, inboxes, reminders and tools, with an automatic checker. The sandbox is also the benchmark and the source of RL rewards.
- **Two models:** the assistant is Chorus's own model. Later, Chorus runs ablation pools and skill experts for the separate CASSANDRA flagship.
- **Open source and open to anyone:** "the people's AI, from scratch".
- **No server of ours** (D37, D38):
  - Nothing runs around the clock on a machine the owner runs or pays for.
  - Code, data shards and checkpoints live on public file hosts.
  - Newcomers find the network through the owner's and the pilot participants' machines, which are also the only relays.
  - Production training averages asynchronously or in groups. A synchronous mode is kept for comparisons with Stage 0.

## 3. Principles

1. **Infrastructure is separate from the training method.** The network hands out work units and merges results. Full-copy and sliced-MoE work units both run on it from the first version (D34). Methods change without changing the network.
2. **Work units are data, never code.** A volunteer's client runs only signed, released code. The coordinator sends model versions, data shard IDs and settings, never programs.
3. **Gates are written down before the runs they judge**, as in Stage 0. Every result states its hardware, scale, seeds and what was not tested.
4. **Honest framing:** no novelty claims; every number traceable to its source; the literature report's rules apply to any later survey.
5. **Plan first:** every step gets a `docs/implementations/` document before code, and the owner's decision on anything the documents do not settle.
6. **No server of ours, and no single canonical copy held by one machine** (D37). Coordination is either a role any peer can take or a shared-state protocol on public hosts. The current model is defined by a merge rule that every peer computes identically.
7. **Every expert has at least 2 holders in every round of a decentralized run** (D37). A lone holder that disconnects would lose its expert's training for that round. `rolling` assignment gives exactly 2; `coverage` gives a single holder about 30% of the time.

## 4. Phases

Time estimates are rough and assume one developer working with Claude; they will be revised after Phase 1.

### Phase 0 · Loose ends (days)

| Step | Deliverable |
|---|---|
| 0.1 | Batch 1 code committed (done: `42df982`). Its five runs move to the network as the first research pool (D33) |
| 0.2 | PR #17 (literature report) merged (done: `22baf92`) |

### Phase 1 · Decide and specify (about 1 to 2 weeks, no GPU)

| Step | Deliverable | Notes |
|---|---|---|
| 1.1 | **System study: how volunteer training is coordinated with no server anyone runs, and what stays central in each design.** It evaluates two design families against D37 and D38: peer-to-peer discovery with group averaging, and public-host shared state with a merge any peer can compute and check | A brief first (`docs/research/2026-10-13-system-study-brief.md`), reviewed before launch; then an audited report like the literature investigation. Ends in a design recommendation for the owner (D35), including who may write shared state |
| 1.2 | **Product spec:** the assistant's tasks, the sandbox and checker, the data policy, the tokenizer plan, model-size targets for local inference, safety rules (confirmation before actions; prompt injection inside emails) | |
| 1.3 | **System architecture document** | Peer roles, the shared-state or peer protocol, discovery and bootstrap, connection relaying through our own machines, storage on public hosts, the merge rule, the holder-count rule, failure and churn handling, synchronous and asynchronous modes, versioning, the trust model for trusted participants |
| 1.4 | **SRS and PLAN rewritten** around this roadmap | The Stage 1 to 3 outlines become requirements with acceptance criteria |

### Phase 2 · Data foundation (about 2 to 3 weeks, mostly CPU)

| Step | Deliverable |
|---|---|
| 2.1 | English and Turkish pretraining corpus: open-licensed, human-written, with every licence recorded; deduplicated and filtered. A stated policy on web text written after the arrival of AI writing tools |
| 2.2 | Byte-level BPE tokenizer trained on both languages; vocabulary size chosen by measuring tokens per word in each |
| 2.3 | Fixed, hashed, versioned data shards that volunteers download; held-out evaluation sets in both languages |

### Phase 3 · Network v0 on machines we control (about 3 to 4 weeks)

| Step | Deliverable |
|---|---|
| 3.1 | **Protocol specification.** A work unit carries a model version, data shard IDs, local steps, a seed, settings, and (for slices) the experts to hold. A result carries the update, statistics and a checksum |
| 3.2 | **Coordination without a server** (D37): a peer role or a deterministic shared-state protocol, as the study recommends. It covers membership, work assignment (already deterministic from seed and round in `cassandra_chorus/coordinator`), merging with the outer optimizer, checkpoints on public hosts, run logs and a status page any peer can render |
| 3.3 | **Peer client** (`cassandra-chorus` command): GPU detection and capacity report, download, local training with the existing loop, compressed upload, resume after interruption, **auto mode** (next work unit after each merge), usage limits; acts as a bootstrap peer and a relay when it can accept connections; runs synchronous or asynchronous mode |
| 3.4 | Storage and transport for model versions and updates: public file hosts and direct peer transfer, without third-party relays |
| 3.5 | **Gate N1a (plumbing correctness), synchronous mode.** Full-model averaging on Task B across two real machines lands within seed noise of the simulated result for the same configuration, and a sliced run (with at least 2 holders per expert) does the same. Stage 0 is the reference |
| 3.6 | **Gate N1b (asynchronous algorithm).** A gate for the asynchronous algorithm the study recommends, written down before its first run: its quality against the synchronous mode and against centralized training at equal compute, at the pilot's scale |

### Phase 4 · Friends pilot over the internet (3 to 5 trusted people, D36)

| Step | Deliverable |
|---|---|
| 4.1 | Installer and instructions (Windows and Linux, NVIDIA first); a contributor dashboard |
| 4.2 | **First research pool:** batch 1 (runs B1-1 to B1-5), then the H sweep and keep-against-reset AdamW, run in parallel across machines |
| 4.3 | **Pilot pretraining** of an English and Turkish model of about 100M to 300M parameters, plus a smaller centralized reference (SRS S2-03) |
| 4.4 | **Gate N2.** The distributed model is within an allowance, fixed before the run, of the centralized reference at equal compute, and the system survives worker dropouts |

### Phase 5 · Assistant post-training (alongside Phase 4, mostly one GPU)

| Step | Deliverable |
|---|---|
| 5.1 | The assistant sandbox in both languages, with its checker and a held-out benchmark |
| 5.2 | SFT data generated by our own code; SFT; evaluation |
| 5.3 | Reinforcement learning with checkable rewards from the sandbox; human feedback considered later, as a second way for people to contribute |
| 5.4 | Local inference: quantization and a small demo that asks for confirmation before any action |

### Phase 6 · The open pool (SRS Stage 3)

| Step | Deliverable |
|---|---|
| 6.1 | Threat model; checks on submitted work (sampled re-execution, scoring updates on held-out data); merge rules that resist poisoned updates |
| 6.2 | Accounts, a contribution ledger, a leaderboard, the GUI app |
| 6.3 | Weekly ablation pools and skill experts for the CASSANDRA flagship |
| 6.4 | Permissionless participation: anyone may join without being invited, once 6.1 is in place |

### Research track (continuous, on the network once it exists)

The averaging cost, remedies for sliced MoE, model size, and anything the gaps section of the literature report lists. Each becomes a research pool with its own plan and pre-registered reading.

## 5. Order and dependencies

- Phase 1 comes before any building. Steps 1.1 to 1.3 can be written in parallel; 1.4 follows them.
- Phase 2 and Phase 3 can run in parallel: Gate N1a uses text8, so it does not need the new corpus.
- Phase 4.3 needs Phases 2 and 3. Phase 4.2 needs only Phase 3.
- Phase 5 needs the tokenizer (2.2) and a pretrained base (4.3). The sandbox (5.1) can be built earlier.

## 6. Decisions still to make, and when

| Decision | When |
|---|---|
| Build on an existing framework or our own | End of 1.1 (D35) |
| Model sizes for the pilot and the assistant | 1.2 |
| Tokenizer vocabulary size | 2.2 |
| The allowance for Gate N2 | Before 4.3 starts |
| Who may write to shared state | End of 1.1 (D37) |
| The asynchronous algorithm and its Gate N1b | End of 1.1, gate written in 1.3 |
| Limits of the public hosts used (size, rate, terms) | 1.3 |
| Which sources count as "human-written" | 2.1 |

## 7. Risks

| Risk | Mitigation |
|---|---|
| Distributed pretraining loses quality, as in Stage 0 | Full-copy work units with the best-supported method from the literature; Gate N2 with a pre-registered allowance; the research track runs the fixes |
| Too little compute from 3 to 5 people for a useful assistant | The pilot is sized to the pool; the sandbox measures the smallest model that does the tasks; more participants come with Phase 6 |
| Security of software that strangers run | Work units are data, not code; only signed releases run; trusted participants only until Phase 6 |
| Not enough open-licensed Turkish text | Measured in 2.1 before committing to the model size |
| The reference laptop's power faults | Long runs move to the network. The laptop is also a bootstrap peer and relay, so other participants' machines must be able to take that role when it is off |
| Home networks block incoming connections, and only our machines may relay (D37) | The study measures what direct connection and relaying through our machines can achieve; exchange through public file hosts is the fallback |
| No canonical model, because no machine holds it | A merge rule every peer computes identically from public inputs; checkpoints replicated on public hosts |
| A lone holder of an expert disconnects | At least 2 holders per expert in every round (principle 7) |
| Public hosts change their limits or terms | More than one host; the shared state is plain files that can move |

## 8. Next actions

1. Owner reviews this roadmap.
2. Merge PR #17.
3. Write the brief for step 1.1 (the system study, rescoped by D37 and D38), have it reviewed, then launch it; start step 1.2 (the product spec).
