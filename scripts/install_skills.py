"""Copy the four skills into the directory your agent reads skills from.

    python scripts/install_skills.py [TARGET_DIR] [--force]

TARGET_DIR defaults to `~/.agents/skills`, which is a common cross-host
location — not a standard. Hosts differ, and some read skills from the project
instead. Check your agent's documentation and pass its directory if it uses
another one.

An existing `ho-*` directory is kept, not overwritten, unless you pass --force.
--force overwrites the files this repository ships and nothing else: it never
deletes, so other skills in the target and your own additions inside a skill
directory both survive.

This script writes only under TARGET_DIR. It does not modify your source code
or your VCS configuration.

Standard library only. Runs on Windows, macOS and Linux.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(REPO, "skills")

SKILLS = ("ho-flow", "ho-design", "ho-impl", "ho-review")


class InstallError(Exception):
    """A condition the user has to fix, reported without a traceback."""


class Result:
    """What the run did to each skill, so the report can be honest about it.

    Three lists rather than a count, for the same reason `init_project.py`
    keeps three: someone running this a second time needs to see that their
    edits were kept, not merely that the command succeeded.
    """

    def __init__(self, target):
        self.target = target
        self.created = []
        self.kept = []
        self.updated = []


def default_target():
    """The directory used when the caller names none.

    Resolved at call time rather than at import, so a test — or a user with an
    unusual HOME — gets the home directory in force now.
    """
    return os.path.join(os.path.expanduser("~"), ".agents", "skills")


def _copy_tree(src, dest):
    """Copy every file under `src` into `dest`, overwriting matching files.

    Deliberately not `shutil.copytree`: that either refuses to write into an
    existing directory or, with `dirs_exist_ok`, still gives no way to promise
    that nothing already there is removed. Walking the source means the only
    paths ever touched are the ones this repository ships.
    """
    for base, dirs, files in os.walk(src):
        # Compiled Python from a source checkout is not part of a skill.
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        relative = os.path.relpath(base, src)
        out = dest if relative == "." else os.path.join(dest, relative)
        os.makedirs(out, exist_ok=True)
        for name in files:
            shutil.copyfile(os.path.join(base, name), os.path.join(out, name))


def install(target_dir, force=False):
    """Install the four skills into `target_dir` and report what happened."""
    target = os.path.abspath(target_dir)

    if os.path.exists(target) and not os.path.isdir(target):
        raise InstallError("%s exists and is not a directory" % target)

    missing = [s for s in SKILLS if not os.path.isdir(os.path.join(SOURCE, s))]
    if missing:
        raise InstallError(
            "cannot find %s under %s; run this from a checkout of the repository"
            % (", ".join(missing), SOURCE))

    try:
        os.makedirs(target, exist_ok=True)
    except OSError as error:
        raise InstallError("cannot create %s: %s" % (target, error))

    result = Result(target)
    for skill in SKILLS:
        dest = os.path.join(target, skill)
        if os.path.exists(dest):
            # Present means present: a directory someone made by hand is still
            # theirs, and filling it in silently would be the overwrite this
            # flag exists to prevent.
            if not force:
                result.kept.append(skill)
                continue
            result.updated.append(skill)
        else:
            result.created.append(skill)

        try:
            _copy_tree(os.path.join(SOURCE, skill), dest)
        except OSError as error:
            raise InstallError("cannot write %s: %s" % (dest, error))

    return result


def _report(result):
    print("target   %s" % result.target)
    for skill in result.created:
        print("created  %s" % skill)
    for skill in result.updated:
        print("updated  %s" % skill)
    for skill in result.kept:
        print("kept     %s (already present; --force to update)" % skill)
    if not result.created and not result.updated:
        print("nothing to do")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Copy the four ho-* skills into your agent's skills directory.",
        epilog="Existing skills are kept unless --force is given. Nothing is ever deleted.",
    )
    parser.add_argument(
        "target_dir", nargs="?", default=None,
        help="where to install (default: %s)" % default_target())
    parser.add_argument(
        "--force", action="store_true",
        help="overwrite the shipped files of skills that are already there")
    args = parser.parse_args(argv)

    try:
        result = install(args.target_dir or default_target(), args.force)
    except InstallError as error:
        print("error: %s" % error, file=sys.stderr)
        return 1

    _report(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
