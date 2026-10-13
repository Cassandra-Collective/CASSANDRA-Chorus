# System study brief: coordinating volunteer training with no server of ours

Roadmap step 1.1 (`docs/ROADMAP.md`). Decisions D34, D35, D37 and D38 (`docs/SRS.md` section 9) are the acceptance criteria. Read `docs/ROADMAP.md`, `docs/SRS.md` section 9 (D29 to D38), and `docs/research/2026-10-11-stage0-literature-report.md` sections 3.1 and 5 first.

---

## Your task

Find out how existing systems coordinate training, or similar volunteer computation, across home machines **without a server that anyone has to run around the clock**, and what each of them still keeps central. Then set out the designs open to CASSANDRA Chorus under the owner's requirements below, with the evidence for and against each.

The output is an audited report from which the owner chooses:
- a design;
- whether to build on an existing system or write our own (D35);
- who may write shared state.

We want to know what works and what it costs, not to confirm a preferred answer.

## The project in brief

- **Goal:** CASSANDRA Chorus trains a language model from scratch with volunteers' consumer GPUs. The first product is a small local English and Turkish assistant (D29 to D32).
- **Two kinds of work unit, both supported from the first networked version (D34):**
  - **Full copy:** a peer trains the whole model for H local steps, and the results are averaged (DiLoCo-style local averaging).
  - **Slice:** a peer holds the shared part of a mixture-of-experts model plus some of its experts and trains them for H steps. Each expert is averaged only over the peers that held it; the shared part over all peers.
- **Slice assignment needs no server.** It is computed from the run seed and the round number (`cassandra_chorus/coordinator/assignment.py`), so every peer can compute the same plan.
- **What Stage 0 measured.** In single-machine simulation with synchronous rounds of H = 125, 4 workers and plain averaging, full-model averaging cost +6.1% test bits per character against centralized training, and slicing +10.8% in total (`docs/stage0-report.md`).
- **The pilot:**
  - 3 to 5 trusted people with consumer NVIDIA GPUs on home connections;
  - models of about 100M to 300M parameters, so a full fp16 update is about 0.2 to 0.6 GB;
  - the owner's laptop has unreliable mains power.

## The owner's requirements (acceptance criteria)

- **R1, no server of ours (D37).** Nothing runs around the clock on a machine the owner runs or pays for.
- **R2, what may stay central (D37):**
  - the code-signing key;
  - bootstrap peers, which are the owner's and the pilot participants' machines (intermittently online);
  - public file hosts (for example GitHub releases, the Hugging Face Hub, BitTorrent) for code, data shards and checkpoints;
  - a starting configuration the owner publishes.
- **R3, no third-party relays (D37).** Only our own machines may relay connections between peers.
- **R4, asynchronous or group averaging for production training (D37), plus a synchronous mode (D38)** that reproduces Stage 0's rounds for comparison.
- **R5, at least 2 holders per expert in every round of a decentralized run (D37).**
- **R6, both work-unit kinds (D34).**
- **R7, write access to shared state is your question (D37).** Compare the options and recommend one: per-participant tokens to a shared repository; signed per-peer storage; peer-to-peer only; a ledger.

## Questions to answer

For every claim, cite the source and say what part you read.

1. **Discovery and bootstrap.** How do peers find each other when the only bootstrap peers are home machines that are often off? Which systems use a DHT (Kademlia, the BitTorrent mainline DHT, libp2p), and what happens when every bootstrap peer is offline?
2. **Connections through home routers without third-party relays (R3).**
   - What do hole punching and NAT traversal achieve in practice, with success rates where a primary source gives them?
   - Can our own reachable machines act as relays, and what if none is reachable?
   - Is exchange through public file hosts alone a workable fallback?
3. **Membership and the current model.**
   - Without a server, who decides which peers take part in a round or group, and which model version is current?
   - Which systems define the model by a merge rule every peer computes identically from public inputs, so that any peer can check it?
   - What do ledger-based systems (Psyche, Templar or Covenant) put on the ledger, and is a ledger needed for a trusted pilot?
4. **Averaging without a server.**
   - Synchronous: all-reduce and group all-reduce over home links.
   - Asynchronous and group: Asynchronous Local-SGD (arXiv 2401.09135), Decoupled DiLoCo (arXiv 2604.21428), Moshpit SGD (arXiv 2103.03239), gossip averaging, and others you find.
   - For each: the quality cost against synchronous training **and** against centralized training, with numbers only from parts you read, and the communication cost.
   - Check specifically whether Decoupled DiLoCo's synchronizer can run as a rotating peer role or needs a server.
   - Is there any precedent for averaging an expert within the group of peers that holds it?
