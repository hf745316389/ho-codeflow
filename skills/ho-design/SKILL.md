---
name: ho-design
description: Use when a change needs a written design before any code is written, when a request's scope or business meaning is not settled, or when the next phase will run in a different session or a different agent with no access to this conversation.
---

# Design

Produce one file someone else can implement from with no access to this
conversation. You do not write business code in this phase.

## Locate the change

Read the project's own rules first — `AGENTS.md`, `CLAUDE.md`, or whatever it
uses — then `.ho/protocol.md` and `.ho/config.yaml` if they exist. Change
artifacts live in `.ho/changes/<id>/`.

If more than one change is open and the request names none of them, list the
candidates and ask which. Do not pick one, and do not do all of them.

## Settle the facts yourself

File paths, function signatures, test commands, current behaviour: open the
files and read them. Never hand back a question you could have answered by
reading the project.

## Questions that block

**A question whose answer changes the direction of the work stops this phase.**
Write the design down to that point, put the question in `Open questions`, and
stop. One question at a time — the one that changes the most.

Reversibility is not a reason to answer it yourself.

| Rationalization | Why it fails |
|---|---|
| "It's additive and reversible, so I'll pick one and flag it" | Reversible describes the code. The question is about what the number *means*. A wrong meaning gets acted on before anyone reverts anything. |
| "No reply is possible in this run, so I have to decide" | Not being able to get an answer now is the reason to write the question down, not the reason to answer it. |
| "The other reading already exists elsewhere, so they obviously meant this one" | That is an inference about intent. It is still a guess. |
| "I'll implement it and flag the ambiguity in my report" | Disclosure afterwards is not a decision the user made. |
| "Asking would block them on something trivial" | If it were trivial it would not change the direction. |

**Red flags — you are about to fail:** "I'll pick the reversible one and note
it" · "it's additive, nothing breaks" · "I'll flag it in the report" · "there's
nobody to ask right now" · "they must mean this one".

Contested business meaning, an unstated scope boundary, and a conflict between
two documented sources are all blocking. A naming preference or a formatting
choice is not — decide those and move on.

## The artifact

Write `01-design.md` with these sections, in this order:

1. **Background and goal** — why this change, in the user's terms
2. **Confirmed decisions** — what the user settled, and when
3. **Open questions** — blocking questions, or `none`
4. **Non-goals** — what this change deliberately does not do
5. **Current state with evidence** — what you read, with paths
6. **Proposed design and trade-offs** — including what you rejected
7. **Files in scope** — every file the implementer may touch
8. **Ordered tasks** — small enough to check off
9. **Acceptance criteria** — the table below
10. **Risks and approval boundaries** — what must not proceed without asking

Then update `change.yaml` and stop. Do not start implementing because the
design "turned out simple".

## change.yaml

`status` takes exactly one of these values. There is no other vocabulary —
do not coin one:

`draft` · `ready_for_implementation` · `implementing` · `ready_for_review` ·
`rework` · `complete` · `abandoned`

This phase leaves `status: draft` while `Open questions` lists anything, and
sets `ready_for_implementation` only after the user has answered every one of
them. Blocked is not a status; it is `draft` with an open question.

Also set: `id`, `slug`, `title`, `mode`, `round`, `roles`, `created_at`,
`updated_at`.

`id` is `YYYY-MM-DD-<slug>`, and the change directory is named after it:
`.ho/changes/2026-08-05-monthly-active-users/`. Not a counter, not a bare slug.

## Acceptance criteria

Every row is `action → observable result → how to verify`. A criterion that
cannot be checked by running something or reading a named file is not a
criterion.

| # | Action | Expected observable result | How to verify |
|---|---|---|---|
| AC1 | Call `monthly_active_users(store, "2026-01")` | Returns 2 | unit test |
| AC2 | Run the suite | `python -m unittest discover -s tests -q` passes | command output |

Check each criterion against what is actually in the project before you write
it. A criterion that names a fixture row, a flag, or a file that does not exist
sends the implementer into an unrecorded judgment call.

Bad: "the metric works correctly", "performance is acceptable", "the code is
clean". None of those can come back `pass` or `fail`.
