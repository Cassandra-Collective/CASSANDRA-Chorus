# 2026-10-13 · System study: coordinating volunteer training with no server of ours

| | |
|---|---|
| PLAN step | Roadmap step 1.1 (`docs/ROADMAP.md`) |
| Branch | `research/system-study` |
| SRS requirements | D34, D35, D37, D38 (acceptance criteria R1 to R7 in the brief) |
| Status | Report written and audited; awaiting the owner's decisions |

## Problem / Motivation

The owner decided there will be no server of ours (D37): no machine that the owner runs or pays for around the clock. Production training averages asynchronously or in groups, and a synchronous mode is kept (D38). Only our machines relay connections, and the study was to recommend who may write shared state.

Before designing the network (roadmap step 1.3), we needed to know three things:
- how existing systems coordinate volunteer training without a server;
- what each of them still keeps central;
- whether to build on one of them or write our own (D35).

## What Changed

| File | Description |
|---|---|
| `docs/research/2026-10-13-system-study-brief.md` | The brief, revised after the advisor's review: the (a), (b) and (c) classification of central elements, building on the Stage 0 notes, dated maintenance claims. |
| `docs/research/2026-10-13-system-study-notes/` | Seven research notes, one per strand: discovery and connections; averaging without a server; membership and shared state; storage, code trust and bandwidth; systems health; churn handling; contrast cases and file-host exchange. Plus `audit/`, the audit trail. |
| `docs/research/2026-10-13-system-study-report.md` | The report, in the brief's eight sections. |
| `docs/implementations/2026-10-13-system-study.md` | This document. |

## Implementation Approach

The work followed the brief's method and honesty rules.

- **Research:** seven strands in two waves of at most four, after the earlier session-limit failures. Papers were read in raw text; documentation, specifications and READMEs were fetched raw; code was read from shallow clones and never run. Maintenance facts are dated API records with their raw fields.
- **Writing:** one writer synthesized the notes into the report.
- **Auditing:**
  - Four auditors checked every number and factual claim in sections 1 to 6 against the raw sources, and the unverified-items rule. They found 39 problems, all fixed (`audit/fix-log.md`).
  - The 56 changed lines were re-audited and a second, independent unverified-items audit was run. Their 11 findings and 3 section 7 points were fixed by the coordinator, as listed in `audit/README.md`.

## Mathematical / Statistical Details

The report's percentages are relative gaps computed by the researchers from the sources' tables and labelled inference. For example, a loss ratio minus 1, or a ratio of token counts (HALoS: 16.1B / 12.9B = 1.248, about 24.8% more tokens). The audits recomputed them.

## Design Decisions

- **The (a), (b), (c) classification of central elements.** The owner twice chose our own machines over public third-party networks for live use (bootstrap, relays). Designs that need such a network are therefore flagged for the owner, never recommended by default.
- **Two waves of at most four agents, with auditors writing their files early.** This was a lesson from the earlier session-limit failures. During this study a network outage interrupted wave 2 for about 3.5 hours, and the researchers resumed from their saved notes.
- **The report's recommendation is labelled inference** and depends on an interpretation the owner must confirm: that deadline-bounded group averaging meets "groups of available peers" in D37.

## Verification

- **Audit counts:**
  - audit 1: 186 items, 7 problems;
  - audit 2: 139 items, 11 problems;
  - audit 3: 99 OK checks, 15 problems;
  - audit 4: 136 unverified items compiled, 6 problems.

  After the fixes:
  - re-audit A: 118 claims, 3 problems;
  - re-audit B: 88 claims, 6 problems;
  - re-audit C: 2 problems and 3 section 7 points.

  All are fixed. The per-item results are in `docs/research/2026-10-13-system-study-notes/audit/`.
- **The final fixes** were checked by the coordinator against the notes or raw text: NoLoCo's range, Covenant-72B's setting, the PyPI query time, Streaming DiLoCo's 500M ablation model.
- **The report:** 8 section headings; no em or en dashes; summary 639 words (the brief asked for about 600).

**Not verified:**
- the final fixes did not get a third audit round;
- the report's own claim that its recommendation is feasible rests on prototypes not yet run (report section 6).

## Related Docs

`docs/ROADMAP.md` (steps 1.1 and 1.3), `docs/SRS.md` D34 to D38, `docs/research/2026-10-11-stage0-literature-report.md`.
