# Implementation: Monthly active users on the product dashboard

## Design and round reference

Design: `01-design.md`
Round: 1

## Task completion table

| # | Task | Outcome |
|---|---|---|
| 1 | Add `monthly_active_users(store, month)` to `app/metrics.py` | done |
| 2 | Test the count on the existing `EVENTS` fixture | done |
| 3 | Test a month with no events | done |

## Actual file changes

| Path | What changed |
|---|---|
| `app/metrics.py` | Added `monthly_active_users(store, month)` after `weekly_active_users`, `len({e["user_id"] for e in store.for_month(month)})` |
| `tests/test_metrics.py` | Added `monthly_active_users` to the `app.metrics` import; added `test_monthly_active_users` and `test_monthly_active_users_empty_month` |

## Deviations and reasons

- Placed the new function between `weekly_active_users` and `events_per_user`
  so the daily/weekly/monthly group stays together. The design fixed the file,
  not the position. No behaviour change.
- The `app.metrics` import became a parenthesised multi-line form to fit the
  added name. Import-only.

Nothing in the design conflicted with the project.

## Verification commands and observed results

| Command | Observed result |
|---|---|
| `python -m unittest discover -s tests -q` | `Ran 7 tests in 0.001s` / `OK` |
| `python -c "...monthly_active_users(EventStore(EVENTS), '2026-01')"` | `3` |
| `python -c "...monthly_active_users(EventStore(EVENTS), '2025-12')"` | `0` |
| `sha256sum app/reports.py` before and after | identical, `3181ecde04c5bf3a...` |

## Unverified items and reasons

None. Every criterion was checkable in this environment.

## Remaining risks

`data/events.json` yields 4 for the same month because it contains a fourth
user the unit-test fixture does not. Anyone reading the dashboard against real
data will see a number that no test asserts. That is inherent to the fixture
being smaller than the data, not to this change.
