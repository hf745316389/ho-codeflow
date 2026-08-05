# Ho CodeFlow protocol v1

The rules every phase shares. `scripts/init_project.py` copies this file into a
project as `.ho/protocol.md`, and that copy is what agents read at runtime.

## Layout

```
<project>/
├── .ho/
│   ├── config.yaml
│   ├── protocol.md
│   └── changes/
│       └── 2026-08-05-example-change/
│           ├── change.yaml
│           ├── 01-design.md
│           ├── 02-implementation.md
│           └── 03-review.md
└── <project files>
```

A change id is `YYYY-MM-DD-<slug>` and the directory is named after it.

## State

`change.yaml` is the only place state lives. Do not also record status inside
the markdown artifacts — two copies of a state disagree eventually.

`status` is one of `draft`, `ready_for_implementation`, `implementing`,
`ready_for_review`, `rework`, `complete`, `abandoned`. There is no `blocked`:
work that has stopped on a question keeps the status of the phase it stopped
in, and the question lives in the artifact.

```
draft                    -> ready_for_implementation
ready_for_implementation -> implementing
implementing             -> ready_for_review
ready_for_review         -> complete
ready_for_review         -> rework
rework                   -> implementing        (round += 1)
any unfinished state     -> abandoned           (only when the user says so)
```

`ready_for_implementation` records the user's approval, not the designer's
sense of being finished. A design stays `draft` while `Open questions` lists
anything, and also when it lists nothing: having no question left to ask is not
the same as having been approved. The user moves it on — or `ho-flow` does when
they asked for `auto`, which is that approval given in advance.

Where an open question exists, the user's answer carries the approval too. They
do not have to say yes twice.

`review_kind` is `self` or `independent`, and it is set by whoever writes the
review, on the basis of whether they also designed or implemented the change.

## Which change

When more than one change is open and the request names none of them, list the
candidates and ask which. Do not infer one from recency, ordering, or which
looks more prepared, and do not do all of them.

## Where work stops for approval

Regardless of any instruction to work straight through:

- irreversible deletion
- data migrations
- writes to systems outside this project
- publishing or sending anything other people will see
- production changes
- anything the project's own rules gate

Checking that the blast radius matches the request establishes what would
happen. It does not establish that you may do it.

## Evidence

Code facts come from the files, not from what a previous phase reported about
them. Test results come from a command run in the current round. An item that
could not be checked is recorded as `unverified` with the reason; whether the
change can still be `complete` with one is settled by the design's definition
of done.

Ho CodeFlow does not mandate a citation format. Follow whatever the project
already uses.

## Concurrent edits

Record a SHA-256 for each file you intend to change when you first read it. Re-
read and compare before writing. If it changed and the change is not yours,
rebase your edit onto the new content, and ask if the two contradict. Never
resolve an unexplained change by reverting, by overwriting the whole file, or
by restoring an old copy.

## Precedence

The project's own instruction file — `AGENTS.md`, or whatever equivalent your
host reads — outranks this protocol. Platform and safety rules outrank
everything here.

## Language

Artifact prose follows the user's language. Field names, status values, and
file names stay as written here in every language.
