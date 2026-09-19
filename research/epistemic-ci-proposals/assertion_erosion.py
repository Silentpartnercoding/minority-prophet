"""Proposed Epistemic CI check: ASSERTION EROSION.

**Failure mode.** A test fails. The test is edited until it passes. The
codebase's guarantees shrink, and the suite stays green, and nothing anywhere
records that a promise was withdrawn.

**Why the existing ten miss it.** Every current check evaluates a suite as it
stands: whether a test can fail, whether a control discriminates, whether an
artifact is bound. All of them are single-snapshot. Erosion is only visible
*between* snapshots -- a weakened assertion is perfectly healthy on its own
terms, and would pass Vacuous Test, Control Discrimination and the rest without
complaint. What makes it a defect is that it used to say more.

**What this check cannot do.** It cannot tell a correction from a convenience.
Sometimes a test is genuinely wrong and weakening it is the honest repair; this
module produced exactly that case in its own repository on 2026-09-08, when
three assertions about a bond reference were loosened because the rule they
encoded was mistaken. No static analysis distinguishes that from laziness.

It is therefore **not a gate**. It is a flag: it guarantees that a human is
asked, and that the answer is written down somewhere an outsider can read it.
The gain is not detection -- it is denying anyone the ability to weaken a
guarantee without noticing they did.

**Trivially evadable**, and stated as such: split the change across two commits
and this sees nothing. It is a speed bump against drift, not a wall against
intent. Drift is the common failure; intent is the rare one.
"""

from __future__ import annotations

import ast
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field

#: How much an assertion promises. Deleting one drops it to zero.
#: Ranked by how many ways the assertion can fail: an exact match is violated by
#: any difference, while a truthiness check survives most of them.
ASSERTION_STRENGTH: dict[str, int] = {
    "assertEqual": 3, "assertNotEqual": 3, "assertIs": 3, "assertIsNot": 3,
    "assertRaises": 3, "assertRaisesRegex": 3, "assertSetEqual": 3,
    "assertDictEqual": 3, "assertListEqual": 3, "assertSequenceEqual": 3,
    "assertIn": 2, "assertNotIn": 2, "assertAlmostEqual": 2,
    "assertGreater": 2, "assertLess": 2, "assertIsInstance": 2,
    "assertGreaterEqual": 1, "assertLessEqual": 1,
    "assertTrue": 1, "assertFalse": 1,
    "assertIsNone": 1, "assertIsNotNone": 1,
}


@dataclass(frozen=True)
class Assertion:
    test: str
    method: str

    @property
    def strength(self) -> int:
        return ASSERTION_STRENGTH.get(self.method, 1)


@dataclass
class ErosionReport:
    removed: list[Assertion] = field(default_factory=list)
    weakened: list[tuple[str, str, str]] = field(default_factory=list)
    added: list[Assertion] = field(default_factory=list)
    tests_removed: list[str] = field(default_factory=list)
    covered_module_changed: bool = False

    @property
    def eroded(self) -> bool:
        return bool(self.removed or self.weakened or self.tests_removed)

    @property
    def needs_review(self) -> bool:
        """Erosion alongside a change to the code under test.

        Either alone is ordinary. Together is the shape of a test edited to
        accommodate the change rather than to judge it.
        """
        return self.eroded and self.covered_module_changed

    def summary(self) -> str:
        if not self.eroded:
            return "no assertion erosion"
        parts = []
        if self.tests_removed:
            parts.append(f"{len(self.tests_removed)} test(s) removed")
        if self.removed:
            parts.append(f"{len(self.removed)} assertion(s) removed")
        if self.weakened:
            parts.append(f"{len(self.weakened)} assertion(s) weakened")
        tail = (" alongside a change to the module under test -- correction or "
                "convenience?" if self.covered_module_changed else "")
        return ", ".join(parts) + tail


def _assertions(source: str) -> dict[str, list[str]]:
    """Assertion method names per test function. Order is preserved."""
    out: dict[str, list[str]] = {}
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return out
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test"):
            continue
        found: list[str] = []
        for inner in ast.walk(node):
            if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute):
                if inner.func.attr.startswith("assert"):
                    found.append(inner.func.attr)
            elif isinstance(inner, ast.With):
                for item in inner.items:
                    call = item.context_expr
                    if (isinstance(call, ast.Call)
                            and isinstance(call.func, ast.Attribute)
                            and call.func.attr.startswith("assert")):
                        found.append(call.func.attr)
            elif isinstance(inner, ast.Assert):
                found.append("assert")
        out[node.name] = found
    return out


def check_assertion_erosion(before: str, after: str, *,
                            covered_module_changed: bool = False) -> ErosionReport:
    """Compare two versions of a test file for weakened guarantees.

    Positional comparison within each test: the nth assertion before against the
    nth after. Crude, and it will report noise on a genuine restructure -- which
    is acceptable for a flag and would not be for a gate.
    """
    old, new = _assertions(before), _assertions(after)
    report = ErosionReport(covered_module_changed=covered_module_changed)

    for test, old_calls in old.items():
        if test not in new:
            report.tests_removed.append(test)
            report.removed.extend(Assertion(test, m) for m in old_calls)
            continue
        new_calls = new[test]
        for index, method in enumerate(old_calls):
            if index >= len(new_calls):
                report.removed.append(Assertion(test, method))
                continue
            replacement = new_calls[index]
            if replacement == method:
                continue
            before_strength = ASSERTION_STRENGTH.get(method, 1)
            after_strength = ASSERTION_STRENGTH.get(replacement, 1)
            if after_strength < before_strength:
                report.weakened.append((test, method, replacement))

    for test, new_calls in new.items():
        if test not in old:
            report.added.extend(Assertion(test, m) for m in new_calls)

    return report


#: Modules that ship with Python. A test importing these says nothing about
#: which code it covers, and including them would make every test look as though
#: it covered the standard library.
_STDLIB = frozenset(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else frozenset()


def covered_modules(test_source: str, *, roots: Iterable[str] = ()) -> set[str]:
    """First-party modules a test file imports, as repository-relative paths.

    `covered_module_changed` is the input `needs_review` turns on, and nothing
    derived it -- the property that separates a correction from a convenience
    depended on a boolean no caller was shown how to produce. This derives the
    CANDIDATES from the test's own imports.

    It deliberately stops there. Whether one of these actually changed is a
    question about a diff, which this module cannot see and should not guess at:
    inferring it would be the static analysis the proposal disclaims. The caller
    holds the diff; this names what to look for in it.

    `roots` limits the result to first-party top-level packages when given. Left
    empty, anything outside the standard library counts, which over-reports
    third-party imports rather than silently dropping a real one.
    """
    try:
        tree = ast.parse(test_source)
    except SyntaxError:
        return set()

    allowed = tuple(roots)
    found: set[str] = set()
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.ImportFrom):
            if node.level:          # relative import: no dotted path to resolve
                continue
            if node.module:
                names.append(node.module)
        elif isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        for name in names:
            top = name.split(".", 1)[0]
            if top in _STDLIB:
                continue
            if allowed and top not in allowed:
                continue
            found.add(name.replace(".", "/") + ".py")
    return found


def module_changed(test_source: str, changed_paths: Iterable[str], *,
                   roots: Iterable[str] = ()) -> bool:
    """Whether any module this test covers appears in `changed_paths`.

    The caller supplies what changed -- from a diff, a commit, a CI event. This
    only answers whether the overlap is non-empty, so the judgement stays where
    the evidence is.
    """
    covered = covered_modules(test_source, roots=roots)
    changed = {str(path).lstrip("./") for path in changed_paths}
    return bool(covered & changed)
