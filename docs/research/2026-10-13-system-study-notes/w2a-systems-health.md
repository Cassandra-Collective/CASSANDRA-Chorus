# W2a: the systems themselves: maintenance, licence, runtime and fit (system study question 9) · notes

Status: complete draft, 2026-10-13 18:30 TST (skeleton 17:55 TST).

Strand: question 9 of `docs/research/2026-10-13-system-study-brief.md` only. No design is recommended here.

**How these notes were made.**
- GitHub data: `gh api` (authenticated, read-only). Raw JSON saved under the session scratchpad, `sysstudy/sources/w2a/api/<owner>_<repo>/`. Endpoints per repository:
  - `repos/R` (fields `full_name`, `default_branch`, `license.spdx_id`, `archived`, `pushed_at`, `created_at`, `open_issues_count`, `description`);
  - `repos/R/releases/latest` (`tag_name`, `published_at`) and `repos/R/releases?per_page=5`;
  - `repos/R/tags?per_page=5`;
  - `repos/R/commits?per_page=3` (default branch; `sha`, `commit.committer.date`);
  - `repos/R/languages`;
  - `repos/R/contents/.github/workflows`;
  - `search/issues?q=repo:R+type:pr+state:open` and `...type:issue...` (`total_count`).
- Package indexes: PyPI JSON (`https://pypi.org/pypi/NAME/json`; `info.version`, `urls[].filename`, `urls[].upload_time_iso_8601`), crates.io (`https://crates.io/api/v1/crates/NAME`; `crate.max_stable_version`, `versions[].created_at`), npm registry (`dist-tags.latest`, `time[<version>]`), Go module proxy (`@latest`: `Version`, `Time`). Saved under `sysstudy/sources/w2a/pkg/`.
- Raw files: `curl -sL https://raw.githubusercontent.com/OWNER/REPO/HEAD/PATH` into `sysstudy/sources/w2a/raw/`. Read with `grep`/`sed`. Nothing downloaded was run, built or installed.
- Times: all queries on **2026-10-13**, machine clock **TST (UTC+3)**. API timestamps ending in `Z` are UTC.
- `open_issues_count` from the repository endpoint **includes open pull requests**; the search counts separate them. Where the two disagree it is noted.
- Classification of central elements (brief): **(a)** a server we would run; **(b)** a public host for static files; **(c)** a public third-party network for live coordination or discovery. Mechanisms are cited from the wave-1 notes (`w1a` to `w1d`, block numbers) and not re-read.
- "(inference)" marks my reasoning. Every "Fit" line is inference from the cited mechanisms.

## Systems

### 1. Hivemind (learning-at-home), with its `p2pd` daemon fork

- **Repository:** https://github.com/learning-at-home/hivemind
- **API record (queried 2026-10-13 17:55:34 to 17:55:46 TST):**
  - `license.spdx_id` MIT; `archived` false; `default_branch` master; `created_at` 2020-02-27T13:50:19Z.
  - `pushed_at` 2026-01-11T21:13:45Z.
  - `releases/latest`: `tag_name` 1.1.12, `published_at` 2026-01-03T07:41:24Z. Earlier: 1.1.11 (2025-04-20T10:27:23Z), 1.1.10 (2023-08-31T20:07:52Z).
  - Newest default-branch commit `4bd43b778950`, `commit.committer.date` 2026-01-04T23:36:23Z, "Make Hivemind compatible with PEP 517 (#670)". The two before: 2025-10-12 ("Fix p2pd cross-compilation, build wheels in GHA (#665)"), 2025-08-03.
  - `open_issues_count` 94 = 70 open issues + 24 open PRs (search `total_count`).
- **Package (PyPI, queried 18:05:53 TST):** `hivemind` 1.1.12. Files uploaded 2026-01-03T07:42:07Z to 07:42:17Z: `macosx_10_9_x86_64`, `macosx_11_0_arm64`, `manylinux2014_aarch64` and `manylinux2014_x86_64` wheels, plus the sdist. **No Windows wheel.**
- **Its libp2p daemon fork:** https://github.com/learning-at-home/go-libp2p-daemon (API 17:56:03 to 17:56:27 TST).
  - `license.spdx_id` NOASSERTION; the root holds `LICENSE-APACHE` and `LICENSE-MIT` (contents listing, 18:19:56 TST), i.e. dual-licensed.
  - `pushed_at` 2025-02-09T20:45:52Z; `releases/latest` v0.5.0.hivemind1, `published_at` 2023-11-21T00:53:40Z.
  - Newest commit `67c84abe11d6`, 2023-11-21T18:25:33Z ("Update README.md"); 0 open issues, 2 open PRs.
  - Hivemind pins it: `P2PD_VERSION = "v0.5.0.hivemind1"` (`setup.py` line 16).
  - The fork is built against go-libp2p v0.32.1 (`w1a` S7, `go.mod`). Upstream go-libp2p is now v0.50.0 (block 3).
- **Upstream daemon, for comparison:** https://github.com/libp2p/go-libp2p-daemon (API 18:17:53 to 18:18:19 TST): `license.spdx_id` NOASSERTION; `pushed_at` 2026-03-09T20:07:50Z; latest release v0.9.2 (2026-03-09T20:07:50Z); 25 open issues, 3 open PRs.
- **Licence:** MIT (Hivemind); the fork is MIT or Apache-2.0.
- **Language and runtime:**
  - Python: 99.9% of bytes (`languages`). `pyproject.toml` line 11: `requires-python = ">=3.9"`. The README says "Python 3.8+" (line 43); the two disagree.
  - PyTorch ≥ 1.9.0 (`requirements.txt`).
  - Networking runs in a separate Go binary, `p2pd`, launched as a child process (`w1a` S7).
- **Windows support: not native.**
  - README lines 82 to 90: "Linux is the default OS for which hivemind is developed and tested". Windows 10+ is "(experimental)" and runs through WSL.
  - `setup.py`:
    - line 63 lists the supported platforms as `linux-amd64`, `linux-arm64`, `darwin-amd64`, `darwin-arm64`;
    - both the download path (lines 136 to 143, "does not provide a precompiled p2pd binary") and the build-from-source path (lines 100 to 103, through `_parse_platform`, which raises `Unsupported platform`) stop on any other platform.
    - (inference, from code read, not run) A native Windows install fails at the `p2pd` step.
  - CI: `run-tests.yml` runs on `ubuntu-latest` only, Python 3.9 to 3.12 (lines 13 to 16). `release.yml` builds wheels for those same four platforms (line 13).
- **Python bindings:** Hivemind is itself a Python library.
- **Documentation:** README; `docs/` on Read the Docs (`.readthedocs.yml`); `w1a` read `docs/user/dht.md`.
- **What it provides toward Chorus:**
  - Discovery: its own Kademlia-style DHT over libp2p streams. A private DHT is created by starting without `initial_peers` (`w1a` S7).
  - Connections: `p2pd` with AutoNAT, hole punching, and relays whose limits are raised to 4 GiB and 30 minutes (`w1a` S7).
  - Averaging: `DecentralizedAverager` takes "a sequence of pytorch tensors that will be averaged in each all-reduce". Groups are formed by matchmaking under a key `prefix`, with `target_group_size`, `min_matchmaking_time` and `allreduce_timeout` (`hivemind/averaging/averager.py` lines 50 to 83, fetched 18:20:35 TST). It comes from the Moshpit and DeDLOC line of work (`w1b` S3, S4).
  - State transfer: from a peer (`allow_state_sharing`, `load_state_from_peers`), with compression codecs (`w1d` S4).
  - Signed DHT records (`w1c` S12).
  - Storage: none (`w1d` S4).
  - Client: none; it is a library.
- **Central elements:** (`w1a` S7; `w1d` T4, T5)
  - initial peers: **(a)** if one must be always on; otherwise our intermittent machines;
  - `use_ipfs=True`: **(c)**;
  - the `p2pd` binary from GitHub releases and the wheel on PyPI: **(b)**.
- **Fit with R1 to R7 (inference):**
  - R1 **partly**: works with intermittent bootstrap peers only if one listed peer is up and reachable at join time (`w1a` S7).
  - R2 **partly**: the bootstrap list can be our own machines, but the DHT does not persist.
  - R3 **partly**: relays are our own peers, but they must be publicly reachable; the only documented all-NAT mode is (c).
  - R4 **met in mechanism** for group averaging. The synchronous mode would be one group of all peers (not tested anywhere read).
  - R5 **not provided**: `target_group_size` is a target, not a per-expert minimum.
  - R6 **partly**: full copies have precedents (DeDLOC, `w1b` S4; OpenDiLoCo, block 9). Slices: none built in; see the work-unit line below.
  - R7: embodies the peer-to-peer option with signed, expiring records (`w1c` S12); durable state needs a host (b).
