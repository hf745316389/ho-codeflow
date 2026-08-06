# Examples

Two complete changes, shown as the files they leave behind.

- [solo/](solo/) — one agent runs every phase. The design stops on a business
  question, the user answers, and the change reaches `complete` with a
  self-review.
- [relay/](relay/) — three agents. The implementer finds that the design does
  not match the project, stops, and the reviewer sends it back for `rework`.

These are illustrations, hand-written to show the shape of each artifact. They
are not transcripts. The relay one follows a conflict that real agents did hit
— the runs are in `tests/baseline/` — but the prose here is composed, not
captured, so read it as a worked example rather than as evidence.

The relay example is the more instructive of the two: it is the failure the
baseline reproduced 5/5 without the skills, caught at the point where it costs
one question instead of a wrong number in a finance report.

It also has a loose end that the skills do not currently close. Its blocking
fix says the acceptance criterion must be restated — an edit to an approved
design — and nothing in the protocol says who may make that edit or how it is
recorded. See the known gaps in the README.
