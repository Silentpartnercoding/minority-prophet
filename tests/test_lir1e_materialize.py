import json
import tempfile
import unittest
from pathlib import Path

from experiments.lir1.llm_echo.generate_cases import build
from experiments.lir1.llm_echo.materialize import materialize
from experiments.lir1.model import read_jsonl


class LIR1EMaterializeTests(unittest.TestCase):
    def test_materializes_exact_copy_and_six_mutations_per_case(self):
        requests, labels = build(bytes(range(32)), "development")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, rows in (("requests.jsonl", requests), ("labels.jsonl", labels)):
                (root / name).write_text("".join(json.dumps(row) + "\n" for row in rows))
            responses = []
            for index, request in enumerate(requests):
                label = next(row for row in labels if row["recordId"] == request["requestId"])
                responses.append({
                    "requestId": request["requestId"], "status": "valid", "model": request["modelSlot"],
                    "completedAt": f"2026-01-01T00:{index // 60:02d}:{index % 60:02d}Z",
                    "rawResponse": json.dumps({"answer": label["expectedAnswer"], "confidence": 1, "explanation": "Source packet states the token."}),
                })
            (root / "responses.jsonl").write_text("".join(json.dumps(row) + "\n" for row in responses))
            summary = materialize(root / "requests.jsonl", root / "responses.jsonl", root / "labels.jsonl", root / "out")
            claims = read_jsonl(root / "out/claims.jsonl")
            self.assertEqual(summary["claimCount"], 144)
            copies = [row for row in claims if row.independence_label == "copy"]
            mutations = [row for row in claims if row.independence_label == "mutated_copy"]
            self.assertEqual((len(copies), len(mutations)), (12, 72))
            self.assertTrue(all(row.observed_parents for row in copies + mutations))


if __name__ == "__main__":
    unittest.main()
