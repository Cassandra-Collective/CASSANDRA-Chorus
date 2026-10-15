# 2026-10-15 · Questions go to Discussions Q&A

| | |
|---|---|
| PLAN step | none (housekeeping) |
| Branch | `docs/discussions-qa` |
| SRS requirements | D45 (every pull request closes an issue: #120) |
| Status | Planned |

Project prose style: no em or en dashes.

## Problem / Motivation

On 2026-10-15 the owner turned on GitHub Discussions in every repository of the organisation. This repository now has the default categories, including **Q&A**, the one category whose threads can have an answer marked as accepted: https://github.com/Cassandra-Collective/CASSANDRA-Chorus/discussions/categories/q-a

Nothing pointed there. The "Questions and help" link on the new-issue page led to the organisation support page, and `CONTRIBUTING.md` section 11 sent questions that are not yet an issue to the same page. Section 11 did not mention the Question form added in #118 either, so a reader of the guide had no direct route for a question at all.

## What Changed

| File | Description |
|---|---|
| `.github/ISSUE_TEMPLATE/config.yml` | The "Questions and help" contact link becomes "Ask a question", pointing at this repository's Discussions Q&A, with an `about` line saying open questions and help go there; the security and code of conduct links and `blank_issues_enabled: false` are unchanged. |
| `CONTRIBUTING.md` | Section 11 "Getting help" points open questions first at Discussions Q&A, names the Question form for a question that should be tracked as an issue, keeps the rule that a question about an existing issue goes in its comments, and still links the support page. |
| `docs/implementations/2026-10-15-discussions-qa.md` | This document. |

## Implementation Approach

Two text edits, no code.

- In `config.yml` the third contact link is replaced in place, so the order on the new-issue page stays: security report, code of conduct, questions.
- In `CONTRIBUTING.md` only section 11 changes. It gives three routes with one rule for choosing: an open question goes to Discussions Q&A; a question that should be tracked, for example because its answer will need a change to the code or the documents, goes through the Question form (label `question`); a question about an existing issue goes in that issue's comments.

The Question form itself (`.github/ISSUE_TEMPLATE/question.yml`) is not changed.

## Mathematical / Statistical Details

None: links and wording only.

## Design Decisions

- **Replace the support link rather than add a fourth one.** The support page is organisation-wide and mostly says where to ask; with Q&A on, the direct route is more useful on the new-issue page. Section 11 still links the support page for what to expect.
- **Keep the Question form.** Some questions are bug reports or documentation gaps in disguise, and those belong in the tracker with a label. Without the form, and with blank issues off, a question could not be tracked at all.
- **Discussions do not weaken D45.** D45 tracks all work (tasks, features, bugs, research, experiments and owner decisions) as issues. An open question about how something works is not work; when the answer to one turns into work, that work becomes an issue as before.
- **Link the Q&A category, not the Discussions front page.** The category URL opens the list of Q&A threads, and a discussion started there can have an answer marked.
- **No new SRS D-number.** Turning Discussions on is the owner's organisation decision of 2026-10-15, applied here without a decision of its own, as #116 did for the organisation's code of conduct and security links.

## Verification

Planned:

- Parse `config.yml` with PyYAML `safe_load`; check that its keys are exactly `blank_issues_enabled` and `contact_links`, that `blank_issues_enabled` is still `false`, and that there are three contact links, each with exactly `name`, `url` and `about`.
- Check that the Q&A URL returns HTTP 200.
- Check that no test or script reads the changed files (`git grep` over `tests`, `scripts` and `cassandra_chorus`), then run the full test suite.
- Search every changed file for U+2013 and U+2014.

**Not tested:** to be completed.

## Related Docs

- `CONTRIBUTING.md`, section 11
- `docs/SRS.md`, decision D45
- `docs/implementations/2026-10-14-question-form.md` (the Question form, #118)
- `docs/implementations/2026-10-14-conduct-and-security-links.md` (the contact links, #116)
- Organisation support page: https://github.com/Cassandra-Collective/.github/blob/main/SUPPORT.md
