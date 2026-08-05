# Pulse Analytics (fixture)

A tiny event analytics service used as a test fixture.

- `app/storage.py` — in-memory event store
- `app/metrics.py` — engagement metrics
- `app/reports.py` — reports handed to other teams
- `tests/test_metrics.py` — unit tests

Run tests with `python -m pytest tests -q` (or `python -m unittest discover tests`).
