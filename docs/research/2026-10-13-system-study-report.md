# Coordinating volunteer training with no server of ours: system study report

| | |
|---|---|
| Date | 2026-10-13 |
| Status | Draft for the owner; audited 2026-10-13 (every number in sections 1 to 6 against raw sources; unverified items), fixes applied, changed lines re-audited and a second independent unverified-items audit run |
| Answers | [`2026-10-13-system-study-brief.md`](2026-10-13-system-study-brief.md) (ROADMAP step 1.1; acceptance criteria D34, D35, D37, D38) |
| Method | Seven research strands in two waves on 2026-10-13, local time (TST, UTC+3): wave 1 (w1a to w1d) 17:18 to 17:50; wave 2 (w2a to w2c) 17:53 to about 18:45, with w2c resumed 22:00 to 22:12 after a network outage. Papers were read in raw text (arXiv PDF through `pdftotext`, or arXiv HTML where a table was garbled); documentation, specifications and READMEs were fetched raw; code was read from shallow clones and never run, built or installed. Maintenance facts are dated GitHub API and package-index records with their raw fields. No number comes from a search snippet or a summarizing page fetch. Arithmetic is marked "(inference)". |
| Notes | [2026-10-13-system-study-notes/](2026-10-13-system-study-notes/): [w1a discovery, NAT, bootstrap](2026-10-13-system-study-notes/w1a-discovery-nat-bootstrap.md), [w1b averaging without a server](2026-10-13-system-study-notes/w1b-averaging-without-a-server.md), [w1c membership and shared state](2026-10-13-system-study-notes/w1c-membership-shared-state.md), [w1d storage, trust, bandwidth](2026-10-13-system-study-notes/w1d-storage-trust-bandwidth.md), [w2a systems health](2026-10-13-system-study-notes/w2a-systems-health.md), [w2b churn](2026-10-13-system-study-notes/w2b-churn-handling.md), [w2c contrasts and file-host exchange](2026-10-13-system-study-notes/w2c-contrasts-filehost-exchange.md) |
| Earlier research | [Stage 0 literature report](2026-10-11-stage0-literature-report.md) and its [notes](2026-10-11-literature-notes/), cited as "Stage 0 report §3.1" or "note 01 A8" |

**Citations.** "w1b S9" is source block S9 of notes file w1b; "w2b F4" is finding F4 of w2b. Locators inside the notes (section and version, table, file and line at a commit, API field and query time) are carried where a number is used. Read status: **F** full text, **P** paper sections, **C** code read, **D** documentation, README or specification read, **A** API or package-index record only.

**One interpretation, for the owner to confirm.** R4 (D37) says production training "averages asynchronously or in groups of available peers". This report reads **deadline-bounded group averaging of whichever peers have posted by a round's deadline** as meeting the "groups of available peers" branch, although each such round is synchronous within its group. Sections 1, 4 and 5 depend on this reading.

---

## 1. Summary

**Answer.** Volunteer training can be coordinated with nothing of ours always on, but the evidence supports one shape: deadline-closed rounds with inputs on a public file host, merged by every peer from the same files. Every system read with one shared model keeps one function central: **an agreed record of which updates count in a round**. Psyche keeps it on a ledger, Templar in a ledger clock plus one validator's list, HF²L with the owner, BOINC in its server database and Flower in its SuperLink (w1c Q3d; w2c part 1); flwr-serverless's asynchronous mode has none, so peers can merge different sets (w2c T2). For a trusted pilot, an owner-signed configuration plus a conditional ("compare-and-swap") commit log on the Hugging Face Hub could carry it (inference, untested; w1c S15).

**Three findings constrain every design.**

1. **Asynchrony and having no server pull against each other.** Every asynchronous method read that applies stale updates keeps the global model on one central holder; only the one-round overlap methods avoid one, by keeping a synchronous all-reduce (w1b F1, F2). The server-free methods are synchronous group all-reduce (Moshpit, DeDLOC, SWARM) and gossip, which leaves no single shared model; pure pairwise gossip costs about 0% to 5% against DiLoCo at 8 to 32 workers (inference: loss ratios in w1b S10, log-perplexity ratios in S9), while NoLoCo's results range from −1.45% to +0.42% (inference, w1b S8). So R4's asynchronous branch is closed under R1 unless the owner accepts a rotating holder, which no source tests; its group branch is open.
2. **Direct connections need one of our machines to be reachable** (w1a Q2). Exchange through file hosts needs only outbound connections (inference) and has four precedents whose design is not tied to one cloud region (unlike LambdaML), none measured on home connections (w2c part 2).
3. **Reuse means old training code or a networking library.** Hivemind, Petals, prime-diloco and Templar are dormant or barely maintained; Psyche's repository has had no default-branch commit since 2026-03-20 (status not confirmed; see section 7); none documents native Windows support. go-libp2p and iroh released within the last month and test on Windows (w2a; GitHub API, queried 2026-10-13).

**Designs that meet R1 to R7 (inference; section 4).**

- **A. Bulletin board.** All exchange, and a conditional-commit log of each round's counted set, on public file hosts; every peer merges. Central: signing key, configuration, host (b).
- **B. Private peer swarm.** Group all-reduce among our machines over iroh or libp2p; meets R1 and R3 only while one of ours is reachable (unmeasured).
- **C. Hybrid.** A as record and fallback; B's direct transfer where measured to work.

In all three, rolling assignment gives each expert 2 holders; churn can still leave 1 or 0, which no volunteer system read prevents without operator-run machines (w2b F5, inference). Publishing the merged model every round caps the loss at one round of that expert's training (inference). Ledgers, public STUN and the Hub's bucket event stream are class (c) or borderline: flagged, not recommended.

**Recommendation (inference; the owner decides under D35).** Write our own thin layer for Option A on `huggingface_hub`, safetensors and the existing coordinator code, with a replaceable transport for C. Participants write only their own repositories and signed log entries (section 4.5). Gate N1b's candidate: deadline-quorum rounds against the synchronous mode and centralized training. It depends on the R4 reading and four prototypes (section 6): Hub commit limits, concurrent conditional commits, upload times from pilot homes, merge determinism.

**Confidence.** Moderate on negative findings 1 and 2: they rest on the sections and code paths the notes list as read, not on full reads or an exhaustive search. Low on anything quantitative: no source measures home links, groups of 3 to 5, an expert's holders falling from 2 to 1, or file-host exchange of 0.2 to 0.6 GB updates (w1b gaps; w2b F6; w2c gap 1).


---

## 2. Requirements matrix

Every rating is **inference** from the mechanism cited, as the notes label their own "Fit" lines. "Not addressed" means the system has nothing to say about that requirement. The R7 column names the write-access option the system embodies: **1** per-participant tokens to a shared repository, **2** signed per-peer storage, **3** peer-to-peer only, **4** a ledger. Central elements: **(a)** a server we would run, **(b)** a public static-file host, **(c)** a public third-party network for live coordination. Read status letters are defined in the header.

### 2.1 Systems and building blocks

