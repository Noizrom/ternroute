from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.contracts import Result, Task, load_tasks, write_results_atomic
from app.errors import ContractError


class ContractTests(unittest.TestCase):
    def test_round_trip_preserves_ids_order_and_unicode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "input" / "tasks.json"
            output_path = root / "output" / "results.json"
            input_path.parent.mkdir()
            input_path.write_text(
                json.dumps(
                    [
                        {"task_id": "α", "prompt": "First task"},
                        {"task_id": "2", "prompt": "Second task"},
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            tasks = load_tasks(input_path)
            results = [
                Result(task_id="α", answer="One"),
                Result(task_id="2", answer="Two"),
            ]
            write_results_atomic(output_path, tasks, results)

            self.assertEqual(
                json.loads(output_path.read_text(encoding="utf-8")),
                [
                    {"task_id": "α", "answer": "One"},
                    {"task_id": "2", "answer": "Two"},
                ],
            )
            self.assertFalse((output_path.parent / "results.json.tmp").exists())

    def test_empty_array_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.json"
            path.write_text("[]", encoding="utf-8")
            self.assertEqual(load_tasks(path), [])

    def test_duplicate_ids_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.json"
            path.write_text(
                '[{"task_id":"x","prompt":"a"},{"task_id":"x","prompt":"b"}]',
                encoding="utf-8",
            )
            with self.assertRaises(ContractError):
                load_tasks(path)

    def test_non_string_id_is_rejected_without_coercion(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.json"
            path.write_text('[{"task_id":1,"prompt":"a"}]', encoding="utf-8")
            with self.assertRaises(ContractError):
                load_tasks(path)

    def test_result_order_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tasks = [Task(task_id="a", prompt="one"), Task(task_id="b", prompt="two")]
            results = [Result(task_id="b", answer="x"), Result(task_id="a", answer="y")]
            with self.assertRaises(ContractError):
                write_results_atomic(Path(directory) / "results.json", tasks, results)


if __name__ == "__main__":
    unittest.main()
