# Contributing

Thanks for looking. Ho CodeFlow is small on purpose, so the bar for adding to
it is deliberately high.

## The one rule that is not negotiable

**No rule goes into a skill without a recorded baseline failure.**

Before you add a constraint, a prohibition, or a required section, run the
scenario against a fresh-context agent that does not have the skill, five
independent samples, and record what it actually did. If the agent already
does the right thing without the rule, the rule does not go in — it would be
regulating a problem that is not there, and it costs every future reader
context for nothing.

This is not a formality. Of the seven failures the original design predicted,
three did not reproduce. See `tests/baseline/results.md`.

## Adding or changing a rule

1. Write the scenario in `tests/scenarios/` with an explicit scoring table:
   what counts as pass, what counts as fail.
2. Add whatever fixture it needs to `tests/scenarios/setup_fixture.py`.
3. Run five fresh-context samples **without** your change. Record verbatim
   what the agents did and how they justified it.
4. If the control did not fail, stop. Open an issue with the results instead
   of a pull request with a rule.
5. If it did fail, write the smallest guidance that addresses the specific
   rationalizations you recorded, then re-run the same five samples.
6. Put both runs in `tests/baseline/results.md`.

## Match the form to the failure

- The agent knows the rule and skips it under pressure → a prohibition, plus
  the rationalizations you actually observed, quoted.
- The agent complies but the output has the wrong shape → a positive contract
  saying what the output is, in order. Not a list of things not to do.
- The agent omits an element from something it already produces → make it a
  required slot in the template, not a reminder in prose.

## Vendor neutrality

Skill bodies name no AI coding product, no product-specific command, and no
product-specific config file. README and installation docs may name products
as examples of hosts. `scripts/validate.py` checks this.

## Before you open a pull request

```
python scripts/validate.py
```

It must pass on Windows and on at least one Unix-like environment. Both
READMEs have to stay in step: protocol states, config fields, and command
examples appear in `README.md` and `README.zh-CN.md`, and a change to one
without the other is a bug.

## Scope

Out of scope for this project, by design: calling model APIs, choosing which
agent to use, syncing files between machines, creating branches or commits or
pull requests on your behalf, and replacing your project's own coding
standards. See "Non-goals" in the README.
