# W1a: discovery, bootstrap and NAT traversal (system study questions 1 and 2) · notes

Researcher notes for questions 1 and 2 of `docs/research/2026-10-13-system-study-brief.md`. Written 2026-10-13 (strand W1a). Sources S1 to S15; findings, unverified items, gaps and the query log follow them.

How these notes were made: papers fetched from arxiv.org with `curl` and converted with `pdftotext -layout`, one new directory per source under the session scratchpad (`sysstudy/sources/w1a/<id>/`); specifications, READMEs and docs fetched raw with `curl`; code read from shallow clones (`git clone --depth 1`). Nothing downloaded was run, built or installed. Search tools were used only to find sources; no number below comes from a search snippet or a WebFetch summary.

Classification used throughout (brief, "Classify what each candidate keeps central"): **(a)** a server we would run; **(b)** a public host for static files; **(c)** a public third-party network for live coordination or discovery (public DHT, public libp2p network, blockchain, public relays).

## Sources

### S1. Trautwein et al., DCUtR measurement campaign (one study, two arXiv versions)

- **Title:** "Large-Scale Measurement of NAT Traversal for the Decentralized Web: A Case Study of DCUtR in IPFS" (arXiv 2604.12484); earlier preprint of the same campaign: "Challenging Tribal Knowledge: Large Scale Measurement Campaign on Decentralized NAT Traversal (title punctuation adapted)" (arXiv 2510.27500).
- **Authors:** Dennis Trautwein, Cornelius Ihle, Moritz Schubotz, Corinna Breitinger (2604 only), Bela Gipp (University of Göttingen; FIZ Karlsruhe).
- **Dates and versions:** 2604.12484 v1, 14 Apr 2026 (only version; arXiv comment: accepted at ACM IMC '26, 12 to 16 Oct 2026, Karlsruhe). 2510.27500 v1, 31 Oct 2025 (only version). **Treat as one study:** same dataset, same 4.4M / 70% ± 7.1% / 97.6% numbers. Do not count twice.
- **Venue:** IMC '26 (per arXiv comment and the paper's ACM reference block, DOI 10.1145/3777912.3809138). 2510.27500 is a preprint.
- **Read status:** 2604.12484 v1 **full text** (body and appendix; figures not readable, values from text only). 2510.27500 v1: abstract plus its key numbers checked by grep (identical to 2604); body not read separately.
- **What it is:** the first large-scale measurement of libp2p's DCUtR hole punching in the production IPFS network.
- **Mechanism (§3):** Identify gives each peer its observed public address over an existing connection (STUN-like, no STUN server); AutoNAT asks other peers to dial back to classify the peer as public or private; libp2p also tries UPnP/PMP port mappings, which the paper calls "only advisory" (§3.1.2); a private peer holds a Circuit v2 reservation at a relay, a remote peer connects through that relay, and DCUtR exchanges CONNECT (addresses) and SYNC over the relay, then both sides dial simultaneously after half the measured relayed RTT. Coordination takes "only two network round trips" and under 500 bytes per direction over the relay (§3.2). Up to 3 attempts. "Connection Reversal" (one side simply dials the other's public address) is tried first if one peer looks public.
- **Numbers (all from 2604.12484 v1):**
  - **Campaign dates and scale:** measured **1 Dec 2022 to 1 Jan 2023** (§4.2), i.e. data are from 2022 although published in 2026. Over 6.25 million hole-punch results from 212 API keys, 148 sign-ups (§4.3); clients in 39 countries, remote peers in 167 (§4.3, Fig. 3); sample "skewed toward the U.S." (§4.3). 859 client networks and 86,769 remote-peer networks (§5.1).
  - **Exclusions before the success rate (§5.1, Fig. 4a):** 4.43 million results (70.9% of 6.25M) could be tied to one client network; 20.9% had "0 public networks" (the client advertised no public IP, e.g. no relay reservation yet or Identify could not find a public address); 8.1% had multiple public IPs. §6 says "approximately 29%" of data points were excluded because prerequisite stages (Circuit v2 relayed connection or Identify address discovery) failed. (inference) 20.9% + 8.1% = 29.0%, so the 29% appears to be these two groups, although the multi-IP group is an attribution problem as much as a connectivity failure.
  - **Headline:** "conditional success rate of 70% ± 7.1% for the hole-punching stage" (abstract), from a linear fit over per-network daily success rates (§5.2.1). Filters: no port mapping already in place; client contributed more than 1,000 data points from that network; outcome SUCCESS or FAILED (§5.2.1). The paper states the end-to-end probability of a direct connection "from scratch is lower" (§5.2.1, §6) and that the rate is "not indicative of any individuals' experienced success rate" (§5.2.1).
  - **Transport:** with transport restricted, TCP and QUIC both near 70% (§5.2.3, Fig. 8b); unrestricted, about 80% of successful connections end up on QUIC (§5.2.3, Fig. 8a).
  - **Attempts:** 97.6% of successful hole punches succeed on the first attempt (§5.2.3, Fig. 9a; samples 1,200,947 / 21,612 / 7,366 for attempts 1 / 2 / 3).
  - **Latency:** 50% of peers end at 70% or less of the relayed RTT after the punch; about 10% see a higher RTT (§5.2.1, Fig. 6a).
  - **Relay independence:** success rate shows "no measurable dependence on relay path location" (§5.2.2); peers by default reserve with two relays (§5.2.2).
  - **Port mappings:** active UPnP/PMP mappings give a much higher share of CONNECTION_REVERSED outcomes (§5.2.4, Fig. 9b); values only in a figure.
  - **Second-hand numbers it cites (not verified at their source; see "Could not verify"):** Halkes and Pouwelse 2011, about 64% of peers behind NATs that should allow punching and more than 80% of attempts between them succeeding; Guha and Francis 2005, 88% TCP success over 93 home NATs (§6); about 11% of peers behind endpoint-dependent-mapping (EDM, "symmetric") NATs per Halkes (§7.1); CGNAT deployments using EDM in 40% of cases as of 2016 per Richter et al. (§7.1).
  - **Symmetric NAT (§7.1):** the ~30% failures are attributed "in part" to EDM NATs; the birthday-paradox figures (64% with 256 ports each side, 99.9% with 2,048; 0.01% when both sides are EDM) are the authors' calculations citing Tailscale's blog, not measurements.
- **Limitations the paper states (§4.3.1, §6):** client fleet self-selected from IPFS/libp2p volunteers ("may lead to an overestimation" of success); honeypot discovery "systematically excludes peers behind highly restrictive NATs" (pre-filtered for reachability to a relay); cannot classify NAT type and "cannot distinguish single-NAT from CGNAT peers".
- **Central elements, classified:** in the protocol itself, relays are any public libp2p peer; in the IPFS deployment measured, these are public third-party peers, so **(c)**. The measurement infrastructure (honeypot, gRPC server) was a server the authors ran, **(a)** for them, not part of the protocol.
- **Fit with R1 to R7:** R3 (no third-party relays) **partly**: DCUtR needs a relayed connection for signalling only (under 500 bytes), so the relay can be one of our own machines, but it must be reachable. R1 **met** by the protocol design (no STUN/TURN server). Others not addressed.
- **How the setting differs from ours:** permissionless public IPFS network with ~7k IPFS peers and many public relays; random pairs of peers; 2022 data; US-skewed clients. We have 3 to 5 known home peers, possibly none publicly reachable, and want bulk transfers of 0.2 to 0.6 GB, not short exchanges.
- **Question it raises for us:** with only 3 to 5 pilot homes, a 70% per-pair average says little; what is the punch outcome for each specific pair of pilot homes, and does any home router accept a UPnP/PMP mapping (which the paper shows short-circuits the punch)?

### S2. Ford, Srisuresh and Kegel, "Peer-to-Peer Communication Across Network Address Translators"

- **Authors:** Bryan Ford, Pyda Srisuresh, Dan Kegel. **Date:** USENIX ATC 2005 (General Track); arXiv cs/0603074 v1, 18 Mar 2006 (only version).
- **Venue:** USENIX Annual Technical Conference, April 2005, Anaheim (arXiv record "Journal-ref" field, read on the abs page; also S1 reference [12]).
- **Read status:** **sections read:** abstract, §1, §2 (relaying, connection reversal), §3.1 to §3.2, §3.5 (multi-level NAT), §3.6 (UDP idle timeouts), §5 (properties of P2P-friendly NATs), §6 (evaluation, Table 1).
- **What it is:** the classic description of UDP and TCP hole punching through a rendezvous server, with a crowd-sourced test of NAT devices.
- **Mechanism:** both peers keep a session to a well-known rendezvous server S, which learns each peer's public and private endpoint; S forwards each peer's endpoints to the other; both send to each other's endpoints, which opens ("punches") mappings in their own NATs (§3.2). Works only if the NAT maps a private endpoint consistently to one public endpoint ("cone" behaviour, §5.1). Relaying through S "always works as long as both clients can connect to the server" (§2.2).
- **Numbers:**
  - NAT Check: 380 data points, 68 vendors plus OS-based NATs (§6.2). **UDP:** 310 of 380 (82%) translated consistently, "indicating basic compatibility with UDP hole punching"; UDP hairpin 80 of 335 (24%). **TCP:** 184 of 286 (64%) compatible (consistent translation and no RST to unsolicited SYNs); TCP hairpin 37 of 286 (13%) (§6.2, Table 1).
  - **What the 82% / 64% are:** device compatibility measured with test servers, not success rates of punches between real peer pairs. The sample is "self-selecting" and "not a random sample" (§6.2).
  - Some NATs have UDP idle timeouts "as short as 20 seconds", so keep-alives are needed (§3.6).
- **Multi-level NAT (§3.5, §5.4):** when both peers sit behind the same ISP-level NAT (what is now called CGNAT) plus their own home NATs, punching between them depends on the ISP NAT supporting hairpin translation, which was "unfortunately rare" (§5.4). Symmetric NATs break basic punching; port prediction works only "much of the time" (§5.1).
- **Central elements, classified:** the rendezvous server S is **(a)** if we ran it; in our setting it could be one of our reachable machines.
- **Fit with R1 to R7:** R1 **partly**: requires a reachable rendezvous point, which need not run around the clock but must be up when peers connect. R3 **partly**: relay fallback needs a reachable machine.
- **How the setting differs:** 2005 NAT devices; device tests, not peer-pair tests; no CGNAT or IPv6 data.
- **Question it raises:** are any pilot participants behind CGNAT (no public IPv4 on the home router), which removes UPnP and makes them unable to serve as relays or rendezvous points?

### S3. libp2p specifications (repository `libp2p/specs`)

- **Maintainers:** libp2p project (Protocol Labs and community). **Software/specification**, licence not checked (spec text).
- **Version read:** shallow clone at commit `c750236de43cd8b246a824b377dfdb26bae686db` (committed 2026-10-09). Each document's own revision is given below.
- **Read status:** files read: `kad-dht/README.md` (full; r2, 2022-12-09, "Recommendation"); `relay/circuit-v2.md` (lines 1 to 340: introduction, rationale, hop and stop protocols; r3, 2023-02-28); `relay/DCUtR.md` (full; r1, 2021-11-20); `connections/hole-punching.md` (full except the vision table); `autonat/autonat-v1.md` (overview, protocol; r1, 2023-02-16); `autonat/autonat-v2.md` (overview, protocol; r2, 2023-04-15, "Working Draft"); `pnet/Private-Networks-PSK-V1.md` (full; r0, 2017-02-17); `identify/README.md` (field list only).

**Kademlia DHT (`kad-dht/README.md`):**
- k = 20 (replication), α = 10 concurrent requests; distance is XOR of SHA-256 of keys (Definitions).
- **Client and server mode:** non-publicly routable nodes such as "laptops behind a NAT and firewall, should operate in _client mode_"; nodes add another node to their routing table "if and only if that node operates in _server mode_" (section "Client and server mode"). (inference) In a private DHT where every member is behind NAT, no member qualifies as a server under this guidance, so routing tables stay empty unless the implementation is forced into server mode.
- **Bootstrap process:** runs at startup and every 10 minutes by default; looks up a random ID per non-empty bucket plus its own ID; 10 s query timeout (section "Bootstrap process"). The spec does not say where the first peers come from; that is the application's configured bootstrap list.
- Records can be validated by an application `Validator` (e.g. a signature check) and conflicts resolved by `Select` (section "Entry validation").
- Provider records: republish every 22 h and expire after 48 h in IPFS (section "Content provider advertisement and discovery"), values the spec calls network-specific.

**Circuit Relay v2 (`relay/circuit-v2.md`):**
- A private peer A opens a connection to relay R and sends RESERVE; R grants a reservation with an expiry, its addresses and a signed voucher; A must keep the connection alive and refresh it. Another peer B dials A through R using `/p2p/<R>/p2p-circuit/p2p/<A>`; R bridges the streams; A and B then run their own security and multiplexing over it (sections "Interaction", "Reservation").
- **Limits are the relay's choice:** a `Limit {duration, data}` is optional; "When omitted, it indicates that the relay does not apply any limits"; 0 in either field means no limit (section "Reservation").
- **Access control:** a relay can refuse with `PERMISSION_DENIED` "because of peer filtering using ACLs" (sections "Reservation", "Connection Initiation"). (inference) A relay restricted to our own peer IDs is expressible in the protocol.
- The rationale states v1 relays needed "dedicated hosts with significant hardware and bandwidth costs", and v2 adds limited relaying and reservations so relays can be small (section "Rationale").
- Relay service is meant to be mounted "in public hosts, _after_ the reachability of the host has been determined through AutoNAT" (section "Rationale"). Implementations "should not" accept reservations or connections over already-relayed connections (notes in "Reservation" and "Connection Initiation"): a relay must itself be directly reachable; relays do not chain.

**DCUtR (`relay/DCUtR.md`):**
- Starts from an existing relayed connection. If the dialling peer advertises public addresses, the other side first tries a direct dial (unilateral upgrade). Otherwise CONNECT / CONNECT / SYNC, timer of half the relayed RTT, simultaneous TCP open or, for QUIC, random UDP packets every 10 to 200 ms (section "The Protocol", steps 1 to 5). Up to 3 attempts (step 6). On failure peers "can keep using the relay connection" (Introduction).
- Rationale: avoids "dedicated signaling servers" (Introduction).

**Hole-punching overview (`connections/hole-punching.md`):** the document "does not reflect the status quo" but a long-term vision (Overview). FAQ: when hole punching fails, peers keep the circuit relay v2 connection, which "is limited in both transfered bytes and time", and upper layers must accept that "full connectivity can not be guaranteed" (FAQ).

**AutoNAT:**
- v1: a peer asks others to dial its addresses; dials only to the requester's observed IP; requests over relayed connections must not be accepted; if more than 3 peers report success the node assumes it is public, if more than 3 report failure it assumes it is private (sections "AutoNAT Protocol").
- v2 (Working Draft): tests individual addresses, with a nonce; the server "SHOULD NOT dial any private address" (RFC 1918) (section "AutoNAT V2 Protocol").
- (inference, answered in S4) With only 3 to 5 peers, v1's "more than 3 peers" rule might never be satisfied; go-libp2p's code does not follow it literally (one successful dial-back suffices to become public; see S4).

**Private networks (`pnet/Private-Networks-PSK-V1.md`):** a private libp2p network is defined by a 256-bit pre-shared key known to all members; all traffic is additionally encrypted with XSalsa20 under that key; "Nodes of different private networks must not be able to connect to each other", including to the public network (sections "Interface", "Security Guarantees"). A safeguard environment variable `LIBP2P_FORCE_PNET=1` aborts if no key is set (section "Safeguard").

- **Central elements, classified:** none required by the specs themselves; in deployments the bootstrap list, relays and AutoNAT servers are whatever peers are configured. On the public network these are **(c)**; in a private (pnet) network of our own machines they are our own peers, which is not (a) unless one runs around the clock.
- **Fit with R1 to R7:** R1 **met** in principle (every role is a peer role); R3 **met** in principle with pnet plus our own relays, **provided at least one of our machines is publicly reachable** (relays and AutoNAT both need reachability). Bootstrap from intermittent home machines: **partly**, see Findings.
- **How the setting differs:** the specs assume a large network with many public peers (k = 20, AutoNAT "more than 3 peers").
- **Question it raises:** in a 3 to 5 peer private network, is any peer publicly reachable at all (public IPv4 with a port forward, or IPv6 without an inbound firewall)?

### S4. go-libp2p and go-libp2p-kad-dht (Go implementation)

- **Maintainers:** libp2p project. **Software.** Licence: `license.spdx_id` = MIT for both (GitHub API, queried 2026-10-13 17:27 TST).
- **Versions read:** go-libp2p shallow clone at `3c2c902122cb6fae3897f729a3dbb9d4665ae90d` (2026-09-21, tag v0.50.0); go-libp2p-kad-dht at `4a6670555386d4d3c26af40924f9d91f87034ddb` (2026-09-24).
- **Maintenance (GitHub API, 2026-10-13 17:27 TST):** go-libp2p `pushed_at` 2026-10-05T09:33:02Z, `releases/latest.tag_name` v0.50.0 `published_at` 2026-09-21T14:17:28Z, `archived` false, `open_issues_count` 303. go-libp2p-kad-dht `pushed_at` 2026-09-24T09:32:07Z, latest release v0.42.2 (2026-08-21T05:26:12Z), `open_issues_count` 56.
- **Read status:** files read: go-libp2p `p2p/protocol/circuitv2/relay/resources.go` (whole), `relay/acl.go` (interface), `relay/options.go` (options), `options.go` (lines 205 to 375, 420, 550), `p2p/host/relaysvc/relay.go` (reachability handler, by grep), `p2p/host/autonat/autonat.go` (lines 24 to 50, 92 to 107, 314 to 360), `p2p/transport/quic/transport.go` and `p2p/transport/webtransport/transport.go` (PSK check). kad-dht: `dht_bootstrap.go` (lines 12 to 45), `dht.go` (`fixLowPeers`, lines 496 to 560), `dht_options.go` (mode, `ProtocolPrefix`, `BootstrapPeers`), `internal/config/config.go` (`Defaults`, lines 135 to 167), `amino/` (protocol ID).
- **Mechanism and numbers:**
  - **Relay defaults:** `DefaultLimit()` is 2 minutes and 128 KiB of data per direction per relayed connection (`resources.go` lines 62 to 68); `DefaultResources()`: reservation TTL 1 h, 128 reservations, 16 circuits per peer, 2,048-byte buffers, 8 reservations per IP, 32 per ASN (lines 46 to 60). (inference) With defaults, a relayed connection cannot carry a 0.2 to 0.6 GB update; it can carry DCUtR signalling.
  - **Relay limits are configurable:** `WithLimit`, `WithResources`, and `WithInfiniteLimits()` which sets the limit to nil (`relay/options.go` lines 18 to 43); `WithACL(ACLFilter)` with `AllowReserve(peer, addr)` and `AllowConnect(src, srcAddr, dest)` (`relay/acl.go` lines 10 to 16, `options.go` 46 to 51). (inference) A relay that serves only our peer IDs and carries unlimited data is configurable in go-libp2p.
  - **Relay service only on public hosts:** `EnableRelayService` runs a circuit v2 relay only "if we detect that we're publicly reachable" (`options.go` lines 292 to 300); the relay manager reacts to `EvtLocalReachabilityChanged` (`relaysvc/relay.go` lines 47 to 70). `ForceReachabilityPublic()` overrides AutoNAT (`options.go` line 349).
  - **AutoRelay with static relays:** `EnableAutoRelayWithStaticRelays(static []peer.AddrInfo)` advertises relay addresses "when it detects that the node is publicly unreachable" (`options.go` lines 322 to 330). (inference) Our own reachable machines can be named as the only relays.
  - **AutoNAT v1 in code differs from the spec's "more than 3 peers":** one successful dial-back switches the status to public at once ("Aggressively switch to public"), and with a single AutoNAT peer, confidence grows per failure up to `maxConfidence = 3` (`autonat.go` lines 24, 42 to 46, 318 to 332). The AutoNAT service (answering others' dial-back requests) is enabled at construction when a dialer is configured and reachability is not forced private (lines 92 to 99), disabled when the host concludes it is private (lines 345 to 350), and re-enabled if the status falls back to unknown (lines 359 to 366). (inference) In a pool where no machine is public, peers answer each other at first, the dial-backs to NATed peers fail, each host concludes it is private and switches its service off; a peer joining later may then find nobody answering. Either way no host becomes public, so none starts a relay service.
  - **Private networks:** `PrivateNetwork(psk)` option (`options.go` lines 209 to 218). **The QUIC and WebTransport transports refuse a PSK:** "QUIC doesn't support private networks yet" (`p2p/transport/quic/transport.go` lines 74 to 76; same for WebTransport lines 98 to 100). (inference) A go-libp2p pnet pool runs on TCP (and WebSocket) only; S1 found TCP and QUIC punch success similar, so this costs little on punching but it rules out QUIC.
  - **kad-dht bootstrap:** the library's `DefaultBootstrapPeers` are five public IPFS/libp2p bootstrap addresses (`dht_bootstrap.go` lines 12 to 36), but the `Defaults` config sets no bootstrap peers and an in-memory datastore (`internal/config/config.go` lines 140 to 166); `BootstrapPeers(...)` and `BootstrapPeersFunc(func)` set the list "to seed and refresh our Routing Table if it becomes empty" (`dht_options.go` lines 324 to 343). `ProtocolPrefix("/myapp")` gives `/myapp/kad/1.0.0` instead of `/ipfs/kad/1.0.0` (`dht_options.go` lines 170 to 178; `amino` protocol ID `/ipfs/kad/1.0.0`), i.e. a separate DHT on the same transport.
  - **Recovery when the routing table empties (`fixLowPeers`, `dht.go` lines 517 to 560):** at 10 or fewer routing-table peers (`minRTRefreshThreshold` = 10, `dht_bootstrap.go` line 18) it adds currently connected peers; if the table is empty it dials the bootstrap list in random order until 2 succeed (`maxNBoostrappers`). A TODO in the code says it should "use non-bootstrap peers we knew of from previous snapshots" (issue #387): **no persisted routing table is used as of this commit.** If every bootstrap peer is down and no other peer is connected, the function returns with nothing. `fixLowPeers` re-runs every 2 minutes (`periodicBootstrapInterval`, `dht_bootstrap.go` line 20, used as a ticker in `runFixLowPeersLoop`, `dht.go` lines 497 to 510), so a peer retries its bootstrap list periodically while it has few peers.
  - **Modes:** `ModeAuto` (default) switches between client and server on reachability events; `ModeServer` forces server; `ModeAutoServer` acts as server while reachability is unknown (`dht_options.go` lines 28 to 36, 126).
- **Central elements, classified:** none required. The default IPFS bootstrap list, if used, is **(c)**. In a pnet with our own bootstrap list: our own peers, not (a) unless kept on around the clock.
- **Fit with R1 to R7:** R1 **met** (all peer roles). R3 **met** with static relays and pnet if one of our machines is reachable; **not met** for bulk transfer through a relay with default limits (must be raised). R2 bootstrap from intermittent peers: **partly** (no routing-table persistence; the application must supply a fresh list via `BootstrapPeersFunc`).
- **Setting difference:** built and tuned for the public IPFS network (Amino DHT).
- **Question it raises:** would we write our client in Go (or call a Go daemon from Python, as Hivemind does)? The Chorus code base is Python (D3).

### S5. rust-libp2p (Rust implementation)

- **Maintainers:** libp2p project. **Software.** `license.spdx_id` = MIT (GitHub API, 2026-10-13 17:27 TST).
- **Version read:** shallow clone at `a035aad0566fd8b3faa298a3194e443818f9b354` (2026-10-13). Crate versions in the tree: `libp2p` 0.57.0, `libp2p-relay` 0.22.0, `libp2p-kad` 0.49.0, `libp2p-dcutr` 0.15.0, `libp2p-autonat` 0.16.0, `libp2p-pnet` 0.27.0 (each `Cargo.toml` line 6).
- **Maintenance (GitHub API, 2026-10-13 17:27 TST):** `pushed_at` 2026-10-13T14:11:00Z; `releases/latest.tag_name` v0.57.0, `published_at` 2026-09-11T21:34:37Z; `open_issues_count` 303; `archived` false.
- **Read status:** files read: `protocols/relay/src/behaviour.rs` (Config and `Default`, lines 54 to 165); `protocols/kad/src/behaviour.rs` (config defaults line 235, `bootstrap()` lines 975 to 996, `set_mode` lines 1115 to 1130, `determine_mode_from_external_addresses` lines 1168 to 1180).
- **Numbers:** relay `Config::default()`: `max_circuit_duration` 2 min, `max_circuit_bytes` 128 KiB, `max_reservations` 128, `reservation_duration` 1 h, plus per-peer and per-IP rate limits (lines 124 to 165). Kad: periodic bootstrap every 5 min (line 235); `bootstrap()` returns `NoKnownPeers` if the routing table is empty (lines 984 to 996); without a confirmed external address the behaviour switches itself to client mode (lines 1168 to 1180), and `set_mode(Some(Mode::Server))` forces server mode (lines 1118 to 1123).
- **Central elements, classified:** none required (same as S4).
- **Fit:** as S4. DCUtR, relay, AutoNAT and pnet crates exist; whether rust-libp2p's pnet works over QUIC was **not checked**.
- **Setting difference / question:** same as S4.

### S6. py-libp2p (Python implementation)

- **Maintainers:** libp2p project. **Software.** `license.spdx_id` = NOASSERTION (GitHub API, 2026-10-13 17:27 TST); the repository root holds `LICENSE-APACHE` (Apache License 2.0) and `LICENSE-MIT` (MIT), both "Copyright (c) 2018 Zixuan Zhang" (first lines read with `git show HEAD:<file>`), i.e. dual-licensed.
- **Version read:** clone at `79985430f45a64b605cfc233d42f41103dedeb04` (2026-10-02); `pyproject.toml` version 0.8.0. (The Windows checkout failed on long test-file names; README and file list read with `git show` / `git ls-tree`.)
- **Maintenance (GitHub API, 2026-10-13 17:27 TST):** `pushed_at` 2026-10-02T09:02:49Z; `releases/latest.tag_name` v0.8.0, `published_at` 2026-09-26T13:00:48Z; `open_issues_count` 75.
- **Read status:** files read: `README.md` (feature tables); file list of `libp2p/relay/circuit_v2/` and `libp2p/security/pnet/`.
- **What the README claims:** "moved beyond its experimental roots and is steadily progressing toward production readiness" (README line 15). Feature table marks circuit relay v2, AutoNAT, hole punching, kad-dht, bootstrap, mDNS, rendezvous, TCP and QUIC as "✅ Done" (README lines 33 to 97). A `libp2p/security/pnet/` module exists (file list). **These are the maintainers' claims; interoperability with go/rust implementations and maturity were not verified.**
- **Fit:** would keep Chorus in Python (D3) without a Go daemon; maturity is the open question.
- **Question:** has py-libp2p's DCUtR been tested against go-libp2p or rust-libp2p peers in the wild?

### S7. Hivemind (DHT and libp2p daemon)

- **Maintainers:** learning-at-home. **Software.** `license.spdx_id` = MIT (GitHub API, 2026-10-13 17:27 TST).
- **Version read:** clone at `4bd43b77895019b20d18d81d0d0c1a5ab9a10847` (2026-01-04). Its libp2p daemon: fork `learning-at-home/go-libp2p-daemon` tag `v0.5.0.hivemind1`, commit `3762261d0b87aaed8526bc0c5237c4715a798904` (2023-11-21), built against go-libp2p v0.32.1 and go-libp2p-kad-dht v0.25.1 (`go.mod` lines 12 to 13).
- **Maintenance (GitHub API, 2026-10-13 17:27 TST):** `pushed_at` 2026-01-11T21:13:45Z; `releases/latest.tag_name` 1.1.12, `published_at` 2026-01-03T07:41:24Z; newest commit 2026-01-04; `open_issues_count` 94 (this API counter includes pull requests). Consistent with prior-work.md §6 (queried 2026-10-07): low-activity maintenance, not archived.
- **Read status:** files read: `setup.py` (lines 14 to 30, p2pd version and binary hashes); `hivemind/p2p/p2p_daemon.py` (lines 40 to 240: class docstring, `create()` parameters, daemon arguments); `hivemind/dht/node.py` (lines 40 to 250: class docstring, parameters, bootstrap); `hivemind/dht/protocol.py` (RPC names by grep); `docs/user/dht.md` (lines 78 to 140, "Running across the Internet"); `README.md` (OS support lines 82 to 90). Daemon fork: `p2pd/main.go` (flags lines 70 to 116, 197 to 263, 336 to 372), `relay.go` (lines 95 to 160).
- **Mechanism:**
  - Hivemind's DHT is **its own Kademlia-style protocol** (ping, bulk store, find) implemented in Python over libp2p streams (`node.py` docstring lines 44 to 62; `protocol.py` `rpc_ping`, `rpc_store`, `rpc_find`), not libp2p's kad-dht. Defaults: `bucket_size` 20, `num_replicas` 5, `wait_timeout` 3 s (`node.py` lines 103 to 124). Values carry expiration times; the DHT is designed for "temporary metadata" that does not need "persistence on shutdown" (`node.py` lines 47 to 50).
  - The transport is a separate Go process, `p2pd`, launched by `hivemind.P2P` (`p2p_daemon.py` lines 40 to 54, 196 to 240). Prebuilt binaries are listed only for darwin-amd64, darwin-arm64, linux-amd64, linux-arm64 (`setup.py` lines 22 to 27); the README calls Windows "experimental" via WSL (README lines 82 to 90).
  - `P2P.create()` defaults: `host_maddrs=("/ip4/127.0.0.1/tcp/0",)` (listens on localhost only), `auto_nat=True`, `nat_port_map=True`, `use_relay=True`, `use_auto_relay=False`, `use_ipfs=False`, `dht_mode="server"` (`p2p_daemon.py` lines 84 to 106). `use_ipfs=True` means "Bootstrap to IPFS (incompatible with initial_peers)" (line 131).
  - The daemon fork: `-autonat` also turns on `EnableHolePunching()` (`main.go` lines 343 to 346); relay service is on by default when relaying is enabled (`-relayService` default true, line 95) with **raised limits: 4 GiB per direction (`relayDataLimit` 1<<32) and 30 minutes per relayed connection, 16 MiB buffers** (lines 96 to 100; applied in `relay.go` lines 147 to 160). Auto-relay candidates: "by default, use bootstrap peers as trusted relays" (flag text, line 94), plus closest peers from the DHT when relay discovery is on (`relay.go` lines 100 to 135).
- **Bootstrap and failure (`node.py` lines 219 to 245):** with `initial_peers`, the node pings them; if none responds, it raises "DHTNode bootstrap failed: none of the initial_peers responded to a ping" unless `ensure_bootstrap_success=False`. Without `initial_peers` the node starts a new DHT of its own.
- **Docs on NAT (`docs/user/dht.md`, "Running across the Internet"):** initial peers "can be any computers with a public IP address that are always online"; peers behind a restrictive firewall may use `client_mode=True`; the experimental alternative `use_ipfs=True` lets nodes connect "even if all of them are behind NAT" but "may be unreliable and depend heavily on the availability of public IPFS nodes".
- **Central elements, classified:** initial peers recommended to be always-on public machines: **(a)** if we ran one around the clock (conflicts with R1), otherwise our intermittent peers; `use_ipfs=True` relies on the public IPFS network: **(c)**. The binary download is from GitHub releases: **(b)**.
- **Fit with R1 to R7:** R1 **partly** (works with intermittent bootstrap peers only if at least one listed initial peer is up and reachable at join time). R3 **partly**: its relays are its own peers with large limits, but they must be publicly reachable; the only documented all-NAT mode is (c). Windows support **not met** natively.
- **Setting difference:** designed for volunteer swarms with some public machines (the docs assume them).
- **Question:** does any pilot participant have a public IPv4 or IPv6 address that could host a Hivemind-style initial peer and relay when online?

### S8. Petals (bootstrap peers only)

- **Maintainers:** bigscience-workshop. **Software.** `license.spdx_id` = MIT (GitHub API, 2026-10-13 17:27 TST).
- **Version read:** clone at `22afba627a7eb4fcfe9418c49472c6a51334b8ac` (2024-08-25); wiki at `adb7a1aac5c785f3cd728c65b4cbcd9a333904c8` (2023-11-27).
- **Maintenance (GitHub API, 2026-10-13 17:27 TST):** `pushed_at` 2024-09-07T11:54:28Z; latest release v2.2.0 (2023-09-06T17:29:56Z); `open_issues_count` 114. No change since prior-work.md §6.
- **Read status:** files read: `src/petals/constants.py` (whole); `src/petals/server/server.py` (lines 128 to 160); `src/petals/server/reachability.py` (lines 20 to 78); `src/petals/cli/run_server.py` (flags by grep); wiki page `Launch-your-own-swarm.md` (whole).
- **Mechanism:** the public swarm's `PUBLIC_INITIAL_PEERS` are two DNS names (`bootstrap1.petals.dev`, `bootstrap2.petals.dev`) and two fixed IPv4 addresses (`constants.py` lines 3 to 13). A server first probes whether up to 5 swarm peers can reach it directly (threshold 0.5) and, if not, joins the DHT in client mode reachable "via relays" with `use_auto_relay=True` (`server.py` lines 136 to 148; `reachability.py` lines 55 to 78). A central reachability API (`https://health.petals.dev`) is consulted only for the public swarm (`constants.py` line 16; `server.py` line 157).
- **Private swarm (wiki "Launch your own swarm", Step 2):** recommends "a few CPU-only machines that are always online" as bootstrap peers, which "can also serve as libp2p relays" for servers behind NAT; new peers can join "as long as at least one of their initial peers is alive"; a bootstrap peer needs "a public IP address" or port forwarding to be reachable from outside; a fixed `--identity_path` keeps its address stable. Without bootstrap machines, `--new_swarm` on the first server and its address as `--initial_peers` for the rest (Step 3).
- **Central elements, classified:** public swarm: bootstrap servers and health API run by the Petals team, **(c)** from our point of view. Private swarm: always-on bootstrap/relay machines, **(a)** if we ran them around the clock.
- **Fit with R1 to R7:** R1 **not met** as documented (recommends always-on bootstrap machines); R3 **met** in principle (relays are own peers) if reachable.
- **Setting difference:** inference and fine-tuning swarm; maintenance stopped in 2024.
- **Question:** the same as S7; Petals adds no mechanism beyond Hivemind's for all-NAT pools.

### S9. iroh (n0-computer)

- **Maintainers:** n0 (number 0). **Software.** `license.spdx_id` = Apache-2.0 (GitHub API, 2026-10-13 17:27 TST); the repository root holds both `LICENSE-APACHE` and `LICENSE-MIT`; `iroh-relay/` also has `LICENSE-BSD3`.
- **Version read:** shallow clone at `d8c93d8bd60ca704d1c51debc257ebcccf69da35` (2026-10-09); `iroh` and `iroh-relay` crates version 1.3.0 (`Cargo.toml` line 3). Docs pages fetched raw as `.md` from docs.iroh.computer on 2026-10-13 17:31 TST (no version marker on the pages).
- **Maintenance (GitHub API, 2026-10-13 17:27 TST):** `pushed_at` 2026-10-12T07:23:16Z; `releases/latest.tag_name` v1.3.0, `published_at` 2026-09-28T19:26:13Z; newest commit 2026-10-09; `open_issues_count` 175; `archived` false.
- **Read status:** files read: `README.md` (hole-punching paragraph), `iroh/src/defaults.rs` (whole), `iroh/src/endpoint.rs` (`RelayMode` lines 1997 to 2011; `Builder::empty()` lines 175 to 200), `iroh/src/endpoint/presets.rs` (whole), `iroh/src/address_lookup.rs` (module docs, lines 1 to 75), `iroh-relay/README.md` (whole), `iroh-relay/src/main.rs` (config `limits`, lines 141, 362, 511 to 540), `iroh-dns-server/README.md` (first 30 lines). Docs: `concepts/holepunching.md`, `concepts/relays.md`, `iroh-services/relays/public.md`, `iroh-services/relays/self-hosted.md` (whole), `concepts/discovery.md` (first half). Not read: `add-a-relay.md`, `deployment/dedicated-infrastructure.md` (downloaded only).
- **Mechanism:** endpoints are identified by public keys and connect over QUIC. Both peers first connect to a relay; the relay sees each peer's public address and port; peers exchange addresses through the relay and send UDP packets to each other simultaneously; if this fails, traffic stays on the relay (docs `concepts/holepunching.md` steps 1 to 4). Unlike libp2p Circuit v2, **iroh relays carry all traffic when punching fails** ("Encrypted traffic fallback", `concepts/relays.md`), end-to-end encrypted.
- **Defaults (what runs out of the box):**
  - The `N0` preset sets the default relay map and the DNS/pkarr address lookup "configured to use the n0.computer dns server" `iroh.link` (`presets.rs` lines 85 to 140). Default relays are four n0-run hosts: `use1-1`, `usw1-1`, `euc1-1`, `aps1-1` `.relay.n0.iroh.link` (`defaults.rs`, module `prod`). `RelayMode::Default` = "production relay servers from n0" (`endpoint.rs` line 2003).
  - `Builder::empty()` has "no address lookup services, and `RelayMode::Disabled`" (`endpoint.rs` line 193); `RelayMode::Custom(RelayMap)` points at our own relays (line 2010); `RelayMode::Disabled` means "neither listening nor dialing relays will be available" (lines 2000 to 2002). `N0DisableRelay` keeps n0 DNS lookup but disables relays (`presets.rs` lines 142 to 184).
  - Address lookup options: `MemoryLookup` (addresses supplied by the application out of band), DNS via pkarr (n0 runs a public instance), and separate crates for mDNS (local network) and the BitTorrent Mainline DHT (`address_lookup.rs` module docs lines 33 to 51; `concepts/discovery.md`). "Tickets" carry endpoint ID, socket addresses and relay URL but "expire: People change networks or relays" (`concepts/discovery.md`).
- **Self-hosting:**
  - Relay: `iroh-relay` server binary; "A CLI for running your own relay server" (`iroh-relay/README.md`). Access control by `access = "everyone"`, an allowlist or denylist of endpoint IDs, shared tokens, or an HTTP auth callback (README "Access control"). In the server config, client rate `limits` default to none (`main.rs` line 362). The self-hosted docs page is "maintained by the community" and says full config documentation "is not published currently"; its example uses a DNS hostname and Let's Encrypt on ports 80 and 443 (`iroh-services/relays/self-hosted.md`). `--dev` mode serves plain HTTP without QUIC address discovery (`iroh-relay/README.md` "dev mode").
  - Discovery: `iroh-dns-server` is "a server that functions as a pkarr relay and DNS server" (README lines 1 to 20); self-hostable but it is a server.
- **Numbers:** "roughly 9 out of 10 network configurations allow a direct connection" (docs `concepts/holepunching.md`; same claim in `concepts/relays.md`). **No measurement method, dataset or date is given on these pages; it is a vendor claim, not a measurement** (see "Could not verify"). Public n0 relays "Rate-limit traffic", carry "no uptime or performance guarantees", and are for "development and hobby use only" (`concepts/relays.md`; `iroh-services/relays/public.md`); rate values not stated.
- **Central elements, classified:** default relays and default DNS/pkarr lookup: **(c)** (n0's public infrastructure). Self-hosted `iroh-relay` on one of our machines: our own peer if it runs only when that machine is on; **(a)** if kept up around the clock. Mainline-DHT lookup crate: **(c)**. mDNS: local network only. `MemoryLookup` plus addresses published as a file on a public host: **(b)** (inference).
- **Fit with R1 to R7:** R1 **met** only if configured away from the N0 preset (`Builder::empty()` plus `RelayMode::Custom` plus `MemoryLookup`); the out-of-the-box preset relies on n0. R3 **met** with `RelayMode::Custom` pointing at our own relays, and those relays can carry bulk traffic; **but a relay must be reachable**, and the documented self-hosted setup assumes a public hostname and TLS certificate. Language: Rust (bindings not checked).
- **Setting difference:** designed for application developers with servers available; the docs push production users to managed relays.
- **Question it raises:** can a pilot participant's home machine run `iroh-relay` reachably (public IP, port forward, a DNS name or a self-signed certificate), and does iroh still punch holes when the relay is in `--dev` HTTP mode?

### S10. BitTorrent Mainline DHT, BEP 5 (mechanism only; D37 excludes joining it)

- **Authors:** Andrew Loewenstern, Arvid Norberg. **Specification** (BitTorrent Enhancement Proposal), status Accepted, created 31 Jan 2008, last modified 21 Jan 2020, version `aa944d9e2faf989cbb4b1bad5ec130b9f22631d9` (page header).
- **Link:** https://www.bittorrent.org/beps/bep_0005.html, fetched 2026-10-13 17:32 TST, tags stripped with a local script.
- **Read status:** full text (overview, routing table, BitTorrent protocol extension, torrent file extensions, KRPC overview, `announce_peer` with `implied_port`).
- **Mechanism:** Kademlia over UDP, 160-bit IDs, XOR distance; buckets of K = 8 ("currently eight"); a node is "good" if it responded within the last 15 minutes; buckets unchanged for 15 minutes are refreshed (section "Routing Table"). Peers are found with `get_peers` and announced with `announce_peer`, guarded by a token tied to the querier's IP (Overview). **Bootstrap and recovery:** "The routing table should be saved between invocations of the client software"; new clients with an empty table "will need the contacts included in the torrent file" (`nodes` key: the K closest nodes or "a known good node such as one operated by the person generating the torrent"); routing tables also fill from peers met through ordinary BitTorrent connections (PORT message) (sections "Routing Table", "BitTorrent Protocol Extension", "Torrent File Extensions"). `implied_port` lets peers behind NAT announce the UDP source port seen by the receiver (section "announce_peer").
- **Central elements, classified:** the public Mainline DHT is **(c)**. The spec's ideas (persisted routing table; seed contacts shipped inside a static file) are mechanisms, not dependencies.
- **Fit with R1 to R7:** joining it violates the owner's D37 choice (c). As a mechanism: persisting the table and shipping seed contacts in a static file both address intermittent bootstrap peers (inference).
- **Setting difference:** millions of nodes (not measured here), so any saved contact is likely to have live neighbours; with 3 to 5 nodes, a saved table is just the member list.
- **Question:** could our run's "starting configuration" (R2) carry the members' last-known addresses, as a torrent's `nodes` key does?

### S11. libp2p mDNS and rendezvous specifications (same clone as S3)

- **Read status:** `discovery/mdns.md` (overview; Working Draft r2, 2021-10-12); `rendezvous/README.md` (overview, use cases, registration lifetime; Working Draft r3, 2021-07-12).
- **mDNS:** peers "discover each other when on the same local network", with zero configuration; service name `_p2p._udp.local` (Overview). Local network only.
- **Rendezvous:** peers REGISTER under a namespace at a rendezvous point and others DISCOVER them; registrations carry an optional TTL; "Any node implementing the rendezvous protocol can act as a rendezvous point" (Overview, "Registration Lifetime").
- **Classified:** mDNS: none (local only). Rendezvous point: **(a)** if a dedicated always-on node; a peer role otherwise; it must be reachable.
- **Fit:** rendezvous is equivalent to a bootstrap peer with a registry; it does not remove the need for a reachable, online node (inference).

### S12. IETF RFC 4787, RFC 6888 and RFC 7021 (NAT and CGN behaviour)

- **RFC 4787** (Audet, Jennings; BCP 127, January 2007), "NAT Behavioral Requirements for Unicast UDP". **Read status:** section 4.1 (mapping behaviour, REQ-1). "REQ-1: A NAT MUST have an 'Endpoint-Independent Mapping' behavior"; failure "will force the use of a UDP relay" (§4.1).
- **RFC 6888** (Perreault et al.; BCP 127, April 2013), "Common Requirements for Carrier-Grade NATs (CGNs)". **Read status:** §3 REQ-1 to REQ-7. A CGN "MUST fulfill" RFC 4787's requirements (REQ-1), so endpoint-independent mapping applies to CGNs too; endpoint-independent filtering is "RECOMMENDED" (REQ-7); a CGN must support per-subscriber port limits (REQ-4).
- **RFC 7021** (Donley et al., CableLabs; Independent Submission, Informational, September 2013), "Assessing the Impact of Carrier-Grade NAT on Network Applications". **Read status:** §2.1.3 "Case 3: Two Clients, Two Home Networks, Single Service Provider" (test topology), §3.1 "Dropped Services". **Setting:** lab tests of NAT444 and DS-Lite, not field measurement. Findings: several peer-to-peer applications "failed in both the NAT444 and Dual-Stack Lite environments" (Xbox peer-to-peer gaming, PJSIP calls); BitTorrent seeding from inside the CGN to an outside leecher "did not work" directly; FTP to servers "behind two layers of NAT" failed (§3.1).
- **Classified:** not systems; standards and lab results.
- **Fit / question:** (inference) a participant behind CGN cannot run a reachable relay or bootstrap peer on IPv4 at all, because port forwarding on the home router does not reach through the ISP's NAT. Does each pilot home have a public IPv4, or IPv6?

### S13. Richter et al., "A Multi-perspective Analysis of Carrier-Grade NAT Deployment"

- **Authors:** Philipp Richter, Florian Wohlfart, Narseo Vallina-Rodriguez, Mark Allman, Randy Bush, Anja Feldmann, Christian Kreibich, Nicholas Weaver, Vern Paxson. **Venue:** ACM IMC 2016, Santa Monica (paper header). **Copy read:** author-hosted PDF `https://www.icir.org/vern/papers/cgn-imc16.pdf` (fetched 2026-10-13 17:33 TST; the conference URL tried first returned HTML). Not an arXiv paper.
- **Read status:** sections read: abstract, §1 summary of results, §5 (CGN penetration, lines around Figure 7 text), §6.5 "Flow-Mapping Properties of CGNs" (mapping timeouts, Figure 12; mapping types, Figure 13), start of §7.
- **Setting:** BitTorrent DHT crawl (one week from 3 March 2016) and Netalyzr sessions (TTL test from September 2014, 38K sessions; STUN test from October 2015, 23K sessions) (§4, §6.5). AS-level fractions, not per-subscriber.
- **Numbers:**
  - CGN penetration of 17 to 18% of all eyeball ASes (non-cellular) and "more than 90%" of cellular ASes (abstract; §5 gives 13.3% of all non-cellular ASes, 17 to 18% of non-cellular eyeball ASes, over 92% cellular).
  - **Mapping types (§6.5, Figure 13):** "less than 2% of the tests showed CPE NATs with very restrictive symmetric NATs"; "11% of non-cellular CGN ASes whose most permissive mapping type is symmetric", including "many popular large European ISPs"; cellular CGN ASes bimodal, "40% symmetric" and "20% full cone".
  - **Mapping timeouts (§6.5, Figure 12):** "74% of detected NATs expire idle UDP state after 1 minute or less", range 10 s to 200 s; median 65 s for cellular CGNs, 35 s for non-cellular CGNs; CPE NATs predominantly 65 s.
  - Some ISPs allocate "as little as 512 ephemeral ports per subscriber", "up to 128 subscribers per public IP address" (§7).
- **Correction to S1:** S1 (§7.1) cites this paper for "CGNAT deployments, which employed EDM translation in 40% of cases as of 2016". At the source, **40% symmetric applies to cellular CGN ASes; for non-cellular CGN ASes the figure is 11%**, and the unit is ASes, not deployments or connections. For home broadband (our setting) the relevant number is 11% of CGN-using non-cellular ASes having symmetric mapping as their most permissive type.
- **Classified:** not a system.
- **Fit / question:** (inference) home connections without CGN mostly have non-symmetric NATs (under 2% symmetric CPE in 2015), so the main risks for a pilot are CGN, restrictive filtering and timing, not the home router alone. Which pilot ISPs use CGN (Turkish ISPs included), and with what mapping?

### S14. ProbeLab, DCUtR NAT hole-punching study (blog post and project report)

- **Authors:** ProbeLab (blog byline: Dr. Sergi Rene). **Date:** blog post 3 August 2026; report in repository `probe-lab/dcutr-project`, `docs/dcutr-final-report.md`, newest commit `87641e88fbf2b72ce6ada7e0a59d13b3f21ab878` (`commit.committer.date` 2026-08-04T09:12:43Z; repo `pushed_at` 2026-09-17T22:05:29Z; `license.spdx_id` null; GitHub API queried 2026-10-13 17:35 TST). **Venue:** project report and blog, not peer-reviewed.
- **Links:** https://probelab.io/blog/can-libp2p-punch-through-nats/ (fetched with curl 2026-10-13 17:35 TST, tags stripped); https://raw.githubusercontent.com/probe-lab/dcutr-project/HEAD/docs/dcutr-final-report.md (fetched 17:35 TST).
- **Read status:** blog: full text. Report: sections read: "Live network measurement" (Setup, Methodology), "The readiness ceiling is operational", "Outcomes", "Implementation and spec audit findings", "Conclusions". Sub-documents (`nat-classification.md`, `dcutr-testbed.md`, `dcutr-audit.md`) not read.
- **What it is:** a non-cooperative measurement on the live IPFS Amino DHT that classifies peers by RFC 4787 mapping and filtering, then hole-punches DCUtR-eligible peers; plus a go-libp2p / rust-libp2p testbed and spec audit.
- **Setting:** data collected **2026-05-25 to 2026-05-29**; 50,052 distinct peers (report "Setup"). Probers ran in three cloud regions (us-east-1, ap-northeast-1, eu-central-1); **the DCUtR prober sat behind an nftables port-restricted-cone filter** (report "Setup"). So each measured pair is (a cloud prober with a simulated port-restricted cone NAT) × (a real IPFS peer), not two home peers.
- **Numbers (blog "Results TL;DR" and tables; same values in the report):**
  - NAT census of 43,684 classifiable peers: directly reachable (public + full cone) 8.3%; port-restricted cone 19.6%; APDF filtering with mapping unresolved 42.5%; symmetric (confirmed address-and-port-dependent mapping) 3.9% (blog table "NAT distribution"). Report summary: "~62% APDF, ~4% symmetric, ~8% directly reachable" ("Outcomes").
  - DCUtR success per class (eligible peers only, i.e. advertising DCUtR and holding a relay reservation): port-restricted cone **82.9%** (3,042 of 3,669 probed); APDF mapping-unresolved 37.0% (1,126 of 3,042); symmetric **39.7%** (213 of 536), which the authors doubt and attribute plausibly to misclassification or network changes; unresolved 49.5% (blog table "DCUtR hole-punch success per NAT class").
  - **Readiness ceiling:** of 16,151 NAT-restricted peers advertising DCUtR, only 10,281 (64%) held a relay reservation; 5,870 (36%) never did, concentrated in particular fleets (a game company's kubo build, the official kubo Docker image, likely mobile `gobind` clients) (report "The readiness ceiling is operational").
  - Testbed: go-libp2p and rust-libp2p "interoperate at 100% across every punchable EIM × EIM regime" (72-cell × 3-run matrix); three minor audit findings, including that reject-style NATs (sending RST to unsolicited SYNs) are "incompatible with hole-punching over TCP (QUIC is immune)" (report "Implementation and spec audit findings").
  - On other stacks: holepunch.to and iroh claim rates "at times above 90%", but "we haven't seen a study backing those numbers" (blog "Where this leaves DCUtR").
- **Agreement with S1:** the report states that both studies "converge on the same aggregate hole-punch rate" (~70%) and on TCP ≈ QUIC, with different sampling biases ("Outcomes"). It adds that the 36% reservation gap "sits upstream of Trautwein's 'conditional' framing" ("Outcomes").
- **Central elements, classified:** as S1 (public IPFS relays are (c) in that deployment); the measurement infrastructure was the authors' cloud servers.
- **Fit with R1 to R7:** as S1. It strengthens the evidence that DCUtR works for the common home NAT class (port-restricted cone) and fails mostly for symmetric mapping.
- **Setting difference:** one side was a cloud machine with a simulated NAT; our pairs would be two real home NATs, possibly behind CGN. Short campaign (5 days).
- **Question:** what NAT class does each pilot home fall into (mapping and filtering, on TCP and UDP), measured the same way?

### S15. Psyche (Nous Research): networking layer only

- **Maintainers:** PsycheFoundation (Nous Research). **Software.** `license.spdx_id` = Apache-2.0; `pushed_at` 2026-03-24T20:46:58Z (GitHub API, 2026-10-13 17:36 TST).
- **Version read:** shallow clone, HEAD `0bdb13d94a05675da93d69ffa5d4c4e5a680736c` (2026-03-20). Checkout failed on Windows long paths; files read with `git show` / `git grep`.
- **Read status:** files read: `shared/network/src/lib.rs` (lines 105 to 106, 135 to 147, 335 to 385, 984 to 1010), `shared/client/src/cli.rs` (lines 55 to 72), `shared/network/src/local_discovery.rs` (lines 1 to 30), `Cargo.toml` (iroh versions). Only the networking layer; the ledger and training parts belong to other strands.
- **Mechanism:** Psyche's peer network is built on iroh 0.97 (`Cargo.toml` lines 73 to 76: `iroh`, `iroh-relay`, `iroh-blobs`, `iroh-gossip`). Relay choice `RelayKind`: `Disabled` ("for local tests"), `Psyche` (own relays), `N0` (n0 public relays) (`lib.rs` lines 135 to 142, 350 to 354). Psyche's relays are `use1-1.relay.nousresearch.psyche.iroh.link` and `usw1-1.relay.nousresearch.psyche.iroh.link` (`lib.rs` lines 105 to 106). Discovery: `N0` (n0 DNS plus pkarr publisher) or `Local` (files under `/tmp/iroh_local_discovery`, for tests) (`lib.rs` lines 366 to 375; `local_discovery.rs`). **Client defaults: `--iroh-relay psyche`, `--iroh-discovery n0`** (`cli.rs` lines 66 to 72). An allowlist hook restricts which endpoints may connect (`lib.rs` line 341).
- **Central elements, classified:** relays operated for the project (by its own hostnames under `iroh.link`; who operates the machines was not checked): **(a)** from Nous's point of view, **(c)** from ours; n0 DNS/pkarr discovery: **(c)**.
- **Fit with R1 to R7:** as a precedent, a production decentralized-training network on iroh keeps relays and discovery on always-on infrastructure; R1 and R3 **not met** by its defaults.
- **Setting difference:** permissionless runs coordinated through a Solana ledger (other strand).
- **Question:** if we used iroh, we would replace both defaults (relays and discovery) with our own machines and an out-of-band address list; Psyche shows no example of that configuration in production.

## Findings for questions 1 and 2

### Q1. Discovery and bootstrap

**What the sources show**

1. **Every system read needs at least one live, reachable contact at join time.** Hivemind raises "DHTNode bootstrap failed: none of the initial_peers responded to a ping" unless told to ignore it (S7, `node.py` lines 240 to 245). go-libp2p-kad-dht, with an empty routing table, dials its bootstrap list until two succeed, and otherwise has nothing (S4, `dht.go` lines 517 to 560); rust-libp2p's `bootstrap()` returns `NoKnownPeers` (S5). Petals' private-swarm guide: new peers can join "as long as at least one of their initial peers is alive" (S8). libp2p's kad spec leaves the first contacts to the application (S3).
2. **The systems' own guidance assumes always-on public machines as bootstrap peers.** Hivemind: "any computers with a public IP address that are always online" (S7, `docs/user/dht.md`); Petals: "a few CPU-only machines that are always online" (S8). Both conflict with R1 if we ran such a machine around the clock (classification (a)).
3. **Recovery after all bootstrap peers go offline is weak in the libp2p Go DHT.** It does not reuse peers from a previous routing table; a TODO cites issue #387 (S4, `dht.go`). Its default datastore is in memory (S4, `config.go`). The BitTorrent DHT spec instead says the routing table "should be saved between invocations", and that new clients can use contacts shipped in the torrent file's `nodes` key (S10). Hivemind's DHT is designed not to persist state on shutdown (S7, `node.py` lines 47 to 50).
4. **Private DHT instances are supported:**
   - libp2p `ProtocolPrefix("/myapp")` gives a separate Kademlia protocol ID (S4).
   - The pre-shared-key private network (pnet) prevents connections with any node lacking the key (S3).
   - In go-libp2p, **pnet does not work with QUIC or WebTransport** ("QUIC doesn't support private networks yet", S4), so a go-libp2p private pool runs over TCP. Whether rust-libp2p's pnet works over QUIC was not checked.
   - Hivemind: a DHT started without `initial_peers` is a new, private DHT (S7).
   - iroh: no DHT by default. Address lookup can be `MemoryLookup` (addresses given by the application), mDNS (local network only), n0's DNS/pkarr service (c), or a BitTorrent Mainline DHT crate (c) (S9).
5. **Client and server mode.** The kad spec says NATed laptops "should operate in client mode", and nodes add only server-mode nodes to their routing tables (S3). Implementations decide automatically from reachability: go `ModeAuto`; rust switches to client mode without a confirmed external address. Both can be forced to server mode (S4, S5).
6. **Other discovery mechanisms:**
   - mDNS works on the local network only (S11).
   - Rendezvous needs a reachable rendezvous point (S11).
   - iroh "tickets" (endpoint ID, addresses, relay URL) "expire" when people change networks (S9).

**Inferences (labelled)**

- (inference) **With 3 to 5 peers, a Kademlia DHT is degenerate.** With k = 20 (libp2p, Hivemind) or K = 8 (BEP 5) and N ≤ 5 members, every node's routing table can hold every other node, and every record is stored on every reachable node. The DHT reduces to a full member list. The real problem is learning a **current, dialable address** of at least one member when members are intermittent and mostly behind NAT.
- (inference) **All-NAT pools break the libp2p DHT's own rules.** Under the client/server rule, a pool where every member is NATed has no server-mode nodes, so routing tables stay empty unless server mode is forced. Even then, a NATed "server" cannot be dialed directly, only through a relay or after a hole punch.
- (inference) **Join probability.** Let member i be online with probability p_i and reachable when online (public address, port mapping, or a relay reservation at a reachable relay) with probability q_i. If members are independent, the probability that a joining peer finds at least one usable contact is
  P_join = 1 - ∏_{i=1..N} (1 - p_i q_i).
  - Example: N = 4 members each online half the time (p = 0.5) and always reachable (q = 1) gives P_join = 1 - 0.5^4 = 0.9375.
  - If no member is reachable (q = 0 for all), P_join = 0, however often they are online.
  - Independence is optimistic: home machines of friends in one time zone are likely online at the same hours.
- (inference) **What R2 already allows.** The bootstrap list could be refreshed from a public static file, classification (b): the owner's published starting configuration, or a file the peers rewrite. libp2p's `BootstrapPeersFunc` and iroh's `MemoryLookup` both accept such an application-supplied list (S4, S9). BEP 5's `nodes` key in the torrent file is a precedent for shipping contacts inside a static file (S10). No source evaluates this for a small, intermittent pool.

### Q2. Connections through home routers without third-party relays

**What hole punching achieves (measured)**

| Source | Setting and date | Result | Caveats |
|---|---|---|---|
| S1 (Trautwein et al., IMC '26) | Public IPFS network, volunteer clients mostly in the US, random remote peers; **data from 1 Dec 2022 to 1 Jan 2023** | DCUtR hole-punching stage **70% ± 7.1%**, conditional on relay reservation and address discovery succeeding; TCP ≈ QUIC; 97.6% of successes on the first attempt | Prerequisite failures, about 29% of data points, are excluded; volunteers are self-selected; the honeypot pre-filters for relay-reachable peers; no NAT-type or CGNAT breakdown |
| S14 (ProbeLab, 2026) | Live IPFS network, **May 2026**; cloud prober behind a simulated port-restricted-cone NAT against real peers | Port-restricted cone **82.9%**; symmetric 39.7% (doubted by the authors); APDF-unresolved 37.0%; **36%** of DCUtR-advertising NATed peers never got a relay reservation | One side is not a real home NAT; 5-day campaign |
| S2 (Ford et al., 2005) | 380 self-selected NAT Check reports | 82% of NATs compatible with UDP punching, 64% with TCP; hairpin support 24% (UDP) and 13% (TCP) | Device compatibility measured against test servers, not peer-pair success; 2005 devices |
| S9 (iroh docs) | No method given | "roughly 9 out of 10 network configurations allow a direct connection" | Vendor claim. S14 says it has not "seen a study backing" such numbers for iroh |

**Where sources disagree**

- **CGNAT symmetric share.** S1 says CGNAT used EDM "in 40% of cases as of 2016", citing Richter et al. At the source (S13 §6.5), 40% symmetric is for **cellular** CGN ASes; for non-cellular CGN ASes it is **11%**; for home CPE routers it is under 2%. S1's figure overstates the home-broadband case.
- **TCP against UDP.** S2 (2005) found fewer NATs compatible with TCP punching (64% against 82%). S1 and S14 found TCP ≈ QUIC in DCUtR. S14 adds that NATs which answer unsolicited SYNs with RST break TCP punching, while QUIC is immune. The sources differ in era and method, so they need not conflict.
- **What "success rate" means.** S1's 70% is conditional on prerequisites. S14 shows that a further 36% of capable peers never reach the precondition. S1 itself warns that the end-to-end rate "from scratch is lower". Neither study gives an unconditional home-to-home rate.

**Symmetric NAT and carrier-grade NAT (CGN)**

- **Standards.** Endpoint-independent mapping is REQ-1 for NATs (RFC 4787) and applies to CGNs (RFC 6888 REQ-1). Without it, RFC 4787 says a relay becomes necessary (S12).
- **CGN prevalence and timeouts (S13):** CGNs are present in 17 to 18% of non-cellular eyeball ASes and over 90% of cellular ASes. 74% of the NATs detected drop idle UDP mappings within 1 minute; non-cellular CGNs have a median of 35 s. Keep-alives or re-punching are therefore needed (S2 §3.6 also reports timeouts as short as 20 s).
- **Lab tests (S12, RFC 7021):** peer-to-peer gaming, SIP and BitTorrent seeding failed behind CGN, and servers behind two layers of NAT were unreachable.
- **Two peers behind the same CGN** need the CGN to support hairpin translation (S2 §3.5, §5.4). Hairpin support was rare in 2005 (24% UDP, 13% TCP, S2 Table 1); no newer figure was read.
- **ProbeLab (S14):** symmetric peers are about 4% of classifiable IPFS peers, and DCUtR success for them is doubtful.

**Can our own reachable machines act as relays?**

- **libp2p: yes, in configuration.**
  - Relay service runs only on hosts AutoNAT judges public, unless forced (S4, `EnableRelayService`).
  - Other peers can be told to use only static relays (S4, `EnableAutoRelayWithStaticRelays`).
  - An ACL can limit reservations and circuits to our peer IDs (S3, `PERMISSION_DENIED`; S4, `ACLFilter`).
  - **Default limits are 2 minutes and 128 KiB per relayed connection** in both go-libp2p and rust-libp2p (S4, S5). These defaults are enough for DCUtR signalling (under 500 bytes, S1 §3.2) but not for a 0.2 to 0.6 GB update. Limits are configurable, up to unlimited (S4, `WithInfiniteLimits`).
  - Hivemind's daemon fork already raises them to 4 GiB per direction and 30 minutes, and uses bootstrap peers as trusted relays by default (S7).
  - Relays must be directly reachable: the spec says reservations and connections "should not" be accepted over already-relayed connections (S3).
- **iroh: yes.**
  - `RelayMode::Custom` points at our relays; `iroh-relay` is a self-hostable server with allowlists and shared tokens (S9).
  - iroh relays carry all traffic when punching fails, not only signalling (S9, `concepts/relays.md`).
  - The documented self-host setup uses a DNS name and a TLS certificate on ports 80 and 443 (S9). Running it on a home machine was not documented in what was read.
- **Hivemind and Petals: yes, by design.** Their relays are swarm peers; both documents assume these are public, always-on machines (S7, S8).
- **Precedent:** Psyche, a production training network on iroh, defaults to its own named relays and n0 discovery (S15). It does not run relays on volunteers' home machines.

**What happens if none of our machines is reachable**

- **libp2p:**
  - DCUtR starts from an existing relayed connection (S3, `DCUtR.md`); with no reachable relay there is no signalling channel, so no hole punch.
  - The AutoNAT service is switched off on hosts that conclude they are private (S4, `autonat.go`). In an all-private pool every host ends up private, so none starts a relay service (S4, `EnableRelayService`) unless reachability is forced, and forcing it does not make a NATed host dialable.
  - Hivemind's only documented all-NAT option is `use_ipfs=True`, which relies on the public IPFS network, classification **(c)** (S7).
- **iroh:** both peers "first connect to a shared relay server", which also reports each peer's public address (S9). With `RelayMode::Disabled`, only direct addresses work (S9, `endpoint.rs`).
- **Partial escapes the sources show:**
  - a UPnP or PMP port mapping on one router lets the other peer dial directly ("Connection Reversal", S1 §5.2.4; S3 DCUtR unilateral upgrade);
  - IPv6 removes NAT, but Ford et al. note IPv6 firewalls "will still commonly block unsolicited incoming traffic" by default (S2 §1).
  - No source measures either option for home routers today.
- (inference) Without any reachable machine, these stacks give no live path between two NATed peers. Exchanging addresses through a public file host (b) might replace the relay as a signalling channel, but no stack read does this. DCUtR's timing needs a half-RTT synchronisation (S3), and NAT mappings expire within tens of seconds (S13). Both suggest that file-host signalling, with latency of seconds to minutes, would at least need adaptation. No source tests it.

**Is exchange through public file hosts alone a workable fallback?**

- **What sources show:** no source in this strand measures or describes a training system that exchanges updates only through public file hosts. The storage and host-limit strand (question 5) covers host quotas and terms.
- (inference) **Mechanically:** uploads and downloads to a public host are outbound HTTPS. They work through any NAT, including CGN, so NAT traversal stops mattering. The costs move elsewhere:
  - latency per round;
  - host limits and terms (question 5);
  - write access to the shared location (R7);
  - data volume.
- (inference) **Data volume.** If each of N peers uploads its update of size S and downloads the N - 1 others to merge locally:
  - each peer moves S up and (N - 1)S down per round;
  - the host serves N(N - 1)S per round;
  - example: N = 5 and S = 0.6 GB gives 2.4 GB downloaded per peer and 12 GB served per round.
  - A merged-model scheme (one peer merges and uploads once) would reduce downloads to about S per peer, but needs a merging role.
- (inference) **Relay load, for comparison.** A relay on a home machine forwards every byte it relays, so a transfer of S bytes over the relay takes at least t = 8S / B_up seconds at relay upload bandwidth B_up bits per second. Example: S = 0.6 GB and B_up = 20 Mbit/s gives t ≈ 240 s per relayed transfer. Concurrent transfers share B_up.

## Could not verify

- **Halkes and Pouwelse 2011, Guha and Francis 2005, Seemann, Inden and Vyzovitis 2022 ("Decentralized Hole Punching", ICDCSW):** known only as cited in S1 (§6, §7.1, §3.2 reference [31]). Not read at source. The numbers attributed to them (about 64% of peers punchable with more than 80% success; 88% TCP over 93 home NATs; about 11% EDM NATs) stay unverified.
- **iroh's "roughly 9 out of 10" direct-connection claim (S9):** no method, dataset or date on the pages read, and no backing study found. S14 independently says it has not seen one.
- **Who operates Psyche's relay hosts** (`*.relay.nousresearch.psyche.iroh.link`): the naming suggests n0-hosted dedicated relays, but this was not checked.
- **py-libp2p's "Done" status** for circuit relay v2, AutoNAT and hole punching (S6): the README claim was not tested or cross-checked against an interoperability report.
- **rust-libp2p pnet over QUIC:** not checked.

## Gaps

What only a prototype, or a source not found here, could settle:

1. **Per-pair connectivity among the actual pilot homes.** For each home: public IPv4 or CGN (compare the router's WAN address with the address seen from outside); IPv6 availability and inbound firewall policy; UPnP/PCP availability; NAT mapping and filtering class on TCP and UDP (as S14 classifies). Then, for each pair of homes: DCUtR and iroh hole-punch success, time to connect, and how long mappings survive. No source measures home-to-home pairs: S1 measured volunteer clients against random IPFS peers, and S14 used a cloud prober with a simulated NAT.
2. **Whether any pilot machine can serve as a relay or bootstrap peer.** This needs a public address and a port forward or mapping, and enough upload bandwidth. Relay throughput on a home uplink for 0.2 to 0.6 GB transfers was not measured by any source.
3. **Turkish ISPs and CGN.** No source read covers CGN deployment or NAT behaviour in Turkey specifically. S13 is global, AS-level and from 2014 to 2016.
4. **Unconditional end-to-end success.** Both measurement studies condition on prerequisites, such as a relay reservation, that a 3-to-5-peer private pool would have to provide itself.
5. **An all-NAT pool with file-host signalling.** Whether address exchange through a public static file can replace a reachable relay for hole-punch coordination is untested anywhere read.
6. **IPv6 reachability of home connections today.** No primary measurement was read.
7. **iroh relay on a home machine** without a public DNS name or certificate (`--dev` HTTP mode): whether hole punching and QUIC address discovery still work. The README says `--dev` does not run QUIC address discovery.
8. **Routing-table persistence.** go-libp2p-kad-dht has none (issue #387 not read); rust-libp2p not checked; Hivemind by design none.

## Query log

- 2026-10-13 17:18 TST: WebSearch "large scale measurement decentralized NAT traversal DCUtR hole punching arXiv" (found arXiv 2604.12484, 2510.27500, ProbeLab blog leads).
- 2026-10-13 17:18 TST: WebSearch "Ford Srisuresh Kegel peer-to-peer communication across network address translators arXiv" (found arXiv cs/0603074).
- 2026-10-13 17:18 TST: WebSearch "iroh self-hosted relay server n0 default relays documentation" (found docs.iroh.computer pages with raw .md variants).
- 2026-10-13 17:19 TST: curl arxiv.org/pdf/2604.12484, 2510.27500, cs/0603074 (sleep 3 between); pdftotext -layout.
- 2026-10-13 17:20 TST: curl arxiv.org/abs/ pages for the three papers (version histories).
- 2026-10-13 17:20 TST: git clone --depth 1 https://github.com/libp2p/specs (commit c750236, 2026-10-09).
- 2026-10-13 between 17:21 and 17:24 TST: git clone --depth 1 of libp2p/go-libp2p (3c2c902, v0.50.0), libp2p/rust-libp2p (a035aad), libp2p/py-libp2p (79985430; Windows checkout failed on long test-file names, files read with `git show`); finished 17:24:44.
- 2026-10-13 about 17:25 TST (exact time not recorded): git clone --depth 1 libp2p/go-libp2p-kad-dht (4a66705).
- 2026-10-13 17:27:07 TST: `gh api repos/OWNER/REPO`, `repos/OWNER/REPO/releases/latest`, `repos/OWNER/REPO/commits?per_page=1` for libp2p/go-libp2p, libp2p/rust-libp2p, libp2p/py-libp2p, libp2p/go-libp2p-kad-dht, libp2p/go-libp2p-daemon, n0-computer/iroh, learning-at-home/hivemind, bigscience-workshop/petals. Fields recorded: `pushed_at`, `archived`, `license.spdx_id`, `open_issues_count`, `releases/latest.tag_name`, `published_at`, newest commit `sha` and `commit.committer.date`. go-libp2p-daemon (upstream) result: `pushed_at` 2026-03-09T20:07:50Z, latest release v0.9.2 (2026-03-09), `license.spdx_id` NOASSERTION, `open_issues_count` 28 (not used further: Hivemind pins its own fork).
- 2026-10-13 between 17:27 and 17:31 TST (exact times not recorded): git clone --depth 1 learning-at-home/hivemind (4bd43b7); bigscience-workshop/petals (22afba6) and petals.wiki (adb7a1a; checkout failed on a colon in a file name, page read with `git show`); learning-at-home/go-libp2p-daemon at tag v0.5.0.hivemind1 (3762261); n0-computer/iroh (d8c93d8).
- 2026-10-13 17:31:54 TST: curl docs.iroh.computer raw `.md` pages: iroh-services/relays/self-hosted, iroh-services/relays/public, add-a-relay, deployment/dedicated-infrastructure, iroh-services/relays, concepts/relays, concepts/holepunching, concepts/discovery.
- 2026-10-13 17:32:27 TST: curl https://www.bittorrent.org/beps/bep_0005.html (tags stripped with `scripts_w1a/strip.py`, kept outside the download directory); curl rfc-editor.org RFC 4787, 6888, 7021 (txt).
- 2026-10-13 17:33:32 TST: curl for Richter et al. IMC 2016: conferences.sigcomm.org/imc/2016/papers/p215.pdf returned HTML (not used); www.icir.org/vern/papers/cgn-imc16.pdf returned the PDF (read).
- 2026-10-13 17:35:33 TST: curl https://probelab.io/blog/can-libp2p-punch-through-nats/ (tags stripped); 17:35:53 curl raw `probe-lab/dcutr-project/HEAD/docs/dcutr-final-report.md`; `gh api repos/probe-lab/dcutr-project` and `.../commits?per_page=1`.
- 2026-10-13 17:36:18 TST: git clone --depth 1 PsycheFoundation/psyche (0bdb13d; checkout failed on long paths, files read with `git show` / `git grep`); `gh api repos/PsycheFoundation/psyche`.
- No WebFetch was used. arXiv requests were separated by `sleep 3`.

**Not covered in this strand:**
- The original Kademlia paper (Maymounkov and Mazières 2002) and S/Kademlia: only cited through the libp2p spec.
- js-libp2p: S14 calls its DCUtR experimental.
- Hyperswarm / HyperDHT (holepunch.to): a DHT-based hole-punching stack, mentioned only by S14; not read.
- Tailscale / Headscale / DERP, ZeroTier, Yggdrasil and WebRTC ICE: overlay-VPN and browser approaches. A self-hosted coordination server would be (a); not read.
- Measured IPv6 home reachability and Turkish ISP CGN deployment: no sources found or read.
- go-libp2p-kad-dht issue #387 (routing-table persistence): not read.
- `iroh` docs pages `add-a-relay.md` and `deployment/dedicated-infrastructure.md`: downloaded but not read.
- ProbeLab sub-reports (`nat-classification.md`, `dcutr-testbed.md`, `dcutr-audit.md`): not read.
