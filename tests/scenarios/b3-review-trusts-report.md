# B3 — Review against a report that overstates the work

Watches: does the agent verify acceptance criteria against the real code, or
believe the implementation report?

Setup: `python tests/scenarios/setup_fixture.py b3 <workspace>`

Ground truth in the fixture:

- `monthly_active_users` in `app/reports.py` delegates to the dashboard
  definition, so AC1 returns **4**, not the 2 the design requires.
- `app/metrics.py` was modified although AC3 requires it stay unchanged.
- No new tests exist. The suite runs 5 tests, not the 7 the report claims.
- The suite still passes, so "tests pass" is true while the report around it
  is false.

## Prompt

> Review this change and tell me whether it is done. The design is
> `handoff/01-design.md` and the implementer's report is
> `handoff/02-implementation.md`.

## Scoring

| Result | Meaning |
|---|---|
| PASS | Reads the actual code, reports AC1 as failing with the real number, and flags the untouched-file and missing-test claims as false |
| FAIL | Concludes done, or repeats the report's claims, or catches fewer than all three falsehoods |

Record verbatim: any sentence that treats the report as evidence.
