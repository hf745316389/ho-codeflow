# Configuration

`.ho/config.yaml` holds project defaults. Every key is optional; a missing key
takes the default below. A missing file means all defaults, and the first time
a change is created the flow offers to write one.

| Key | Default | What it does |
|---|---|---|
| `version` | `1` | Config schema version |
| `mode` | `solo` | `solo` or `relay` when the request names neither |
| `paths.root` | `.ho` | Where Ho CodeFlow keeps its files |
| `paths.changes` | `.ho/changes` | Where change directories go |
| `approval.after_design` | `true` | Stop for approval after the design |
| `approval.destructive_actions` | `true` | Stop before irreversible actions |
| `approval.external_writes` | `true` | Stop before writing outside the project |
| `review.fresh_context_preferred` | `true` | Prefer a reviewer without the implementation in context |
| `review.independent_reviewer_for_high_risk` | `true` | Ask for an independent reviewer when the design marks the change high-risk |
| `concurrency.verify_file_fingerprints` | `true` | Record and re-check file hashes before writing |
| `language.artifacts` | `auto` | `auto` follows the user's language in prose; field names and status values stay English |

## What config cannot do

`approval.destructive_actions: false` does not authorize deletion. Setting a
gate to `false` says the project does not want a routine prompt for that class
of action; it does not convert an irreversible or outward-facing action into a
routine one. Those still stop and ask.

`auto` is never stored here. It is an option on a single request.

`mode` is `solo` or `relay` and nothing else.

## Precedence

The project's own instruction file outranks this config, and this config
outranks Ho CodeFlow's defaults. Platform and safety rules outrank all three.
