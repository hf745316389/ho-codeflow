# RED baseline

What agents do on these scenarios **without** Ho CodeFlow installed. Every rule
in a skill has to point at a failure recorded here. Where the baseline did not
fail, the skill does not get a rule — see `results.md`.

## How the runs were made

- One fresh-context agent per sample, five samples per scenario, each in its own
  copy of `tests/fixtures/sample-project` produced by
  `tests/scenarios/setup_fixture.py`.
- Each agent got a realistic user message and nothing else. No Ho CodeFlow
  concepts, no protocol, no artifact requirement beyond a closing report.
- Agents were told skills and slash commands were off limits, so the baseline
  measures a plain capable coding agent rather than one already under some
  other workflow harness.
- Agents were told the user had stepped away and no reply would arrive before
  the turn ended. This is the honest constraint of a single-turn run, but it is
  also a pressure: see the confounds section in `results.md`.
- Outcomes that could be checked mechanically were checked mechanically, not
  taken from the agent's own report.

## Reading the results

`pass` means the agent did the thing the scenario hoped for. `fail` means it
did the thing the scenario was watching for. A scenario where the control does
not fail is a finding, not a wasted run: it says the corresponding rule would
be regulating a problem that is not there.

## Re-running

```
python tests/scenarios/setup_fixture.py b1 /some/empty/dir
```

Then hand a fresh agent the prompt from `tests/scenarios/b1-*.md` pointed at
that directory, and score it with the table in the same file.
