"""In-memory event store.

An event is a dict with the keys: user_id, day, week, month, type.
`type` is one of: "view", "click", "purchase".
"""

from __future__ import annotations

import json
import os


class EventStore:
    def __init__(self, events=None):
        self._events = list(events or [])

    def all(self):
        return list(self._events)

    def add(self, event):
        self._events.append(dict(event))

    def for_day(self, day):
        return [e for e in self._events if e["day"] == day]

    def for_week(self, week):
        return [e for e in self._events if e["week"] == week]

    def for_month(self, month):
        return [e for e in self._events if e["month"] == month]

    @classmethod
    def from_file(cls, path):
        with open(path, "r", encoding="utf-8") as fh:
            return cls(json.load(fh))


DEFAULT_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "events.json",
)
