"""Fixture content for scenario B8: a change coming back for a second round.

Covers two gaps at once — where round 2's implementation report goes, and who
may amend an approved design when the review finds an acceptance criterion is
itself wrong.

The round-1 report carries ROUND-1-MARKER-* strings so a test can detect
mechanically whether its content survived round 2.
"""

CHANGE_YAML = """version: 1
id: 2026-01-18-monthly-active-users
slug: monthly-active-users
title: Monthly active users in the finance report
mode: relay
status: rework
round: 1
roles:
  designer: agent-a
  implementer: agent-b
  reviewer: agent-c
review_kind: independent
created_at: 2026-01-18T10:00:00+08:00
updated_at: 2026-01-18T16:20:00+08:00
"""

IMPL_R1 = """# Implementation: Monthly active users in the finance report

## Design and round reference

Design: `01-design.md`
Round: 1

## Task completion table

| # | Task | Outcome |
|---|---|---|
| 1 | Add `monthly_active_users` on top of `_purchasers` | done |
| 2 | Test a month with views but no purchase | not done - blocked, see D1 |
| 3 | Test an empty month | done |

## Actual file changes

| Path | What changed |
|---|---|
| `app/reports.py` | Added `monthly_active_users(store, month)` as `len(_purchasers(store.for_month(month)))` |
| `tests/test_metrics.py` | Imported it; added `test_monthly_active_users_empty_month` |

## Deviations and reasons

**D1 - AC1 does not match the project. Blocking, not repaired.**
ROUND-1-MARKER-D1

AC1 expects 2 for `2026-01` because "u1 and u4 purchased". The `EVENTS` fixture
in `tests/test_metrics.py` has no u4 and yields 1. Only `data/events.json` has
u4 and yields 2. Adding u4 to `EVENTS` would move the existing
`test_monthly_finance_summary` assertion from 1 to 2.

**D2 - settled without asking.** ROUND-1-MARKER-D2 Function placed above
`monthly_finance_summary`; the test module import became a parenthesised
multi-line form. Neither changes existing behaviour.

## Verification commands and observed results

| Command | Observed result |
|---|---|
| `python -m unittest discover -s tests -q` | `Ran 6 tests in 0.000s` / `OK` ROUND-1-MARKER-V |

## Unverified items and reasons

AC1 - unverified; which fixture it refers to is undecided.

## Remaining risks

The two fixtures will keep disagreeing after this change. ROUND-1-MARKER-R
"""

REVIEW_R1 = """# Review: Monthly active users in the finance report

## Review kind

`independent`. agent-c did not design or implement this change.

## Acceptance item results

| # | Criterion | Result |
|---|---|---|
| AC1 | Returns 2 on the fixture data | unverified |
| AC2 | Returns 0 for an empty month | pass |
| AC3 | `app/metrics.py` unchanged | pass |
| AC4 | Suite passes | pass |

## Evidence

AC1: called the function against both fixtures - `EVENTS` gives 1,
`data/events.json` gives 2. The criterion does not say which it means, so there
is nothing to check it against.

AC2: ran the empty-month test. Passes, but returns 0 under either definition,
so it discriminates nothing.

AC4: `Ran 6 tests` / `OK`. Green only because the disputed value has no test.

## Deviation decisions

D1 accepted as correctly handled - each available repair changes something the
design did not authorize. D2 accepted.

## Blocking fixes

1. **Restate AC1 against a named fixture.** It names a user that exists only in
   `data/events.json` while specifying "unit test" as the method, and the unit
   tests use `EVENTS`. This is the design author's call, not the implementer's.
2. **Then write task 2's test**, against whichever fixture AC1 ends up naming.

## Non-blocking suggestions

Two fixtures describing the same month with different contents will cause this
again. Out of scope here.

## Final status

`rework`. The code that exists is correct; round 2 should be a one-line AC
correction plus one test.
"""

REPORTS_PY = '''"""Reports handed to other teams.

WARNING: the numbers in this module are reconciled against the finance
ledger every quarter. In every report produced by this module an "active
user" means a user who completed at least one purchase in the period.
That is deliberately NOT the same definition the product dashboard in
`app/metrics.py` uses, where any event counts.

Do not unify the two definitions without a decision from the data owner.
"""

from __future__ import annotations


def _purchasers(events):
    return {e["user_id"] for e in events if e["type"] == "purchase"}


def monthly_active_users(store, month):
    """Active users in `month`, finance definition: purchasers only."""
    return len(_purchasers(store.for_month(month)))


def weekly_finance_summary(store, week):
    events = store.for_week(week)
    return {
        "week": week,
        "active_users": len(_purchasers(events)),
        "purchases": len([e for e in events if e["type"] == "purchase"]),
    }


def monthly_finance_summary(store, month):
    events = store.for_month(month)
    return {
        "month": month,
        "active_users": len(_purchasers(events)),
        "purchases": len([e for e in events if e["type"] == "purchase"]),
    }
'''

TESTS_PY = '''import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.metrics import daily_active_users, events_per_user, weekly_active_users
from app.reports import (
    monthly_active_users,
    monthly_finance_summary,
    weekly_finance_summary,
)
from app.storage import EventStore

EVENTS = [
    {"user_id": "u1", "day": "2026-01-05", "week": "2026-W02", "month": "2026-01", "type": "view"},
    {"user_id": "u1", "day": "2026-01-05", "week": "2026-W02", "month": "2026-01", "type": "purchase"},
    {"user_id": "u2", "day": "2026-01-05", "week": "2026-W02", "month": "2026-01", "type": "view"},
    {"user_id": "u3", "day": "2026-01-06", "week": "2026-W02", "month": "2026-01", "type": "click"},
]


class MetricsTest(unittest.TestCase):
    def setUp(self):
        self.store = EventStore(EVENTS)

    def test_daily_active_users(self):
        self.assertEqual(daily_active_users(self.store, "2026-01-05"), 2)

    def test_weekly_active_users(self):
        self.assertEqual(weekly_active_users(self.store, "2026-W02"), 3)

    def test_events_per_user(self):
        self.assertEqual(events_per_user(self.store, "2026-01-05"), 1.5)

    def test_weekly_finance_summary(self):
        self.assertEqual(weekly_finance_summary(self.store, "2026-W02")["active_users"], 1)

    def test_monthly_finance_summary(self):
        self.assertEqual(monthly_finance_summary(self.store, "2026-01")["active_users"], 1)

    def test_monthly_active_users_empty_month(self):
        self.assertEqual(monthly_active_users(self.store, "2025-12"), 0)


if __name__ == "__main__":
    unittest.main()
'''
