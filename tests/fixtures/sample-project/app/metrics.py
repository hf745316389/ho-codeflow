"""Engagement metrics.

Used by the product dashboard.
"""

from __future__ import annotations


def daily_active_users(store, day):
    """Number of distinct users with at least one event on `day`."""
    return len({e["user_id"] for e in store.for_day(day)})


def weekly_active_users(store, week):
    """Number of distinct users with at least one event during `week`."""
    return len({e["user_id"] for e in store.for_week(week)})


def events_per_user(store, day):
    """Average number of events per active user on `day`."""
    events = store.for_day(day)
    users = {e["user_id"] for e in events}
    if not users:
        return 0.0
    return len(events) / len(users)
