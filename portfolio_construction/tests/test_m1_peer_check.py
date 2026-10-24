"""Independent Member 2 audit of M1's published coupon and principal ledgers."""
import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"portfolio_construction/revised_mandate"
sys.path.insert(0,str(SRC))
spec=importlib.util.spec_from_file_location("m1_peer_check",SRC/"m1_peer_check.py")
checker=importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

class M1PeerCheckTests(unittest.TestCase):
    def test_all_112_cashflow_cells_match_within_one_cent(self):
        with tempfile.TemporaryDirectory() as d:
            result=checker.check(Path(d)/"check.csv")
            self.assertEqual(len(result),112)
            self.assertTrue(result.pass_at_1_cent.all())
            self.assertLess(result.discrepancy_USD.abs().max(),0.01)
            self.assertEqual(set(result.year),set(range(2023,2031)))

    def test_tampered_m1_cash_ledger_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            names=("revised_holdings.csv","revised_funding_summary.csv",
                   "principal_matching_ledger.csv","coupon_funding_ledger.csv")
            for name in names:
                shutil.copy2(checker.M1_PATH/name,Path(d)/name)
            p=Path(d)/"coupon_funding_ledger.csv"
            text=p.read_text()
            original="117857.14285714286"
            self.assertIn(original,text)
            p.write_text(text.replace(original,"117858.14285714286",1))
            with self.assertRaises(AssertionError):
                checker.check(Path(d)/"audit.csv",m1=d)

if __name__=="__main__":
    unittest.main()
