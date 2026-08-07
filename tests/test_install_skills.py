"""Tests for scripts/install_skills.py.

    python -m unittest discover -s tests -p "test_install_skills.py" -q

Standard library only, and every case runs against a temporary directory so a
test run can never touch the developer's real skills directory.
"""

from __future__ import annotations

import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest
import unittest.mock

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))

import install_skills  # noqa: E402  (path set above)


SKILLS = ("ho-flow", "ho-design", "ho-impl", "ho-review")


class InstallSkillsTest(unittest.TestCase):
    def setUp(self):
        self.target = tempfile.mkdtemp(prefix="ho-skills-")
        self.addCleanup(shutil.rmtree, self.target, ignore_errors=True)

    def read(self, *parts):
        with open(os.path.join(*parts), "r", encoding="utf-8") as fh:
            return fh.read()

    def run_main(self, argv):
        """Call main() with its console output captured, and return the code.

        The CLI is supposed to print; a test run is not supposed to be buried
        in it.
        """
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = install_skills.main(argv)
        return code, out.getvalue(), err.getvalue()

    # -- AC3 ---------------------------------------------------------------

    def test_installs_the_four_skills_with_their_contents(self):
        install_skills.install(self.target)

        for skill in SKILLS:
            sdir = os.path.join(self.target, skill)
            self.assertTrue(os.path.isdir(sdir), "%s was not created" % skill)
            self.assertTrue(os.path.isfile(os.path.join(sdir, "SKILL.md")))
            self.assertTrue(
                os.path.isfile(os.path.join(sdir, "agents", "openai.yaml")),
                "%s: nested files must be copied, not just the top level" % skill,
            )

    def test_copied_skill_is_byte_identical_to_the_source(self):
        install_skills.install(self.target)

        source = self.read(REPO, "skills", "ho-design", "SKILL.md")
        installed = self.read(self.target, "ho-design", "SKILL.md")
        self.assertEqual(source, installed)

    def test_reports_every_installed_skill_as_created(self):
        result = install_skills.install(self.target)

        self.assertEqual(sorted(result.created), sorted(SKILLS))
        self.assertEqual(result.kept, [])
        self.assertEqual(result.updated, [])

    # -- default target ----------------------------------------------------

    def test_default_target_is_agents_skills_under_the_home_directory(self):
        self.assertEqual(
            install_skills.default_target(),
            os.path.join(os.path.expanduser("~"), ".agents", "skills"),
        )

    def test_default_target_follows_the_home_directory_of_the_current_user(self):
        home = os.path.join(self.target, "somebody")
        env = dict(os.environ)
        # expanduser reads USERPROFILE on Windows and HOME elsewhere; set both
        # so the assertion means the same thing on every platform.
        env["USERPROFILE"] = home
        env["HOME"] = home
        env.pop("HOMEDRIVE", None)
        env.pop("HOMEPATH", None)

        with unittest.mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(
                install_skills.default_target(),
                os.path.join(home, ".agents", "skills"),
            )

    # -- AC4: a second run keeps what is there -----------------------------

    def test_second_run_keeps_existing_skills_and_changes_nothing(self):
        install_skills.install(self.target)
        edited = os.path.join(self.target, "ho-design", "SKILL.md")
        with open(edited, "w", encoding="utf-8") as fh:
            fh.write("local edit")

        result = install_skills.install(self.target)

        self.assertEqual(sorted(result.kept), sorted(SKILLS))
        self.assertEqual(result.created, [])
        self.assertEqual(result.updated, [])
        self.assertEqual(self.read(edited), "local edit")

    def test_a_skill_directory_counts_as_present_even_when_empty(self):
        os.makedirs(os.path.join(self.target, "ho-impl"))

        result = install_skills.install(self.target)

        self.assertEqual(result.kept, ["ho-impl"])
        self.assertFalse(
            os.path.exists(os.path.join(self.target, "ho-impl", "SKILL.md")),
            "without --force an existing directory must not be filled in",
        )

    # -- AC5: --force updates the four, and only the four ------------------

    def test_force_restores_an_edited_skill_file(self):
        install_skills.install(self.target)
        edited = os.path.join(self.target, "ho-design", "SKILL.md")
        with open(edited, "w", encoding="utf-8") as fh:
            fh.write("local edit")

        result = install_skills.install(self.target, force=True)

        self.assertEqual(sorted(result.updated), sorted(SKILLS))
        self.assertEqual(result.created, [])
        self.assertEqual(
            self.read(edited),
            self.read(REPO, "skills", "ho-design", "SKILL.md"),
        )

    def test_force_leaves_unrelated_skills_in_the_target_alone(self):
        other = os.path.join(self.target, "someone-elses-skill")
        os.makedirs(other)
        with open(os.path.join(other, "SKILL.md"), "w", encoding="utf-8") as fh:
            fh.write("not mine")
        loose = os.path.join(self.target, "notes.txt")
        with open(loose, "w", encoding="utf-8") as fh:
            fh.write("keep me")

        install_skills.install(self.target, force=True)

        self.assertEqual(self.read(other, "SKILL.md"), "not mine")
        self.assertEqual(self.read(loose), "keep me")

    def test_force_keeps_extra_files_inside_a_skill_directory(self):
        install_skills.install(self.target)
        extra = os.path.join(self.target, "ho-review", "my-note.md")
        with open(extra, "w", encoding="utf-8") as fh:
            fh.write("mine")

        install_skills.install(self.target, force=True)

        self.assertTrue(os.path.isfile(extra), "--force must not delete, only overwrite")

    # -- target directory creation ----------------------------------------

    def test_creates_the_target_directory_when_it_does_not_exist(self):
        nested = os.path.join(self.target, "deep", "not", "there")

        install_skills.install(nested)

        self.assertTrue(os.path.isfile(os.path.join(nested, "ho-flow", "SKILL.md")))

    # -- Windows path handling --------------------------------------------

    def test_handles_a_target_path_containing_spaces(self):
        spaced = os.path.join(self.target, "Agent Skills", "my skills")

        install_skills.install(spaced)

        self.assertTrue(os.path.isfile(os.path.join(spaced, "ho-impl", "SKILL.md")))

    def test_accepts_a_relative_target_and_resolves_it(self):
        cwd = os.getcwd()
        os.chdir(self.target)
        self.addCleanup(os.chdir, cwd)

        install_skills.install(os.path.join(".", "here"))

        self.assertTrue(
            os.path.isfile(os.path.join(self.target, "here", "ho-flow", "SKILL.md")))

    def test_reports_paths_without_mixing_separators(self):
        result = install_skills.install(self.target)

        # The report names skills, not paths; the target is echoed once and has
        # to be a real path on this platform.
        self.assertEqual(sorted(result.created), sorted(SKILLS))
        self.assertTrue(os.path.isabs(result.target))
        self.assertEqual(result.target, os.path.abspath(self.target))

    # -- failure behaviour -------------------------------------------------

    def test_a_target_that_is_a_file_fails_with_a_readable_message(self):
        blocker = os.path.join(self.target, "a-file")
        with open(blocker, "w", encoding="utf-8") as fh:
            fh.write("")

        with self.assertRaises(install_skills.InstallError) as caught:
            install_skills.install(blocker)

        self.assertIn(blocker, str(caught.exception))

    def test_main_returns_nonzero_and_explains_when_the_target_is_a_file(self):
        blocker = os.path.join(self.target, "a-file")
        with open(blocker, "w", encoding="utf-8") as fh:
            fh.write("")

        code, _, err = self.run_main([blocker])

        self.assertNotEqual(code, 0)
        self.assertIn(blocker, err)

    def test_main_installs_into_the_given_target_and_returns_zero(self):
        code, out, _ = self.run_main([self.target])

        self.assertEqual(code, 0)
        self.assertTrue(
            os.path.isfile(os.path.join(self.target, "ho-flow", "SKILL.md")))
        for skill in SKILLS:
            self.assertIn("created  %s" % skill, out)

    def test_main_accepts_force_after_the_target(self):
        self.run_main([self.target])
        edited = os.path.join(self.target, "ho-flow", "SKILL.md")
        with open(edited, "w", encoding="utf-8") as fh:
            fh.write("local edit")

        code, out, _ = self.run_main([self.target, "--force"])

        self.assertEqual(code, 0)
        self.assertIn("updated  ho-flow", out)
        self.assertEqual(
            self.read(edited),
            self.read(REPO, "skills", "ho-flow", "SKILL.md"),
        )

    # -- the script stays out of the project ------------------------------

    def test_installing_does_not_write_anything_into_the_repository(self):
        before = self.snapshot(REPO)

        install_skills.install(self.target)

        self.assertEqual(before, self.snapshot(REPO))

    def snapshot(self, root):
        seen = {}
        for base, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
            for name in files:
                path = os.path.join(base, name)
                seen[path] = os.path.getsize(path)
        return seen


if __name__ == "__main__":
    unittest.main()
