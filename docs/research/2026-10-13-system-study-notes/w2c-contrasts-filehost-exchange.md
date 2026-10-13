# W2c: contrast cases (BOINC, Flower) and exchange through public file hosts only · system-study notes

Researcher notes for wave 2, strand W2c, of `docs/research/2026-10-13-system-study-brief.md`. Started 2026-10-13 17:54 TST; interrupted by a network error about 18:36 and resumed 22:00; completed 2026-10-13 22:10 TST. Sources: part 1 B1, B2, F1 to F3; part 2 T1 to T9 (training over storage, Hub timestamps) and N1 to N5 (hole-punch coordination).

Part 1: what a central server does in BOINC and Flower, and which of its functions could be replaced by a deterministic rule, a public file host or a peer role.
Part 2: designs in which peers never connect directly and all exchange goes through uploads to and downloads from storage; and whether a file host can coordinate a hole punch.

Classification (brief): **(a)** a server we would run; **(b)** a public host for static files; **(c)** a public third-party network for live coordination or discovery.

Builds on wave 1: `w1a` (connections), `w1c` (Templar membership and write access), `w1d` (host limits, BOINC code signing T1). Not repeated here.

## Sources

### Part 1: contrast cases

#### B1. BOINC wiki: server roles, jobs as data, replication (contrast case, not a candidate)

- **Maintainer:** BOINC project (UC Berkeley and community). Documentation (wiki repository).
- **Link:** https://github.com/BOINC/boinc.wiki (Markdown pages).
- **Version:** shallow clone at `7e16379966f15b9be85fc6206f875e02c70d6bc0` (commit date 2026-10-10T15:17:28-07:00), cloned 2026-10-13 17:57 TST into `sources/w2c/bw`. The shallow clone has no per-page history, so page dates are unknown; same commit as w1d T1.
- **Read status:** files read in full: `ServerIntro.md` (sections "Hardware" to "Installing", rest skimmed), `ServerComponents.md`, `BackendLogic.md`, `BackendState.md`, `Daemons.md`, `JobIntro.md`, `JobIn.md`, `Validators.md`, `JobReplication.md`, `Adaptive-Replication.md`, `Homogeneous-Redundancy.md`, `Assimilation-introduction.md`, `Work-generators.md`, `WorkDistribution.md`, `Input-file-handling.md`, `FileUpload.md`, `BoincFiles.md` (lines 1 to 80). `Job-templates.md`: input-template section only. `MultiHost.md`: first 40 lines. Code signing is w1d T1 and is not repeated.
- **What it shows for part 1:**
  - **The server is several daemons around one database.** A project is "A MySQL database", a project directory and a configuration file listing daemons and periodic tasks (`ServerComponents.md`). The daemons: work generator, feeder, scheduler (CGI), transitioner, validator, assimilator, file_deleter, db_purge (`Daemons.md`; `BackendLogic.md`).
  - **Scheduler.** Answers client requests: a host asks for enough work to keep its processors busy for X seconds (`<work_req_seconds>`), and the scheduler enumerates unsent results, filters them (platform, disk and memory, deadline feasibility, one result per user per workunit, daily quota per host, homogeneous redundancy), and sends them (`WorkDistribution.md`). When it sends a result it sets `report_deadline = now + wu.delay_bound` (`BackendLogic.md`, "Scheduler").
  - **Transitioner.** A state machine over each workunit: marks results past their deadline as `NO_REPLY`, triggers validation once the number of successful results reaches `min_quorum`, creates new results when some are lost or failed ("generate L new results", L = N − K), sets error flags (too many error, success or total results), and triggers assimilation and file deletion (`BackendLogic.md`, "Transitioner"; `BackendState.md`). Default `--sleep_interval` 5 s (`Daemons.md`).
  - **Validator.** Two parts: a "Syntax check" that output files exist and are well formed, and a "Replication check": "If a strict majority are found to be 'equivalent'", those are valid (`Validators.md`). It picks a canonical result and grants credit; equivalence may be fuzzy ("agree within some tolerance") through application-specific validators (`Validators.md`).
  - **Redundancy parameters (per workunit):** `min_quorum` ("Set this to two or more if you want redundant computing"), `target_nresults`, `max_error_results`, `max_total_results`, `max_success_results`, `delay_bound` ("Set this to several times the average execution time") (`JobIn.md`). Worked timelines show a lost result replaced and a quorum of 2 out of 3 reached before the third returns (`JobReplication.md`).
  - **Cost of replication:** "at least 50% of total CPU time is spent checking result validity" under default replication; **adaptive replication** trusts a host with probability 1 − 1/CV(H, V) once its consecutive-valid count CV(H, V) ≥ 10, aiming at "perhaps only 5% or 10%" overhead (`Adaptive-Replication.md`).
  - **Homogeneous redundancy:** sends replicas of one job only to hosts in the same "numerical equivalence class" so results can be compared with strict equality (`Homogeneous-Redundancy.md`).
  - **Assimilator.** Project-specific handler run once per completed workunit ("performed exactly once per work unit", `JobReplication.md`); might copy outputs to an archive or parse them into a database (`Assimilation-introduction.md`).
  - **Work generator.** A program on the server that stages input files and calls `create_work()` with a workunit record and templates; the flow-controlled variant keeps "a constant number of unsent jobs" by querying the database (`Work-generators.md`). Job submitters must have login access to the server, or use web or remote submission (`JobIntro.md`).
  - **File distribution.** Clients download with HTTP GET (Range for resumption) and upload with POST to a CGI `file_upload_handler`; the upload request carries the `<file_info>` exactly as the scheduler sent it, including "a signature based on the project's file upload authentication key pair" (`FileUpload.md`). Files are immutable by name: "If a file is changed, even by a single byte, it becomes a new file" (`BoincFiles.md`). File deleter removes inputs when all results are over and the workunit is assimilated (`Daemons.md`).
  - **Work units as data.** An input template is an XML document listing input files (`<file_info>` with optional `<url>`, `<md5_cksum>`, `<nbytes>`, `<sticky/>`) and a `<workunit>` block with `<command_line>`, resource bounds and redundancy parameters (`Job-templates.md`). "Remote files" can be "served from outside servers, i.e. not BOINC project servers", given by URL, size and MD5 (`Job-templates.md`). A workunit names an application, not a version (`JobIn.md`).
  - **Server requirements as stated by BOINC:** "Your server must have a static IP address"; make it "highly reliable (UPS power supply, RAID ...)" (`ServerIntro.md`, "Hardware").
- **Numbers with locators:** replication overhead "at least 50%"; adaptive target "5% or 10%"; trust threshold CV ≥ 10 (`Adaptive-Replication.md`). HR type 1 ≈ 80 classes, type 2 ≈ 15 classes, noted as "out of date" (`Homogeneous-Redundancy.md`). Transitioner backlog "> 1 hour" is the documented trigger for a catch-up procedure (`Daemons.md`). Setting: public volunteer computing, untrusted hosts, independent jobs.
- **Central elements, classified:** the project server (scheduler, database, daemons, upload handler): **(a)** if we ran it. Download hosts for input and app files can be any web server, so **(b)** is possible for downloads ("remote files"). Upload targets are a CGI program that checks a signed `<file_info>`: **(a)**. The BOINC-run list of projects and client versions is a server of the BOINC project (B2 §2.2).
- **Fit with R1 to R7:** not a candidate; stated only for what replacing the server costs (see Findings, part 1).
- **Question it raises for us:** BOINC's transitioner and validator need one place that records "result sent at T, deadline T + delay_bound, reported or not". Without a database, what record of "who took which work unit, and when" can every peer read and trust?

#### B2. Anderson, "BOINC: A Platform for Volunteer Computing"

- **Author:** David P. Anderson (UC Berkeley). **Link:** https://arxiv.org/abs/1903.01699. Journal version: J. Grid Computing (not checked).
- **Version:** arXiv v1, submitted 5 Mar 2019 (only version, per the abs page fetched 2026-10-13 18:10 TST). PDF fetched 18:11 TST, `pdftotext -layout`.
- **Read status:** sections read: §1.2, §2 (structure), §2.1 (first paragraph), §2.2 "Client/server interaction", §3.3 to §3.5, §3.9, §3.10, §4 "The life of a job", §5.1 "Server architecture", §10.8 "Use of cloud storage". Not read: §3.1, §3.2, §3.6 to §3.8, §5.2 onward except §10.8.
- **What it shows for part 1:**
  - "All communication uses client-initiated HTTP"; clients therefore work "behind firewalls that allow outgoing HTTP", and "The server must be publicly accessible via HTTP" (§2.2).
  - **Intermittent server tolerated:** "All client/server interactions handle failure using exponential back-off ... when a server resumes after a period of being off-line" (§2.2).
  - "Files need not be located on project servers"; downloads are checked "using hashes, and (for application files) code signing" (§2.2). "File uploads need not go to the project server"; Climateprediction.net sends results "directly to the collaborators' servers" (§2.2). Upload filenames "include a random string to prevent spoofing"; optional "encryption-based tokens to limit the size of uploaded files" (§2.2).
  - **Life of a job (§4):** a dispatched instance has four possible outcomes (correct, crash, incorrect, never returned). Deadline = dispatch time + `delay_bound(J)`; past it, "a new instance of J is created". Canonical output files are kept until all instances are resolved, so late results can still be checked for credit.
  - **Server architecture (§5.1):** the server "centers on a relational database"; the scheduler reads a shared-memory cache of about "a thousand" dispatchable instances refilled by a feeder; a single machine can dispatch "hundreds of jobs per second". Daemons "communicate and synchronize through the database"; the transitioner exists so other programs only "set a flag in the job's database record", which "eliminates the need for concurrency control of DB access". "If a daemon fails ... work for the failed component builds up in the database and is eventually processed".
  - **Validation (§3.4):** replication-based validation processes each job "on two unrelated computers"; homogeneous redundancy and homogeneous app version for bitwise comparison; adaptive replication "moves this factor close to one" (the factor of at least two lost to replication).
  - **Cloud storage (§10.8, future work):** inputs and outputs "reside on storage that is local or NFS-attached to the server"; using cloud storage via REST APIs is proposed, not implemented, as of 2019.
