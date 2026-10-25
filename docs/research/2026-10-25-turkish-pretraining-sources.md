# Turkish pretraining sources: rights, authorship and conditional volume

Research for [issue #54](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/54), roadmap 2.1b and D32. Every external document and endpoint linked here was accessed on **2026-10-25**. The [implementation plan](../implementations/2026-10-25-turkish-pretraining-sources.md) was committed first.

**Assessment, Inference:** of thirteen candidate sources, keep seven under conditions and reject six as offered. None is approved for training. The two quantified retained leads give a gross planning scenario of **0.2491 to 0.5611 billion Turkish tokens**, before rights, authorship, quality, holdout and overlap exclusions. The newer Wikipedia lead comes from an AI-era snapshot and has a licence-version discrepancy; the parliamentary lead has unresolved underlying speech rights. There is no established positive amount of fully audited usable text.

**Model-size implication, Inference:** this does not establish enough Turkish data for any size in OD-6's provisional range. A 100M pilot could fit a modest-repetition budget under favourable, explicitly conditional scenarios below. A 300M or 1B model with half its training tokens in Turkish needs more unique approved Turkish text or more repetition than the cited paper's approximately four-epoch low-loss-change result. This is a measurement gap and a conditional budget comparison, not proof that Turkish lacks enough text.

## Method and units

The fields match the [English survey at commit e637be6b87af34d065f95c7511e7d65ed0f5d8b1][EN]: name, kind, source URL, exact licence and legal text, obligations, compilation versus underlying rights, authorship evidence and risks, dates, published size, inferred tokens, acquisition and disposition. C means conditional keep; R means reject the offered collection or route. All dispositions are **Inference:** for further investigation, not owner licence decisions.

Primary legal codes, Turkish statutory text, publisher policies, dataset cards, papers and aggregate metadata were read directly. Search snippets were discovery only. Turkish sources were read in Turkish. No corpus or corpus-text sample was downloaded. The ParlaMint XML fetched was its descriptive root header, not its included speech files. Temporary reference documents and metadata were held outside the repository and OneDrive.

M means million and B means billion. **Inference:** until OD-7 supplies a measured balanced tokenizer, use a sensitivity scenario of **2 to 5 text characters per token**, or **1.5 to 2.5 tokens per published word-level unit**. For character count C, tokens are C/5 to C/2; for words W, they are 1.5W to 2.5W. These are declared planning assumptions, not measured Turkish ratios, confidence intervals or guaranteed bounds. Wiki40B's published Turkish ratio is 4.611 characters per monolingual SentencePiece token [W4], which is one reference point, not calibration of Chorus. Publisher subword counts keep their original units. Compressed files, XML, Parquet/Arrow storage and document counts are not treated as plain text.

Counts before filtering are gross source volume, not unique retained training volume. A dated dump dates capture, not original writing. A human editorial process supports authorship but does not certify the absence of bots, machine translation, synthetic passages or model outputs. Model-based language identification and filtering are recorded separately from generated prose. Their acceptability remains open for OD-4.

## Candidate table

Estimates in this table are **Inference:** using the method above; unknown means unquantified, not measured zero. Details and unresolved conditions follow.

| ID and source | Kind | Licence or statutory basis, with primary text | Text dates | Published size and estimated tokens | Disposition |
|---|---|---|---|---|---|
| T01 [Turkish Wikipedia, `20231101.tr`][W1] | encyclopedia | Card says [CC BY-SA 3.0 Unported][L-SA3]; post-transition underlying text points to [CC BY-SA 4.0 International][L-SA4] [W3]. Version reconciliation required | Dump 2023-11-01; original revision range unverified | 534,988 articles; full-split mean text length 1,637.43767 characters [W2]. Inferred approximately 876.0095M characters, **0.1752 to 0.4380B tokens** | C: attribution, SA, actual revision licence and human-authorship review |
| T02 [Turkish Wikisource / Vikikaynak][WS] | public-domain books | Work-specific public domain under [Law 5846][LAW]; contributor text/translations [CC BY-SA 4.0 International][L-SA4] | Historical originals and ongoing transcriptions; selected range unverified | Eligible book text characters, words and tokens unknown; dump listing inaccessible [WS-DUMP] | C: scan-backed, rights-verified editions and human transcription review |
| T03 [Mevzuat Bilgi Sistemi][MEV] | government and legal texts | Law 5846 article 31 [LAW], a statutory reuse freedom, not a CC licence | Varies by instrument and consolidated version; eligible range unverified | Aggregate eligible text size and tokens unknown | C: officially published instrument text only; service and bulk route not verified |
| T04 [Anayasa Mahkemesi decisions][AYM] | government and legal texts | Law 5846 article 31 [LAW], not a blanket licence for the website | Decision and publication dates differ; selected range unverified | Decision-body bytes/words and tokens unknown | C: officially published judicial text, field and access review |
| T05 [TBMM laws, decisions and proceedings][TBMM] | government and legal texts | Article 31 for qualifying legal texts; article 32 has purpose limits for speeches [LAW] | Official guide distinguishes legislative terms and access formats [TBMM]; selected range unverified | No verified aggregate eligible text or tokens | C: article-31 subset only; speeches need a separate basis |
| T06 [ParlaMint-TR 4.1][PM] | government and legal texts | Publisher [CC BY 4.0 International][L-BY4] [PM-H]; underlying speech rights remain a separate condition | 2011-06-28 to 2022-11-17 [PM-H] | 49,255,262 words, 681,052 speeches [PM-H]; **0.07388 to 0.12314B tokens** | C: CC attribution, speech-rights chain and transcript provenance |
| T07 [İktisadi ve İdari Yaklaşımlar Dergisi, JEAA][J-LIC] | other, academic prose | [CC BY 4.0 International][L-BY4], stated by the journal, not by all of DergiPark | Archive observed from 2019-12-31 through 2026-06-30 [J-ARCH] | Selected Turkish article bodies, words and tokens unknown | C: article-level licence/date/language/authorship checks |
| T08 [Turkish National Corpus, TNC][TNC] | other, balanced corpus | Authors describe free non-commercial use [TNC-P]; exact licence text/version not obtained | 1990 to 2009 [TNC-P] | 50M words [TNC-P]; **0.075 to 0.125B tokens**, ineligible as offered | R: no verified open bulk-text grant; full terms inaccessible |
| T09 [mC4 Turkish][MC4] | filtered web text | [Open Data Commons Attribution License v1.0][L-ODC] compilation; [Common Crawl terms][L-CC]; underlying page rights unresolved | Paper uses the then-available monthly crawls; original writing dates unverified [MT5] | Paper table 6: 71M pages, 88B publisher tokens [MT5]; Chorus count unknown | R: wrapper does not clear underlying rights or human authorship |
| T10 [OSCAR 22.01 Turkish][OSCAR] | filtered web text | [CC0 1.0 Universal][L-CC0] for packaging/metadata/annotations only; publisher disclaims ownership of text | November/December 2021 crawl [OS-DOC] | 75.1 GB, 10,826,031 documents, 6,421,221,358 space-separated tokens [OSCAR]; **9.632 to 16.053B subword tokens**, ineligible | R: underlying rights unresolved; publisher currently suspends access |
| T11 [CulturaX Turkish][CULT] | filtered web text | Current card inherits mC4 and OSCAR terms, not a separate blanket text licence [L-ODC][L-CC0][L-CC] | Combined mC4 and OSCAR releases through 23.01; original writing range unverified [CULT-P] | 94,207,460 documents, 64,292,787,164 publisher tokens [CULT]; Chorus count unknown | R: inherited rights and authorship gaps |
| T12 [FineWeb2, `tur_Latn`][FW2] | filtered web text | [ODC-By v1.0][L-ODC] compilation and [Common Crawl terms][L-CC] | Crawls from summer 2013 through April 2024 [FW2]; writing dates unknown | 41,933,799,420 words, 95,129,129 documents, 284.52 GB UTF-8 text, 125.53 GB disk [FW2]; **62.901 to 104.834B tokens**, ineligible | R: no page-level rights or human-only clearance |
| T13 [VNGRS Web Corpus][VN] | filtered web text | Publisher card [CC BY-NC-SA 4.0 International][L-NCSA4]; underlying mC4/OSCAR terms and rights also matter | Parent mC4/OSCAR-2201 dates; original writing range unverified | 50.3M pages, 25.33B VBART tokens [VN]; Chorus count unknown | R: NC/SA restrictions, inherited page rights and authorship gaps |

## Obligations read from the primary legal texts

These are text and database obligations. **Inference:** whether released weights are adapted material or a produced work is not settled by this survey. OD-3 and OD-10 remain for the owner. No candidate is labelled safe for unrestricted weights.

| Instrument | Attribution and notice-keeping | SA / NC / ND | Other conditions and limits |
|---|---|---|---|
| [CC BY 4.0 International][L-BY4], sections 2 to 4 and 6 | On sharing, retain supplied creator, copyright, licence and disclaimer notices and source URI where practicable; identify changes and provide licence text/link; remove attribution on request where practicable | None / none / none | No extra downstream restrictions or effective technological measures; grants only rights the licensor controls; no endorsement; limited treatment of moral/privacy rights, no patent/trademark grant; breach can terminate rights |
| [CC BY-SA 4.0 International][L-SA4], sections 2 to 4 | BY obligations above | Shared adaptations use same elements, this/later version or a BY-SA-compatible licence / none / none | Adapter licence link required; adapted databases can trigger SA; no extra restrictions; source and imported-material rights still matter |
| [CC BY-SA 3.0 Unported][L-SA3], sections 3 and 4 | Preserve copyright/licence/disclaimer notices; supplied author/designated credit, title and URI where practicable; identify adaptation | Distributed adaptations use permitted same/later/ported/compatible licence / none / none | No sublicensing, restrictive terms or technological barriers; honour/reputation condition with jurisdictional qualification; a collection does not automatically become an adaptation |
| [CC BY-NC-SA 4.0 International][L-NCSA4], sections 1 to 4 | BY attribution, modification and notice duties | Shared adaptations retain NC-SA through allowed adapter licence / licensed reproduction, adaptation and sharing restricted to NonCommercial purposes / none | NonCommercial concerns commercial advantage or monetary compensation; being an open-source project does not itself establish compliance. No additional restrictions; grant limited to controlled rights |
| [CC0 1.0 Universal][L-CC0], sections 1 to 4 | No attribution or notice-retention condition in the dedication/fallback | None / none / none | Waiver/fallback applies to affirmer's rights only; does not clear third-party rights; no patent/trademark waiver or title warranty. OSCAR explicitly limits its application to packaging/metadata/annotations |
| [ODC-By v1.0][L-ODC], sections 2 to 4 | Public database conveyance: retain required notices and licence text/URI. Public produced works: notice of database origin and licence | None / none / none | Database rights/contract, not copyright in individual contents. No sublicensing or extra restrictions on granted rights; derivative-database conveyance has notice conditions |
| [Common Crawl Terms of Use][L-CC], last updated 2024-03-07 | Respect third-party copyright and other rights; do not disguise origin or claim endorsement | No blanket content grant | Access to a crawl is distinct from permission from page authors; service restrictions, privacy/IP obligations, disclaimers and dispute terms remain |
| [Law 5846][LAW], articles 26, 27, 31 and 32 | These are statutory provisions, not versions of a CC licence; preserve provenance and distinguish protected additions | No CC SA/NC/ND elements to infer | Expired economic rights, official legal texts and speeches have different rules, discussed below; no worldwide clearance follows |
| [TNC authors' description][TNC-P] | Full attribution/notice conditions not verified | Non-commercial described; SA and ND unknown | A paper describing access is not the missing licence agreement. No open bulk-text permission established |

## Turkish copyright law and the limits of official-text reuse

This is a research record, **not legal advice**. The Turkish text of Law No. 5846 was read from the Ministry of Culture and Tourism's [official laws page][LAW-HOME] and its linked [Turkish PDF][LAW]. The direct [mevzuat.gov.tr PDF][LAW-MEV] timed out. The ministry also links an [English file named as a 2026 edition][LAW-EN]; the relevant term, legal-text and speech provisions agree with the Turkish copy. The filename is not proof that every amendment is consolidated. Later amendments and every volunteer's territorial position were not independently established.

- **Articles 26 and 27:** economic rights expire, subject to the article-46/47 cases. The ordinary term is the author's life plus 70 years; joint authorship uses the last surviving author. Article 26 starts death-based calculation on the first day of the following year. Anonymous and legal-person cases have separate publication-based provisions in article 27. **Inference:** for an ordinary, already disclosed, single-author work with verified death in 1955, the ordinary calculation reaches expiry at the start of 2026. This is an example, not a blanket pre-publication-year cutoff or an automatic clearance of every edition.
- **Articles 6 and 8, and article 26:** translations and qualifying adaptations/compilations have separate rights; expiry of the original does not establish expiry of a modern translation or scholarly contribution. Article 6 distinguishes ordinary transcription/facsimile from scholarly preparation of previously unpublished work. **Inference:** inspect the actual edition, translator, editor and added material, not just the old author's name. OCR/transcription fidelity and human authorship are separate checks.
- **Article 46:** the statute has special provisions for previously unpublished or undisclosed works held by public libraries, museums and similar institutions after the economic term expires. **Inference:** a library scan does not automatically establish a universally unrestricted book. Article 47 and Additional Article 2 also caution against treating digitization, nationalization or a historical publication date as universal clearance.
- **Article 31:** officially published or announced laws, presidential decrees, regulations, notifications, circulars and judicial decisions may be reproduced, distributed, adapted or otherwise used. **Inference:** retain this statutory-freedom class separately from licensed text. It is evidence for reuse of the qualifying legal text, not a claim that every Turkish government webpage, commercial case annotation or institutional report is public domain worldwide.
- **Article 32:** speeches in the Grand National Assembly and other specified settings may be reproduced and disseminated for news and information; other reproduction/distribution purposes belong to the author. **Inference:** this does not establish blanket training permission for parliamentary transcripts. ParlaMint's CC BY statement needs a verified chain covering the underlying speech for the intended use, or another established basis. This unresolved point is not silently settled by its dataset licence.
- **Articles 14 to 19:** disclosure, attribution and integrity have their own provisions. **Inference:** economic-term expiry should not be described as removing every moral or other right. Distributed volunteers also need the applicable territorial analysis.

The ministry's own [website terms][KTB-TERMS] restrict ordinary site materials, including modification and non-personal use. **Inference:** this reinforces the need to isolate article-31 instruments rather than classify a whole government domain as open. No legal conclusion is drawn here about the enforceability of website terms against statutory freedoms.

## Detailed source records

### T01. Turkish Wikipedia, with a historical alternative

The [publisher card][W1] at revision `b04c8d1ceb2f5cd4588862100d08de323dccfbaa` describes extraction with `mwparserfromhell` and supplies article IDs, URLs, titles and text. The Turkish split has 534,988 records, 552,923,659 download bytes and 997,254,242 generated-storage bytes. Those storage quantities include format/metadata effects and are not converted.

The [statistics response][W2] has `partial: false`, no missing text and mean `text` length 1,637.43767. The [API documentation][W2-DOC] defines these as character-length statistics for the full split when `partial` is false. **Inference:** 534,988 * 1,637.43767 = approximately 876,009,504 characters, rounded because the mean is published with finite precision. Dividing by 5 and 2 gives **175.202M to 438.005M tokens**. This uses text only, excluding title/URL/ID lengths. The live statistics endpoint is not commit-addressed; its agreement with the card's record count was checked, but reproducibility requires a future pinned extraction.

The card names CC BY-SA 3.0 and GFDL, while the [Wikimedia transition announcement][W3] and [terms section 7][WM-TERMS] identify CC BY-SA 4.0 for post-transition contributions. **Inference:** treat the November snapshot as requiring the actual revision/import licence, conservatively including 4.0; do not assume the card's older 3.0 statement clears every page. Both CC legal codes were read. This survey selects a CC route only, not GFDL. Preserve page/history attribution and imported-source notices; extracted text can lose those notices. Imported text can have compatible licences and additional attribution duties.

Human evidence is community authorship with revision histories. **Risk, Inference:** bot articles, machine-translated imports, copied passages and AI-era edits are possible. Markup extraction is not an authorship audit; no corpus-wide generation or filtering-model inventory was found. Acquisition is the pinned Hub revision's `20231101.tr` Parquet files, with provenance recovered separately. **Disposition, Inference:** conditional keep after OD-3/OD-4 and licence/provenance reconciliation; no positive audited retention measured.

For an older, non-additive alternative, the [Wiki40B author paper][W4], table 2, reports Turkish train approximately **53.0M monolingual 32K SentencePiece tokens and 244.6M characters**. Its authors estimate training statistics from dev/test. **Inference:** the character scenario gives **48.92M to 122.30M planning tokens** for train only. The [TFDS builder][W5] explicitly states CC BY-SA 3.0 Unported for the dataset; its Apache software header does not license the prose. The paper describes rule-based page/section removal and Google's markup cleaning, not generative rewriting; its model-generated demonstration passages are not a proposed training source. Original dump date and complete internal processing provenance were not established. The [current TFDS catalogue][W6] gives 142,576 train examples and 308.87 MiB total storage, whereas the paper reports 170,378 Turkish pages across splits. Exact version equivalence was not verified, so do not substitute catalogue bytes into the historical paper estimate. Keep dev/test held out and do not add old Wikipedia text to the newer snapshot as unique data.

### T02. Turkish Wikisource / Vikikaynak

The [Turkish copyright policy][WS] separates public-domain/free works from contributor translations and new text under CC BY-SA 4.0. **Inference:** admit only work/edition-specific rights, not a blanket public-domain dump. Check author's and translator's dates, source scan and editorial additions against the law above and relevant territories. A site policy's broad statements about old Ottoman works or official speeches do not replace the statute's conditions.

Human evidence is transcription of identified source works and contributor review. **Risk, Inference:** raw OCR, bot formatting, unverified or machine translations and AI-assisted new additions need review. No complete model-use audit or original-date range was verified. Acquire a selected, scan-backed edition through wiki export or the XML dump, retaining rights tags and revision provenance. The [dump listing][WS-DUMP] returned access failure here; no dump date, compressed bytes or eligible text count is asserted. **Inference:** tokens are unknown until rights/language/namespace selection, OCR review and extraction. Avoid counting page transcriptions and their mainspace transclusions twice. Conditional keep, separately allocated to public-domain and SA classes after selection.

### T03. Mevzuat Bilgi Sistemi

The [TBMM guide][TBMM] identifies the Presidency's [Mevzuat system][MEV] as the route for current consolidated legal instruments. The official copy of Law 5846 demonstrates the legal-text class, not an aggregate corpus. Article 31 is the proposed basis; no separate blanket database or website-text licence was verified.

Human evidence is official legislative drafting/publication. **Risk, Inference:** source status alone does not certify all current drafting is human-only; exclude navigation, external commentary and unverified generated summaries. Consolidation, annotations, OCR and successive versions also require review. The service timed out, so its full coverage, original/publication date range, bulk-download method and eligible characters/words remain unverified. **Inference:** tokens unknown, no contribution to quantified totals. Conditional keep for qualifying official text after access, version and provenance checks, deduplicated against TBMM and Wikisource.

### T04. Anayasa Mahkemesi decisions

The [official decision bank][AYM] is a judicial-text lead under article 31, not a dataset with a blanket CC grant. Its current application required JavaScript; the institutional guide also failed through the research fetch route. No bulk endpoint, complete date coverage, archive size or selected body-word count was established. **Inference:** token volume is unknown.

Human evidence is the judiciary's publication of authored decisions. **Risk, Inference:** decision status is not a human-only certificate; quoted submissions, redactions, added headnotes, translations and automated summaries need separate treatment. Retain published decision bodies and their source identity; exclude third-party commentary and assess personal-data fields. Acquisition would be official decision HTML/PDF, but corpus-scale retrieval was not verified. Conditional keep after body/provenance and access checks; no invented volume and no addition of the same decision as also published in another official channel.

### T05. TBMM legal texts and raw proceedings

The [Turkish official access guide][TBMM] lists adopted laws, decisions, explanatory material, commission reports and plenary transcripts, with different HTML/PDF coverage. It describes article-level histories from law 5496 dated 2006-05-10, HTML laws from the 21st legislative term and PDFs from the first term. These are access descriptions, not an aggregate eligible word count or a blanket licence.

**Inference:** separate adopted article-31 legal instruments from speech transcripts governed by article 32 and from reports/explanatory prose with unverified grants. A document's presence beside a law does not establish identical rights. Human parliamentary drafting and recorded speech are evidence, but OCR, quotations, later additions and any transcription automation remain unverified. Obtain selected adopted text through the official query routes linked by the guide; aggregate bytes, date coverage after selection and tokens are unknown. Conditional keep only for a verified article-31 subset; raw speeches do not enter usable totals. T06 is an alternative delivery of overlapping proceedings, not an extra independent corpus.

### T06. ParlaMint-TR 4.1

The [release record][PM] labels the corpus CC BY 4.0 and offers `ParlaMint-TR.tgz`, listed as 280.68 MB, containing TEI and derived plain text/metadata. It was not downloaded. The [v4.1 root header][PM-H] gives **49,255,262 words**, **681,052 speeches**, dates **2011-06-28 to 2022-11-17**, and the same licence. The [release statistics][PM-STATS] independently round the Turkish size to 49.26M words. **Inference:** 49,255,262 * 1.5 to * 2.5 gives **73,882,893 to 123,138,155 tokens**. Do not convert the compressed bundle or treat annotation tokens as model tokens.

Human evidence is attributed TBMM speech transcription. The header reports conversion to TEI, spacing normalization and no correction of source texts. It does not certify every transcription tool. **Risk, Inference:** transcription errors, quotations, translated segments and underlying speech-rights coverage need checking. A CC grant from the corpus publisher does not establish control of every speaker's rights under article 32. Restrict the proposed text to original Turkish utterances; acceptability of human speech transcripts under the human-written rule is open for the owner. The release distinguishes original text, linguistic annotations and a separate machine-translated English release. No machine translation or generated annotation is proposed as Turkish pretraining prose. Conditional keep; its quantified attribution-class scenario is available only if the underlying-rights and provenance conditions are met.

### T07. JEAA articles, not all of DergiPark

The [journal's Turkish licence policy][J-LIC] states CC BY 4.0 for its articles, with authors retaining copyright. The [ethics policy][J-ETH] describes authorship and publication responsibilities. **Inference:** this is a source-specific lead for attributable academic prose, not permission for every journal on the hosting platform. Match the policy with each article version's notice and exclude separately licensed quotations/material and non-Turkish bodies.

The [archive][J-ARCH] shows issues from 2019-12-31 to 2026-06-30 when accessed; original writing dates and aggregate Turkish body-word counts were not established. **Inference:** tokens unknown. Named authors and editorial review support human authorship, but do not exclude translation assistance or model-written passages, particularly in later issues; no complete model-use audit was found. Obtain individual article PDFs through the archive, retaining DOI, author, journal, licence and date. No PDF collection or text sample was downloaded. Conditional keep after article-level rights, extraction, date and authorship checks, with unknown incremental volume.

### T08. Turkish National Corpus

The [authors' original paper][TNC-P] describes **50M words**, **1990 to 2009**, mostly sampled written material with a spoken component, and free non-commercial use. **Inference:** at the declared word conversion this is **75M to 125M tokens**, not eligible volume. The corpus spans books and periodicals; its compilers' access arrangement is not proof of an open grant from all underlying authors.

The [project site][TNC] returned an access error; the exact agreement, version, attribution/SA/ND terms, redistribution and bulk-download permission could not be read. The paper describes a web search interface and rule-based morphological annotation. **Risk, Inference:** older publication dates and curated source genres support human origin but do not certify all transcriptions or translations. Reject the offered access route for now, on missing open rights and full terms. Do not equate free non-commercial querying with an open corpus for volunteer training. Current size and current access conditions remain unverified.

### T09. mC4 Turkish

The [mT5 author paper][MT5], table 6, reports **71M Turkish pages and 88B tokens** in its tokenizer. It uses the then-available **71 monthly Common Crawl snapshots**, language identification with `cld3`, line filtering and deduplication. Complete first/last crawl dates and original writing dates were not verified. The [distribution card][MC4] identifies ODC-BY and Common Crawl terms. The database licence expressly does not grant copyright in individual contents.

**Risk, Inference:** a neural language classifier selects language, not human authorship; bots, machine translations and copied material remain possible. No generation step is described for the original text, but no human-only audit is provided. The legacy card directs readers to `allenai/c4`; a permitted, version-matched Turkish bulk download and its current archive bytes were not independently established. **Inference:** Chorus tokens and an independently open-licensed retained subset are unknown. Reject as offered. Its size cannot be added to its derivatives T11/T13 or counted as licensed Turkish prose.

### T10. OSCAR 22.01 Turkish

The [publisher's source card][OSCAR] explicitly limits CC0 to packaging/metadata/annotations and says it owns none of the extracted text. Its current access notice says access is suspended pending clarification. No request, jurisdictional affirmation or gated download was made. The [version documentation][OS-DOC] identifies the November/December 2021 crawl and document-oriented gzip JSONL layout.

Published Turkish scale is **75.1 GB**, **10,826,031 documents**, **6,421,221,358 space-separated tokens** [OSCAR]. **Inference:** the word-unit conversion gives **9.632 to 16.053B hypothetical subword tokens**. This is rejected volume. The bytes include serialization/metadata and are not converted. `Ungoliant`/FastText language classification and heuristic annotations do not establish human authorship. **Risk, Inference:** document-level classification can retain other languages, bots and machine translation; all generation/model-use paths were not audited. Reject for underlying rights and access conditions. CC0 does not turn the crawled prose into public domain.

### T11. CulturaX Turkish

The [current source card][CULT] reports **94,207,460 documents and 64,292,787,164 tokens** for Turkish. Its licence section says to follow mC4 and OSCAR terms; it supplies no new blanket underlying-text grant. The [author paper][CULT-P], table 1, rounds this to 94.21M documents and 64.29B tokens. Its processing uses language identification and Wikipedia-trained SentencePiece/KenLM perplexity filtering plus deduplication. These are models used in selection, not a claim that the retained prose was rewritten.

It combines mC4 with OSCAR releases through 23.01, which includes a late-2022 crawl [OS23]. **Risk, Inference:** AI-era text, bots, translation and inherited rights gaps remain; cleaning is not a human-only test. Original writing-date range and archive bytes were not verified. Obtain the `tr` Parquet configuration through the Hub's authenticated route if its terms and access are later cleared; no gated action was taken. **Inference:** publisher tokens are not Chorus tokens; eligible retained volume is unknown. Reject as offered, and never add its full count to mC4/OSCAR parents.

### T12. FineWeb2 Turkish

The [publisher card][FW2], with changelog through v2.1.1, publishes Turkish **41,933,799,420 words**, **95,129,129 documents**, **284.52 GB UTF-8 text** and **125.53 GB disk**. It explicitly reports word counts instead of a universal model-token count. **Inference:** applying the declared word-unit range gives **62.901 to 104.834B tokens** before any rights/authorship exclusions. No such tokens enter usable totals.

The underlying crawls span summer 2013 through April 2024. ODC-By and Common Crawl terms do not establish page-level permissions. The documented pipeline uses GlotLID language classification, extraction, heuristic filtering, global deduplication and replacement of some personal identifiers. **Risk, Inference:** those operations do not certify human origin; machine translation, bots and AI-era writing can remain. The card does not report generative rewriting of all prose or a complete synthetic-text audit. Obtain the `tur_Latn` Parquet subset at a pinned version; rehydration/upsampling changes presentations, not unique volume. Reject as offered, with rights-allowlisted recoverable volume unknown.

### T13. VNGRS Web Corpus

The [publisher card][VN] labels its release **CC BY-NC-SA 4.0** and reports **50.3M pages and 25.33B VBART-tokenizer tokens**. Its metadata lists **84,893,303,434 download bytes** and **141,807,806,497 generated-storage bytes**, neither independently measured here or converted. It is a cleaned Turkish combination of OSCAR-2201 and mC4, not a separately rights-verified text source. The card's pipeline citation has a mismatched paper label/link; this was not used as proof of exact cleaning behaviour. It also states research-only use and prior consent for other purposes. **Inference:** record that extra restriction alongside its CC label; their legal interaction was not resolved.

**Inference:** retain the NC, attribution and SA conditions, parent licences and unknown page rights separately. The project being open source does not answer the NC question. **Risk, Inference:** parent text has uncertain human authorship, machine translation and bot contamination; complete filtering-model use and original writing-date range were not verified. The parent release date does not establish the writing date of every document. Parquet shards are listed through the Hub configuration, but none was downloaded. **Inference:** Chorus token count is unknown. Reject as offered on restrictions and underlying-rights/provenance gaps, without deciding whether NC or any particular classifier is acceptable under OD-3/OD-4.

## Volume by licence class and overlap

All arithmetic here is **Inference:**. These classes match #53's underlying-rights classes; legal statutory freedoms are identified explicitly inside the first class rather than called CC0. Conditions apply before any number becomes a usable amount.

| Underlying text class | Conditional quantified planning scenario | Unknown additions and conditions | Audited usable amount established |
|---|---|---|---|
| Public domain and CC0, including separately identified statutory freedom | **Unknown** | Rights-verified T02 books; T03/T04/T05 qualifying article-31 text. T10's CC0 wrapper contributes no cleared prose | No positive measured amount; unknown is not zero |
| Attribution-only text | T06: **0.073882893 to 0.123138155B tokens** | Only if underlying speech rights and human transcript provenance are established; T07 incremental volume unknown | No positive measured amount |
| Share-alike text | T01 newer snapshot: **0.175201901 to 0.438004752B tokens** | Resolve revision/import licences, attribution, AI-era provenance and extraction. T02 SA subset unknown | No positive measured amount |
| Other, restrictive or unresolved rights | **Zero included** | T08 to T13 as offered, plus non-article-31 raw proceedings in T05; headline sizes are not usable amounts | Zero counted under this conservative selection |

The quantified sum is **0.249084794 to 0.561142907B tokens**. This adds only the two different source collections, not alternative versions or derivatives. It still has unmeasured quotations, repeated boilerplate and cross-source overlap. Formally, `U = rW * TW + rP * TP - O + A`, where rW and rP are measured retained fractions, O is retained cross-source overlap, and A is incremental deduplicated text from approved unquantified sources. These quantities were not measured. Therefore there is no justified positive lower bound after checks. If parliamentary speech rights are not established, set the ParlaMint term to zero; if SA is rejected, set the Wikipedia term to zero. Rejected web mixtures contribute neither a lower bound nor an approved ceiling.

The older Wiki40B train alternative is **0.04892 to 0.12230B tokens** under the same character scenario, replacing newer Wikipedia rather than adding to it. With ParlaMint its gross alternative is **0.122802893 to 0.245438155B**. The paper's own 53.0M publisher tokens are an independent, tokenizer-specific reference. Do not train on its dev/test splits to inflate volume. Reserve future evaluation material and remove duplicated books, statutes, decisions and proceedings across T01 to T07 before counting training volume.

## Ratio to English, pinned to #53

The remote branch existed. The note read was `origin/research/53-english-sources` at **e637be6b87af34d065f95c7511e7d65ed0f5d8b1**, [immutable note link][EN]. Its quantified scenarios are public domain **4.08 to 6.80B**, SA **3.24 to 5.40B**, combined **7.32 to 12.20B**; its attribution-only volume is unknown. These are conditional English components, not audited usable totals. English uses text-byte conversions, Turkish uses text-character/word conversions. The snapshots and curated domains differ.

**Inference:** for intervals TR = [a,b] and EN = [c,d], the unconstrained ratio scenario is [a/d,b/c]. This crosses independent sensitivity extremes and is not a confidence interval or a synchronized corpus-size comparison.

| Class | Turkish quantified scenario | English quantified scenario from pinned note | Turkish / English |
|---|---|---|---|
| Public domain / CC0 / identified statutory freedom | Unknown | 4.08 to 6.80B | **Unknown**, not zero |
| Attribution-only | 0.07388 to 0.12314B, speech-rights condition | Unknown | **Unknown** |
| Share-alike | 0.17520 to 0.43800B | 3.24 to 5.40B | **3.24% to 13.52%** |
| Other/restrictive/unresolved as offered | Zero included | Zero included | **Undefined**, no 0/0 percentage |
| Sum of the quantified conditional leads only | 0.24908 to 0.56114B | 7.32 to 12.20B | **2.04% to 7.67%** |

No ratio of fully audited usable corpora can be calculated from these notes. Unknown additions could change the ratios substantially. As a narrower historical check using the same paper and extraction family, Wiki40B table 2 gives Turkish train **244.6M characters** versus English train **8,862.1M characters** [W4]. **Inference:** that character ratio is **2.76%**. It is not the newer Wikipedia ratio or a substitute for the required per-class comparison.

## Model size and repetition

The [assistant specification](../assistant-spec.md), section 7, gives approximately **100M to 1B parameters**, to be calculated from OD-6 rather than assumed. The [roadmap](../ROADMAP.md), step 4.3, describes a pilot around **100M to 300M**. Neither a device nor a final size is chosen here.

[Hoffmann et al. 2022][CHIN], table 1 and compute-optimal analysis, pair Chinchilla's **70B parameters with 1.4T training tokens**, and find approximately proportional scaling of parameters and data. **Inference:** use `D approximately 20N` as a rounded starting point, since 1.4T / 70B = 20. This is a compute-allocation heuristic, not a minimum for learning, a Turkish-specific law, or a validated MoE-total-parameter rule. OD-6 inference memory and any sparse-architecture scaling need their own calculation.

[Muennighoff et al. 2023][REPEAT], abstract, sections 5 to 7 and appendix Q, find little loss change with up to about **four epochs** in their studied setting, then diminishing returns. Their fitted repeated-data model has substantial diminishing returns around **sixteen epochs**; these are not hard cutoffs or Turkish guarantees. They study mostly English C4/OSCAR and fixed training choices. Appendix Q explicitly distinguishes repeating only a fraction of data from their whole-corpus scenario. **Inference:** a bilingual Turkish-only oversampling scenario is a budget calculation, not a direct replication of their result.

**Inference:** D is training-token presentations, U is distinct retained Turkish volume and f is the Turkish share of total presentations. Turkish passes are `E_TR = fD/U`; repeats after the first pass are E_TR minus 1 when positive. The table below first sets f = 1 to compare a fully Turkish budget. Bilingual f = 0.5 is an illustration, not an owner decision. It does not assert either language alone needs 20N tokens.

| Parameters | Approximate total training presentations, 20N | Unique Turkish needed at four passes, f = 1 | Unique Turkish needed at four passes, f = 0.5 |
|---|---|---|---|
| 100M | 2B | 0.5B | 0.25B |
| 300M | 6B | 1.5B | 0.75B |
| 1B | 20B | 5B | 2.5B |

**Inference:** required passes for the newer quantified leads, assuming all their gross volume survives and no overlap or holdout loss. A range lists the high-volume case first. Repeated presentations do not create new unique text.

| Allowed quantified classes | 100M, f = 1 | 300M, f = 1 | 1B, f = 1 | 100M / 300M / 1B, f = 0.5 |
|---|---|---|---|---|
| Public domain / statutory only | Unknown | Unknown | Unknown | Unknown at every size |
| Attribution-only, T06 rights condition | 16.24 to 27.07 | 48.73 to 81.21 | 162.42 to 270.70 | 8.12 to 13.53 / 24.36 to 40.60 / 81.21 to 135.35 |
| Share-alike, T01 conditions | 4.57 to 11.42 | 13.70 to 34.25 | 45.66 to 114.15 | 2.28 to 5.71 / 6.85 to 17.12 / 22.83 to 57.08 |
| Attribution plus SA, both conditions | **3.56 to 8.03** | **10.69 to 24.09** | **35.64 to 80.29** | **1.78 to 4.01 / 5.35 to 12.04 / 17.82 to 40.15** |

**Assessment, Inference:** public-domain/statutory-only and attribution-only evidence does not establish support for the planned range. With SA alone, a 100M, half-Turkish pilot fits four passes only if retained unique Turkish is at least 0.25B, which lies inside its gross scenario; a fully Turkish 100M run exceeds four passes even at the high end. Combining SA with a separately cleared ParlaMint lead could support a 100M fully Turkish budget within four passes only if retained U reaches 0.5B, near the top of the gross range. A half-Turkish 100M budget needs U at least 0.25B. None of these retention conditions was measured, so they support investigating a pilot, not declaring its data ready.

For **300M at half Turkish**, the combined gross pool requires **5.35 to 12.04 Turkish passes**, already beyond the approximately four-epoch finding; larger approved sources or an owner-accepted repeated-data experiment are needed. For **1B at half Turkish**, **17.82 to 40.15 passes** are required even before filtering, past the fitted sixteen-epoch diminishing-return reference. These figures do not support a 1B, half-Turkish commitment on the current evidence. With a smaller f, requirements fall: for example f = 0.1 at 1B gives the same Turkish presentations as f = 1 at 100M, but neither Turkish competence nor that language allocation follows from the arithmetic.

If OD-4 instead requires the older Wiki40B alternative, the combined pool gives **8.15 to 16.29 passes** at 100M with f = 1, or **4.07 to 8.14** with f = 0.5. Even this older alternative has no source-wide human-only certificate. More approved English tokens cannot by themselves establish Turkish task quality. Any pilot still needs held-out Turkish loss and the bilingual sandbox evaluation, independently of memory feasibility.

## Verification, unknowns and scope limits

Examined **13 candidate sources**: **7 conditional keeps**, **6 rejects**, **0 unconditional approvals**. Primary legal texts were fetched directly: BY 4.0, BY-SA 3.0, BY-SA 4.0, BY-NC-SA 4.0, CC0 1.0, ODC-By v1.0, Common Crawl terms and Law 5846. T01/T02 licence claims were checked against publisher/wiki policies and the CC legal codes; T03/T04/T05 against the statute; T06/T07 against publisher grants and BY's controlled-rights limit; T08 has no readable full agreement and is rejected; T09 to T13 were checked against original distribution policies, legal codes and explicit parent/underlying-rights limits. No missing licence was filled from a search result or an unofficial mirror.

- **T01:** no verified human-retention fraction, project tokenizer, exact original revision range, complete import/attribution recovery, or resolved 3.0/4.0 card mismatch. The statistics API is live, the mean is rounded, and full text was not independently counted. Wiki40B's exact original dump date and equivalence to today's TFDS release are unverified.
- **T02:** dump date/bytes were inaccessible; eligible work count, date range and extracted text by PD/SA class are unknown. No universal Ottoman-book cutoff is asserted.
- **T03 to T05:** aggregate selected dates, characters/words, tokens, bulk access and deduplicated incremental volume were not established. The Mevzuat service timed out; AYM yielded an application shell. Commission reports and speech rights were not blanket-cleared.
- **T06:** the publisher licence is verified; control of underlying speaker rights, a human-only transcript audit, held-out allocation and cross-source overlap are not. The published word count was not reproduced from speech files.
- **T07:** per-article historic licence consistency, Turkish body totals, non-Turkish/quotation exclusions and use of AI/translation tools are unverified. Archive dates do not date every sentence.
- **T08:** exact licence agreement/version, current access/download terms, current size and underlying permissions are unavailable. The 50M figure is the original authors' published scale.
- **T09 to T13:** no rights-clean human-written subset size, retained proportion, Chorus token conversion or complete original writing-date range was established. T09 version-matched bulk access and current archive bytes; T10 metadata-versus-text bytes and suspended-route availability; T11 archive bytes; T12 manifest byte reconciliation and full model-use history; T13 independent archive-byte reconciliation, extra restriction's interaction with CC, and exact cleaning-model inventory remain unverified. Their published counts use different token definitions and overlapping parent data.
- **Law:** the relevant Turkish articles and the ministry's English counterpart were read. Consolidation through every amendment as of the access date, applicability in each volunteer jurisdiction and the copyright status of weights were not established.
- **Arithmetic:** conversions, sums, class-ratio extremes and repetition tables were recomputed. All retention, overlap, tokenizer and language-mixture assumptions remain hypotheses, not measurements.

**Not covered:** the post-AI web text policy (#55); download, filtering, attribution infrastructure, deduplication or pipeline work (#56); model/tokenizer training; exhaustive title/article clearance; model quality and local device feasibility. The English ratio is included, pinned to #53's remote commit; a ratio of actually audited usable text remains unavailable. This is not an exhaustive inventory of all Turkish sources. Additional libraries, news archives, parallel translations and web subsets need independent rights/provenance work before counting them.

## Questions for the owner

1. **OD-3 / OD-10:** which text licences, statutory freedoms and compilation obligations are acceptable, and how will attribution, notices, share-alike and any implications for released weights be handled? NC sources remain outside the conservative totals.
2. **OD-3:** what territorial and edition evidence is required for old books and article-31 materials, and what evidence establishes rights to use parliamentary speeches beyond article 32's purpose-limited freedom? The ParlaMint volume depends on that unresolved condition.
3. **OD-4 / D32:** what evidence is sufficient for wiki revisions, historical transcriptions, human-speech transcripts, translations and scholarly text? Is the November 2023 Wikipedia snapshot eligible after review, or is an older snapshot required? Are classification/perplexity models acceptable when original prose is retained?
4. **OD-6 / OD-7:** which device, architecture, model size, tokenizer and Turkish sampling fraction should the later measurement target? A retained-token threshold and held-out evaluation are needed before a model-size commitment; this note selects none of them.

## Primary-source register

Access date for every link: **2026-10-25**. The source-count above counts candidate collections, not every document, legal code or metadata endpoint examined. Failed endpoints are explicitly labelled rather than used as licence or volume evidence.

| Reference | Primary evidence read |
|---|---|
| W1 to W3 | [Pinned Wikimedia dataset card][W1]; [full-split Turkish statistics JSON][W2] and [API definitions][W2-DOC]; [Wikimedia's licence transition][W3] and [terms, section 7][WM-TERMS] |
| W4 to W6 | [Wiki40B paper][W4], sections 2.1 to 2.6 and table 2; [TFDS builder's dataset licence][W5]; [current catalogue][W6] |
| WS | [Turkish Wikisource copyright policy][WS]; [dump listing, access failed][WS-DUMP] |
| LAW | [Ministry laws index][LAW-HOME], its [Turkish law PDF][LAW] and [English counterpart][LAW-EN]; [direct consolidation endpoint, timeout][LAW-MEV]; [ministry website terms][KTB-TERMS] |
| MEV, AYM, TBMM | [Mevzuat, timeout][MEV]; [AYM decision application, JS shell][AYM]; [TBMM's Turkish access/coverage guide][TBMM] |
| PM | [CLARIN 4.1 release and licence][PM]; [v4.1 Turkish descriptive header][PM-H]; [v4.1 word/date statistics][PM-STATS] |
| J | [JEAA licence][J-LIC], [ethics][J-ETH] and [dated archive][J-ARCH] |
| TNC | [Original authors' corpus-construction paper][TNC-P]; [project site, access failed][TNC] |
| MC4, MT5 | [mC4 distribution card][MC4]; [mT5 paper][MT5], section 3.1 and table 6 |
| OSCAR | [Publisher source card and access/licence notice][OSCAR]; [22.01 version documentation][OS-DOC]; [23.01 parent-date/filter documentation][OS23] |
| CULT | [CulturaX source card][CULT] and [original author paper][CULT-P], processing sections and table 1 |
| FW2, VN | [FineWeb2 raw publisher card][FW2]; [VNGRS raw publisher card][VN] |
| CHIN, REPEAT | [Hoffmann et al. PDF][CHIN], compute-optimal analysis/table 1; [Muennighoff et al. paper][REPEAT], abstract, sections 5 to 7 and appendix Q |
| EN | [English survey at the exact remote commit read][EN], class totals and uncertainty definitions |

[L-BY4]: https://creativecommons.org/licenses/by/4.0/legalcode.txt
[L-SA3]: https://creativecommons.org/licenses/by-sa/3.0/legalcode.txt
[L-SA4]: https://creativecommons.org/licenses/by-sa/4.0/legalcode.txt
[L-NCSA4]: https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.txt
[L-CC0]: https://creativecommons.org/publicdomain/zero/1.0/legalcode.txt
[L-ODC]: https://opendatacommons.org/licenses/by/1-0/
[L-CC]: https://commoncrawl.org/terms-of-use
[W1]: https://huggingface.co/datasets/wikimedia/wikipedia/raw/b04c8d1ceb2f5cd4588862100d08de323dccfbaa/README.md
[W2]: https://datasets-server.huggingface.co/statistics?dataset=wikimedia%2Fwikipedia&config=20231101.tr&split=train
[W2-DOC]: https://huggingface.co/docs/dataset-viewer/statistics
[W3]: https://diff.wikimedia.org/2023/06/29/stepping-into-the-future-wikimedia-projects-transition-to-creative-commons-4-0-license/
[WM-TERMS]: https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use#7._Licensing_of_Content
[W4]: https://aclanthology.org/2020.lrec-1.297.pdf
[W5]: https://raw.githubusercontent.com/tensorflow/datasets/master/tensorflow_datasets/text/wiki40b.py
[W6]: https://www.tensorflow.org/datasets/catalog/wiki40b
[WS]: https://tr.wikisource.org/wiki/Vikikaynak:Telif_haklar%C4%B1
[WS-DUMP]: https://dumps.wikimedia.org/trwikisource/latest/
[LAW-HOME]: https://telifhaklari.ktb.gov.tr/TR-332443/kanunlar.html
[LAW]: https://telifhaklari.ktb.gov.tr/Eklenti/106879,fikir-ve-sanat-eserleri-kanunupdf.pdf?0
[LAW-EN]: https://telifhaklari.ktb.gov.tr/Eklenti/144855,lawonintellectualandartisticworks2026pdf.pdf?0
[LAW-MEV]: https://www.mevzuat.gov.tr/MevzuatMetin/1.3.5846.pdf
[KTB-TERMS]: https://hukuk.ktb.gov.tr/TR-137347/site-kullanim-kosullari-yasal-uyari.html
[MEV]: https://www.mevzuat.gov.tr/
[AYM]: https://kararlarbilgibankasi.anayasa.gov.tr/
[TBMM]: https://www.tbmm.gov.tr/kanun-ve-karar-bilgi-sistemi
[PM]: https://www.clarin.si/repository/xmlui/handle/11356/1912
[PM-H]: https://raw.githubusercontent.com/clarin-eric/ParlaMint/v4.1/Samples/ParlaMint-TR/ParlaMint-TR.xml
[PM-STATS]: https://raw.githubusercontent.com/clarin-eric/ParlaMint/v4.1/Build/Metadata/ParlaMint-overview-stats.tsv
[J-LIC]: https://dergipark.org.tr/tr/pub/jeaa/page/18354
[J-ETH]: https://dergipark.org.tr/tr/pub/jeaa/policy
[J-ARCH]: https://dergipark.org.tr/tr/pub/jeaa/archive
[TNC]: https://www.tnc.org.tr/
[TNC-P]: https://aclanthology.org/L12-1590.pdf
[MC4]: https://huggingface.co/datasets/legacy-datasets/mc4/raw/main/README.md
[MT5]: https://arxiv.org/pdf/2010.11934
[OSCAR]: https://huggingface.co/datasets/oscar-corpus/OSCAR-2201/blob/main/README.md
[OS-DOC]: https://oscar-project.github.io/documentation/versions/oscar-2201/
[OS23]: https://oscar-project.github.io/documentation/versions/oscar-2301/
[CULT]: https://huggingface.co/datasets/uonlp/CulturaX/blob/main/README.md
[CULT-P]: https://arxiv.org/pdf/2309.09400
[FW2]: https://huggingface.co/datasets/HuggingFaceFW/fineweb-2/raw/main/README.md
[VN]: https://huggingface.co/datasets/vngrs-ai/vngrs-web-corpus/raw/main/README.md
[CHIN]: https://arxiv.org/pdf/2203.15556
[REPEAT]: https://arxiv.org/html/2305.16264v3
[EN]: https://github.com/Cassandra-Collective/CASSANDRA-Chorus/blob/e637be6b87af34d065f95c7511e7d65ed0f5d8b1/docs/research/2026-10-25-english-pretraining-sources.md