5. **Checkpoints when no peer holds the whole model.** How do systems persist and replicate state on public hosts or content-addressed storage? What are the size, rate and terms-of-service limits of the hosts a pilot would use (Hugging Face Hub, GitHub releases, BitTorrent and IPFS)?
6. **Churn.** How do systems handle peers that leave mid-round, stragglers and timeouts? What do they do when a group loses its only copy of something (R5)?
7. **Write access and trust (R7).** For each option in R7: what the participant must be trusted with, what an honest mistake or a malicious participant could do, and what remains central.
8. **Code trust.** How do volunteer-computing projects make sure participants run genuine code (signed releases, reproducible builds), and keep work units as data rather than code?
9. **The systems themselves.** For each candidate:
   - the language and runtime;
   - the licence;
   - its maintenance state: latest release and commit dates from the GitHub or package-index API;
   - documentation;
   - how much of Chorus it would provide;
   - its fit with R1 to R6.
10. **Bandwidth.** What do the systems and papers report about update sizes and compression for 100M to 1B models over home connections?

## Candidates

Evaluate them; do not assume any is right. Each one is listed because of how it coordinates.

- **Peer-to-peer discovery with group averaging:**
  - Hivemind and Learning@home (DHT, decentralized averaging). The 2026-10-07 survey recorded Hivemind as barely maintained; confirm or correct this.
  - Moshpit SGD and DeDLOC.
  - SWARM parallelism.
  - Petals, for its peer-to-peer plumbing.
  - Agora or Pluralis.
  - libp2p and iroh, as building blocks.
- **Shared state on public hosts or a ledger:**
  - Psyche (Nous Research).
  - Templar and Covenant-72B (Bittensor).
  - Prime Intellect's framework (does it need a central orchestrator?).
  - Gensyn, if relevant.
  - Plain content-addressed storage on the Hugging Face Hub or BitTorrent.
- **Contrast cases with a central server:** BOINC and Flower, to show what a server provides and what replacing it costs.
- **Asynchronous algorithms:** as in question 4.

Add anything closer that you find, especially from 2025 and 2026.

## Method and honesty rules

The rules of the Stage 0 literature investigation apply. Additionally:

- **Primary sources only.**
  - For papers: arXiv text read from the PDF or HTML.
  - For systems: official documentation and README files fetched raw, the source code itself, and the GitHub or package-index APIs.
  - Search results and summarizing page fetches serve only to find sources; never record a number or claim from them.
- **Never invent a source.** Anything not confirmed at its source goes only under "Unverified leads".
- **Read status for every source:** full text, sections read (which), abstract only, or code read (which files).
- **Locators for every number:** section, table or file and line, plus version, commit or release.
- **Inference is labelled.** Separate what a source shows from your reasoning, especially in the design options.
- **Scale and setting:** trusted peers or permissionless, data-centre links or home connections, model size.
- **Quotations** under about 15 words.
- **No novelty claims about Chorus.**

## Deliverables

One Markdown report, `docs/research/2026-10-13-system-study-report.md`, with these sections:

1. **Summary (one page):** the designs that satisfy R1 to R7, what each keeps central, and how confident the evidence allows us to be.
2. **Requirements matrix:** candidate systems and approaches against R1 to R7. Each cell says met, partly met or not met, with its evidence and read status.
3. **Findings by question (1 to 10):** what the sources show, where they disagree, and what is unknown.
4. **Design options for Chorus.** Two or three concrete architectures. For each:
   - the peer roles;
   - the shared state and where it lives;
   - the merge rule;
   - how synchronous and asynchronous modes run;
   - the holder-count rule;
   - failure behaviour;
   - what is reused against what is built;
   - risks.

   Labelled inference, with a recommendation the owner can accept or reject.
5. **Asynchronous algorithm options:** the evidence on each one's quality cost, and a candidate for Gate N1b.
6. **What to prototype before deciding:** small experiments that would settle open points, for example measured hole-punching success between the pilot participants' homes.
7. **Unverified leads.**
8. **Search log:** queries, sources, dates, and what was not covered.
