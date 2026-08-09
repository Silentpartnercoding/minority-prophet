import hashlib
import pathlib
import sys
import tempfile
import unittest

from scripts.check_public_boundary import violations, sensitive_vocabulary_hit

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts/check_public_boundary.py"


def test_rejects_new_local_paths():
    lines = [("README.md", 3, "/Users/example/private/project/output.json")]
    assert any("local user path" in r for r in violations(lines))


def test_rejects_local_paths_after_any_delimiter():
    """PBC-101 gap 1. The rule once required whitespace, a quote or '(' before
    the path, so the two most common shapes in this repository's run records --
    an assignment and an scp-style remote -- were passed. Measured at the time:
    11 of 37 real leaked lines missed."""
    lines = [
        ("run/environment-lock.txt", 1, "python_executable=/Users/someone/venv/bin/python"),
        ("run/git-remotes.txt", 2, "origin  user@10.0.0.1:/Users/someone/repo/project"),
    ]
    results = violations(lines)
    assert len(results) == 2, f"both delimiter forms must be caught: {results}"


def test_sensitive_vocabulary_is_matched_without_being_named(monkeypatch):
    """BLK-101. Internal vocabulary is matched by digest so that this checker --
    a public file -- stops publishing the list of what it protects. The term
    used here is injected, so this test names nothing real either."""
    monkeypatch.setenv("MP_BOUNDARY_TERMS", "widget lane alpha")
    assert sensitive_vocabulary_hit("we should ship the widget lane alpha soon")
    assert not sensitive_vocabulary_hit("we should ship the widget soon")
    results = violations([("README.md", 4, "part of the widget lane alpha")])
    assert any("internal vocabulary" in r for r in results)


def test_the_shipped_vocabulary_list_names_nothing():
    """The regression that motivated BLK-101: the blocklist must not contain a
    readable term. Every shipped entry is a 64-character hex digest."""
    source = __import__("pathlib").Path("scripts/check_public_boundary.py").read_text()
    block = source.split("_TERM_DIGESTS = frozenset({")[1].split("})")[0]
    entries = [e.strip().strip('",') for e in block.splitlines() if e.strip().startswith('"')]
    assert entries, "digest list should not be empty"
    for entry in entries:
        assert len(entry) == 64 and all(c in "0123456789abcdef" for c in entry), entry


def test_rejects_high_confidence_secret_shape():
    lines = [
        ("config.txt", 7, "token=ghp_abcdefghijklmnopqrstuvwxyz1234567890"),
        ("config.txt", 8, "client_secret=abcdefghijklmnopqrstuvwxyz123456"),
        ("config.txt", 9, "https://service.test/callback?access_token=abcdefghijklmnopqrstuvwxyz"),
    ]
    results = violations(lines)
    assert any("GitHub token" in result for result in results)
    assert any("assigned secret" in result for result in results)
    assert any("credential-bearing URL" in result for result in results)


def test_allows_public_technical_language():
    lines = [
        ("README.md", 1, "The verifier exposes uncertainty and cannot manufacture evidence."),
        ("docs/design.md", 8, "Run python scripts/run_experiment.py from the repository root."),
        ("docs/config.md", 9, "Set API_KEY=YOUR_API_KEY before running the example."),
    ]
    assert violations(lines) == []


SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts/check_public_boundary.py"


class TestEmptyDiffIsRefusedNotPassed(unittest.TestCase):
    """A vacuous run must not report success.

    Running the check with --head HEAD before committing makes base and head the
    same commit. The diff is empty, nothing is inspected, and the old behaviour
    was to print "passed". Three publications in this programme were cleared by
    exactly that, including the leak FINDING-PBC-101 records.
    """

    def _repo(self, tmp):
        import subprocess as sp
        g = lambda *a: sp.run(("git",) + a, cwd=tmp, capture_output=True, check=True)
        g("init", "-q", "-b", "main")
        g("config", "user.email", "t@t"); g("config", "user.name", "t")
        (tmp / "a.txt").write_text("clean\n")
        g("add", "-A"); g("commit", "-qm", "base")
        return g

    def _run(self, tmp):
        import subprocess as sp
        return sp.run((sys.executable, str(SCRIPT), "--base", "HEAD", "--head", "HEAD"),
                      cwd=tmp, capture_output=True, text=True)

    def test_empty_diff_with_a_dirty_tree_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = pathlib.Path(d); self._repo(tmp)
            (tmp / "a.txt").write_text("uncommitted change\n")   # the real situation
            r = self._run(tmp)
            self.assertEqual(r.returncode, 1, f"must not pass:\n{r.stdout}{r.stderr}")
            self.assertIn("REFUSED", r.stderr)

    def test_empty_diff_with_a_clean_tree_still_passes(self):
        """The guard must not break the legitimate no-op case: a branch with
        nothing added is genuinely clean, and blocking it would make the check
        impossible to run in CI on an unchanged tree."""
        with tempfile.TemporaryDirectory() as d:
            tmp = pathlib.Path(d); self._repo(tmp)
            r = self._run(tmp)
            self.assertEqual(r.returncode, 0, f"{r.stdout}{r.stderr}")


