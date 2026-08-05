import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.metrics import daily_active_users, events_per_user, weekly_active_users
from app.reports import monthly_finance_summary, weekly_finance_summary
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


if __name__ == "__main__":
    unittest.main()
