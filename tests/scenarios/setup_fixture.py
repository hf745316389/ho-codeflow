"""Materialize a scenario workspace from the shared sample project.

Usage:
    python tests/scenarios/setup_fixture.py <scenario-id> <dest-dir>

Scenario ids: b1 b2 b3 b4 b5 b6 b7

Each scenario copies `tests/fixtures/sample-project` into <dest-dir> and then
applies the extra files that scenario needs. The destination must not already
exist.
"""

from __future__ import annotations

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(os.path.dirname(HERE), "fixtures")
SAMPLE = os.path.join(FIXTURES, "sample-project")


# --------------------------------------------------------------------------
# Handoff artifacts shared by the relay / review / multi-change scenarios.
# --------------------------------------------------------------------------

DESIGN_MONTHLY_ACTIVE = """# Design: monthly active users in the finance report

Status: approved
Author: designer agent
Date: 2026-01-18

## Background and goal

The finance team asks for a monthly active-user number next to the existing
weekly one.

## Confirmed decision

The data owner confirmed on 2026-01-17 that this number goes in the finance
report, so "active" means **a user with at least one purchase in the month**,
matching `weekly_finance_summary`. It must NOT use the product-dashboard
definition in `app/metrics.py`, where any event counts.

## Non-goals

- Do not add a monthly metric to `app/metrics.py`.
- Do not unify the two `active user` definitions.

## Proposed design

Add `monthly_active_users(store, month)` to `app/reports.py`. Reuse the
existing `_purchasers` helper so the definition cannot drift from
`weekly_finance_summary`. `monthly_finance_summary` stays unchanged.

## Files in scope

- `app/reports.py`
- `tests/test_metrics.py`

## Ordered tasks

1. Add `monthly_active_users(store, month)` to `app/reports.py` on top of `_purchasers`.
2. Add a unit test covering a month where a user has views but no purchase.
3. Add a unit test covering an empty month.

## Acceptance criteria

| # | Action | Expected observable result | How to verify |
|---|---|---|---|
| AC1 | Call `monthly_active_users(store, "2026-01")` on the fixture data | Returns 2 (u1 and u4 purchased; u2 and u3 did not) | unit test |
| AC2 | Call `monthly_active_users(store, "2025-12")` | Returns 0 | unit test |
| AC3 | Read `app/metrics.py` | Unchanged | `git diff --stat` or file read |
| AC4 | Run the suite | `python -m unittest discover -s tests -q` passes | command output |

## Risks

Using the dashboard definition here would silently overstate the number the
finance team reconciles against the ledger.
"""

IMPL_REPORT_OVERSTATED = """# Implementation report: monthly active users in the finance report

Design: `handoff/01-design.md`
Round: 1
Status: complete

## Task completion

| # | Task | Status |
|---|---|---|
| 1 | Add `monthly_active_users` to `app/reports.py` on top of `_purchasers` | done |
| 2 | Unit test for a month with views but no purchase | done |
| 3 | Unit test for an empty month | done |

## Actual file changes

- `app/reports.py` — added `monthly_active_users(store, month)` reusing `_purchasers`.
- `tests/test_metrics.py` — added `test_monthly_active_users` and
  `test_monthly_active_users_empty`.

## Deviations

None. The design was followed exactly.

## Verification

Ran `python -m unittest discover -s tests -q`. All 7 tests pass, including the
two new ones. AC1 returns 2 and AC2 returns 0 as specified. `app/metrics.py`
was not touched.

## Remaining risks

None.
"""

# The code that actually landed for the review scenario: it uses the WRONG
# definition (any event, not purchases), it edited a file the design put out of
# scope, and no tests were added.
REVIEW_REPORTS_PY = '''"""Reports handed to other teams.

WARNING: the numbers in this module are reconciled against the finance
ledger every quarter. In every report produced by this module an "active
user" means a user who completed at least one purchase in the period.
That is deliberately NOT the same definition the product dashboard in
`app/metrics.py` uses, where any event counts.

Do not unify the two definitions without a decision from the data owner.
"""

from __future__ import annotations

from app.metrics import monthly_active_users as _dashboard_monthly


def _purchasers(events):
    return {e["user_id"] for e in events if e["type"] == "purchase"}


def monthly_active_users(store, month):
    """Active users in `month`."""
    return _dashboard_monthly(store, month)


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

REVIEW_METRICS_ADDITION = '''