- **Full copy / slice (inference):**
  - Full copy: yes; this is how DeDLOC and OpenDiLoCo used it.
  - Slice: the averager is a generic group average over any tensor list under a key prefix, so one averager per expert, keyed by that expert, would match only the peers holding it. Nothing read implements or tests this. The holder-group precedent remains FoMoE, which is synchronous and coordinated (`w1b` S17, F6).
- **Risks:**
  - Maintenance: low activity. Packaging and build fixes only since 2025 (the commit messages above); 24 open PRs.
  - Networking: a 2023 fork built on go-libp2p v0.32.1, while upstream is at v0.50.0. (inference) Later upstream fixes in NAT traversal and security are absent.
  - Platform: no native Windows; the pilot's Windows laptops would need WSL2 with CUDA.
  - Fragmentation: downstream projects pin different Hivemind commits.
    - Petals: `213bff98a62a` (2024-07-15).
    - Node0 and Agora: `4d5c41495be0` (2025-05-06).
    - GenRL: unpinned from PyPI (blocks 2, 12, 13).
    - Commit dates: `gh api repos/learning-at-home/hivemind/commits/<sha>`, 18:11:59 TST.

### 2. Petals (bigscience-workshop)

- **Repository:** https://github.com/bigscience-workshop/petals
- **API record (17:55:47 to 17:56:03 TST):**
  - `license.spdx_id` MIT; `archived` false.
  - `pushed_at` 2024-09-07T11:54:28Z.
  - `releases/latest` v2.2.0, `published_at` 2023-09-06T17:29:56Z.
  - Newest commit `22afba627a7e`, 2024-08-25T08:12:19Z ("Upgrade Pydantic to >= 2.0.0 (#607)").
  - `open_issues_count` 114 = 94 issues + 20 PRs.
- **Package (PyPI, 18:05:56 TST):** `petals` 2.2.0.post1, pure-Python wheel uploaded 2023-11-20T23:09:10Z.
- **Licence:** MIT.
- **Language and runtime:** Python (`setup.cfg` line 33: `python_requires = >=3.8`). It depends on Hivemind pinned to a git commit: `hivemind @ git+...@213bff98...` (line 42), committed 2024-07-15.
- **Windows support:** through WSL only. The README says "Windows + WSL" and points to a wiki guide (line 56). The CI matrix in `run-tests.yaml` is Ubuntu and macOS only (lines 11 to 22).
- **Python bindings:** Python library.
- **Documentation:** README and the GitHub wiki (`w1a` S8 read "Launch your own swarm").
- **What it provides toward Chorus:**
  - Discovery and connections: Hivemind's.
  - Servers hold transformer blocks and fetch only those from the Hugging Face Hub (`w1d` S5).
  - No pretraining averaging; it does inference and fine-tuning (`docs/prior-work.md` §5).
- **Central elements:** (`w1a` S8; `w1d` S5)
  - public swarm: the bootstrap servers and `health.petals.dev` API, **(c)**;
  - private swarm: always-on bootstrap and relay machines, **(a)**;
  - weights: Hugging Face Hub, **(b)**.
- **Fit (inference):**
  - R1 **not met** as documented.
  - R3 **partly**: relays are its own peers, if reachable.
  - R4 to R6: **not addressed**; it is not a training-averaging system.
  - R7: not applicable.
- **Full copy / slice:** neither. It is only a precedent for downloading part of a model from a public host (`w1d` S5).
- **Risks:** unmaintained. No default-branch commit since 2024-08-25 and no GitHub release since 2023-09-06 (both from the API record above). It pins a 2024 Hivemind commit.

### 3. go-libp2p (with go-libp2p-kad-dht)

- **Repository:** https://github.com/libp2p/go-libp2p
- **API record (17:56:27 to 17:57:14 TST):**
  - `license.spdx_id` MIT; `archived` false.
  - `pushed_at` 2026-10-05T09:33:02Z.
  - `releases/latest` v0.50.0, `published_at` 2026-09-21T14:17:28Z. Earlier: v0.49.0 (2026-07-28), v0.48.0 (2026-03-17), v0.47.0 (2026-01-25).
  - Newest commit `3c2c902122cb`, 2026-09-21T14:17:10Z ("Release v0.50.0").
  - `open_issues_count` 303 = 262 issues + 41 PRs.
- **Go module proxy (`@latest`, 18:08:56 TST):** `Version` v0.50.0, `Time` 2026-09-21T14:17:10Z, `Origin.Hash` 3c2c9021.
- **go-libp2p-kad-dht (17:57:14 to 17:57:32 TST):** MIT; `pushed_at` 2026-09-24T09:32:07Z; `releases/latest` v0.42.2 (2026-08-21T05:26:12Z); newest commit 2026-09-24T09:32:07Z; 48 issues and 8 PRs open.
- **Licence:** MIT.
- **Language and runtime:** Go. `go.mod` line 3 says `go 1.26.0`; CI tests Go 1.26.x and 1.27.x (`go-test.yml`).
- **Windows support: tested in CI.** The test template's OS matrix is `["ubuntu", "macos", "windows"]` (`go-test-template.yml` lines 21 to 28).
- **Python bindings:** none in the repository. The route used in practice is the daemon (`p2pd`) with a client library, as Hivemind does (block 1).
- **Documentation:** README; the `libp2p/specs` repository; `w1a` S3 and S4 read the specifications and code.
- **What it provides toward Chorus:**
  - Discovery: Kademlia DHT, mDNS, rendezvous.
  - Connections: AutoNAT, DCUtR hole punching, Circuit Relay v2, and private networks (pnet). Pnet runs over TCP only; QUIC refuses a pre-shared key (`w1a` S4).
  - No averaging, no storage, no client.
- **Central elements:** none required. The default public IPFS bootstrap list is **(c)** if used (`w1a` S4).
- **Fit (inference):**
  - R1 **met**: every role is a peer role.
  - R2 **partly**: the application must supply the bootstrap list, and the routing table is not persisted (`w1a` S4).
  - R3 **met in configuration**, with pnet and our own static relays, but only if one of our machines is reachable. Default relay limits (2 minutes, 128 KiB) must be raised.
  - R4 to R7: **not addressed**; it is a transport layer.
- **Full copy / slice:** neither. Averaging must be built on top.
- **Risks:** the language differs from the Python code base (D3), so we would use a daemon or write Go. The maintenance state is healthy (monthly to bimonthly releases).

### 4. rust-libp2p

- **Repository:** https://github.com/libp2p/rust-libp2p
- **API record (17:57:32 to 17:57:49 TST):**
  - `license.spdx_id` MIT; `archived` false.
  - `pushed_at` 2026-10-13T14:11:00Z.
  - `releases/latest` v0.57.0, `published_at` 2026-09-11T21:34:37Z; the previous release was libp2p-v0.56.0 (2025-06-28).
  - Newest commit `a035aad0566f`, 2026-10-13T14:10:59Z.
  - `open_issues_count` 303. The search counts give 163 issues + 136 PRs = 299, so the two disagree by 4.
- **crates.io (18:07:01 TST):** `libp2p` `max_stable_version` 0.57.0, `created_at` 2026-09-11T16:46:20Z, licence MIT.
- **Licence:** MIT.
- **Language and runtime:** Rust.
- **Windows support: compile check only.**
  - The `cross` job runs `cargo check --package libp2p --all-features --target=x86_64-pc-windows-msvc` on `windows-latest` (`ci.yml` lines 125 to 153).
  - The `test` job runs on `ubuntu-latest` (lines 18 to 21).
- **Python bindings:** none found in the repository (nothing outside it searched).
- **Documentation:** README; docs.rs (not fetched).
- **What it provides, central elements, fit:** as block 3 (`w1a` S5). Whether its pnet works over QUIC was not checked (`w1a`).
- **Risks:** no Windows tests; Rust; Python use would need bindings we build ourselves (inference).

### 5. py-libp2p

