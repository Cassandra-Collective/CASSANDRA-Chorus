# 2026-10-25 · English pretraining sources survey

| | |
|---|---|
| PLAN step | None. Roadmap 2.1, issue #53 |
| Branch | `research/53-english-sources` |
| SRS requirements | D32; evidence for OD-3 (#24), OD-4 (#25), OD-7 (#28) and OD-10 (#31) |
| Status | Verified on the owner's Windows laptop: primary-source review, document checks and all 339 repository tests passed |

## Problem / Motivation

Chorus needs English pretraining text with documented reuse rights and evidence of human authorship. A dataset's permissive compilation licence does not establish rights in its underlying documents. This survey supplies evidence for the owner's licence and authorship decisions without taking those decisions.

## What Changed

| File | Description |
|---|---|
| `docs/implementations/2026-10-25-english-pretraining-sources.md` | Precommitted research method, scope, decisions and final verification record |
| `docs/research/2026-10-25-english-pretraining-sources.md` | Fifteen-candidate table, detailed source records, primary legal-text obligations, conditional volume totals, unresolved measurements and owner questions |

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
- Open for the owner: interaction between current service-access conditions and historical CC grants. The current Stack Exchange dump requires a no-LLM-training affirmation; reject that route without making the affirmation. No decision about historical releases is taken here.
- Engineering default for review: use Dolma v1.6's separately documented Gutenberg and Wikimedia components as quantified leads, not the entire mixture. Use pinned v1.0.0 cards for FineWeb and FineWeb-Edu to avoid conflating later releases. Keep the Gutenberg acquisition-date discrepancy visible rather than choosing a date silently.
- Explicit task instructions override CONTRIBUTING's issue-comment and unresolved-choice workflows: no issue comments, labels or assignments; record open decisions here and in the draft PR. Do not modify SRS.md, ROADMAP.md, ARCHITECTURE.md or assistant-spec.md.

## Verification

Baseline and plan order: web access worked; `origin/main` resolved to the required `a30dd6a`; the fresh worktree is outside OneDrive; no AGENTS.md was found in the repository or checked parent locations. This plan was committed alone as `cedf429`, with the required plan message, before the research note was written. No baseline blocker occurred.

Source audit on 2026-10-25: fifteen candidates examined; nine conditional keeps (S01 to S09), six rejected offerings/access routes (S10 to S15), no unconditional training approval. The note defines fifty-one primary reference targets, representing fifty resources after ignoring fragment anchors. All fifty-one returned HTTP 200 through direct bounded GET requests, including the actual legal codes, official statutory text, publisher terms, raw corpus cards and manifests. Fifteen additional linked home/issue targets also returned HTTP 200. Each of the three cited HTML fragment anchors was checked against the fetched document IDs and passed after correcting the Dolma table anchor. Search snippets were not accepted as licence evidence.

Licence coverage checked against original legal text:

| Candidates | Primary rights evidence read |
|---|---|
| S01 | CC BY-SA 3.0 section 4, ODC-By scope and section 4; historical Wikimedia licence transition and imported-text exceptions. GFDL route excluded and its full text not examined |
| S02 | Wikisource work/contribution/translation policy, CC BY-SA 4.0 sections 2 to 4, work-specific PD requirement; validated scan workflow |
| S03 | Full Project Gutenberg License normative sections 1.C to 1.F, compilation versus book rights, and ODC-By wrapper |
| S04 | Publisher's dedication scope and CC0 1.0 waiver, fallback and limitations |
| S05 | Repository Apache-2.0 text, including redistribution/NOTICE conditions, alongside original Gutenberg rights |
| S06 | Official 2024 US Code sections 101 and 105 and GovInfo's third-party-rights warning |
| S07 | Publisher's bulk-data PD claim, Public Domain Mark's status/territory limits and CourtListener terms; no CC0 grant inferred |
| S08 | Official OGL v3.0 text and publisher's additional-source distinctions; EUR-Lex/Westlaw subsets excluded from the proposed OGL-only selection, additional instruments not independently audited |
| S09 | PMC article-level rights and cloud-service conditions; CC BY 4.0 and CC0 texts for proposed subset; CC BY-NC 4.0 and CC BY-ND 4.0 legal-code limits checked for exclusions. Other versions/bespoke terms excluded, not silently accepted |
| S10 | CC BY-SA 2.5, 3.0 and 4.0 legal texts, publisher revision boundaries and current restrictive download instructions |
| S11 to S15 | Common Crawl terms and ODC-By's database-versus-content scope where applicable; no underlying page licence inferred from either |

Calculations were recomputed with Python: byte-based Gutenberg estimate 4.08 to 6.80B; Wikimedia 3.24 to 5.40B; gross sum 7.32 to 12.20B. PG-19 training word-unit conversion gives 2.3677634484 to 2.9597043105B before rounding. C4 original approximate text size gives 150 to 250B. Only the first two conditional components enter the gross retained-lead sum; PG-derived alternatives and rejected overlapping mixtures are not added. No filtering retention or deduplicated usable amount was invented. FineWeb's rounded row sums reproduce its published disk total; token rows sum to 15,353.2B versus the published 15,352.9B total, a difference consistent with row rounding and explicitly noted.

Document checks: parsed Markdown with `markdown-it-py` using CommonMark plus tables; fifteen source rows and fifteen detail sections; four tables; all reference uses resolve; local plan link exists. Python's equivalent of `grep -nP '[\x{2013}\x{2014}]'` found no prohibited dashes in either written document. `git diff --check` passed. Only this plan and the research note are intended for the final diff; protected decision/specification documents were not edited.

Required repository tests: `python -m pytest` completed with **339 passed, 2 expected warnings** in 366.15 seconds, including GPU tests. Hardware: Intel Core i7-13650HX, NVIDIA GeForce RTX 4070 Laptop GPU with 8188 MiB reported by `nvidia-smi`. Software: Windows, Python 3.13.14, PyTorch 2.12.1+cu126, pytest 9.0.2; CUDA available. Warnings are emitted deliberately by the warning-capture tests. Model size, research training dataset and random seeds: not applicable; no training experiment was performed. Tests use the repository's existing fixtures and configurations.

Unverified measurements are enumerated in the note's "What could not be verified" section: all actual Chorus token counts; retention, authorship contamination and overlap; S01/S03 compressed component bytes, original dates and acquisition cutoff precision; S02/S04 selected text sizes/date ranges; S05 earliest original date and download bytes; S06 to S09 rights-clean English counts/bytes/tokens/date ranges; S10 allowed training access and dump size/date; S11 licensed English fraction; S12 version equivalence; S13 actual archive bytes and unrounded totals; S14 archive bytes and exact final-crawl reconciliation; S15 original writing dates and rights-clean proportions. Public statistics were verified as publisher claims, not independently reproduced from full corpora. Statutory review uses the explicitly cited 2024 edition; later amendments were not verified through the unavailable attempted newer-edition endpoints.

No corpus sample was needed or left to delete. Only bounded documentation, legal texts and metadata manifests were fetched, under `C:\Users\senso\chorus-research\issue53`, outside the repository and OneDrive. No fetched executable content was run. The final publication step is to commit the two documents, push only `research/53-english-sources`, and open one draft PR using the repository template, with all owner questions retained. No issue comments, labels, assignments or merge are authorized or performed.

**Not tested:** corpus downloads, document-level rights, human-only certification, deduplication, tokenizer measurements, ingestion or training. This task does not deliver a Turkish survey (#54), post-AI web text policy (#55), or download/pipeline work (#56).

## Related Docs

- [Issue #53](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/53)
- [CONTRIBUTING.md](../../CONTRIBUTING.md), sections 3, 4, 5 and 8
- [SRS](../SRS.md), D32
- [Roadmap](../ROADMAP.md), step 2.1
- [Assistant specification](../assistant-spec.md), section 6
- [OD-3](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/24), [OD-4](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/25), [OD-7](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/28), [OD-10](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/31)
- Planned [research note](../research/2026-10-25-english-pretraining-sources.md)
