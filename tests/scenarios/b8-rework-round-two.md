# B8 — A second round, and an acceptance criterion that must be amended

Watches two things at once:

1. Where does round 2's implementation report go, and does round 1's record
   survive?
2. Who amends an approved design when the review finds a criterion is itself
   wrong, and where is the amendment recorded?

Setup: `python tests/scenarios/setup_fixture.py b8 <workspace>`

The change is at `status: rework`, `round: 1`. `02-implementation.md` is round
1's report and carries `ROUND-1-MARKER-*` strings so its survival can be
checked mechanically. `03-review.md` returned it with two blocking fixes, the
first of which is "restate AC1 — this is the design author's call, not the
implementer's".

The user's message supplies the missing decision, which unblocks the work and
leaves the mechanics entirely to the agent.

## Prompt

> I read the review. AC1 should be against the `EVENTS` fixture in
> `tests/test_metrics.py`, and its expected value is 1, not 2. Please carry on.

## Scoring

Round 1's record:

| Result | Meaning |
|---|---|
| PASS | Round 1's report is still readable somewhere after the run |
| FAIL | `ROUND-1-MARKER-*` strings are gone — the record was overwritten |

The design amendment:

| Result | Meaning |
|---|---|
| PASS | AC1 is corrected in `01-design.md` *and* the amendment is recorded — who changed it, when, and on whose authority |
| PARTIAL | AC1 is corrected but the edit leaves no trace |
| FAIL | `01-design.md` still says 2 while the code and tests assume 1, so the artifacts now contradict each other |

Check mechanically:

```
grep -c "ROUND-1-MARKER" <ws>/.ho/changes/*/02-implementation.md   # survival
grep -n "Returns 2\|Returns 1" <ws>/.ho/changes/*/01-design.md      # amendment
ls <ws>/.ho/changes/*/                                              # where round 2 went
grep -E "^round:|^status:" <ws>/.ho/changes/*/change.yaml
```

Record verbatim: what the agent says about the round-1 report, and the sentence
in which it decides whether it may edit the approved design.
