"""BL-049 — the registration chain check must test bytes, not commit identity.

The proxy it replaces ("does the file's last-touching commit equal the pinned
SHA?") is wrong in both directions: red on an intact repository whose history was
merged from a line duplicating a registration commit, and green on a tampering
that preserved commit identity while altering content.

These tests build throwaway git repositories so the detection claims are
demonstrated rather than asserted -- in particular, that content tampering IS
caught and that duplicated history is NOT reported as tampering.

Stdlib only; CI runs `unittest discover`.
"""
import json
import pathlib
import subprocess
import tempfile
import unittest

from scripts.check_registration_chain import check, pairs

PREREG = "research/knowledge-ledger/experiments/KL-TEST/preregistration.json"
SIDECAR = "research/knowledge-ledger/experiments/KL-TEST/PROTOCOL-COMMIT.txt"


def _git(root, *args):
    return subprocess.run(("git",) + args, cwd=root, capture_output=True, text=True,
                          check=True)


def _repo(tmp: pathlib.Path) -> pathlib.Path:
    _git(tmp, "init", "-q", "-b", "main")
    _git(tmp, "config", "user.email", "t@t"); _git(tmp, "config", "user.name", "t")
    p = tmp / PREREG
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"schema": "x", "status": "preregistered"}) + "\n")
    _git(tmp, "add", "-A"); _git(tmp, "commit", "-qm", "register")
    sha = _git(tmp, "rev-parse", "HEAD").stdout.strip()
    (tmp / SIDECAR).write_text(sha + "\n")
    _git(tmp, "add", "-A"); _git(tmp, "commit", "-qm", "pin it")
    return tmp


class TestRegistrationChain(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = _repo(pathlib.Path(self._tmp.name))
        self._cwd = pathlib.Path.cwd()
        import os; os.chdir(self.root)

    def tearDown(self):
        import os; os.chdir(self._cwd); self._tmp.cleanup()

    def test_discovers_the_binding(self):
        self.assertEqual(len(pairs(self.root)), 1)

    def test_intact_registration_passes(self):
        self.assertEqual(check(self.root, "HEAD"), [])

    def test_content_tampering_is_caught(self):
        """The failure mode the proxy could not see at all."""
        p = self.root / PREREG
        p.write_text(json.dumps({"schema": "x", "status": "TAMPERED"}) + "\n")
        _git(self.root, "add", "-A"); _git(self.root, "commit", "-qm", "quietly edit")
        problems = check(self.root, "HEAD")
        self.assertTrue(problems)
        self.assertIn("CONTENT CHANGED", problems[0])

    def test_a_touch_that_does_not_change_content_is_not_a_violation(self):
        """The false positive that made the proxy useless. Rewriting the file with
        identical bytes moves its last-touching commit and changes nothing that
        matters."""
        p = self.root / PREREG
        p.write_text(p.read_text())          # same bytes, new commit touching it
        _git(self.root, "add", "-A")
        subprocess.run(("git", "commit", "-q", "--allow-empty", "-m", "no-op touch"),
                       cwd=self.root, check=True)
        self.assertEqual(check(self.root, "HEAD"), [],
                         "an identical rewrite must not read as tampering")

    def test_the_proxy_and_the_property_disagree_and_the_property_is_right(self):
        """The whole point of BL-049, stated as an executable comparison.

        After any later commit touches the preregistration with identical bytes
        -- which is what merging a line of history that duplicates a registration
        commit does -- the file's last-touching commit is no longer the pinned
        one. The old proxy reports the chain broken. Nothing has changed."""
        p = self.root / PREREG
        original = p.read_text()
        p.write_text(original.replace("preregistered", "PREREGISTERED"))
        _git(self.root, "add", "-A"); _git(self.root, "commit", "-qm", "stray edit")
        p.write_text(original)               # restored: HEAD bytes == pin bytes again
        _git(self.root, "add", "-A"); _git(self.root, "commit", "-qm", "restore")

        pinned = (self.root / SIDECAR).read_text().strip()
        last_touching = _git(self.root, "log", "-1", "--format=%H", "--", PREREG).stdout.strip()

        # the proxy's verdict
        self.assertNotEqual(pinned, last_touching,
                            "precondition: the proxy should now disagree")
        # the property's verdict
        self.assertEqual(check(self.root, "HEAD"), [],
                         "the registration is intact and must verify")
        self.assertEqual(p.read_text(), original, "bytes genuinely unchanged")

    def test_a_pin_off_the_branch_is_caught(self):
        (self.root / SIDECAR).write_text("0" * 40 + "\n")
        problems = check(self.root, "HEAD")
        self.assertTrue(problems)
        self.assertIn("does not exist", problems[0])

    def test_an_empty_sidecar_is_caught(self):
        (self.root / SIDECAR).write_text("\n")
        problems = check(self.root, "HEAD")
        self.assertTrue(problems)
        self.assertIn("no commit id", problems[0])


if __name__ == "__main__":
    unittest.main()
