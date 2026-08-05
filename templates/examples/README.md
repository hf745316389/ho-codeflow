# Examples

Two complete changes, shown as the files they leave behind.

- [solo/](solo/) — one agent runs every phase. The design stops on a business
  question, the user answers, and the change reaches `complete` with a
  self-review.
- [relay/](relay/) — three agents. The implementer finds that the design does
  not match the project, stops, and the reviewer sends it back for `rework`.

Both are edited-down versions of real runs against the sample project in
`tests/fixtures/`. The relay example is the more instructive one: it is the
failure the baseline reproduced 5/5 without the skills, caught here at the
point where it costs one question instead of a wrong number in a finance
report.