class TestSweepMode(unittest.TestCase):
    """The diff mode cannot see what was already published. A term added to the
    blocklist today is never applied to yesterday's commits, which is how an
    owner-designated never-public term outlived the rule that blocks it."""

    def _repo(self, tmp, content):
        import subprocess as sp
        g = lambda *a: sp.run(("git",) + a, cwd=tmp, capture_output=True, check=True)
        g("init", "-q", "-b", "main")
        g("config", "user.email", "t@t"); g("config", "user.name", "t")
        (tmp / "old.md").write_text(content)
        g("add", "-A"); g("commit", "-qm", "already published")
        return g

    def _sweep(self, tmp):
        import subprocess as sp
        return sp.run((sys.executable, str(SCRIPT), "--sweep", "--head", "HEAD"),
                      cwd=tmp, capture_output=True, text=True)

    def test_sweep_finds_a_pre_existing_violation_the_diff_mode_cannot(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = pathlib.Path(d)
            self._repo(tmp, "note: /Users/someone/secret/path/file.txt\n")

            import subprocess as sp
            diff = sp.run((sys.executable, str(SCRIPT), "--base", "HEAD", "--head", "HEAD"),
                          cwd=tmp, capture_output=True, text=True)
            self.assertEqual(diff.returncode, 0,
                             "precondition: the diff mode sees nothing to inspect")

            swept = self._sweep(tmp)
            self.assertEqual(swept.returncode, 1, f"{swept.stdout}{swept.stderr}")
            self.assertIn("SWEEP failed", swept.stderr)
            self.assertIn("old.md", swept.stderr)

    def test_sweep_is_clean_on_a_tree_with_nothing_to_find(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = pathlib.Path(d)
            self._repo(tmp, "an ordinary sentence about verification.\n")
            r = self._sweep(tmp)
            self.assertEqual(r.returncode, 0, f"{r.stdout}{r.stderr}")
            self.assertIn("sweep clean", r.stdout)


def test_digests_can_be_supplied_without_the_term(monkeypatch):
    """The term must be able to stay out of every artefact.

    MP_BOUNDARY_TERMS requires the plaintext to reach CI, which means typing it
    somewhere that logs. MP_BOUNDARY_DIGESTS takes the hash instead, computed on
    the owner's machine, so the word exists in no file, no history and no
    transcript -- and the digest is in a secret rather than in this public file,
    so it cannot be wordlisted either.
    """
    import hashlib as _h
    monkeypatch.delenv("MP_BOUNDARY_TERMS", raising=False)
    monkeypatch.setenv("MP_BOUNDARY_DIGESTS",
                       _h.sha256(b"invented lane marker").hexdigest())
    assert sensitive_vocabulary_hit("ship it through the invented lane marker")
    assert not sensitive_vocabulary_hit("ship it through the ordinary channel")


def test_multiple_digests_may_be_separated_by_whitespace_or_commas(monkeypatch):
    import hashlib as _h
    a = _h.sha256(b"alpha widget").hexdigest()
    b = _h.sha256(b"beta widget").hexdigest()
    monkeypatch.delenv("MP_BOUNDARY_TERMS", raising=False)
    monkeypatch.setenv("MP_BOUNDARY_DIGESTS", f"{a}, {b}")
    assert sensitive_vocabulary_hit("the alpha widget")
    assert sensitive_vocabulary_hit("the beta widget")


def test_malformed_digest_entries_are_ignored_not_crashed_on(monkeypatch):
    """A secret with a stray quote or a truncated value must not take CI down;
    it must simply not match. A boundary check that crashes is a boundary check
    that gets disabled."""
    monkeypatch.delenv("MP_BOUNDARY_TERMS", raising=False)
    monkeypatch.setenv("MP_BOUNDARY_DIGESTS", "not-a-digest, deadbeef, ''")
    assert not sensitive_vocabulary_hit("any ordinary sentence at all")


def test_the_helper_refuses_a_term_on_the_command_line():
    """A term in argv is in the shell history and the process list before the
    program starts, which defeats the purpose of the tool."""
    import subprocess as sp
    script = pathlib.Path(__file__).resolve().parents[1] / "scripts/add_boundary_term.py"
    r = sp.run([sys.executable, str(script), "some-term"], capture_output=True, text=True)
    assert r.returncode == 2
    assert "shell history" in r.stderr


def test_the_helper_digest_matches_what_the_checker_looks_for(monkeypatch):
    """The tool is useless if its digest is not the one the matcher tests."""
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
    from add_boundary_term import digest
    monkeypatch.delenv("MP_BOUNDARY_TERMS", raising=False)
    monkeypatch.setenv("MP_BOUNDARY_DIGESTS", digest("Some Invented Phrase"))
    assert sensitive_vocabulary_hit("we mention some invented phrase here")
