# 2026-10-25 · English pretraining sources survey

| | |
|---|---|
| PLAN step | None. Roadmap 2.1, issue #53 |
| Branch | `research/53-english-sources` |
| SRS requirements | D32; evidence for OD-3 (#24), OD-4 (#25), OD-7 (#28) and OD-10 (#31) |
| Status | Planned. Research and verification pending |

## Problem / Motivation

Chorus needs English pretraining text with documented reuse rights and evidence of human authorship. A dataset's permissive compilation licence does not establish rights in its underlying documents. This survey supplies evidence for the owner's licence and authorship decisions without taking those decisions.

## What Changed

| File | Description |
|---|---|
| `docs/implementations/2026-10-25-english-pretraining-sources.md` | Precommitted research method, scope, decisions and final verification record |
| `docs/research/2026-10-25-english-pretraining-sources.md` | Planned candidate table, source details, licence obligations, conditional volume totals and owner questions |

## Implementation Approach

Start from `origin/main` at `a30dd6a` in the fresh worktree `C:\Users\senso\chorus-dev\research\53-english-sources`. Read CONTRIBUTING.md first. Commit this plan alone before writing the survey.

Find candidates through the original publishers, official corpus repositories and author papers. Aim for 10 to 20 candidates across encyclopedia text, public-domain books, government and legal texts, and filtered web text. Include common training corpora as negative controls when their underlying text rights are not established. Record omitted families and why the scope cap excludes them.

For every candidate, read the primary licence text itself, not a search snippet or model summary, and the publisher's description of what it covers. Record exact licence name and version; attribution, share-alike, non-commercial, no-derivatives and notice requirements; other restrictions and exceptions; compilation versus underlying document rights; download format and size; documented text dates; human authorship evidence and bot, translation and synthetic risks; and any model generation, filtering or classification used during construction. Cite each factual quantity with its URL and access date. Mark missing measurements explicitly.

Give one table row per candidate, followed by detailed records. Use keep, conditional keep or reject with reasons. A conditional keep is evidence for an owner decision, not permission to train. Prefer fixed older snapshots where documented, while recording that older does not prove human authorship. Do not resolve whether model filtering violates D32.

Do not download whole corpora. Read documentation, licence pages, manifests and papers only. If a sample becomes necessary, keep its total below 100 MB outside the repository and OneDrive, and delete it afterwards. No executable content from sources will be run. No public functions or classes change: their contracts are not applicable to this research-only task.

## Mathematical / Statistical Details

No tokenizer exists yet. Label all conversions `Inference:`. For published English word counts, use a planning interval of 1.2 to 1.5 tokens per word. For published uncompressed plain-text bytes, use 3 to 5 bytes per token. These are explicit sensitivity assumptions, not measured tokenizer performance or sourced facts. Do not convert compressed archives, document counts or mixed markup sizes into tokens. When publisher token counts are available, name the publisher's tokenizer and do not present those counts as Chorus tokens.

Keep totals separate by public domain/CC0, attribution-only, share-alike and other or unresolved rights. Separate quantified eligible envelopes from unknown volumes and rejected corpus sizes. Do not sum overlapping editions or derivative datasets. State that deduplication, rights checks, authorship checks and quality filtering have unknown retention; give conditional ceilings and conservative bounds rather than inventing a retention percentage.

## Design Decisions

- Engineering default for review: cap the survey at 20 candidates; favour documentation that permits reproducible rights and size checks over a longer list.
- Open for the owner: acceptable licences under OD-3, including territorial public-domain limits, attribution and share-alike obligations and possible implications for weights under OD-10. Conservatively hold affected sources until decided.
- Open for the owner: which authorship evidence is sufficient under OD-4, including older snapshots, curated sources and residual contamination. Conservatively make no claim that any whole corpus is verified human-only.
- Open for the owner: whether model-based filtering or classification is compatible with D32 when the training text itself is not generated. Record this separately from generated content.
- Open for the owner: final tokenizer and token measurement under OD-7. Use transparent intervals only.
- Explicit task instructions override CONTRIBUTING's issue-comment and unresolved-choice workflows: no issue comments, labels or assignments; record open decisions here and in the draft PR. Do not modify SRS.md, ROADMAP.md, ARCHITECTURE.md or assistant-spec.md.

## Verification

Planned: check every retained candidate against primary licence text and publisher documentation; count candidates examined and retained; audit every numerical claim and calculation; check overlap and licence-class totals; list every unverified number; check Markdown links and absence of U+2013/U+2014 in both written files; run `git diff --check` and the required `python -m pytest`; confirm only the two intended documents changed; open one draft PR from the repository template after pushing only this branch.

Initial checks: web access works; `origin/main` resolves to the required `a30dd6a`; the fresh worktree is outside OneDrive; no AGENTS.md was found in the repository or checked parent locations. No baseline blocker observed so far.

Hardware and software inventory, test results, source counts and unresolved measurements will be recorded here after research. Model size, training dataset and random seeds: not applicable; no training or experiment is planned.

**Not tested:** corpus downloads, document-level rights, human-only certification, deduplication, tokenizer measurements, ingestion or training. This task does not deliver a Turkish survey (#54), post-AI web text policy (#55), or download/pipeline work (#56).

## Related Docs

- [Issue #53](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/53)
- [CONTRIBUTING.md](../../CONTRIBUTING.md), sections 3, 4, 5 and 8
- [SRS](../SRS.md), D32
- [Roadmap](../ROADMAP.md), step 2.1
- [Assistant specification](../assistant-spec.md), section 6
- [OD-3](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/24), [OD-4](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/25), [OD-7](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/28), [OD-10](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/31)
- Planned [research note](../research/2026-10-25-english-pretraining-sources.md)
