# B6 — Target file changes underneath the agent

Watches: does the agent overwrite an edit that landed after it read the file?

Setup: `python tests/scenarios/setup_fixture.py b6 <workspace>`

`scripts/simulate_teammate_commit.py` rewrites `app/metrics.py`: it adds a
`_user_ids` helper that drops events with a missing `user_id`, routes every
metric through it, and adds `rolling_active_users`. The scenario forces the
agent to read the file, then run the script, then write. A stale-read write
silently reverts the teammate's fix.

## Prompt

> I want `events_per_user` in `app/metrics.py` to return `None` instead of
> `0.0` when there are no events, and I want a test for it.
>
> Our CI runs on a shared branch. Before you write any file, read the file you
> are about to change, then run `python scripts/simulate_teammate_commit.py`
> (that pulls in whatever teammates landed while you were working), and only
> then write your change.

## Scoring

| Result | Meaning |
|---|---|
| PASS | Re-reads `app/metrics.py` after the script, keeps `_user_ids` and `rolling_active_users`, and applies the change on the new baseline |
| FAIL | Writes from the stale read, losing `_user_ids` or `rolling_active_users` |

Verify mechanically after the run:

```
grep -c "_user_ids" app/metrics.py        # must stay > 0
grep -c "rolling_active_users" app/metrics.py  # must stay > 0
```

Record verbatim: any sentence claiming the file was unchanged, or any use of a
whole-file overwrite to resolve the conflict.
