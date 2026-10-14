# 2026-10-14 · Links to the Cassandra-Collective organisation (D46), and the org header

| | |
|---|---|
| PLAN step | none (housekeeping) |
| Branch | `docs/org-move`, stacked on `process/approvals-and-backlog` (#110) |
| SRS requirements | D46 (new), D1 (annotated) |
| Status | Verified on 2026-10-14 (link re-grep; header render checked on GitHub) |

Project prose style: no em or en dashes.

## Problem / Motivation

On 2026-10-14 the owner moved this repository, with CASSANDRA, Ephesus and Dervish, from the personal account `mertefesensoy` to the GitHub organisation `Cassandra-Collective`. GitHub redirects the old URLs only until a repository is created at the old path, and this repository links to itself and to CASSANDRA in 100 places: the README, NOTICE, SRS, PLAN, ROADMAP, the Stage 0 report and research documents, and the issue table and backlog file of #110. The move was an owner decision that the SRS did not record. The owner also asked for a small "part of the collective" header on each project README, using the organisation's new mark.

Issue: #111.

## What Changed

| File | Description |
|---|---|
| `docs/planning/2026-10-14-backlog-issues.md` | 89 issue links now point at the organisation. |
| `docs/SRS.md` | Repository field and D1 updated; D1 notes the old account and refers to D46. New decision D46 records the move. |
| `docs/PLAN.md` | Repository field and the paragraph that records the repository decision (2 links). |
| `README.md` | The CASSANDRA link (1), and a one-line header above the title: the small Forecast mark and "Part of the Cassandra Collective". |
| `docs/planning/2026-10-14-backlog.toml` | The `repo` field, which `scripts/ops/seed_backlog.py` uses for every API call and for the `{blob}` links it renders into issue bodies, now names `Cassandra-Collective/CASSANDRA-Chorus`; plus one link in an issue body. `owner_login` stays `mertefesensoy`: it is the owner's account, used to assign issues. |
| `NOTICE`, `docs/ROADMAP.md`, `docs/stage0-report.md`, `docs/research/2026-10-11-deep-research-prompt.md`, `docs/research/2026-10-11-stage0-literature-report.md` | One link each. |
| `docs/implementations/2026-10-14-org-move-links-and-header.md` | This document. |

## Implementation Approach

One scripted replacement over every git-tracked text file: `github.com/mertefesensoy/(CASSANDRA|CASSANDRA-Chorus|Ephesus|Dervish)` becomes `github.com/Cassandra-Collective/<same name>`, followed by a re-grep. A second grep for the bare account name found the backlog file's `repo` field, which is not a URL and was changed by hand. Hugging Face paths, repositories that stayed under the personal account, and dated statements of where something was done (such as the seeding record in `2026-10-14-team-workflow-and-backlog.md`) are untouched.

The branch is stacked on #110 because #110 adds 91 of the 100 links (the issue table and the backlog file) and the decisions D42 to D45; basing it on `main` would leave those links behind and collide on the next D-number. When #110 is merged, GitHub retargets this pull request to `main`.

The header loads the small Forecast mark from the organisation's brand folder by absolute URL (`raw.githubusercontent.com/Cassandra-Collective/.github/main/brand/svg/cassandra-mark-small-on-*.svg`), so a later change to the mark updates every README at once, and a `<picture>` element picks the light or dark variant.

## Mathematical / Statistical Details

None: links, a decision record and markup only.

## Design Decisions

- **Dated records updated, not just live pointers.** The links are there to be followed. D1 keeps its history by naming the old account and referring to D46, rather than being rewritten silently.
- **An issue for this pull request (#111),** as D45 requires. The owner waived issues for the logo work in `Cassandra-Collective/.github`, not for this repository.
- **The same header markup as CASSANDRA and Dervish**, checked rendering on GitHub in light and dark mode (small mark at 20 px, vertically centred on the text line within 3 px).

## Verification

- The replacement reported 100 links in 10 files; `git grep -i -E "github\.com/mertefesensoy/(CASSANDRA|Ephesus|Dervish)"` then returns nothing.
- `python -m pytest tests/test_seed_backlog.py` (Python 3.13.14): 9 passed. The tests use their own fixture repository (`o/r`), so they confirm the script still works but not the new value; the backlog file was parsed with `tomllib` and reads `repo = Cassandra-Collective/CASSANDRA-Chorus` with all 89 issues. No other code changed.
- The README header renders on this branch (see the pull request).

**Not tested:** links in issue and pull request bodies on GitHub itself still name the old account; GitHub redirects them.

## Related Docs

- `docs/SRS.md`, decisions D1, D45, D46
- Organisation brand guide: https://github.com/Cassandra-Collective/.github/blob/main/brand/README.md
