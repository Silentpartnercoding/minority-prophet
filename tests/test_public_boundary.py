from scripts.check_public_boundary import violations


def test_rejects_new_local_paths_and_strategy_language():
    lines = [
        ("README.md", 3, "/Users/example/private/project/output.json"),
        ("README.md", 4, "This is part of our shadow lane."),
    ]
    results = violations(lines)
    assert any("local user path" in result for result in results)
    assert any("internal strategy wording" in result for result in results)


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
