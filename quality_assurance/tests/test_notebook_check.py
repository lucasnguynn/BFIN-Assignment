"""Unit tests for the notebook-execution gate (synthetic notebooks only)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from quality_assurance import checks  # noqa: E402


def write_nb(path, cells):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"cells": cells, "metadata": {}, "nbformat": 4, "nbformat_minor": 5}))


def code_cell(count, outputs):
    return {"cell_type": "code", "source": ["1+1"], "execution_count": count, "outputs": outputs, "metadata": {}}


class NotebookGate(unittest.TestCase):
    def run_gate(self, cells):
        with tempfile.TemporaryDirectory() as t:
            write_nb(Path(t) / "n.ipynb", cells)
            return checks.check_notebooks(t, ["n.ipynb"])[0]["status"]

    def test_executed_notebook_passes(self):
        out = [{"output_type": "stream", "name": "stdout", "text": "2\n"}]
        self.assertEqual(self.run_gate([code_cell(1, out), {"cell_type": "markdown", "source": ["x"], "metadata": {}}]), "PASS")

    def test_unexecuted_cell_fails(self):
        self.assertEqual(self.run_gate([code_cell(None, [])]), "FAIL")

    def test_error_output_fails(self):
        err = [{"output_type": "error", "ename": "Error", "evalue": "x", "traceback": []}]
        self.assertEqual(self.run_gate([code_cell(1, err)]), "FAIL")

    def test_missing_notebook_fails(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(checks.check_notebooks(t, ["missing.ipynb"])[0]["status"], "FAIL")


class DeliveredNotebooks(unittest.TestCase):
    def test_repository_notebooks_are_executed(self):
        for r in checks.check_notebooks(ROOT):
            self.assertEqual(r["status"], "PASS", r["detail"])


if __name__ == "__main__":
    unittest.main()