- **Repository:** https://github.com/libp2p/py-libp2p
- **API record (17:57:49 to 17:58:21 TST):**
  - `license.spdx_id` NOASSERTION; the root holds `LICENSE-APACHE` and `LICENSE-MIT` (root listing, 18:02:50 TST).
  - `pushed_at` 2026-10-02T09:02:49Z.
  - `releases/latest` v0.8.0, `published_at` 2026-09-26T13:00:48Z; earlier v0.7.0 (2026-07-09).
  - Newest commit `79985430f45a`, 2026-10-02T09:02:47Z.
  - `open_issues_count` 75 = 62 issues + 13 PRs.
  - Repository `description` still ends "[under development]".
- **Package (PyPI, 18:05:58 TST):**
  - `libp2p` 0.8.0, pure `py3-none-any` wheel uploaded 2026-09-26T12:40:44Z.
  - `license_expression` "MIT AND Apache-2.0"; classifier "Development Status :: 4 - Beta"; `requires_python` ">=3.10, <4.0".
  - Release cadence by upload time: 0.3.0 (2025-09-25), 0.4.0 (2025-11-05), 0.5.0 (2025-12-21), 0.6.0 (2026-02-16), 0.7.0 (2026-07-09), 0.8.0 (2026-09-26).
- **Licence:** MIT and Apache-2.0 (dual).
- **Language and runtime:** pure Python ≥ 3.10.
- **Windows support: tested in CI, partially.**
  - `tox.yml` has a `windows` job on `windows-latest`, Python 3.11 to 3.13, with the tox environments `core`, `demos`, `utils` and `wheel` (lines 109 to 142).
  - The `interop` environment runs only in the Linux job (lines 16 to 21, 52 to 84).
  - `pyproject.toml` line 27 excludes `fastecdsa` on `win32`.
- **Python bindings:** native.
- **Documentation:** README feature tables (`w1a` S6) and Read the Docs.
- **What it provides:** the same protocol set as block 3, by the README's own claims ("Done" for relay v2, AutoNAT, hole punching, kad-dht; `w1a` S6). The README says it "moved beyond its experimental roots and is steadily progressing toward production readiness" (line 15).
- **Central elements, fit:** as block 3, in principle (inference). It would keep Chorus in Python.
- **Risks:**
  - Maturity is self-reported: Beta classifier, "[under development]" in the description.
  - Interoperability of its NAT traversal with go and rust peers is not verified (`w1a`, Could not verify).
  - The Windows CI does not run the interop tests.

### 6. js-libp2p

- **Repository:** https://github.com/libp2p/js-libp2p
- **API record (17:58:21 to 17:58:35 TST):**
  - `license.spdx_id` Apache-2.0; the root holds `LICENSE-APACHE` and `LICENSE-MIT`.
  - `pushed_at` 2026-10-12T00:20:16Z.
  - `releases/latest` is `utils-v7.4.2` (2026-10-10T06:50:02Z). This is a monorepo with one release per package, so "latest" names whichever package released last.
  - Newest commit `4a416447c618`, 2026-10-11T23:58:49Z.
  - `open_issues_count` 118 = 65 issues + 53 PRs.
- **Package (npm, 18:08:56 TST):** `libp2p` `dist-tags.latest` 3.3.12, `time` 2026-10-10T06:56:11.920Z, licence "Apache-2.0 OR MIT".
- **Licence:** Apache-2.0 or MIT.
- **Language and runtime:** TypeScript, on Node.js and in browsers.
- **Windows support: tested in CI.** The `test-node` matrix is `os: [windows-latest, ubuntu-latest, macos-15]` (`main.yml` lines 46 to 55).
- **Python bindings:** none.
- **Documentation:** README; https://libp2p.github.io/js-libp2p/ (`homepage` field; not fetched).
- **What it provides, central elements, fit:** as block 3 in kind (inference). Mechanisms were not read in wave 1. `w1a` notes that the ProbeLab study (`w1a` S14) calls its DCUtR experimental.
- **Risks:** a third runtime (Node.js) beside Python and PyTorch.

### 7. iroh (n0-computer), with its Python bindings `iroh-ffi`

- **Repository:** https://github.com/n0-computer/iroh
- **API record (17:58:35 to 17:58:50 TST):**
  - `license.spdx_id` Apache-2.0; the root holds `LICENSE-APACHE` and `LICENSE-MIT`.
  - `pushed_at` 2026-10-13T14:50:08Z.
  - `releases/latest` v1.3.0, `published_at` 2026-09-28T19:26:13Z. Earlier: v1.2.0 (2026-09-11), v1.1.0 (2026-08-25), v1.0.3 (2026-07-20), v1.0.2 (2026-07-06).
  - Newest commit `d8c93d8bd60c`, 2026-10-09T11:07:24Z.
  - `open_issues_count` 175 = 153 issues + 22 PRs.
- **crates.io (18:06:54 to 18:06:57 TST):** `iroh` 1.3.0 (`created_at` 2026-09-28T19:22:11Z) and `iroh-relay` 1.3.0 (2026-09-28T19:21:59Z), licence "MIT OR Apache-2.0".
- **Release binaries (`releases/latest` assets, 18:21:14 TST):** `iroh-relay` and `iroh-dns-server` for `x86_64-pc-windows-msvc` (zip), Linux (gnu and musl, x86_64 and aarch64) and macOS.
- **Licence:** MIT or Apache-2.0.
- **Language and runtime:** Rust (99.6%).
- **Windows support: tested in CI.**
  - `tests.yaml` job `build_and_test_windows` runs `cargo nextest run` for target `x86_64-pc-windows-msvc` on Windows runners (lines 220 to 246, 330 to 360).
  - A Wine sanity workflow also exists (`wine.yaml`).
  - Windows release binaries for the relay server are published (above).
- **Python bindings:** https://github.com/n0-computer/iroh-ffi
  - API record (17:58:51 to 17:59:05 TST): Apache-2.0; `pushed_at` 2026-10-05T20:37:38Z; `releases/latest` v1.1.0 (2026-07-16T13:04:43Z); newest default-branch commit `3103bf5295be` (2026-07-28T19:17:33Z); 12 issues and 5 PRs open.
  - PyPI `iroh` 1.1.0 (18:06:02 TST): wheels uploaded 2026-07-16T13:54Z for `win_amd64`, `manylinux_2_28` x86_64 and aarch64, and `macosx_11_0_arm64`. Classifier "Development Status :: 3 - Alpha".
  - `README.python.md` lists the same four targets, including "amd64 win". The CI `wheels.yml` builds the Windows wheel on `windows-latest` (lines 80 to 95).
  - `Cargo.toml` line 37: `iroh = { version = "1.0.0" }`, i.e. any 1.x by semver. The binding release is 1.1.0 while the core is at 1.3.0.
  - `support-matrix.yaml` marks Python `true` for "Custom relays (full RelayMap)" and "Endpoints".
- **Documentation:** docs.iroh.computer (pages read in `w1a` S9); README.
- **What it provides toward Chorus:**
  - Connections: QUIC, hole punching, and relays that carry all traffic when punching fails (`w1a` S9).
  - Discovery: `MemoryLookup`, mDNS, DNS/pkarr (n0 public instance), and a Mainline DHT crate (`w1a` S9).
  - No averaging, storage or client in this repository. Blobs are in a separate crate, not checked here.
- **Central elements:** (`w1a` S9)
  - default n0 relays and n0 DNS/pkarr: **(c)**;
  - a self-hosted `iroh-relay`: **(a)** if run around the clock, otherwise a peer role;
  - `MemoryLookup` fed from a published static file: **(b)** (inference).
- **Fit (inference):**
  - R1 **met only with non-default configuration**: `Builder::empty()`, `RelayMode::Custom`, `MemoryLookup`.
  - R3 **met** with a reachable relay of our own; a Windows relay binary exists. The documented self-hosting uses a DNS name and TLS (`w1a` S9).
  - R4 to R7: **not addressed**; it is a transport.
- **Full copy / slice:** neither; averaging must be built on top.
- **Risks:**
  - The Python binding is Alpha and trails the core (1.1.0 against 1.3.0).
  - Fast version churn: 1.0.2 to 1.3.0 between 2026-07-06 and 2026-09-28.
  - Out of the box it depends on n0 infrastructure (c).
  - The "9 out of 10" direct-connection claim is unverified (`w1a`).

### 8. Psyche (Nous Research; Psyche Foundation)

