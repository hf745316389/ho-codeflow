# Review: Monthly active users on the product dashboard

## Review kind

`self`. The same agent designed, implemented and reviewed this change. It is
not an independent review and should not be read as one. The change is
additive, low-risk, and the design did not mark it as needing an independent
reviewer.

## Acceptance item results

| # | Criterion | Result |
|---|---|---|
| AC1 | Returns 3 on the `EVENTS` fixture | pass |
| AC2 | Returns 0 for an empty month | pass |
| AC3 | `app/reports.py` unchanged | pass |
| AC4 | Suite passes | pass |

## Evidence

| # | How you checked it | What you observed |
|---|---|---|
| AC1 | Ran the new test, then called the function directly against `EventStore(EVENTS)` | `3` both ways. This one discriminates: the purchase definition would give 1 here |
| AC2 | Called it for `2025-12` | `0`. Note this passes under either definition, so it confirms the empty-month path and nothing about the definition |
| AC3 | SHA-256 before the first edit and after the last | Identical. No git in this project, so the hash stands in for `git diff` |
| AC4 | `python -m unittest discover -s tests -q` | `Ran 7 tests` / `OK`. 5 pre-existing plus the 2 new ones |

## Deviation decisions

| Deviation | Accepted? | Why |
|---|---|---|
| Function placed between `weekly_active_users` and `events_per_user` | yes | Keeps the period-metric group together; no behaviour effect |
| Import reformatted to multi-line | yes | Import-only, no name removed or repointed |

No undeclared deviations found: the two files changed are exactly the two the
design put in scope.

## Blocking fixes

None.

## Non-blocking suggestions

- A test asserting that `app.metrics.monthly_active_users` and
  `app.reports.monthly_finance_summary(...)["active_users"]` disagree on data
  where a user has events but no purchase would pin the divergence the module
  docstring warns about. Not gating: the design's non-goals rule out touching
  `app/reports.py` in this change.

## Final status

`complete`. All four criteria pass with evidence, the two definitions remain
separate, and nothing outside the design's scope was touched.
