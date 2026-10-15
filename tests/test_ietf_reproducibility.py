from scripts.check_ietf_reproducibility import normalized_html


def test_ignores_only_xml2rfc_generator_environment_banner():
    first = "<html>\n<!-- Generator version information:\n Python 3.12.14\n-->\n<body>same</body>"
    second = "<html>\n<!-- Generator version information:\n Python 3.12.15\n-->\n<body>same</body>"
    assert normalized_html(first) == normalized_html(second)


def test_preserves_substantive_draft_content():
    assert normalized_html("<body>allowed</body>") != normalized_html("<body>denied</body>")
