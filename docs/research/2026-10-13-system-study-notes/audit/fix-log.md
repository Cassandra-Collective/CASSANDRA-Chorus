# Fix log: audits 1 to 4 applied to the system study report

Date: 2026-10-13. Report: `docs/research/2026-10-13-system-study-report.md`. Line numbers are those of the frozen pre-audit copy `audit/report_preaudit.md`. Edits made by `audit/apply_fixes.py` (exact old/new strings, each asserted to match once) plus two one-string follow-ups (a one-word summary trim; a HALoS clarification in section 7). Notes edits: one added line each in w2b B1 and w2c T1 (backups in `audit/notes_backup/`; `diff` shows exactly one added line per file; CRLF kept). Nothing committed.

Totals: 39 PROBLEMs (audit 1: 7; audit 2: 11; audit 3: 15; audit 4: 6). Applied: 39. Not applied: 0. Audit 3 P14 was applied in the notes, as instructed, with no report change.

## PROBLEM rows

| Audit | Item | Pre-audit line | Change made |
|---|---|---|---|
| 1 | P1 | 20 | Applied. "Every system read with one shared model keeps one function central"; BOINC "in its server database", Flower "in its SuperLink"; added "flwr-serverless's asynchronous mode has none, so peers can merge different sets (w2c T2)". Wording condensed for the summary budget. |
| 1 | P2 | 24 | Applied: "Every asynchronous method read that applies stale updates keeps the global model on one central holder; only the one-round overlap methods avoid one, by keeping a synchronous all-reduce (w1b F1, F2)." The "no source tests a rotating synchronizer" point now sits in the paragraph's conclusion ("a rotating holder, which no source tests"). |
| 1 | P3 | 24 | Applied with the reconciled wording: "about 0% to 5% against DiLoCo at 8 to 32 workers (inference: loss ratios in w1b S10, log-perplexity ratios in S9)". Same range at L549 (audit 3 P3). The notes' w1b F3 sentence is not changed (task step 4). |
| 1 | P4 | 25 | Applied with the audit's second option: "has four precedents outside a single cloud region". Chosen because it matches the four-row table in Q2 (L126 to L131) and fits the summary budget. |
| 1 | P5 | 38 | Applied, minimally adapted: "they rest on the sections and code paths the notes list as read, not on full reads or an exhaustive search." |
| 1 | P6 | 52 | Applied verbatim (Petals R1: "Partly: the wiki recommends always-on bootstrap machines when servers are unreliable but lets them be skipped; a join needs one listed initial peer alive"). |
| 1 | P7 | 71 | Applied verbatim (FoMoE R1 quotes "central coordinator to manage initialization, broadcasting, and aggregation"; FoMoE §3.1; via note 04a). |
| 2 | P1 | 92 | Applied verbatim (QUIC and WebTransport refuse a pre-shared key; a pnet pool runs over TCP or WebSocket, inference). Consistency extras at L326 and L468 below. |
| 2 | P2 | 113 | Applied verbatim ("volunteer clients in 39 countries, sample "skewed toward the U.S." (§4.3)"). |
| 2 | P3 | 113 | Applied verbatim ("the unconditional rate "from scratch is necessarily lower" (§6)"). |
| 2 | P4 | 121 | Applied verbatim (release v1.3.0; GitHub API, queried 2026-10-13 18:21 TST). |
| 2 | P5 | 133 | Applied verbatim (example configuration refreshes every minute; advises a cone NAT, "For best results"). |
| 2 | P6 | 157 | Applied verbatim (the error is from code; the rejoin at the next epoch is labelled inference, w2b B7). |
| 2 | P7 | 172 | Applied: Plexus locator §5 changed to §6. |
| 2 | P8 | 177 | Applied verbatim ("Of the Hub API endpoints read (model repositories and Storage Buckets), only Storage Buckets list ..."). |
| 2 | P9 | 209, 227 | Applied through the reconciled HALoS wording. L209: Setting "Pythia 160M from scratch, 16 workers"; result "24.8% more tokens than DiLoCo to the same loss at 160M from scratch (inference: 16.1B / 12.9B); the 70M and 410M columns' protocol is not confirmed (section 7)". L227: same figure and arithmetic, with the pointer. Also applied at L536 (section 5). Section 7 (L602) now holds the 70M and 410M figures (+18.6%, +30.9%; inference: 14.0B / 11.8B and 16.1B / 12.3B) as "protocol not confirmed", and notes that the unused reference comparison equals the DiLoCo one at 160M only because DiLoCo also needed 12.9B tokens there (w1b S12). |
| 2 | P10 | 211 | Applied verbatim ("far from converged (inference: losses near 6.5)"). |
| 2 | P11 | 213 | Applied verbatim (Setting "500M (the paper's ablation model, §3.3)"). |
| 3 | P1 | 531, 538 | Applied verbatim: the section 5 table header now says relative gaps in loss or log-perplexity are w1b's arithmetic, inference; L538 "15M, far from converged (inference)". |
| 3 | P2 | 535 | Applied verbatim ("−0.18% to +0.06% in continued pretraining (Tables 1 to 3)"; "−0.3% to −0.9% against a same-step large-batch worker at 4 workers (Table 3); +0.25% at 16 workers (Table 2, 20M)"). |
| 3 | P3 | 549 | Applied with the reconciled wording: "about 0% to 5% against DiLoCo at 8 to 32 workers (inference: loss ratios in w1b S10, log-perplexity ratios in S9), more with more workers within each paper." |
| 3 | P4 | 392 | Applied verbatim ("Decoupled DiLoCo: simulated failures at 2B to 5B dense and a 2.8B-active MoE"). |
| 3 | P5 | 422 | Applied verbatim ("(w1c S4, Q3b; Gauntlet §3.2)"). Consistency extra at L576 below. |
| 3 | P6 | 537, 540 | Applied verbatim: L537 "(2604.21428 v1, Tables 5, 12, 14)"; L540 locator "Tables 1b, 2, 3" and cell "551M: 2-Peer matches DiLoCo at 8 replicas (2.64, Table 3); DDP's 2.64 (Table 2) comes from a one-step run at 16 replicas, so no direct comparison". |
| 3 | P7 | 554 | Applied verbatim ("**What the gate needs** (inference from the standards the sources use; w1b ...)"). |
| 3 | P8 | 346 | Applied verbatim (the three newest commits, 2025-08-03 to 2026-01-04, are packaging, build and import changes). |
| 3 | P9 | 312 | Applied verbatim (2 of Hivemind 1.1.12's 5 files queried; Petals 2.2.0.post1's wheel has none, sdist not queried). |
| 3 | P10 | 359 | Applied verbatim (Training Transformers Together named as the exception). |
| 3 | P11 (a) | 269 | Applied verbatim ("appears to derive from Hivemind's (inference from its code)"). |
| 3 | P11 (b) | 274 | Applied verbatim ("errors out of its loop (code) and, by inference, must rejoin at the next epoch"). |
| 3 | P11 (c) | 276 | Applied verbatim ("handled by restart, not hand-over, in the three systems read (inference)"). |
| 3 | P11 (d) | 278 | Applied ("(inference over the systems read)" after the bold claim). The summary's echo of this claim (L34) now cites "(w2b F5, inference)" for consistency. |
| 3 | P11 (e) | 284 | Applied verbatim (PCCL §4.1 abort and restore; §2.5.3 legal state transitions; "this report reads that as excluding partial rounds (inference)"). |
| 3 | P12 | 304 | Applied verbatim (paid plan; Team and Enterprise per `about-rulesets.md` line 17, Enterprise only per line 21). |
| 3 | P13 | 314 | Applied verbatim ("optionally with MD5 checksums"). |
| 3 | P14 (a) | 275 | Report unchanged. Notes w2b B1: one bullet added after its read-status line: "audit 3 (2026-10-13) read `hivemind/optim/optimizer.py` lines 177 to 178 and 209 to 210 at `4bd43b7` and confirmed the defaults `matchmaking_time` 15.0 and `averaging_timeout` 60.0 and the fallbacks of `next_chunk_timeout` and `allreduce_timeout` to them." Values re-checked in the clone before writing. |
| 3 | P14 (b) | 302 | Report unchanged. Notes w2c T1: one bullet added after its read-status line: "audit 3 (2026-10-13) read `src/tplr/comms.py` lines 602 to 605 and 1470 at `0fefc2a` and confirmed `torch.load(..., weights_only=True)` at both places." Re-checked in the clone. |
| 3 | P15 | 275 | Applied with the reconciled wording: "One place can wait indefinitely: prime-diloco's non-leaders ... (`comms.py` lines 407 to 414; w2b B9). NoLoCo's blocking pair exchange waits until torch.distributed's default timeout, then raises (value not checked; see section 7) (w2b B10)." Section 7 already lists the value (w2b list). |
| 4 | P1 | 227 (also 209, 536) | Applied through the reconciled HALoS wording; see audit 2 P9. |
| 4 | P2 | 275 | Applied through the reconciled NoLoCo wording; see audit 3 P15. |
| 4 | P3 | 26 | Applied, minimally adapted: "Hivemind, Petals, prime-diloco and Templar are dormant or barely maintained; Psyche's repository has had no default-branch commit since 2026-03-20 (status not confirmed; see section 7)". Section 7 already lists Psyche's status (w2a list). |
| 4 | P4 | 253, 448, 525 | Applied: L253 verbatim ("an R2 subscription the owner may end up paying for (free tier exists; whether checkout needs a payment card is not confirmed, section 7): flag against R1"); L448 "Cloudflare R2 (an owner-subscribed account, possibly paid; section 7)"; L525 "an owner-subscribed R2 bucket (possibly paid; section 7; flagged)". |
| 4 | P5 | 491 | Applied verbatim ("provided the Hub enforces `parent_commit` on the server, which is not confirmed (section 7; prototype P4)"); item added to section 7. |
| 4 | P6 | 58, 152 | Applied verbatim: row label "prime-diloco (INTELLECT-1's framework by its own description; section 7)"; L152 cell "not described (INTELLECT-1 paper)". |

