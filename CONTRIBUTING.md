# Contributing to CASSANDRA Chorus

This project is led by its owner, Mert Efe Şensoy, who plans the work, assigns it and takes the decisions marked as owner decisions. These rules applied to every step of Stage 0 and continue for the team. Their origin is SRS decision D45 (`docs/SRS.md`, section 9).

## 1. Where the work is

- **Everything is an issue.** Every task, feature, bug, research question, experiment and owner decision is a GitHub issue in this repository. If it is not an issue, it is not planned work: open one, using a template.
- **Milestones are the roadmap's phases.** They follow `docs/ROADMAP.md`, from "Phase 1: Decide and specify" to "Phase 6: Open pool", plus "Research track" and "Housekeeping and process".
- **The design lives in the documents:**
  - `docs/ROADMAP.md`: the phases and gates;
  - `docs/ARCHITECTURE.md`: the working architecture (D44);
  - `docs/SRS.md`: requirements and every decision, numbered D1, D2 and so on;
  - the product specification, `docs/assistant-spec.md` (PR #20 while under review).
- **The seed backlog** of 2026-10-14 is recorded in `docs/planning/`. After seeding, the issues are the source of truth.

## 2. Labels

| Kind | Labels | Meaning |
|---|---|---|
| Type | `type: feature`, `bug`, `task`, `decision`, `research`, `experiment`, `docs`, `epic` | What kind of work it is. An epic is split into issues when its phase starts |
| Area | `area: protocol`, `client`, `merge`, `storage`, `security`, `data`, `tokenizer`, `model`, `training`, `sandbox`, `inference`, `ops`, `process` | Which part of the system it touches |
| Priority | `priority: high`, `medium`, `low` | High means needed now or blocking other work |
| Status | `status: blocked`, `needs owner`, `deferred` | Blocked: the body says by which issues. Needs owner: only the owner can do or decide it. Deferred: postponed by the owner |

`good first issue` and `help wanted` are used as usual.

## 3. From issue to merged change

1. **Take an issue that is assigned to you,** or ask the owner for one. Comment when you start.
2. **Branch from `main`** as `<kind>/<issue number>-<slug>`. The kinds are `feat`, `fix`, `docs`, `exp`, `research` and `ops`; for example, `feat/57-round-log`.
3. **Plan first.** Any meaningful change starts with an implementation document, `docs/implementations/YYYY-MM-DD-<slug>.md`, copied from `docs/implementations/_TEMPLATE.md`. Write it **before** the code and commit it first. It has these sections:
   - Problem / Motivation;
   - What Changed (a table of every file);
   - Implementation Approach (with each function's contract);
   - Mathematical / Statistical Details;
   - Design Decisions;
   - Verification;
   - Related Docs.

   If the plan needs a choice the documents do not settle, ask in the issue. Do not guess.
4. **Implement with tests.** `python -m pytest` must pass. GPU tests are marked `gpu` and skip without a GPU.
5. **Complete the Verification section:** what you ran, on what hardware, and what it does not cover.
6. **Open a pull request** that says `Closes #<issue>`, fill in the template, and request a review.
7. **Merging** is done by the owner (later, by the maintainers; D40) after review. PRs are merged with a merge commit.

## 4. Decisions

- An issue labelled `type: decision` asks the owner to choose. It states:
  - the decision;
  - when it is needed;
  - the context and links;
  - the known options and the evidence.

  Anyone may add evidence in comments.
- The owner's comment is the decision. It is then recorded as the next SRS D-number, and the affected documents are updated, in a pull request that closes the issue.
- Code never settles a decision silently. A rule that is not in a document is not a rule.

## 5. Experiments and research

- **Gates and readings are written before the runs they judge** (roadmap principle 3). An experiment's plan document states its pre-registered reading.
- **Every result states its hardware, scale, dataset and seeds, and what was not tested.** Results go in `results/`, with an entry in `RESULTS.md`.
- **Research follows the literature report's rules:**
  - read primary sources (raw text where possible);
  - every number traceable to its source;
  - inference labelled as inference;
  - no novelty claims.
- **Long runs on a laptop** start in a visible window with the screen on (`scripts/ops/launch_visible.ps1`), with keep-awake held from launch.

## 6. Hosts, tokens and security

- **Never commit a token, key or password.** Hugging Face tokens are fine-grained and scoped to what a task needs. Load them from the local token store, never from code.
- **The Hugging Face Hub's free plan limits:**
  - 128 commit-creation requests per hour per account, and rejected conditional commits very likely count;
  - 1,000 API requests per 300 s.

  Never burst-test commits. Batch files into one commit. Test repositories are private and named `proto-*`.
- **Work units and updates are data, never code.** Read only safetensors and JSON from hosts. Never unpickle, import or execute a fetched file.
- **Data policy (D32):** no other models' outputs in any training data. Every data source's licence is recorded.

## 7. Environment

- **Python 3.13 and PyTorch 2.12 or later** (`pyproject.toml`). Code runs from the repository root without installation: `python -m pytest`, `python scripts/...`.
- **Keep run outputs and data outside the repository and outside synced folders** (OneDrive, Dropbox):
  - set `CHORUS_RUNS_DIR` for run outputs;
  - set `CHORUS_DATA_DIR` for corpora.

## 8. Writing style

- Plain, direct English.
- Explain why, not only what.
- State each function's contract: its inputs, outputs, side effects and invariants.
- **No em or en dashes** in documents or code comments; use commas, colons, parentheses or separate sentences.

## 9. Code of conduct

Everyone who takes part in this project, in issues, pull requests, reviews, comments or any other project space, follows the Cassandra Collective [code of conduct](https://github.com/Cassandra-Collective/.github/blob/main/CODE_OF_CONDUCT.md). It is an organisation default: it lives in the organisation's `.github` repository, and GitHub applies it to every repository that has no code of conduct of its own. This repository links to it instead of keeping a copy.

## 10. Reporting security problems

Section 6 is about handling tokens and fetched files safely. This section is about what to do when you find a security problem, for example a token or key exposed in the repository, or a way to make the code load or run something it should not.

- **Never report a security problem in a public issue, pull request, comment or discussion.** A public report tells everyone before there is a fix.
- **Report it privately** through GitHub's private vulnerability reporting: [open a private report](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/security/advisories/new), or use "Report a vulnerability" on the repository's Security tab. The report, and the work on a fix, stay private until an advisory is published.
- The organisation's [security policy](https://github.com/Cassandra-Collective/.github/blob/main/SECURITY.md) applies to this repository.

## 11. Getting help

- **Open questions and help:** ask in [Discussions Q&A](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/discussions/categories/q-a). Anyone can answer there, and the answer that settles a question can be marked as accepted.
- **A question that should be tracked as an issue,** for example one whose answer will need a change to the code or the documents: open an issue with the **Question** form on the new-issue page. It applies the `question` label.
- **A question about an existing issue** goes in that issue's comments.

The organisation's [support page](https://github.com/Cassandra-Collective/.github/blob/main/SUPPORT.md) explains what to expect.