- **Repository:** `https://github.com/PsycheFoundation/psyche` now redirects: `gh api repos/PsycheFoundation/psyche` returned `full_name` "PsycheFoundation/nousnet" (17:55:22 TST). Canonical: https://github.com/PsycheFoundation/nousnet
- **API record (17:59:05 to 17:59:20 TST):**
  - `license.spdx_id` Apache-2.0; `archived` false; `created_at` 2025-01-23.
  - `pushed_at` 2026-03-24T20:46:58Z.
  - `releases/latest` v0.2.0, `published_at` 2026-01-21T00:39:21Z. Pre-releases: "dev" (2026-01-15), "run-manager-pre-0" (2025-12-12).
  - Newest commit `0bdb13d94a05`, 2026-03-20T19:58:10Z ("Use `bf16` type on model sharing (#635)").
  - `open_issues_count` 138 = 75 issues + 63 PRs.
  - Organisation listing (18:10:09 TST): only `nousnet` and `psyche-backoffice` (`pushed_at` 2025-12-06). No newer Psyche repository was found there.
- **Packages:** none found under the project's names.
  - PyPI `psyche` 0.0.1 (uploaded 2017-02-10, author Matteo Cafasso) is an **unrelated namesake**.
  - crates.io `psyche-core` 0.2.19 (2019, `repository` PsichiX/psyche) is an **unrelated namesake**.
  - crates.io `psyche-client`: 404.
  - The client is distributed as a Docker image plus a `run-manager` binary (`w1d` T5).
- **Licence:** Apache-2.0.
- **Language and runtime:** Rust 77.7%, TypeScript 10.0%, Python 4.8%, Nix 2.6% (`languages`). Networking on iroh 0.97 (`w1a` S15). The client runs in Docker.
- **Windows support: none.**
  - `psyche-book/src/enduser/join-run.md` line 11: "The Psyche client currently only runs on modern Linux distributions."
  - It requires Docker Engine, the NVIDIA Container Toolkit and a Solana keypair (lines 25 to 50).
  - `build-run-manager.yml` builds only `linux-x64` (lines 25, 70 to 90).
- **Python bindings:** a `python/` directory exists (root listing); not read. No Python API claim recorded.
- **Documentation:** the in-repo "Psyche book" (`w1c` S1 read it). The README links https://docs.psyche.network (not fetched).
- **What it provides toward Chorus:** a complete stack for data-parallel full copies:
  - coordinator (Solana program, or a TCP server for development);
  - peer-to-peer exchange of compressed per-step results over iroh;
  - witness-based selection of results;
  - Hugging Face, GCS or peer-to-peer checkpoints;
  - a client (run-manager and Docker) (`w1c` S1; `w1d` S2, T5).
- **Central elements:** (`w1a` S15; `w1c` S1; `w1d` S2)
  - Solana coordinator: **(c)**;
  - TCP coordinator: **(a)**, documented as a development tool;
  - checkpoints on Hugging Face: **(b)**; on GCS: (b), paid;
  - relays: n0 **(c)**, or Psyche-run (**(a)** for Nous, **(c)** for us);
  - n0 discovery: **(c)**;
  - new here: `join-run.md` line 101 recommends dedicated Solana RPC services (Helius, QuickNode, Triton) or self-hosting an RPC node: **(c)**, or **(a)** if self-hosted.
- **Fit (inference; mechanisms from `w1c` S1):**
  - R1 **partly**: the chain is not a server we run, but it is (c).
  - R2 **not met**: Solana is not on the R2 list.
  - R3 **partly**: relays can be disabled.
  - R4 **not met**: synchronous steps with a witness barrier.
  - R5 and R6 (slice): **not addressed**.
  - R7: the ledger option.
- **Full copy / slice:** full copy only, and per-step data parallel rather than H-step local averaging. No slices.
- **Risks:**
  - No default-branch commit since 2026-03-20 (about 7 months before this query), and `pushed_at` 2026-03-24. (inference) Development appears paused or moved out of this repository; not established.
  - Linux only, so it excludes the pilot's Windows laptops.
  - Depends on Solana and RPC providers.

### 9. Prime Intellect: `prime-diloco` (INTELLECT-1 framework), with the `prime` CLI, OpenDiLoCo and `prime-rl`

- **Repository:** https://github.com/PrimeIntellect-ai/prime-diloco. `description` (quoted in part): "a framework for efficient, globally distributed training of AI models".
- **API record (17:59:20 to 17:59:37 TST):**
  - `license.spdx_id` Apache-2.0; `archived` false; `created_at` 2024-09-11T17:07:36Z.
  - `pushed_at` 2026-07-17T22:02:52Z.
  - `releases/latest` v0.5, `published_at` 2024-10-24T01:35:47Z; the only other releases are v0.1 to v0.3 (October 2024).
  - Newest default-branch commit `de5b9317da5f`, `commit.committer.date` 2025-04-10T20:29:58Z ("docs: fix typo in Hugging Face upload instructions").
  - `open_issues_count` 26 = 12 issues + 14 PRs.
  - (inference) `pushed_at` is 15 months later than the newest default-branch commit, so the 2026 pushes went to other branches. Not checked.
- **Packages:**
  - The `pyproject.toml` name is `zeroband` 0.1.0, not published.
  - PyPI `zeroband` 0.0.2 (uploaded 2024-10-04, author "Jackmin801", summary "stealth stealth very sneaky") is a placeholder, **not the framework**.
  - PyPI `prime` 0.12.0 (uploaded 2026-10-12T07:29:25Z) is the **CLI and SDK**, not the framework.
- **Licence:** Apache-2.0.
- **Language and runtime:**
  - Python 92.6% and C++ 5.3% (a custom int8 all-reduce kernel, JIT-compiled; README "Custom Int8 All-Reduce Kernel").
  - `requires-python >=3.10`; `torch==2.5.1` (`pyproject.toml`); uses `uv` and `torchrun`.
- **Windows support: none stated.**
  - The README's checkpointing writes to `/dev/shm`; its run example sets `GLOO_SOCKET_IFNAME=lo` (README "Asynchronous distributed checkpointing"; line 91).
  - CI `gpu.yml` runs on `self-hosted`, with the OS not stated.
  - (inference) Linux only in practice.
- **Python bindings:** a Python framework.
- **Documentation:** README; the INTELLECT-1 technical report PDF in the repository (`w1c` S5 read the arXiv version).
- **What it provides toward Chorus (README; `w1c` S5; `w1d` S3):**
  - `ElasticDeviceMesh`: heartbeat membership through a master key-value store;
  - DiLoCo outer steps with an int8 all-reduce;
  - asynchronous checkpointing to a remote store through fsspec;
  - live recovery from peers' sidecar HTTP servers;
  - full copies only.
- **Central elements:** the master key-value store, **(a)**; the Tailscale VPN used in INTELLECT-1, **(c)** (inference, `w1c` S5); remote checkpoint storage through fsspec, **(b)** if a public bucket (`w1d` S3).
- **Fit (inference):**
  - R1 **not met** as run.
  - R3 **not met** as run (Tailscale).
  - R4: a synchronous all-reduce. That is a synchronous mode (D38), not the asynchronous one.
  - R5 and R6 (slice): **no**.
  - R7: trust in contributors is implicit.
- **Full copy / slice:** full copy only.
- **Risks:**
  - No default-branch commit for 18 months (2025-04-10 to the query date); last release October 2024.
  - Prime Intellect's active training repository is now RL. `PrimeIntellect-ai/prime-rl` (API 18:19:56 TST): Apache-2.0, `pushed_at` 2026-10-13T14:57:55Z, `releases/latest` v0.9.0 (2026-08-25T20:14:45Z), `description` "Agentic RL Training at Scale". Recorded as a lead only; it was not read and is not pretraining.
- **Related records:**
  - **`PrimeIntellect-ai/prime`** (API 17:59:51 to 18:00:08 TST): `description` "Official CLI and Python SDK for Prime Intellect ..."; MIT; `pushed_at` 2026-10-13T00:22:13Z; `releases/latest` v0.12.0 (2026-10-12T07:29:10Z); `created_at` 2024-12-29. Not a training framework (see Corrections).
  - **OpenDiLoCo** (`PrimeIntellect-ai/OpenDiLoCo`, `full_name` "PrimeIntellect-ai/OpenDiloco", API 18:00:08 to 18:00:22 TST):
    - Apache-2.0; `pushed_at` 2026-07-17T21:01:46Z; no releases.
    - Newest commit `2d750e58a692`, 2025-01-13T02:40:59Z; the commit before it, `90eb7580c9ed`, is "add no longer maintained notice + link to prime repo".
    - README line 5: "OpenDiLoCo is no longer maintained." It links to `github.com/PrimeIntellect-ai/prime`, which is now the CLI.
    - It used Hivemind for "distributed weight averaging" (README lines 74 to 84).