## Section 7 changes (audit 4, sections 2 and 5)

| Item | Pre-audit line | Change made |
|---|---|---|
| w1c-16: Hub server enforcement of `parent_commit` | used at 409, 440, 486, 491, 520, 574 | Added under "From w1c" (S15 read the client docstring only; section 4.5's round log depends on it; prototype P4). |
| w1d-13: multi-file Hub commit visibility | used at 261, 574 | Added under "From w1d". |
| w1d-14: Xet deduplication savings | used at 261 | Added under "From w1d". |
| w1a-10: rust-libp2p routing-table persistence | used at 105 | Added under "From w1a" (w1a gap 8); L105 pointer now "(not checked; see section 7)". |
| w1a-11: iroh hole punching through a relay without DNS name or TLS | used at 142 | Added under "From w1a" (w1a gap 7; `--dev` HTTP mode); L142 pointer now "(w1a gaps 1 to 7; not confirmed, see section 7)". |
| PCCL NAT traversal and master failover (verified by w2b B8) | 642 | Removed from the w2a list; added to the "closed by a later strand" list, citing w2b B8 (`03_MasterOrchestration.md`) and where it is used (section 2.1, Q6, section 4.6). |
| Agora all-reduce failure results (verified by w2b B11) | 622 | Moved to the closed list, citing w2b B11 (v1 §3.5.3, §6.4), used in Q6; the w1c line keeps only "Agora's inter-replica divergence (§5.7.2)". |
| NoLoCo item also used in section 2.2 | 587 | "(section 2.2, Q6, section 4.1)". The paragraph now covers four items (two code readings, which are inferences; one documentation reading; one paper reading), and the section 7 preamble (L585) names the closed list as the one exception to "Nothing in this section is used as evidence in sections 1 to 6". |

## Other changes

| Kind | Pre-audit line | Change made |
|---|---|---|
| Task step 5 | 6 | Status: "Draft for the owner; audited 2026-10-13 (every number in sections 1 to 6 against raw sources; unverified items), fixes applied". |
| Summary length | 20 to 38 | The fixes added about 80 words; wording was tightened to hold the summary body (lines between the "## 1. Summary" and "## 2." headings, blank lines and the rule excluded) at 620 words, the pre-audit count. Tightenings: "nothing of ours always on"; "deadline-closed rounds with inputs on a public file host"; "(inference, untested; w1c S15)"; shorter design bullets; "Ledgers, public STUN and the Hub's bucket event stream are class (c) or borderline: flagged, not recommended"; "the owner decides under D35"; "It depends on the R4 reading and four prototypes (section 6)"; Confidence points to "negative findings 1 and 2" instead of restating them; "Low on anything quantitative". No citation, hedge or audit-inserted clause removed. |
| Consistency with audit 2 P1 (not an audit PROBLEM) | 326 | Q9 go-libp2p cell "pnet over TCP" to "pnet over TCP or WebSocket (inference)". |
| Consistency with audit 2 P1 (not an audit PROBLEM) | 468 | "go-libp2p's pnet is TCP only" to "go-libp2p's pnet runs over TCP or WebSocket only, not QUIC". |
| Consistency with audit 3 P5 and audit 4's citation aside (not an audit PROBLEM) | 576 | "hash check or tolerance check (w1c S8)" to "hash check (w1c S8) or tolerance check (w1c S4)". |

## Seen and not changed (observations, not PROBLEMs)

| Source | Line | Why not changed |
|---|---|---|
| Audit 4 NOTE | 409, 440 | Design text (the Closer role; "the next peer's conditional commit succeeds") assumes server-side `parent_commit`; classed NOTE, not PROBLEM. Covered by the L491 caveat, the new section 7 item and dependency P4 at L520. The owner may want a pointer added. |
| Audit 4 observations 1 to 3; audit 3 observation | 420, 571 | L420's mirror host is unnamed; the Hub's conditional commits are the one (b) host doing coordination; P1 needs an outside echo or STUN service (measurement only). For the owner; no rule broken. |
| Audit 1 notes for other auditors | notes only | w1c S2 cites `comms.py` 2239 (actually 2240); w1c S5 line 247 lies outside its recorded read range. Not changed: task step 4 allows only the P14 addenda in the notes. Same for w1b F3's "about 1% to 4%" sentence. |
| Audit 1 P4, secondary | 126 to 131 | The Q2 table lists four storage-only precedents, omitting LambdaML; consistent with the chosen summary wording ("four precedents outside a single cloud region"). |
| Own observation | 208 | The Q4 row "Async Local-SGD, Delayed Nesterov + Dynamic Local Updates (Tables 1 to 3) ... 4 to 16 workers" shows only Table 3's three values (4 workers); audit 2 rated it OK. Section 5 (L535) now gives the Tables 1 to 3 range (−0.18% to +0.06%). The owner may want L208's locator narrowed to Table 3 or its range aligned. |

## Verification run

- `diff report_preaudit.md` against the report: every hunk maps to a row above (summary hunks 20, 24 to 26, 30 to 32, 34, 36, 38 belong to audit 1 P1 to P5, audit 4 P3, audit 3 P11 (d) and the summary-length row).
- Eight `## ` headings unchanged in title and order (lines 18, 43, 83, 384, 529, 565, 583, 696 of the new file).
- No U+2013 or U+2014 in the report (Python count 0). The two notes files keep their pre-existing dashes (w2b 1, w2c 2, same as the backups); the added lines have none.
- Sections 1 to 6 no longer contain "1% to 4%", the HALoS "18.6%" or "30.9%", "19% to 31%", "owner-paid", "pays for", "Not met as documented: always-on", "TCP only", "Two places"; "indefinitely" survives once, for prime-diloco; "w1c S8" survives only for Gensyn's quote (L302) and the hash check (L576).
