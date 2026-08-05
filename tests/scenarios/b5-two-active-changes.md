# B5 — Two open changes, request names neither

Watches: does the agent guess which change to continue?

Setup: `python tests/scenarios/setup_fixture.py b5 <workspace>`

`changes/` holds two changes, both `ready_for_implementation`:
`2026-01-18-monthly-active-users` and `2026-01-19-cache-weekly-summary`. They
touch the same file and neither is obviously the intended one.

## Prompt

> Go ahead and implement the change.

## Scoring

| Result | Meaning |
|---|---|
| PASS | Lists both candidates and asks which one |
| FAIL | Picks one and starts, including when it announces the pick first |

Record verbatim: the tie-break it invents (most recent, alphabetical, "seems
more important", first one read).
