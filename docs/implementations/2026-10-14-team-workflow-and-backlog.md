# 2026-10-14 · Owner approvals, team workflow and the issue backlog

| | |
|---|---|
| PLAN step | Roadmap, all phases: the plan as tickets (`docs/ROADMAP.md`) |
| Branch | `process/approvals-and-backlog` |
| SRS requirements | D42 to D45 (new) |
| Status | Implemented: approvals recorded, issues #21 to #109 created and verified; this PR awaits the owner's review |

## Problem / Motivation

On 2026-10-14 the owner approved the plan presented after the prototypes, and PRs #18 (prototypes) and #19 (architecture draft 0.1). The owner also said they will now lead a team.

> "everything that we will need to do needs to be properly planned and every issue, problem, feature, need etc needs to be ticketed via github so i can assign them to my teammates. I approve all of the PRs and the plan but they need to be documented as such"

Until now the plan lived only in documents: the roadmap, the open-decision tables (AD-1 to AD-12 in the architecture, OD-1 to OD-10 in the product spec), and the deferred-items list of the Stage 0 close-out. A team cannot be assigned work from prose. The approvals were also recorded only in conversation and in PR comments, not in the SRS.

## What Changed

| File or place | Description |
|---|---|
| PRs #18 and #19 | An approval comment on each, quoting the owner; merged with merge commits, as #17 was. |
| PR #20 | The product specification, draft 0.1, opened for review. It was **not** among the approvals: it was never a PR before. |
| `docs/SRS.md` | Decisions D42 to D45 and a header change row. |
| `docs/ROADMAP.md` | Status set to approved (D42); today's three plan changes in Phase 3; steps 1.2 to 1.4 updated; the decisions table and next actions point to the issue tracker. |
| `docs/ARCHITECTURE.md` | Status set to the working architecture (D44); new owner decision AD-13 (round length and update-size budget); issue numbers added to the AD table. |
| `docs/implementations/2026-10-14-solo-prototypes.md`, `2026-10-14-architecture-draft.md` | Status rows updated to the approvals. |
| `CONTRIBUTING.md` | New. The team workflow: from issue to branch to plan document to PR to review to merge. Also the project's conventions, the meaning of labels and milestones, and how decisions are recorded. |
| `.github/ISSUE_TEMPLATE/` | New. Forms for a task or feature, a bug, an owner decision, and a research question or experiment. |
| `.github/pull_request_template.md` | New. A checklist: linked issue, implementation document, tests, results stated honestly, house style. |
| `docs/planning/2026-10-14-backlog.toml` | New. The seed backlog as data: labels, milestones and every issue (title, labels, milestone, assignee, body, blockers). |
| `scripts/ops/seed_backlog.py` | New. Creates the labels, milestones and issues from the TOML file through the `gh` command. Idempotent, paced and verified. |
| `docs/planning/2026-10-14-backlog-issues.md` | New, generated. The created issues: key, number, title and milestone. |
| `docs/implementations/2026-10-14-team-workflow-and-backlog.md` | This document. |
| GitHub (outside git) | Labels, 8 milestones and the seed issues in `mertefesensoy/CASSANDRA-Chorus`. |

## Implementation Approach

**Approvals.** The owner's words are quoted in the PR comments and recorded as SRS decisions:

| Decision | Content |
|---|---|
| D42 | The roadmap is approved, with three changes from today's findings: a second machine before Gate N1a; update size as a Phase 3 design constraint; commit attempts budgeted by the client. |
| D43 | The prototype results are accepted: P3 reduced and run tonight, P5 deferred, P8 done. |
| D44 | Architecture draft 0.1 is the **working architecture** and the basis for Phase 3 planning. This supersedes D41's deferral. AD-1 to AD-13 stay open as tracked decisions, and the sections marked "Waits on" can still change with P3 and P5. |
| D45 | The team workflow: all work is tracked as GitHub issues. |