### 10. PCCL (Prime Collective Communications Library)

- **Repository:** https://github.com/PrimeIntellect-ai/pccl. `description`: "implements fault tolerant collective communications over IP".
- **API record (17:59:37 to 17:59:51 TST):**
  - `license.spdx_id` MIT; `archived` false; `created_at` 2024-12-06.
  - `pushed_at` 2025-09-12T08:53:07Z.
  - `releases/latest` `release/v1.0.0`, `published_at` 2025-05-21T00:53:59Z (the only release).
  - Newest commit `2af926aca813`, 2025-09-12T08:53:03Z.
  - `open_issues_count` 3 = 1 issue + 2 PRs.
- **Package (PyPI `pypccl`, 18:06:04 TST):** 1.0.0. Only two wheels:
  - `cp312-cp312-manylinux_2_17_x86_64`, uploaded 2025-05-21T02:19:30Z;
  - `cp313-cp313-macosx_15_0_arm64`, uploaded 2025-05-19T18:29:35Z.
  - **No Windows wheel on PyPI.** The README's install command is `pip install pypccl` (line 129).
- **GitHub release assets (`releases/latest`, 18:19:56 TST):**
  - `pypccl-1.0.0-cp312-cp312-win_amd64-nocuda.whl` and `...win_arm64-nocuda.whl`;
  - Linux wheels with and without CUDA, and a macOS arm64 wheel;
  - `libpccl` zips, including Windows x64 and arm64 (no CUDA).
  - **No Windows CUDA build is published.**
- **Licence:** MIT.
- **Language and runtime:** C++20 (70.0%) with Python bindings (25.1%). The README asks for MSVC 17+, gcc 12+ or clang 12+, and Python 3.12+ for the bindings (lines 136 to 138).
- **Windows support: claimed and built.**
  - README "Supported Operating Systems": Windows, macOS, Linux (lines 140 to 144); Windows build instructions (lines 167 to 190, 284 to 310).
  - CI `cmake-multi-platform.yml` uses self-hosted Windows X64 runners with and without CUDA (lines 52 to 73).
  - Windows wheels exist only as GitHub release assets, without CUDA.
- **Python bindings:** `pypccl` (module `pccl`). The README example uses `Communicator("127.0.0.1:48148", peer_group=0, ...)`, `sync_shared_state` and `all_reduce` (lines 85 to 125).
- **Documentation:** README; `docs/` directory (not read); technical report arXiv 2505.14065 (`w1c` S7).
- **What it provides toward Chorus:**
  - Averaging primitive: fault-tolerant all-reduce over IP; shared-state hash synchronisation to keep peers bit-identical; `peer_group` (README examples, lines 31 to 37 and 90 to 93; `w1c` S7).
  - Membership and topology through a master.
  - No discovery beyond the master address. NAT traversal is not claimed in what was read.
  - No storage, no client.
- **Central elements:** the master process, **(a)**. The README's C++ example connects to `.master_address` (lines 31 to 37); `w1c` S7 reports an "authoritarian" master.
- **Fit (inference):**
  - R1 **not met**: a master must run for the whole run. Whether the role can move between peers is not addressed (`w1c` S7).
  - R3 **unknown**: no relay or NAT traversal found in what was read.
  - R4: synchronous collectives, so it could serve the D38 synchronous mode.
  - R5 and R6: a generic collective over any tensor set. `peer_group` might map onto expert holder groups (untested). A peer in several holder groups would need several groups or communicators (not checked).
- **Full copy / slice:** full copy by all-reduce of pseudo-gradients (inference); slice only if peer groups can be layered (unverified).
- **Risks:**
  - One release (2025-05-21); quiet since 2025-09-12.
  - PyPI lacks Windows wheels, and no Windows CUDA build exists.
  - Master failure behaviour is undocumented (`w1c` S7).

### 11. Templar (Covenant AI; formerly tplr-ai)

- **Repository:** `https://github.com/tplr-ai/templar` redirects to https://github.com/one-covenant/templar (`full_name` "one-covenant/templar", 17:55:22 TST).
- **API record (18:00:23 to 18:00:36 TST):**
  - `license.spdx_id` MIT; `archived` false.
  - `pushed_at` 2026-10-04T16:14:55Z.
  - `releases/latest` v2.1.28, `published_at` 2026-01-21T02:03:50Z. Earlier: v2.1.27 (2026-01-18), v2.1.26 (2026-01-17).
  - Newest commit `0fefc2ad763c`, 2026-10-04T16:14:54Z, "test: harden env initialization in conftest" (a test-only change).
  - The commit before it, `142666f0dd91`, 2026-03-31T02:52:32Z, "Update readme".
  - `open_issues_count` 32 = 28 issues + 4 PRs.
- **Dormant: confirmed.**
  - README at HEAD (fetched 18:04:17 TST), lines 22 to 26: "Templar is dormant". "Templar's decentralized training protocol is not currently active, but may return in the future." Subnet 3 now runs "Crusades", an optimisation competition.
  - The commit diff of `142666f0dd91` (`gh api .../commits/142666f0dd91`, 18:09:55 TST) shows these lines **added on 2026-03-31**.
  - `one-covenant/crusades` (18:09:42 TST): `pushed_at` 2026-04-08T19:08:51Z, `license.spdx_id` null.
- **Package:** the `pyproject.toml` name is `tplr` (`requires-python >=3.11`; depends on `bittensor>=9.10.1`, `torch>=2.7.1`, `boto3`, `s3fs`, lines 10 to 43). PyPI `tplr`: 404 (18:06:42 TST).
- **Licence:** MIT.
- **Language and runtime:** Python 96.7%; Python ≥ 3.11; installed with `uv` or Docker (`w1d` T5).
- **Windows support:** not stated. CI `ci.yml` runs on `ubuntu-latest` only (lines 12, 20, 47). No Windows mention in the README (grep). Not established either way.
- **Python bindings:** a Python code base.
- **Documentation:** README; `docs/miner.md` and `docs/validator.md` (`w1d` S1).
- **What it provides toward Chorus:**
  - Bittensor-coordinated training of full copies in synchronous windows;
  - pseudo-gradient exchange through each participant's own R2 bucket;
  - validator scoring (`w1c` S2; `w1d` S1).
- **Central elements:** (`w1c` S2)
  - Bittensor: **(c)**;
  - per-participant R2 buckets: **(b)**-like, each paid by its participant;
  - the leader validator: a role, **(a)** if we ran it around the clock.
- **Fit (inference):**
  - R1 **partly**.
  - R2 **not met** (Bittensor).
  - R3 **met** in the sense that there are no relays; all exchange goes through object storage.
  - R4 **not met**: synchronous windows.
  - R5 and R6 (slice): **no**.
  - R7: the signed per-peer storage pattern.
- **Full copy / slice:** full copy only.
- **Risks:** dormant since 2026-03-31; tied to Bittensor; not packaged.

### 12. Gensyn RL Swarm, with GenRL

- **Repository:** https://github.com/gensyn-ai/rl-swarm
- **API record (18:00:36 to 18:00:50 TST):**
  - `license.spdx_id` MIT; `archived` false.
  - `pushed_at` 2026-01-05T21:15:30Z.
  - `releases/latest` v0.7.0, `published_at` 2025-11-12T15:52:57Z.
  - Newest commit `9c95410b1ac0`, 2026-01-05T21:15:29Z (merge of "readme_updates").
  - `open_issues_count` 113 = 64 issues + 49 PRs.
  - No `.github/workflows` (contents API: Not Found), so no CI in the repository.
- **Status:**
  - README line 3: "There are no official swarms running right now."
  - It was added by commit `ca40bce55b6a` (2026-01-05T21:02:45Z; commit diff read 18:11:15 TST).
  - The README body still describes CodeZero running on the Gensyn Testnet (lines 7 to 15). The two statements conflict; line 3 is the newer one.
