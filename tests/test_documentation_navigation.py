from __future__ import annotations

import importlib.util
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check_documentation_navigation.py"
SPEC = importlib.util.spec_from_file_location("check_documentation_navigation", SCRIPT)
assert SPEC and SPEC.loader
NAVIGATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(NAVIGATION)


def test_repository_navigation_is_complete() -> None:
    assert NAVIGATION.check(ROOT) == []


def test_checker_reports_broken_local_link(tmp_path: pathlib.Path) -> None:
    for relative in (*NAVIGATION.NAVIGATION_DOCUMENTS, *NAVIGATION.STABLE_ENTRY_POINTS):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# Placeholder\n", encoding="utf-8")

    readme = tmp_path / "README.md"
    required_links = "\n".join(
        f"[required]({destination})" for destination in NAVIGATION.README_DESTINATIONS
    )
    readme.write_text(f"# Front door\n\n{required_links}\n[broken](missing.md)\n", encoding="utf-8")

    assert "README.md: broken local link: missing.md" in NAVIGATION.check(tmp_path)
