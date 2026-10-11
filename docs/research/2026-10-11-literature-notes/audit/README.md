# Audit trail for the Stage 0 literature report

These files record how `../../2026-10-11-stage0-literature-report.md` was checked against the papers it cites, on 2026-10-11. They are kept so that anyone can see what was checked, what was wrong, and what was changed.

## The two rules audited

1. **Every number taken from a paper comes from a part of that paper that was actually read.** For each number, an auditor:
   - searched the paper's raw text (arXiv PDF converted with `pdftotext -layout`, or arXiv HTML) for it;
   - confirmed the stated location (table, figure caption or section);
   - confirmed that location lies inside the sections the research notes record as read;
   - recomputed derived numbers and checked they carry an "(inference)" label.
2. **Anything that could not be verified appears only in section 7 ("Unverified leads").** An auditor compiled every unverified item from the notes and searched sections 1 to 6 for it.

## Order of work and files

Line numbers inside each file refer to the report **as it stood when that audit ran**, not to the final report.

| Stage | File | Scope | Report version audited |
|---|---|---|---|
| First audit | `audit-1-summary-readinglist.md` | header, section 1, section 2 (18 entries) | after the summary was cut to one page |
| First audit | `audit-2a-s3intro-q1.md` | section 3 opening and 3.1 | same |
| First audit | `audit-2b-q2-q3.md` | sections 3.2 and 3.3 | same |
| First audit | `audit3-parts/part-a.md` | sections 3.4, 3.5 and the section 5 table | same |
| First audit | `audit3-parts/part-b.md` | section 3.6 | same |
| First audit | `audit3-parts/part-c.md` | section 4, rows A1 to B4 | same |
| First audit | `audit-3d-remedies-B5-D1-and-gaps.md` | section 4, rows B5 to D1, and section 6 | same |
| First audit | `audit-4-unverified.md` | rule 2 over sections 1 to 6 | same |
| First audit | `audit3-parts/manifest.md` | map of paper names to arXiv IDs, versions and read status | n/a |
| Fixes | `fix-log.md` | one row per problem from the first audit (71), with the change made | n/a |
| Re-audit | `reaudit-A1.md`, `reaudit-A2.md` | the 104 lines in sections 1 to 6 changed by the fixes, both rules | after the 71 fixes |
| Re-audit | `reaudit-B-unverified.md` | rule 2 again over sections 1 to 6, by an auditor who did not see `audit-4` | after the 71 fixes |

The re-audits raised a final handful of problems (wrong section references, one rounding slip, one figure that came from an auditor's reading rather than the notes, and items missing from section 7). These were fixed directly in the report; they are listed in the implementation doc `docs/implementations/2026-10-11-stage0-literature-investigation.md`.

## Paths that no longer exist

The audits refer to a temporary session folder (`scratchpad/papers/...`, `scratchpad/audit/...`). It held the downloaded paper text and is not kept. To repeat a check, download the paper by its arXiv ID and the version the notes record (`https://arxiv.org/pdf/<ID>v<N>`) and convert it with `pdftotext -layout`.

## The holder-count simulation

The report's header states how many workers hold each expert in a round under the `coverage` policy. The coordinator derived it by re-implementing `_coverage()` from `cassandra_chorus/coordinator/assignment.py` and drawing 100,000 assignments (4 workers, 4 of 8 experts each):

```python
import collections
import random

def coverage(caps, n_experts, rng):
    held = [set() for _ in caps]
    experts = list(range(n_experts))
    rng.shuffle(experts)
    turn = 0
    for e in experts:  # deal every expert once, in turn, skipping full workers
        while len(held[turn % len(caps)]) >= caps[turn % len(caps)]:
            turn += 1
        held[turn % len(caps)].add(e)
        turn += 1
    for i, c in enumerate(caps):  # fill remaining capacity with experts not yet held
        free = [e for e in range(n_experts) if e not in held[i]]
        held[i].update(rng.sample(free, c - len(held[i])))
    return held

cnt = collections.Counter()
rng = random.Random(0)
for _ in range(100000):
    held = coverage([4, 4, 4, 4], 8, rng)
    for e in range(8):
        cnt[sum(e in h for h in held)] += 1
tot = sum(cnt.values())
print({k: round(v / tot, 4) for k, v in sorted(cnt.items())})
# {1: 0.2961, 2: 0.4448, 3: 0.2221, 4: 0.037}
```

## Mechanical checks on the final report

A script queried the arXiv API for every arXiv ID in the report and compared the returned title with the report's text, requested every link, and checked the section headings, the reading-list count and novelty language. Final run: 157 arXiv IDs, all resolved; 150 links, all returned 200; 8 headings; 18 reading-list entries; no novelty claim.
