# Implementation: Monthly active users in the finance report

## Design and round reference

Design: `01-design.md`
Round: 1
Implementer: agent-b, opened fresh with no access to the design conversation

## Task completion table

| # | Task | Outcome |
|---|---|---|
| 1 | Add `monthly_active_users` on top of `_purchasers` | done |
| 2 | Test a month with views but no purchase | not done — blocked, see D1 |
| 3 | Test an empty month | done |

## Actual file changes

| Path | What changed |
|---|---|
| `app/reports.py` | Added `monthly_active_users(store, month)` as `len(_purchasers(store.for_month(month)))`, above `monthly_finance_summary`. Nothing else touched |
| `tests/test_metrics.py` | Imported `monthly_active_users`; added `test_monthly_active_users_empty_month` |

## Deviations and reasons

**D1 — AC1 does not match the project. Blocking, not repaired.**

AC1 says the call returns 2 "on the fixture data", because "u1 and u4
purchased". There are two fixtures and they disagree:

- `data/events.json` contains a u4 purchase in `2026-01` and gives **2**. No
  unit test loads this file.
- The `EVENTS` list in `tests/test_metrics.py`, which every existing test uses,
  contains no u4 at all and gives **1**.

Every way of making AC1 pass is a decision this design did not authorize:

- Adding u4 to `EVENTS` changes the existing assertion
  `test_monthly_finance_summary(...)["active_users"] == 1` to 2. That assertion
  is a claim about a number reconciled against the finance ledger.
- Pointing the new test at `data/events.json` pulls a file the design did not
  put in scope into the unit tests.
- Asserting 1 contradicts the number AC1 states and the reasoning it gives.

Task 2's test is exactly the disputed `2026-01` case, so it is unwritten rather
than guessed at.

**Question for the design author:** which fixture did AC1 mean? If it is
`EVENTS`, its expected value is 1 and not 2, and the AC needs restating rather
than the fixture editing.

**D2 — settled without asking.** Function placed above `monthly_finance_summary`;
the design gave no ordering. The `app.reports` import in the test module became
a parenthesised multi-line form to fit the added name. Neither changes any
existing behaviour, assertion, or the files-in-scope list.

## Verification commands and observed results

| Command | Observed result |
|---|---|
| `python -m unittest discover -s tests -q` | `Ran 6 tests in 0.000s` / `OK` |
| `python -c "...monthly_active_users(store, '2026-01')..."` on both fixtures | `EVENTS -> 1`, `data/events.json -> 2` |
| `sha256sum app/metrics.py` before and after | identical, `248e3110d8bac296...` (AC3) |

## Unverified items and reasons

AC1 — unverified, because which fixture it refers to is undecided. The
function's arithmetic is almost certainly right; the disagreement is about
which data it should be asserted against.

## Remaining risks

Whoever answers D1 should note that the two fixtures will keep disagreeing
after this change. If the suite is ever pointed at `data/events.json`, several
existing expected values move.

---

**Note for readers of this example.** `change.yaml` stays at `implementing`
here, not `ready_for_review`: one task is unfinished and one criterion is
unmet. A report that says "blocked" while the state says "ready for review"
tells the next agent the work is done.
