"""Pre-freeze document integrity checks; no post-2022 market data used."""
import csv
import hashlib
import unittest
from pathlib import Path

from docx import Document

BASE=Path(__file__).resolve().parents[1]
TOP=BASE.parent
FROZEN_WEIGHTS_HASH="a15469f1478370e2d9399cae8ab7aae215545fe2e040d02435bdc3ea7d10672d"

class InitialRecordConsistencyTests(unittest.TestCase):
    def test_original_weights_unchanged(self):
        got=hashlib.sha256((BASE/'evidence/decision_weights_confirmed.csv').read_bytes()).hexdigest()
        self.assertEqual(got, FROZEN_WEIGHTS_HASH)

    def test_student_facing_document_no_named_future_action(self):
        doc=Document(BASE/'docs/Kappa_Initial_Decision_Record.docx')
        content=' '.join(x.text for x in doc.paragraphs)
        self.assertNotIn('Kenvue',content)
        self.assertNotIn('2023 JNJ',content)
        self.assertIn('Do not make discretionary trades',content)
        self.assertIn('do not elect voluntary tender or exchange offers',content)
        self.assertIn('do not count dividends twice',content)
        self.assertIn('actual share counts may rise',content)
        self.assertIn('22 October submission',content)

    def test_pdf_copies_identical(self):
        self.assertEqual(hashlib.sha256((BASE/'docs/Kappa_Initial_Decision_Record.pdf').read_bytes()).hexdigest(),
                         '92a32e52ccc5c46095f2b8a6e6af2e0f2ef953909a7c2c6575614fa3c46ec8e8')

    def test_source_window_unchanged(self):
        p=BASE/'data/processed/asset_monthly_returns_estimation.csv'
        import pandas as pd
        x=pd.read_csv(p)
        self.assertEqual(len(x),96)
        self.assertFalse(any('2023' in str(v) for v in x.iloc[:,0]))

if __name__=='__main__': unittest.main()
