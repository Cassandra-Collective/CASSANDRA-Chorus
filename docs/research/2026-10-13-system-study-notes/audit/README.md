# Audit trail for the system study report

These files record how `../../2026-10-13-system-study-report.md` was checked against its sources on 2026-10-13. The same two rules as the Stage 0 literature report were audited:

1. Every number and factual claim taken from a source comes from a part of it that was read, and matches it.
2. Anything unverified appears only in section 7.

Line numbers in each file refer to the report as it stood when that audit ran.

| Stage | File | Scope |
|---|---|---|
| First audit | `audit-1-summary-matrix.md` | Header, section 1, section 2 (the requirements matrix): 7 problems |
| First audit | `audit-2-q1-q5.md` | Section 3, questions 1 to 5: 11 problems |
| First audit | `audit-3-q6-s6.md` | Questions 6 to 10, sections 4 to 6: 15 problems at 22 locations |
| First audit | `audit-4-unverified.md` | Rule 2 over sections 1 to 6: 6 problems, plus section 7 additions and removals |
| Fixes | `fix-log.md` | One row per problem (39), all applied |
| Re-audit | `reaudit-A.md`, `reaudit-B.md` | The 56 lines in sections 1 to 6 changed by the fixes, both rules: 3 and 6 problems |
| Re-audit | `reaudit-C-unverified.md` | Rule 2 again, by an auditor who did not see `audit-4`: 2 problems and 3 section 7 accuracy points |

## Fixes after the re-audits

These were applied by the coordinator, without a further audit round, and checked against the notes or raw text as listed.

- **Gossip cost range** (summary, section 5): scoped to pure pairwise gossip. NoLoCo's results are given separately as −1.45% to +0.42% (inference, w1b S8; checked in the notes).
- **"Four precedents"** for file-host exchange: now "whose design is not tied to one cloud region (unlike LambdaML)".
- **Decoupled DiLoCo** (requirements matrix and section 4 table): no longer listed among stale-update methods. Its paper says it applies no stale gradient (App. A, per re-audit B).
- **NoLoCo's wait:** it sets no timeout of its own; that it waits for torch.distributed's default timeout and then raises is labelled as inference (value and behaviour not checked).
- **GitHub rulesets:** the Enterprise-only statement is at line 23 of the page, not 21.
- **Hivemind:** "no Windows wheel" is now dated (PyPI, queried 2026-10-13 18:05 TST; checked in w2a).
- **Measured settings in Q10:** Covenant-72B is added as a second exception to "data centre" (permissionless peers with at least 8 B200 GPUs each, on commodity internet links; checked in the paper text, w1c sources).
- **GASLoC:** "no direct comparison" became "the parts read give no DDP value at 8 replicas".
- **rust-libp2p and js-libp2p rows:** they now say what was not read or checked, with pointers to section 7. A section 7 item was added for rust-libp2p's private networks over QUIC.
- **Section 7 accuracy:**
  - the Agora item is marked closed only in part (§6.4 read; §5.7.1 still open);
  - Stage 0 leads that this study read now have their own list, with two read at abstract level only;
  - a duplicate Psyche item was removed;
  - the opening sentence notes the partial Agora closure.
- **Streaming DiLoCo's 500M setting:** recorded as a read-status addendum in note w1b S14. Audit 2 read §3.3's opening, and the coordinator re-checked it.

## Paths that no longer exist

The audits refer to a temporary session folder (`scratchpad/sysstudy/...`). It held the downloaded sources and is not kept. To repeat a check, fetch the source again by the ID, URL, commit or query recorded in the notes.