- **Numbers with locators:** "hundreds of jobs per second" from one server (§5.1, citing [17], not read); cache "on the order of a thousand" instances (§5.1); "millions of jobs per day" with scaled-out daemons and database (§5.1). Setting: public projects with up to millions of hosts.
- **Central elements, classified:** as B1. The paper confirms the server is the only component that must be reachable; volunteers only make outbound HTTP.
- **Fit with R1 to R7:** not a candidate.
- **Question it raises for us:** BOINC already lets downloads come from any URL with a hash and lets uploads go to other servers; the part it never moved off its own machine is the database that serialises job state. Is that the part a file-host design must replace with a rule?

#### F1. Flower framework: SuperLink, strategies, failure handling (contrast case, not a candidate)

- **Maintainers:** Flower Labs. **Link:** https://github.com/adap/flower, which the GitHub API resolves to `flwrlabs/flower`. Software. `license.spdx_id` Apache-2.0; `pushed_at` 2026-10-13T15:23:58Z; `archived` false; `releases/latest.tag_name` framework-1.39.0, `published_at` 2026-09-28T23:27:26Z (GitHub API, queried 2026-10-13 18:25 TST).
- **Version:** shallow clone of `main` at `47c6a8273e5e919623495ad8db7fa622af9f0ca8` (2026-10-13T14:53:08Z), finished 2026-10-13 18:14 TST into `sources/w2c/fl`; `framework/pyproject.toml` line 7 says `version = "1.40.0"` (unreleased main). Checkout warnings: some long paths under `baselines/` and `examples/` were not written (Windows path limit); no file under `framework/` was affected.
- **Read status:** files read: `framework/docs/source/explanation-flower-architecture.rst` (whole), `ref-flower-network-communication.rst` (lines 1 to 244), `explanation-superlink-high-availability.rst` (whole); `framework/py/flwr/serverapp/strategy/strategy.py` lines 135 to 240 (`start`); `serverapp/strategy/fedavg.py` lines 49 to 125, 162 to 280 (`configure_train`, `_check_and_log_replies`, `aggregate_train`); `serverapp/strategy/strategy_utils.py` lines 67 to 100 (`aggregate_arrayrecords`), 147 to 186 (`sample_nodes`); `serverapp/grid/grid.py` lines 129 to 161 (`send_and_receive` docstring); legacy API: `server/strategy/fedavg.py` (grep of `accept_failures`, lines 79 to 139, 223 to 229), `server/server.py` (grep of `fit_round`), `server/client_manager.py` lines 75 to 127, 178 to 185. Grep of all `framework/docs/source` `.rst`/`.md` files for "peer-to-peer", "peer to peer", "serverless", "decentraliz", "without a server", "gossip".
- **What it shows for part 1:**
  - **Roles.** A Flower server is "SuperLink, SuperExec, and `ServerApp`". The SuperLink is "A long-running process that forwards task instructions to clients (SuperNodes) and receives task results back"; the `ServerApp` holds "client selection, client configuration, result aggregation" (`explanation-flower-architecture.rst` lines 41 to 51). The topology is "hub-and-spoke" (lines 11 to 30).
  - **Who must be reachable.** "each SuperNode acts as an HTTP client and the SuperLink acts as an HTTP server"; "only outgoing connections are necessary" from a SuperNode, which does "not respond to incoming requests" (`ref-flower-network-communication.rst` lines 86 to 93). SuperLink's Fleet, Runtime and Control APIs share default port 8000 (lines 118 to 145).
  - **Strategy and client selection.** The round loop (`Strategy.start`) calls `configure_train`, then `grid.send_and_receive(..., timeout=timeout)` with default `timeout` 3600 s, then `aggregate_train` (`strategy.py` lines 140, 201 to 225). `configure_train` takes `int(len(connected nodes) * fraction_train)`, at least `min_train_nodes` (default 2) (`fedavg.py` lines 170 to 172). `sample_nodes` blocks, polling every second, until `min_available_nodes` (default 2) are connected, then draws `random.sample(all_nodes, sample_size)` (`strategy_utils.py` lines 170 to 183).
  - **Aggregation.** FedAvg is a weighted mean over valid replies: weights `w_i / Σ w` from the `"num-examples"` metric, summed array by array (`strategy_utils.py` lines 67 to 99).
  - **Failure handling.** Replies carrying an error are separated out, logged ("Received error in reply from node"), and excluded from aggregation (`fedavg.py` lines 210 to 247, 255). `send_and_receive` returns whatever arrived before the timeout; it "may not return replies for all sent messages", and "A message remains valid until its TTL" (`grid.py` lines 155 to 160). In the legacy API, `accept_failures` (default True) decides whether a round with failures is aggregated at all (`server/strategy/fedavg.py` lines 79 to 80, 228 to 229); `SimpleClientManager.wait_for` blocks until enough clients connect, default timeout 86,400 s (`client_manager.py` lines 115 to 126).
  - **Server availability.** "SuperLink High Availability Mode" puts a load balancer in front of several SuperLink replicas that "share durable state in a PostgreSQL backend"; the load balancer and PostgreSQL "become critical infrastructure"; it is "available in preview" (`explanation-superlink-high-availability.rst` lines 9 to 17, 42 to 70).
  - **Any mode without a server?** None found in the files grepped: the only match was an unrelated tutorial sentence about "decentralized data" (`tutorial-series-what-is-federated-learning.rst` line 302). The Simulation Runtime runs everything on one machine (the paper's Virtual Client Engine, F2 §3.4). (inference) Nothing in what was read prevents the SuperLink from running on one participant's machine, but that machine must accept inbound HTTP from every SuperNode, so it is a reachable server in role, even if not always on.
- **Numbers with locators:** default round timeout 3600 s (`strategy.py` line 140); `min_train_nodes` and `min_available_nodes` default 2 (`fedavg.py` lines 57 to 61); legacy `wait_for` default 86,400 s (`client_manager.py` line 115); default port 8000 (network page table). Setting: cross-device and cross-silo federated learning with a coordinating server.
- **Central elements, classified:** SuperLink (with SuperExec and `ServerApp`): **(a)** if we ran it; in HA mode, plus a load balancer and PostgreSQL, **(a)**. Optional OIDC server for user authentication (network page lines 13 to 18): a third-party service, not training coordination.
- **Fit with R1 to R7:** not a candidate; stated only for what replacing the server costs (see Findings, part 1).
- **Question it raises for us:** Flower's selection samples from "nodes connected now". A file host shows only who has uploaded, not who is online. Is "uploaded before the deadline" an acceptable stand-in for "connected and selected" in our rounds?

#### F2. Beutel et al., "Flower: A Friendly Federated Learning Research Framework"

- **Authors:** Daniel J. Beutel, Taner Topal, Akhil Mathur, Xinchi Qiu, Javier Fernandez-Marques, Yan Gao, Lorenzo Sani, Kwing Hei Li, Titouan Parcollet, Pedro Porto Buarque de Gusmão, Nicholas D. Lane (author list from the arXiv abs page). **Link:** https://arxiv.org/abs/2007.14390.
- **Version:** v5, "last revised 5 Mar 2022" (abs page fetched 2026-10-13 18:10 TST); PDF v5 fetched 18:11 TST, `pdftotext -layout`. The paper predates the SuperLink/SuperNode architecture; the current architecture comes from F1.
- **Read status:** sections read: Table 1 (built-in strategies), §3.3 "Core Framework Architecture" (right column), §3.4 "Virtual Client Engine", §5.3 passage on the cutoff-time FedAvg variant. Two-column extraction interleaves columns; quotations below were checked against the right-hand column only.
- **What it shows for part 1:**
  - "the FL loop asks the Strategy to configure the next round", sends configurations, "receives the resulting client updates (or failures)", and "delegates result aggregation to the Strategy" (§3.3). The framework "manages ... connection handling, client life cycle, timeouts, and error handling" (§3.3).
  - Table 1 lists "Fault Tolerant FedAvg", "A variant of FedAvg that can tolerate faulty client conditions such as client disconnections or laggards".
  - §5.3: a FedAvg variant where each client gets "a cutoff time" after which it "must send its model parameters to the server, irrespective of whether it has finished"; with the cutoff set to 1.99 minutes for CPU clients, convergence is faster "at the expense of a 4% accuracy drop" (Table 3 setting: Jetson and other embedded devices; dataset not confirmed in the passage read).
- **Numbers with locators:** cutoff 1.99 min, 4% accuracy drop (§5.3, Table 3). Setting: on-device FL experiments, not language models.
- **Central elements, classified:** the Flower server: **(a)** if we ran it.
- **Fit with R1 to R7:** not a candidate.
- **Question it raises for us:** the cutoff-time variant is a deadline rule applied by the client, not the server. Could a deadline written into the round's public configuration replace the server's timeout?

#### F3. Dhasade, Kermarrec, Lavoie, Pouwelse, Sharma, de Vos, "Practical Federated Learning without a Server" (Plexus)

- **Authors:** Akash Dhasade, Anne-Marie Kermarrec, Erick Lavoie, Johan Pouwelse, Rishi Sharma, Martijn de Vos. **Link:** https://arxiv.org/abs/2503.05509. Venue: EuroMLSys '25 (ACM reference block in the PDF).
- **Version:** arXiv v1, 7 Mar 2025 (only version; abs page fetched 2026-10-13 18:34 TST); PDF v1 fetched 18:34 TST.
- **Read status:** sections read: abstract, §3.1 assumptions, §3.2, §3.3 with Algorithm 1, §3.4 with Algorithm 2, §3.5, limitations passage (§5). Experiments (§4) not read beyond the abstract's numbers.
- **What it shows for part 1:** it replaces two Flower server functions with rules every node computes.
  - **Client selection by hash:** `Sample(r, s)` sorts `hash(i + r)` over the node IDs in the local view and takes the first s (Algorithm 1). "As long as the list of candidates is the same between all nodes, the order of contact and the resulting samples will mostly be the same" (§3.3).
  - **Aggregation as a rotating peer role:** the aggregator of round r is the sample member "with the largest bandwidth" (Algorithm 1); it aggregates on receiving a "success fraction" of the sample's models and sends the result to the next sample (Algorithm 2; §3.4). "The aggregator in Plexus temporarily performs the role of the FL server" (§3.5).
  - **Limits stated by the authors:** nodes are assumed connected "through a fully connected overlay network" (§3.1); "we currently assume all nodes remain online during training", and churn "requires additional coordination" (§5); in experiments "the round completes when 80% of the models are received" (§5).
- **Numbers with locators:** "up to 1000 nodes"; time-to-accuracy reduced "1.4-1.6×" and communication "15.8-292×" against decentralized-learning baselines (abstract). Setting: emulation with traces of compute speed, latency and capacity.
- **Central elements, classified:** none in the protocol; the implementation uses the IPv8 overlay library (§4.1) for authenticated messaging between nodes, which requires direct connectivity (inference).
- **Fit with R1 to R7:** not evaluated as a candidate here; cited only as evidence that selection and aggregation can be a rule plus a rotating role.
- **Question it raises for us:** Plexus's rule needs every node to hold the same member list and assumes no one leaves. With 3 to 5 intermittent peers, what replaces "the aggregator is online" when the hash picks someone who is off?

### Part 2: exchange through file hosts only

#### T1. Templar (Covenant AI): cadence, discovery and the role of the chain in object-storage exchange

- **Maintainers:** Covenant AI (formerly tplr.ai). **Link:** https://github.com/one-covenant/templar. Software, licence MIT and `pushed_at` 2026-10-04T16:14:55Z per w1c S2 (GitHub API 2026-10-13 17:19 TST; not re-queried).
- **Version:** shallow clone at `0fefc2ad763cd4cfda080e58267fe562455f3b45` (2026-10-04T17:14:54+01:00), cloned 2026-10-13 17:57 TST into `sources/w2c/tp`. Same commit as wave 1. The README says the protocol is dormant (w1c S2).
- **Read status:** files read: `hparams/hparams.json` (whole), `hparams/150M.json`, `hparams/1B.json` (whole); `src/tplr/chain.py` lines 30 to 130 and 195 to 350; `src/tplr/comms.py` lines 280 to 292, 341 to 560 (cleanup, `s3_get_object` header and time check), 1287 to 1380 (`put`), 1412 to 1450 (`get` header), 1631 to 1720 (`gather` header); `neurons/miner.py` lines 370 to 395, 455 to 500, 660 to 770, 845 to 870; `neurons/validator.py` lines 2770 to 2800, 3020 to 3070; `neurons/base_node.py` lines 130 to 160; `src/tplr/config.py` lines 50 to 80; `src/tplr/dcp_checkpoint.py` lines 520 to 580; `docs/r2_bucket_management.md` (whole). Wave-1 reads (w1c S2, w1d S1) are not repeated.
- **Read-status addendum:** audit 3 (2026-10-13) read `src/tplr/comms.py` lines 602 to 605 and 1470 at `0fefc2a` and confirmed `torch.load(..., weights_only=True)` at both places.
- **Which configuration:** `hparams.json` at this commit is a run configuration with `"project": "dough"` and `"model_size": "70B"` (lines 12, 32). It is not necessarily the Covenant-72B run's configuration.
- **How often participants upload and read (code at `0fefc2a`):**
  - **Window length:** `blocks_per_window` 115 (`hparams.json` line 20). The code assumes "≈12 s per block" in a log-message comment (`neurons/base_node.py` line 145, `eta_seconds = max(0, remaining_blocks * 12)`); this is the code's assumption, not a measured chain fact. (inference) 115 × 12 s ≈ 23 minutes per window. Covenant-72B reports a 20-minute compute window (w1d P4, §4.3).
  - **Upload:** once per window per miner. The master rank trains, logs "Training complete; waiting for window to be exhausted...", calls `wait_until_window(step_window + 1)`, then uploads its gradient for the window just finished (`miner.py` lines 685 to 701). A per-window `debug` object is also uploaded (`miner.py` lines 855 to 861). At start-up a miner uploads a "dummy gradient to mark this miner as active" (`miner.py` lines 457 to 468).
  - **Upload deadline:** the accepted interval is `time_min` = the chain timestamp of the window's first block (`sync_block = current_window * blocks_per_window`, `miner.py` lines 717 to 725, falling back to the local `time.time()` if the chain query fails) to `time_max = time_min + time_window_delta_seconds`, with `time_window_delta_seconds` 70 (`hparams.json` line 50; `miner.py` lines 727 to 730). The check compares the object's storage `LastModified` (from a HEAD request) with that interval and returns `TOO_EARLY` or `TOO_LATE` (`comms.py` lines 520 to 544).
  - **Read:** once per window, `gather_with_reserve` downloads the listed peers' gradients with `timeout=90` per peer (`miner.py` lines 750 to 765); `s3_get_object` defaults to a 30 s HEAD timeout (`comms.py` line 481). Peers are sorted before fetching ("Ensure deterministic order across processes/ranks") (`comms.py` lines 1708 to 1709). `gather_peer_count` 20 and `reserve_peer_count` 10 (`hparams.json` lines 36, 39).
  - **Peer list:** fetched each window by the master rank (`update_peers`, `miner.py` lines 480 to 488); the validator posts a new one when `peer_replacement_frequency` (2) windows have passed, effective `peer_list_window_margin` (1) window later (`validator.py` lines 3027 to 3066; `hparams.json` lines 42, 43).
  - **Checkpoints:** every `checkpoint_frequency` (10) global steps the validator saves and uploads a DCP checkpoint (`validator.py` lines 2779 to 2800; `hparams.json` line 35).
  - **Retention:** `put` defaults to `stale_retention=10` windows; the miner passes 100 for gradients; a background task deletes the uploader's own older `gradient-<window>-<uid>-v<version>.pt` objects (`comms.py` lines 341 to 410, 1287 to 1295; `miner.py` line 700).
- **Sizes:** the code logs the uploaded size as the sum of tensor bytes (`miner.py` lines 703 to 711) but no file states a typical size. Compression settings: `topk_compression` 64, `target_chunk` 64, `quantization_bins` 4 (`hparams.json` lines 25, 26, 59). Measured sizes are in wave 1 (w1d P3 Table 1: 5.45 MB to 17.21 MB per pseudo-gradient for a 512M model at 0.78% to 3.12% density; w1d P4: more than 146× compression). Not repeated here.
- **Object format:** objects are written with `torch.save` as `.pt` files (`comms.py` line 1352) and read with `torch.load(..., weights_only=True)` (`comms.py` lines 602 to 605, 1470).
- **How participants find each other's buckets:**
  - Each participant commits a 128-character string to the chain: bucket name and account ID (first 32 characters), access key ID (next 32), secret access key (rest) (`chain.py` lines 195 to 254). The bucket endpoint is `https://<account_id>.r2.cloudflarestorage.com` (`comms.py` line 290).
  - All commitments are read with one `query_map` over `Commitments.CommitmentOf` for the subnet, keyed by hotkey and mapped to UIDs through the metagraph (`chain.py` lines 264 to 322). A background task refreshes the metagraph and commitments every `fetch_interval` seconds, default 600 (`chain.py` lines 42, 94 to 112).
  - The shared "aggregator" and "dataset" buckets are not on the chain: their credentials come from environment variables `R2_AGGREGATOR_*` and `R2_DATASET_*` (`config.py` lines 63 to 67). Writing the aggregator object uses the aggregator bucket's **write** credentials (`comms.py` lines 1320 to 1331).
- **The checkpoint pointer:** after each rank uploads its shards, rank 0 lists the remote prefix, re-uploads missing shards ("mop-up"), then writes `checkpoints/<version>/_LATEST.json` containing `{"latest_window": <window>}` (`dcp_checkpoint.py` lines 520 to 556). (inference) This is the manifest-last pattern also seen in Psyche's GCS checkpoints (w1d S2). The pointer is a mutable object overwritten by whoever holds that bucket's write credentials.
- **What the chain adds, function by function (from the code above):**
  1. Registry of participants (hotkey to UID; metagraph).
  2. Registry of storage locations and read keys (commitments).
  3. A shared clock: block numbers define windows, and a block's timestamp anchors each put window.
  4. Stake, which selects whose peer list, start window and checkpoint everyone follows (`_get_highest_stake_validator_bucket`, `comms.py` line 2225; w1c S2).
  5. Weights and rewards (`set_weights`, w1c S2).
- **Central elements, classified:** Bittensor chain **(c)**; per-participant R2 buckets **(b)**, each a paid account (w1d H12); the shared aggregator and dataset buckets **(b)**, with write credentials held by the operators; the highest-staked validator, a participant role that every miner follows, **(a)** if we ran it around the clock.
- **Fit with R1 to R7 (inference):** R3 met in the sense that no peer connects to another; R1 and R2 not met as built (chain (c)); R4 not met (synchronous windows); R7: a concrete form of "signed per-peer storage", where the "signature" is the chain-registered hotkey that committed the bucket, not a signature on each file.
- **Question it raises for us:** Templar's arrival test trusts the storage provider's `LastModified` and the chain's block timestamp. On a host such as the Hugging Face Hub, is there a server-assigned timestamp per upload that a reader can obtain, and could the round's start time come from the owner's published schedule instead of a chain?

#### T2. Namjoshi, Green, Sharma, Si, "Serverless Federated Learning with flwr-serverless" (paper and code)

- **Authors:** Sanjeev V. Namjoshi, Reese Green, Krishi Sharma, Zhangzhang Si (KUNGFU.AI). **Link:** https://arxiv.org/abs/2310.15329; code https://github.com/kungfuai/flwr_serverless.
- **Version:** arXiv v1, 23 Oct 2023 (only version; abs page fetched 2026-10-13 18:26 TST); PDF v1 fetched 18:27 TST. Code: shallow clone at `bbf8a106066af241763fe34b77bda39c04f38102` (2026-02-25T15:39:49-06:00), cloned 18:29 TST into `sources/w2c/fs`; GitHub API (18:29 TST): `license.spdx_id` null, `pushed_at` 2026-02-25T22:06:34Z, `archived` false.
- **Read status:** paper: full text (§1 to §7, Tables 1 to 7; references skimmed). Code: files read: `flwr_serverless/federated_node/async_federated_node.py` (whole), `sync_federated_node.py` lines 91 to 190, `shared_folder/s3_folder.py` lines 1 to 135 and grep for `pickle`.
- **What it shows for part 2:**
  - **Design:** "the weight store is intended to be any remote folder that is accessible by the client machine, for example a bucket/blob location" (§3). Each client trains one epoch, pushes its weights, pulls whatever others have deposited, aggregates locally and continues; there is "no 'federated round'" in the asynchronous mode (§3, Algorithm 1, Fig. 2). A synchronous mode waits "until all other clients have deposited their weights" (§3).
  - **Code: one key per writer.** The asynchronous node writes `model_store[self.node_id]` (its own key, overwritten each epoch) with a `model_hash` of node ID plus wall-clock time, and reads every other key whose hash it has not seen (`async_federated_node.py` lines 141 to 177). Aggregation runs Flower's `strategy.aggregate_fit` on the client (lines 79 to 111).
  - **Code: completeness marker.** `S3Folder.__setitem__` deletes `<key>.success`, puts the object, then puts the `.success` flag; `get` polls for the flag every `retry_sleep_time` 3 s up to `max_retry` 3 times, then returns the default (`s3_folder.py` lines 7 to 11, 44 to 99). Values are Python pickles (`pickle.dumps` / `pickle.loads`, `s3_folder.py` lines 186, 201).
  - **Code: synchronous wait has no exit.** The sync node loops "while len(...) < self.num_nodes - 1" with a sleep of `min(60 * 2**wait_counter, max_retry)` and `max_retry = 3`, i.e. 3 s, and no timeout in the lines read (`sync_federated_node.py` lines 166 to 184). (inference) One missing node blocks every other node indefinitely in synchronous mode.
- **Numbers with locators (accuracy only; no storage latency, throughput or cost is reported):**
  - MNIST, 2 nodes, skew 0: sync 0.987 ± 0.001, async 0.985 ± 0.001; centralized 0.987 (Table 1).
  - Pythia-14M on WikiText-103 (first 100,000 training examples), next-token accuracy: FedAvg sync 0.26 / 0.237 / 0.227 and async 0.251 / 0.239 / 0.221 for 2 / 3 / 5 nodes; centralized 0.279 (Table 7).
  - **Setting caveat (§5, item 6):** "We simulated concurrent training jobs with python multi-threading"; no more than five nodes (item 5). (inference) The exchange through S3 was not measured across real machines or home links.
- **Central elements, classified:** the shared folder, e.g. an S3 bucket: **(b)**-like object storage (a paid account). No server, no chain.
- **Fit with R1 to R7 (inference):** R1 and R3 met by design (no server, no peer connection); R2 met if the folder is a public host the owner may use; R4 partly (asynchronous mode exists; quality evidence is small-scale); R5 and R6 not addressed (full-model replicas); R7: all writers share one folder and one credential set in the code read, separated only by key naming.
- **Question it raises for us:** the asynchronous node averages "whatever is there now", so two peers can compute different models from different reads. Is that acceptable for Chorus, or must every peer apply the same set (as in Templar and Psyche)?

#### T3. Jiang et al., "Towards Demystifying Serverless Machine Learning Training" (LambdaML)

- **Authors:** Jiawei Jiang, Shaoduo Gan, Yue Liu, Fanlin Wang, Gustavo Alonso, Ana Klimovic, Ankit Singla, Wentao Wu, Ce Zhang (ETH Zürich, Microsoft Research; per the abs page). **Link:** https://arxiv.org/abs/2105.07806. Venue: SIGMOD 2021 (not checked at source).
- **Version:** arXiv v1, 17 May 2021 (only version; abs page fetched 2026-10-13 18:26 TST); PDF v1 fetched 18:27 TST.
- **Read status:** sections read: §3.2.2 "Communication Channel" (start), §3.2.4 "Synchronization Protocol", §4.3 "Communication Channels" with Table 1 and Table 2. Table 6 (analytical-model constants) was looked at but its column alignment is garbled in extraction; no number from it is used.
- **What it shows for part 2:**
  - Function instances "cannot directly communicate", so training state goes through storage: S3, ElastiCache (Memcached, Redis) or DynamoDB (§3.2.2).
  - **A synchronous protocol built only on storage listings (§3.2.4).** Merging phase: executors write updates under names that encode "the training epoch, the training iteration, and the partition ID"; the aggregator lists names, counts them, and keeps polling until the count equals the number of workers. Updating phase: the merged file gets a similar name and executors poll until it appears.
  - **S3 against in-memory stores (§4.3, Table 1):** Memcached communication is faster than S3, "7× and 7.7×" for LR and KMeans with up to 50 workers, but end-to-end Memcached is slower for LR because it "takes more than two minutes to start Memcached whereas starting S3 is instant". Table 1, MobileNet on CIFAR-10, W = 10: Memcached relative cost 0.9 and slowdown 0.77 against S3. DynamoDB "only allows messages smaller than 400KB".
- **Numbers with locators:** as above (§4.3, Table 1). Setting: AWS Lambda functions in one cloud region, small models (LR, SVM, KMeans, MobileNet, ResNet on CIFAR-10).
- **Central elements, classified:** S3 **(b)**-like object storage; Memcached/Redis/DynamoDB are managed cloud services (a paid service; not static hosts). The "aggregator" in AllReduce is one of the functions, a role, not a server.
- **Fit with R1 to R7 (inference):** shows the mechanics of synchronous rounds over object-store listings (relevant to R4's synchronous mode). Setting is a data centre, not home links.
- **Question it raises for us:** LambdaML's "count files with this round's name until all workers have written" is a deterministic round-close rule over a listing. On a public host, how stale can a listing be, and does a reader ever see a file before it is complete?

#### T4. Grafberger, Chadha, Jindal, Gu, Gerndt, "FedLess: Secure and Scalable Federated Learning Using Serverless Computing"

- **Authors:** Andreas Grafberger, Mohak Chadha, Anshul Jindal, Jianfeng Gu, Michael Gerndt (TU Munich). **Link:** https://arxiv.org/abs/2111.03396. IEEE BigData 2021 per search snippets (not checked at source).
- **Version:** arXiv v1, 5 Nov 2021 (only version; abs page fetched 2026-10-13 18:26 TST); PDF v1 fetched about 18:28 TST after one network failure.
- **Read status:** sections read: §IV-A architecture (system overview), Fig. 2 to 3 captions, §V-B passage on FedKeeper comparison (round durations; values partly garbled). Not read: security details, most of §V.
- **What it shows for part 2:** it is **not** file-host-only. A "control plane" holds a MongoDB "Parameter Server", a MongoDB "Client Database", an OpenWhisk cluster for the aggregator function, and the "FedLess Controller", which is "responsible for selecting the clients that participate in each round, invoking them and the aggregator" (§IV-A). Clients are functions that the controller invokes over HTTP, so each client must be reachable (inference from "invoking them").
- **Numbers with locators:** a median client execution time falling "from 4.46 seconds to 3.83 seconds" after an optimisation (§V, FedKeeper comparison). Fig. 12 compares FaaS and IaaS client costs to reach a target MNIST accuracy; its values are in a figure and not recorded. Setting: cloud FaaS (AWS Lambda, GCF, Azure, OpenWhisk), MNIST/FEMNIST/Shakespeare.
- **Central elements, classified:** controller, MongoDB parameter server and client database, aggregator cluster: **(a)**.
- **Fit with R1 to R7:** not met for R1 (central controller and database). Included as a contrast: "serverless" in the FaaS sense still has a coordinator.
- **Question it raises for us:** none beyond T3; it shows that "serverless FL" in the literature usually means cloud functions plus a coordinator, not "no coordinator".

#### T5. Ziashahabi, He, Avestimehr, "Understanding Communication Backends in Cross-Silo Federated Learning" (gRPC+S3)

- **Authors:** Amir Ziashahabi, Chaoyang He, Salman Avestimehr (University of Southern California; TensorOpera). **Link:** https://arxiv.org/abs/2604.10859.
- **Version:** arXiv v1, 12 Apr 2026 (only version; abs page fetched 2026-10-13 18:26 TST); PDF v1 fetched about 18:28 TST.
- **Read status:** sections read: abstract, §I contributions, §III (gRPC+S3 design, "Advantages"), §V setting lines (model sizes), §VI Geo-Distributed result paragraph, §VII Discussion.
- **What it shows for part 2:** a hybrid in which gRPC carries metadata and the S3 object key while the model goes through S3; "the server uploads once, and all clients fetch concurrently"; S3 lets "late or failed receivers ... re-fetch without forcing the sender to re-transmit" (§III-B).
- **Numbers with locators:** in the Geo-Distributed setting, gRPC+S3 is "3.5 to 3.8× faster than gRPC for large models" (§VI); abstract: "up to 3.8× end-to-end speedup over gRPC"; recommended with "gRPC fallback for small payloads (< 10 MB)" (§VII). Models: 2.39 MB, 19.85 MB, 253.19 MB (DistilBERT) and 1,243.14 MB (ViT-Large) (§V-B). Setting: cloud VMs (AWS regions including Oregon, North Virginia, Hong Kong, Stockholm, São Paulo), cross-silo.
- **Central elements, classified:** the FL server and its gRPC endpoint **(a)**; S3 **(b)**-like.
- **Fit with R1 to R7:** R1 not met (server). It is evidence that offloading large payloads to object storage beats a single gRPC stream over long-distance links, in data-centre conditions.
- **Question it raises for us:** at 0.2 to 0.6 GB per update over home uplinks, is the upload to the host, rather than the host itself, the bottleneck? No source here measures that.

#### T6. Asyn2F (Cao et al.)

- **Authors:** Tien-Dung Cao, Nguyen T. Vuong, Thai Q. Le, Hoang V. N. Dao, Tram Truong-Huu. **Link:** https://arxiv.org/abs/2403.01417. **Version:** v1, 3 Mar 2024 (abs page fetched 2026-10-13 18:26 TST; PDF 18:28 TST).
- **Read status:** grep only of the PDF text for "queue", "S3", "MinIO", "notify", plus the lines around them (§3 architecture, §4.2 message formats). Not read in full.
- **What it shows for part 2:** a server aggregates; workers and server exchange model files through cloud storage ("AWS S3" or MinIO) and notifications through a RabbitMQ queue (grep hits around lines 105, 445 to 545 of the text).
- **Central elements, classified:** server and message broker **(a)**; storage **(b)**-like.
- **Fit with R1 to R7:** R1 not met. A contrast: storage for payloads, live broker for coordination.
- **Question it raises for us:** none new.

#### T7. Hivetrain / `bit-current/DistributedTraining` (Bittensor subnet 25): updates exchanged through Hugging Face Hub repositories

- **Maintainers:** bit-current (Hivetrain). **Link:** https://github.com/bit-current/DistributedTraining. Software. GitHub API (2026-10-13 18:32 TST): `license.spdx_id` null (the README says MIT), `pushed_at` 2024-05-30T21:47:52Z, `archived` false. (inference) Not maintained since May 2024.
- **Version:** shallow clone at `8d5dd201bcf9253f496cf9ace2c529cbf44f1be2` (2024-05-30T17:47:52-04:00), cloned 18:32 TST into `sources/w2c/dt`.
- **Read status:** files read: `README.md` (whole); `hivetrain/chain_manager.py` lines 57 to 122; `hivetrain/hf_manager.py` lines 85 to 130, 151 to 171; `hivetrain/averaging_logic.py` lines 60 to 72, 178 to 197, 544 to 581 (grep for the rest); `neurons/miner.py` lines 48 to 56, 110 to 130; `neurons/averager.py` lines 50 to 56, 102 to 106.
- **What it shows for part 2:**
  - "we integrate Hugging Face as a central hub ... without the complexities of direct exchanges" (README, Introduction). Miners upload a weight delta to their own Hub model repository; validators download and score deltas; an "averager node, a centralized node run by the subnet owner", builds the averaged base model each interval (README, Key Components).
  - **Discovery:** each miner commits its Hub repository ID to the chain (`subtensor.commit(wallet, subnet_uid, hf_repo)`), and readers fetch it by hotkey (`chain_manager.py` lines 71 to 115).
  - **Cadence:** the GPT-2 miner loop passes `send_interval=800` to `DeltaLoop` (`miner.py` lines 115 to 126; model `openai-community/gpt2`); `DeltaLoop` was not read, so the unit is not confirmed (a nearby line sets `send_interval = 600` with the comment "Every 60 seconds", `miner.py` line 51); the averager runs `run_periodic_averaging(test_loader, 7, 0.01, 1200)`, i.e. a 1,200 s period (`averager.py` line 106; parameter `t` in `averaging_logic.py` line 544); new versions are detected by comparing the latest commit SHA (`hf_manager.py` lines 151 to 159), with `check_update_interval` 300 s by default (`averaging_logic.py` line 348).
  - **Commit growth handled by squashing:** each push is followed by `super_squash_history` and a Git LFS prune (`hf_manager.py` lines 92 to 130).
  - **Format:** downloaded deltas are read with `torch.load(gradient_file_path)` without `weights_only` (`averaging_logic.py` line 70). (inference) Every reader unpickles files written by other participants.
- **Numbers:** none measured; cadence values above are code constants.
- **Central elements, classified:** Hugging Face Hub **(b)**; Bittensor chain for the repository registry and scores **(c)**; the averager, run by the subnet owner around the clock **(a)** if we ran it.
- **Fit with R1 to R7 (inference):** R3 met (no direct connection); R1 not met (averager); R2 not met (chain). It is the one precedent found of a training network whose update exchange ran on the Hugging Face Hub.
- **Question it raises for us:** with a Hub repository per participant and history squashed after every push, did the subnet hit Hub rate limits or abuse rules? The repository read records no such incident; nothing found answers it.

#### T8. HF²L / `IsaacYangSLA/hf_fl` ("Hugging Face Federated Learning")

- **Maintainer:** Isaac Yang (GitHub user `IsaacYangSLA`). **Link:** https://github.com/IsaacYangSLA/hf_fl; PyPI `hf2l`. GitHub API (18:33 TST): `license.spdx_id` null, `pushed_at` 2026-10-13T05:39:19Z, `created_at` 2026-09-03T21:36:26Z, 0 stars. PyPI JSON (fetched 18:32 TST): versions 0.1.0 and 0.1.1; 0.1.1 wheel uploaded 2026-09-08T22:55:52.
- **Version:** shallow clone at `fe9569e2fdb36af2f6295d31b7c059a6eed538cf` (2026-10-12T19:40:37Z), cloned 18:33 TST into `sources/w2c/hffl`.
- **Read status:** `README.md` lines 1 to 82, 194 to 206, 476 to 640. Not read: `docs/` (architecture, Exchange service, workflow), code.
- **What it shows for part 2:**
  - Self-described "proof of concept (POC) for coordinating federated model training through Hugging Face Hub", JFrog Artifactory, an "Exchange service" (PostgreSQL plus private S3), or a local store (README lines 1 to 12, 66 to 72).
  - **On the Hub:** clients open pull requests with submissions; the owner "needs repository write permission; clients use their own credentials and need permission to open pull requests" (lines 194 to 206). With `--discover-submissions` the owner lists open pull requests, rejects authors outside an allowlist that maps Hub usernames to participant IDs, pins each candidate revision and "verifies commit ancestry" (lines 593 to 640).
  - **Listeners:** `hf2l listen` polls the global reference, trains and uploads; the owner role "waits for enough eligible participants", aggregates and publishes; example `--poll-interval 30`; "no broker or webhook is required"; owner publication uses "Hugging Face conditional commits" (lines 476 to 516).
  - Synchronous FedAvg only; "automated swarm coordination is not implemented" (README "Three design pillars").
- **Numbers:** none (no latency, throughput or cost reported in the parts read).
- **Central elements, classified:** Hugging Face Hub **(b)**; the owner listener, which must run for rounds to advance: **(a)** if kept running around the clock, otherwise a role on the owner's machine.
- **Fit with R1 to R7 (inference):** R1 partly (no server, but rounds stop when the owner's listener is off); R2 and R3 met; R4 synchronous only; R7 shows per-participant tokens with pull requests (participants cannot write `main`).
- **Question it raises for us:** HF²L's pull-request model gives one ordered, owner-controlled record of which submissions counted. Is "the owner merges" acceptable for Chorus given the owner's unreliable power?

#### T9. Hugging Face Hub OpenAPI specification (timestamp fields only)

- **Maintainer:** Hugging Face. **Links:** `docs/hub/api.md` in `huggingface/hub-docs` (main at `bde5a40f42d949f3c3cb4ea09360482d5587038e`; the file's last commit `820e2fb4a2` 2026-03-13), which now points to https://huggingface.co/.well-known/openapi.json. Both fetched 2026-10-13 22:11 to 22:12 TST; the spec reports `openapi` 3.1.0, `info.version` 0.0.1.
- **Read status:** `api.md` (whole, 15 lines); the spec was parsed with a local script (Python `-I`) for the `tree` and `paths-info` endpoints of model repositories and Storage Buckets only.
- **What it shows for part 2:** `GET /api/buckets/{namespace}/{repo}/tree/{path}` and `POST .../paths-info` return per-file `uploadedAt` and `mtime` (`date-time`); `GET /api/models/{namespace}/{repo}/tree/{rev}/{path}` returns `lastCommit` with `id`, `title`, `date`. No field description says who assigns these times.
- **Central elements, classified:** the Hub **(b)**.
- **Question it raises for us:** a Templar-style put window on the Hub would need a server-assigned arrival time; Storage Buckets' `uploadedAt` is the candidate, to be confirmed by a test upload.

#### N1. STUNMESH-go (`tjjh89017/stunmesh-go`): WireGuard endpoints exchanged through shared storage, no relay

- **Maintainer:** tjjh89017 (GitHub user). **Link:** https://github.com/tjjh89017/stunmesh-go. Software. GitHub API (2026-10-13 18:35 TST): `license.spdx_id` LGPL-3.0, `pushed_at` 2026-10-13T06:40:35Z, `created_at` 2021-05-23, `archived` false; `releases/latest.tag_name` v1.15.1, `published_at` 2026-09-07T07:33:07Z.
- **Version:** shallow clone at `74a0d38f07df0a5fbb53af3fb6fd19713d9935bf` (2026-09-29T16:12:06+02:00), cloned 18:35 TST into `sources/w2c/sm`. The repository contains a `CLAUDE.md`; it was treated as untrusted data and not read.
- **Read status:** files read: `README.md` (whole), `contrib/README.md` (lines 1 to 50), `internal/entity/peer_id.go` lines 1 to 48, `docs/architecture.md` lines 1 to 132 (code-structure notes, little on mechanism).
- **What it shows for part 2 (hole punching coordinated through storage):**
  - It "discovers each node's public IP and port via STUN, encrypts the endpoint with a Curve25519 sealed box, and shares it through a pluggable storage backend (Cloudflare DNS, OpenDHT, or your own script)"; "No rendezvous server, no relay, no VPS in the middle" (README lines 3 to 5).
  - Storage keys are per directed pair: the hex SHA-1 of (own public key, peer public key) for writing and of (peer, own) for reading (`peer_id.go` lines 28 to 44).
  - Default `refresh_interval: "1m"`; "wait roughly two refresh intervals, and the tunnel comes up" (README lines 81 to 103). The example STUN server is `stun.l.google.com:19302` (README line 93).
  - **NAT support:** full cone, restricted cone and port-restricted cone "fully supported"; symmetric NAT "may be difficult"; "ensure at least one peer is behind a cone NAT type" (README lines 17 to 22).
  - **Backends:** Cloudflare DNS TXT records (needs a zone and API token); OpenDHT through a proxy (default `dhtproxy.jami.net`, IPv6 only, values "expire after 10 minutes", lookups "take seconds"); or an exec/shell plugin protocol for any other store (`contrib/README.md`).
  - (inference) The punch itself is WireGuard's own handshake retransmission and keepalive toward the published endpoint, repeated each refresh, so the design needs no sub-second coordination; the minute-scale refresh is what makes a slow store usable. The README does not state this mechanism in these words.
- **Numbers:** no success rates are given; the only figures are configuration defaults (1 minute refresh) and OpenDHT's 10-minute expiry.
- **Central elements, classified:** STUN server: Google's public server **(c)** in the example; it could be one of our machines only if reachable. Storage: Cloudflare DNS on the user's own zone, a hosted service holding a small record (closest to **(b)**, flagged because it is a DNS API, not a static file host); OpenDHT **(c)**; an exec plugin writing to a file host would be **(b)** (inference; not tested in what was read).
- **Fit with R1 to R7 (inference):** R1 met (nothing of ours runs around the clock); R3 met (no relay at all); but reflexive-address discovery depends on a STUN server, which is (c) unless one of our machines is reachable. It is the closest precedent found for wave-1 gap 5.
- **Question it raises for us:** STUN needs a publicly reachable server. Could a pilot use a public STUN server ((c), used only to learn one's own address, carrying no data), or would the owner treat that like a third-party relay?

#### N2. wgsd (`jwhited/wgsd`): WireGuard endpoints served over DNS-SD

- **Maintainer:** Jordan Whited. **Link:** https://github.com/jwhited/wgsd. GitHub API (2026-10-13 18:35 TST): `license.spdx_id` MIT, `pushed_at` 2023-12-26T21:23:14Z, latest release v0.3.6 (2023-12-26). **Version:** shallow clone at `537afbe95b2019ac8c32e700bd6d7dc2929e3187` (2023-12-26).
- **Read status:** `README.md` lines 1 to 60.
- **What it shows for part 2:** a CoreDNS plugin that serves the WireGuard peers' endpoints (SRV, A/AAAA, TXT records) of the host it runs on, enabling "NAT-to-NAT WireGuard connectivity where UDP hole punching is supported" and "a mesh of WireGuard peers from a central registry" (README). (inference) The registry learns peers' public endpoints from their WireGuard handshakes with it, so it must be a reachable host.
- **Central elements, classified:** the registry (CoreDNS plus WireGuard) **(a)** if run around the clock; a peer role if run on a reachable member's machine only while it is on.
- **Fit / question:** another precedent of address exchange decoupled from relaying; unlike N1, the address-learning point is a server we would run.

#### N3. HyperDHT and Hyperswarm (Holepunch): hole punching coordinated through DHT nodes

- **Maintainers:** Holepunch (`holepunchto`). **Links:** https://github.com/holepunchto/hyperdht, https://github.com/holepunchto/hyperswarm. GitHub API (2026-10-13 18:25 TST): hyperdht `license.spdx_id` MIT, `pushed_at` 2026-10-05T19:31:57Z, latest release v6.34.1 (2026-10-05); hyperswarm MIT, `pushed_at` 2026-09-22T16:37:34Z, latest v4.17.2 (2026-09-22).
- **Version:** shallow clones: hyperdht `fdcda937d8cf3ca2e494396c430218e2996e6b29` (2026-10-05), hyperswarm `1e508a7e4a632a0fe9ab6e391cfc8a791c9b5014` (2026-09-22), both cloned 2026-10-13 17:57 TST.
- **Read status:** hyperdht: `README.md` (grep plus lines 13, 71 to 124, 173, 221 to 225, 285 to 321), `lib/constants.js` lines 17 to 20, `docs/handshake.md` and `docs/holepunch.md` (whole), `lib/connect.js` (grep of comments and relay state, lines 1 to 110, 221 to 340 skimmed). hyperswarm: cloned, not read (it builds on HyperDHT).
- **What it shows for part 2:**
  - **Coordination is live and through DHT nodes.** "a handshake is performed with two intermediary relay nodes; one chosen by the client and one chosen by the server"; the client and server "don't interact directly, but instead communicate through the intermediary relay nodes" (`docs/handshake.md`). Hole-punch messages (`PEER_HOLEPUNCH`) also pass through these DHT nodes, while both sides ping each other's addresses (`docs/holepunch.md`). These "relay nodes" carry signalling; separately, `connect.js` can fall back to a `blind-relay` connection for data (`lib/connect.js` lines 3, 51 to 106).
  - **Default bootstrap:** three nodes `node1` to `node3.hyperdht.org` port 49737 (`lib/constants.js` lines 17 to 20), "publicly served on behalf of the commons" (README line 84).
  - **Private network:** "start one or more dht nodes with an empty bootstrap array" and use them as `bootstrap` everywhere; "You'll need at least one persistent node for the network to be completely operational" (README line 84). "You can run servers on normal home computers, as the DHT will UDP holepunch connections for you" (README line 124).
  - `randomPunchInterval` default 20,000 ms between punches (README line 77).
- **Numbers:** no success rates in the files read (ProbeLab, w1a S14, says it has not seen studies backing "above 90%" claims for holepunch.to).
- **Central elements, classified:** public bootstrap and DHT nodes **(c)**; a private DHT needs at least one persistent, reachable node: **(a)** if run around the clock.
- **Fit with R1 to R7 (inference):** R1 not met in a private network (a persistent node is required); R3 partly (signalling relays are DHT nodes; data relay optional). Does not use a file host.
- **Question it raises for us:** the handshake needs a DHT node that both peers can reach at the same moment; in an all-NAT pilot, which node plays that part?

#### N4. Headscale (self-hosted Tailscale control server) and its DERP documentation

- **Maintainers:** Juan Font and contributors. **Link:** https://github.com/juanfont/headscale. GitHub API (2026-10-13 18:25 TST): `license.spdx_id` BSD-3-Clause, `pushed_at` 2026-10-13T13:14:40Z, latest release v0.29.5 (2026-10-13T13:05:15Z).
- **Version:** shallow clone at `efe18a89cdfc48a8e8bc12fb0574d03811c8d1e9` (2026-10-13T14:38:29+02:00); the working-tree checkout failed (all files reported deleted), so files were read with `git show HEAD:<path>`.
- **Read status:** `README.md` lines 1 to 40; `docs/ref/derp.md` lines 1 to 60; `docs/setup/requirements.md` lines 1 to 40.
- **What it shows for part 2:**
  - Tailscale's control server is "an exchange point of Wireguard public keys"; it assigns addresses and enforces user boundaries; it is the only closed-source part of Tailscale (README "What is Tailscale").
  - Headscale needs "A server with a public IP address", HTTPS on port 443 (`requirements.md`).
  - DERP relays traffic "in case a direct connection can't be established"; the embedded DERP server also "uses STUN (udp/3478) to help clients discover their public IP addresses"; by default Headscale adds its DERP to "the list of free-to-use DERP servers offered by Tailscale Inc."; removing those leaves "a single point of failure" (`derp.md`).
- **Central elements, classified:** Headscale control server **(a)**; Tailscale's public DERP and STUN servers **(c)**; Headscale's embedded DERP **(a)**.
- **Fit with R1 to R7:** R1 not met (a reachable server); R3 met only if Tailscale's DERP map is removed.
- **Question it raises for us:** none beyond N5.

#### N5. David Anderson (Tailscale), "How NAT traversal works" (blog post)

- **Link:** https://tailscale.com/blog/how-nat-traversal-works. **Date:** August 21, 2020 (page). Page read (fetched 2026-10-13 22:05 TST with curl; tags stripped with an inline Python script run with `-I`).
- **Read status:** passages read: the "side channel" section, the firewall-timeout paragraph, the IPv6 paragraph and the closing "TL;DR" recap. The rest (NAT types, birthday-paradox section) not read here; w1a S1 cites its birthday figures.
- **What it shows for part 2:**
  - "Both endpoints must attempt communication at roughly the same time"; the side channel "can have a few seconds of latency, and only needs to deliver a few thousand bytes in total"; "In the distant past, I used XMPP chat messages as the side channel"; WebRTC leaves the "signalling channel" to the application; in Tailscale "our coordination server and fleet of DERP ... servers act as our side channel".
  - Firewalls forget idle UDP sessions ("a common value for UDP is 30 seconds"), so peers must keep sending or have "some out-of-band way of restarting the connection on demand".
  - Recipe: "A communication side channel with your peers", "A couple of STUN servers", fallback relays "optional, but highly recommended"; exchange all candidate `ip:ports` "through your side channel".
  - With IPv6 everywhere one could drop STUN and port mapping but would still need firewall traversal and "a side channel".
- **Numbers:** "a few seconds of latency", "a few thousand bytes", "30 seconds" (all as stated by the author, not measured in the post).
- **Central elements, classified:** coordination server **(a)** (for Tailscale, (c) for us); STUN servers and DERP **(c)** if third-party.
- **Fit:** vendor engineering write-up, not a measurement. It supports the idea that a slow, low-volume side channel is enough for signalling, but it does not test a file host.
- **Question it raises for us:** is a file host polled every few seconds an adequate "side channel" for the "roughly the same time" requirement, given 30-second firewall timeouts?

## Findings

No design is recommended here. "(inference)" marks reasoning; everything else cites a block above.

### Part 1: what a central server does in BOINC and Flower, and which functions could be replaced

**What the sources show.**

- **BOINC's server is a set of daemons serialised through one database.** Daemons "communicate and synchronize through the database"; the transitioner exists so that schedulers and validators only "set a flag", which "eliminates the need for concurrency control" (B2 §5.1; B1 `BackendLogic.md`). The server "must be publicly accessible via HTTP" and, by BOINC's own guidance, have "a static IP address" (B2 §2.2; B1 `ServerIntro.md`). Clients only make outbound HTTP and back off exponentially when the server is off-line (B2 §2.2).
- **BOINC already moves two functions off its own machine:** input and application files can come from "outside servers" by URL, size and MD5, and uploads "need not go to the project server" (B1 `Job-templates.md`; B2 §2.2). Work units are XML data: input files, command line, resource bounds and redundancy parameters (B1 `Job-templates.md`, `JobIn.md`). Code is signed offline (w1d T1).
- **Flower's server is a reachable HTTP endpoint that holds the live view of connected clients.** SuperNodes only make outbound connections to the SuperLink (F1, network page). Selection samples from nodes connected now and blocks until `min_available_nodes` are connected (F1, `sample_nodes`). Aggregation is a weighted mean over the replies that arrived before the timeout (default 3600 s) and carried no error (F1). Making the SuperLink highly available needs a load balancer plus PostgreSQL, in preview (F1). No mode without a server was found in the documentation grepped (F1).
- **One paper replaces Flower's selection and aggregation with a rule and a rotating role:** Plexus sorts `hash(node + round)` to pick each round's sample and makes the highest-bandwidth member the aggregator (F3, Algorithm 1). It assumes a fully connected overlay and no churn (F3 §3.1, §5).

**Function by function (classification of the replacement; all judgements are inference from the cited blocks).**

| Server function | Where shown | Replaceable by | What the replacement loses, or what it still needs |
|---|---|---|---|
| Distribute code, inputs, data shards | BOINC data servers and remote files (B1, B2 §2.2) | **(b) public host** plus hashes in a signed configuration; BOINC itself already allows this | Nothing for downloads; host limits and terms apply (w1d Q5a) |
| Define work units | BOINC work generator, XML templates (B1) | **Deterministic rule** from run seed and round (as Chorus's `assignment.py`, per the brief) plus the owner's published configuration (b) | BOINC's flow control ("constant number of unsent jobs") and per-host size matching need a live view; a rule cannot see host speed unless peers publish it |
| Dispatch: who does which unit, when | BOINC scheduler (B1 `WorkDistribution.md`); Flower `sample_nodes` (F1) | **Deterministic rule** (hash sampling, F3) over a member list in the signed configuration | Who is online now. A rule picks peers that may be off; Plexus assumes no churn (F3 §5). Matching units to host capability |
| Deadlines, timeouts, reissue of lost work | BOINC transitioner, `delay_bound` (B1, B2 §4); Flower round timeout (F1); Flower paper's client-side cutoff (F2 §5.3) | **Rule:** a deadline per round in the published configuration, with arrival judged by the host's server-side timestamp (Templar's `LastModified` window, T1) | A trusted clock. Templar takes the round start from the chain and arrival time from the host (T1); without a chain the start time must come from the published schedule or from the first upload. Reissue to another peer must also be a rule every peer computes the same way |
| Upload authentication | BOINC signed `<file_info>` to `file_upload_handler` (B1 `FileUpload.md`) | **(b) host access control:** per-participant repositories, buckets or pull requests (T1, T7, T8; w1c Q7) | The host's own rules decide who can write where (w1c S13, S14) |
| Validation (syntax, replication, quorum) | BOINC validator, `min_quorum`, adaptive replication (B1, B2 §3.4) | **Peer role** (any peer re-checks published files) or a **rule** (format and norm checks, as Templar's validators and Gauntlet, w1c S2 to S4) | Replication costs "at least 50%" of compute (B1); bitwise comparison needs homogeneous hardware classes (B1 `Homogeneous-Redundancy.md`), which consumer GPUs are unlikely to share. For a trusted pilot, BOINC's own adaptive replication suggests checking only occasionally (inference) |
| Aggregate or assimilate results | BOINC assimilator (B1); Flower `aggregate_train` (F1) | **Deterministic merge rule** every peer computes from the same input files (Psyche and Templar, w1c Q3b), or a **rotating peer role** (Plexus aggregator, F3) | Agreement on the input set. A peer that misses a file computes a different model (flwr-serverless async merges "whatever is there", T2) |
| Record of state: which units were taken, done, counted | BOINC database (B2 §5.1); SuperLink state and HA PostgreSQL (F1) | Hardest to replace. Candidates: an ordered record on a host with conditional commits (w1c S15), a single writer's merge (HF²L owner, T8; Templar leader validator, T1), or a ledger (c) | This is the same function w1c Q3d identifies as hardest ("which updates count"). BOINC's architecture exists to serialise exactly this through one database (B2 §5.1) |
| Clean-up | BOINC file deleter and db_purge (B1) | Uploader deletes its own old files (Templar `cleanup_s3_data`, T1) or host retention | None material |
| Be reachable | BOINC (static IP), Flower SuperLink (port 8000, inbound HTTP) | **(b) public host**, which every peer reaches with outbound HTTPS (B2 §2.2 shows the outbound-only client model works through firewalls) | Live push: peers must poll. A Flower SuperLink on a participant's machine would still need inbound connections (F1), which an all-NAT pool lacks (w1a Q2) |

**(inference) Summary for the report.** Most server functions in both systems split into a rule (selection, deadlines, merge), a static host (distribution, upload targets), or an occasional peer role (validation, aggregation). The function that does not split cleanly is the single serialised record of round state, which BOINC keeps in its database and Flower in its SuperLink. Replacing it needs a clock and an agreed input set; Templar shows one way (chain clock, host timestamps, leader list), HF²L another (owner merges pull requests), and flwr-serverless's asynchronous mode drops agreement altogether.

### Part 2: exchange through public file hosts only

**Systems and papers found that exchange training updates only through storage (no peer-to-peer connection):**

| System (block) | Host | Who writes where | How locations are found | Round clock and counted set | Aggregation | Measured latency, throughput or cost | Central elements |
|---|---|---|---|---|---|---|---|
| Templar / Covenant-72B (T1; w1c S2; w1d P3, P4) | Cloudflare R2, one bucket per participant | Each miner its own bucket; validators their own | Bucket name and read keys committed to the chain, refreshed every 600 s | Chain block time starts each window; upload must land within 70 s by the host's `LastModified`; leader validator's peer list fixes who counts | Every miner applies the listed peers' compressed updates | Covenant-72B: 70 s communication per round of about 20 minutes, ≤ 500 Mb/s down, 110 Mb/s up, data-centre peers (w1d P4) | Chain (c); R2 (b, paid); leader validator (a) |
| Hivetrain, Bittensor subnet 25 (T7) | Hugging Face Hub, one model repository per miner | Each miner its own repository; averager the base-model repository | Repository ID committed to the chain | Averager every 1,200 s; miners `send_interval=800` (unit not confirmed); new versions detected by commit SHA | Central averager (subnet owner) | None reported | Chain (c); Hub (b); averager (a) |
| flwr-serverless (T2) | Any shared folder, e.g. S3 | One key per node in one shared folder | Same folder for all | Asynchronous: no rounds; synchronous: wait until all nodes posted (no timeout in code) | Each node aggregates locally with a Flower strategy | None; experiments ran as threads on one machine (§5) | Object store (b-like) |
| HF²L (T8) | Hugging Face Hub (also JFrog, S3 via its own service) | Participants open pull requests; owner writes `main` | Owner's allowlist maps Hub users to participants | Owner listener polls (example 30 s), waits for enough participants, merges | Owner computes FedAvg and publishes with a conditional commit | None reported | Hub (b); owner listener (a, or a role) |
| LambdaML (T3) | S3, Memcached, Redis, DynamoDB | Workers write named files per epoch, iteration, partition | Fixed naming scheme | Aggregator counts files in a listing, polling until all workers have written | One function aggregates, writes merged file; others poll for it | S3 slower per round than Memcached ("7×"/"7.7×" for LR/KMeans), but no start-up delay; DynamoDB items < 400 KB (§4.3) | S3 (b-like); data-centre setting |

Contrasts that keep a coordinator: FedLess (controller plus MongoDB, T4), gRPC+S3 (server plus S3, "3.5 to 3.8×" faster than gRPC for large models across regions, T5), Asyn2F (server plus RabbitMQ plus S3, T6).

**Patterns common to the storage-only designs (from the blocks; the generalisation is inference):**

1. **One location per writer:** a bucket (T1), a repository (T7), a key (T2), a pull request (T8). None of the designs read lets participants overwrite each other's files.
2. **A completeness marker written last:** `_LATEST.json` after a listing check (T1), a `.success` flag after the object (T2), Psyche's manifest (w1d S2), HF²L's pinned revisions and commit ancestry (T8). A reader that ignores the marker can read a half-written upload.
3. **A registry of locations:** on a chain in both Bittensor systems (T1, T7); in a configuration or allowlist in HF²L (T8); implicit (one shared folder) in flwr-serverless (T2).
4. **Someone or something fixes the counted set:** a leader validator plus chain clock (T1), an averager (T7), the owner (T8), or nobody (T2's asynchronous mode, where each node merges what it sees).
5. **Polling, not push:** every design polls a listing, a commit SHA or a pointer (T1 to T3, T7, T8). The Hugging Face Hub also offers a bucket change-event stream (w1d H1), which none of these systems uses.

**What the chain adds in Templar, and what a signed file on a host could carry instead (inference; extends w1c Q3d):**

| Chain function in Templar (T1) | Signed file on a public host (b)? |
|---|---|
| Participant registry (hotkey to UID) | Yes: an owner-signed member list in the published configuration |
| Storage registry with read keys (128-character commitment, refreshed every 600 s) | Yes: locations in the same signed configuration; public read needs no keys on a public repository |
| Round clock (block number, block timestamp) | Partly: a schedule in the configuration plus host-side timestamps. The Hub API lists `uploadedAt` and `mtime` per file for Storage Buckets and only `lastCommit.date` for repositories (T9); whether `uploadedAt` is assigned by the server, and whether a commit date can be set by the client, is not stated (Could not verify) |
| Choosing the leader whose list and checkpoint everyone follows (stake) | Only by fixing the rule (for example the owner's key, or a hash rotation as in F3); the owner's key brings back a single writer |
| Weights, rewards, slashing | Not needed for a trusted pilot (w1c Q3d) |

**Using a file host to coordinate a hole punch (wave-1 gap 5):**

- **Precedent exists, outside training.** STUNMESH-go publishes each node's STUN-discovered endpoint, encrypted, in shared storage (Cloudflare DNS TXT records, OpenDHT, or any store reached by an exec script), reads its peers' endpoints from the same storage and points WireGuard at them: "No rendezvous server, no relay" (N1). It works for cone NATs and asks that at least one peer be behind one; symmetric NAT "may be difficult" (N1). It reports no success rates.
- **The side channel can be slow.** Tailscale's write-up says the signalling channel "can have a few seconds of latency, and only needs to deliver a few thousand bytes", and that its author once used XMPP chat messages (N5). STUNMESH-go refreshes every minute and expects the tunnel after "roughly two refresh intervals" (N1).
- **What the precedents still need:** a STUN server to learn one's own public address (Google's public one in STUNMESH-go's example, (c); N1), or Tailscale's or Headscale's STUN on a public machine (N4, N5); live DHT relay nodes in HyperDHT (N3); a public-IP control server in Headscale (N4); a reachable registry in wgsd (N2).
- **(inference) Decomposition of what a reachable relay does in DCUtR or iroh (w1a S1, S9), against a static file host:**
  1. *Address exchange:* a file host can carry it (N1 does, through DNS or a script).
  2. *Learning one's own public address and port:* a file host cannot, because an HTTPS upload reveals at most the TCP source address to the host, and the host does not report it back. This needs STUN (a reachable server: (c) if public, or one of our machines if reachable), a UPnP/PCP mapping, or IPv6 (w1a Q2).
  3. *Timing:* DCUtR synchronises to half an RTT over the relay (w1a S1); STUNMESH-go instead repeats WireGuard's handshake every refresh (N1), and Tailscale says "roughly the same time" (N5). Minute-scale retries fit inside the 30-second-to-a-few-minutes firewall timeouts only if peers keep sending (N5; w1a S13). Untested with a file host.
  4. *Fallback transport for bulk data:* a file host does this by itself, since uploading and downloading the update is the exchange (T1, T7).
- **No source tests file-host-coordinated hole punching between two home NATs, or reports its success rate.**

**Numbers for latency, throughput and cost in storage-only training:** the only per-round figures found are Covenant-72B's (data-centre peers, w1d P4) and LambdaML's relative comparisons (one cloud region, T3). Nothing measures exchange through a public file host over home connections, and neither Hub-based system (T7, T8) reports timings.

## Could not verify

- **Venues of LambdaML (SIGMOD 2021) and FedLess (IEEE BigData 2021):** seen only in search results; the arXiv pages read do not state them in the parts read.
- **LambdaML Table 6 (S3 bandwidth and latency constants):** column alignment garbled in the PDF extraction; no number taken.
- **FedLess Fig. 12 cost values:** in a figure; extraction garbled.
- **STUNMESH-go success in practice:** no success rate, field study or user count found; the FOSDEM 2026 talk and the documentation site (docs.stunmesh.dev) were not read. Whether anyone uses an exec plugin backed by a static file host (GitHub, the Hub) was not found.
- **HF²L's webhook-triggered GitHub workflow (`docs/FEDAVG_WORKFLOW.md`) and its Exchange service:** not read.
- **Hivetrain's operating history** (Hub rate limits hit, run length, number of miners): nothing found in the repository read.
- **Whether the Hugging Face Hub's per-file times are server-assigned** (the analogue of R2's `LastModified` in T1): the OpenAPI spec lists `uploadedAt` and `mtime` for Storage Bucket files and `lastCommit.date` for repository files (T9), with no description of who sets them. The names suggest `uploadedAt` is server-side and `mtime` client-supplied, but that is inference.
- **IPFS- and blockchain-based FL papers (IPLS arXiv 2101.01901, GFL 2010.10996, BRFL 2310.13403), GitFL (2211.12049), FLHub (2202.06493):** known only from search results; not read, so nothing is recorded from them.
- **Tailscale's "few seconds of latency" side-channel claim:** an author's statement in a blog post, not a measurement.
- **Hyperswarm itself:** cloned but not read; its behaviour is assumed to follow HyperDHT (N3).
- **Flower's "Fault Tolerant FedAvg" implementation:** named in the paper's Table 1 (F2); its code was not read.

## Gaps

1. **No measurement of training exchange through a public file host over home connections.** Per-round latency, upload time of 0.2 to 0.6 GB on home uplinks, listing staleness and host rate limits all remain unmeasured. A pilot measurement would be the only source.
2. **No tested precedent of hole punching coordinated through a static file host between two home NATs.** STUNMESH-go uses DNS records or a DHT, not a static file host, and reports no rates. Reflexive address discovery still needs STUN or port mapping.
3. **Hugging Face Hub as a bulletin board for training:** two small precedents (Hivetrain, HF²L), neither with timings or reports of hitting Hub limits.
4. **Part 1 coverage:** BOINC paper §6 (scheduling policy) and Flower's Simulation Runtime were not read; BOINC's account-manager and BOINC-run project-list servers were noted but not examined.
5. **Agreement on the counted set without a ledger or single writer:** no source found that solves it on a plain file host; consistent with w1c's negative result.
6. **Serverless-FL literature beyond the four papers read** (Apodotiko 2404.14033, FLStore 2503.00323, LIFL, λ-FL) was not read; the search snippets suggest FaaS designs with coordinators, which would not change part 2's conclusion, but this is unverified.

## Query log

- 2026-10-13 17:53:47 TST: read the brief and the wave-1 notes (w1a sections S1 to S15 headings, S9 to Q2 findings; w1c S2 Templar, Q3 and Q7 findings; w1d H1 to T7 and Q5 findings).
- 2026-10-13 17:54:45 TST: created `sysstudy/sources/w2c/` and `sysstudy/scripts_w2c/`.
- 2026-10-13 17:55:01 TST: first `git clone --depth 1` of BOINC/boinc.wiki, adap/flower, one-covenant/templar, holepunchto/hyperdht, holepunchto/hyperswarm, juanfont/headscale: all failed ("Could not resolve host: github.com"; transient network loss; boinc.wiki partial). Directories removed.
- 2026-10-13 17:57:24 TST: clones retried into new empty directories under `sources/w2c/` (`bw`, `tp`, `hd`, `hs`, `hsc`, `fl`); all succeeded; Headscale's checkout failed (files read with `git show`); Flower finished 18:14:15 with long-path warnings outside `framework/`. HEAD SHAs are in each block.
- 2026-10-13 about 17:58 to 18:10 TST: read BOINC wiki pages (list in B1).
- 2026-10-13 18:10:46 TST: curl arxiv.org/abs/1903.01699 and /abs/2007.14390 (`sleep 3` between); 18:11:04 PDFs 1903.01699v1 and 2007.14390v5; `pdftotext -layout`.
- 2026-10-13 18:11 to 18:20 TST: read Templar files (list in T1).
- 2026-10-13 18:20 TST (approximate): advisor consulted on approach before writing.
- 2026-10-13 18:20 to 18:25 TST: read Flower docs and code (list in F1); Flower paper sections (F2).
- 2026-10-13 18:25:00 TST: `gh api repos/{adap/flower, BOINC/boinc, holepunchto/hyperdht, holepunchto/hyperswarm, juanfont/headscale, tailscale/tailscale}` and `.../releases/latest` (fields `license.spdx_id`, `pushed_at`, `archived`, `tag_name`, `published_at`). adap/flower resolves to flwrlabs/flower. BOINC/boinc: LGPL-3.0, `pushed_at` 2026-10-13T13:38:44Z, latest release server_release/1.6/1.6.2 (2026-06-12) (recorded, not used further). tailscale/tailscale: BSD-3-Clause, `pushed_at` 2026-10-12T15:07:15Z, latest v1.104.1 (2026-10-07) (recorded; code not read).
- 2026-10-13 about 18:25 TST: WebSearch "serverless federated learning cloud functions arXiv" (leads: FedLess 2111.03396, Apodotiko 2404.14033, FLStore 2503.00323, 2402.07295).
- 2026-10-13 about 18:25 TST: WebSearch "federated learning shared object storage S3 no server asynchronous" (leads: flwr-serverless 2310.15329, Asyn2F 2403.01417, 2604.10859, FLSys 2111.09445, a patent).
- 2026-10-13 about 18:25 TST: WebSearch "serverless machine learning training communication S3 Redis LambdaML" (leads: LambdaML 2105.07806, SMLT 2205.01853).
- 2026-10-13 18:26:23 to 18:26:43 TST: curl arXiv abs pages 2310.15329, 2105.07806, 2111.03396, 2604.10859, 2403.01417 (`sleep 3` between).
- 2026-10-13 18:26:43 to 18:28:22 TST: PDFs v1 of the same five (`sleep 3` between); 2111.03396 and 2604.10859 failed ("Failed to connect to arxiv.org"), retried at 18:28:47 with `--retry 3` and `sleep 4`, succeeded.
- 2026-10-13 18:29:25 TST: `git clone --depth 1` kungfuai/flwr_serverless (`sources/w2c/fs`); `gh api repos/kungfuai/flwr_serverless`.
- 2026-10-13 about 18:31 TST: WebSearch "federated learning git repository as coordination medium model updates commits" (leads: GitFL 2211.12049, FLHub 2202.06493, harmonia, hf2l).
- 2026-10-13 about 18:31 TST: WebSearch "decentralized training Hugging Face Hub exchange model updates between peers no server" (leads: bit-current/DistributedTraining, Plexus 2503.05509, IPLS 2101.01901, hf2l).
- 2026-10-13 about 18:31 TST: WebSearch "federated learning IPFS model exchange decentralized storage arXiv latency" (leads: IPLS, GFL 2010.10996, BRFL 2310.13403, 2307.10492, 2602.04384; none read).
- 2026-10-13 18:32:50 TST: `git clone --depth 1` bit-current/DistributedTraining (`dt`); `gh api repos/bit-current/DistributedTraining`; curl https://pypi.org/pypi/hf2l/json (parsed with Python `-I`).
- 2026-10-13 about 18:33 TST: `git clone --depth 1` IsaacYangSLA/hf_fl (`hffl`); `gh api repos/IsaacYangSLA/hf_fl`.
- 2026-10-13 18:34:38 TST: curl arxiv.org/abs/2503.05509, `sleep 3`, PDF v1; `gh api repos/IsaacYangSLA/hf_fl --jq .created_at`.
- 2026-10-13 about 18:34 TST: WebSearch "NAT hole punching without rendezvous server exchange endpoints via DNS TXT record or shared file WireGuard" (leads: wgsd, WireGuard mailing-list PoC 2016, wg-wormhole).
- 2026-10-13 about 18:34 TST: WebSearch "WebRTC manual signaling copy paste SDP serverless peer connection github gist signaling" (leads: serverless-webrtc-testbench, rcasto/peer-net, @sctlib/rtc; none read).
- 2026-10-13 about 18:35 TST: WebSearch "stunmesh-go wireguard STUN endpoint exchange cloudflare DNS plugin" (lead: tjjh89017/stunmesh-go).
- 2026-10-13 about 18:35 TST: WebSearch "hole punching coordinated through git repository or pastebin endpoint exchange p2p no relay" (leads: quic-holepunch, mosh-devel 2012 thread, p2ptool; none read).
- 2026-10-13 18:35:33 TST: `git clone --depth 1` tjjh89017/stunmesh-go (`sm`) and jwhited/wgsd (`wg`); `gh api` for both. STUNMESH-go's `CLAUDE.md` not read (untrusted).
- 2026-10-13 about 18:36 TST to 22:00 TST: session interrupted by a network error while reading the STUNMESH-go README; resumed at 22:00:42 TST.
- 2026-10-13 22:00 to 22:05 TST: read Plexus §3 to §5 (F3), wgsd README (N2), HyperDHT README, constants, docs and `connect.js` (N3), Headscale README and docs via `git show` (N4).
- 2026-10-13 22:05:57 TST: curl https://tailscale.com/blog/how-nat-traversal-works (tags stripped with an inline Python script, `-I`); passages read (N5).
- 2026-10-13 about 22:09 TST: advisor consulted before handback; three wording fixes applied (T1 quotation, T7 unit, F2 dataset).
- 2026-10-13 22:11:42 TST: `gh api repos/huggingface/hub-docs/commits/main` and `commits?path=docs/hub/api.md`; curl raw `docs/hub/api.md` at `bde5a40`; 22:12:08 curl https://huggingface.co/.well-known/openapi.json, parsed with `scripts_w2c/oapi.py` and `oapi2.py` (Python `-I`) (T9).
- WebFetch was not used. No number or claim above comes from a search snippet. Nothing downloaded was run, built or installed.

**Not covered in this strand:**
- Hyperswarm's own code (cloned, not read); iroh beyond w1a S9.
- Apodotiko, FLStore, LIFL, λ-FL, SMLT, FLSys (serverless or storage-assisted FL with coordinators): leads only.
- IPLS, GFL, BRFL and other IPFS-plus-ledger FL papers; GitFL; FLHub; harmonia: leads only.
- Manual WebRTC signalling projects and the 2016 WireGuard hole-punching proof of concept: leads only.
- STUNMESH-go documentation site and FOSDEM 2026 talk; HF²L `docs/`.
- BOINC paper §6 (scheduling) and §7 (credit); Flower's Simulation Runtime and Fault Tolerant FedAvg code.
- Tailscale's own coordination-server documentation (only the blog post read).
