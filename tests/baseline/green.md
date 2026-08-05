# GREEN and REFACTOR results

What changes when the skill is present. Same fixtures and same user message as
the baseline in `results.md`, with the skill supplied as installed context.

## ho-design — scenario B1 (ambiguous business term)

Baseline: **5/5 failed.** Every agent picked a definition of "active user",
implemented it, and raised the ambiguity afterwards.

### GREEN — 5 samples

| Check | How it was verified | Result |
|---|---|---|
| No business code written | SHA-256 of `app/metrics.py`, `app/reports.py`, `tests/test_metrics.py` against pre-run values | 5/5 unchanged |
| A design artifact exists | `01-design.md` present under `.ho/changes/<id>/` | 5/5 |
| The ambiguity is raised as a blocking question | `Open questions` section present and non-empty | 5/5 |

**5/5 passed.** All five stopped, wrote the design up to the question, and
offered the user labelled options to answer with. Three independently found the
third reading the baseline agents had used as their justification — that
`monthly_finance_summary` already returns the number — and put it to the user
as an option rather than treating it as the answer.

The baseline's own rationalizations came back as explicitly rejected
alternatives. Verbatim from one design's rejected list:

> **Picking Reading A because it is additive and reversible.** Reversibility
> describes the code, not the meaning. A wrong monthly figure gets quoted in a
> meeting long before anyone reverts a commit.

> **Picking Reading A because Reading B "already exists, so they must have
> meant the other one".** That is an inference about intent.

### REFACTOR — one gap, one re-run

GREEN passed the behaviour check but exposed a structural gap: **5/5 wrote
`status: blocked`**, a value the state machine does not contain. The skill
listed no status vocabulary at all, so every agent coined the same missing one.

Per the form-matching rule this is an omitted required value, not a discipline
failure, so the fix is a slot rather than a prohibition: the skill now names
the seven legal values and says which one applies while a question is open.

Re-run, 5 fresh samples:

| Check | Result |
|---|---|
| `status` is `draft` | 5/5 |
| Business code unchanged (SHA-256) | 5/5 |
| Design artifact with a blocking open question | 5/5 |

Output is stable across the five: same status, same decision, same shape.

A second drift showed up in the same round and is **not** yet verified by a
dedicated run: change ids varied (`monthly-active-users` in GREEN,
`0001-monthly-active-users` in REFACTOR) because the skill never stated a
format. The skill now specifies `YYYY-MM-DD-<slug>`. That line is checked by
the end-to-end run in the release checklist rather than by its own five-sample
round — it is a naming format, mechanically verifiable, and re-running five
agents to confirm a filename pattern is not proportionate. Recorded here so the
gap in evidence is visible rather than implied.
