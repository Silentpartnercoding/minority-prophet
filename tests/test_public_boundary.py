import hashlib

from scripts.check_public_boundary import violations, sensitive_vocabulary_hit


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
