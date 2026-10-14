# P4 concurrent log writers

Plan: `docs/implementations/2026-10-14-solo-prototypes.md`. Repository `cassandra-chorus/proto-log` (private), run `r2` started 2026-10-14T06:19:06Z. Writers are separate processes on one machine, one account and token. Known limits: free plan: 128 commit-creation requests per hour per account; API 1,000 requests per 300 s. Commit attempts by HTTP status: {'200': 22, '409': 48, '412': 6}; first 429 after attempt none.

## Close races (5 writers, same parent, same instant)

| Trial | Successes | Winner | File content | Statuses | Send spread (ms) | Pass |
|---|---|---|---|---|---|---|
| 0 | 1 | m0 | m0 | 200, 409, 409, 409, 412 | 946.6 | yes |
| 1 | 1 | m2 | m2 | 200, 409, 409, 409, 409 | 3.8 | yes |
| 2 | 1 | m4 | m4 | 200, 409, 409, 409, 409 | 1.3 | yes |
| 3 | 1 | m3 | m3 | 200, 409, 409, 409, 409 | 0.2 | yes |
| 4 | 1 | m2 | m2 | 200, 409, 409, 409, 409 | 0.1 | yes |
| 5 | 1 | m4 | m4 | 200, 409, 409, 409, 409 | 2.2 | yes |
| 6 | 1 | m1 | m1 | 200, 409, 409, 409, 409 | 4.7 | yes |
| 7 | 1 | m1 | m1 | 200, 409, 409, 409, 409 | 1.8 | yes |
| 8 | 1 | m4 | m4 | 200, 409, 409, 409, 409 | 1.7 | yes |
| 9 | 1 | m0 | m0 | 200, 409, 409, 409, 409 | 1.4 | yes |

## Multi-file visibility (50 files in one commit)

| Trial | Commit status | Listings | Counts seen | Partial seen | Full after commit returned (s) | Commit took (s) |
|---|---|---|---|---|---|---|
| 0 | 200 | 6 | [0, 50] | no | -0.22 | 1.1 |
| 1 | 200 | 6 | [0, 50] | no | -0.24 | 1.17 |

## Appends

3 writers, 4 entries each. Told: {'failed': 2, 'success': 10}. Attempts: 24 by status {'200': 10, '409': 9, '412': 5}. Missing after success: 0; present after failure: 0; unexpected: 0. Pass: **yes**.

Commits in the repository afterwards: 61. All checks passed: **yes**.
