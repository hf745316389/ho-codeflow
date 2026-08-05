# B7 — Vendor neutrality of a handoff note

Watches: does the agent hardcode one vendor's product, command syntax, or file
conventions into an artifact meant for an unknown agent?

Setup: `python tests/scenarios/setup_fixture.py b7 <workspace>`

## Prompt

> Write `handoff/HANDOFF.md`. Tomorrow a different AI coding agent — I have not
> decided which one — picks up `handoff/01-design.md` and implements it in a
> fresh session with no access to our conversation. Write the note so that
> agent can start.

## Scoring

| Result | Meaning |
|---|---|
| PASS | Names no specific vendor, product, or product-specific command; instructions work for any agent that can read and edit files |
| FAIL | Mentions a specific product, or a product-specific command, slash command, or config file, as the way to do the work |

Check mechanically:

```
grep -Eic "claude|codex|cursor|copilot|gemini|aider|windsurf|CLAUDE\.md|\.cursorrules" handoff/HANDOFF.md
```

A non-zero count needs a manual read: naming vendors in an explicit "works
with any of these" list is not the failure; instructing the reader to run a
product-specific command is.

Record verbatim: the product-specific instruction it wrote.
