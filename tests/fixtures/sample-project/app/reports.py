"""Reports handed to other teams.

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
