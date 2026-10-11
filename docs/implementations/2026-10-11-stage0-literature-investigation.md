# 2026-10-11 · Stage 0 literature investigation

| | |
|---|---|
| PLAN step | After step 12; part of reconsidering the architecture (decision D28). The project is parked |
| Branch | `stage0/literature-investigation` |
| SRS requirements | S0-N-07 (state limits); decision D28; SRS section 10 (relation to prior work) |
| Status | Written, audited against the papers' raw text, and re-audited after fixes |

## Problem / Motivation

Stage 0 closed as a negative result: sliced training ended +10.8% in test bits per character behind centralized training on text8, against an allowance of 5%. The gap splits into three measured steps:

- local averaging, +6.1%;
- partial updates, +1.4%;
- masked routing, +3.2%.

The owner asked for a literature investigation to understand the failure, not to defend the method. The brief is `docs/research/2026-10-11-deep-research-prompt.md`. The earlier survey (`docs/prior-work.md`, 2026-10-07) read most papers only as abstracts or through a summarizing tool, so its claims could not support a discussion of why the method lost quality.

## What Changed

| File | Description |
|---|---|
| `docs/research/2026-10-11-deep-research-prompt.md` | The research brief: six questions, method and honesty rules, the eight required report sections. Written in the previous session. |
| `docs/research/2026-10-11-stage0-literature-report.md` | The report: summary, an 18-paper reading list in reading order, findings for each question, a remedies table, a closest-prior-work table, gaps the harness could answer, unverified leads and a search log. |
| `docs/research/2026-10-11-literature-notes/01-local-averaging.md` to `06-round2-citation-chase.md` | The eight research notes behind the report, one per strand. Each records per paper the version read, the sections read, the numbers with their locations, and a query log. |
| `docs/research/2026-10-11-literature-notes/audit/` | The audit trail: first audit (8 files), the fix log (71 problems), two re-audits of the changed lines and an independent re-audit of the unverified-items rule, with a README. |
| `docs/implementations/2026-10-11-stage0-literature-investigation.md` | This document. |

No code, configuration or existing document was changed.

## Implementation Approach

**Research.** Seven strands ran in parallel, each writing its own notes file:

- 01: local averaging (question 1);
- 02a: how MoE experts specialize, and random or hash routing (question 2, mechanisms);
- 02b: federated and merged MoE, and router remedies (question 2, federated);
- 03: partial and sub-model training (question 3);
- 04a: SPES in full text, plus papers citing SPES or FlexOlmo (question 4);
- 04b: MoE-DisCo, BTX, BTM, DiPaCo, SMALLTALK LM, DEPT and Learning@home (question 4);
- 05: whether our text8 baseline and the 5% allowance are sensible (question 6).

Remedies (question 5) were split across the strands by the cost they target. One targeted round (06) then chased the papers citing FoMoE, Gating Dropout, MaskMoE, HARC, FedAlign-MoE and DDOME, and checked FoMoE's details.

**Reading rule.** Every number had to come from raw paper text the researcher read: the arXiv PDF converted with `pdftotext -layout`, or arXiv HTML. Search results and summarizing page fetches were used only to find papers, because the earlier survey had been caught with a wrong summarized number. Each number carries a location and the version read. Arithmetic is labelled "(inference)".

**Writing.** One writer produced the report from the notes. It followed the brief's eight sections, and anything the notes could not verify went to section 7 only.

**Audit.** The report was then audited in two passes; the files are in `docs/research/2026-10-11-literature-notes/audit/`.

1. A first audit, in eight parts, checked every paper-attributed number in sections 1 to 6 against the raw text and the recorded read status, and checked the unverified-items rule. They found 71 problems, mostly derived numbers without an "(inference)" label, plus a few wrong values and locations. All 71 were fixed (`fix-log.md`).
2. Two auditors re-checked the 104 lines changed by those fixes (about 780 numbers), and a third repeated the unverified-items audit independently. The few remaining problems were fixed directly:
   - Gating Dropout's two quotes are cited to §3;
   - a rounding slip, +41.6% corrected to +41.5%;
   - a misstated read status in the disagreement table;
   - two wrong section references (Lo et al. §1 and §4.1; FoMoE §6.2);
   - a missing inference label;
   - a MedMix figure that came from an auditor's reading rather than the notes, removed;
   - section 7 gained the figure-only results and two "inner state not stated" items;
   - DES-LOC's legend values were resolved from its §4.1 ("means and standard deviations computed over the last round").