The product specification stays under review (PR #20), with a review ticket assigned to the owner.

**Backlog as data, created by a script.** The backlog is a TOML file so that it can be reviewed in a PR, and so the issues can be recreated or extended. TOML is read by Python's standard `tomllib`, so no new dependency is needed. The script, `scripts/ops/seed_backlog.py`:
1. Creates or updates the labels; creates missing milestones by title.
2. Lists existing issues (all states) and skips any whose title already exists, so it resumes after an interruption and never duplicates.
3. Creates the issues **in file order**. Each body may refer to an earlier issue as `{#key}` and to a file on `main` as `{blob}path`. The first is replaced by that issue's number, the second by a full GitHub URL (relative paths do not resolve in issues).
4. Waits 1.5 s between creations. GitHub allows 80 content-creating requests per minute and 500 per hour (system study, Q5), and this morning's Hub rate limit is the reason for caution.
5. Checks at the end that every planned title exists exactly once, and writes the key-to-number table.
6. With `--dry-run`, prints the plan and changes nothing.

**Shape of the backlog:**
- One issue per assignable unit of work.
- Every issue has context links, the task, acceptance criteria as checkboxes, what it does not cover, and its blockers.
- **Owner decisions** are issues of their own (type `decision`), assigned to the owner, under the milestone of the step that needs them. Work items name them as blockers instead of restating them.
- **Owner-only actions** carry `status: needs owner` and are assigned to the owner: the laptop runs, recruiting a second machine, messages sent in the owner's name.

**Labels:**

| Kind | Labels |
|---|---|
| Type | feature, bug, task, decision, research, experiment, docs, epic |
| Area | protocol, client, merge, storage, security, data, tokenizer, model, training, sandbox, inference, ops, process |
| Priority | high, medium, low |
| Status | blocked, needs owner, deferred |

GitHub's default labels are kept. Only `good first issue` and `help wanted` are used by the backlog.

**Milestones:**
- one per remaining roadmap phase (1 to 6);
- "Research track";
- "Housekeeping".

**Not in the public tracker:** the reference laptop's charger and battery service, a personal hardware matter. It is listed for the owner in conversation instead.

## Mathematical / Statistical Details

None. This is a process and documentation change. The only numbers are pacing:
- 1.5 s between issue creations gives at most 40 per minute, half of GitHub's 80;
- about 90 issues stay under the 500 per hour limit.

## Design Decisions

- **Recording only what was approved.** "All of the PRs" was said when #18 and #19 were the open PRs, so the product specification gets its own PR and a review ticket. If the owner meant to include it, one word changes that.
- **D44's wording.** Approving the architecture PR makes draft 0.1 the working basis, not a frozen design. The draft itself labels open decisions and prototype dependencies, so the approval keeps them open.
- **The workflow PR is not merged by Claude.** It contains new process content (templates, CONTRIBUTING) that the owner has not seen, and a team lead merging PRs is the habit to establish. The issues go live immediately, because GitHub issues do not depend on a merge.
- **No GitHub Project board yet.** The `gh` token has the `repo`, `workflow`, `read:org` and `gist` scopes, not `project`. The owner can grant it with `gh auth refresh -s project`, and a board can then be added without changing the issues.
- **Prefixed labels** (`type:`, `area:`, `priority:`, `status:`) instead of GitHub's defaults, so that a team can filter on one dimension at a time.
- **A TOML seed file, not hand-made issues.** The seed is reviewable, re-runnable and diffable. After seeding, **the issues are the source of truth**; the TOML file records what was planned on 2026-10-14.

## Verification

**Offline.** `python -m pytest tests/test_seed_backlog.py` passed, 9 tests. They cover:
- the real backlog file validates;
- placeholder rendering and assignees;
- seven kinds of invalid file rejected, including a forward reference.

**Dry run.** `python scripts/ops/seed_backlog.py docs/planning/2026-10-14-backlog.toml --dry-run` planned 89 issues:

| Milestone | Issues |
|---|---|
| Phase 1 | 10 |
| Phase 2 | 10 |
| Phase 3 | 33 |
| Phase 4 | 10 |
| Phase 5 | 11 |
| Phase 6 | 4 |
| Research track | 4 |
| Housekeeping and process | 7 |

Two bodies were rendered and read before sending (#64 and #45 in the end).

**Real run, 2026-10-14:**
- 27 labels created; 8 milestones created (numbers 1 to 8); 89 issues created, **#21 to #109**, at 1.5 s apart.
- The final check first reported the last two issues missing, although the run had printed both as created. A direct listing seconds later showed them. GitHub's issue listing lags new issues by a few seconds, so the check now retries up to 4 times, 10 s apart.
- A re-run then skipped all 89 (idempotence), confirmed **every planned title exists exactly once**, and wrote `docs/planning/2026-10-14-backlog-issues.md`.

**Spot checks with `gh issue view`:**
- #64: its labels, milestone and blocker numbers (#61, #63, #33) were right, and its links were full `blob/main` URLs.
- #38: assigned to the owner, with the decision labels.

**Approvals:**
- PRs #18 and #19 carry the approval comments and were merged with merge commits (`594e9d1`, `2fbbecd`).
- PR #20 (product specification) is open for review.

**Not covered:**
- How the issue forms render on GitHub. They take effect only once this PR is merged to the default branch.
- No project board, for lack of the `project` token scope (issue #51).

## Related Docs

- `docs/ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/SRS.md` section 9.
- `docs/stage0-closeout.md` section 5 (deferred items).
- `docs/implementations/2026-10-14-solo-prototypes.md`.
