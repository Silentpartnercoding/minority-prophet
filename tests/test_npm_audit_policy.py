from scripts.check_npm_audit import unexpected_advisories


def test_allows_only_the_recorded_braces_advisory_and_its_dependency_chain():
    report = {"vulnerabilities": {
        "braces": {"via": [{"url": "https://github.com/advisories/GHSA-vfj7-8cjw-p6xm"}]},
        "micromatch": {"via": ["braces"]},
        "consumer": {"via": ["micromatch"]},
    }}
    assert unexpected_advisories(report, {"GHSA-vfj7-8cjw-p6xm"}) == set()


def test_rejects_an_unlisted_advisory_hidden_behind_a_dependency():
    report = {"vulnerabilities": {
        "dependency": {"via": [{"url": "https://github.com/advisories/GHSA-new-risk"}]},
        "consumer": {"via": ["dependency"]},
    }}
    assert unexpected_advisories(report, {"GHSA-vfj7-8cjw-p6xm"}) == {"GHSA-new-risk"}


def test_rejects_an_advisory_without_a_github_identifier():
    report = {"vulnerabilities": {
        "dependency": {"via": [{"source": 1234, "name": "dependency", "url": "https://example.test/advisory"}]},
    }}
    assert unexpected_advisories(report, set()) == {"advisory-source:1234"}
