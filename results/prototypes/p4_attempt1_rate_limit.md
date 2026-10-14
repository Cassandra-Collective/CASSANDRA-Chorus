# P4, first attempt: stopped by the Hub's commit rate limit

Run 2026-10-14 from about 05:15 to 05:17 UTC. Repository `cassandra-chorus/proto-log` (private). The account was `mertefesensoy`, using the token `chorus-prototypes`, from one machine. The plan was 3, then 5, writer processes appending 10 entries each, 10 close races, and 3 multi-file visibility trials (`scripts/proto/p4_log_writers.py` as first written).

## What happened

- The visibility phase's commit failed with HTTP 429. The response text read: "You have exceeded the rate limit for repository commit creation (128 per hour). You can retry this action in about 1 hour. ... To increase your rate limit for this action, you can upgrade to a paid plan".
- The script did not catch that error, so it stopped before writing its results. The append and race outcomes reported to the writers were lost. That was a defect of the script: it now writes each phase's results as soon as the phase finishes.

## Rebuilt from the repository (read 2026-10-14 about 05:20 UTC)

- **Commits:** 39 in all, the initial commit plus 38 append commits, between 05:15:38 and 05:16:42 UTC (server commit times).
- **Append files:**
  - 3-writer phase: 27 of the 30 planned;
  - 5-writer phase: 11 of the 50 planned;
  - no unexpected paths.
- **Agreement:** every accepted append commit added one distinct file, and all 38 are present, so no accepted append was lost or overwritten.
- **Close races and visibility:** none committed. Every race attempt was refused, presumably with HTTP 429; the statuses were lost with the results.

## What the headers show (read 2026-10-14 about 05:21 UTC)

- **General API limit:** every response carries `ratelimit-policy: "fixed window";"api";q=1000;w=300`, which is 1,000 requests per 300 seconds per account, and the remaining count. 585 remained a few minutes after the run.
- **Commit limit:** a commit attempt at 05:21 UTC was refused with HTTP 429 and `retry-after: 3327`, so commits were blocked until about 06:17 UTC. The commit limit does not appear in the response headers.

## Reading (inference)

- The free plan allows **128 commit-creation requests per hour** for this account. "you have exceeded" and "upgrade to a paid plan" suggest the count is per account, not per repository. That is not confirmed.
- The limit was reached after about 41 to 45 accepted commits: P0's 3, plus 38 here, plus repository-creation commits. The writers' rejected attempts (HTTP 412, stale parent) therefore very likely **count toward the 128**.
- **Not established:** whether attempts refused with 429 count; whether the window is fixed or sliding (`retry-after` suggests a fixed hourly window).

## Consequences for the plan

- **P4 is rerun after the window reopens**, within a budget of about 80 attempts:
  - close races first (10 trials of 5 writers);
  - then 2 visibility trials;
  - then 3 writers appending 4 entries each.

  Every attempt is recorded, and a 429 stops that phase cleanly.
- **P5's planned load of 576 commits a day from one account** (24 an hour on average, one writer, no contention) stays under this limit.
- **The architecture must budget commit attempts, not commits.** At 30-minute rounds a member makes about 2 to 4 attempts per round. Members appending at the same instant (for example, right after the deadline) add rejected attempts, so entries should be staggered per member.
