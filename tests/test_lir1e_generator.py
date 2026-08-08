import json
import tempfile
import unittest
from pathlib import Path

from experiments.lir1.llm_echo.generate_cases import (
    COUNTS,
    PRIVATE_KEYS,
    assert_boundary,
    build,
    prepare,
)


class LIR1EGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.seed = bytes(range(32))

    def test_frozen_counts_and_false_majority_shape(self):
        requests, labels = build(self.seed, "development")
        self.assertEqual(len(requests), COUNTS["development"] * 5)
        self.assertEqual(len(labels), COUNTS["development"] * 12)
        for case_number in range(COUNTS["development"]):
            case_id = requests[case_number * 5]["caseId"]
            case_labels = [row for row in labels if row["caseId"] == case_id]
            false_rows = [row for row in case_labels if row["sourcePolarity"] == "constructed-false"]
            true_rows = [row for row in case_labels if row["sourcePolarity"] == "constructed-true"]
            self.assertEqual((len(false_rows), len(true_rows)), (9, 3))
            self.assertEqual(len({row["trueRootId"] for row in case_labels}), 4)

    def test_same_source_and_disjoint_cells_are_structural(self):
        requests, _ = build(self.seed, "development")
        for case_id in {row["caseId"] for row in requests}:
            rows = [row for row in requests if row["caseId"] == case_id]
            shared = [row for row in rows if row["assignmentCell"] == "same_model_same_source"]
            disjoint = [row for row in rows if "disjoint" in row["assignmentCell"]]
            self.assertEqual(len({row["sourceSha256"] for row in shared}), 1)
            self.assertEqual(len({row["sourceSha256"] for row in disjoint}), 3)
            self.assertFalse({row["sourceSha256"] for row in shared} & {row["sourceSha256"] for row in disjoint})

    def test_public_requests_exclude_label_fields(self):
        requests, labels = build(self.seed, "development")
        assert_boundary(requests, labels)
        public = "\n".join(json.dumps(row, sort_keys=True) for row in requests)
        for key in PRIVATE_KEYS:
            self.assertNotIn(f'"{key}"', public)

    def test_generation_is_byte_deterministic_and_seed_sensitive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first_seed = root / "first.seed"
            second_seed = root / "second.seed"
            first_seed.write_bytes(self.seed)
            second_seed.write_bytes(b"z" * 32)
            first = prepare(first_seed, "development", root / "first")
            repeat = prepare(first_seed, "development", root / "repeat")
            second = prepare(second_seed, "development", root / "second")
            self.assertEqual(first["files"], repeat["files"])
            self.assertNotEqual(first["files"], second["files"])

    def test_wrong_case_count_and_short_seed_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "frozen at 12"):
            build(self.seed, "development", count=11)
        with self.assertRaisesRegex(ValueError, "at least 32"):
            build(b"short", "development")


if __name__ == "__main__":
    unittest.main()
