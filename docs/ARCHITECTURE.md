# CASSANDRA Chorus: system architecture

| | |
|---|---|
| Roadmap step | 1.3, system architecture document (`docs/ROADMAP.md`) |
| Status | **Draft 0.1, 2026-10-14. Not adopted.** D41 defers the design until the prototypes the owner's machine can run alone have reported |
| Decisions it builds on | D29 to D41 (`docs/SRS.md` section 9) |
| Evidence | `docs/research/2026-10-13-system-study-report.md` (the study); `docs/implementations/2026-10-14-solo-prototypes.md` and `results/prototypes/` (the prototypes) |
| Replaces | Nothing. Step 1.4 turns the adopted parts into SRS requirements |

## 0. How to read this draft

The design described here is the study's **Option A, the bulletin board**:
- all exchange goes through public file hosts;
- every peer computes the merge;
- a signed log, appended with conditional commits, records which updates count in each round.

It is the candidate, not the decision (D41). Four labels mark what kind of statement each one is:

| Label | Meaning |
|---|---|
| **Rule** | a proposed protocol rule; binding once the owner adopts this document |
| **Waits on Pn** | a prototype result can confirm or change it (prototype IDs from the study's section 6) |
| **AD-n** | an owner decision this document needs; all are listed in section 15 |
| **Inference** | reasoned from sources or measurements, not shown by them |

What this document is not: the SRS (step 1.4), an implementation plan (each component gets its own `docs/implementations/` plan before code), or the product specification (`docs/assistant-spec.md`, step 1.2).

## 1. Requirements

| ID | Requirement | Source |
|---|---|---|
| R1 | Nothing runs around the clock on a machine the owner runs or pays for | D37 |
| R2 | May stay central: the code-signing key, bootstrap peers (the owner's and participants' machines), public file hosts, the starting configuration | D37 |
| R3 | Only our own machines relay connections; no third-party relays | D37 |
| R4 | Production training uses deadline-quorum group averaging with one shared model; a synchronous mode reproduces Stage 0's rounds | D37, D38, D39 |
| R5 | At least 2 holders per expert in every round of a decentralized run | D37, principle 7 |
| R6 | Both work-unit kinds: full copies and sliced mixture-of-experts | D34 |
| R7 | Each pilot participant writes only their own repositories plus signed entries in one round log; the owner alone signs releases and the configuration | D40 |
| R8 | The current model is defined by a merge rule that every peer computes identically from public inputs | principle 6 |
| R9 | Work units and updates are data, never code; clients run only signed releases | principle 2 |
| R10 | Gate N1a: the synchronous mode on two real machines lands within seed noise of the Stage 0 simulation | ROADMAP 3.5 |

## 2. Overview

```
  owner, offline                     public file hosts (class b)
  +----------------+   signed      +--------------------------------------------+
  | signing key    |-------------->| config repo:  run-config.json + .sig        |
  | (Ed25519)      |   releases    | releases:     archive, manifest + .sig      |
  +----------------+               |                                             |
                                   | round log:    one branch, signed entries,   |
  peer m0 --- own update ------->  |               appended by conditional commit|
  peer m1 --- log entries ------>  | m0's repo:    m0's updates (only m0 writes) |
  peer m2 <-- updates, log, -----  | m1's repo:    m1's updates (only m1 writes) |
     ...      checkpoints          | checkpoints:  the round's publisher's repo  |
                                   |               + a mirror                    |
                                   +--------------------------------------------+
```

**One round, in outline (deadline mode):**
1. **Ready.** Members who want to train in round t post a signed "ready" entry before round t starts. Those entries form the present set P_t.
2. **Assignment.** Every peer computes the same assignment from the run seed, t and P_t.
3. **Training.** Each assigned peer downloads the start state G_{t−1} (or its slice), trains H steps, uploads its update to its own repository and posts a signed "posted" entry.
4. **Close.** At the deadline, the first peer whose conditional commit of "round t closed" succeeds fixes the counted set S_t.
5. **Merge.** Every peer computes the merge of S_t, or the parts it needs.
6. **Publish.** The round's designated publisher uploads the merged checkpoint G_t and its hashes; other peers check their own results against those hashes.
7. **Late work.** A late peer's update is ignored; it adopts G_t.

Nothing in this outline needs a server, a peer-to-peer connection or a relay. Its costs are the host's limits, round time spent uploading and downloading, and trust in the members who can write the log (sections 9 and 13).

## 3. Peer roles

| Role | Who | Chosen by | Does |
|---|---|---|---|
| Trainer | any member in P_t | the assignment (section 8) | trains its work unit, uploads the update, posts it |
| Merger | every member | (everyone) | computes the merge of S_t for the parts it needs (all parts in full-copy mode; the shared part and its next round's experts in sliced mode) |
| Closer | any member | **Rule:** the first successful conditional commit of the close entry after the deadline | fixes S_t |
| Publisher | one member of S_t | **Rule (proposal, inference):** members of S_t in the order of SHA-256(run seed, t, member ID). The first publishes; if its checkpoint entry is not in the log within the grace time after the close, the next one does | uploads G_t (sharded by part) and posts the checkpoint entry with the hashes |
| Signer | the owner, offline | the configuration | signs client releases and run configurations |

**Why the publisher is designated rather than raced (inference).** A race to commit a small entry, as for the close, costs nothing. A race to upload a 0.2 to 0.6 GB checkpoint would waste several home uploads per round. A deterministic order with a fallback has one uploader per round when all is well.

## 4. Identities, keys and accounts

- **Owner signing key.**
  - Ed25519, generated and kept offline (BOINC's practice, study Q8). Signs the run configuration and release manifests.
  - **Rule:** a signature covers a domain prefix followed by the file's exact bytes, `b"cassandra-chorus/<kind>/v1\n" + bytes`. A verifier checks the bytes before parsing them, and nothing is re-serialized before checking.
  - The prefix stops a signature for one kind of file being presented as a signature for another.
  - **P9 (one machine, 2026-10-14):** a fresh client process holding only the public key accepted the genuine files. It rejected six tampering cases: a flipped byte in the configuration, a flipped or truncated signature, a wrong key, a modified archive, and a configuration signature presented as a manifest's (`results/prototypes/p9_signing_dry_run.md`). Not yet run on a second machine.
  - The public key is pinned in the client release. **Rule (from BOINC, study Q8):** a new key is accepted only when the old key signs it.
  - Where the private key lives, and its backup, is AD-1.
- **Member keys.**
  - Each member generates an Ed25519 key pair on their own machine. The configuration lists the public keys, and each log entry is signed with its member's key.
  - **Rule:** an entry whose signature fails, or whose member is not in the configuration in force for that round, is ignored by every reader.
- **Configuration serial.**
  - **Rule:** the configuration carries a serial number. A client never accepts a configuration whose serial is lower than one it has already accepted, which blocks the replay of an old, validly signed configuration.
  - Not tested.
- **Host accounts.**
  - Each member uses their own Hugging Face account and a fine-grained token. Under R7 the token writes the member's own repositories plus the round log.
  - **P0 (2026-10-14):** a fine-grained token whose only permission is `repo.contribute.write` on the organisation could:
    - create, write, read, branch and delete private repositories in that organisation;
    - create and use a private Storage Bucket there (on the free plan);
    - but not create anything in its owner's personal namespace (HTTP 403).

    So each member's own update repositories fit such a token (`results/prototypes/p0_hub_scope_probe.md`).
  - Whether a token can write the log repository that **another** account created needs a second account (**waits on a friend's account**).
  - Whether the log sits in an organisation of its own is AD-2.

## 5. Shared state: what lives where

| Item | Where (class b hosts) | Written by | Format | Kept |
|---|---|---|---|---|
| Run configuration | config repository, `run-config.json` plus `.sig`; mirrored as a GitHub release asset | owner only | JSON plus signature file | every serial |
| Client releases | GitHub releases of the project repository: archive, manifest, `.sig` | owner only (signs offline; uploads from any machine) | zip, JSON, signature | every release |
| Round log | one branch of one Hub repository (AD-2: in its own organisation) | members, by conditional commit | one JSON file per entry plus its `.sig`, added in one commit | the run; squashed or rotated per section 9 |
| Updates | each member's own repository or Storage Bucket (a free organisation can create buckets, P0; buckets are not git repositories, so their uploads are presumably outside the commit limit, not yet confirmed; **waits on P3**) | that member only | per round: `shared.safetensors`, one `L<l>E<e>.safetensors` per held expert, and `manifest.json` written last | until the round's checkpoint is mirrored; the member deletes older rounds |
| Checkpoints | the publisher's own repository; mirrored to a second host (AD-3) | the round's publisher | the same part files as updates, plus `optimizer/` (outer state, float64) and `manifest.json` written last | every round's pointer; files of every k-th round (AD-4) |

- **Parts.** A model is cut into parts:
  - the **shared part**: every tensor outside the experts, except the router rows;
  - one part per **expert**: its weights plus its router row (study 4.1).

  Update and checkpoint files follow the same cut. A slice holder downloads only the shared part and its own experts, as Petals servers fetch only their blocks through an index (study Q5).
- **Rule:**
  - a reader never uses an update or checkpoint without its manifest;
  - the manifest lists every file's SHA-256 and size, and is uploaded last;
  - a file that does not match its manifest is treated as missing (study Q5: Psyche's and Templar's atomic markers).
- **Rule:**
  - only safetensors and JSON are ever read from the hosts;
  - nothing fetched is unpickled, imported or executed (R9; study Q7, Q8).

## 6. The round protocol

### 6.1 Timeline of round t

Times come from the configuration: round length L, training deadline D (an offset from the round's start) and grace time g. Round t starts at T_t = T_0 + t·L in UTC.

| When | Who | What |
|---|---|---|
| before T_t | each member who will train | "ready for t" (in the combined entry, 6.2) |
| T_t | every peer | P_t := members with a valid ready entry in the log at T_t; compute the assignment |
| T_t to T_t + D | trainers | download the start state, train H steps, upload the update (manifest last), post "posted for t" |
| after T_t + D | any member | conditional commit of "close t" listing S_t |
| after the close | every peer | merge (section 7) |
| close to close + g | the designated publisher | upload G_t, post "checkpoint t" with hashes |
| after "checkpoint t" | every peer | compare its own part hashes with the published ones (7.2) |

How a peer reads "at T_t" is **inference**: from the log's tree at the first commit it sees whose server time is at or after T_t. Whether Hub commit times are assigned by the server is recorded by P4 but not settled (**waits on P4**). Clock skew between members is accepted in the pilot (section 13).

### 6.2 Log entries

**Rule.** Each entry is a JSON file at `rounds/<t, 6 digits>/<member>.<type>.json`, with its signature at the same path plus `.sig`. Both are added in a single commit. Every entry carries `schema` (an integer, 1 for now), `run`, `round`, `type`, `member` and `client_version`.

| Type | Written by | Payload |
|---|---|---|
| `member` (combined) | each member, once per round it takes part in | `ready_for` (t+1); `posted` (repository, revision, manifest SHA-256 and example count of its round-t update, if any); `merge_hashes` (its part hashes for G_{t−1}, if it merged) |
| `close` | the closer | the counted set S_t: for each member, the posted entry's path and manifest SHA-256 |
| `checkpoint` | the publisher | repository, revision, manifest SHA-256, the model hash and every part hash of G_t |
| `abort` | the closer (synchronous mode only) | the reason, for example a timeout waiting for an assigned member |

**Commit rate (inference).** With the combined entry, a round costs one commit per member plus one close and one checkpoint. At 5 members and 30-minute rounds that is 7 per round, 336 per day to the log repository. **P5 runs this rate for a week (waits on P5).**

**Commit budget.** P4's first attempt (2026-10-14) hit the Hub's free-plan limit, in the response text: "rate limit for repository commit creation (128 per hour)". It was reached after about 41 to 45 accepted commits, so rejected conditional commits very likely count (`results/prototypes/p4_attempt1_rate_limit.md`). Every response also reports a general API limit of 1,000 requests per 300 s.
- **Rule:** the protocol budgets commit **attempts**, not commits, per member account and hour. At 30-minute rounds a member makes about 2 to 4 attempts per round, far below 128 per hour. Retries after conflicts are what can exhaust the budget.
- **Rule:** members stagger their appends by a member-specific offset (for example, a hash of the member ID modulo a minute), so that entries posted near the deadline rarely collide.
- **Rule:** a 429 is a back-off signal, never a reason to drop an entry. An entry that cannot be posted before the close is simply late.

### 6.3 Appending

**Rule:**
- a member appends with `create_commit(..., parent_commit=<the head it last read>)`;
- on rejection it re-reads the head and retries;
- an entry is never modified or deleted, and every entry's path is new.

The Hub documents that such a commit "will fail if `revision` does not point to `parent_commit`" (study Q3, `hf_api.py`). P0 showed the **server** refusing a commit with a stale parent: HTTP 412 Precondition Failed, with one writer. Whether that holds when several writers commit at the same instant is **P4's question (waits on P4)**. If it does not, this design needs a different record of the counted set (study Q3, candidates 3 to 5).

### 6.4 Closing and the counted set

**Rule.** In **deadline mode** (D39):
- any member may close round t once T_t + D has passed by its clock;
- the close entry lists every valid posted entry for t in the tree of its parent commit;
- the first successful close is the only close; a later close commit for the same round is ignored;
- S_t is exactly the list in that close entry.

**Rule. The counted set is fixed by the log, not by what a peer managed to download.**
- A peer that cannot fetch a counted update retries.
- After a limit, it skips the merge and adopts the published checkpoint.
- It never merges a subset, because that would fork the model.

This is Psyche's behaviour, where a client lacking an agreed payload stops (study Q6).

**Rule.** Every peer validates each counted update identically before merging. An update that fails is excluded by every peer alike, because validation is a pure function of the files. It fails if:
- its files do not match its manifest;
- its tensor names or shapes do not match the assignment;
- any value is NaN or infinite;
- its example count is not positive.

**Minimum quorum.** If fewer than Q_min updates are posted by the deadline, the round closes with S_t empty, and G_t = G_{t−1} with the outer state unchanged. The value of Q_min is AD-5.

### 6.5 Synchronous mode (D38)

**Rule:**
- the closer may close round t only when every member assigned in round t has posted;
- if that has not happened by a long timeout (AD-6), the closer posts `abort` and the round is rerun with the same assignment;
- assignment, H and the merge are Stage 0's, so Gate N1a compares the two directly.

The timeout is what flwr-serverless's synchronous mode lacks (study 4.1).

### 6.6 Joining, leaving and late work

- **Late:** an update posted after the close is never counted. Its author adopts G_t and is in P_{t+1} only if it posts "ready" in time.
- **Leaving:** a member stops posting "ready". Nothing else is needed.
- **Joining:**
  - the owner signs a configuration with a higher serial listing the new member's key and repository;
  - the newcomer downloads the latest checkpoint and posts "ready".
- **A member that misses many rounds** is no different from a newcomer.

## 7. The merge rule

**Rule.** The merge is Stage 0's merge (`cassandra_chorus/coordinator/merge.py`; SRS S0-F-08 to S0-F-10, with D11 for router rows), computed by every peer, with the additions P6 calls for. These are stated as explicit rules because the code's behaviour alone does not make them part of the protocol.

### 7.1 Computing it

1. **Inputs:**
   - the start state G_{t−1}, as published;
   - the outer optimizer's state, as published;
   - the counted set S_t from the close entry;
   - each counted member's update and example count n_i;
   - the round's assignment.
2. **Order. Rule:** results enter the merge sorted by member ID. In float64, (a + b) + c can differ from a + (b + c) in the last bit, so a peer that summed in download order could compute different bits.
3. **Averaging:**
   - for each parameter, A = (Σ_{i ∈ C} n_i W_i) / (Σ_{i ∈ C} n_i), over the contributors C (every counted member for the shared part; the counted holders for an expert and its router row);
   - accumulated in float64, then cast to the parameter's dtype;
   - an entry with no contributor keeps its value and its outer state.
4. **Division. Rule:** the division in step 3 is IEEE division in float64 on every device.
   - **P6 finding (2026-10-14, PyTorch 2.12.1+cu126):** dividing by a Python number on CUDA multiplies by its reciprocal. On 10 million random float64 values this gave results identical to the CPU's `x * (1/s)`, while 6,679,936 of them differed from the CPU's `x / s`. Dividing by a float64 tensor on the GPU matched the CPU exactly.
   - **At full scale** (the 46,050,432-parameter Stage 0 model):
     - with the current code, the sliced merge on the GPU differed from the CPU in 472 elements after plain averaging and 526 after a second Nesterov round (largest difference 5.96e-08); the full-copy merge happened to be equal;
     - with the division done by a device tensor, both kinds were **bitwise equal** to the CPU, also with the results shuffled (`results/prototypes/p6_merge_determinism.md`).
5. **Outer step:**
   - plain averaging or Nesterov, as the configuration says;
   - **Rule:** the outer state (Nesterov velocity) is stored and published as **float64**.
   - **P6 (full scale):** storing it as float32 between rounds changed round 2's merged model in 204,432 elements (sliced) and 132,276 (full).
6. **Representation:**
   - whether members upload full states W_i or deltas Δ_i = G_{t−1} − W_i is AD-7;
   - **P6 (full scale, CPU):** rebuilding W_i = G_{t−1} − Δ_i before the merge gave the same bits as full states; merging the deltas directly (G − mean Δ) did not (355,790 and 499,977 elements differed);
   - either works if every peer does the same thing. **Rule (proposal):** if deltas are shipped, peers rebuild full states and run the same merge.
7. **Device:**
   - **Rule (proposal):** the merge is computed on the CPU, whatever GPU a peer has. **P6:** `merge()` alone took 0.3 to 1.1 s on this laptop's CPU at full scale. Pinning the device removes the class of differences found on the GPU, which this prototype can only sample.
   - On the CPU, P6 found the merge bitwise stable across repeats, 1 thread against 14, results in member, reversed or shuffled order, and in memory against through files.

### 7.2 Agreement

- **Rule. The canonical hash of a part** is SHA-256 over its tensors, in ascending name order. For each tensor, it covers:
  - the name;
  - the dtype name;
  - the shape;
  - the data length;
  - the C-contiguous little-endian bytes.

  It is defined over tensors, so two correct safetensors writers cannot disagree (P6 implements it in `scripts/proto/common.py`).
- **Rule. The model hash** is SHA-256 over the sorted list of (part ID, part hash). A slice holder can therefore check the parts it computed without computing the rest.
- **Rule.** Each member posts the hashes of the parts it merged, in its next combined entry.
- **On a mismatch with the publisher's hashes:**
  - the member adopts the published checkpoint;
  - it records the mismatch, which then shows on the status page;
  - in the pilot, a mismatch is a bug to investigate, not a vote.
- Whether equal hashes hold **across machines and PyTorch builds** is not something one laptop can test. P6 shows only that they hold on one machine under the variants it ran. Equal hashes there are necessary, not sufficient. If cross-machine equality fails, the fallback is a tolerance check, as Templar's sync score does (study Q3), and AD-8 decides between them.

### 7.3 What the merge does not do

It does not judge update quality: no loss scoring, no outlier rejection. For trusted pilot members, validation (6.4) and the hashes are the checks. Quality checks are a Phase 6 question (section 13).

## 8. Work units and assignment

- **Kinds (R6).**
  - **Full-copy units:** the whole model, DiLoCo-style.
  - **Sliced units:** the shared part plus a set of experts.
  - The configuration says which kind each round uses, or a mix per member (AD-9).
- **Present set.** P_t comes from the ready entries (6.1). **Rule:** the assignment is a pure function of the run seed, t and P_t (the member IDs, sorted). It uses the existing `assign_slices` with the `rolling` policy, which gives exactly 2 holders per expert in Stage 0's setting (D37).
- **Holder-count rule (R5; study 4.1):**
  1. assign from P_t with `rolling` so that every expert has 2 holders;
  2. place an expert's holders in different homes where possible; the configuration records each member's home (AD-10);
  3. if an expert's counted holders fall to 1, the survivor's update is merged alone (a quorum of 1), or that expert's update is skipped. No source measures which is better, so Gate N1b pre-registers one (section 14);
  4. if they fall to 0, the expert keeps G_{t−1}: one round of its training is lost, not the expert;
  5. if P_t is too small to give every expert 2 holders, the round runs full-copy units only, or is skipped (AD-9).
- **Training data.** Which data shards a work unit trains on must also be a pure function of the run seed, t and the member, so that a rerun gives the same result. Stage 0 seeds each worker's data stream from the run seed, worker and round (`sim/data/w<i>/r<t>` in `cassandra_chorus/sim/harness.py`). Mapping that onto the pilot corpus (Phase 2) is open; **inference:** shard IDs and offsets go in the configuration, never data in the log.
- **Weights.** n_i is the number of examples the member trained on, as posted. In the trusted pilot it is taken as stated. It could be checked against the assignment's step count and batch size, since H and the batch size are fixed.

## 9. Storage, checkpoints and host limits

**Known limits** (study Q5, read 2026-10-13):
- Hub repositories: "a few thousand commits" degrade a repository, which "is not meant to work as a database"; `CommitScheduler` advises at least 5 minutes between commits.
- **Commit creation: 128 requests per hour on the free plan, rejected conditional commits very likely included.** This comes from the HTTP 429 text seen by P4 on 2026-10-14; the study had found the commit limits undocumented.
- **API requests: 1,000 per 300 s**, fixed window, per account (response headers, 2026-10-14).
- Free downloads: 5,000 per 5 minutes per user.
- "Excessive bulk activity" counts as abuse.
- Storage Buckets: mutable, non-versioned, intended for checkpoints and logs; free allowance not quantified.
- GitHub release assets: under 2 GiB each on free accounts; 500 content-creating API requests per hour.

**Measured from this home** (**waits on P3, P5**):

| Quantity | Value | Prototype |
|---|---|---|
| Smoke test, Storage Bucket, one 0.1 GB file | upload 95.1 s (8.4 Mbit/s); download 60.4 s (13.2 Mbit/s) | P3 smoke |
| Smoke test, Storage Bucket, one 10 MB file | upload 9.06 s; visible to another process after 0.55 s; download 7.43 s | P3 smoke |
| Upload and download times, 0.2 GB and 0.6 GB, Hub repository and bucket, 3 repeats | pending (size of the run waits for the owner) | P3 |
| A free organisation may create Storage Buckets | yes | P0 |
| Xet savings on a successive, slightly changed update | pending | P3 |
| Commit latency and refusals at 336 log commits and 5 × 48 update commits per day, over a week | pending | P5 |
| Time to squash the log's history | pending | P5 |

**Rules (proposals, inference until P5 reports):**
- **Log rotation.** The log repository is squashed or replaced when it nears the commit count at which P5 sees a slowdown. A rotation is an owner-signed configuration naming the new log and the last round of the old one.
- **Retention.** Members delete their own updates once the round's checkpoint is mirrored. Checkpoints keep every k-th round in full (AD-4) and every round's hashes in the log.
- **Mirror.** Every checkpoint is copied to a second host (AD-3), so a single host's outage stops rounds but loses nothing (study 4.1).

**Traffic per peer and round (inference, study 4.1).** In full-copy mode, a peer that merges everything downloads N − 1 updates: at N = 5 and 0.6 GB, 2.4 GB per round. The alternative is to download only the published checkpoint and spot-check it. That trades bandwidth for trust in the publisher and is AD-11.

**What this home's link implies (inference from the P3 smoke test, one home, one morning):**
- At 8.4 Mbit/s up, one 0.6 GB update takes about 9.5 minutes to upload.
- At 13.2 Mbit/s down, the 2.4 GB that a full-copy peer needs to merge everything takes about 25 minutes.
- Together, with training, that does not fit a 30-minute round. Full-copy rounds of that size need longer rounds, publisher-only merging (AD-11), smaller updates (slices; compression, which the study's Q10 covers), or all three.
- The pilot model's size, which decides update size, is still open (product specification, step 1.2).

## 10. Discovery and connections

Option A needs no peer-to-peer connections, no discovery and no relays: peers find each other's data through the repositories listed in the signed configuration. R3 is met trivially.

**Rule.** All transfers go through one transport interface:
- put a file;
- get a file;
- list a prefix;
- append a log entry with a parent.

The host-backed transport is the first implementation. If the home survey (P1, P2; not scheduled, D41) finds reachable machines, a direct transport for update bytes can be added as the study's Option C, while the log stays on the host. Library defaults that use third-party relays or DHTs (iroh's n0 relays, IPFS bootstrap) must be replaced before any such use (study 4.2).

## 11. Failures and churn

| Event | What happens |
|---|---|
| A trainer leaves mid-round | its update never arrives; it is outside S_t; with 2 holders per expert, its experts are trained by the other holder (6.4, 8) |
| Every peer goes offline | the log and checkpoints stay on the hosts; training resumes from the last checkpoint when peers return |
| The owner's laptop is off | nothing waits for it, except signing a new configuration or release |
| The closer dies after its close commit | the close stands; anyone can merge |
| The closer dies before committing | another member's close commit succeeds |
| The publisher dies or is slow | the next publisher in order publishes after the grace time (section 3) |
| A peer cannot download a counted update | it retries, then adopts the published checkpoint; it never merges a subset (6.4) |
| A peer's merge hash differs from the publisher's | it adopts the published checkpoint and records the mismatch (7.2) |
| An update contains NaN or Inf, or mismatched names or shapes | every peer excludes it identically (6.4) |
| The host is down | rounds stall; checkpoints survive on the mirror |
| The host refuses commits (rate limit) | appends back off and retry; if the deadline passes, the round closes with what was posted; P5 measures how often |
| A member's clock is wrong | it may close early or late; accepted in the pilot (13) |
| A member corrupts or squashes the log | forged entries fail signature checks; deleted history is recovered from checkpoints, member repositories and the mirror (13) |

## 12. Code trust, releases and versioning

- **Releases.**
  - The owner tags a release, builds the archive, writes a manifest with its SHA-256 and signs the manifest offline.
  - **Rule:** a client installs or runs a new version only after verifying the manifest's signature with the pinned public key and the archive's hash against the manifest (P9).
  - No reproducible-build claim is made (study Q8).
- **Work units are data (R9).** A work unit is a configuration entry plus an assignment computed locally. An update is safetensors plus JSON. The client never fetches code except as a signed release.
- **Versions:**
  - the client follows semantic versioning;
  - every log entry carries `schema` and `client_version`;
  - every checkpoint manifest carries a format version;
  - the configuration carries its serial and the client versions allowed from round t onwards.
- **Rule:** upgrades happen at round boundaries named in a configuration. A client older than the configuration allows posts nothing and asks its user to upgrade.

## 13. Trust model

**Pilot (D40): 3 to 5 trusted people.**

| A member can | Because | Detected by | Recovery |
|---|---|---|---|
| post a poisoned but well-formed update | merges do not judge quality (7.3) | loss curves; hashes do not catch it | exclude the member by a new configuration; roll back to an earlier checkpoint |
| delete, rewrite or squash the round log | the log needs write access for several members; on the Hub, the `write` role can "create, delete, or rename any repo" in its organisation (study Q7) | entries missing against members' own records and the mirror | rebuild from checkpoints, member repositories and the mirror; AD-2 limits the reach |
| close a round early (clock skew or on purpose) | the deadline is checked by the closer's clock | close commit time against the configured deadline | accepted; the round still merges valid updates |
| leak their token | tokens live on members' machines | host audit logs, if any | revoke; a new configuration |

Accepted by the owner (D40): during the trusted pilot, any member could damage the log.

**Later (D40):** pilot participants become **maintainers**, and only that group writes shared state, so the network never depends on one person. The design above already has no single-person role except signing (AD-1 decides whether signing is shared).

**Phase 6, the open pool: not designed here.** Strangers would need update-quality checks, rate limits, protection against Sybil identities, and probably a different record of the counted set. The study flags a ledger (class (c), against R2) as the main candidate to evaluate then.

## 14. Gate N1b, draft pre-registration

The roadmap places the Gate N1b definition in step 1.3. This is a draft for the owner, from the study's section 5. It is fixed, with the allowance, before its first run, and it follows prototype P7 (simulation in the Stage 0 harness), which needs GPU time after Phase 1.

- **Method under test:** deadline-quorum group averaging (D39), with the outer optimizer fixed here (AD-12), in Option A's deadline mode.
- **Comparisons**, at equal compute, on Stage 0's seeds 7, 11 and 19:
  - against the synchronous mode;
  - against centralized training.
- **Equal compute:** the definition states whether dropped late work counts as compute spent (steps run) or not (steps merged). Both are reported; one is primary (AD-12).
- **Readings:**
  - equal tokens and equal wall-clock are both reported, one pre-registered as primary;
  - HeLoCo's comparison flips sign between them (study section 5).
- **Churn:** a recorded, replayable schedule of departures, including mid-round, applied identically to every arm.
- **Recorded per round:**
  - lateness per member;
  - realized holders per expert;
  - the quality of experts whose holders fell to 1 or 0, under the rule chosen for step 3 of the holder-count rule (section 8).
- **Scale:** the pilot's model and 3 to 5 members. Task B (text8) is the first test, as Gate N1a also uses.
- **Allowance:** the largest acceptable gap against each comparison (AD-12). Without it, the gate is a measurement, not a gate.
- **Downstream check:** after SFT (Phase 5), given the conflicting post-training reports (study Q4).

## 15. Owner decisions this draft needs

| ID | Decision | Needed by |
|---|---|---|
| AD-1 | Where the signing key lives and how it is backed up; whether maintainers later co-sign | first signed release |
| AD-2 | Whether the round log lives in an organisation of its own (limits the reach of the `write` role) | before Phase 3 networking |
| AD-3 | The checkpoint mirror's host (GitHub releases, a second Hub organisation, or another) | Phase 3 |
| AD-4 | Checkpoint retention: every k-th round kept in full | Phase 3 |
| AD-5 | Q_min, the minimum number of updates for a round to merge | Gate N1b pre-registration |
| AD-6 | The synchronous mode's abort timeout | Gate N1a |
| AD-7 | Full states or deltas as the update format (P6 informs) | after P6 |
| AD-8 | Bitwise hashes or a tolerance check for agreement (P6 here; cross-machine runs later) | after P6 and a second machine |
| AD-9 | Which work-unit kind each round uses; what happens when P_t is too small for 2 holders per expert | Phase 3 |
| AD-10 | Whether members' homes go in the configuration (for holder placement) | Phase 4 |
| AD-11 | Whether every peer downloads all updates and merges, or downloads the checkpoint and spot-checks | after P3 |
| AD-12 | Gate N1b: the outer optimizer, the primary reading, the compute accounting, the allowance | before Gate N1b's first run |

## 16. What waits on which prototype

| Prototype | Sections it can change | State on 2026-10-14 |
|---|---|---|
| P0 token scope probe | 4, 5 | done: organisation repositories and buckets yes, personal namespace no; stale parent refused with 412 |
| P3 transfers from this home | 5, 9, AD-11 | smoke test done (8.4 Mbit/s up, 13.2 down); full run's size waits for the owner |
| P4 concurrent log writers | 6.1, 6.2, 6.3, 6.4 | first attempt stopped by the 128-per-hour commit limit; rerun pending |
| P5 a week at the planned rate | 6.2, 9 | not yet run |
| P6 merge determinism | 7, AD-7, AD-8 | done on one machine at full scale |
| P8 Windows installs | 10, 12 | awaiting the owner's approval of the package list |
| P9 signing | 4, 12 | done on one machine: all 7 cases as expected |
| P1, P2 home survey | 10 (Option C) | not scheduled (D41) |
| P7 deadline-quorum simulation | 14 | after Phase 1 (GPU time) |

## 17. Related documents

- `docs/research/2026-10-13-system-study-report.md`: sections 4.1 (Option A), 4.5 (write access), 4.7 (recommendation), 5 (Gate N1b), 6 (prototypes).
- `docs/implementations/2026-10-14-solo-prototypes.md` and `results/prototypes/`.
- `docs/ROADMAP.md`: principles 1, 2, 6, 7; steps 1.3, 3.5, 3.6.
- `docs/SRS.md`: D11, D34 to D41.
- `docs/implementations/2026-10-08-coordinator.md`: the merge and assignment algorithms.
