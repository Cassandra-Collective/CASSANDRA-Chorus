# 2026-10-14 · System architecture, draft 0.1

| | |
|---|---|
| PLAN step | Roadmap step 1.3 (`docs/ROADMAP.md`) |
| Branch | `docs/architecture` |
| SRS requirements | D34, D37 to D41; principles 2, 6, 7 |
| Status | Draft for the owner's review; not adopted (D41) |

## Problem / Motivation

The system study (step 1.1) recommended a design; the owner accepted its reading of "groups of available peers" (D39) and its write-access model (D40), and deferred adopting the design until the prototypes the owner's machine can run alone report (D41). D41 also asked for the architecture document to be drafted in parallel, so that:

- the prototypes test the rules the design actually needs;
- what remains open is written down, rather than settled implicitly by whoever writes the code first.

## What Changed

| File | Description |
|---|---|
| `docs/ARCHITECTURE.md` | New. Draft 0.1 of the architecture, in 17 sections, built around the study's Option A:<br>• requirements;<br>• overview;<br>• peer roles;<br>• keys and accounts;<br>• shared state;<br>• the round protocol and log entries;<br>• the merge rule and agreement;<br>• work units and the holder-count rule;<br>• storage and host limits;<br>• connections;<br>• failures;<br>• code trust and versioning;<br>• the trust model;<br>• a draft Gate N1b pre-registration;<br>• twelve owner decisions (AD-1 to AD-12);<br>• a table of what waits on which prototype. |
| `docs/ROADMAP.md` | Step 1.3's note records that draft 0.1 exists and is not adopted. |
| `docs/implementations/2026-10-14-architecture-draft.md` | This document. |

## Implementation Approach

- **Every statement is labelled.**
  - **Rule:** proposed, binding once adopted.
  - **Waits on Pn:** a prototype can change it.
  - **AD-n:** an owner decision.
  - **Inference:** reasoned, not shown.

  The labels keep D41's ordering visible: nothing here is the design until the owner adopts it.
- **The study's Option A is restated as concrete protocol rules,** not as a description:
  - the entry layout;
  - the close and counted-set rules;
  - the publisher order;
  - the part cut for files and hashes;
  - the merge's arithmetic.
- **P6 and P9 findings are written in as rules where they are already clear**, and marked as waiting where only toy-scale results exist:
  - the canonical order of the counted set;
  - IEEE division in the merge;
  - float64 outer state;
  - per-part canonical hashes;
  - signatures over exact file bytes with a domain prefix.
- **Gate N1b** is drafted here because the roadmap's decisions table places it in step 1.3. Its allowance and primary reading are owner decisions (AD-12).

## Mathematical / Statistical Details

The merge formula, the canonical hash and the commit-rate arithmetic are stated in the document itself:

- section 7: A = (Σ n_i W_i) / (Σ n_i) over the contributors, in float64, with IEEE division, then the outer step;
- section 7.2: the part hash, and the model hash over the sorted (part ID, part hash) list;
- section 6.2: 7 commits per round, 48 rounds per day, 336 log commits per day.

The derivations are in `docs/implementations/2026-10-14-solo-prototypes.md` and `docs/implementations/2026-10-08-coordinator.md`.

## Design Decisions

- **A designated publisher with a fallback order**, instead of a race, because a race would waste several large home uploads per round. Inference, for review.
- **The counted set is fixed by the log, never by a peer's downloads.** A peer that cannot fetch an update adopts the checkpoint instead of merging a subset. This keeps one model at the cost of that peer's round (Psyche's behaviour, study Q6).
- **A proposal to merge on the CPU only.** The merge is cheap, and pinning the device removes the class of differences P6 found on the GPU.
- **Router rows travel with their expert** in files and hashes (the study's section 4.1), so a slice holder needs only the shared part and its own experts.
- **One combined log entry per member and round**, so the log's commit rate is 7 per round, not 17, against the Hub's undocumented commit limits.
- **The open pool (Phase 6) is explicitly not designed.** The trust model covers the pilot (D40) and notes what strangers would add.

## Verification

- Every number from the prototypes in the draft was checked against the prototype outputs of 2026-10-14:
  - the CUDA division count (6,679,936 of 10 million);
  - the toy-scale P6 counts (1; 114 and 96; 219 and 325);
  - P9's seven cases.
- Statements from the study were checked against its report sections as cited: Q3, Q5, Q6, Q7, Q8 and 4.1.
- SRS references were checked: D11 is the router-row rule, and the merge requirements are S0-F-08 to S0-F-10.
- Stage 0's seeded data streams were checked in `cassandra_chorus/sim/harness.py`.
- No em or en dashes.

**Not verified:** the draft's feasibility rests on P0, P3, P4, P5 and P6 at full scale, which had not reported when it was written (section 16 of the draft).

## Related Docs

`docs/research/2026-10-13-system-study-report.md`, `docs/implementations/2026-10-14-solo-prototypes.md`, `docs/ROADMAP.md`, `docs/SRS.md`.
