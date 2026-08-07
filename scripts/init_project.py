"""Create `.ho/` in a project.

    python scripts/init_project.py [PROJECT_DIR] [--language en|zh-CN]
                                   [--mode solo|relay] [--force]

PROJECT_DIR defaults to the current directory. Existing files are never
overwritten unless you pass --force, and --force still never touches
`.ho/changes/` — handoff data is not a template.

This script does not modify your source code, your VCS configuration, or
anything outside `.ho/`.

Standard library only. Runs on Windows, macOS and Linux.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(REPO, "templates")
# The protocol has one canonical home; the zh-CN rendering lives with the
# other translated templates.
PROTOCOL_EN = os.path.join(REPO, "skills", "ho-flow", "references", "protocol.md")
PROTOCOL_ZH = os.path.join(TEMPLATES, "zh-CN", "protocol.md")

LANGUAGES = ("en", "zh-CN")
MODES = ("solo", "relay")

DOC_TEMPLATES = ("design.md", "implementation.md", "review.md")


class Result:
    """What the run did to each path, so the report can be honest about it.

    Three lists rather than a count: a user who runs this twice needs to see
    that the second run kept their edits, not just that it "succeeded".
    """

    def __init__(self):
        self.created = []
        self.kept = []
        self.replaced = []


def _template_dir(language):
    # English templates sit at the top of templates/; every translation gets a
    # subdirectory named after its language tag.
    return TEMPLATES if language == "en" else os.path.join(TEMPLATES, language)


def _copy(src, dest, force, result):
    """Copy `src` to `dest`, leaving an existing file alone unless forced.

    Silently overwriting is the one thing this script must never do: `.ho/` is
    inside someone's project and its config is meant to be edited.
    """
    if os.path.exists(dest):
        if not force:
            result.kept.append(dest)
            return
        result.replaced.append(dest)
    else:
        result.created.append(dest)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copyfile(src, dest)


def init(project_dir, language="en", mode="solo", force=False):
    project_dir = os.path.abspath(project_dir)
    if not os.path.isdir(project_dir):
        raise SystemExit("error: %s is not a directory" % project_dir)

    ho = os.path.join(project_dir, ".ho")
    tdir = _template_dir(language)
    result = Result()

    # config.yaml is the one file that is not a straight copy — the requested
    # --mode has to be written into it. Everything else goes through _copy().
    config_src = os.path.join(TEMPLATES, "config.yaml")
    config_dest = os.path.join(ho, "config.yaml")
    if os.path.exists(config_dest) and not force:
        result.kept.append(config_dest)
    else:
        existed = os.path.exists(config_dest)
        with open(config_src, "r", encoding="utf-8") as fh:
            text = fh.read()
        text = text.replace("\nmode: solo\n", "\nmode: %s\n" % mode)
        os.makedirs(ho, exist_ok=True)
        with open(config_dest, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        (result.replaced if existed else result.created).append(config_dest)

    # The project gets its own copy of the protocol rather than a pointer at
    # this repository: agents read `.ho/protocol.md` at runtime, and the project
    # keeps working after this checkout is gone.
    protocol_src = PROTOCOL_EN if language == "en" else PROTOCOL_ZH
    _copy(protocol_src, os.path.join(ho, "protocol.md"), force, result)

    for name in DOC_TEMPLATES:
        _copy(os.path.join(tdir, name),
              os.path.join(ho, "templates", name), force, result)
    _copy(os.path.join(TEMPLATES, "change.yaml"),
          os.path.join(ho, "templates", "change.yaml"), force, result)

    # Handoff data, never a template. Created empty and never overwritten, not
    # even under --force: the directory holds work in progress, and a re-init
    # that wiped it would destroy the record the whole workflow exists to keep.
    changes = os.path.join(ho, "changes")
    if not os.path.isdir(changes):
        os.makedirs(changes)
        result.created.append(changes)

    return result


def _report(result, project_dir):
    def rel(p):
        try:
            return os.path.relpath(p, project_dir)
        except ValueError:
            # Windows: relpath raises when the two paths are on different
            # drives. Fall back to the absolute path rather than crash.
            return p

    for path in result.created:
        print("created  %s" % rel(path))
    for path in result.replaced:
        print("replaced %s" % rel(path))
    for path in result.kept:
        print("kept     %s (already present; --force to replace)" % rel(path))
    if not result.created and not result.replaced:
        print("nothing to do")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Create .ho/ in a project.",
        epilog="Existing files are kept unless --force is given.",
    )
    parser.add_argument("project_dir", nargs="?", default=".",
                        help="project to initialize (default: current directory)")
    parser.add_argument("--language", choices=LANGUAGES, default="en",
                        help="language of the copied document templates")
    parser.add_argument("--mode", choices=MODES, default="solo",
                        help="default mode written into config.yaml")
    parser.add_argument("--force", action="store_true",
                        help="replace existing files under .ho/, except changes/")
    # argparse rejects an unknown --mode or --language for us, which is why
    # nothing downstream re-validates them. Note `auto` is deliberately absent:
    # it is a per-request option, not a mode.
    args = parser.parse_args(argv)

    result = init(args.project_dir, args.language, args.mode, args.force)
    _report(result, os.path.abspath(args.project_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