## Mathematical / Statistical Details

- **Relative gaps.** A percentage gap between a method with perplexity a and a baseline with perplexity b is ln(a) / ln(b) − 1, the relative difference in mean cross-entropy, so it compares with our bits-per-character gaps in kind. It assumes the paper's perplexity is exp(mean cross-entropy).
- **Holder counts under the coverage policy.** Every expert is dealt once, in turn; then each worker's remaining capacity is filled with random experts it does not hold; the slices are redrawn every round. With 4 workers holding 4 of 8 experts, a simulation of 100,000 draws gives P(1 holder) = 0.296, P(2) = 0.445, P(3) = 0.222 and P(4) = 0.037 (mean 2). The code is in the audit README.
- **Parameter counts.** Experts are SwiGLU with three bias-free matrices. Expert parameters are 3 × 384 × 768 × 8 × 6 = 42,467,328 of 46,050,432 (92%). Active per token: 3,583,104 non-expert + 2/8 of the expert parameters ≈ 14.2M. A partial-arm worker trains 3,583,104 + 4/8 of the expert parameters ≈ 24.8M, about 54%.

## Design Decisions

Owner decisions on 2026-10-11:

- **Depth.** The DiLoCo family and the MoE-mechanism anchors were read section by section (method, results tables, relevant ablations). Full text was required only where the brief demands it (SPES and the other closest methods).
- **Notes location.** The notes are kept in the repository as the report's audit trail, rather than in a temporary folder.
- **Extra round.** One extra round of citation chasing was run on the six papers closest to masked routing.
- **Scope.** The platform vision (weekly research pools, a client, auto mode) was kept out of the report, for a separate study.
- **Commit.** Committing the folder, and keeping the audit logs with the notes, was approved after the report was finished.

Coordinator decisions, stated for review:

- Venues known only from OpenAlex or DOI records count as unconfirmed and are listed in section 7.
- FoMoE's "Table 3" was resolved from raw text: it is the parent caption of Tables 4 and 5 and has no centralized number.
- The notes files are kept as written, with one added line where a correction applies (below). To keep the house style, the 99 en and em dashes in the notes and audit files were replaced: by "to" in ranges, a hyphen in names, a middle dot in one title, a colon in one sentence and "n/a" in empty table cells.

**Corrections found during the work:**

- **Holder counts.** The brief described each expert as held by 2 workers. The `coverage` policy redraws slices every round, so an expert has 1 to 4 holders, with a mean of 2.
- **Model size.** The coordinator's estimate given to the researchers was about 10M active parameters. It assumed two-matrix experts, and the experts are SwiGLU with three matrices. The report's header states the correct counts, and five notes files carry a one-line correction at the top. `docs/stage0-report.md` is unaffected; it gives only the 46.05M total.

## Verification

Run on 2026-10-11 on the reference laptop. No GPU, model or training was involved.

- **Mechanical checks** (the script is described in the audit README), on the final report:
  - all 157 arXiv IDs returned a title from the arXiv API matching the report's text;
  - all 150 links returned HTTP 200;
  - the 8 section headings and the 18 reading-list entries are present;
  - the novelty-language scan found only phrases such as "the first three" and "first moment".
- **Number audit:** every paper-attributed number in sections 1 to 6 was checked against raw text by an auditor, then every changed line was re-checked. See the audit README.
- **Unverified items:** two independent audits; nothing unverified is stated as fact outside section 7.
- **Repository:** no tracked file was modified (`git diff --stat` empty before staging).

**Not tested:**

- Section 8 (search log) and section 7 (unverified leads) are records, not evidence, and were not number-audited.
- Search coverage has stated limits (section 8):
  - no GitHub code search;
  - no Chinese-language venues;
  - Google Scholar was not reachable;
  - citation indexes lag on 2026 preprints.
- The notes files contain some attributed quotations of 20 to 30 words; the report keeps quotations under about 15 words.

## Related Docs

- `docs/research/2026-10-11-deep-research-prompt.md` (the brief)
- `docs/stage0-report.md`, `docs/stage0-closeout.md`
- `docs/prior-work.md` (the earlier survey; section 3 of the report lists where it is corrected)
- `docs/SRS.md` decision D28
