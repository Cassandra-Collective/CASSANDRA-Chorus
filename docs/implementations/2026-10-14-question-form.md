# 2026-10-14 · A Question form in the issue chooser

| | |
|---|---|
| PLAN step | none (housekeeping) |
| Branch | `docs/question-form` |
| SRS requirements | D45 (every pull request closes an issue: #118) |
| Status | Verified (YAML parsed; the same form renders as valid in `Cassandra-Collective/.github`) |

Project prose style: no em or en dashes.

## Problem / Motivation

On 2026-10-14 the owner turned blank issues off in every repository of the organisation. Here they were already off, but the forms (task, bug, decision, experiment) have no place for a question. `CONTRIBUTING.md` sends questions to the organisation support page, and that page now says every repository has a Question form. Without one, someone with a question has no way to open an issue.

## What Changed

| File | Description |
|---|---|
| `.github/ISSUE_TEMPLATE/question.yml` | The organisation's Question form, unchanged: it asks for the question, what was tried or read, and the commit or version, and applies the label `question`. |
| `docs/implementations/2026-10-14-question-form.md` | This document. |

## Implementation Approach

The file is a byte-for-byte copy of `.github/ISSUE_TEMPLATE/question.yml` in `Cassandra-Collective/.github`, so every repository asks questions the same way. Its links are absolute, so they work from any repository. The label it applies, `question`, already exists here.

## Mathematical / Statistical Details

None: an issue form only.

## Design Decisions

- **Copy the organisation form rather than write a Chorus-specific one.** A question needs no Chorus-specific fields, and one wording across the organisation is easier to keep in step.
- **No change to `config.yml`.** `blank_issues_enabled` stays `false`, as it already was. The owner's decision of 2026-10-14 makes that the rule everywhere.

## Verification

- The form parses with PyYAML on Python 3.13.14, with `name: Question` and `labels: ['question']`.
- The `question` label exists (`gh label list`).
- The identical file in `Cassandra-Collective/.github` renders on GitHub as a valid issue form (checked in a browser on 2026-10-14).

**Not tested:** the new-issue page of this repository. It needs a signed-in account and the file on `main`.

## Related Docs

- `CONTRIBUTING.md` (questions)
- Organisation support page: https://github.com/Cassandra-Collective/.github/blob/main/SUPPORT.md
- `docs/implementations/2026-10-14-conduct-and-security-links.md`
