# Review: <title>

## Review kind

`self` or `independent`.

`self` means you also designed or implemented this change. Say so plainly; a
labelled self-review is useful, an unlabelled one is misleading.

## Acceptance item results

| # | Criterion | Result |
|---|---|---|
| AC1 | | pass / fail / unverified |
| AC2 | | |

Exactly one result per criterion. There is no fourth value: not `partial`, not
`mostly`, not `n/a`. A criterion the implementer did not attempt is `fail` —
`unverified` is about your ability to check it, not their decision to skip it.

## Evidence

| # | How you checked it | What you observed |
|---|---|---|
| AC1 | | |

From a file you opened or a command you ran during this review. The
implementation report is where to look, not what you found.

If a criterion would give the same result under an implementation you know to
be wrong, say so here. It passed without discriminating anything.

## Deviation decisions

| Deviation | Accepted? | Why |
|---|---|---|
| | | |

One row per deviation the implementer recorded. If the artifacts show a
deviation they did not record, add it here and say it was undeclared.

## Blocking fixes

What must change before this is done. Each one names the criterion, the
observed result, and what would have to be different.

## Non-blocking suggestions

What you would change but are not gating on. Keep this list separate so the
reader can tell which one they have to act on.

## Final status

`rework` or `complete`, and the reason. Do not write `complete` while anything
is listed under blocking fixes.
