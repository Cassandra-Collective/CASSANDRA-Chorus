# Policy options for web text after AI writing tools

Evidence for [issue #55][ISSUE] and [OD-4, issue #25][OD4], not a policy decision. All linked evidence was accessed on **2026-10-25**. The [implementation plan](../implementations/2026-10-25-ai-era-web-text-policy.md) was committed first. D32 still requires human-written, open-licensed pretraining text and forbids other models' outputs. This research note is not training data.

**Inference:** older captures reduce exposure to recent generators but discard later human writing; curation can recover documented human text but has an unmeasured selection cost; accepting a residual preserves the largest candidate envelope but cannot establish human-only data through detection. Neither survey measures a positive amount of fully audited usable text. OD-4 must settle what evidence is sufficient before any envelope becomes a training commitment.

## Inputs, units and what the comparison can measure

The required notes existed on origin and were read as Git blob text, without merging their branches:

| Input | Branch and exact commit | Sections used |
|---|---|---|
| [English survey, issue #53][EN] | `research/53-english-sources`, `e637be6b87af34d065f95c7511e7d65ed0f5d8b1` | Candidate records S01 to S15; licence-class totals; dates and overlap limits |
| [Turkish survey, issue #54][TR] | `research/54-turkish-sources`, `c1db10da0fd4aa64d7b4de7b9a5e25ad0c52f9b0` | Candidate records T01 to T13; licence-class totals; historical alternative and repetition scenarios |

These are research-branch findings, not merged source approvals. Their immutable links remain usable while the survey PRs are pending. Corpus publishers and original papers were read directly as text for the key quantities below. No corpus bodies, samples or training data were downloaded; the ParlaMint document read is a descriptive header. Search snippets were discovery aids only.

All derived volumes below are **Inference:** using the surveys' sensitivity assumptions. B means billion estimated tokens, not measured Chorus tokens. English uses uncompressed text bytes divided by 5 to 3, or 1.2 to 1.5 tokens per published word-level unit for PG-19. Turkish uses text characters divided by 5 to 2, or 1.5 to 2.5 tokens per published word-level unit. These assumptions are not confidence intervals, calibrated tokenizers or guaranteed bounds. Compressed archives, XML and metadata storage are not converted. Publisher token counts keep their own units. [EN][TR]

A policy exclusion means a candidate is held out under the stated rule, not that all its prose is synthetic or permanently unusable. Conditional retention means only that the policy permits investigating it: rights, authorship, extraction, deduplication and holdout checks can still remove any part. Unknown volume is not measured zero. No retention fraction is invented.

## The cutoff is a risk window

Tool availability and web prevalence answer different questions. A release date establishes an opportunity to produce text; it does not establish adoption in every language or the first synthetic webpage.

| Dated primary evidence | What it establishes | What it does not establish |
|---|---|---|
| OpenAI released the full GPT-2 model on **2019-11-05**. [R1] | Public access to a generator before current chat tools | A beginning of all machine writing, or a human-only guarantee for earlier captures |
| GPT-3 API private beta announced **2020-06-11**. [R2] | Commercial text-completion access before ChatGPT | General availability on that date or web contamination prevalence |
| API waitlist removed on **2021-11-18**, in supported countries; publisher reported tens of thousands of developers already using it. [R3] | Broader developer access and evidence of use | A worldwide or Turkish adoption threshold |
| ChatGPT free research preview launched **2022-11-30**. [R4] | A public conversational route to generating text | A clean boundary between human and machine writing |
| Google began opening Bard access on **2023-03-21**, initially in the US and UK. [R5] | Expansion of public chat interfaces beyond one provider | Universal language or country availability at launch |

**Inference:** distinguish an earlier generator-access interval, **2019 to 2021**, from the expansion of public chat interfaces in **late 2022 to early 2023**, anchored by the releases above. These are overlapping risk periods, not an onset estimate with a statistical confidence interval. Older machine translation, templates and other generation remain possible before them. A pre-ChatGPT rule addresses recent chatbot exposure, not all model output. This note selects no cutoff.

Measurements exist, with important population limits:

- **Dolezal et al., preprint dated 2026-04-14:** report roughly **35%** of newly published websites classified as AI-generated or AI-assisted by mid-2025. Their sample spans **August 2022 to May 2025**, uses oldest available Internet Archive captures, retains English and selects the longest paragraph, excluding pages whose selected paragraph has fewer than **100 words**. It uses Pangram v3 classification. This is a detector-based estimate for that archived-page population, not a known fraction of all web tokens. The paper's near-zero pre-ChatGPT classification does not certify clean early data: its own robustness appendix reports failures on older completion models. Turkish is absent from its language robustness tests. [P1] (sections 1, 3.1, 3.3 and appendix A)
- **He et al., preprint submitted 2026-04-30:** DeGenTWeb reports **2.1%** LLM-dominant sites in its late-2022 cohort versus **29.4%** in its early-2025 cohort. Cohorts use the earliest archival date among sampled pages as a proxy for site creation; this is not the same sites measured repeatedly over time. It studies roughly **100,000 sites**, selects English pages with sufficient prose and aggregates page scores to classify sites. Its validation uses **144 sites**; it also documents failures on sites generated with newer models. This is a site-level method with coverage and detector limits, not a sentence-level human-authorship certificate. [P2] (sections 1 to 4)

**Inference:** these studies support treating recent web text as exposed to generation. Their estimates cannot be averaged or applied as a retention multiplier to either survey: pages, sites and tokens are different units, and neither supplies a Turkish corpus-specific rate. An earliest capture also bounds when those bytes existed, not necessarily when they were first written. Backdated page metadata alone is weaker evidence.

## Survey baseline by language, licence class and date

The following quantities define the comparison. They are the surveys' gross, non-additive planning components, before eligibility losses. The symbols avoid silently substituting different snapshots. All conversions are **Inference:**. [EN][TR]

| Symbol and class | Gross estimated B tokens | Date and delivery constraints |
|---|---|---|
| G: English public-domain book lead, S03 | **4.08 to 6.80** | Dolma Gutenberg extraction: **20.4 GB** text. Paper acquisition April 2023; card says March 2023. Original edition dates incomplete. Underlying US-unrestricted works still need edition/territorial checks; ODC-By compilation terms remain. [EN][DOLMA] |
| W_EN: English share-alike lead, S01 | **3.24 to 5.40** | Dolma Wikimedia extraction: **16.2 GB**, March 2023 dump; original revision range unknown. Historical CC BY-SA 3.0 route plus wrapper and imported-text obligations. [EN][DOLMA] |
| P: Turkish attribution-only lead, T06 | **0.073882893 to 0.123138155** | ParlaMint-TR 4.1: **49,255,262 words**, source dates **2011-06-28 to 2022-11-17**; header publication **2024-05-14**. Publisher CC BY 4.0 does not settle the survey's underlying speaker-rights or transcript-provenance questions. [TR][PM] |
| W_TR: Turkish share-alike lead, T01 | **0.175201901 to 0.438004752** | Wikipedia **2023-11-01** dump: **534,988** articles times mean **1,637.43767** text characters, about **876.0095M** characters. Actual revision/import licence and card's 3.0 versus post-transition 4.0 discrepancy remain unresolved. Statistics endpoint was live, not commit-addressed. [TR] |

**Inference:** G + W_EN gives **7.32 to 12.20B** English; P + W_TR gives **0.249084794 to 0.561142907B** Turkish. These sums have unmeasured overlap and are not unique usable corpora. They have no established positive lower bound after eligibility checks. [EN][TR]

| Additional underlying class | English additions in the survey | Turkish additions in the survey |
|---|---|---|
| Public domain / CC0, with statutory freedoms kept distinct | Unknown incremental size: rights-tagged Wikisource, Standard Ebooks, Federal Register, judicial opinions, selected PMC articles | Unknown: rights-tagged Vikikaynak and qualifying legal instruments/decisions under the statutory route described in #54 |
| Attribution-only | Unknown: OGL-only legislation and selected CC BY PMC articles | Unknown beyond P: selected CC BY JEAA articles; observed journal archive **2019-12-31 to 2026-06-30** [TR] |
| Share-alike | Unknown beyond W_EN: selected Wikisource contributions and separately approved article subsets | Unknown beyond W_TR: selected Vikikaynak contributions |
| Restrictive, unresolved or disallowed access routes | Zero counted as offered under every option | Zero counted as offered under every option |

The final row is a rights/access exclusion already present in both surveys, not a volume cost caused by OD-4. ODC-By covers database rights rather than copyright in individual contents, and Common Crawl terms preserve third-party obligations. [L1][L2] CC attribution or share-alike grants also depend on the rights the licensor controls. [L3][L4] Authorship policy cannot fix absent rights. Licence acceptability and weight-release implications remain OD-3 / OD-10.

For scale, the rejected English C4 lead has an inferred **150 to 250B** planning tokens from the original approximately **750 GB** text, despite its **April 2019** crawl. The rejected Turkish OSCAR 22.01 lead uses **November/December 2021** crawls and has an inferred **9.632 to 16.053B** tokens. FineWeb spans **summer 2013 to March 2024**, reporting **15,352.9B GPT-2 tokens**; FineWeb2 Turkish spans **summer 2013 to April 2024**, with an inferred **62.901 to 104.834B** tokens. These are rejected, overlapping collections with unresolved underlying rights, not volume recoverable merely by choosing a residual or an early crawl. The surveys provide no rights-cleared, cutoff-stratified subset counts for them. [EN] (S11 to S15); [TR] (T08 to T13)

## Volume comparison for the policy options

### Operational definitions for comparison

**Older snapshots only:** require the actual captured text version to predate an owner-selected cutoff. For a concrete sensitivity case, consider any cutoff from the early access period through the ChatGPT launch. The quantified newer releases above postdate that case, and no qualifying older capture of their full contents was established. Publication date and capture date remain separate fields. This does not choose a cutoff. A later transcription of an old book or speech is not automatically an older capture. Admitting it by matching an older original would be a provenance exception, recorded separately below.

**Curated sources only:** use a deliberately narrow scenario: identified book editions, scan-backed validated transcriptions, official source bodies and attributable scholarly articles with inspectable authorship and editorial records. Hold the whole open-edit Wikipedia releases out as offered; reviewable individual revisions could be recovered only if the owner accepts that evidence. P remains conditional on underlying rights and the acceptance of human-speech transcription. This operational boundary makes a cost visible; it does not define curation for OD-4 or claim that an institution guarantees human-only writing.

**A stated, accepted residual:** allow later, rights-cleared source versions after provenance checks, filtering and a documented audit, with an explicit owner decision about remaining uncertainty. Hold known generated prose out. A measured residual is not available from these surveys; a detector pass cannot supply one. No permission to introduce known model outputs or override D32 is inferred.

### Gross volume retained for investigation and excluded as offered

All entries are **Inference:** scenarios from the cited baseline, not measured policy yields. "Unknown additions" refers to the preceding class table. A zero below is a specified exclusion of the quantified delivery route, not proof of absent text. [EN][TR]

| Language and underlying class | Older captures, through pre-ChatGPT sensitivity case | Narrow curation scenario | Stated residual scenario |
|---|---|---|---|
| English PD / CC0 | G held out: **0 kept, 4.08 to 6.80B excluded** from this 2023 delivery. Older editions/additions unknown; PG-19 alternative below | G remains conditional: **4.08 to 6.80B gross**, further loss unknown; additions unknown | Same G envelope; no date-only exclusion, audit/filter loss unknown; additions unknown |
| English attribution-only | Both retained and excluded sizes unknown; no date-stratified OGL/PMC inventory | Retained and excluded sizes unknown after document-level selection | Retained and excluded sizes unknown; no automatic new rights grant |
| English share-alike | W_EN held out: **0 kept, 3.24 to 5.40B excluded**; older snapshot/additions unquantified | W_EN held out as offered: **0 kept, 3.24 to 5.40B excluded**; separately verified revisions/transcriptions unknown | W_EN remains conditional: **3.24 to 5.40B gross**, audit/filter loss unknown; additions unknown |
| English restrictive/unresolved | **0 counted**, as already rejected; policy-specific recoverable subset unknown | Same | Same |
| Turkish PD / statutory / CC0 | Both retained and excluded sizes unknown; selected editions and legal-text versions not inventoried by cutoff | Retained and excluded sizes unknown; scan-backed or official bodies need source checks | Retained and excluded sizes unknown; statutory and territorial conditions unchanged |
| Turkish attribution-only | Current P delivery held out: **0 kept, 0.073882893 to 0.123138155B excluded** because no pre-cutoff capture is established for this delivery; original-date exception below; JEAA older portion unknown | P remains conditional: **0.073882893 to 0.123138155B gross**, further loss unknown; JEAA additions unknown | Same P envelope; no date-only exclusion, audit/filter loss unknown; JEAA additions unknown |
| Turkish share-alike | W_TR held out: **0 kept, 0.175201901 to 0.438004752B excluded**; historical alternative below | W_TR held out as offered: **0 kept, 0.175201901 to 0.438004752B excluded**; individually verified material unknown | W_TR remains conditional: **0.175201901 to 0.438004752B gross**, audit/filter loss unknown; additions unknown |
| Turkish restrictive/unresolved | **0 counted**, as already rejected; recoverable subset unknown | Same | Same |

**Inference:** strict older captures retain none of the newer quantified delivery routes and hold out **7.32 to 12.20B English** and **0.249084794 to 0.561142907B Turkish** as offered, before considering alternatives. Narrow curation keeps G and P as conditional gross leads and excludes W_EN and W_TR as offered. The residual scenario preserves the entire newer gross envelopes for investigation, with unknown actual losses. For every option, audited usable volume is still unknown and has no demonstrated positive lower bound. [EN][TR]

If the owner includes audited Wikipedia revisions in "curated," replace each wiki exclusion with an unknown retained fraction of its gross envelope. The upper envelope can then equal the residual scenario, while its evidence requirement differs. No measured additional retention follows from renaming a source curated.

### Older alternatives and the cost of distinguishing content from capture

| Language and class | Survey alternative and date evidence | Volume consequence, Inference |
|---|---|---|
| English book body, PD subject to rights and Apache release terms | PG-19 train books published **before 1919**, **1,973,136,207 word-level units**. Earliest original date and artifact-level capture provenance remain unverified. [EN] (S05); [PG19] | **2.37 to 2.96B** instead of G's **4.08 to 6.80B**, not added to G. Independent conversion extremes give an envelope difference of about **1.12 to 4.43B**; this is not matched-title attrition or a measured lost fraction |
| English share-alike | Standalone Wikipedia `20220301.en` is an older lead, but the survey has storage including metadata rather than eligible text bytes. [EN] (S01) | Retained tokens and net loss relative to W_EN unknown. It precedes ChatGPT but follows earlier generator availability |
| Turkish share-alike | Wiki40B paper published in **2020**, with train estimate **244.6M characters**. Exact dump date and equivalence to today's download unverified. [TR] (T01); [W40] | **0.04892 to 0.12230B**, replacing W_TR. At the same characters-per-token assumption, the character-based envelope is about **72.08% smaller**: `1 - 244.6 / 876.0095`. This combines different extraction/version populations; it is not measured deletion of newer AI text |
| Turkish attribution-only | P's source interval ends **2022-11-17**, before ChatGPT, although the inspected release is later. [PM] | With independently verified old source text and an accepted original-date exception, the full **0.073882893 to 0.123138155B** remains a conditional lead. Under earlier cutoffs inside its source interval, the keep/loss split is unknown |

**Inference:** combining the older Turkish wiki alternative with that explicit P exception gives **0.122802893 to 0.245438155B** gross. The paired low-end and high-end conversion scenarios are respectively **50.70% and 56.26% smaller** than their newer counterparts. These two comparisons are not bounds across all independent word/character conversion choices. It is not a strict older-capture result, a confidence interval or a measured human-retention rate. It still depends on artifact provenance, SA approval and parliamentary rights. [TR]

The surveys do not provide annual rights-cleared text counts. An exact volume retained at each earlier cutoff cannot be reconstructed from aggregate date ranges. A cutoff in early 2023 also cannot be applied precisely to an English "March 2023" acquisition with no verified day. These gaps remain unknown, rather than being assigned a percentage.

## How the options would be checked

The following procedures are **Inference:** proposed operational checks for later pipeline work (#56), not implemented or authorized source approvals.

| Option | Admission evidence and repeatable checks | Remaining risk |
|---|---|---|
| Older snapshots only | Record cutoff rationale and whether it concerns capture or original text. Pin archive/revision ID, capture timestamp, hash, licence version and extraction version. Retrieve the captured body rather than a live page bearing an old date. For wikis, recover the actual historical revision and import/attribution chain. Exclude later appendices, wrappers, translations and silently updated files. Match old editions to scans if an exception permits a later transcription. Compare per-language/class counts before and after the cutoff, then deduplicate and preserve holdouts | Earlier generators, bot text and translation remain; missing/false dates and later additions can bypass superficial checks. Old text can lack rights or domain coverage. No timestamp certifies authorship |
| Curated sources only | Maintain an allowlist of particular collections and text fields, not entire domains. Require named original edition/author or attributable institutional record, editorial workflow and available revision evidence. Match book bodies to scans; inspect translations, introductions and OCR corrections. Use official decision/instrument bodies, excluding generated summaries and third-party material. For speech, reconcile transcript to official dated sources and verify rights; exclude machine-translated/annotation outputs. For academic text, verify article-version licence, dates and disclosures, then inspect supporting provenance. Quarantine unverifiable passages; log reason-coded losses | Editors and institutions may use undisclosed generation. Historical bodies can acquire modern additions. Human review of plausible prose alone cannot establish how it was produced. Restricting genres can reduce contemporary and conversational Turkish coverage |
| Stated, accepted residual | Apply rights and provenance gates first. Reject declared generated prose and generated translations; preserve separate records for model-based filtering. Pin source versions, detector version/threshold and extraction. Validate errors separately for each language, genre, length and date stratum with provenance-supported controls kept outside training. Audit randomly sampled retained material as well as flagged rejects. Record confirmed machine, confirmed human and unknown outcomes; unresolved cases are quarantined unless an explicit owner policy permits them. Freeze and version a release with its audit statement; investigate and remove discovered violations | False negatives, mixed human/AI passages, editing and new generators remain. False positives lose human volume, with unmeasured Turkish cost. The audit may bound observed labels but cannot infer true authorship where reviewers cannot establish it. A residual acceptance criterion may require an explicit interpretation or revision of D32 |

For all options, maintain a source manifest with source URL, immutable version/hash, language, underlying and wrapper rights, source/publication/revision/capture dates separately, provenance evidence, transformations and every exclusion reason. Keep model-generated metadata and research prose out of training text. Classifier use that preserves original text is a separate OD-4 question from generated training prose. Deduplicate across versions, sources and held-out material before reporting unique retained tokens.

## Detectors provide evidence, not a human-only certificate

- OpenAI's classifier announcement reported **26% true-positive detection** of AI-written text and **9% false positives** on its English challenge set. It warned about short text, non-English inputs, editing and errors outside the training distribution. The classifier was withdrawn for low accuracy on **2023-07-20**. Those are results for that retired system and setting, not current detector performance. [D1]
- Sadasivan et al., version dated **2025-01-17**, stress-test watermark, trained, zero-shot and retrieval detectors using recursive paraphrasing. Their experiments show substantial evasion with limited text-quality degradation in many settings. Their theoretical analysis concerns the distance between human and generator distributions; it does not prove every detector is useless in every practical setting. [D2] (sections 2 to 4)
- MULTITuDE reports average F1 of **0.9292 on English versus 0.6903 on its non-English test languages** for English-trained detectors. Its **11 languages** do not include Turkish. This demonstrates cross-language generalization risk, not a measured Turkish error rate. [D3] (table 1 and language list)

**Inference:** use a detector to prioritize investigation, not to declare all accepted text human or to reject an author solely by a score. A source's human editorial process and direct original-version evidence remain valuable even when a detector passes it. Missing watermark or AI disclosure is not positive evidence of human authorship. The web-prevalence measurements above do not resolve detector errors or mixed authorship in Chorus's sources.

For a future residual audit, pre-register the population, sampling unit, language/class/date strata, handling of unknowns and the owner's acceptance threshold. Report document-level and token-weighted results separately; long documents can dominate token exposure. Sample retained material, rather than estimating purity from the number of detector rejects. Source-level clusters and shared boilerplate require a sampling design that accounts for dependence. Report uncertain provenance explicitly, together with false-positive losses and sensitivity tests. No audit or detector calibration was run for this note, and no numerical residual limit is proposed.

## What the cost means for Turkish

**Inference:** the newer quantified Turkish envelope is only **2.04% to 7.67%** of the newer quantified English envelope when crossing independent conversion extremes: `0.249084794 / 12.20` to `0.561142907 / 7.32`. This is a planning ratio between different corpora and conversion assumptions, not the ratio of all available or approved text. Turkish PD/statutory additions and English attribution-only additions are unquantified. [EN][TR]

The constraints differ by option:

- **Older captures:** neither newer quantified Turkish delivery survives the strict capture rule. Even the historical-wiki-plus-P-exception scenario reduces the gross pool to **0.1228 to 0.2454B**. A pre-ChatGPT original-date exception could preserve speech material that a capture-only rule rejects; adopting that exception is an owner decision.
- **Narrow curation:** holding out the whole open-edit Wikipedia lead leaves P at **0.0739 to 0.1231B** quantified, subject to its unresolved rights and provenance. If speech rights are not established, no quantified Turkish component remains in that scenario. Unknown books, legal texts and academic additions must be measured before claiming they fill the gap.
- **Residual:** retaining W_TR and P preserves **0.2491 to 0.5611B** gross for investigation, but establishes neither an accepted residual nor enough usable Turkish. An English detector result cannot justify a Turkish retention or error assumption. [TR]

For a concrete budget illustration, #54 uses an approximate **20 training tokens per parameter** starting point from Hoffmann et al., rounded from **1.4T tokens / 70B parameters**. This is not a minimum-data law or a validated rule for MoE total parameters. A **100M** model with **half** its presentations in Turkish would consume **1B Turkish token presentations**. **Inference:** `passes = presentations / distinct retained tokens` gives **1.78 to 4.01 passes** over the newer gross pool, **4.07 to 8.14** over the historical-wiki-plus-P-exception pool, or **8.12 to 13.53** over P alone. These are optimistic gross-volume scenarios before filtering, overlap and holdouts; they choose neither a model size nor a language allocation. [TR][SCALE]

Muennighoff et al. report little loss change through approximately **four epochs** in their studied setting, with diminishing returns thereafter; their whole-corpus experiments are not a guarantee for bilingual Turkish-only oversampling. [REPEAT] **Inference:** stricter selection can force more repetition or a smaller Turkish presentation budget. Additional English text does not establish Turkish quality, and repeated presentations do not create new unique Turkish text. OD-6 and later evaluation must use measured retained volume.

## Unverified quantities and scope

- No corpus contamination rate, rights/authorship retention, actual Chorus token count, holdout loss or cross-source overlap was measured. No policy option has a defensible positive lower bound on fully audited usable text.
- No exact rights-cleared volume by cutoff year exists in the pinned surveys. The original dates of English book editions and wiki revisions, artifact provenance for historical alternatives and current-versus-paper Wiki40B equivalence remain incomplete.
- The Turkish wiki licence discrepancy, ParlaMint underlying speech rights and transcription evidence, and incremental book/legal/article quantities remain unresolved as in #54. This note does not re-clear territorial rights or decide implications for model weights.
- The external web studies are preprints and detector-based population estimates. Their experiments were not reproduced. No Turkish contamination estimate or Turkish detector performance is established by the sources used here; this is not a claim that no Turkish evaluation exists anywhere.
- No source acquisition pipeline, corpus audit, detector benchmark, model/tokenizer training or Turkish quality experiment was performed. The note proposes checks for #56; it does not implement them.

## Questions for the owner

1. **OD-4:** which part of the evidence window should define the cutoff, and does it apply to capture/revision bytes or original authorship? Are later scan-matched transcriptions and independently verified old parliamentary texts allowed as exceptions?
2. **OD-4:** what counts as curation? Are individually audited wiki revisions acceptable, and what editorial/provenance evidence is enough for books, official text, translations, speech transcripts and scholarly articles?
3. **OD-4 / D32:** can a stated residual be accepted under D32? If so, what must be measured, what threshold and confidence are required, and how are unknown, mixed or edited AI passages treated? Known model outputs remain excluded unless the owner changes the requirement.
4. **OD-3 / OD-10:** which underlying licences and wrapper obligations are acceptable, how is the Turkish wiki licence mismatch resolved, and what establishes territorial/edition and parliamentary speaker rights?
5. **OD-4 / OD-6 / OD-7:** are classification-only models acceptable; what retained Turkish quantity and held-out quality must be demonstrated before choosing the tokenizer, model size and language allocation?

## Source register

Access date for **every URL below: 2026-10-25**. Links identify primary texts or the exact internal survey commits. The bibliography is evidence for research, not an allowlist of training documents. PDF sources were read through their extracted text; no claims depend on a figure read only visually.

| Reference | Source and location used |
|---|---|
| EN | [English survey at the origin commit read][EN], candidate records and totals |
| TR | [Turkish survey at the origin commit read][TR], candidate records, totals and repetition arithmetic |
| R1 to R5 | [GPT-2 full release][R1]; [API private beta][R2]; [waitlist removal][R3]; [ChatGPT launch][R4]; [Bard access announcement][R5] |
| P1 | [Dolezal et al., dated preprint HTML][P1], sections 1, 3.1, 3.3 and appendix A |
| P2 | [He et al., preprint PDF text][P2], introduction, pipeline, validation, prevalence and limitations; [submission record][P2-DATE] |
| D1 | [OpenAI classifier report and withdrawal notice][D1], evaluation and limitations |
| D2 | [Sadasivan et al., pinned version HTML][D2], sections 2 to 4 |
| D3 | [Macko et al., MULTITuDE paper][D3], table 1 and language list |
| DOLMA | [Soldaini et al., table 1 and section 8][DOLMA], text bytes and collection dates |
| PG19 | [DeepMind publisher README, raw text][PG19], original-date rule and train statistics |
| PM | [ParlaMint v4.1 Turkish header, raw XML][PM], extent, publication/source dates, licence and editorial declaration |
| W40 | [Guo et al., Wiki40B paper][W40], table 2; train characters estimated by its authors from held-out splits |
| L1 to L4 | [ODC-By legal text][L1], preamble; [Common Crawl terms][L2]; [CC BY legal code][L3]; [CC BY-SA legal code][L4] |
| SCALE | [Hoffmann et al., primary paper][SCALE], compute-optimal analysis; the illustrative budget is inherited from TR |
| REPEAT | [Muennighoff et al., pinned paper HTML][REPEAT], abstract, resource-return analysis and appendix Q |

## Trade-off for OD-4

**Inference:** strict older captures offer a simpler, inspectable date gate but exclude the surveys' newer quantified releases, leaving historical replacements and unmeasured additions to establish volume. Curation can recover later transcriptions and accountable human sources, with a substantial, unmeasured review cost and a smaller quantified pool under the narrow scenario. A stated residual keeps the largest candidate envelope, especially the newer Turkish wiki lead, but needs an explicit owner rule about uncertainty; detectors do not establish human-only text. Turkish loses proportionally important options when wiki text, speech or later transcriptions are excluded. The choice is how much recent and diverse human text to give up for stronger provenance evidence, and what unresolved risk the owner can accept under D32. This note records the trade-off and leaves the decision to OD-4.

[ISSUE]: https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/55
[OD4]: https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/25
[EN]: https://github.com/Cassandra-Collective/CASSANDRA-Chorus/blob/e637be6b87af34d065f95c7511e7d65ed0f5d8b1/docs/research/2026-10-25-english-pretraining-sources.md
[TR]: https://github.com/Cassandra-Collective/CASSANDRA-Chorus/blob/c1db10da0fd4aa64d7b4de7b9a5e25ad0c52f9b0/docs/research/2026-10-25-turkish-pretraining-sources.md
[R1]: https://openai.com/index/gpt-2-1-5b-release/
[R2]: https://openai.com/index/openai-api/
[R3]: https://openai.com/index/api-no-waitlist/
[R4]: https://openai.com/index/chatgpt/
[R5]: https://blog.google/innovation-and-ai/products/try-bard/
[P1]: https://arxiv.org/html/2604.26965v1
[P2]: https://arxiv.org/pdf/2605.00087v1
[P2-DATE]: https://arxiv.org/abs/2605.00087v1
[D1]: https://openai.com/index/new-ai-classifier-for-indicating-ai-written-text/
[D2]: https://arxiv.org/html/2303.11156v4
[D3]: https://aclanthology.org/2023.emnlp-main.616.pdf
[DOLMA]: https://arxiv.org/html/2402.00159v2
[PG19]: https://raw.githubusercontent.com/google-deepmind/pg19/master/README.md
[PM]: https://raw.githubusercontent.com/clarin-eric/ParlaMint/v4.1/Samples/ParlaMint-TR/ParlaMint-TR.xml
[W40]: https://aclanthology.org/2020.lrec-1.297.pdf
[L1]: https://opendatacommons.org/licenses/by/1-0/
[L2]: https://commoncrawl.org/terms-of-use
[L3]: https://creativecommons.org/licenses/by/4.0/legalcode.txt
[L4]: https://creativecommons.org/licenses/by-sa/4.0/legalcode.txt
[SCALE]: https://arxiv.org/pdf/2203.15556
[REPEAT]: https://arxiv.org/html/2305.16264v3
