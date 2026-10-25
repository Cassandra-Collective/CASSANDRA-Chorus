# English pretraining sources: rights, authorship and conditional volume

Research for [issue #53](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/53), roadmap 2.1 and D32. All external sources linked below were accessed on **2026-10-25**. The [implementation plan](../implementations/2026-10-25-english-pretraining-sources.md) was committed before this note.

**Assessment (Inference):** retain nine candidates for conditional investigation and reject six as offered. None is approved for training. The quantified retained components provide a gross planning envelope of **7.32 to 12.20 billion estimated tokens** before further rights, authorship, quality and overlap exclusions. That is not a measured usable corpus. The licence-class totals and their conditions appear below; unmeasured candidates are not assigned invented volumes.

## Method and boundaries

The survey covers encyclopedia text, public-domain books, government and legal texts, and filtered web text. Candidates came from original publishers, corpus authors and their official documentation. Familiar web corpora serve as controls for the difference between a database licence and permission to reuse its contents. Licence legal codes, statutory text and publisher terms were fetched and read directly as text. Search results were used to locate them, not as evidence for licence conclusions. No corpus or corpus sample was downloaded. Documentation and manifests were read outside the repository and OneDrive.

Every estimate is marked **Inference:**. B means billion and T means trillion; GB means decimal bytes unless the publisher uses another unit. Planning assumptions are 3 to 5 uncompressed English text bytes per token, or 1.2 to 1.5 tokens per published word-level unit. Thus, for text bytes X, T is between X/5 and X/3. These are sensitivity assumptions, not confidence intervals, measured tokenizer ratios or promises about the future Chorus tokenizer (OD-7). Compressed bytes, XML, dataset storage including metadata, document counts and multilingual crawl bytes are not converted. Publisher token counts retain their publisher tokenizer and are not Chorus counts.

Dates distinguish original publication, revision, crawl and digitization. A crawl timestamp cannot establish when the text was written. A historical book can have a modern translation, introduction or transcription. The record for every candidate separates model generation from model filtering or classification. An older snapshot or editorial process is evidence, not proof of human-only text. Where documentation does not report a model audit, absence of a reported model is not certification that none was used.

The scope cap was twenty candidates; fifteen are recorded. Not covered: the Turkish survey (#54), a post-AI web policy (#55), download and pipeline work (#56), or legal conclusions about weights. Other encyclopedia editions, standalone arXiv, peS2o, OpenAlex, news, subtitles, Reddit, The Pile and additional crawl derivatives were left out to avoid expanding into multilingual data, speech, metadata-only sources, mixed article rights or repetitive crawl surveys. Hansard is a useful future government-text lead, but its open archive and separately annotated commercial corpus need a separate volume reconciliation. Omission does not establish rejection or permission.

## Candidate table

Each ID has a detailed record below. C means conditional keep; R means reject the offered whole dataset or access route. Dispositions are **Inference:** under the conservative scope of this survey, not owner decisions. Licence names link to legal texts, except public-domain status, which links to the publisher's claim or governing statute. Table estimates inherit the explicitly stated inference method.

| ID and source home | Kind | Rights and licence text | Documented dates | Published scale and estimated tokens | Disposition |
|---|---|---|---|---|---|
| S01 [Wikipedia and Wikibooks](https://www.wikimedia.org/), Dolma Wikimedia component | encyclopedia text | [CC BY-SA 3.0 Unported][L-SA3] for the selected historical text; [ODC-By v1.0][L-ODC] compilation | March 2023 dump; original revision range not measured [D2] | 16.2 GB UTF-8 text, 6.2M documents [D1]; **Inference:** 3.24 to 5.40B tokens | C: share-alike, attribution, snapshot and bot/AI review |
| S02 [English Wikisource](https://en.wikisource.org/) | public-domain books | Work-specific PD/free licence; new contributions [CC BY-SA 4.0 International][L-SA4] [D4] | Historical works with ongoing edits; dump observed October 2026 [D5] | Article XML archive 3,428,152,987 compressed bytes [D5]; eligible tokens unknown | C: scan-backed, validated, rights-tagged works only |
| S03 [Project Gutenberg](https://www.gutenberg.org/), Dolma English extraction | public-domain books | US-unrestricted works; [Full Project Gutenberg License][L-PG], unversioned; [ODC-By v1.0][L-ODC] compilation | April 2023 acquisition in paper; card cutoff March 2023 [D2][D3]; original dates incomplete | 20.4 GB UTF-8 text, approximately 56,000 documents [D1]; **Inference:** 4.08 to 6.80B tokens | C: per-edition and territorial rights, wrapper and classifier review |
| S04 [Standard Ebooks](https://standardebooks.org/) | public-domain books | US-PD originals; [CC0 1.0 Universal][L-CC0] for its own contributions [D7] | Historical originals and modern ebook revisions; no aggregate original-date range verified | Aggregate text/download size and tokens not published on inspected pages | C: edition and translation rights; curated alternative to S03 |
| S05 [PG-19](https://github.com/google-deepmind/pg19) | public-domain books | [Apache License, Version 2.0][L-APACHE] release; underlying Gutenberg rights remain relevant | Books published before 1919 [D9]; earliest date not verified | Train: 28,602 books, 1,973,136,207 word-level units [D9]; **Inference:** 2.37 to 2.96B subword tokens | C: older alternative to S03, never an added full volume |
| S06 [GovInfo Federal Register](https://www.govinfo.gov/help/fr) | government and legal texts | [17 USC 105][L-105] status, not a blanket open licence; publisher exceptions [D11] | Collection 1936 onward; machine-readable coverage differs [D12] | No aggregate eligible English text size verified; tokens unknown | C: official federal prose only; exclude third-party material |
| S07 [CourtListener opinions](https://www.courtlistener.com/) | government and legal texts | Publisher [public-domain claim][D14] and [Public Domain Mark 1.0][L-PDM], not CC0 | Opinion dates vary by court; full range not verified | Bulk CSV snapshots available; eligible text bytes and tokens unknown | C: judicial opinion text only, rights and field audit |
| S08 [Legislation.gov.uk](https://www.legislation.gov.uk/) | government and legal texts | [Open Government Licence v3.0][L-OGL]; some additional source terms [D16] | Coverage varies by legislation type and version [D17] | No aggregate English OGL-only text size verified; tokens unknown | C: OGL-only English selection; isolate additional obligations |
| S09 [PMC Open Access Subset](https://pmc.ncbi.nlm.nih.gov/tools/openftlist/) | other | Per-article terms; restrict lead selection to [CC BY 4.0 International][L-BY4], [CC0 1.0][L-CC0] or documented PD | Article dates and versions vary; no aggregate eligible range verified | Cloud README: roughly 8M article versions across distributed types [D19], not eligible English count; tokens unknown | C: article-version licence allowlist and authorship audit |
| S10 [Stack Exchange](https://stackexchange.com/) current dump | other | [CC BY-SA 2.5 Generic][L-SA25], [3.0 Unported][L-SA3], [4.0 International][L-SA4], by revision [D22]; restrictive current access [D23] | Licence boundaries below; chosen dump date not obtained | Size shown inside account settings [D23]; not fetched; tokens unknown | R: current route requires a no-LLM-training affirmation |
| S11 [Common Crawl](https://commoncrawl.org/), April 2019 | filtered web text | [Terms of Use, updated March 7, 2024][L-CC]; third-party page rights unresolved | Crawled April 18 to 26, 2019 [D25] | 2.5B pages, 198 TiB uncompressed mixed content [D25]; eligible English tokens unknown | R: crawl access is not an underlying text licence |
| S12 [C4 English](https://huggingface.co/datasets/allenai/c4) | filtered web text | [ODC-By v1.0][L-ODC] wrapper plus [Common Crawl terms][L-CC] [D26] | April 2019 crawl [D27] | Original paper: about 750 GB text [D27]; **Inference:** about 150 to 250B tokens for that original corpus | R: document rights and human-only provenance unresolved |
| S13 [FineWeb](https://huggingface.co/datasets/HuggingFaceFW/fineweb), v1.0.0 | filtered web text | [ODC-By v1.0][L-ODC] wrapper plus [Common Crawl terms][L-CC] | Summer 2013 to March 2024, pinned card [D28] | Published total: 41,880.2 GB disk, 15,352.9B GPT-2 tokens [D28]; Chorus tokens unknown | R: mixed page rights and authorship; classifier used |
| S14 [FineWeb-Edu](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu), v1.0.0 | filtered web text | [ODC-By v1.0][L-ODC] wrapper plus [Common Crawl terms][L-CC] | Crawl configurations from 2013 through 2024 [D29]; writing dates unknown | Published about 1.3T tokens [D29], inherited GPT-2 counting; total archive bytes not verified | R: rights unresolved; LLM-derived educational labels flagged |
| S15 [Dolma](https://huggingface.co/datasets/allenai/dolma), full v1.6 mix | other | [ODC-By v1.0][L-ODC] compilation; all original-source agreements also apply [D3] | Component cutoffs differ, including 2023 [D2][D3] | 5.4 TB gzip download; 3,059B Llama tokens [D3]; Chorus tokens unknown | R: mixed rights and authorship; salvage only audited components |

## Obligations read from primary legal texts

These summaries identify what each licence actually conditions. They do not decide whether model weights are adapted material or a produced work. That remains for OD-3 and OD-10. Keep the applicable version, licence link, document identity, provenance and required notices with any later selection.

| Instrument | Attribution and notices | Share-alike / non-commercial / no-derivatives | Other material conditions and limits |
|---|---|---|---|
| [CC0 1.0 Universal][L-CC0], sections 2 to 4 | No attribution or notice-retention condition under the dedication/fallback | None / none / none | Waives only affirmer's rights to the extent possible; fallback licence; does not clear other people's rights or patent/trademark rights; no warranty |
| [CC BY 4.0 International][L-BY4], sections 2 to 4 and 6 | On sharing, retain supplied creator, copyright, licence and disclaimer notices and source URI where practicable; identify changes and link licence; remove attribution on request where practicable | None / none / none | No additional restrictions or effective technological measures restricting licensed rights; no implied endorsement; privacy, moral, patent and trademark rights have limits or exclusions; breach terminates rights, with specified reinstatement provisions |
| [CC BY-SA 4.0 International][L-SA4], sections 2 to 4 | BY obligations above | Shared adaptations: same licence elements, this/later version or approved compatible licence / none / none | Adapted databases can trigger share-alike; no restrictive downstream terms or technological measures. Applies only to rights the licensor can grant |
| [CC BY-SA 3.0 Unported][L-SA3], section 4 | Retain copyright, licence and disclaimer notices; credit author/designated parties, supplied title, URI where practicable and adaptation; removal of credit on request where practicable | Distribute adaptations under allowed same/later/ported/compatible licence / none / none | No sublicensing, restrictive terms or effective technological measures; no implied endorsement; section 4(d) protects author honour/reputation, subject to its jurisdictional qualification |
| [CC BY-SA 2.5 Generic][L-SA25], section 4 | Retain copyright, licence and disclaimer notices, author/designated credit, supplied title, URI and adaptation credit | Distributed derivatives use same/later version or allowed jurisdiction licence / none / none | No sublicensing or inconsistent access/use controls; source in a collection retains its conditions without automatically licensing the whole collection alike |
| [Apache License, Version 2.0][L-APACHE], sections 3 to 9 | Include licence; mark changed files; retain relevant source notices and supplied NOTICE attributions on redistribution | None / none / none | Limited patent grant and patent-litigation termination; no general trademark grant; additional warranty/support commitments are on the distributor's own behalf, with indemnification condition |
| [Open Data Commons Attribution License v1.0][L-ODC], preamble and sections 2 to 4 | Public database conveyance: licence/URI in database and documentation, preserve copyright/database/licence notices. Public produced work: notice identifying database and licence | No share-alike for produced works / none / none | Governs database rights, not individual contents. No sublicensing or further restrictions on granted rights. Derivative-database conveyance has its own notice/licence conditions |
| [Open Government Licence v3.0][L-OGL] | Acknowledge provider/source using specified or default statement, with licence link where possible; aggregation may link to attribution list | None / none / none | No endorsement; excludes personal data, unlicensed third-party rights, certain insignia/logos and other IP. Breach ends rights; no warranty |
| [Full Project Gutenberg License][L-PG], unversioned, sections 1.C to 1.F | Compilation copyright distinguished from underlying works; branded redistribution retains full licence and prescribed notice; other formats need access to original format | Not a CC share-alike, NC or ND licence | US-unrestricted text with all PG references removed has a different reuse path. Branded charged distribution adds royalty/refund duties or permission. Non-US rights and permission-only books require separate checking |
| [17 USC 105 and 101, 2024 edition][L-105] [L-101] | No general copyright attribution requirement for a qualifying federal work under these sections; publisher may request credit [D11] | Not licences; no SA/NC/ND grant to interpret | Official-duty definition, assigned copyrights and statutory covered scholarly-work exceptions matter. Does not establish worldwide status or rights in third-party additions |
| [Public Domain Mark 1.0][L-PDM] | Identifies claimed status; creates no attribution licence condition | Not a licence or waiver | Territorial, moral, privacy and other rights can remain. Do not substitute it for CC0 or evidence of title |
| [Common Crawl Terms of Use][L-CC], dated revision above | Respect third-party copyrights; do not disguise origin or impersonate endorsement | No blanket content licence; do not classify the crawl as CC0 or permissive text | Limited service-access grant, acceptable-use/privacy/IP obligations, disclaimers, indemnification and dispute terms. Source page licences still need evidence |

For the PMC screening exclusions, the [CC BY-NC 4.0 International legal code][L-NC4] limits licensed reproduction, adaptation and sharing to non-commercial purposes. The [CC BY-ND 4.0 International legal code][L-ND4] permits producing/reproducing adaptations but not sharing them; it is not a ban on all private adaptation. Both retain attribution/notice conditions and restrict extra downstream barriers. **Assessment (Inference):** hold NC, ND, older/unread versions and bespoke terms out of the conservative selection. This does not settle their acceptability for Chorus.

## Detailed source records

### S01. Wikipedia and Wikibooks, selected Wikimedia component

Use the documented Dolma component, not its full mixture. [D1] reports 16.2 GB of UTF-8 text. **Inference:** 16.2 billion / 5 to / 3 gives 3.24 to 5.40B planning tokens. Its published Llama count is 4.3B [D1]; that is an independent publisher count. The paper identifies English and Simple editions, a March 2023 dump and WikiExtractor processing [D2]. Original revision start dates are unverified. The card and paper differ on the precision of collection cutoffs; neither is an original writing-date range.

The March snapshot predates Wikimedia's announced move from CC BY-SA 3.0 to 4.0 [D30]. Use the historical 3.0 route and preserve page-specific attribution exceptions; the legacy Wikipedia card explicitly distinguishes CC-only imports from the GFDL route [D31]. This survey does not select GFDL and did not examine its full legal text. Dolma's ODC-By wrapper does not replace either underlying licence.

Human evidence: editor-contributed reference material and page provenance. The paper reports FastText language identification, short-page exclusion and extraction [D2]. No generation step is reported for this component. **Risk (Inference):** bot-created prose, translated/imported pages and AI-era edits can remain; a language classifier cannot verify authorship. Obtain gzip JSONL through the [v1.6 URL manifest][D32], selecting the Wikimedia component only. Component compressed download bytes are unverified. **Assessment (Inference):** conditional on share-alike/attribution acceptance, provenance recovery and OD-4. An older alternative is `20220301.en`, with 6,458,670 records and 20.28 GB generated storage [D31]; that storage includes metadata and is not converted or added here.

### S02. English Wikisource

The policy separates underlying source works from original contributor material and translations [D4]. Do not treat the entire dump as public domain. Select work-level rights tags, underlying edition and translation rights, and scan-backed validated text. Its validation process requires another contributor to check a proofread page [D6]. New contributor material uses CC BY-SA 4.0; excluded material may use other free licences. This note selects only demonstrable PD or the examined BY-SA route, not every compatible licence.

The inspected dump listing dates the full `pages-articles.xml.bz2` object to October 1, 2026 and gives 3,428,152,987 bytes [D5]. Download through that listing as bzip2 XML; do not add Page-namespace transcriptions and mainspace transclusions as separate books. **Inference:** no defensible token estimate follows from compressed mixed-namespace XML; retained text and total original-date range are unknown.

**Risk (Inference):** OCR errors, bot formatting, modern translation and unsourced contributor prose require review. Validation supports transcription fidelity, not an audit of every tool used. The cited documentation gives no corpus-wide model-use inventory or human-only certificate. **Assessment (Inference):** conditional keep for validated, rights-tagged editions; quantify only after selection and deduplication against S03 to S05.

### S03. Project Gutenberg, with a quantified English extraction

Gutenberg describes volunteer digitization and proofreading [D33]. Its offline-catalogue documentation warns that release dates are ebook dates and that metadata do not contain original print publication dates [D8]. The library is therefore not a dated pre-AI snapshot merely because the underlying books are old.

For a bounded estimate, use the English Gutenberg component described in [D1][D2]: 20.4 GB UTF-8 text. **Inference:** 20.4 billion / 5 to / 3 gives 4.08 to 6.80B tokens, before edition/rights screening. The paper gives an April acquisition and the card a March cutoff [D2][D3]; record that mismatch rather than asserting a precise final document date. The earliest and latest original print dates are not established. FastText language selection is reported [D2], without a reported generative rewrite step.

Underlying rights follow the PG instrument above; permissions to PG do not automatically grant all reuse rights. For branded charged distribution under section 1.E.8, the normative text specifies a royalty of 20% of gross profits, payment within 60 days of the relevant tax-return dates, rejection refunds for notice within 30 days of receipt, and remedies for defects reported within 90 days of receipt [L-PG]. Section 1.F.6 also imposes indemnification for specified distribution, alteration and defect claims. These are not conditions of every stripped, locally rights-clear book body. Dolma adds ODC-By compilation terms. Download originals as text/HTML/EPUB through the [official mirrors/catalogue routes][D8], or select only the Gutenberg gzip JSONL component in [D32]. Component compressed bytes are unverified. **Risk (Inference):** translations, introductions, transcription errors and modern revisions remain; removed boilerplate can make rights recovery harder. **Assessment (Inference):** conditional keep; verify source editions and territories, recover notices, and decide whether the classifier and wrapper are acceptable. Count this once, not alongside complete PG-derived alternatives.

### S04. Standard Ebooks

The publisher describes a volunteer editing effort, US-public-domain originals and a public-domain dedication for its own work [D7]. CC0 covers only rights it can waive; it cannot cure a translation still protected elsewhere. Text and cover art must not be assumed to have identical rights. **Risk (Inference):** original book authorship is strong evidence for the book body, but modern corrections, introductions and translations still need provenance. No complete model-generation or filtering inventory was located in the cited pages.

Obtain individual EPUBs or the publisher's [source repositories][D34], extracting book text from XHTML. [Bulk ZIP downloads][D35] are a patron benefit; this survey did not purchase access. The inspected pages do not provide a verified aggregate English text byte/word count, full archive byte total or original-publication date interval. **Inference:** tokens are unknown, not the number of repositories times an assumed average book. **Assessment (Inference):** conditional keep as a curated edition source; treat overlap with Gutenberg and Wikisource as unknown and assign no incremental volume yet.

### S05. PG-19

[D9] identifies books published before 1919 and a train split of 28,602 books with 1,973,136,207 word-level units. Validation and test are separate. **Inference:** multiplying the training count by 1.2 and 1.5 gives approximately 2.37 to 2.96B subword tokens. Do not train on the held-out splits merely to increase this estimate. The publisher warns about dated style and historical biases, relevant to an assistant [D9]. Earliest publication and per-edition territorial status remain unverified.

The repository's [LICENSE][D10] is Apache-2.0, and its README applies that name to the dataset. Keep Apache notices for the release; do not assume this establishes fresh copyright permission in all Gutenberg originals or translations. The documented processing removes PG boilerplate and replaces specified offensive words, rather than generating paraphrases [D9]. **Risk (Inference):** this favours historical human authorship but does not certify digitization tools or eliminate rights mistakes.

The README links the `deepmind-gutenberg` cloud bucket; books are plain text with CSV metadata. TFDS publishes 10.94 GiB generated dataset storage and explicitly leaves download size unknown [D36]. **Assessment (Inference):** conditional keep as an older, bounded alternative to S03. Its overlap has not been measured; exclude its full volume from additive totals.

### S06. GovInfo Federal Register

Restrict this lead to the Federal Register, rather than declaring all GovInfo holdings reusable. Its publisher describes official agency rules, proposed rules, notices and presidential documents, with historical coverage from 1936 [D12]. Official federal authorship is evidence of an editorial source, not a guarantee about quoted attachments or recent drafting tools. [D11] warns that government publications can contain third-party copyrighted material. Read both the statutory exception and official-duty definition, including the covered scholarly-work exception [L-105][L-101]. No separate dataset licence was found that overrides those distinctions.

Download annual/monthly ZIPs of XML through the [bulk directory][D13], or the documented text/PDF renditions [D12]. Coverage and representations differ by year; the historical PDF start must not be presented as complete XML coverage. Aggregate eligible English prose bytes, document count after exclusions and tokens were not verified. **Inference:** page counts or compressed ZIP sizes would not establish usable tokens.

**Risk (Inference):** agency prose can quote private standards, repeat regulations or contain templated output; OCR and AI-era assistance are unquantified. No corpus-wide generation/filtering audit is reported in the inspected documentation. **Assessment (Inference):** conditional keep for verified official prose, bounded dates and non-US rights review, with unknown volume.

### S07. CourtListener judicial opinions

The bulk documentation identifies the files as free of known copyright restrictions and uses a Public Domain Mark, not a CC0 dedication [D14]. Its terms acknowledge third-party copyrighted works in filings [D15]. Keep the lead restricted to judicial opinions; dockets, parties' filings, commercial headnotes and all extracted material cannot inherit a blanket judicial-text status. The CourtListener software's licence is not a corpus licence.

The publisher offers timestamped full snapshots as UTF-8 CSV in its [S3 bulk listing][D37], with separate opinion, cluster and court tables [D14]. Full opinion-date coverage, eligible plain-text size and compressed download total were not verified. The separate embeddings distribution is model output and is excluded, not counted as prose.

**Risk (Inference):** judicial drafting supports human-source provenance, but OCR/transcription, third-party quotations and modern AI-assisted drafting remain possible. The bulk guide does not document a complete model-use audit of all text fields. **Assessment (Inference):** conditional keep after selecting original opinion text, excluding model-derived fields and additions, and verifying rights and provenance. Tokens remain unknown; do not multiply a case count by a guessed average opinion length.

### S08. Legislation.gov.uk

The publisher's reuse documentation states OGL v3.0 and separately identifies EUR-Lex-derived and Westlaw-derived content [D16]. These are not interchangeable with a blanket OGL-only selection. Westlaw-derived records can be identified by publisher metadata and require an additional source acknowledgement; EU-derived content has additional reuse terms. This survey does not count those subsets and did not complete an independent audit of the additional instruments. OGL excludes third-party rights it does not license.

[D17] describes coverage and gaps by instrument type. Enactment, amendment and consolidated-version dates differ. A complete original-to-current English text date interval for the selected OGL-only subset was not verified. The [official API documentation][D18] provides XML via document URLs ending in `/data.xml` and Atom lists. Aggregate eligible text/download bytes and tokens remain unknown; do not count multiple consolidated versions as distinct prose without deduplication.

**Risk (Inference):** drafted legislation provides institutional authorship evidence, while automated consolidation, quotations, bilingual material and modern drafting assistance still require review. No complete model-use inventory was located. **Assessment (Inference):** conditional keep for English OGL-only text and associated notices, with additional-source records isolated and uncounted.

### S09. PMC Open Access Subset

Open access is not one licence. PMC requires reading article-level terms and warns that missing copyright statements do not imply freedom to reuse [D20]. For the conservative lead, allow only explicitly evidenced CC0, PD or CC BY 4.0 article versions; hold BY-SA separately for OD-3, and exclude NC, ND, TDM-only and unread/bespoke versions from totals. The licence allowlist must inspect the legal statement, not only an OA label.

Use the current [PMC Cloud Service][D21] and its [bucket README][D19]: article-version JATS XML, extracted TXT and JSON metadata. The README reports roughly 8M versions across distributed types, not an English, permissively licensed or human-only count. It also requires NLM source acknowledgement, trademark/non-endorsement precautions, redistribution only when licensed and current-data or clear outdated-data disclosure. These are service conditions in addition to article licences. Current per-version objects replace the legacy bulk-package approach [D21].

Eligible publication-date range, English article count, text/download byte totals and tokens were not verified. **Risk (Inference):** named authors and publication records are evidence, but peer review and an OA licence do not rule out machine translation, synthetic papers or AI-assisted writing. No whole-subset model-use certificate is reported. **Assessment (Inference):** conditional keep after article-version rights, authorship and date screening; deduplicate manuscripts, versions and papers appearing elsewhere. Do not equate free-to-read author manuscripts with open-licensed training text.

### S10. Stack Exchange current data dump

The publisher specifies revision-based licences: before April 8, 2011, CC BY-SA 2.5; from that date until May 2, 2018, CC BY-SA 3.0; thereafter CC BY-SA 4.0 [D22]. Preserve the exact revision's licence and user/source attribution. Quoted material and copied code can have different underlying rights.

The current official download instructions require an account-settings checkbox affirming no intent to use the dump for LLM training [D23]. No account action or affirmation was made. Size and current release date are behind that route and were not verified. Structured dump details are linked by the publisher, but a permitted training download was not established. **Inference:** eligible tokens and byte totals are unknown.

Human evidence is user-authored questions and answers. **Risk (Inference):** moderation does not certify human-only text; bot posts, machine translation, copied responses and model answers remain possible, especially in current revisions. No complete model-use audit was found. **Assessment (Inference):** reject this current access route. A lawfully obtained historical CC release could be assessed separately; its existence, exact contents, access conditions and non-overlap were not verified here. This survey does not resolve the legal interaction between an existing CC grant and later service restrictions.

### S11. Common Crawl April 2019

The [publisher's release][D25] gives April 18 to 26, 2019, 2.5B pages and 198 TiB uncompressed content. Its compressed WARC, WAT and WET sizes are 44.86, 16.32 and 6.96 TiB respectively. Path manifests lead to `crawl-data/CC-MAIN-2019-18/`. WARC is the crawl capture, WAT metadata and WET extracted text; none is a rights-cleared English corpus.

Read the actual service terms [L-CC]: a limited access licence and duties concerning third-party rights, not permission from every page author. **Inference:** an open-licensed English subset's size and tokens cannot be inferred from multilingual, markup-bearing crawl bytes.

**Risk (Inference):** an older crawl reduces exposure to later writing tools but still includes bots, machine translation, templated pages and potentially generated text. The release describes crawling, not a human-authorship selection; no human-only certification or full model-use inventory is supplied. **Assessment (Inference):** reject as offered. A later source-level licence allowlist might recover a subset, but its size is unknown and no portion enters the usable totals.

### S12. C4 English

The original authors describe about 750 GB of cleaned text from April 2019 [D27]. **Inference:** at the stated byte conversion, the original corpus corresponds to about 150 to 250B planning tokens. This is not a measurement of an arbitrary later C4 release. The AllenAI distribution instead reports 305 GB to download and 364,868,892 training records plus a separate validation split [D26]. Its JSON records carry text, URL and timestamp. Do not convert that download size or merge versions' storage statistics.

The distributor's ODC-By licence and explicit Common Crawl terms reference [D26] do not license each webpage. Cleaning uses heuristics, deduplication and statistical language classification through `langdetect`, not a documented generative rewrite [D26][D27]. **Risk (Inference):** detected English is not verified human authorship; bot prose and translation survive historical filtering. **Assessment (Inference):** reject the offered whole corpus for this open-licensed human-text selection. An independently rights-verified subset would have unknown retention and volume. No original-writing-date interval is established by the crawl date.

### S13. FineWeb v1.0.0

The pinned [publisher card][D28] states 95 crawls, summer 2013 through March 2024, and publishes a total of 15,352.9B GPT-2 tokens and 41,880.2 GB disk. These are publisher statistics, not corpus measurements made here. **Inference:** summing its rounded rows reproduces the disk total and gives 15,353.2B tokens, 0.3B above the printed token total; rounding can account for that difference. Obtain Parquet under the dataset's `v1.0.0` revision, selecting dump directories as needed. Current `main` has later data and different totals; it is not the selected release. Actual archive bytes were not independently measured.

ODC-By and Common Crawl terms cover the wrapper/access, not each page's copyright. The documented pipeline uses FastText language classification, extraction, heuristic quality rules, MinHash deduplication and PII formatting [D28]. It does not report a generative rewrite. **Risk (Inference):** classifier-selected English still includes bots, machine translation and AI-era content; crawl time is not writing time. Per-crawl deduplication does not establish uniqueness across crawls. **Assessment (Inference):** reject as offered; no eligible token contribution. **Inference:** Chorus token count cannot be derived from GPT-2 totals without a tokenizer comparison, even before rights selection.

### S14. FineWeb-Edu v1.0.0

The pinned [card][D29] describes about 1.3T educational tokens selected from FineWeb and lists crawl configurations through 2024. Preserve its revision rather than silently using newer `main`. The headline count is publisher-reported and approximate; whole-release byte total and exact final crawl boundary were not independently reconciled. Parquet is distributed through the same Hub repository. **Inference:** the inherited GPT-2 token count is not a Chorus measurement.

The construction explicitly uses Llama 3 70B Instruct scores to train a regression classifier based on Snowflake-arctic-embed, then filters the original web text [D29]. This is LLM-generated supervision for selection, not evidence that the entire training text was rewritten by that LLM. Its ODC-By/Common Crawl rights limitations are inherited from FineWeb.

**Risk (Inference):** educational classification cannot certify human authorship or page permissions; synthetic pages and machine translations may remain. **Assessment (Inference):** reject as offered on underlying rights and unverified authorship. Whether LLM-based selection itself breaks D32 is open for the owner, independently of those rejection reasons. Do not add this subset on top of FineWeb or count its generated labels as human prose.

### S15. Dolma full v1.6 mix

The current official [card][D3] records the switch to ODC-By, the continued applicability of source agreements, v1.6's 5.4 TB gzip download and its 3,059B Llama-token total. Select `urls/v1_6.txt` [D32] for that version's gzip JSONL objects. Do not mix in the separate v1.7 release, its changed components, instruction collections or OLMo-token statistics.

Its component cutoffs vary; there is no single verified original-writing-date range. [D2] describes language and toxicity classifiers and heuristic processing, with component-specific differences. These are model-based decisions even when they do not generate prose. **Risk (Inference):** the mix includes web/social text without corpus-wide open rights or human-only provenance. The fact that book and reference components are promising does not clear the full mixture.

**Assessment (Inference):** reject the full dataset, with zero contribution in that form. S01 and S03 are separately conditional salvage candidates. Do not add their volumes to the full mixture or treat ODC-By as clearance of Reddit, crawled pages or academic articles. **Inference:** publisher Llama totals cannot be converted to Chorus tokens without a tokenizer; subtracting rejected components also needs their actual rights/authorship retention, not a guessed percentage.

## Totals, overlap and the meaning of usable

The classes below describe **underlying text rights**, with wrapper obligations shown explicitly. Quantified envelopes use only published uncompressed text bytes from [D1]. They assume every byte in the selected component survives; this is a planning scenario, not a retention estimate. Unknown additional volumes are excluded, not assumed absent. All calculations in this section are **Inference:**.

| Underlying licence class | Non-additive quantified planning envelope | Conditions and unknown additions | Audited usable volume established here |
|---|---|---|---|
| Public domain and CC0 | S03: 20.4 GB / 5 to / 3 = **4.08 to 6.80B tokens** | Includes ODC-By compilation obligations for this delivery route; needs edition/territorial/authorship screening. S02 PD works, S04, S06, S07 and S09 PD/CC0 subset have unknown incremental volume | No positive measured amount; conditional ceiling for the quantified component 6.80B under the conversion assumption |
| Attribution-only text | **Unknown** | S08 OGL-only and S09 CC BY 4.0 subset; no verified eligible text size. Wrapper attribution alone does not put S11 to S15 here | Unknown, no positive measured amount |
| Share-alike text | S01: 16.2 GB / 5 to / 3 = **3.24 to 5.40B tokens** | ODC-By wrapper plus historical CC BY-SA; bot/AI and imported-rights review required. S02 BY-SA and any later-approved S09 BY-SA subset unquantified | No positive measured amount; conditional ceiling for quantified component 5.40B under the conversion assumption |
| Other, restrictive or unresolved rights | **Zero included** | S10 current dump access, S11 to S15 whole mixtures, and S09 NC/ND/TDM-only/unread licences excluded. Their published sizes are not eligible corpus volume | Zero counted by this survey's conservative selection, not proof that no reusable documents exist |

For the two quantified leads, the gross sum is **4.08 + 3.24 = 7.32B** to **6.80 + 5.40 = 12.20B** tokens. It is not a deduplicated total: repeated quotations and other cross-source overlap remain unmeasured. The distinct retained contribution can conservatively range from zero to 12.20B under these conversion assumptions, plus unmeasured eligible additions. There is no justified positive lower bound after rights and human-authorship checks, and this survey does not invent one.

An auditable later total is `U = rG * TG + rW * TW - O + A`, where G is the selected Gutenberg component, W the selected Wikimedia component, rG and rW are measured retention fractions between zero and one, O is their measured retained overlap in tokens, and A is the deduplicated incremental volume from other approved candidates. None of rG, rW, O or A was measured here. Set W to zero if share-alike is not accepted. If compilation attribution is unacceptable, neither quantified Dolma delivery route is approved; do not call the Gutenberg route unrestricted merely because its underlying originals may be PD.

For an older-book alternative, S05's train split gives **2.37 to 2.96B estimated tokens**, subject to its Apache wrapper and underlying rights checks. Substitute it for S03 rather than adding it. Standard Ebooks and Wikisource may offer better editions of the same works; they add no quantified incremental volume here. C4, FineWeb, FineWeb-Edu and Dolma overlap with Common Crawl and curated sources, and FineWeb-Edu is a FineWeb subset. Rejected headline totals are never summed into usable volume.

## What could not be verified

- No actual Chorus token counts, authorship-contamination fractions, rights-filter retention, quality retention or cross-source overlap were measured. The conversion intervals are assumptions and need not bound the eventual tokenizer.
- S01: original revision range, compressed component bytes and complete attribution/import recovery; the older standalone snapshot's pure text bytes. S03: exact collection cutoff (paper/card mismatch), original publication range and compressed component bytes.
- S02: eligible work count, extracted byte/word size and tokens by rights class, original-date range and overlap. S04: aggregate text/download size, tokens and original-date range. S05: earliest original date, exact original download bytes and title-level overlap; TFDS itself leaves download size unknown.
- S06 to S08: selected English text bytes, archive totals, eligible token counts and complete dates for the selected rights-clean subset. For S07, the full court/opinion date range and model use in all text fields remain unverified. Additional S08 source instruments were not independently audited and are excluded.
- S09: English counts, bytes and tokens after article-version licence/date/authorship screening; complete original-date range. The roughly 8M published version count is not this subset's size.
- S10: a permissible training download, current dump date/bytes and eligible tokens. S11: open-licensed English portion and its text bytes/tokens. S12: exact equivalence between the paper's approximate text size and later mirrors. S13: actual manifest byte totals and unrounded counts behind the small table-sum difference. S14: full byte total, precise last-crawl reconciliation and current-versus-pinned headline agreement. S15: original writing-date range and rights-clean retained proportions.
- The statutory evidence is explicitly the official 2024 US Code edition. Later amendments were not verified through the attempted newer-edition endpoints; this survey does not establish a current worldwide legal clearance.

## Questions for the owner

1. **OD-3 / OD-10:** which underlying licences and compilation conditions are acceptable, and how will attribution, notice preservation and possible share-alike obligations be handled for distributed corpora, applications and weights? This survey does not decide that weights are, or are not, adaptations or produced works.
2. **OD-3:** what territorial evidence is required for US-public-domain books and government/legal material used by volunteers elsewhere? Are NC, ND, bespoke terms and TDM-only material excluded? The current conservative totals exclude them.
3. **OD-4:** what evidence is sufficient for book bodies, translations, editorial additions, institutional text and wiki revisions? Is an older fixed snapshot required, a curated/validated selection sufficient, or a stated residual accepted? No candidate has a verified human-only certificate here.
4. **D32 / OD-4:** are language, toxicity and educational classifiers acceptable when original text is retained? Does LLM-generated classifier supervision, as in FineWeb-Edu, receive different treatment from FastText or `langdetect`? Generated labels and generated training prose must be recorded separately.
5. **OD-3 / OD-4:** should current service restrictions exclude otherwise CC-licensed material acquired through that route, and should older lawful releases be investigated separately? The current Stack Exchange affirmation must not be made for this training purpose.
6. **OD-7:** after licences and authorship criteria are selected, which tokenizer and text extraction define the final volume measurement? Until then, use the conditional class envelopes and unknowns above.

## Primary-source register

Access date for every entry and legal text: **2026-10-25**. Raw publisher cards, HTML legal codes and official statutory text were read; no licence conclusion relies only on a deed or search snippet. The Public Domain Mark is explicitly a status marker, not a licence with hidden legal code.

| Reference | Primary source and evidence used |
|---|---|
| D1 | [Dolma author paper, table 1][D1]: uncompressed UTF-8 text volumes and publisher token units for curated components |
| D2 | [Same paper, section 8 and datasheet][D2]: acquisition dates, extraction, language selection and processing risks |
| D3 | [Official Dolma raw card][D3]: v1.6 size, version table, source agreements and wrapper licence |
| D4 to D6 | [Wikisource copyright policy][D4], [dump listing][D5], [validation guide][D6] |
| D7 to D8 | [Standard Ebooks about page][D7]; [Gutenberg offline catalogues and mirror routes][D8] |
| D9 to D10 | [PG-19 raw README][D9] and [repository legal text][D10] |
| D11 to D13 | [GovInfo policies][D11], [Federal Register collection documentation][D12], [bulk listing][D13] |
| D14 to D15 | [CourtListener bulk guide][D14] and [service terms][D15] |
| D16 to D18 | [Legislation reuse rights][D16], [coverage][D17], [API/download documentation][D18] |
| D19 to D21 | [PMC cloud README and terms][D19], [copyright notice][D20], [current cloud-service documentation][D21] |
| D22 to D23 | [Stack Overflow licence-by-revision policy][D22] and [current dump-access instructions][D23] |
| D25 to D27 | [Common Crawl April release][D25], [AllenAI C4 raw card][D26], [T5 author paper, section 2.2][D27] |
| D28 to D29 | [FineWeb v1.0.0 raw card][D28], [FineWeb-Edu v1.0.0 raw card][D29] |
| D30 to D32 | [Wikimedia's licence-transition announcement][D30], [legacy Wikipedia raw card][D31], [Dolma v1.6 URL manifest][D32] |
| D33 to D37 | [Gutenberg authorship description][D33], [Standard Ebooks source repositories][D34], [bulk-access page][D35], [TFDS PG-19 sizes][D36], [CourtListener S3 listing][D37] |

[L-CC0]: https://creativecommons.org/publicdomain/zero/1.0/legalcode.txt
[L-BY4]: https://creativecommons.org/licenses/by/4.0/legalcode.txt
[L-SA4]: https://creativecommons.org/licenses/by-sa/4.0/legalcode.txt
[L-SA3]: https://creativecommons.org/licenses/by-sa/3.0/legalcode.txt
[L-SA25]: https://creativecommons.org/licenses/by-sa/2.5/legalcode.en
[L-NC4]: https://creativecommons.org/licenses/by-nc/4.0/legalcode.txt
[L-ND4]: https://creativecommons.org/licenses/by-nd/4.0/legalcode.txt
[L-APACHE]: https://www.apache.org/licenses/LICENSE-2.0.txt
[L-ODC]: https://opendatacommons.org/licenses/by/1-0/
[L-OGL]: https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
[L-PG]: https://www.gutenberg.org/policy/license.html
[L-105]: https://www.govinfo.gov/content/pkg/USCODE-2024-title17/html/USCODE-2024-title17-chap1-sec105.htm
[L-101]: https://www.govinfo.gov/content/pkg/USCODE-2024-title17/html/USCODE-2024-title17-chap1-sec101.htm
[L-PDM]: https://creativecommons.org/publicdomain/mark/1.0/
[L-CC]: https://commoncrawl.org/terms-of-use
[D1]: https://arxiv.org/html/2402.00159v2#S0.T1
[D2]: https://arxiv.org/html/2402.00159v2#S8
[D3]: https://huggingface.co/datasets/allenai/dolma/raw/main/README.md
[D4]: https://en.wikisource.org/wiki/Wikisource:Copyright_policy
[D5]: https://dumps.wikimedia.org/enwikisource/latest/
[D6]: https://en.wikisource.org/wiki/Help:Beginner%27s_guide_to_validation
[D7]: https://standardebooks.org/about
[D8]: https://www.gutenberg.org/ebooks/offline_catalogs.html
[D9]: https://raw.githubusercontent.com/google-deepmind/pg19/master/README.md
[D10]: https://raw.githubusercontent.com/google-deepmind/pg19/master/LICENSE
[D11]: https://www.govinfo.gov/about/policies
[D12]: https://www.govinfo.gov/help/fr
[D13]: https://www.govinfo.gov/bulkdata/FR
[D14]: https://wiki.free.law/c/courtlistener/help/api/bulk-data/bulk-legal-data
[D15]: https://www.courtlistener.com/terms/
[D16]: https://legislation.github.io/data-documentation/reuse-licence.html
[D17]: https://legislation.github.io/data-documentation/what-we-have.html
[D18]: https://legislation.github.io/data-documentation/
[D19]: https://pmc-oa-opendata.s3.amazonaws.com/README.txt
[D20]: https://pmc.ncbi.nlm.nih.gov/about/copyright/
[D21]: https://pmc.ncbi.nlm.nih.gov/tools/pmcaws/
[D22]: https://stackoverflow.com/help/licensing
[D23]: https://stackoverflow.com/help/data-dumps
[D25]: https://commoncrawl.org/blog/april-2019-crawl-archive-now-available
[D26]: https://huggingface.co/datasets/allenai/c4/raw/main/README.md
[D27]: https://arxiv.org/html/1910.10683v4#S2.SS2
[D28]: https://huggingface.co/datasets/HuggingFaceFW/fineweb/raw/v1.0.0/README.md
[D29]: https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu/raw/v1.0.0/README.md
[D30]: https://diff.wikimedia.org/2023/06/29/stepping-into-the-future-wikimedia-projects-transition-to-creative-commons-4-0-license/
[D31]: https://huggingface.co/datasets/legacy-datasets/wikipedia/raw/main/README.md
[D32]: https://huggingface.co/datasets/allenai/dolma/raw/main/urls/v1_6.txt
[D33]: https://www.gutenberg.org/about/
[D34]: https://github.com/standardebooks
[D35]: https://standardebooks.org/bulk-downloads
[D36]: https://www.tensorflow.org/datasets/catalog/pg19
[D37]: https://com-courtlistener-storage.s3-us-west-2.amazonaws.com/list.html?prefix=bulk-data/
