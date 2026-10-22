"""Pre-freeze document integrity checks; no post-2022 market data used."""
import hashlib
import re
import unittest
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

BASE = Path(__file__).resolve().parents[1]
PDF_PATH = BASE / "docs" / "Kappa Foundation- Initial Decision.pdf"
FROZEN_WEIGHTS_HASH = "92a32e52ccc5c46095f2b8a6e6af2e0f2ef953909a7c2c6575614fa3c46ec8e8"


def pdf_text(path):
    """All page text of the PDF with whitespace collapsed (line breaks do not matter)."""
    reader = PdfReader(str(path))
    return re.sub(r"\s+", " ", " ".join(page.extract_text() or "" for page in reader.pages))


class InitialRecordConsistencyTests(unittest.TestCase):
    def test_original_weights_unchanged(self):
        got = hashlib.sha256((BASE / "evidence/decision_weights_confirmed.csv").read_bytes()).hexdigest()
        self.assertEqual(got, FROZEN_WEIGHTS_HASH)

    def test_source_window_unchanged(self):
        x = pd.read_csv(BASE / "data/processed/asset_monthly_returns_estimation.csv")
        self.assertEqual(len(x), 96)
        self.assertFalse(any("2023" in str(v) for v in x.iloc[:, 0]))

    def test_decision_record_is_two_pages(self):
        self.assertEqual(len(PdfReader(str(PDF_PATH)).pages), 2)

    def test_decision_record_states_frozen_rules(self):
        text = pdf_text(PDF_PATH)
        for phrase in [
            "No discretionary trading",
            "no voluntary tender or exchange elections",
            "adjusted-close total-return proxies",
            "fractional equity purchases",
            "22 October",
            "Sample Mean-Variance",
            "VTI",
        ]:
            self.assertIn(phrase, text)

    def test_decision_record_names_no_future_action(self):
        text = pdf_text(PDF_PATH)
        self.assertNotIn("Kenvue", text)
        self.assertNotIn("2023 JNJ", text)


if __name__ == "__main__":
    unittest.main()