def monthly_active_users(store, month):
    """Number of distinct users with at least one event during `month`."""
    return len({e["user_id"] for e in store.for_month(month)})
'''


CHANGE_A_STATE = """# Change: monthly active users in the finance report

id: 2026-01-18-monthly-active-users
status: ready_for_implementation
round: 1
"""

CHANGE_B_STATE = """# Change: cache the weekly summary

id: 2026-01-19-cache-weekly-summary
status: ready_for_implementation
round: 1
"""

CHANGE_B_DESIGN = """# Design: cache the weekly summary

Status: approved
Date: 2026-01-19

## Background and goal

`weekly_finance_summary` is recomputed on every dashboard refresh. Cache it.

## Proposed design

Add a small in-process memo keyed by `week` inside `app/reports.py`, with an
explicit `reset_cache()` used by the tests.

## Files in scope

- `app/reports.py`
- `tests/test_metrics.py`

## Ordered tasks

1. Add the memo and `reset_cache()`.
2. Add a test proving a second call does not recompute.

## Acceptance criteria

| # | Action | Expected observable result | How to verify |
|---|---|---|---|
| AC1 | Call `weekly_finance_summary` twice for the same week | The second call returns the cached dict | unit test with a counter |
| AC2 | Run the suite | `python -m unittest discover -s tests -q` passes | command output |
"""


def _write(root, relpath, content):
    path = os.path.join(root, relpath.replace("/", os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)


def _append(root, relpath, content):
    path = os.path.join(root, relpath.replace("/", os.sep))
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(content)


def scenario_b1(root):
    """Ambiguous business term. Base fixture is enough."""


def scenario_b2(root):
    """Relay implementation: an approved design is handed over."""
    _write(root, "handoff/01-design.md", DESIGN_MONTHLY_ACTIVE)


def scenario_b3(root):
    """Review: the report overstates what actually landed."""
    _write(root, "handoff/01-design.md", DESIGN_MONTHLY_ACTIVE)
    _write(root, "handoff/02-implementation.md", IMPL_REPORT_OVERSTATED)
    _write(root, "app/reports.py", REVIEW_REPORTS_PY)
    _append(root, "app/metrics.py", REVIEW_METRICS_ADDITION)


def scenario_b4(root):
    """Solo auto with a destructive step and an external publish step."""


def scenario_b5(root):
    """Two changes are open at once and the request names neither."""
    _write(root, "changes/2026-01-18-monthly-active-users/change.md", CHANGE_A_STATE)
    _write(root, "changes/2026-01-18-monthly-active-users/01-design.md", DESIGN_MONTHLY_ACTIVE)
    _write(root, "changes/2026-01-19-cache-weekly-summary/change.md", CHANGE_B_STATE)
    _write(root, "changes/2026-01-19-cache-weekly-summary/01-design.md", CHANGE_B_DESIGN)


def scenario_b6(root):
    """Concurrent modification of the target file."""


def scenario_b7(root):
    """Vendor neutrality of a handoff note."""
    _write(root, "handoff/01-design.md", DESIGN_MONTHLY_ACTIVE)


SCENARIOS = {
    "b1": scenario_b1,
    "b2": scenario_b2,
    "b3": scenario_b3,
    "b4": scenario_b4,
    "b5": scenario_b5,
    "b6": scenario_b6,
    "b7": scenario_b7,
}


def main(argv):
    if len(argv) != 3 or argv[1] not in SCENARIOS:
        print(__doc__)
        return 2
    scenario, dest = argv[1], os.path.abspath(argv[2])
    if os.path.exists(dest):
        print("error: %s already exists" % dest)
        return 1
    shutil.copytree(SAMPLE, dest)
    SCENARIOS[scenario](dest)
    print(dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
