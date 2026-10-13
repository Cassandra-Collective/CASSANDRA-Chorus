# 2026-10-13 · Assistant product specification, draft 0.1

| | |
|---|---|
| PLAN step | Roadmap step 1.2 (`docs/ROADMAP.md`) |
| Branch | `docs/assistant-spec` |
| SRS requirements | D29 to D32, D37 |
| Status | Draft for the owner's review |

## Problem / Motivation

The roadmap's later phases depend on knowing what the assistant must do:

- the data pipeline (Phase 2);
- the pilot model's size (4.3);
- the sandbox and post-training (Phase 5).

D29 to D32 set the target in a sentence each; nothing specified the tasks, the tools, the sandbox, the data policy in practice, the safety rules or what the owner still has to decide.

## What Changed

| File | Description |
|---|---|
| `docs/assistant-spec.md` | New. The assistant's scope, the tool layer and a draft tool set, the sandbox (world generator, task generator with a reference solver, episode runner, checker, adversarial emails), the training pipeline, the data policy in practice, the tokenizer and model-size approach, safety and privacy rules, evaluation, and ten owner decisions (OD-1 to OD-10) with when each is needed. |
| `docs/implementations/2026-10-13-assistant-spec.md` | This document. |

## Implementation Approach

The spec turns the owner's decisions into the requirements that later phases need. Every choice the decisions do not settle is listed as an owner decision with the step that needs it, rather than defaulted. Written while the system study (step 1.1) runs, without new questions to the owner, at the owner's instruction of no further stops.

## Mathematical / Statistical Details

None: a specification. The model-size range in section 7 is stated as "to be calculated, not assumed".

## Design Decisions

- **The tool layer, not the model, enforces safety.** Confirmation before irreversible actions is checked in code, so a model that skips it cannot act. This keeps the guarantee independent of training quality.
- **One sandbox for SFT data, evaluation and RL rewards.** It is the only data source D32 allows for post-training. Its known weakness, the narrow language of templates, is stated, and an option within D32 (volunteer-written text) is offered as OD-5.
- **Turkish-specific requirements** (date expressions, agglutinative forms, registers) are written into the sandbox, so the benchmark measures both languages separately.
- **No claims about specific datasets or licences.** Those are step 2.1's findings, to be read from primary sources.

## Verification

- Checked against D29 to D32 and D37 for consistency (scope, data policy, local operation).
- No em or en dashes.
- No code changed.

**Not verified:** feasibility of the size range and of template-only SFT data; both are measured later (sections 4 and 7).

## Related Docs

`docs/ROADMAP.md` (steps 1.2, 2.1 to 2.3, 5.1 to 5.4), `docs/SRS.md` section 9.
