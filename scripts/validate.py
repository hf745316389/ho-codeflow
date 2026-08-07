"""Check this repository for the drift that silently breaks handoffs.

    python scripts/validate.py [--verbose]

Exits 0 when everything passes, 1 otherwise. Standard library only; runs on
Windows, macOS and Linux.

What it checks, and why each one is here rather than left to review:

- Skill layout and frontmatter. A skill with a malformed header is not
  discoverable, and the failure is silent.
- The shared vocabulary. Status values, modes and review kinds are how one
  agent reads what another wrote. A value invented in one file is understood
  nowhere else.
- Artifact filenames. The next agent opens `01-design.md` by name.
- Vendor neutrality of the skills, protocol and templates. READMEs may name
  products as installation examples; the skills may not.
- Both READMEs carrying the same vocabulary, so a translation cannot drift.
- Markdown fences and relative links, which break quietly.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKILLS = ("ho-flow", "ho-design", "ho-impl", "ho-review")

STATUSES = (
    "draft",
    "ready_for_implementation",
    "implementing",
    "ready_for_review",
    "rework",
    "complete",
    "abandoned",
)
MODES = ("solo", "relay")
REVIEW_KINDS = ("self", "independent")
ARTIFACTS = ("change.yaml", "01-design.md", "02-implementation.md", "03-review.md")

# Vendor names in a skill body would make the handoff instructions wrong for
# whoever the reader actually opens tomorrow. READMEs may name products as
# installation examples; skills and templates may not.
VENDOR = re.compile(
    r"\b(claude|codex|cursor|copilot|gemini|aider|windsurf|chatgpt|openai|anthropic)\b"
    r"|CLAUDE\.md|\.cursorrules",
    re.IGNORECASE,
)
# `agents/openai.yaml` is a filename fixed by the host ecosystem, and skills may
# name it when explaining that the file is optional.
VENDOR_ALLOWED = ("agents/openai.yaml", "openai.yaml")

FRONTMATTER_KEYS = ("name", "description")


class Report:
    """Collects failures instead of raising on the first one.

    A contributor fixing drift wants the whole list in one run, not one error
    per invocation. `checks` counts every assertion attempted — see the note in
    the README about how to read that number.
    """

    def __init__(self):
        self.errors = []
        self.checks = 0

    def check(self, ok, message):
        self.checks += 1
        if not ok:
            self.errors.append(message)
        return ok


def read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def markdown_files():
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in (".git", ".dev", "__pycache__")]
        for name in files:
            if name.endswith(".md"):
                yield os.path.join(root, name)


def rel(path):
    return os.path.relpath(path, REPO).replace(os.sep, "/")


# --------------------------------------------------------------------------


def parse_frontmatter(text):
    """Return (dict, body) or (None, text) when there is no frontmatter.

    A deliberately small YAML subset — flat `key: value` pairs plus indented
    continuation lines — because this repository ships no dependencies and the
    frontmatter spec allows nothing more than that anyway. Anything it cannot
    parse is reported as malformed rather than guessed at.
    """
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    raw = text[4:end]
    body = text[end + 5:]
    data = {}
    key = None
    for line in raw.split("\n"):
        if not line.strip():
            continue
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if match:
            key = match.group(1)
            data[key] = match.group(2).strip()
        elif key is not None and line.startswith((" ", "\t")):
            data[key] = (data[key] + " " + line.strip()).strip()
        else:
            return None, text
    return data, body


def check_skills(report):
    for skill in SKILLS:
        sdir = os.path.join(REPO, "skills", skill)
        if not report.check(os.path.isdir(sdir), "missing skill directory: skills/%s" % skill):
            continue

        path = os.path.join(sdir, "SKILL.md")
        if not report.check(os.path.isfile(path), "missing skills/%s/SKILL.md" % skill):
            continue

        text = read(path)
        data, body = parse_frontmatter(text)
        if not report.check(data is not None,
                            "skills/%s/SKILL.md: no parseable YAML frontmatter" % skill):
            continue

        report.check(
            set(data) == set(FRONTMATTER_KEYS),
            "skills/%s/SKILL.md: frontmatter keys are %s, expected exactly %s"
            % (skill, sorted(data), sorted(FRONTMATTER_KEYS)),
        )
        report.check(data.get("name") == skill,
                     "skills/%s/SKILL.md: name is %r, expected %r"
                     % (skill, data.get("name"), skill))

        raw_header = text[4:text.find("\n---\n", 4)]
        report.check(len(raw_header) <= 1024,
                     "skills/%s/SKILL.md: frontmatter is %d chars, limit is 1024"
                     % (skill, len(raw_header)))

        description = data.get("description", "")
        # "Use when" keeps descriptions to triggering conditions. A description
        # that summarises the workflow gets followed *instead of* the skill body.
        report.check(description.startswith("Use when"),
                     "skills/%s/SKILL.md: description must start with 'Use when'" % skill)
        report.check(len(description) <= 500,
                     "skills/%s/SKILL.md: description is %d chars, keep it under 500"
                     % (skill, len(description)))
        report.check(bool(body.strip()),
                     "skills/%s/SKILL.md: body is empty" % skill)

        agents = os.path.join(sdir, "agents", "openai.yaml")
        report.check(os.path.isfile(agents),
                     "missing skills/%s/agents/openai.yaml" % skill)

        # Skill directories hold runtime files only. Anything a human reads —
        # installation, changelog — belongs in the repository root, so that a
        # skill copied into an agent's skills directory carries no dead weight.
        for stray in ("README.md", "CHANGELOG.md", "INSTALL.md"):
            report.check(not os.path.exists(os.path.join(sdir, stray)),
                         "skills/%s/%s: skill directories hold runtime files only"
                         % (skill, stray))


def check_vendor_neutrality(report):
    targets = []
    for skill in SKILLS:
        sdir = os.path.join(REPO, "skills", skill)
        for root, dirs, files in os.walk(sdir):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            targets += [os.path.join(root, f) for f in files if f.endswith(".md")]
    tdir = os.path.join(REPO, "templates")
    for root, dirs, files in os.walk(tdir):
        dirs[:] = [d for d in dirs if d != "examples"]
        targets += [os.path.join(root, f) for f in files if f.endswith(".md")]

    for path in targets:
        for lineno, line in enumerate(read(path).split("\n"), 1):
            if any(allowed in line for allowed in VENDOR_ALLOWED):
                continue
            match = VENDOR.search(line)
            report.check(match is None,
                         "%s:%d names a vendor (%s); skills and templates stay neutral"
                         % (rel(path), lineno, match.group(0) if match else ""))


def check_vocabulary(report):
    """Every status/mode/review_kind value written anywhere must be a legal one.

    Invented values are the failure mode this catches: agents coined `blocked`
    and `reviewed` in testing, and a status one agent writes and the next does
    not recognise breaks the handoff silently. `tests/` is excluded because its
    fixtures deliberately contain wrong values.
    """
    pattern = re.compile(r"^\s*[-*|>` ]*(status|mode|review_kind):\s*`?([a-z_][a-z_]*)`?",
                         re.MULTILINE)
    legal = {"status": STATUSES, "mode": MODES, "review_kind": REVIEW_KINDS}

    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in (".git", ".dev", "__pycache__", "tests")]
        for name in files:
            if not name.endswith((".md", ".yaml", ".yml")):
                continue
            path = os.path.join(root, name)
            for match in pattern.finditer(read(path)):
                field, value = match.group(1), match.group(2)
                report.check(value in legal[field],
                             "%s: %s: %s is not a legal value (allowed: %s)"
                             % (rel(path), field, value, ", ".join(legal[field])))


def check_readmes(report):
    """The two READMEs must mention the same vocabulary, or neither.

    Prose is not compared — translations should read naturally. What cannot
    drift is which statuses, modes, artifacts and skills exist, because a
    reader of one README should not learn a different product from the other.
    """
    # README.md is the one GitHub renders on the repository page, and it holds
    # the Chinese text; the English rendering lives beside it under its own
    # language tag. Which language is default is a positioning decision, not a
    # structural one — this check only cares that the two stay in step.
    default = os.path.join(REPO, "README.md")
    english = os.path.join(REPO, "README.en.md")
    if not report.check(os.path.isfile(default), "missing README.md"):
        return
    if not report.check(os.path.isfile(english), "missing README.en.md"):
        return

    default_text, english_text = read(default), read(english)
    for token in list(STATUSES) + list(MODES) + list(ARTIFACTS) + list(SKILLS):
        in_default, in_english = token in default_text, token in english_text
        # Plain ASCII: this message has to survive a Windows console codepage.
        report.check(in_default == in_english,
                     "%r appears in %s but not the other README; the two must stay in step"
                     % (token, "README.md" if in_default else "README.en.md"))


def check_templates(report):
    required = ("config.yaml", "change.yaml", "design.md", "implementation.md", "review.md")
    for name in required:
        report.check(os.path.isfile(os.path.join(REPO, "templates", name)),
                     "missing templates/%s" % name)
    for name in ("protocol.md", "design.md", "implementation.md", "review.md"):
        report.check(os.path.isfile(os.path.join(REPO, "templates", "zh-CN", name)),
                     "missing templates/zh-CN/%s" % name)
    report.check(
        os.path.isfile(os.path.join(REPO, "skills", "ho-flow", "references", "protocol.md")),
        "missing skills/ho-flow/references/protocol.md (the canonical protocol)",
    )
    # One canonical English protocol, not two that can drift.
    report.check(
        not os.path.exists(os.path.join(REPO, "templates", "protocol.md")),
        "templates/protocol.md duplicates skills/ho-flow/references/protocol.md; "
        "keep one English protocol",
    )


def check_fences(report):
    # An unbalanced fence swallows the rest of the file when rendered, which
    # hides content rather than announcing itself.
    for path in markdown_files():
        count = 0
        for line in read(path).split("\n"):
            if line.lstrip().startswith("```"):
                count += 1
        report.check(count % 2 == 0,
                     "%s: %d code fences, unbalanced" % (rel(path), count))


LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def check_links(report):
    for path in markdown_files():
        base = os.path.dirname(path)
        for target in LINK.findall(read(path)):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            clean = target.split("#", 1)[0]
            if not clean:
                continue
            if "<" in clean or ">" in clean:
                # A documentation placeholder such as `.ho/changes/<id>/`, not
                # a path that is supposed to exist.
                continue
            resolved = os.path.normpath(os.path.join(base, clean))
            report.check(os.path.exists(resolved),
                         "%s: link target %r does not exist" % (rel(path), target))


def check_config_example(report):
    text = read(os.path.join(REPO, "templates", "config.yaml"))
    for field in ("version", "mode", "paths", "approval", "review",
                  "concurrency", "language"):
        report.check(re.search(r"^%s:" % field, text, re.MULTILINE) is not None,
                     "templates/config.yaml: missing top-level key %r" % field)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    report = Report()
    for check in (check_skills, check_vendor_neutrality, check_vocabulary,
                  check_readmes, check_templates, check_fences, check_links,
                  check_config_example):
        check(report)

    if report.errors:
        for error in report.errors:
            print("FAIL %s" % error)
        print("\n%d of %d checks failed" % (len(report.errors), report.checks))
        return 1

    print("ok: %d checks passed" % report.checks)
    if args.verbose:
        print("skills: %s" % ", ".join(SKILLS))
        print("statuses: %s" % ", ".join(STATUSES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