| Candidate | R1 no server of ours | R2 only allowed central elements | R3 own relays only | R4 async or group, plus sync | R5 2 holders per expert | R6 both work units | R7 write access | Keeps central |
|---|---|---|---|---|---|---|---|---|
| **Hivemind** (DHT, `p2pd`, averager) | Partly: a listed initial peer must be up and reachable at join (w1a S7, C) | Partly: bootstrap list can be ours; DHT not persisted by design (w1a S7, C) | Partly: relays are its own peers, limits raised to 4 GiB and 30 min, but must be reachable; all-NAT mode uses public IPFS (w1a S7, C) | Met in mechanism: group all-reduce with timeouts and fallback to local update (w2b B1, C) | Not met: `min_group_size` 2 is a threshold; its MoE layer has 1 holder per expert (w2b B1, C) | Partly: full copies used by DeDLOC and OpenDiLoCo; per-expert groups untested (w2a 1, D; section 7) | Option 3: owner-signed, expiring DHT records; durable state needs a host (w1c S12, C) | Initial peers (a) if always on; `use_ipfs` (c); wheel and binary on PyPI and GitHub (b) (w2a 1, A) |
| **Petals** | Partly: the wiki recommends always-on bootstrap machines when servers are unreliable but lets them be skipped; a join needs one listed initial peer alive (w1a S8, D) | Partly: private-swarm bootstrap list (w1a S8, D) | Partly: relays are its own peers, if reachable (w1a S8, C) | Not addressed: servers do not update weights (w2b B5, P) | Precedent only: rebalancing covers blocks; a sole holder never leaves (w2b B5, C) | Not met | Not applicable | Public bootstrap and health API (c); private bootstrap (a); weights on the Hub (b) (w2a 2) |
| **Agora, Node0** (Pluralis) | Not met: Authorizer, monitors, operator reducers (w1c S11, P) | Not met | Not met: public inbound port required; no relays described (w2a 13, D) | Met: asynchronous partial averaging within a stage (w2b B11, P) | Partly: operator floor of 4 to 16 replicas per stage (w2b B11 §5.1, P) | Not met: pipeline stages | Signed short-lived credentials from one Authorizer; operator-only checkpoints (w1c S11, P) | Authorizer and services (a); operator S3 checkpoints (b-like) |
| **libp2p** (go; also rust, py, js) | Met: every role is a peer role (w1a S3, S4, D and C) | Partly: application supplies the bootstrap list; go DHT does not persist its routing table (w1a S4, C) | Met in configuration: pnet, static relays, ACL; a relay must be reachable; default limits 2 min and 128 KiB (w1a S4, S5, C) | Not addressed (transport) | Not addressed | Not addressed | Not addressed | None required; default IPFS bootstrap list (c) if used (w1a S4) |
| **iroh** | Met only with non-default configuration (w1a S9, C) | Partly: addresses can be supplied by the application (`MemoryLookup`) (w1a S9, C) | Met with our own reachable relay; relays carry all traffic when punching fails (w1a S9, C and D) | Not addressed (transport) | Not addressed | Not addressed | Not addressed | Default n0 relays and DNS lookup (c); self-hosted relay (a) if always on (w1a S9) |
| **Psyche** | Partly: Solana coordinator is not ours but is (c); TCP coordinator is a development tool (w1c S1, D and C) | Not met: Solana is outside R2 | Partly: relays can be disabled; defaults are project relays and n0 discovery (w1a S15, C) | Not met: synchronous steps behind a witness barrier (w1c S1, C) | Not addressed: one trainer per batch (w2b B7, C) | Partly: full copies, per-step data parallel; no slices (w2a 8) | Option 4; any epoch member can repoint the checkpoint (w1c S1, C) | Solana (c); Hub checkpoints (b); relays and discovery (c) for us; RPC providers (c) (w2a 8, D) |
| **Templar, Covenant-72B** | Partly: no server of ours, but every miner follows one leader validator (w1c S2, C) | Not met: Bittensor (c) | Met: no peer connections; all exchange through object storage (w1c S2; w1d P4, P) | Not met: synchronous windows (w2c T1, C) | Not addressed | Partly: full copies only | Option 2: one R2 bucket per participant, read keys on chain (w1c S2, C) | Bittensor (c); R2 buckets (b, paid per participant); leader validator (a if ours). README notice "Templar is dormant" added 2026-03-31 (commit `142666f0dd91`; w2a 11) |
| **prime-diloco** (INTELLECT-1's framework by its own description; section 7) | Not met: master key-value store on rank 0 for the whole run (w1c S5, C) | Partly: remote checkpoints through fsspec (w1d S3, C) | Not met as run: Tailscale VPN (w1c S5, P) | Partly: synchronous DiLoCo all-reduce, usable for D38's mode (w2a 9) | Not addressed | Partly: full copies only | None described; trust implicit (w1c S5, P) | Rank-0 store (a); Tailscale, (c) by inference only (section 7); remote store (b) |
| **PCCL** | Not met: a master; "Master Crash = End of Run" (w2b B8, D) | Not addressed | Not met: open ports needed; no relays (w2b B8, D) | Partly: synchronous fault-tolerant collectives (w2a 10) | Not addressed; peer groups per expert unconfirmed (section 7) | Partly: full copies | Not applicable; bit-identical state checked by hash (w1c S7, P) | Master (a) |
| **Gensyn RL Swarm** | Not met: a stage-manager account advances rounds (w1c S9, C) | Not met: Gensyn Testnet (c) | Not addressed | Not addressed: each node keeps its own model (w1c S9, SAPO abstract only) | Not addressed | Not addressed | Option 4 as a registry and round clock (w1c S9, C) | Testnet (c); stage manager (a) |

### 2.2 Algorithms and storage-only approaches

| Candidate | R1 | R2 | R3 | R4 | R5 | R6 | R7 | Keeps central |
|---|---|---|---|---|---|---|---|---|
| **Moshpit SGD, DeDLOC** (group averaging, run on Hivemind) | Partly: no server in averaging; DeDLOC needs a backbone peer "available at all times" (w1b S4, P) | Partly: DeDLOC's first peer pushed state to the Hub (w2b B4, C) | Partly: participants with public addresses served as STUN and relays; (c) only if a public libp2p network is used (w1b S4, P) | Met: group all-reduce; a failed groupmate makes the group skip a round (w1b S3, P) | Not addressed: full replicas (w2b B3, C) | Partly: full copies; averaging any vector in any group fits holder groups (w1b S3) | Not addressed; DeDLOC used an allowlist authorization server (w1d P10, P) | Backbone peer (a); authorization server (a); DHT among peers (none if ours) |
| **SWARM** | Partly: no server; DHT bootstrap (w1b S5, P) | Not addressed | Not addressed | Partly: synchronous per-step averaging within stage groups (w1b S5, P) | Partly: several peers per stage; survives with one; no minimum (w2b B6, P and C) | Not met: stages, not experts or local-step copies | Not addressed | DHT (none if ours) |
| **Central-holder asynchrony**: Async Local-SGD, HeLoCo, HALoS (stale updates); Decoupled DiLoCo (quorum merge at a syncer, no stale gradient, App. A) | Not met as published: one server or syncer holds the global state (w1b F2, P) | Not addressed | Not addressed | Met: asynchronous | Not addressed | Partly: full copies; Decoupled DiLoCo's MoE runs hold every expert (w1b S1, P) | Not addressed | Server, syncer or parameter servers (a) |
| **Gossip local SGD**: NoLoCo, Factored Gossip LocalM1M2, GASLoC | Met in the algorithm: pairs only (w1b F2, P) | Not addressed | Not addressed | Met: no global barrier, but no single shared model (w1b F1, P) | Not addressed | Partly: full copies | Not addressed | None; NoLoCo's code assumes a fixed world (w2b B10, C) |
| **One-round-delayed merges**: Eager Updates, Streaming DiLoCo overlap | Met: all-reduce, no server (w1b S13, S14, P) | Not addressed | Not addressed | Partly: a bounded delay, not membership asynchrony | Not addressed | Partly: full copies | Not addressed | None |
| **FoMoE** (holder-group averaging) | Not met as published: a "central coordinator to manage initialization, broadcasting, and aggregation", synchronous rounds only (FoMoE §3.1; w1b S17, via note 04a; F) | Not addressed | Not addressed | Not met: synchronous | Met: O_e holders per expert; O_e = 2 is R5's minimum | Met for slices (dense part over all, experts within holder groups); full replica as baseline | Not addressed | Coordinator (a) |
| **flwr-serverless** | Met: no server (w2c T2, C) | Met if the folder is an allowed host | Met: no connections | Partly: asynchronous mode merges whatever is there; synchronous mode waits forever (w2c T2, C) | Not addressed | Partly: full copies | One shared folder and one credential set (w2c T2, C) | Object store (b-like) |
| **HF²L** | Partly: rounds stop while the owner's listener is off (w2c T8, D) | Met: the Hub | Met | Not met: synchronous FedAvg only | Not addressed | Partly: full copies | Option 1 variant: participants open pull requests, the owner merges (w2c T8, D) | Hub (b); owner listener (a if always on) |
| **Hivetrain** (Bittensor subnet 25) | Not met: central averager run by the subnet owner (w2c T7, C and D) | Not met: chain registry (c) | Met | Not met: periodic central averaging | Not addressed | Partly: full copies | Option 2: one Hub repository per miner, history squashed after each push (w2c T7, C) | Hub (b); chain (c); averager (a) |
| **Plain public storage**: Hub, GitHub releases, BitTorrent, IPFS | Met for the Hub and GitHub; BitTorrent needs a tracker on our machines or the public DHT; IPFS persistence needs an always-on node or a paid pinning service (w1d H9, H11, D) | Met for the Hub, GitHub and BitTorrent (named in R2) | Met: no relays | Not addressed (storage) | Not addressed | Not addressed | Depends on host roles and tokens (w1c S13, S14, D) | (b); tracker (a) or public DHT (c); IPFS (a) or (c) |

### 2.3 Contrast cases (not rated)

**BOINC** keeps a project server, class (a), which must have "a static IP address" (w2c B1, D). **Flower** keeps a SuperLink, "a long-running process" that clients reach over HTTP, class (a) (w2c F1, D and C). Both are read only for what replacing their server costs (section 3, Q3).

---

## 3. Findings by question (1 to 10)

### Q1. Discovery and bootstrap

**What the sources show**

- **Every system read needs at least one live, reachable contact at join time.** Hivemind raises "DHTNode bootstrap failed" when none of its `initial_peers` answers a ping (`hivemind/dht/node.py` lines 219 to 245 at `4bd43b7`). go-libp2p-kad-dht, with an empty routing table, dials its bootstrap list until 2 succeed and otherwise has nothing; it retries every 2 minutes (`dht.go` lines 497 to 560). rust-libp2p's `bootstrap()` returns `NoKnownPeers`. Petals says peers join "as long as at least one of their initial peers is alive" (w1a Q1, S4, S5, S7, S8).
- **The systems' own guidance assumes always-on public machines.** Hivemind asks for "any computers with a public IP address that are always online"; Petals for "a few CPU-only machines that are always online" (w1a S7, S8). Run by us around the clock, these are class (a).
- **When every bootstrap peer is offline, nothing read recovers by itself.** go-libp2p-kad-dht does not reuse a previous routing table (a TODO cites issue #387) and keeps its datastore in memory; Hivemind's DHT holds "temporary metadata" that is not persisted (w1a S4, S7). The BitTorrent DHT specification does the opposite: the routing table "should be saved between invocations", and new clients can use contacts shipped in a torrent file's `nodes` key (BEP 5; w1a S10).
- **Private DHT instances exist.** libp2p's `ProtocolPrefix` gives a separate Kademlia protocol; a pre-shared-key private network (pnet) refuses any node without the key. In go-libp2p the QUIC and WebTransport transports refuse a pre-shared key ("QUIC doesn't support private networks yet", `p2p/transport/quic/transport.go` lines 74 to 76), so a pnet pool runs over TCP or WebSocket (inference). Hivemind starts a new DHT when given no initial peers. iroh has no DHT by default and takes addresses from the application (`MemoryLookup`) (w1a Q1 item 4; S3, S4, S7, S9).
- **NATed nodes are second-class in Kademlia.** The libp2p specification puts NATed laptops in client mode and lets nodes add only server-mode nodes to their routing tables; implementations decide from reachability and can be forced into server mode (w1a S3 to S5).
- mDNS works only on a local network; a rendezvous point must be reachable (w1a S11).
- Public networks read for mechanism only, all class (c): the BitTorrent mainline DHT, the IPFS Amino DHT, n0's DNS and pkarr service, HyperDHT's public bootstrap nodes (w1a S9, S10; w2c N3).

**Inference (from w1a)**

- With 3 to 5 members, a Kademlia DHT degenerates to a full member list (k = 20 or K = 8 exceed N). The real problem is a current, dialable address for at least one member.
- If member i is online with probability p_i and reachable when online with probability q_i, independently, a joining peer finds a usable contact with probability P_join = 1 − ∏(1 − p_i q_i). Four members online half the time and always reachable give 0.9375; if none is reachable, P_join = 0 however often they are online. Independence is optimistic for friends in one time zone.
- R2 already allows a remedy: the owner's published configuration, or a file peers rewrite on a host, can carry last-known addresses, as a torrent's `nodes` key does. libp2p's `BootstrapPeersFunc` and iroh's `MemoryLookup` accept such a list (w1a S4, S9, S10). No source evaluates this for a small, intermittent pool.

**Where sources disagree.** The AutoNAT v1 specification decides "public" after more than 3 peers agree; go-libp2p switches to public after one successful dial-back (w1a S3, S4). With 3 to 5 peers the code's behaviour is what matters (inference).

**Unknown.** Whether any pilot machine has a public IPv4 or IPv6 address that could serve as a bootstrap peer (w1a gaps 1, 2); routing-table persistence in rust-libp2p (not checked; see section 7).

### Q2. Connections through home routers without third-party relays (R3)

**What hole punching achieves, where a primary source measures it**

| Source | Setting | Result | Caveats |
|---|---|---|---|
| Trautwein et al., arXiv 2604.12484 v1, IMC '26 (w1a S1, F) | Public IPFS network; volunteer clients in 39 countries, sample "skewed toward the U.S." (§4.3); **data from 1 Dec 2022 to 1 Jan 2023** | DCUtR hole-punching stage **70% ± 7.1%**, conditional on prerequisites (abstract, §5.2.1); TCP and QUIC both near 70% (§5.2.3); 97.6% of successes on the first attempt (§5.2.3) | About 29% of data points excluded because prerequisites failed (§6); the authors say the unconditional rate "from scratch is necessarily lower" (§6) |
| ProbeLab DCUtR study, May 2026 (w1a S14, D) | Live IPFS network, 25 to 29 May 2026; a cloud prober behind a simulated port-restricted-cone NAT against real peers | Port-restricted cone **82.9%** (3,042 of 3,669); filtering-dependent, mapping unresolved 37.0%; symmetric 39.7% (213 of 536, doubted by the authors); **36%** of NATed peers advertising DCUtR never held a relay reservation | One side is not a real home NAT; 5-day campaign |
| Ford, Srisuresh, Kegel, arXiv cs/0603074 (w1a S2, P) | 380 self-selected NAT Check reports, 2005 | 82% of NATs compatible with UDP punching, 64% with TCP; hairpin 24% (UDP) and 13% (TCP) (§6.2, Table 1) | Device compatibility against test servers, not peer pairs |

- **Carrier-grade NAT (CGN).** CGNs sit in 17% to 18% of non-cellular eyeball networks and over 90% of cellular ones; 11% of non-cellular CGN networks have symmetric mapping as their most permissive type, against under 2% of home routers (Richter et al., IMC 2016, abstract, §5, §6.5; w1a S13, P). 74% of detected NATs drop idle UDP state within 1 minute; the non-cellular CGN median is 35 s (§6.5). In lab tests, peer-to-peer applications failed behind CGN (RFC 7021 §3.1; w1a S12, D).
- **Our own reachable machines can be relays.**
  - libp2p: relay service runs only on hosts judged public, unless forced; peers can be limited to static relays and an ACL can admit only our peer IDs. Defaults allow **2 minutes and 128 KiB per relayed connection** in go and rust (`resources.go` lines 62 to 68; `behaviour.rs` lines 124 to 165), enough for signalling, not for a 0.2 to 0.6 GB update; limits can be lifted (`WithInfiniteLimits`). A relay must itself be directly reachable; relays do not chain (w1a S3, S4, S5, C and D).
  - Hivemind's daemon fork raises the limits to 4 GiB per direction and 30 minutes and uses bootstrap peers as trusted relays (w1a S7, C).
  - iroh: `RelayMode::Custom` points at our relays, and iroh relays **carry all traffic** when punching fails. The documented self-hosted setup uses a DNS name and TLS on ports 80 and 443 (w1a S9, D); a Windows relay binary is published with release v1.3.0 (w2a 7, A; GitHub API, queried 2026-10-13 18:21 TST).
  - Precedent: Psyche, a production network on iroh, defaults to project-named relays and n0 discovery, not volunteers' machines (w1a S15, C).
- **If none of our machines is reachable, no stack read connects two NATed peers.** DCUtR starts from a relayed connection, so with no reachable relay there is no signalling channel. AutoNAT switches its service off on hosts that conclude they are private, so no host starts a relay. Hivemind's only documented all-NAT mode uses the public IPFS network, class (c). iroh with relays disabled uses direct addresses only (w1a Q2). Partial escapes are a UPnP or PMP port mapping on one router, or IPv6, whose firewalls "will still commonly block" unsolicited traffic per Ford et al. §1; neither is measured for home routers today (w1a Q2).
- **Exchange through file hosts alone has precedents** (w2c part 2):

| System | Host | Who writes where | Round clock and counted set | Timings reported |
|---|---|---|---|---|
| Templar, Covenant-72B (w2c T1, C; w1d P4, P) | Cloudflare R2, one bucket per participant | each participant its own bucket | chain block time opens each window; an upload counts if the host's `LastModified` falls within 70 s (`hparams.json` line 50); the leader validator's peer list fixes who counts | 70 s of communication per round of about 20 minutes, data-centre peers (Covenant-72B §4.3) |
| Hivetrain (w2c T7, C) | Hugging Face Hub, one repository per miner | each miner its own repository | central averager every 1,200 s | none |
| flwr-serverless (w2c T2, F and C) | any shared folder, e.g. S3 | one key per node in one folder | none (asynchronous) or wait for all (synchronous) | none; experiments ran as threads on one machine (§5) |
| HF²L (w2c T8, D) | Hugging Face Hub | participants open pull requests; the owner writes `main` | owner's listener waits for enough participants, then merges | none |

- **Can a file host coordinate a hole punch?** STUNMESH-go publishes each node's endpoint, encrypted, through DNS records, OpenDHT or any script-backed store, with "No rendezvous server, no relay"; its example configuration refreshes every minute, and it advises that at least one peer be behind a cone NAT ("For best results"). It learns its own address from a STUN server (Google's public one in its example, class (c)) and reports no success rates (w2c N1, D and C). w2c's decomposition (inference): a file host can carry address exchange and the bulk data itself, but cannot tell a peer its own public address; that needs STUN, a port mapping or IPv6. File-host-coordinated punching between two home NATs is untested anywhere read.

**What this implies for the pilot (inference).** The file host is the only path known to work whatever the homes' NATs are, so it should be the baseline transport and not the fallback the ROADMAP risk table names. Direct connections depend on facts about each home that nobody has measured: public address or CGN, port mapping, NAT class. A reachable machine, if one exists, will be intermittent (the owner's laptop has unreliable mains power), so joins would follow P_join from Q1. A public STUN server would carry no data but is still class (c), so using one is the owner's decision. Arithmetic from w1a: if each of N peers uploads an update of S and downloads the others', each moves S up and (N − 1)S down per round; at N = 5 and S = 0.6 GB that is 2.4 GB down per peer and 12 GB served by the host per round. A relay on a 20 Mbit/s home uplink needs at least 240 s to forward 0.6 GB.

**Where sources disagree.**
- Trautwein et al. cite CGNs using symmetric mapping "in 40% of cases as of 2016"; at the source, 40% applies to cellular CGN networks and 11% to non-cellular ones (w1a S13 correction).
- Ford et al. (2005) found fewer NATs compatible with TCP punching than UDP; the 2022 and 2026 studies found TCP and QUIC similar. Era and method differ (w1a Q2).
- No study gives an unconditional home-to-home rate: Trautwein et al. condition on prerequisites, and ProbeLab shows 36% of capable peers never reach them (w1a Q2).

**Unknown.** Per-pair success among the actual pilot homes; whether Turkish ISPs use CGN; IPv6 reachability of homes today; whether iroh punches holes when its relay runs without a DNS name and certificate (w1a gaps 1 to 7; not confirmed, see section 7); any timing for file-host exchange on home links (w2c gap 1).

### Q3. Membership and the current model

**Who decides, system by system** (w1c Q3a; inference for classifications)

