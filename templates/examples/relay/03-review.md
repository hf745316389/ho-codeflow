# Review: Monthly active users in the finance report

## Review kind

`independent`. agent-c did not design or implement this change and opened it
with no prior context. The design's risk section concerns a ledger-reconciled
number, and the project config asks for an independent reviewer on high-risk
changes, so this one is.

## Acceptance item results

| # | Criterion | Result |
|---|---|---|
| AC1 | Returns 2 on the fixture data | unverified |
| AC2 | Returns 0 for an empty month | pass |
| AC3 | `app/metrics.py` unchanged | pass |
| AC4 | Suite passes | pass |

## Evidence

| # | How you checked it | What you observed |
|---|---|---|
| AC1 | Called the function against both fixtures | `EVENTS -> 1`, `data/events.json -> 2`. I cannot record `pass` or `fail`: the criterion does not say which fixture it means, so there is nothing to check it against. This is `unverified` because the criterion is undecidable as written, not because the implementer skipped it |
| AC2 | Ran `test_monthly_active_users_empty_month` | `0`. Note this returns 0 under the purchase definition and under the dashboard definition alike, so it discriminates nothing about the definition |
| AC3 | SHA-256 of `app/metrics.py` against the value the implementer recorded before their first edit | Identical, `248e3110d8bac296...` |
| AC4 | `python -m unittest discover -s tests -q` | `Ran 6 tests` / `OK`. Green, but the suite contains no test of the disputed `2026-01` value, so a green run says nothing about AC1 |

I read `app/reports.py` directly: `monthly_active_users` is
`len(_purchasers(store.for_month(month)))`. It uses `_purchasers`, as the
confirmed decision requires. The implementation is right; the criterion is what
is broken.

## Deviation decisions

| Deviation | Accepted? | Why |
|---|---|---|
| D1 — AC1 conflicts with the project, left unrepaired and raised as a question | yes, and correctly handled | Each of the three available repairs changes something the design did not authorize. Stopping cost one question; the alternative would have moved a ledger-reconciled assertion silently |
| D2 — function placement and import formatting | yes | Neither changes existing behaviour, an assertion, or the scope list |

No undeclared deviations. The two files changed are the two the design put in
scope.

## Blocking fixes

1. **Restate AC1 against a named fixture.** It currently names a user that
   exists only in `data/events.json` while specifying "unit test" as the
   verification method, and the unit tests use `EVENTS`. Either say `EVENTS` and
   change the expected value to 1, or say `data/events.json` and add it to the
   files in scope. This is the design author's call, not the implementer's.
2. **Then write task 2's test**, against whichever fixture AC1 ends up naming.

## Non-blocking suggestions

- The two fixtures describing the same month with different contents will
  cause this again. Worth its own change; out of scope here.

## Final status

`rework`. One criterion is unverifiable as written and one design task is
consequently unfinished. The code that exists is correct and does not need to
be rewritten — round 2 should be a one-line AC correction plus one test.
