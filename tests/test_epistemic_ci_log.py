"""The stated check count must match the checks actually named beside it.

EPISTEMIC-CI-LOG.md exists to stop local findings quietly failing to travel. It
has now failed at that twice -- it said "three" once and "four" once, each time
after a check had already shipped. The fix applied then was a note asking future
editors to keep the count current, which is a promise rather than a control.

This is the control. Purely local: it compares the number word against the check
names in the same sentence, so it fires on the realistic mistake -- adding a
check to the list and leaving the count, or the reverse. It deliberately does
NOT reach into epistemic-ci to count checks there: if nobody logs a new check,
its name is missing too and a cross-repo test would catch a strictly rarer case
at strictly higher cost.
"""

import re
import unittest
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "research/knowledge-ledger/EPISTEMIC-CI-LOG.md"
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
         "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}


class EpistemicCiLogTests(unittest.TestCase):
    def test_stated_count_matches_the_checks_named(self):
        text = LOG.read_text(encoding="utf-8")
        sentence = re.search(r"Its v0 has \*\*(\w+)\*\* checks(.+?)\n\n", text, re.S)
        self.assertIsNotNone(sentence, "the opening count sentence has moved or changed shape")
        stated = WORDS[sentence.group(1).lower()]
        named = len(re.findall(r"\*\*([A-Z][A-Za-z ]+)\*\*", sentence.group(2)))
        self.assertEqual(
            stated, named,
            f"EPISTEMIC-CI-LOG.md says {stated} checks but names {named}. "
            "Update both, or the log lags the thing it summarises again.",
        )


if __name__ == "__main__":
    unittest.main()
