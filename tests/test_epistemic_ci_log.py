"""The stated check count must match epistemic-ci, not merely itself.

EPISTEMIC-CI-LOG.md exists to stop local findings quietly failing to travel. It
has stated the wrong number three times.

The first version of this test compared the number word against the check names
in the same sentence. That cannot catch the failure that actually recurs: when
both go stale together they stay internally consistent and the test passes. It
missed the count being five while upstream had eight.

The reasoning behind that version was also wrong. A cross-repository check was
rejected as catching "a strictly rarer case at strictly higher cost". That case
is not rarer -- it is the only one that has ever occurred here. So the authority
is now upstream, with the local consistency check kept as a cheap first pass.

A third failure mode is guarded separately: an entry left under a "proposed" or
"awaiting review" heading after its pull request merged. That happened after #13
merged and neither count test caught it, because the count did not change. It is
an observed failure rather than an invented one, so it gets a control.

Network failures SKIP rather than fail: an offline run must not be a false red.
"""

import json
import re
import unittest
import urllib.error
import urllib.request
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "research/knowledge-ledger/EPISTEMIC-CI-LOG.md"
API = ("https://api.github.com/repos/Silentpartnercoding/epistemic-ci"
       "/contents/epistemic_ci/core.py")
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
         "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def stated_count() -> tuple[int, int]:
    """(number the log states, number of checks it names in the same sentence)."""
    text = LOG.read_text(encoding="utf-8")
    sentence = re.search(r"Its v0 has \*\*(\w+)\*\* checks(.+?)\n\n", text, re.S)
    assert sentence, "the opening count sentence has moved or changed shape"
    # \s not " ": markdown reflows, and a bold name split across two lines
    # ("**Executable\nPass Condition**") is still one name. The first version of
    # this test used " " and silently undercounted six of eight.
    named = len(re.findall(r"\*\*([A-Z][A-Za-z\s]+?)\*\*", sentence.group(2), re.S))
    return WORDS[sentence.group(1).lower()], named


PENDING_HEADINGS = ("proposed", "awaiting", "not proposed", "deliberately not")


def entries_by_heading() -> list[tuple[str, int]]:
    """(current heading, referenced PR number) for every epistemic-ci PR link."""
    found: list[tuple[str, int]] = []
    heading = ""
    for line in LOG.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            heading = line.lstrip("# ").strip()
        for number in re.findall(r"epistemic-ci/pull/(\d+)", line):
            found.append((heading, int(number)))
    return found


class EpistemicCiLogTests(unittest.TestCase):
    def test_stated_count_matches_the_checks_named(self):
        """Cheap first pass: the sentence must agree with itself."""
        stated, named = stated_count()
        self.assertEqual(stated, named,
                         f"log says {stated} checks but names {named}")

    def test_stated_count_matches_epistemic_ci(self):
        """The authority is upstream. Skips offline rather than failing."""
        request = urllib.request.Request(
            API, headers={"Accept": "application/vnd.github.raw",
                          "User-Agent": "minority-prophet-log-check"})
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                source = response.read().decode("utf-8")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            self.skipTest(f"epistemic-ci unreachable ({exc}); offline is not a false red")

        upstream = len(re.findall(r"^def check_\w+\(", source, re.M))
        self.assertGreater(upstream, 0, "found no checks upstream; the parse has drifted")
        stated, _ = stated_count()
        self.assertEqual(
            stated, upstream,
            f"EPISTEMIC-CI-LOG.md states {stated} checks; epistemic-ci defines "
            f"{upstream}. The log has lagged upstream three times -- update it, "
            "including which entries moved from proposed to merged.",
        )


    def test_merged_prs_are_not_filed_as_still_pending(self):
        """An entry under "proposed" or "awaiting review" whose PR has merged.

        Observed after #13 merged. Neither count test catches it, because the
        count does not change -- so the log can be simultaneously correct about
        how many checks exist and wrong about which ones are still open.
        """
        entries = entries_by_heading()
        self.assertTrue(entries, "no epistemic-ci PR links found; the parse has drifted")

        stale = []
        for heading, number in entries:
            if not any(word in heading.lower() for word in PENDING_HEADINGS):
                continue
            request = urllib.request.Request(
                f"https://api.github.com/repos/Silentpartnercoding/epistemic-ci/pulls/{number}",
                headers={"Accept": "application/vnd.github+json",
                         "User-Agent": "minority-prophet-log-check"})
            try:
                with urllib.request.urlopen(request, timeout=15) as response:
                    payload = json.load(response)
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                self.skipTest(f"epistemic-ci unreachable ({exc}); offline is not a false red")
            if payload.get("merged_at"):
                stale.append(f"#{number} merged but filed under {heading!r}")

        self.assertEqual(
            stale, [],
            "entries describe merged work as still pending: " + "; ".join(stale),
        )


if __name__ == "__main__":
    unittest.main()
