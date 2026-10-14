# 2026-10-14 · Links to the organisation code of conduct, security policy and support page

| | |
|---|---|
| PLAN step | none (housekeeping) |
| Branch | `docs/conduct-and-security` |
| SRS requirements | D45 (every pull request closes an issue; conventions in `CONTRIBUTING.md`) |
| Status | Planned |

Project prose style: no em or en dashes.

## Problem / Motivation

On 2026-10-14 the owner asked for a contributing guide, a code of conduct and issue and pull request templates in every repository of the Cassandra Collective organisation. This repository already has the contributing guide (`CONTRIBUTING.md`, D45), four issue forms and a pull request template. It has no code of conduct and no security policy, and nothing in it tells a contributor how to report a security problem.

That gap matters more here than in most repositories. Chorus is meant to run on volunteers' machines (README; `docs/ROADMAP.md`, principle 2: "A volunteer's client runs only signed, released code"), so a vulnerability can reach people who never read this repository. A report filed as a public issue would tell everyone before there is a fix. Blank issues are disabled (`blank_issues_enabled: false`), so a reporter who finds no other route is pushed towards one of the public issue forms.

The owner decided the same day that the code of conduct, the security policy and the support page are organisation defaults, kept in https://github.com/Cassandra-Collective/.github and written in a separate pull request there. Private vulnerability reporting has been enabled for this repository. What is left here is to point contributors at those files and at the private report form.

Issue: #116.

## What Changed

| File | Description |
|---|---|
| `CONTRIBUTING.md` | Three new sections at the end: 9 "Code of conduct", 10 "Reporting security problems" (private vulnerability report, the organisation security policy, never in public) and 11 "Getting help" (the support page). Sections 1 to 8 are unchanged. |
| `.github/ISSUE_TEMPLATE/config.yml` | Adds `contact_links` for the private vulnerability report, the code of conduct and the support page. `blank_issues_enabled: false` is kept. |
| `docs/implementations/2026-10-14-conduct-and-security-links.md` | This document. |

`.github/pull_request_template.md` is not changed (see Design Decisions).

## Implementation Approach

Links only; no file is copied from the organisation repository. The four targets are:

| Target | URL |
|---|---|
| Code of conduct | https://github.com/Cassandra-Collective/.github/blob/main/CODE_OF_CONDUCT.md |
| Security policy | https://github.com/Cassandra-Collective/.github/blob/main/SECURITY.md |
| Support | https://github.com/Cassandra-Collective/.github/blob/main/SUPPORT.md |
| Private vulnerability report | https://github.com/Cassandra-Collective/CASSANDRA-Chorus/security/advisories/new |

**`CONTRIBUTING.md`.** The new sections are appended as 9, 10 and 11, so the numbers of sections 1 to 8 do not move. Nothing in the repository refers to a section of `CONTRIBUTING.md` by number today (checked with `git grep`), but appending keeps the existing text byte for byte and leaves any future references safe. Section 10 says how it differs from section 6 ("Hosts, tokens and security"): section 6 is about handling tokens and fetched files, section 10 about reporting a problem someone has found. The new sections describe only what the links are and when to use them, not what the organisation files say, because those files are written and reviewed in the organisation repository and can change there.

**`config.yml`.** GitHub's issue template chooser reads `contact_links`, a list in which each entry has a `name`, a `url` and an `about` text, and shows each entry as a button next to the issue forms. Three entries are added, the private vulnerability report first, because it is the one a reporter must not miss.

**Order of merging.** The three organisation links resolve only after the community-health pull request in Cassandra-Collective/.github is merged. That pull request is merged first; this one has no other dependency.

## Mathematical / Statistical Details

None: links and prose only.

## Design Decisions

- **Organisation defaults, linked rather than copied (owner, 2026-10-14).** GitHub applies an organisation's default community health files (from its `.github` repository) to every repository in the organisation that has no file of the same kind of its own. A copy here would switch that off for this repository and then drift from the organisation text. A link keeps one source of truth, and a change to the organisation policy reaches every repository at once.
- **Private vulnerability reporting rather than an e-mail address.** It is enabled for this repository (owner, 2026-10-14). It needs no address published in the repository, keeps the report and the discussion of a fix in one private place, and lets the maintainers publish an advisory when the fix ships.
- **The private report link is in the issue chooser too.** Contributors who never open `CONTRIBUTING.md` still see it on the new issue page, where a public report would otherwise be filed. GitHub may add its own security policy entry to the chooser once the organisation security policy is in effect, which would show two security entries. Both lead to private reporting; the explicit one is kept because it works today and names the project's rule. The owner may drop it if the duplicate is unwanted.
- **A support entry as well.** With blank issues disabled, a plain question has no form; the support page is the place to send it.
- **The pull request template is unchanged.** Its checklist already has a security line ("No tokens, keys or personal data"), and every item on it is about the pull request's own content. Where to report a vulnerability is a question for someone who has found one, and the issue chooser and section 10 answer it where that person looks.
- **No new SRS D-number.** The owner's decision of 2026-10-14 is an organisation decision, made for all of the organisation's repositories and recorded in the organisation repository. This pull request applies it here without adding a decision of its own.
- **An issue for this pull request (#116),** as D45 requires.

## Verification

Planned:

- Parse `config.yml` with PyYAML `safe_load`; check that `blank_issues_enabled` is still `false`, that there are exactly three contact links, each with `name`, `url` and `about`, and that the file has no other keys.
- Check that no other test reads these files (`git grep` over `tests` and `scripts`), then run the full test suite.
- Byte-wise search for U+2013 and U+2014 in every changed file.
- Check that the private vulnerability report link works: `gh api repos/Cassandra-Collective/CASSANDRA-Chorus/private-vulnerability-reporting`.
- Record whether the three organisation files exist on `.github` main at the time the pull request is opened.

**Not tested:** to be completed.

## Related Docs

- `CONTRIBUTING.md`
- `docs/SRS.md`, decisions D45 and D46
- Organisation repository: https://github.com/Cassandra-Collective/.github
- GitHub documentation: "Creating a default community health file", "Configuring issue templates for your repository" (`contact_links`), "Privately reporting a security vulnerability"