- **GenRL** (https://github.com/gensyn-ai/genrl; API 18:00:50 to 18:01:04 TST):
  - `license.spdx_id` **null**; `pushed_at` 2025-11-12T15:47:35Z.
  - `releases/latest` v0.3.0 (2025-11-12T15:47:35Z); newest commit 2025-11-12T15:46:44Z; 0 issues, 2 PRs open.
  - PyPI `gensyn-genrl` 0.3.0, uploaded 2025-11-06T17:38:24Z; `license_expression` None; no classifiers.
  - **No licence found** for GenRL.
  - `pyproject.toml` depends on `hivemind` (unpinned), `web3` and `eth-account` (lines 18 to 31). The README names "HiveMind" as a `CommunicationManager` backend (lines 29 to 30).
- **Licence:** RL Swarm MIT; GenRL none detected.
- **Language and runtime:** Python 73.1%, TypeScript 18.7% (the `modal-login` web app). Docker is recommended (README lines 99 to 140). CPU-only small models are supported with at least 32 GB RAM (line 48).
- **Windows support:** through WSL, described as "not very well tested and may require you to do some debugging" (README FAQ, line 298).
- **Python bindings:** Python.
- **Documentation:** README; docs.gensyn.ai (not fetched).
- **What it provides toward Chorus:**
  - RL rollout sharing among peers that each keep their own model, over the Hivemind DHT;
  - an on-chain registry and round clock (`w1c` S9).
  - No model averaging.
- **Central elements:** (`w1c` S9)
  - Gensyn Testnet: **(c)**;
  - stage-manager account: **(a)**;
  - Alchemy-hosted wallets: third-party.
- **Fit (inference):** R4 to R6 **not addressed** (no shared model). It is relevant only as a 2025 consumer-hardware swarm running on Hivemind's DHT.
- **Full copy / slice:** neither.
- **Risks:** no official swarms since 2026-01-05; no CI; GenRL has no licence.

### 13. Pluralis Node0, with Agora

- **Node0:** https://github.com/PluralisResearch/node0 (API 18:01:04 to 18:01:18 TST).
  - `license.spdx_id` Apache-2.0; `created_at` 2025-09-16; `pushed_at` 2025-09-23T04:44:01Z.
  - No releases, no tags.
  - Newest commit `32bd084de15d`, 2025-09-23T04:43:54Z ("Restrict uid allocation for clients"); earlier "Turn off volunteer state sharing" (2025-09-20).
  - `open_issues_count` 6, but the search finds 2 issues and 0 PRs; the gap is unexplained.
  - PyPI `node0`: 404 (18:06:44 TST).
- **Agora:** https://github.com/PluralisResearch/agora (API 18:01:18 to 18:01:34 TST).
  - `license.spdx_id` Apache-2.0; `created_at` 2026-05-12; `pushed_at` 2026-07-04T08:42:17Z.
  - No releases.
  - Newest commit `37d29a966528`, 2026-07-04T08:42:04Z (merge "finish-run"); the commit before it is "Conclude the run", 2026-07-04T08:37:29Z.
  - `open_issues_count` 4 = 3 issues + 1 PR.
  - README line 25 (banner alt text): "The Pluralis-8B run has concluded." Then "500B tokens over 7 weeks".
- **Licence:** Apache-2.0 for both. Agora's README credits Hivemind (MIT) (line 445).
- **Language and runtime:**
  - Python 3.11 only: `requires-python = ">=3.11,<3.12"` (Node0 `pyproject.toml` line 5; `agora/pyproject.toml` line 4).
  - `torch==2.7.0`.
  - Both pin `hivemind @ git+...@4d5c41495be0...` (Node0 line 33; Agora line 35), a 2025-05-06 Hivemind commit.
- **Windows support:** "Linux" and "Windows + WSL2" (Node0 README lines 67 to 68; Agora README lines 71 to 72). An inbound port (default 49200) "must be accessible to external connections" (Node0 line 72; Agora lines 77 and 91).
- **Python bindings:** Python.
- **Documentation:** READMEs; Agora has `mkdocs.yml` and `docs/` (not read); paper arXiv 2607.13332 (`w1c` S11).
- **What it provides toward Chorus:**
  - Pipeline-stage training, with periodic partial averaging inside a stage over a Hivemind DHT;
  - an Authorizer that admits nodes and signs credentials (`w1c` S11).
- **Central elements:** (`w1c` S11)
  - Authorizer, health and metrics monitors, and Pluralis reducer nodes: **(a)**;
  - S3 checkpoints written by the operator: **(b)**-like.
- **Fit (inference):**
  - R1 **not met**.
  - R3 **not met** as documented: it requires a public inbound port, and no relays were described.
  - R4: asynchronous averaging within a stage.
  - R5 and R6: stages, not experts; no full copies.
  - R7: the signed-credential pattern.
- **Full copy / slice:** neither directly. Averaging a stage among the workers that hold it is the nearest systems analogue of averaging an expert among its holders (compare SWARM, `w1b` S5). The held part there is a pipeline stage, not an expert.
- **Risks:** event code. Node0 has had no commit since 2025-09-23; the Agora run concluded on 2026-07-04. Neither is maintained as a reusable library (inference). Python 3.11 only, with a pinned 2025 Hivemind.

### 14. Flower (contrast case only)

- **Repository:** https://github.com/flwrlabs/flower (API 18:01:34 to 18:01:48 TST).
  - `license.spdx_id` Apache-2.0; `archived` false.
  - `pushed_at` 2026-10-13T14:59:40Z.
  - `releases/latest` framework-1.39.0, `published_at` 2026-09-28T23:27:26Z.
  - Newest commit `47c6a8273e5e`, 2026-10-13T14:53:08Z.
  - `open_issues_count` 409 = 48 issues + 361 PRs.
- **PyPI `flwr` (18:06:07 TST):** 1.39.0, pure wheel uploaded 2026-09-28T23:26:21Z.
  - `requires_python` ">=3.11, <4.0".
  - The operating-system classifiers list only "MacOS :: MacOS X" and "POSIX :: Linux".
- **Windows:**
  - The wheel is pure Python, so it installs anywhere (inference).
  - The classifiers omit Windows.
  - `framework-test.yml` runs on `ubuntu-24.04` only (lines 22, 47, 180).
  - The install guide has a Windows FAQ entry about terminal output (`how-to-install-flower.rst` lines 76 to 77).
- **Central element:** "SuperLink: A long-running process that forwards task instructions to clients" (`explanation-flower-architecture.rst` line 43, fetched 18:13:53 TST). That is **(a)**. R1 is not met by design; this is the contrast the brief asks for.

### 15. BOINC (contrast case only)

- **Repository:** https://github.com/BOINC/boinc (API 18:01:48 to 18:02:03 TST).
  - `license.spdx_id` LGPL-3.0; `archived` false.
  - `pushed_at` 2026-10-13T13:38:44Z.
  - `releases/latest` `server_release/1.6/1.6.2`, `published_at` 2026-06-12T07:49:21Z.
  - The newest client releases in the list: `client_release/8.2/8.2.15`, a pre-release (2026-06-15T04:44:37Z); `client_release/8.2/8.2.13` (2026-05-03T21:43:51Z).
  - Newest commit `0f611c695763`, 2026-10-12T08:51:00Z.
  - `open_issues_count` 460 = 429 issues + 31 PRs.
- **Language:** C++ 54.9%, PHP 15.1%, C 9.6%, Kotlin 9.1%. Not on PyPI (404).
- **Windows:** `windows.yml` builds on `windows-latest` for x64 and arm64 (lines 49 to 53).
- **Central elements:** the project server, **(a)**; an offline code-signing key (`w1d` T1).

## Summary table

All values come from the API and package-index records in the blocks above, queried on 2026-10-13 between 17:55 and 18:21 TST. "Last commit" is `commit.committer.date` of the newest default-branch commit. "Latest release" is `releases/latest` (`tag_name`, `published_at`) unless a package index is named.

| Candidate | Licence (`license.spdx_id`, 2026-10-13) | Last commit (default branch) | Latest release (date) | Windows support (source, read 2026-10-13) | Archived (2026-10-13) | What it would provide toward Chorus |
|---|---|---|---|---|---|---|
| Hivemind | MIT | 2026-01-04 | 1.1.12 (2026-01-03); PyPI 1.1.12 (2026-01-03) | No native support; WSL "experimental"; no Windows wheel; `setup.py` stops on Windows | false | Private DHT, `p2pd` connections and relays, group averaging, state transfer from peers; no storage or client |
| Hivemind `p2pd` fork | NOASSERTION (MIT and Apache files) | 2023-11-21 | v0.5.0.hivemind1 (2023-11-21) | Not built for Windows (Hivemind `setup.py`) | false | Hivemind's transport (go-libp2p v0.32.1) |
| Petals | MIT | 2024-08-25 | v2.2.0 (2023-09-06); PyPI 2.2.0.post1 (2023-11-20) | WSL only (README); CI Ubuntu and macOS | false | Inference and fine-tuning swarm; partial-weight download from the Hub |
| go-libp2p | MIT | 2026-09-21 | v0.50.0 (2026-09-21) | Tested in CI (ubuntu, macos, windows) | false | Discovery and connections (DHT, AutoNAT, DCUtR, relay v2, pnet over TCP) |
| rust-libp2p | MIT | 2026-10-13 | v0.57.0 (2026-09-11); crates.io 0.57.0 (2026-09-11) | Compile check only (`cargo check` on Windows) | false | As go-libp2p |
| py-libp2p | NOASSERTION (MIT and Apache) | 2026-10-02 | v0.8.0 (2026-09-26); PyPI 0.8.0 (2026-09-26) | Windows CI job (core, demos, utils, wheel; no interop) | false | As go-libp2p, in Python, by its own claims; Beta |
| js-libp2p | Apache-2.0 (npm: Apache-2.0 OR MIT) | 2026-10-11 | npm `libp2p` 3.3.12 (2026-10-10) | Tested in CI (windows-latest) | false | As go-libp2p, on Node.js |
| iroh | Apache-2.0 (crates: MIT OR Apache-2.0) | 2026-10-09 | v1.3.0 (2026-09-28); crates.io 1.3.0 (2026-09-28) | Tested in CI; Windows `iroh-relay` binary in the release | false | QUIC connections, hole punching, own relays carrying traffic, address lookup |
| iroh-ffi (Python) | Apache-2.0 | 2026-07-28 | v1.1.0 (2026-07-16); PyPI `iroh` 1.1.0 (2026-07-16) | `win_amd64` wheel on PyPI | false | Python access to iroh (Alpha), custom relay maps |
| Psyche (`nousnet`) | Apache-2.0 | 2026-03-20 | v0.2.0 (2026-01-21) | None: "only runs on modern Linux distributions" | false | Full stack for data-parallel full copies on Solana and iroh |
| prime-diloco | Apache-2.0 | 2025-04-10 | v0.5 (2024-10-24) | None stated; uses `/dev/shm` (Linux, inference) | false | Synchronous DiLoCo with an elastic process group; full copies only |
| PCCL | MIT | 2025-09-12 | release/v1.0.0 (2025-05-21); PyPI `pypccl` 1.0.0 (2025-05-19/21, no Windows wheel) | Claimed; Windows CI; Windows wheels (no CUDA) only as GitHub release assets | false | Fault-tolerant all-reduce and shared-state hashing; needs a master |
| Templar | MIT | 2026-10-04 (test-only change) | v2.1.28 (2026-01-21) | Not stated; CI Ubuntu only | false | Bittensor-coordinated full-copy training; **dormant since 2026-03-31** |
| RL Swarm | MIT | 2026-01-05 | v0.7.0 (2025-11-12) | WSL, "not very well tested" | false | RL rollout sharing over Hivemind; no model averaging; no official swarms since 2026-01-05 |
| GenRL | null (no licence) | 2025-11-12 | v0.3.0 (2025-11-12); PyPI 0.3.0 (2025-11-06) | Not stated | false | RL framework with a Hivemind backend |
| Node0 | Apache-2.0 | 2025-09-23 | none | Linux; Windows with WSL2 | false | Event client for pipeline training (Pluralis services) |
| Agora | Apache-2.0 | 2026-07-04 | none | Linux; Windows with WSL2 | false | Pipeline training library; run concluded 2026-07-04 |
| Flower (contrast) | Apache-2.0 | 2026-10-13 | framework-1.39.0 (2026-09-28); PyPI 1.39.0 (2026-09-28) | Pure wheel; classifiers macOS and Linux; CI Ubuntu | false | Server-based federated learning (SuperLink, (a)) |
| BOINC (contrast) | LGPL-3.0 | 2026-10-12 | server_release/1.6/1.6.2 (2026-06-12); client 8.2.13 (2026-05-03) | Windows builds in CI (x64, arm64) | false | Server-based volunteer computing ((a)) |

## Corrections to earlier records

1. **`docs/prior-work.md` §6, line 156** (as of 2026-10-07): the `prime` framework (MIT, push 2026-10-06) "is an actively maintained alternative for DiLoCo-style runs".
   - `PrimeIntellect-ai/prime` is now the "Official CLI and Python SDK for Prime Intellect": MIT, `pushed_at` 2026-10-13T00:22:13Z, latest release v0.12.0 on 2026-10-12 (API 17:59:51 TST).
   - The DiLoCo framework is `PrimeIntellect-ai/prime-diloco`: Apache-2.0, newest default-branch commit 2025-04-10, latest release v0.5 on 2024-10-24 (API 17:59:20 TST).
   - So the framework is **not actively maintained**: no default-branch commit in 18 months. This confirms and extends wave 1 (`w1c` S5; `w1d` S3, which also corrects `01-local-averaging.md` A5).
2. **`docs/prior-work.md` §6, Flower row:** now `pushed_at` 2026-10-13T14:59:40Z (was 2026-10-06); newest commit 2026-10-13T14:53:08Z (was 2026-10-01); 48 issues and **361** PRs open (was 354); `open_issues_count` 409 (was 402). The latest release is unchanged: 1.39.0 (2026-09-28).
3. **`docs/prior-work.md` §6, Hivemind row: confirmed, with additions.**
   - Unchanged: 1.1.12 (2026-01-03), push 2026-01-11, newest commit 2026-01-04, 70 issues and 24 PRs, MIT, not archived. "Low-activity maintenance" still holds.
   - Additions: no Windows wheel and no native Windows install path (block 1); its `p2pd` fork has had no commit since 2023-11-21.
4. **`docs/prior-work.md` §5 and §6, Petals rows: confirmed.**
   - Unchanged: v2.2.0 (2026-10-13 query: `published_at` 2023-09-06), push 2024-09-07, newest commit 2024-08-25, 94 issues and 20 PRs.
   - Addition: PyPI's newest version is 2.2.0.post1 (uploaded 2023-11-20), which the earlier record did not mention.
5. **`docs/prior-work.md` §5, Psyche row:** the repository `PsycheFoundation/psyche` redirects to `PsycheFoundation/nousnet` (`w1c` S1; re-confirmed 17:55:22 TST). Maintenance not previously recorded: latest release v0.2.0 (2026-01-21), newest commit 2026-03-20, `pushed_at` 2026-03-24.
6. **OpenDiLoCo's own notice is out of date.** Its README (line 5) says it is no longer maintained and points to `github.com/PrimeIntellect-ai/prime`, which now hosts the CLI. Readers following the link do not reach the framework.
7. **Templar:** wave 1 (`w1c` S2) quoted the dormant notice. It is now dated: added by commit `142666f0dd91` on 2026-03-31. The only later commit (2026-10-04) changes a test file. `tplr-ai/templar` redirects to `one-covenant/templar` (`w1c`, confirmed 17:55:22 TST).
8. **Wave-1 maintenance values re-checked:**
   - Unchanged: go-libp2p, go-libp2p-kad-dht, rust-libp2p (`releases/latest`), py-libp2p, Hivemind, Petals, Psyche, RL Swarm, Node0, Agora and PCCL (`w1a` S4 to S9, S15; `w1c` S1, S7, S9, S11).
   - Updated only by time: iroh `pushed_at` was 2026-10-12T07:23:16Z in `w1a` S9 (queried 17:27 TST) and is 2026-10-13T14:50:08Z here; rust-libp2p `pushed_at` is unchanged at 2026-10-13T14:11:00Z.
   - No wave-1 value was found to be wrong.
9. **Agora duration:** `docs/prior-work.md` §5 and the paper abstract (`w1c` S11) say 40 days. The Agora README banner says "500B tokens over 7 weeks". The sources disagree; not resolved here.

## Could not verify

- **Hivemind averaging restricted to an expert's holders.** That a per-expert `DecentralizedAverager` with its own key prefix would match only holders is inference from the docstring. Not tested, and no code read does it.
- **PCCL peer groups for slices.** Whether `peer_group`, or several communicators per process, can express overlapping holder groups was not checked in code or docs.
- **PCCL NAT traversal and master failover:** not found in the parts read.
- **py-libp2p NAT traversal on Windows,** and its interoperability with go and rust peers. Its Windows CI excludes the `interop` environment.
- **iroh-ffi in practice:** the Python custom-relay support is a `support-matrix.yaml` claim, not tested. Hole punching through a relay in `--dev` mode is still open (`w1a`).
- **Psyche's current status:** docs.psyche.network was not fetched. Whether development continues elsewhere is unknown.
- **prime-diloco's 2026 pushes:** `pushed_at` (2026-07-17) is later than the newest default-branch commit (2025-04-10). That the pushes went to other branches is inference; branches were not listed.
- **Issue-count discrepancies:** rust-libp2p `open_issues_count` 303 against 299 from search; Node0 6 against 2. Unexplained.
- **RL Swarm:** whether community swarms run; the README's "no official swarms" note conflicts with its CodeZero section.
- **Flower native Windows support:** the pure wheel suggests it installs, but no official statement of support was read.
- **BOINC Windows client:** inferred from CI only; the BOINC web site was not read.
- **Python bindings for go-libp2p** other than through the daemon, and for rust-libp2p: not searched outside the repositories.
- **Agora on PyPI:** not queried; the name `agora` may be taken by an unrelated package.

## Query log

All on 2026-10-13, machine clock TST (UTC+3). Raw responses are saved under `sysstudy/sources/w2a/` (`api/_querylog.txt`, `raw/_fetchlog.txt`, `pkg/_pkglog.txt`). Scripts are kept in `sysstudy/scripts_w2a/` (read-only API calls and JSON summarisers, run with `python -I`).

- **17:54:55:** created empty directories `sysstudy/sources/w2a/{api,raw,pkg}` and `sysstudy/scripts_w2a/`.
- **17:55:22:** `gh api repos/{tplr-ai/templar, PsycheFoundation/psyche, PrimeIntellect-ai/prime, learning-at-home/hivemind}`. Found the redirects to `one-covenant/templar` and `PsycheFoundation/nousnet`. Checked the rate limit.
- **17:55:34 to 18:02:03:** `query_repos.sh` over 22 repositories, with the endpoints listed at the top. Per-repository windows:

  | Repository | Window (TST) |
  |---|---|
  | hivemind | 17:55:34 to 17:55:46 |
  | petals | 17:55:47 to 17:56:03 |
  | learning-at-home/go-libp2p-daemon | 17:56:03 to 17:56:27 |
  | go-libp2p | 17:56:27 to 17:57:14 |
  | go-libp2p-kad-dht | 17:57:14 to 17:57:32 |
  | rust-libp2p | 17:57:32 to 17:57:49 |
  | py-libp2p | 17:57:49 to 17:58:21 |
  | js-libp2p | 17:58:21 to 17:58:35 |
  | iroh | 17:58:35 to 17:58:50 |
  | iroh-ffi | 17:58:51 to 17:59:05 |
  | nousnet | 17:59:05 to 17:59:20 |
  | prime-diloco | 17:59:20 to 17:59:37 |
  | pccl | 17:59:37 to 17:59:51 |
  | prime | 17:59:51 to 18:00:08 |
  | OpenDiLoCo | 18:00:08 to 18:00:22 |
  | templar | 18:00:23 to 18:00:36 |
  | rl-swarm | 18:00:36 to 18:00:50 |
  | genrl | 18:00:50 to 18:01:04 |
  | node0 | 18:01:04 to 18:01:18 |
  | agora | 18:01:18 to 18:01:34 |
  | flower | 18:01:34 to 18:01:48 |
  | boinc | 18:01:48 to 18:02:03 |

- **18:02:50:** `gh api repos/R/contents` (root listings) for 16 repositories.
- **18:03:30 to 18:04:29:** raw fetches of READMEs, build files and CI files:
  - Hivemind: `README.md`, `setup.py`, `pyproject.toml`, `requirements.txt`, `run-tests.yml`, `release.yml`.
  - Petals: `README.md`, `setup.cfg`, `run-tests.yaml`.
  - go-libp2p: `README.md`, `go-test.yml`, `go-test-template.yml`, `go-test-config.json`, `go.mod`.
  - rust-libp2p: `README.md`, `ci.yml`.
  - py-libp2p: `README.md`, `pyproject.toml`, `tox.yml`, `tox.ini`.
  - js-libp2p: `README.md`, `main.yml`, `packages/libp2p/package.json`.
  - iroh: `README.md`, `ci.yml`, `tests.yaml`, `wine.yaml`, `release.yml`.
  - iroh-ffi: `README.md`, `README.python.md`, `pyproject.toml`, `support-matrix.yaml`, `wheels.yml`, `ci_python.yml`.
  - nousnet: `README.md`, `build-run-manager.yml`.
  - prime-diloco: `README.md`, `pyproject.toml`, `gpu.yml`.
  - pccl: `README.md`, `cmake-multi-platform.yml`, `publish.yml`.
  - prime: `README.md`. OpenDiLoCo: `README.md`.
  - templar: `README.md`, `pyproject.toml`, `ci.yml`.
  - rl-swarm: `README.md`, `run_rl_swarm.sh`. genrl: `README.md`, `pyproject.toml`.
  - node0: `README.md`, `pyproject.toml`. agora: `README.md`.
  - flower: `README.md`. boinc: `README.md`.
  - All returned HTTP 200.
- **18:05:53 to 18:08:56:** package indexes:
  - PyPI JSON for `hivemind`, `petals`, `libp2p`, `iroh`, `pypccl`, `flwr`, `gensyn-genrl`, `prime`, `zeroband`, `psyche` (200), and `tplr`, `node0`, `boinc` (404);
  - crates.io for `iroh`, `iroh-relay`, `libp2p`, `psyche-core` (200) and `psyche-client` (404);
  - npm `libp2p`; Go proxy `github.com/libp2p/go-libp2p/@latest`.
- **18:09:42:** `gh api repos/one-covenant/templar/commits?path=README.md`; `repos/one-covenant/crusades`.
- **18:09:55:** `gh api repos/one-covenant/templar/commits/142666f0dd91` (diff of the dormant notice).
- **18:10:09:** `gh api orgs/PsycheFoundation/repos?sort=pushed`; listing of `psyche-book/src/enduser`.
- **18:10:39 to 18:10:41:** raw fetches of Psyche `join-run.md`, `client-faq.md`, `quickstart-compute-provider.md`.
- **18:11:15:** `gh api repos/gensyn-ai/rl-swarm/commits/ca40bce55b6a` (diff of the "no official swarms" note).
- **18:11:32 to 18:11:59:** Agora package listing; raw `agora/pyproject.toml`; `gh api repos/learning-at-home/hivemind/commits/{4d5c4149, 213bff98}`.
- **18:12:31 to 18:13:53:** Flower docs listings; raw `framework-test.yml` and `how-to-install-flower.rst`; `explanation-flower-architecture.rst`, saved as `arch.rst` because the first attempt failed on Windows path length. Raw BOINC `windows.yml`.
- **About 18:15:** one transient network failure ("error connecting to api.github.com"). The upstream go-libp2p-daemon query and the iroh-ffi `Cargo.toml` fetch were retried successfully at 18:16:00 and 18:17:53 to 18:18:19.
- **18:19:56:** `gh api repos/PrimeIntellect-ai/pccl/releases/latest` (assets); `repos/learning-at-home/go-libp2p-daemon/contents`; `repos/PrimeIntellect-ai/prime-rl` and its `releases/latest`.
- **18:20:35:** raw `hivemind/averaging/averager.py` (docstring parameters, lines 50 to 83).
- **18:21:14:** `gh api repos/n0-computer/iroh/releases/latest` (assets).
- No WebSearch or WebFetch was used in this strand. No number comes from a search snippet.

**Not covered in this strand:**
- Mechanisms already read in wave 1 were not re-read (cited by block).
- Not read:
  - iroh-ffi `ci_python.yml` (fetched only);
  - Hivemind's docs site; docs.psyche.network; docs.gensyn.ai;
  - the Agora and Node0 `docs/` directories; PCCL `docs/`;
  - js-libp2p mechanisms.
- Moshpit SGD, DeDLOC and SWARM research code: their API records are in `w1b` S3 to S5 (queried 14:36 UTC) and were not re-queried.
- IOTA (Macrocosmos), Hyperswarm/HyperDHT, torchft, Tailscale/Headscale: not evaluated (no API records here). torchft and Hyperswarm are leads only.
- Python bindings for go-libp2p and rust-libp2p outside their repositories were not searched.
