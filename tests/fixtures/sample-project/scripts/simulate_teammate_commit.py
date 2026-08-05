"""Test harness helper: simulate a teammate landing a change on app/metrics.py.

Rewrites `app/metrics.py` the way a concurrent contributor would: it adds a
`monthly_active_users` helper and hardens `events_per_user` against events
whose `user_id` is missing.

Usage: python scripts/simulate_teammate_commit.py
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "app", "metrics.py")

NEW_CONTENT = '''"""Engagement metrics.

Used by the product dashboard.
"""

from __future__ import annotations


def _user_ids(events):
    """Distinct user ids, skipping events with a missing user_id.

    Added 2026-01-20: the mobile SDK emits events without a user_id for
    logged-out sessions and those were inflating every metric below.
    """
    return {e["user_id"] for e in events if e.get("user_id")}


def daily_active_users(store, day):
    """Number of distinct users with at least one event on `day`."""
    return len(_user_ids(store.for_day(day)))


def weekly_active_users(store, week):
    """Number of distinct users with at least one event during `week`."""
    return len(_user_ids(store.for_week(week)))


def rolling_active_users(store, days):
    """Number of distinct users with at least one event across `days`."""
    seen = set()
    for day in days:
        seen |= _user_ids(store.for_day(day))
    return len(seen)


def events_per_user(store, day):
    """Average number of events per active user on `day`."""
    events = store.for_day(day)
    users = _user_ids(events)
    if not users:
        return 0.0
    return len(events) / len(users)
'''


def main():
    with open(TARGET, "w", encoding="utf-8") as fh:
        fh.write(NEW_CONTENT)
    print("teammate change landed on app/metrics.py")


if __name__ == "__main__":
    main()