| System | Who admits | Who fixes a round's members | What defines the current model | What is checked |
|---|---|---|---|---|
| Psyche (Solana) | a `join_authority` key, on chain | the coordinator program's `tick`, which anyone may call | every client applies, per batch, the result reaching the witness quorum, from a common checkpoint | payload hash against its ed25519-signed commitment; recomputation is `todo!()` at the commit read (`coordinator.rs` lines 701 to 702) |
| Templar, Covenant-72B | Bittensor registration | the highest-staked validator's peer list | every miner applies the listed peers' compressed updates found in public buckets within a chain-timed window | validator scoring, put window, format, a sync score from 2 values per tensor |
| prime-diloco | not described (INTELLECT-1 paper) | leader process at rank 0 hosts the key-value store | all-reduce over the live group | none described |
| PCCL | accepted peers vote newcomers in | master process | bit-identical shared state | peers submit state hashes; the master finds outliers |
| Agora | singleton Authorizer | DHT matchmaking window, members ordered deterministically | none single: stage replicas averaged periodically | admission checks; signed credentials checked locally |
| OPEN-1B (Gensyn) | not applicable (central training) | not applicable | a chained state hash per step | anyone replays a step and compares bytes |

**Models defined by a rule every peer computes.** Psyche is the clearest case: no stored model in the coordinator; every client starts from the same checkpoint and applies the witness-selected results, and a client that lacks an agreed payload stops with an error (w1c Q3b; w2b B7, C) and would have to rejoin at the next epoch (inference, w2b B7). Templar has the same structure with a leader's peer list and the chain's block time as inputs (w1c S2). PCCL and OPEN-1B supply the checking half: per-peer hashes for bit-identity, and a chained hash any party can reproduce, which needs fixed-order kernels for bitwise equality (w1c S7, S8). w1c separates two properties (inference): "every peer computes the same thing" and "any peer can check it", where checking is either bitwise (published hashes) or within a tolerance (Templar's sync score).

**What the ledgers carry** (w1c Q3c). Psyche: run configuration (changeable only by `main_authority`), join authorizations, the client roster, epoch and step, the random seed (from block time and slot), witness bloom filters, health checks, the checkpoint pointer and reward points. Templar: registrations, each participant's bucket name and read keys, validator weights, and block times used as the round clock. Prime Intellect's protocol (INTELLECT-2): registrations, verifications, invites, contributions and slashing. RL Swarm: peer IDs, round and stage, bootnodes, votes. Every system keeps the model bytes off the ledger (w1c Q7).

**Is a ledger needed for 3 to 5 trusted friends? Function by function (w1c Q3d; inference)**

| Ledger function | Non-ledger carrier allowed by R2 | What is lost |
|---|---|---|
| Membership roster | owner-signed list of public keys in the published configuration; Agora shows peers can check signed credentials locally (w1c S11) | admission without the owner; revocation needs a new signed list |
| Round clock and seed | seed from run seed and round number, as Chorus's assignment already is | a trusted wall clock |
| **Which updates count** | a rule over files present when the round closes, plus an ordered record: conditional commits on one Hub branch (`create_commit(..., parent_commit=...)` "will fail if `revision` does not point to `parent_commit`", `hf_api.py` lines 5035 to 5039; w1c S15) | the record is protected only by members' honesty and host access rules; a writer can skip the check or squash history irreversibly |
| Storage registry | locations in the signed configuration | nothing material |
| Checkpoint pointer | naming convention plus a published hash | Psyche shows the risk of a pointer any member can overwrite (w1c S1) |
| Scores, rewards, slashing | not needed for a trusted pilot | relevant again at Phase 6 |

**What a central server does, and what replacing it costs** (w2c part 1). In BOINC and Flower, most server functions split into a rule (selection, deadlines, merge), a static host (distribution, upload targets) or an occasional peer role (validation, aggregation). BOINC already serves files from "outside servers" by URL and hash and lets uploads go elsewhere (w2c B1, B2 §2.2). The function that does not split is the serialized record of round state: BOINC's daemons "communicate and synchronize through the database" (Anderson, arXiv 1903.01699 §5.1), and Flower holds it in the SuperLink (w2c F1). Plexus replaces Flower's selection and aggregation with a hash rule and a rotating aggregator, but assumes a fully connected overlay and "all nodes remain online" (arXiv 2503.05509 §3.1, §6; w2c F3, P).

**Candidates for the pilot's record of which updates count (inference).**
1. Owner-signed configuration for membership and schedule (all designs).
2. A conditional-commit log on one Hub branch: entries "ready for round t", "update for round t at path, hash", "round t closed with set S". Cost: commits per round against undocumented limits (Q5).
3. A host-timestamp window, as Templar uses R2's `LastModified`: every peer counts files whose server-assigned upload time falls in the round's window. Of the Hub API endpoints read (model repositories and Storage Buckets), only Storage Buckets list a per-file `uploadedAt`; whether the server assigns it is not confirmed (see section 7).
4. A single writer (the owner merges, as in HF²L). The owner's power is unreliable.
5. A ledger, class (c), flagged.

**Where sources disagree.** Psyche's glossary calls checkpointers "Designated, trusted participants", but the program checks only that the signer is a member, and the last pointer received wins (`instance_state.rs` lines 397 to 414; `coordinator.rs` lines 598 to 600). Its documentation lists a verifying task that the code leaves unimplemented (w1c S1).

**Unknown.** No system was found that defines the model by a checkable merge rule with neither a ledger nor a single writer (w1c gaps; w2c gap 5). This is a negative result over the sources read.

### Q4. Averaging without a server

**Two meanings of "asynchronous"** (w1b F1, inference). Some papers mean **no global barrier** (quorum merges, gossip, group all-reduce); others mean **stale updates** (an update computed on an older model is applied to a newer one). Every stale-update method read applies them to **a single global state held by one party**; the only exceptions, Eager Updates and Streaming DiLoCo's overlap, keep an all-reduce and bound the delay to one round or τ steps. Every server-free method avoids a single global state, so peers hold different models between merges.

**Who holds what** (w1b F2)

| Method | Central holder in the algorithm | Could it rotate among peers? |
|---|---|---|
| Synchronous all-reduce DiLoCo; Stage 0 rounds | none; a missing peer blocks the round or forces a restart (Factored Gossip §5.2) | not needed |
| Moshpit, DeDLOC, SWARM group all-reduce | none; DHT for matchmaking | not needed |
| D-PSGD, AD-PSGD, NoLoCo, Factored Gossip LocalM1M2, GASLoC | none; pairs or a graph | not needed |
| Async Local-SGD (arXiv 2401.09135 v2) | "a central server" holds model, outer momentum and buffer (§3) | not described |
| Decoupled DiLoCo (arXiv 2604.21428 v1) | a syncer holds global fragments and outer optimizer state (§4) | **not described** |
| HeLoCo, HALoS | a synchronizer; local and global parameter servers | not described |
| FoMoE | central coordinator, synchronous rounds (via note 04a) | not described |

**Decoupled DiLoCo's syncer, specifically** (w1b S1, P). The paper runs it "on CPU-only resources, partitioned into M shards", says the design "naturally leads to a parameter server architecture", and argues for "highly stable, CPU-only resources with a minimal failure surface" (§4). Its only syncer-failure path is restart from a Chandy-Lamport checkpoint (App. E.2). Learners, by contrast, recover by copying parameters and optimizer state from a peer learner (App. E.3), and the syncer's "event tape" makes its timing-dependent merges replayable bit for bit (App. E.1). Nothing in the algorithm requires the syncer to be a separate machine (inference). A rotating syncer would need a hand-over of about two model copies (0.8 to 2.4 GB in fp32 for 100M to 300M parameters, inference), agreement on the next holder, and a rule for updates in flight; no paper read describes or tests it (w1b F2). It would also hold the canonical model on one machine during its turn, against ROADMAP principle 6, unless it published every merge (inference).

**Quality cost, from parts read** (w1b F3; gaps in loss or log-perplexity are w1b's arithmetic, inference)

| Method (locator) | Setting | Against synchronous local averaging | Against centralized or data parallel |
|---|---|---|---|
| Async Local-SGD, naive (Table 3, v2) | 20M / 60M / 150M, 4 workers, H = 50, continued from a 24,000-step checkpoint | +1.83% / +1.36% / +1.69% | not given |
| Async Local-SGD, Delayed Nesterov + Dynamic Local Updates (Tables 1 to 3) | same; 4 to 16 workers | −0.14% / −0.03% / +0.06% | −0.86% / −0.34% / −0.42% against a single worker at 4× batch |
| Same algorithm reimplemented in HALoS (arXiv 2506.04531 Table 1) | Pythia 160M from scratch, 16 workers | 24.8% more tokens than DiLoCo to the same loss at 160M from scratch (inference: 16.1B / 12.9B); the 70M and 410M columns' protocol is not confirmed (section 7) | not used here (section 7) |
| Decoupled DiLoCo, quorum K = 1 with grace window, against fully blocking K = 8 (Table 5) | 2B dense, 8 learners, heterogeneous TPUs | text average 55.3 against 54.4; vision 37.0 against 37.6; without the grace window 51.4 and 25.7 | downstream parity with data parallel at 2B to 9B and MoE, e.g. 2B 54.4 against 55.1 (Table 12) |
| HeLoCo (arXiv 2606.00271 Table 1) | 15M, 5 workers, far from converged (inference: losses near 6.5) | −1.8% with no staleness; +15.4% with severe staleness | not given |
| Eager Updates, one-round-delayed merge (arXiv 2502.12996 Table 2) | 500M, 2 replicas, H = 30 | eager +0.75%; naive delay +12.7% (+2.2% with lowered outer learning rate) | 1B against data parallel: +0.75% / +0.40% / +0.41% at 25B / 100B / 250B tokens (Table 1) |
| Streaming DiLoCo overlap (arXiv 2501.18512 §3.3.2) | 500M (the paper's ablation model, §3.3) | under 0.2% up to an overlap of 10 inner steps | n/a |
| Factored Gossip, pure pairwise gossip LocalM1M2 (arXiv 2606.22768 Table 1) | 1.5B, 8 workers, 10B tokens | +1.29% | +3.49% (+2.37% at 30B tokens); +8.99% at 16 workers |
| GASLoC 2-Peer / 1-Peer (arXiv 2606.11081 Tables 1b, 3) | 134M at 8 / 16 / 32 replicas | +0.61 / +1.47 / +2.55% and +1.21 / +2.65 / +3.68% | DiLoCo itself +3.77 / +6.92 / +11.01% against DDP |
| NoLoCo (arXiv 2506.10911 Table 1) | 125M to 6.8B, with pipeline routing | −1.45% to +0.42% | +0.83% to +7.68% against FSDP |
| Moshpit SGD, DeDLOC (§4.3; App. I.6) | ALBERT-large, preemptible and volunteer peers | not measured | final loss "the same within the margin of error"; curves "virtually identical" (figures only) |
| FoMoE, 2 holders of 4 (Table 6, v2) | 54M MoE, synchronous | +1.6% / +2.9% / +2.1% against full replica at K = 32 / 64 / 128 (note 06, via w1b S17); 1 holder +3.4% / +4.8% / +5.3% (note 04a) | no number |

The reference cost is synchronous local averaging itself: tuned DiLoCo-family gaps against data parallel of +0.3% to +3.9% at 4 to 8 workers, and Stage 0's +6.1% with plain averaging (w1b F3, from note 01 A2; Stage 0 report §3.1).

**Communication cost** (w1b F4). An all-reduce sends about 2(N − 1)/N × S per peer per round (w1b's statement of the standard ring cost); at N = 4 and S = 0.2 to 0.6 GB, about 0.3 to 0.9 GB each way, or 120 to 360 s at a 20 Mbit/s uplink (inference). A syncer on one home peer would move about N × S each way per round (inference), the hotspot D-PSGD's Table 1 describes. Pairwise gossip moves the same bytes as DiLoCo ("essentially the same", NoLoCo App. C); its gain is no global barrier. Decoupled DiLoCo's int4 outer gradients cost +0.09% in relative validation loss, 2 bits +32%, 1 bit +83% (Table 10).

**Precedents for averaging an expert within its holders** (w1b F6). FoMoE averages experts and their router rows "within expert replica groups" and the dense part over all workers (w1b S17, from notes 04a, 04b, 06): the direct precedent, synchronous, with a central coordinator, on a 54M proxy. DiPaCo averages each module over the paths through it, with a square-root rescaling (note 04b block 4). SWARM all-reduces gradients within each pipeline stage's peers, synchronously (w1b S5). Learning@home is the counter-example: one holder per expert, no averaging (note 04b block 7; w1b S16). **Not found in this search:** any asynchronous or gossip variant of holder-group averaging, or any study of a holder dropping out of its group.

**Where sources disagree** (w1b F3).
- Async Local-SGD's parity with synchronous DiLoCo (fine-tuning, 4 to 16 workers) against HALoS's finding that the same algorithm needs 24.8% more tokens than DiLoCo at 160M from scratch (inference: 16.1B / 12.9B; the 70M and 410M columns' protocol is not confirmed, see section 7).
- NoLoCo better than DiLoCo against Factored Gossip's reimplementation without pipeline routing, which "diverged after approximately 5k steps" with DiLoCo's settings and reached 22.65 against DiLoCo's 18.65 with its own (App. B.1).
- Streaming DiLoCo's overlap "negligible" up to 10 steps against divergence of a 5-step overlap in Factored Gossip's setting (App. B.2).
- A synchronous DiLoCo pretraining gap that became a large post-training gap at 550M (nanochat-DiLoCo: SFT ChatCORE 0.1190 against 0.0157, arXiv 2511.13761 Table 1) against post-training parity at 5B (Decoupled DiLoCo App. B, which names the former as contrary).
- AD-PSGD's epoch-wise parity with all-reduce against lower accuracy in Moshpit's heterogeneous runs.

**Unknown.** A rotating synchronizer; any method with 3 to 5 peers and real departures at 100M to 300M; quality at equal wall-clock on home links (w1b gaps).

### Q5. Checkpoints when no peer holds the whole model; host limits

**What the sources show** (w1d Q5b)

- **Every system read keeps at least one complete copy somewhere.** Psyche's clients all hold the full model; Hivemind and DeDLOC peers download full state from a peer; INTELLECT-1 moved full model and optimizer state peer to peer in "30-60 minutes" for 10B; Templar stores full checkpoints in a validator's bucket; Petals' full copy lives on the Hub. No source stores a training checkpoint only as pieces held by different peers.
- **Partial retrieval from a full public copy:** Petals servers download only the shard files holding their blocks, through `model.safetensors.index.json` (w1d S5, C); Psyche's joiners fetch the model layer by layer from different peers (w1d S2, D).
- **Atomicity by a marker written last:** Psyche's GCS `manifest.json` acts as "an atomic marker" because listings can show half an upload; Templar writes `_LATEST.json` after its shards; flwr-serverless writes a `.success` flag after each object (w1d S2; w2c T1, T2).
- **Content addressing:** the Hub's Xet backend stores about 64 KB content-defined chunks in 64 MB blocks keyed by hash; Git LFS pointers carry SHA-256; BitTorrent v2 gives each file a SHA-256 Merkle root; INTELLECT-2's SHARDCAST checks the SHA-256 of an assembled checkpoint (w1d H3, H9, P12).
- **Plain distribution without a seed of ours (inference, w1d H9):** a torrent whose web seeds are a public host (BEP 19) needs no always-on seed, but peer discovery still needs a tracker on our machines or the public DHT (c). Whether Hub or GitHub URLs work as web seeds is not confirmed (section 7). IPFS persists content only while "pinned" on an online node: our own always-on node (a) or a paid pinning service (w1d H11).

**Limits of the hosts a pilot would use (read 2026-10-13; w1d Q5a)**

| Host | Size | Rate and quota | Terms that bear on frequent uploads | Class |
|---|---|---|---|---|
| Hugging Face Hub repositories (H1, H2, H4, H5) | 500 GB per file hard, under 200 GB recommended; no per-repository limit; under 100,000 files, under 10,000 per folder; commits under 100 files recommended; HTTP push times out at 60 s | free public storage "Best-effort"; downloads 5,000 per 5 minutes for a free user, 3,000 per IP anonymous ("September '25" table, "subject to change"); **commit limits exist but are not documented**; "a few thousand commits" degrade a repository, which "is not meant to work as a database"; `CommitScheduler` advises at least 5 minutes between commits | "excessive bulk activity" and "excessive or irrelevant data" count as abuse; accounts can be suspended "with or without cause" | (b) |
| Hub Storage Buckets (H1) | as above for quota; repository recommendations do not apply | "non-versioned and mutable", intended for "training checkpoints, logs, intermediate artifacts"; free allowance not quantified; a change-event stream endpoint | same | (b); event stream borderline, flagged |
| GitHub releases (H6 to H8) | 1,000 assets per release; each under 2 GiB on free accounts | no limit on total size "nor bandwidth usage"; API: 5,000 requests per hour, 80 content-creating requests per minute and 500 per hour | "significantly excessive" bandwidth may be throttled; "excessive automated bulk activity" prohibited; one free machine account allowed | (b) |
| GitHub Git LFS (H6) | 2 GB per file on Free and Pro | 10 GiB storage and 10 GiB download bandwidth per month free, then blocked without payment | as above | (b) |
| Cloudflare R2 (H12) | 4.995 TiB per object | free per month: 10 GB-month, 1 million writes, 10 million reads; egress free; 1 write per second per key | needs "an R2 subscription" through a checkout | (b), but an R2 subscription the owner may end up paying for (free tier exists; whether checkout needs a payment card is not confirmed, section 7): flag against R1 |
| BitTorrent (H9) | none in the protocol | none; needs a tracker (a, or a role on our peers) or the public DHT (c); BEP 19 web seeds can be (b) | not applicable | mixed |
| IPFS (H11) | none in the protocol | persistence needs a pinned, online node: our own always-on node (a) or a paid pinning service; discovery through the public Amino DHT (c) | pinning services' own terms (not read) | (a) or (c) |

Arithmetic (inference, w1d): Git LFS's free 10 GiB of monthly bandwidth covers about 17 downloads of a 0.6 GB checkpoint; R2's free 10 GB-month holds about 16 copies of 0.6 GB. At 5 peers, one update commit each plus one log commit per round, and 30-minute rounds, a repository would take about 288 commits a day and reach "a few thousand" within one to two weeks (inference; this report's arithmetic). Storage Buckets avoid commit history but their free allowance is not quantified.

**Where sources disagree.** GitHub's releases page says each asset must be under 2 GiB; its large-files page says under the plan's Git LFS limit; they agree for free accounts and differ for paid plans (w1d H6).

**Unknown.** Hub commit limits; how much free public storage is "Best-effort"; whether Hub or GitHub URLs work as BitTorrent web seeds; whether a multi-file Hub commit becomes visible at once; Xet deduplication savings on successive training updates (w1d gaps). See section 7.

### Q6. Churn: leaving mid-round, stragglers, timeouts, lost holders

**When a groupmate fails during averaging, the code read shows three behaviours** (w2b F1)

| Behaviour | Systems | What survivors end up with |
|---|---|---|
| Partial round: a failed sender is excluded from parts it had not sent; a failed reducer's slice stays local | Hivemind (`partition.py` lines 128 to 136, 248 to 255); Agora, whose all-reduce appears to derive from Hivemind's (inference from its code) | some parts averaged over everyone, some over fewer, some not at all |
| All or nothing, then retry: the collective aborts and restores every buffer | PCCL (§4.1, v1); prime-diloco rebuilds the group and retries up to 3 times (`diloco.py` lines 92 to 121) | a complete average over the rest, or no change |
| Skip: the failed member's contribution is dropped, identically everywhere | Moshpit (absent peers keep their own values); Psyche (a batch without witness consensus is skipped by every client) | the survivors' average, or a smaller effective batch |

- **When averaging fails outright, every training loop read falls back to the peer's own update** and does not block: "Proceeding with local gradients" (Hivemind Optimizer), "using local updates only" (Moshpit's ALBERT loop), "Resorting to calculating pseudo-gradient without reduce" (prime-diloco), "Skipped averaging" (SWARM) (w2b F1).
- **Psyche is the exception:** a client lacking an agreed payload errors out of its loop (code) and, by inference, must rejoin at the next epoch, which keeps every model identical at the cost of the client (w2b B7, C).
- **Every tolerant system time-boxes the round** (w2b F2): Hivemind matchmaking 15 s and averaging timeout 60 s; DeDLOC waits 5 s for stragglers and gives up after 30 s; Agora uses a 40 s matchmaking window and 30 s / 60 s sender and reducer timeouts, and a worker that fails 2 of its last 3 rounds terminates itself; Psyche's repository configuration for its 40B run sets a 360 s training phase and 5 s witness phase (`config/consilience/state.toml`; whether the live run used them is unconfirmed, section 7); prime-diloco evicts a node after 10 s without heartbeat by default. One place can wait indefinitely: prime-diloco's non-leaders waiting for a dead leader ("TODO: Have a timeout here in case the leader is dead", `comms.py` lines 407 to 414; w2b B9). NoLoCo's blocking pair exchange sets no timeout of its own; by inference it waits until torch.distributed's default timeout and then raises (value and behaviour not checked; see section 7) (w2b B10).
- **Coordinator loss is handled by restart, not hand-over, in the three systems read (inference):** PCCL's documentation says "Master Crash = End of Run"; prime-diloco's leader death blocks the rest; Decoupled DiLoCo's syncer restarts from a checkpoint (w2b F3).
- **When the only holder of a part disappears** (w2b F4): a Hivemind MoE expert becomes unavailable until its server returns, with weights only on that server's disk; a Petals block can be refilled because weights are on the Hub; a SWARM stage stalls the pipeline, its state surviving only "on all active nodes" of the stage; Bamboo rolls back to a checkpoint when both holders are lost; Oobleck loses model state if every replica of a stage goes; PCCL's shared state is "effectively lost" when its last distributor leaves; a Psyche batch's update is skipped.
- **Deliberate multiple holders** (w2b F5): Petals, SWARM and Agora keep several holders per part for throughput or coverage; Bamboo keeps exactly 2 per stage, placed in different zones; Oobleck keeps f + 1 replicas to survive f simultaneous failures. **No volunteer system read enforces a minimum holder count without nodes its operator runs** (inference over the systems read): Agora's floor is its own fleet (4 Pluralis nodes per body stage, 8 and 16 on head and tail; arXiv 2607.13332 §5.1), and Bamboo and Oobleck rely on a cluster manager.
- **Measured effects** (w2b F6). Agora's ablation at 1B with 16 workers per stage found convergence slowed while averaging failures were frequent and recovered after failing workers were pruned, with loss going "from roughly 3.04 to 2.97" (§6.4); its 8B run absorbed 669 joins and 607 departures (§5.3.2). Throughput-only results: Bamboo's checkpoint-and-restart wasted 77% of training time on 64 spot instances, and Bamboo reports 3.7× its throughput (§3, abstract); Oobleck reports up to 29.6× over Bamboo and Varuna.
- **Two reasons for several holders lead to different rules** (w2b F9, inference): keeping a part available (Petals, SWARM, Agora), or not losing its state (Bamboo, Oobleck). A Chorus expert's training state between checkpoints exists only on its holders, so the second applies: R5's 2 holders is Oobleck's f = 1 case. If the merged model is published every round, losing both holders costs one round of that expert's training, not the expert. Two holders in one household are likely to fail together, which Bamboo avoids by placing holders in different zones (inference by analogy).

**Where sources disagree.**
- Learning@home's paper says a runtime "regularly saves latest expert weights into the same DHT" (§3.3), and w1b S16 relays that; Hivemind's code at `4bd43b7` saves expert weights to local disk and stores only UID-to-peer records in the DHT (w2b B1, B2). This report follows the code for current Hivemind.
- Hivemind accepts partially averaged rounds; PCCL aborts and restores a failed collective (§4.1) and credits fault tolerance to restricting legal state transitions (§2.5.3); this report reads that as excluding partial rounds (inference). No source compares the two on one task (w2b F1).
- SWARM's paper reports cross-stage rebalancing; its repository README says rebalancing is "not yet added" (w2b B6).
- NoLoCo's paper describes a shared seed for routing; its code seeds routing and outer-step pairing with the step counter (w2b B10).

**Unknown.** The quality effect of a 2-holder group dropping to 1 or 0 under any rule; holder-group averaging under churn (w2b "Unknown"; w1b gaps).

### Q7. Write access and trust (R7)

**The four options compared** (w1c Q7; consequences are inference)

| Option | Exemplars read | Participant is trusted with | Honest mistake | Malicious participant | Stays central |
|---|---|---|---|---|---|
| 1. Per-participant tokens to one shared repository | Psyche checkpointers' own Hub tokens; Hub organisation `write` role; GitHub fine-grained tokens | not overwriting others: a Hub `write` member can "create, delete, or rename any repo" in the organisation; GitHub tokens are scoped to repositories, not paths, in the parts read | overwrites another's update or the checkpoint; a leaked token lets anyone write meanwhile | replaces checkpoints, erases history (`super_squash_history` is "non-revertible"), uploads pickled weights that run code on load | the host (b); the owner as organisation admin |
| 2. Signed per-peer storage | Templar's per-participant R2 buckets; the Hub's free `contributor` role (write only to repositories the user created); Hivemind's owner-signed DHT records | its own outputs only | a bad or late upload affects only its own contribution | a well-formed but poisoned update is still merged unless checked | a registry of locations (on chain in Templar; a signed configuration for us) |
| 3. Peer-to-peer only | Psyche's peer exchange; PCCL; Hivemind's expiring records; INTELLECT-1's peer checkpoint transfer | serving its state correctly | state is unavailable when all holders are off; DHT records expire | serves wrong data; signed hashes catch it | every exemplar still had a coordinator or master |
| 4. A ledger | Psyche (Solana), Templar (Bittensor), Prime Intellect's protocol, RL Swarm | correct transactions | permanent but visible; in Psyche any epoch member can repoint the checkpoint | bounded by program rules, but the chain cannot see off-chain content | the chain (c), plus off-chain storage |

- **Content checks are separate from write access** in every exemplar: hash against a signed commitment, loss scoring, recomputation, bitwise replay (w1c Q7).
- **The file format is part of the write-access question.** Pickled files turn write access into code execution for every reader: Gensyn warns "Checkpoint directories are code, not data." (w1c S8). Among storage-only systems, Hivetrain loads others' files with `torch.load` without `weights_only`, flwr-serverless stores pickles, and Templar writes `.pt` files but reads them with `weights_only=True` (w2c T1, T2, T7).
- **Signed upload URLs** (INTELLECT-2) limit what a participant can write but need a live issuer, class (a) (w1c S6).
- **Per-participant limits on the hosts:** the Hub's `contributor` role and per-participant buckets confine each friend's writes to their own space; GitHub rulesets can block force pushes and require signed commits, and organisation-wide rulesets need a paid plan (Team and Enterprise per `about-rulesets.md` line 17; line 23 of the same page names only the Enterprise plan for organisation-level rulesets) (w1c S13, S14).

**Unknown.** Whether a Hub fine-grained token can limit writes to one repository; GitHub per-path write limits (section 7).

### Q8. Code trust: genuine code, work units as data

- **Key-based signing (BOINC):** a project key pair; every application file is signed, ideally on "a separate computer" kept "disconnected from the network"; clients verify each file; a new key is accepted because each old key signs it; applications run under a separate account (w1d T1, D). This needs no third-party service.
- **Identity-based signing (Sigstore, GitHub artifact attestations, PyPI attestations):** a CI identity gets a short-lived certificate and signatures are logged in Rekor. Offline verification works with a downloaded bundle and trusted root, but then "will not know if key material has been revoked". GitHub states attestations are "not a guarantee that an artifact is secure" (w1d T2 to T4, D).
- **What the candidates do:** Hivemind 1.1.12's manylinux x86_64 wheel and sdist (2 of its 5 files; the rest not queried) carry a publish attestation from its `release.yml` workflow (PyPI Integrity API, queried 2026-10-13 17:42); Petals 2.2.0.post1's wheel has none (sdist not queried); Psyche pins its client Docker image by `sha256` digest in the run's on-chain account; Templar installs by `git clone` (w1d T4, T5). Whether Psyche's run-manager verifies an image signature is not confirmed (section 7).
- **Reproducible builds** mean bit-for-bit identical artifacts from the same source, environment and instructions; no candidate's documentation read claims them (w1d T6).
- **Work units and updates as data:** safetensors is designed so that a downloaded file cannot run code; its header is capped at 100 MB, and tensor values are not checked, so NaN and Inf can arrive. `torch.load` defaults to `weights_only=True` since PyTorch 2.6, which "narrows" the attack surface. The Hub scans pickles. Psyche's checkpoint download also fetches `.py` configuration files (w1d T7, S2). BOINC's work units are XML templates listing input files, optionally with MD5 checksums (w2c B1).
- **Inference (w1d):** R2's "code-signing key" matches BOINC's pattern more directly than keyless signing, which would add an online identity provider and Sigstore's public instance to the trust chain (flagged, not classified). Principle 2 (work units are data) has direct support in these formats, provided the client never unpickles or executes fetched files and checks values before merging.

### Q9. The systems themselves

**Maintenance, licence and platform** (w2a; all GitHub fields queried **2026-10-13 between 17:55 and 18:21 TST**: licence `license.spdx_id`, last commit `commit.committer.date` of the newest default-branch commit, latest release `releases/latest.tag_name` and `published_at`)

| System | Language and runtime | Licence | Last commit | Latest release | Windows | Documentation | Provides toward Chorus |
|---|---|---|---|---|---|---|---|
| Hivemind | Python (`requires-python >=3.9`), PyTorch; Go `p2pd` child process | MIT | 2026-01-04 | 1.1.12 (2026-01-03) | not native: WSL "experimental"; no Windows wheel; `setup.py` stops on Windows | README, Read the Docs | private DHT, connections and relays, group averaging, state transfer; no storage or client |
| Hivemind `p2pd` fork | Go, built on go-libp2p v0.32.1 | NOASSERTION (MIT and Apache files) | 2023-11-21 | v0.5.0.hivemind1 (2023-11-21) | not built for Windows | README | Hivemind's transport |
| Petals | Python; pins a 2024-07-15 Hivemind commit | MIT | 2024-08-25 | v2.2.0 (2023-09-06) | WSL only | README, wiki | inference swarm; partial download from the Hub |
| go-libp2p | Go 1.26 | MIT | 2026-09-21 | v0.50.0 (2026-09-21) | tested in CI | README, `libp2p/specs` | discovery, NAT traversal, relays, pnet over TCP or WebSocket (inference) |
| rust-libp2p | Rust | MIT | 2026-10-13 | v0.57.0 (2026-09-11) | compile check only | README | as go-libp2p; whether its pnet runs over QUIC is not checked (section 7) |
| py-libp2p | Python 3.10 or later | NOASSERTION (MIT and Apache) | 2026-10-02 | v0.8.0 (2026-09-26); PyPI classifier "Beta" | Windows CI without interop tests | README, Read the Docs | as go-libp2p, by its own claims (section 7) |
| js-libp2p | TypeScript, Node.js | Apache-2.0 | 2026-10-11 | npm 3.3.12 (2026-10-10) | tested in CI | README | as go-libp2p in kind (inference; mechanisms not read, section 7); ProbeLab calls its DCUtR experimental (w1a S14) |
| iroh | Rust | Apache-2.0 (crates: MIT OR Apache-2.0) | 2026-10-09 | v1.3.0 (2026-09-28) | tested in CI; Windows relay binary | docs.iroh.computer | QUIC, hole punching, relays carrying data, address lookup |
| iroh-ffi (Python bindings) | Rust with Python wheels | Apache-2.0 | 2026-07-28 | v1.1.0 (2026-07-16); PyPI classifier "Alpha"; `win_amd64` wheel | wheel published | README | Python access to iroh, trailing the core (1.1.0 against 1.3.0) |
| Psyche (`nousnet`) | Rust 77.7%, TypeScript, Python; Docker | Apache-2.0 | 2026-03-20 | v0.2.0 (2026-01-21) | none: "only runs on modern Linux distributions" | in-repo book | full stack for data-parallel full copies on Solana and iroh |
| prime-diloco | Python, C++ kernel; `torch==2.5.1` | Apache-2.0 | 2025-04-10 | v0.5 (2024-10-24) | none stated | README, report | synchronous DiLoCo with an elastic process group |
| PCCL | C++20 with Python bindings | MIT | 2025-09-12 | release/v1.0.0 (2025-05-21) | claimed; Windows wheels without CUDA, only as release assets | README, `docs/` | fault-tolerant all-reduce, state hashing; needs a master |
| Templar | Python 3.11 or later | MIT | 2026-10-04 (test file only) | v2.1.28 (2026-01-21) | not stated; CI Ubuntu only | README, `docs/` | Bittensor-coordinated full copies; **dormant** notice added 2026-03-31 (commit `142666f0dd91`) |
| RL Swarm | Python, TypeScript | MIT | 2026-01-05 | v0.7.0 (2025-11-12) | WSL, "not very well tested" | README | RL rollout sharing; "no official swarms running right now" |
| GenRL | Python | null (no licence found) | 2025-11-12 | v0.3.0 (2025-11-12) | not stated | README | RL framework with a Hivemind backend |
| Node0 | Python 3.11 only | Apache-2.0 | 2025-09-23 | none | Linux; WSL2 | README | event client for Pluralis pipeline training |
| Agora | Python 3.11 only | Apache-2.0 | 2026-07-04 | none | Linux; WSL2 | README, `docs/` | pipeline training library; run concluded 2026-07-04 |
| Flower (contrast) | Python | Apache-2.0 | 2026-10-13 | framework-1.39.0 (2026-09-28) | pure wheel; classifiers macOS and Linux | full docs | server-based federated learning, class (a) |
| BOINC (contrast) | C++, PHP | LGPL-3.0 | 2026-10-12 | server_release/1.6/1.6.2 (2026-06-12) | Windows builds in CI | wiki | server-based volunteer computing, class (a) |

Research code and storage-only systems (GitHub API, `license.spdx_id` and `pushed_at`): moshpit-sgd Apache-2.0, 2025-02-04; DeDLOC Apache-2.0, 2022-01-13; swarm no licence, 2023-12-11; noloco MIT, 2026-03-26; HALoS no licence, 2025-06-05 (all queried 2026-10-13 17:36 TST, w1b); flwr-serverless null, 2026-02-25 (18:29 TST); Hivetrain null, 2024-05-30 (18:32 TST); HF²L null, 2026-10-13, created 2026-09-03 (18:33 TST); STUNMESH-go LGPL-3.0, latest release v1.15.1 on 2026-09-07 (18:35 TST) (w2c).

**Corrections to earlier records** (w2a "Corrections"; w1c S5; w1d S3).
- The 2026-10-07 survey's "barely maintained" for Hivemind is **confirmed**: latest release 1.1.12 on 2026-01-03, newest commit 2026-01-04, the three newest commits (2025-08-03 to 2026-01-04) packaging, build and import changes, 70 open issues and 24 open pull requests (search `total_count`). Added: no Windows wheel (PyPI, queried 2026-10-13 18:05 TST), and its `p2pd` fork has had no commit since 2023-11-21.
- `PrimeIntellect-ai/prime`, listed in `docs/prior-work.md` and note 01 A5 as INTELLECT-1's framework, is now Prime Intellect's CLI and SDK; the framework is `PrimeIntellect-ai/prime-diloco`, with no default-branch commit in 18 months (section 7 for the identity caveat). OpenDiLoCo's README says it "is no longer maintained" and links to the CLI repository.
- Templar's dormant notice is dated: added on 2026-03-31; the only later commit changes a test file.
- `PsycheFoundation/psyche` now redirects to `PsycheFoundation/nousnet`.

**Does Prime Intellect's framework need a central orchestrator?** Yes: prime-diloco's membership lives in a master key-value store hosted by the rank-0 process (w1c S5), and INTELLECT-2's paper says "The orchestrator and discovery service are currently centralized" (§2.4.3; w1c S6).

**Inference for D35** (section 4.6). No existing training system meets R1, R2 and R3 together, supports sliced work units, and is maintained with native Windows support. The healthy projects are the networking libraries, which provide transport only.

**Where sources disagree.** Agora's run length: 40 days in the paper's abstract (w1c S11) against "500B tokens over 7 weeks" in its README banner (w2a 13). Unresolved; neither figure is used.

### Q10. Bandwidth, update sizes and compression

**What the sources report** (w1d Q10; every measured setting is a data centre or rented cloud machines, except Training Transformers Together, a volunteer run whose hardware and links the paper does not state, and Covenant-72B, whose permissionless peers each ran at least 8 B200 GPUs over commodity internet links, §3)

| Source | Model | What is sent | Size or ratio | Quality effect reported |
|---|---|---|---|---|
| SparseLoCo, arXiv 2508.15706 v3 Table 1 | 512M, 8 workers, H = 15 | top-k 3.12% plus 2-bit values plus error feedback | 17.21 MB against 512.40 MB for 8-bit DiLoCo | loss 2.70 against DiLoCo 2.76 and AdamW DDP 2.69; 1 bit fails (4.79, Table 7) |
| Decoupled DiLoCo, Table 10 | 2B | int4 outer gradients | n/a | +0.09% relative validation loss; 2 bits +32%; 1 bit +83% |
| Streaming DiLoCo, Table 1 | 1B, H = 100 | FP4 (E3M0) outer gradients, streamed | 1.10 TB against 441 TB for data parallel over 25B tokens | "no sign of performance regression" from FP4 (§2.4) |
| MuLoCo, arXiv 2505.23725 v3 §6.3 | 416M, 8 workers, H = 30 | quantized or top-k | 8, 4, 2 bits | 4-bit lossless; 2-bit fine with statistical quantization (figures only) |
| OpenDiLoCo, arXiv 2407.07852 §3 | 150M, 1.1B | FP16 pseudo-gradients | half of FP32; 1.1B all-reduce averaged 300 s over 127 to 935 Mbit/s links | "no noticeable impact" (figure only) |
| INTELLECT-1, arXiv 2412.01152 §2.2, Table 2 | 10B | int8 every 100 steps | 4× against FP32; median all-reduce 103 s to 469 s | no ablation found |
| DiLoCo, arXiv 2311.08105 v3 Table 6 | 150M, 8 workers, H = 500 | sign-pruned outer gradients | 25% / 50% / 75% pruned | perplexity −0.06% / +0.39% / +1.66% |
| DeMo, arXiv 2411.19870 v2 Table 1 | 300M, 1B | top-k DCT momentum every step | 300M: 7.49 MB per step at k = 8 against 636.9 MB | downstream equal or better at 100B tokens |
| DisTrO report (2024) | 1.2B | not described | 86.8 MB received per step against 74.4 GB (857×) | says "the 1.2B model seems to be the smallest size" that works consistently; 300M models "do not converge as well" |
| Training Transformers Together, arXiv 2207.03481 §3.3 | 1.1B with tied weights, volunteers | 8-bit large tensors, 16-bit others | not stated | none reported |
| Covenant-72B §4.1, §4.3 | 72B | SparseLoCo, 2-bit | "more than 146×" against dense | none isolated; 70 s communication per round |

- **Home connections:** no source measured any of these schemes over home links or with consumer GPUs. The only home speeds in the sources are an assertion of 10 to 100 Mbit/s for typical connections (Training Transformers Together §2, paraphrased) and an assumed 100 Mbit/s down and 10 up (DisTrO report §3.1) (w1d Q10).
- **Arithmetic (inference, w1d):** a full update for 100M to 300M parameters is 0.2 to 0.6 GB in fp16, 0.1 to 0.3 GB in int8, 0.05 to 0.15 GB at 4 bits. At an assumed 20 Mbit/s uplink, 0.6 GB takes 240 s, 0.3 GB 120 s, 0.15 GB 60 s. SparseLoCo's 17.21 MB scaled linearly to 300M is about 10 MB, about 4 s. In an all-to-all exchange through a host each of 5 peers also downloads 4 updates.

**Where sources disagree.** Dropping values is worse than lowering precision in Streaming DiLoCo and MuLoCo, but works in SparseLoCo with error feedback and in DeMo through a DCT; the results agree once the surrounding method is specified. 2-bit quantization is fine when statistical and poor when linear. The 2024 DisTrO report says 300M models do not converge as well, while DeMo v2 (2026) reports 300M results; the DisTrO README calls DeMo the "seed research/idea", so they may not be the same algorithm. INTELLECT-1 states averages of about 2 and 10 minutes against medians of 103 s and 469 s in its Table 2 (w1d Q10).

**Unknown.** Compression at 100M to 300M with 3 to 5 workers and plain averaging; compression with per-expert holder averaging (w1d unknowns).

---

## 4. Design options for Chorus

**Everything in this section is inference** built on the findings above. Labels like "(w1c S15)" mark the evidence a design element leans on, not evidence that the design works.

### 4.0 The decision the evidence forces: what "asynchronous" can mean with no server (inference)

| Merge timing | Server-free? | One shared model? | Evidence | What it gives up |
|---|---|---|---|---|
| One central holder merges updates as they arrive (Async Local-SGD and HeLoCo apply stale updates; Decoupled DiLoCo merges a quorum at its syncer and, by its own statement, applies no stale gradient, App. A) | no: (a) | yes, on the holder | the most churn evidence (Decoupled DiLoCo: simulated failures at 2B to 5B dense and a 2.8B-active MoE) | R1 |
| Same, with the holder rotating among peers | yes, in principle | yes, but on one machine at a time, against principle 6 unless every merge is published | **none: untested anywhere read** | a hand-over of about 0.8 to 2.4 GB per rotation; agreement on the next holder; a rule for updates in flight |
| **Deadline-quorum group averaging**: merge whoever posted by the deadline; late work is dropped and the late peer adopts the new model | yes | yes: every peer computes the same merge from the same counted set | Decoupled DiLoCo's K = 1 quorum with a grace window matched its fully blocking run (Table 5, with a syncer); Psyche and Templar close rounds on timers; DeDLOC and Moshpit ran group all-reduce through real churn | late work; needs the agreed counted set; synchronous within each round (the R4 reading in the header) |
| Pairwise or sparse gossip (NoLoCo, GASLoC, Factored Gossip LocalM1M2) | yes | no: peers differ between merges | +1.29% against DiLoCo at 1.5B, 8 workers; GASLoC +0.6% to +3.7% at 134M; no training run through departures | principle 6; NoLoCo's stability disputed |
| One-round-delayed eager merge | yes | no: each peer substitutes its own fresh update | +0.75% at 500M, 2 replicas | principle 6; whether the benefit shrinks with more peers is open |
| Naive one-round delay | yes | yes | +12.7% (+2.2% with a lowered outer learning rate) at 500M | quality |

**The owner's decision.** Under R1 the asynchronous branch of R4 is closed, unless the owner accepts an untested rotating holder that also strains principle 6. The group branch is open through deadline-quorum averaging, which keeps a single shared model. Gossip is open if the owner gives up the single shared model. The options below assume deadline-quorum rounds and note where gossip would change them.

### 4.1 Option A: bulletin board on public file hosts (inference)

**Peer roles**

| Role | Who | Does |
|---|---|---|
| Trainer | every peer | downloads the round's model (or its slice), trains H steps, uploads its update |
| Merger | every peer | computes the round's merge from the counted set |
| Closer | the first peer whose conditional commit of "round t closed" succeeds after the deadline | fixes the counted set S_t; other attempts fail and those peers read the winner's entry (w1c S15) |
| Publisher | the first peer whose conditional commit of the round-t checkpoint pointer succeeds | uploads the merged model and outer-optimizer state to its own repository, manifest last (w1d S2) |
| Signer | the owner, offline | signs client releases and the run configuration (R2; w1d T1) |

**Shared state and where it lives**

| Item | Where | Written by | Format |
|---|---|---|---|
| Run configuration: member public keys and storage locations, schedule (round length, deadline), H, seeds, assignment policy, client release digest | owner's repository and a GitHub release (b) | owner only, signed offline | JSON plus signature |
| Updates | each participant's own Hub repository or Storage Bucket (b) | that participant only | safetensors: one file for the shared part and one per held expert with its router rows, plus SHA-256 |
| Round log | one branch of one Hub repository, in an organisation of its own (b) | members, by conditional commit; every entry signed with the member's key | small JSON entries |
| Checkpoints | the publisher's own repository, pointed to from the log; mirrored to a second host | the round's publisher | sharded safetensors with an index, as Petals reads (w1d S5) |

**Merge rule.** For round t with counted set S_t, let Δ_i be peer i's pseudo-gradient (its start-of-round weights minus its end-of-round weights) and w_i the examples it processed. The shared part's outer gradient is g = Σ_{i ∈ S_t} w_i Δ_i / Σ_{i ∈ S_t} w_i. Each expert, with its router rows, uses the same sum over its holders in S_t only (Stage 0's D11 rule). The configured outer step (plain averaging as in Stage 0, or Nesterov) is then applied identically by every peer. An expert with no update in S_t keeps its weights and outer state. This is Stage 0's merge computed by every peer instead of one coordinator; the existing coordinator code already implements merging and the outer optimizer (ROADMAP §1). Each peer posts the hash of the model it computed. If merges are bitwise reproducible across our machines (prototype P6), equal hashes confirm agreement; otherwise peers compare within a tolerance, as Templar's sync score does (w1c S4, Q3b; Gauntlet §3.2).

**Synchronous and group modes**
- **Synchronous mode (D38):** the closer may close round t only when every peer assigned in round t has posted. Assignment, H and merge are Stage 0's, so Gate N1a compares against the simulation. A long timeout aborts and records the round instead of blocking forever, the flaw in flwr-serverless's synchronous mode (w2c T2).
- **Group mode (R4, as read in the header):** the configuration sets a deadline per round; the closer closes at the deadline with whoever has posted. A late peer adopts the new checkpoint, as Decoupled DiLoCo's learners overwrite their fragment with the syncer's (w1b S1) and Hivemind's late peers download state from donors (w2b B1).
- **Gossip variant**, if the owner prefers no barrier: pairs drawn from run seed and round over the present set exchange through the host, and the single shared model is given up (section 4.0). NoLoCo's code shows a pairing every worker can compute, but over a fixed world (w2b B10).

**Holder-count rule (R5)**
1. The present set P_t is the members with a signed "ready for round t" entry in the log before round t starts. A deterministic assignment needs an agreed present set; NoLoCo's code draws over a fixed world and would pair peers with absent partners (w2b B10).
2. Assignment from run seed, round number and P_t with the rolling policy, which gives exactly 2 holders per expert in Stage 0's setting (D37). Holders of one expert are placed in different homes where possible (Bamboo's different zones, w2b B13).
3. If an expert's group falls to 1 by the deadline, the survivor's update is merged alone (a quorum of 1, as Decoupled DiLoCo allows per fragment) or the expert's update is skipped. No source measures which is better (w2b F9), so Gate N1b pre-registers one.
4. If it falls to 0, the expert keeps last round's published state; one round of its training is lost, not the expert (w2b F9).
5. If too few peers are present to give every expert 2 holders, the round runs full-copy units only, or is skipped.

**Failure behaviour**
- A peer leaves mid-round: its update never arrives and is outside S_t.
- Every peer goes offline: the log and checkpoints stay on the host; training resumes from the last checkpoint when peers return.
- The owner's laptop is off: no role needs it except signing a new configuration or release.
- A closer or publisher dies mid-commit: the next peer's conditional commit succeeds (w1c S15); readers never use a checkpoint without its manifest (w1d S2).
- The host is down: rounds stall; checkpoints survive on the mirror (the ROADMAP risk table asks for more than one host).
- A member corrupts the log: forged entries fail signature checks and are ignored, but a member with write access can delete or squash the history; recovery uses checkpoints and per-participant repositories.

**Reused and built**
- **Reused:** `huggingface_hub` (uploads, conditional commits, Storage Buckets; Apache-2.0, `pushed_at` 2026-10-13T13:54:35Z queried 17:42 TST, w1c S15); safetensors (Apache-2.0, w1d T7); PyTorch; the existing `cassandra_chorus/coordinator` (assignment, merging, outer optimizer) and training loop; a standard signature scheme (Psyche signs commitments with ed25519, w1c S1; BOINC uses RSA, w1d T1).
- **Built:** the log format and its three rules (present set, close, counted set); the client loop (download, train, upload, resume, auto mode); signature and hash checks; a status page rendered from the log.

**Central:** the host, class (b); the signing key and configuration (R2). Nothing of class (a) or (c). Flags if adopted: the Hub's bucket event stream (borderline); Cloudflare R2 (an owner-subscribed account, possibly paid; section 7).

**Risks**
- Hub commit limits are undocumented, and "a few thousand commits" degrade a repository; the commit arithmetic in Q5 suggests the log repository reaches that within weeks, so the log may need rotating or squashing by the owner.
- Traffic: in full-copy rounds each peer downloads N − 1 updates (2.4 GB at N = 5 and 0.6 GB) to compute the merge itself. A publisher-only merge cuts this to one checkpoint per peer but makes others trust or spot-check it (w1a Q2). Slice holders fetch only the shared part and their experts' files.
- Round time: blocking rounds add upload, wait and download to every round; 240 s per 0.6 GB upload at 20 Mbit/s. An eager one-round-delayed variant would overlap it at about +0.75% (w1b S13) and give up identical models.
- Listing staleness and half-written uploads, handled only if every reader honours manifests and log entries.
- The log is protected only by members' honesty and host rules (w1c Q3d).
- Quality of deadline-quorum rounds at 3 to 5 peers, and of experts left with one holder, is unmeasured.

### 4.2 Option B: private peer swarm among our machines (inference)

- **Peer roles:** trainer; bootstrap and relay (any of our machines that is publicly reachable while online, configured as a static relay with our peer IDs only and raised limits; w1a S4, S9); averaging-group member; checkpoint publisher chosen by rule.
- **Shared state:** model replicas or expert copies on peers; membership from the owner-signed configuration (a private DHT adds nothing at 3 to 5 members, Q1); addresses refreshed through a file on a host, as BEP 5's `nodes` key suggests (w1a S10); checkpoints and configuration on a host (b).
- **Merge rule:** group all-reduce per round: shared part over all present peers, each expert over its present holders (Moshpit-style group averaging, w1b S3). A single shared model exists only when one group spans everyone present.
- **Synchronous mode:** one group of all assigned peers, waiting for all. **Group mode:** a matchmaking window, then all-reduce with whoever came; Hivemind needs at least 2 members and otherwise each peer keeps its local copy (w2b B1).
- **Holder rule:** each expert's averaging group is its holders. If one holder misses matchmaking, no group forms and the other keeps its own update; if one fails mid-round, the survivor keeps a partly averaged expert (Hivemind) or restores and keeps its own (PCCL) (w2b F1). Between published checkpoints, an expert's state exists only on its holders.
- **Failure behaviour:** if no reachable machine is online, no two NATed peers can connect (Q2), and the swarm stops. A joining peer succeeds with probability P_join (Q1).
- **Reused and built:** iroh, for its Windows CI, Windows relay binary, relays that carry data, and Python wheels (Alpha) (w2a 7); or go-libp2p through a daemon, as Hivemind does. Hivemind's averager failure semantics serve as a reference design, not a dependency, given no native Windows support and a 2023 transport fork (w2a 1). Built: averaging protocol, membership, client, everything above transport.
- **Central:** host (b); our intermittent machines as bootstrap peers and relays. Library defaults (n0 relays and discovery, IPFS bootstrap) are class (c) and must be replaced.
- **Risks:** needs a reachable machine whenever peers connect, which is unmeasured; a relay on a 20 Mbit/s home uplink needs at least 240 s per 0.6 GB, shared by concurrent transfers (w1a Q2); CGN and short NAT timeouts; go-libp2p's pnet runs over TCP or WebSocket only, not QUIC; py-libp2p's NAT traversal is unconfirmed; no single shared model in group mode.

### 4.3 Option C: hybrid (inference)

Option A's log, configuration and checkpoints stay the source of truth for membership, the counted set and recovery. Where a pair of peers can connect directly (measured in prototype P2), the update bytes travel peer to peer, and the log records their hashes so every peer still merges the same counted set. Any pair that cannot connect falls back to the host. This gains speed and lowers host traffic where direct links work, at the cost of two transport paths to build and test. Central elements are those of A, plus our intermittent machines as relays.

### 4.4 The options against R1 to R7 (inference)

| | A. Bulletin board | B. Peer swarm | C. Hybrid |
|---|---|---|---|
| R1 | met: nothing of ours runs continuously | met only while a reachable machine of ours is online | met |
| R2 | met: signing key, configuration, host | met | met |
| R3 | met: no relays at all | met only with our reachable machines as relays | met; direct links optional |
| R4 | group mode by deadline-quorum; synchronous mode by waiting for all | group all-reduce; synchronous mode as one group | as A |
| R5 | by assignment; group can still fall to 1 or 0; one round lost at worst if checkpoints are per round | by assignment; state at risk between checkpoints | as A |
| R6 | both: per-expert files make slices natural | both | both |
| R7 | per-participant repositories plus a signed log (4.5) | peer-to-peer plus checkpoints on a host | as A |
| Keeps central | (b) | (b), our intermittent machines | (b), our intermittent machines |
| Main unknowns | Hub limits; upload times; CAS behaviour; quorum quality at 3 to 5 peers | reachability of any pilot machine; relay throughput | all of A's and B's |

### 4.5 Who may write shared state (R7) (inference)

- **Updates and checkpoints: option 2, signed per-peer storage.** Each participant writes only to their own repositories (their own account, or the Hub's free `contributor` role in an owner-administered organisation, which writes only to repositories the user created; w1c S13). An honest mistake or a poisoned update then affects only that participant's contribution, which the merge can skip.
- **The round log: option 1, confined.** One branch needs several writers, so members need write access to one repository. On the Hub that means the `write` role, which can "create, delete, or rename any repo" in its organisation. Putting the log in an organisation of its own limits that reach to the log. Entries are signed with members' keys from the owner-signed configuration and appended with conditional commits, so forged entries are ignored and races cannot overwrite each other, provided the Hub enforces `parent_commit` on the server, which is not confirmed (section 7; prototype P4). What remains: a member can delete or squash the log; recovery comes from checkpoints and per-participant repositories. Whether a fine-grained token could narrow write access to one repository is unconfirmed (section 7).
- **Releases and configuration: the owner only**, signed offline.
- **Format rule for all writes:** safetensors only; no participant's file is ever unpickled or executed; values are checked for NaN and Inf before merging (Q8).
- **Not recommended for the pilot:** a ledger (option 4) is class (c), outside R2, and not needed for any function a trusted pilot uses (Q3); flagged for Phase 6. Peer-to-peer only (option 3) loses state when every peer is off, and every exemplar read still had a coordinator (w1c Q7).

### 4.6 Build on an existing system or write our own (D35) (inference)

Maintenance values are from the Q9 table (GitHub API `commit.committer.date` and `releases/latest`, queried 2026-10-13 17:55 to 18:21 TST).

| Candidate base | What it would give | Why not as a base |
|---|---|---|
| Hivemind | group averaging with failure handling, private DHT, relays, state transfer | no native Windows install (`setup.py` stops); transport fork from 2023 on go-libp2p v0.32.1 against upstream v0.50.0; low activity; no storage; R5 not provided; its only all-NAT mode is (c) (w2a 1) |
| Psyche | complete full-copy stack with a checkable merge rule | Solana (c); Linux only; no commit since 2026-03-20; synchronous full copies only (w2a 8) |
| prime-diloco | synchronous DiLoCo with an elastic group | master store (a); no default-branch commit since 2025-04-10; full copies only (w2a 9) |
| Templar | storage-only exchange, per-peer buckets | dormant; Bittensor (c) (w2a 11) |
| PCCL | fault-tolerant collectives, bit-identity checks | master (a), whose crash ends the run; one release; no Windows CUDA build (w2a 10; w2b B8) |
| Flower, BOINC | mature server frameworks | a server, class (a), by design (w2c B1, F1) |

The healthy, Windows-tested projects are transport libraries (go-libp2p, iroh), which provide none of the training coordination. So the inference is: **write our own thin coordination layer**, reusing libraries rather than frameworks: `huggingface_hub` and safetensors for Option A now, iroh (or go-libp2p) later if Option C proves worthwhile, and Hivemind's and Psyche's failure rules as reference designs.

### 4.7 Recommendation (inference; the owner accepts or rejects it)

1. **Design:** Option A now, in both modes, with the transport behind one interface so Option C can be added if prototypes P1 and P2 find reachable homes.
2. **R4:** read as deadline-quorum group averaging (section 4.0); the synchronous mode serves Gate N1a.
3. **R7:** per-participant repositories for updates and checkpoints; a signed, conditionally committed log in its own organisation; the owner alone signs releases and configuration (section 4.5).
4. **D35:** our own thin layer on libraries, not an existing framework (section 4.6).

**It depends on:**
- the owner confirming the R4 reading;
- P4: conditional commits behaving as documented under 3 to 5 concurrent writers;
- P3 and P5: the Hub accepting the pilot's commit and upload rate, or Storage Buckets serving for updates, and upload times from pilot homes fitting a round;
- P6: merges being bitwise reproducible, or the owner accepting tolerance checks;
- the owner accepting that, during the trusted pilot, any member could damage the log.

**What would change it:** if the Hub's limits or terms rule out per-round commits, GitHub release assets (500 content-creating requests per hour) or an owner-subscribed R2 bucket (possibly paid; section 7; flagged) could carry updates. If a reachable machine and good per-pair punching are found, Option C moves earlier. If the owner rejects the R4 reading, the remaining paths are a rotating holder (untested) or gossip (no single shared model); both need prototyping before Gate N1b.

---

## 5. Asynchronous algorithm options

**Evidence on each option's quality cost** (all from section 3, Q4; w1b F3 and evidence grid; relative gaps in loss or log-perplexity are w1b's arithmetic, inference)

| Option | Central holder | Against synchronous local averaging | Against centralized or data parallel | Nearest to the pilot |
|---|---|---|---|---|
| Async Local-SGD, Delayed Nesterov + Dynamic Local Updates (2401.09135 v2, Tables 1 to 3) | server (a) | −0.18% to +0.06% in continued pretraining (Tables 1 to 3) | −0.3% to −0.9% against a same-step large-batch worker at 4 workers (Table 3); +0.25% at 16 workers (Table 2, 20M) | 150M, 4 workers, simulated speeds, not from scratch |
| Same, reimplemented by HALoS (2506.04531 Table 1) | server (a) | 24.8% more tokens than DiLoCo at 160M from scratch (inference: 16.1B / 12.9B); 70M and 410M: protocol not confirmed (section 7) | not used (section 7) | 160M from scratch, 16 workers |
| Decoupled DiLoCo (2604.21428 v1, Tables 5, 12, 14) | syncer (a) | K = 1 with grace window matches fully blocking K = 8 on downstream averages (55.3 against 54.4 text) | downstream parity at 2B (54.4 against 55.1) to 9B | data-centre scale; no loss gaps |
| HeLoCo (2606.00271 Table 1) | synchronizer (a) | −1.8% to +15.4% with staleness | none | 15M, far from converged (inference) |
| Pairwise gossip, Factored Gossip LocalM1M2 (2606.22768 Table 1) | none | +1.29% at 8 workers | +3.49%; +8.99% at 16 workers | 1.5B; no departures |
| GASLoC 2-Peer / 1-Peer (2606.11081 Tables 1b, 2, 3) | none | +0.61% to +2.55% / +1.21% to +3.68% at 134M | 551M: 2-Peer matches DiLoCo at 8 replicas (2.64, Table 3); DDP's 2.64 (Table 2) comes from a one-step run at 16 replicas, and the parts read give no DDP value at 8 replicas | 134M, 8 workers minimum |
| NoLoCo (2506.10911 Table 1) | none | −1.45% to +0.42% with pipeline routing; +6.6% and unstable without it per Factored Gossip | +0.83% to +7.68% | disputed |
| Eager one-round delay (2502.12996 Tables 1, 2) | none | +0.75% (2 replicas) | +0.40% to +0.75% at 1B | tells what a one-round lag costs |
| Group all-reduce: Moshpit, DeDLOC | none | not measured | "same within the margin of error" (figure only) | real churn, but synchronous large-batch SGD |
| Holder groups: FoMoE (Table 6, v2, via w1b S17) | coordinator (a) | not applicable (synchronous) | +1.6% / +2.9% / +2.1% against full replica with 2 holders | the only sliced-MoE evidence |

**What the evidence says** (w1b "What the evidence says").
- Staleness through outer momentum is the documented failure: naive asynchronous DiLoCo is worse at every size in Async Local-SGD; asynchronous Nesterov "diverges across all configurations" in HeLoCo; a naive one-round delay costs +12.7% until the outer learning rate is lowered. Every fix changes how momentum meets stale updates.
- Parity claims depend on the regime, as the HALoS reimplementation shows.
- Pure pairwise gossip costs about 0% to 5% against DiLoCo at 8 to 32 workers (inference: loss ratios in w1b S10, log-perplexity ratios in S9), more with more workers within each paper; NoLoCo's results range from −1.45% to +0.42% (inference, w1b S8).
- Every asynchronous result near 100M to 300M is continued pretraining, a reimplementation inside a server hierarchy, or gossip tested only at 8 workers or more; none has 3 to 5 peers with real departures (w1b gate item 8).

**Candidate for Gate N1b (inference).** **Deadline-quorum group averaging** (section 4.0, Option A's group mode), with the outer optimizer fixed in the gate's pre-registration, measured at equal compute against the synchronous mode and against centralized training. Reasons: it is the only server-free option that keeps a single shared model (principle 6); its closest evidence is Decoupled DiLoCo's quorum result (Table 5) and the deadline rounds Psyche and Templar run; its cost relative to the synchronous mode is mostly dropped late work, which a gate can measure. Its weaknesses: that evidence is at 2B with a syncer in data centres, and nothing tests it with 3 to 5 peers or holder groups. A second arm with pairwise gossip drawn from run seed and round is worth adding only if the owner is willing to give up the single shared model.

**What the gate needs** (inference from the standards the sources use; w1b "What a Gate N1b would need"):
1. Both comparisons at equal compute on Stage 0's seeds (7, 11, 19), with the baseline stated, because the asynchronous papers use DiLoCo, same-batch data parallel or tokens to target loss, and none uses Stage 0's more-steps baseline. With dropped late work, "equal compute" must say whether it counts steps run or steps merged (inference).
2. Equal-tokens and equal-wall-clock readings, one pre-registered as primary: HeLoCo's comparison flips sign between them (Table 1, row (1,6,6,6,6): 5.43% worse at equal tokens, 5.80% better at equal wall-clock).
3. A recorded, replayable churn schedule with peers leaving mid-round, as Decoupled DiLoCo's event tapes allow (App. E.1).
4. The staleness or lateness actually seen, per peer.
5. For slices: realized holders per expert per round, and the quality of experts whose group fell to 1 or 0.
6. The outer optimizer and merge as part of the gate's definition.
7. A downstream check after SFT, given the conflicting post-training reports (Q4).

---

## 6. What to prototype before deciding

Durations are this report's estimates (inference), for one developer.

| ID | Experiment | What it measures | Open point it settles | Time |
|---|---|---|---|---|
| P1 | Home network census at each pilot home: router WAN address against the address seen from outside (CGN), IPv6 and its inbound firewall, UPnP or PCP, NAT mapping and filtering class on TCP and UDP (as ProbeLab classifies) | which homes could host a bootstrap peer or relay | feasibility of Options B and C; R3 | 1 day to script, an evening per home |
| P2 | Pairwise connection test: iroh with a custom relay on any reachable pilot machine, and go-libp2p DCUtR with a static relay; then a 0.6 GB transfer direct and through the relay | per-pair success, time to connect, mapping lifetime, relay throughput on a home uplink | whether Option C is worth building | 2 to 3 days |
| P3 | File-host transfer test from each home: upload and download 0.2 and 0.6 GB safetensors to a Hub repository, a Storage Bucket and a GitHub release asset; time until another home sees the file | upload and download times, failures, HTTP 429 responses, listing delay | Option A's round time; which host carries updates | 1 to 2 days |
| P4 | Hub coordination semantics: 3 to 5 concurrent writers appending to one branch with `parent_commit`; an upload from a machine with a wrong clock to test whether bucket `uploadedAt` is server-assigned; visibility of a multi-file commit | lost or duplicated appends; timestamp source; atomic visibility | the counted-set record (Q3 candidates 2 and 3) | 1 day |
| P5 | Hub limits and terms: run the planned commit rate on a test repository for a week; a written enquiry to Hugging Face about "excessive bulk activity" | whether undocumented commit limits or abuse rules trigger | Option A's viability on the Hub | about 1 week elapsed, little effort |
| P6 | Merge determinism: compute the same merge from the same files on each pilot machine, on CPU and GPU, and compare hashes; if they differ, the largest difference | bitwise reproducibility of the merge | hash check (w1c S8) or tolerance check (w1c S4) | half a day |
| P7 | Simulation in the Stage 0 harness: deadline-quorum rounds (and, if wanted, gossip) with 3 to 5 workers under a replayable churn schedule, rolling assignment, and injected 2-to-1 and 2-to-0 holder drops | quality against the synchronous mode and centralized training; effect of losing a holder | Gate N1b design; R5's quality effect | several days of GPU time on one machine; belongs after Phase 1, which has no GPU budget |
| P8 | Windows install check on pilot machines: `huggingface_hub` with Xet, iroh's Python wheel, py-libp2p | whether each installs and runs natively | Windows support of the chosen libraries | half a day |
| P9 | Signing dry run: sign a release and a configuration with an offline key; verify on every pilot machine | that the BOINC-style chain works end to end | Q8's mechanism for R2's signing key | half a day |

---

## 7. Unverified leads

Everything here was seen but not confirmed at source, or was listed as unverified in a notes file. **Nothing in this section is used as evidence in sections 1 to 6**, except the four items in the first list, which a later strand verified (the Agora item only in part).

**Items one strand listed as open and a later strand closed.** These four are available to sections 1 to 6 on the strength of the later reading named in each. The first two rest on code that was read but not run, so they are inferences; of those two, only the NoLoCo item is used (section 2.2, Q6, section 4.1).
- Whether Hivemind's averager is Moshpit All-Reduce (w1b): w2b B1 reads `key_manager.py` and finds it is Moshpit when initial group bits are set and plain group all-reduce otherwise.
- How NoLoCo draws its pairs (w1b): w2b B10 finds every worker computes the same permutation seeded by the local step counter, with no run seed and no coordinator.
- PCCL's NAT traversal and master failover (w2a): w2b B8 read PCCL's `03_MasterOrchestration.md` in full: "Master Crash = End of Run", with no built-in master re-election, and peers need open ports or port forwarding, with no relays. Used in section 2.1, Q6 and section 4.6.
- Agora's failure results (w1c), partly closed: w2b B11 read v1 §3.5.3 and §6.4 in full; §6.4 is used in Q6. The live-run measurement in §5.7.1 ("All-reduce fault tolerance") was not read by any strand and stays open, with the inter-replica divergence of §5.7.2 (w1c list below).

**From w1a (discovery and NAT)**
- Numbers Trautwein et al. cite from other studies: Halkes and Pouwelse 2011 (about 64% of peers punchable, over 80% success), Guha and Francis 2005 (88% TCP over 93 home NATs), about 11% endpoint-dependent NATs; Seemann, Inden and Vyzovitis 2022. Not read at source.
- iroh's claim that "roughly 9 out of 10 network configurations allow a direct connection": no method, dataset or date on the pages read; ProbeLab says it has not seen a study backing such numbers.
- Who operates Psyche's relay hosts under `iroh.link`.
- Whether rust-libp2p's private networks (pnet) run over QUIC (w2a; not checked).
- py-libp2p's README marks circuit relay v2, AutoNAT and hole punching as done; not tested or cross-checked.
- Whether rust-libp2p's private networks work over QUIC.
- Whether rust-libp2p's Kademlia persists its routing table between runs (w1a gap 8: not checked).
- Whether iroh hole punching still works when its relay runs without a DNS name or TLS certificate (`--dev` HTTP mode, which per its README skips QUIC address discovery) (w1a gap 7; also open in w2a).

**From w1b (averaging)**
- Decoupled DiLoCo Table 14, 2B column: printed text averages 52.3 and 51.6 do not match the per-task values, which average to 55.1 and 54.4 (the values Table 12 prints).
- Decoupled DiLoCo Table 15: the reference run for its validation-loss deltas is not stated; its scavenging deltas (for example +0.23% at +300% for Decoupled DiLoCo) are therefore not used.
- Decoupled DiLoCo Table 5: the caption and §5.4 name different TPU generations.
- HALoS Table 1: which method produced the reference loss, and whether the 70M and 410M columns follow the 160M protocol ("from scratch on the first 12.9B tokens"); protocol not confirmed. Hence its "+24.8% tokens against the reference at 160M" is not used (it equals the DiLoCo comparison used in Q4 only because DiLoCo also needed 12.9B tokens at 160M), nor Async Local-SGD's token cost against DiLoCo at 70M and 410M (+18.6% and +30.9%; inference: 14.0B / 11.8B and 16.1B / 12.3B).
- HeLoCo's abstract figures ("up to 7.5%", "up to 22.1%", "up to 3.3%") match single table cells, not the comparisons the abstract implies.
- Venues not confirmed at source: D-PSGD (NeurIPS 2017), AD-PSGD (ICML 2018), HALoS (ICML 2025), Factored Gossip DiLoCo (ICML 2026, arXiv comment only).
- Factored Gossip DiLoCo: who draws its pairwise matching.
- Momentum Look-Ahead (Ajanthan et al., ICLR 2025 workshop), cited by Decoupled DiLoCo and used by HeLoCo: no arXiv version found; not read.
- SWARM Appendix A beyond the parts w2b read; AD-PSGD Appendix A; D-PSGD's supplementary NLP results.

**From w1c (membership and write access)**
- Whether Psyche's `update` instruction refuses changes during an active run.
- Whether Psyche implemented verification after 2026-03-20 elsewhere.
- Whether a Psyche joiner checks the model it assembles from peers against a hash.
- Which process hosts prime-diloco's `god_store`.
- Tailscale's architecture, and so its class (c) classification.
- How Bittensor validators' weights combine (Yuma consensus), and whether miners ever follow a validator other than the highest-staked.
- Whether Templar miners' models are bitwise identical (the sync-score threshold suggests not).
- The licence of Gensyn's RepOp kernels: the two READMEs describe it differently.
- Whether a Hugging Face fine-grained token can restrict writes to one repository.
- Whether the Hub server, rather than the client library, enforces `parent_commit` on a conditional commit (S15 read the client docstring only); section 4.5's round log depends on it (prototype P4).
- GitHub per-path write limits: not found in the parts read, which is not a confirmed absence.
- TOPLOC (arXiv 2501.16007 v2): downloaded, not read.
- Agora's live-run all-reduce fault tolerance (§5.7.1) and inter-replica divergence (§5.7.2).
- `docs/prior-work.md`'s Psyche entry (Consilience 40B, "moving from provability to performance"), from a blog post, not re-read.

**From w1d (storage, trust, bandwidth)**
- Hugging Face commit rate limits (documented as existing, values undocumented).
- How much free public storage "Best-effort" means; the free allowance of Storage Buckets.
- Whether Hub or GitHub download URLs work as BitTorrent web seeds (BEP 19).
- Whether a multi-file Hub commit becomes visible to readers all at once (not stated in the documentation read, H1).
- Xet deduplication savings on successive training updates (not measured by any source read).
- Whether Cloudflare R2's checkout requires a payment card.
- Whether GitHub release downloads count against REST rate limits.
- Whether `cosign sign-blob --key` uploads to Rekor by default.
- Whether pip verifies PEP 740 attestations at install time.
- DisTrO's algorithm (the report does not describe it; Psyche's `distro.rs` not read).
- Whether Psyche's run-manager checks image signatures: a grep of two files found no check, which does not prove absence.
- How a joining peer obtains the current model in Covenant-72B.
- SparseLoCo's 178M results (Appendix J) and its Table 5 (garbled).
- That `prime-diloco` is INTELLECT-1's framework rests on its description and checkpoint code, not on a statement by Prime Intellect.

**From w2a (systems health)**
- That a per-expert Hivemind averager under its own key prefix would match only that expert's holders (inference from a docstring).
- Whether PCCL's `peer_group`, or several communicators, can express overlapping holder groups.
- py-libp2p's NAT traversal on Windows and its interoperability with go and rust peers (its Windows CI excludes the interop tests).
- iroh-ffi's Python support for custom relays (a `support-matrix.yaml` claim).
- Psyche's current status (docs.psyche.network not fetched).
- Whether prime-diloco's 2026 pushes went to other branches.
- Issue-count discrepancies: rust-libp2p 303 against 299; Node0 6 against 2.
- RL Swarm: whether community swarms run; its README's notice and body conflict.
- Flower's native Windows support; BOINC's Windows client (inferred from CI).
- Python bindings for go-libp2p and rust-libp2p outside their repositories.
- Whether the name `agora` on PyPI belongs to Pluralis.

**From w2b (churn)**
- Petals' rebalancing threshold: p = 20% in the paper against a code default that w2b reads as about 33%.
- SWARM Table 5 (32-hour trace replay; no rebalancing 82.7 / 99.0 / 45.4% of optimal throughput overall, first hour and last hour; T = 300 s 95.8 / 99.4 / 88.9; T = 60 s 97.6 / 99.8 / 91.7): row assignment inferred from cell order.
- Whether SWARM's §4.3 and §4.4 experiments used rebalancing code absent from the public repository.
- Whether Psyche's live Consilience run used the repository's configuration values.
- Hivemind's `k_min` check counting responses over the whole batch.
- Hivemind's `_load_state_from_peers` replacing a caller's timeout.
- Learning@home's DHT persistence may exist in the older `mryab/learning-at-home` code.
- NoLoCo's default torch.distributed timeout in the version it pins.
- What an Agora trainer does when a forward replica has left before the backward pass.
- PCCL's peer-group tests (`test_peer_groups.cpp`), not read.
- Bamboo's cost reduction: 2.4× in the abstract against 3.6× in §1.
- Agora's "operating threshold near 85%" of reducer participation, below which convergence suffers (§6.4, Figure 45 caption): one ablation run, no repeat or variance reported.

**From w2c (contrasts and file-host exchange)**
- Venues of LambdaML (SIGMOD 2021) and FedLess (IEEE BigData 2021), seen only in search results.
- LambdaML Table 6 (S3 bandwidth and latency constants), garbled.
- FedLess Fig. 12 cost values.
- STUNMESH-go's success in practice; its documentation site and FOSDEM 2026 talk not read; whether anyone backs it with a static file host.
- HF²L's webhook-triggered GitHub workflow and its Exchange service.
- Hivetrain's operating history: run length, miners, any Hub limits hit.
- Whether the Hub assigns per-file `uploadedAt` server-side (the name suggests so; `mtime` is probably client-supplied).
- IPFS- and blockchain-based FL papers (IPLS 2101.01901, GFL 2010.10996, BRFL 2310.13403), GitFL (2211.12049), FLHub (2202.06493), known only from search results.
- Tailscale's statement that a signalling side channel "can have a few seconds of latency" and "only needs to deliver a few thousand bytes": an author's statement, not a measurement.
- Hyperswarm itself (cloned, not read).
- Flower's "Fault Tolerant FedAvg" implementation.

**Disagreement between notes, unresolved.** Agora's run length: 40 days (paper abstract, w1c S11) against "500B tokens over 7 weeks" (README banner, w2a 13).

**Stage 0 leads now read in this study** (from the Stage 0 report's section 7; used where cited): EDiT, HALoS, HeLoCo, Eager Updates, Covenant-72B, INTELLECT-2, and Moshpit SGD and DeMo beyond their abstracts (w1b, w1c, w1d). Read at abstract level only: "Not Every Sync Is Safe" and Pseudo-Asynchronous Local SGD.

**Leads seen but not opened** (no claims made from them)
- Algorithms: SeedFlood (2602.18181), Epidemic Learning, SPARTA, Gensyn GWTF, "Taming Momentum in a Distributed Asynchronous Environment" (1907.11612), FedBuff, Papaya, HGA-FL, FedAH, DiLoCoX (2506.21263), INTELLECT-3 (w1b, w1d).
- Systems: IOTA (Macrocosmos, 2507.17766; note 04a records an orchestrator), Gensyn REE, torchft, Hyperswarm, Tailscale and Headscale beyond N4 and N5, ZeroTier, Yggdrasil, WebRTC ICE, js-libp2p mechanisms, `PrimeIntellect-ai/prime-rl` (w1a, w1c, w2a, w2c).
- Serverless and storage-assisted FL: Apodotiko (2404.14033), FLStore (2503.00323), LIFL, λ-FL, SMLT (2205.01853), FLSys (2111.09445), harmonia, manual WebRTC signalling projects, a 2016 WireGuard hole-punching proof of concept (w2c).

---

## 8. Search log

All searches ran on 2026-10-13, local machine time (TST, UTC+3). Search tools were used only to discover sources; every number in this report was read in raw text, code or an API record. The full logs, with every query and API call, are in each notes file's "Query log" section.

| Strand (notes file) | Time window | Sources and tools | Main queries and API calls |
|---|---|---|---|
| Discovery, NAT, bootstrap ([w1a](2026-10-13-system-study-notes/w1a-discovery-nat-bootstrap.md)) | 17:18 to 17:36 | arXiv PDF and abs (3 papers); `libp2p/specs`, go-libp2p, go-libp2p-kad-dht, rust-libp2p, py-libp2p, Hivemind, its `p2pd` fork, Petals, iroh and Psyche clones; iroh docs raw; BEP 5; RFCs 4787, 6888, 7021; Richter et al. PDF; ProbeLab blog and report; GitHub API at 17:27:07 | 3 web searches, e.g. "large scale measurement decentralized NAT traversal DCUtR hole punching arXiv"; `gh api repos/.../releases/latest` for 8 repositories |
| Averaging without a server ([w1b](2026-10-13-system-study-notes/w1b-averaging-without-a-server.md)) | 17:18 to 17:44 | arXiv abs, PDF and HTML (19 papers); export.arxiv.org API; GitHub API at 17:36 (14:36 UTC) for 10 repositories; Stage 0 notes 01, 04a, 04b, 06 | 8 web searches, e.g. "asynchronous DiLoCo language model pretraining stale updates 2025 arXiv", "gossip averaging decentralized LLM pretraining no all-reduce 2025"; arXiv API `all:"momentum look-ahead"` |
| Membership and shared state ([w1c](2026-10-13-system-study-notes/w1c-membership-shared-state.md)) | 17:19:05 to 17:44:55 | GitHub organisation listings and clones (Psyche, Templar, prime-diloco, Prime protocol, Node0, Agora, RL Swarm contracts, Gensyn audit); arXiv API and PDFs (9 papers); hub-docs, GitHub docs and `huggingface_hub` raw files | `gh api orgs/.../repos?sort=pushed`; 2 web searches, e.g. "decentralized LLM training without blockchain coordinator shared object storage deterministic aggregation 2026" |
| Storage, trust, bandwidth ([w1d](2026-10-13-system-study-notes/w1d-storage-trust-bandwidth.md)) | 17:18 to 17:50 | arXiv API and PDFs (11 papers); DisTrO report; hub-docs, `huggingface_hub`, GitHub docs and site-policy, BEPs, WebTorrent, IPFS docs, Cloudflare R2 docs, Sigstore, PyPI warehouse docs, BOINC wiki, safetensors, PyTorch docs; PyPI JSON and Integrity API | no web search; known repositories and arXiv IDs only |
| Systems health ([w2a](2026-10-13-system-study-notes/w2a-systems-health.md)) | 17:54:55 to 18:21:14 | GitHub API for 22 repositories (`repos`, `releases/latest`, `commits`, `languages`, workflows, issue and PR search); PyPI, crates.io, npm and Go proxy; raw READMEs, build and CI files | no web search; per-repository API windows recorded in the note |
| Churn ([w2b](2026-10-13-system-study-notes/w2b-churn-handling.md)) | 17:53 to about 18:45 | clones of Hivemind, Petals, SWARM, Moshpit, Psyche, PCCL, prime-diloco, NoLoCo, Node0, Agora, DeDLOC; arXiv abs and PDFs (8 papers) | no web search or GitHub API; code and papers named in the brief and wave 1 |
| Contrasts and file-host exchange ([w2c](2026-10-13-system-study-notes/w2c-contrasts-filehost-exchange.md)) | 17:53:47 to about 18:36, and 22:00 to 22:12:08 | BOINC wiki, Flower, Templar, HyperDHT, Hyperswarm, Headscale, flwr-serverless, Hivetrain, HF²L, STUNMESH-go, wgsd clones; arXiv abs and PDFs (8 papers); Tailscale blog; Hub OpenAPI specification; GitHub API at 18:25 | 10 web searches, e.g. "federated learning shared object storage S3 no server asynchronous", "decentralized training Hugging Face Hub exchange model updates between peers no server", "hole punching coordinated through git repository or pastebin endpoint exchange p2p no relay" |

No strand records using WebFetch. arXiv requests were spaced by `sleep 3`. Nothing downloaded was run, built or installed.

**Not covered, across all strands**

- **Home connections:** no source measures hole punching between two real home NATs, relay throughput on a home uplink, file-host exchange of 0.2 to 0.6 GB updates from homes, IPv6 reachability of homes, or CGN deployment in Turkey (w1a gaps; w2c gap 1).
- **Small pools:** no result with 3 to 5 peers, real departures at 100M to 300M, or an expert's holder group falling from 2 to 1 or 0 (w1b gaps; w2b gaps).
- **Code not read:** Node0 (cloned only); Hyperswarm (cloned only); Agora beyond a grep for timeouts; Psyche's DisTrO implementation; Hivemind's `state_averager.py` in w1d; Templar and Covenant churn handling; HF²L's `docs/`.
- **Sections not read:** SWARM Appendix A in w1b (read in part by w2b); AD-PSGD Appendix A; D-PSGD supplementary results; NoLoCo Appendices D to F; Factored Gossip §1 to §3 and D, E; GASLoC §1, §2, §3.1 and appendices; HeLoCo §1, §2 and appendices; HALoS §1 to §3; EDiT tables (garbled); BOINC paper §6 and §7; Flower's Simulation Runtime; Bamboo and Oobleck §7 tables; Petals Appendix F and SWARM Figure 6 (figures only); ProbeLab's sub-reports; iroh's `add-a-relay` and dedicated-infrastructure pages; go-libp2p-kad-dht issue #387.
- **Documentation not fetched:** docs.psyche.network, docs.gensyn.ai, Hivemind's documentation site, Agora's and Node0's `docs/`, PCCL's `docs/` beyond two pages, PyTorch Distributed Checkpoint docs, the Hub's S3-compatible bucket API page, GitHub Additional Product Terms, Cloudflare's terms, IPFS pinning services' terms.
- **Citation chasing:** none in this study (no OpenAlex or Semantic Scholar); discovery was by 23 web searches (3 in w1a, 8 in w1b, 2 in w1c, 10 in w2c), the arXiv API, organisation listings and the reference lists of papers read. Venues were not checked in OpenAlex.
- **Ledger costs:** transaction fees, RPC providers and chain availability for any chain.
- **Overlay VPNs:** Tailscale, Headscale beyond its README and two docs, ZeroTier, Yggdrasil, WebRTC ICE.
