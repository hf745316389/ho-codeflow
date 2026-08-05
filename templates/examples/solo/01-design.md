# Design: Monthly active users on the product dashboard

Change: `2026-08-05-monthly-active-users`
Round: 1

## Background and goal

The user asked for "a monthly active users number in our reporting, so I can
see it per month".

## Confirmed decisions

- 2026-08-05, in answer to Q1 below: the product-dashboard definition. Any
  event counts. The number belongs next to the daily and weekly metrics.

## Open questions

none — Q1 was raised and answered before implementation started. It is kept
here for the record:

> **Q1 (blocking).** Which "active user" does the monthly number count?
>
> This project keeps two definitions on purpose:
>
> - `app/metrics.py` — the product dashboard. Any event counts. On
>   `data/events.json` for `2026-01` this gives **4**.
> - `app/reports.py` — the finance report. At least one purchase. Same data,
>   same month: **2**. `app/reports.py` says in its own header not to unify the
>   two without the data owner.
>
> There is a third possibility: `monthly_finance_summary` already returns a
> per-month `active_users` under the purchase definition, so if that is the
> number wanted, this may be a labelling job and not a new metric.

## Non-goals

- Not adding a monthly figure to `app/reports.py`.
- Not unifying the two definitions.
- Not changing `monthly_finance_summary`.

## Current state with evidence

- `app/metrics.py` has `daily_active_users` and `weekly_active_users`, both
  counting distinct `user_id` over all event types. There is no monthly
  sibling.
- `app/storage.py` already has `EventStore.for_month`, so no storage change is
  needed.
- `tests/test_metrics.py` builds its store from a module-level `EVENTS` list of
  four rows: u1 (view, purchase), u2 (view), u3 (click). Three distinct users
  in `2026-01`.

## Proposed design and trade-offs

Add `monthly_active_users(store, month)` to `app/metrics.py`, one line, same
shape as `weekly_active_users`.

Rejected: a `definition="any"|"purchase"` parameter. It would make the
ambiguity permanent in the API and let each caller pick a meaning at random.

## Files in scope

- `app/metrics.py`
- `tests/test_metrics.py`

## Ordered tasks

1. Add `monthly_active_users(store, month)` to `app/metrics.py`.
2. Add a test asserting the count on the existing `EVENTS` fixture.
3. Add a test for a month with no events.

## Acceptance criteria

| # | Action | Expected observable result | How to verify |
|---|---|---|---|
| AC1 | `monthly_active_users(EventStore(EVENTS), "2026-01")` | Returns 3 (u1, u2, u3) | unit test |
| AC2 | `monthly_active_users(EventStore(EVENTS), "2025-12")` | Returns 0 | unit test |
| AC3 | Read `app/reports.py` | Unchanged | file read |
| AC4 | Run the suite | `python -m unittest discover -s tests -q` passes | command output |

AC1 asserts 3, not 4: 4 is the count on `data/events.json`, which no unit test
loads. Checked against the actual `EVENTS` list before writing this row.

## Risks and approval boundaries

Low. The change is additive and the two definitions stay apart. Nothing here
deletes data, writes outside the project, or touches production.
