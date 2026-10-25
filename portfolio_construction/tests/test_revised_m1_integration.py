"""M2 revised funding contract checks based on committed 2022-information-set inputs.

Observed 2023-2025 data are deliberately absent from these tests.
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
MOD=ROOT/"portfolio_construction"/"revised_mandate"/"m1_integration.py"
spec=importlib.util.spec_from_file_location("m1_integration",MOD)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class M1ToM2ContractTests(unittest.TestCase):
    def test_revised_m1_funding_cash_ledger(self):
        s=m.load_funding()
        self.assertEqual(set(s),{"Revised M1 Principal matching","Revised M1 Coupon funding"})
        p=s["Revised M1 Principal matching"]
        c=s["Revised M1 Coupon funding"]
        self.assertAlmostEqual(p["cost"],5784228,places=4)
        self.assertAlmostEqual(c["cost"],5429776.178571429,places=4)
        self.assertAlmostEqual(p["cash"],564000,places=4)
        self.assertAlmostEqual(c["cash"],168000,places=4)
        self.assertAlmostEqual(c["units"]["Gamma"],846.4285714285714,places=7)
        self.assertAlmostEqual(c["ledger"][2]["closing_cash"],0,places=4)

    def test_2022_estimation_and_exact_frozen_weights(self):
        panel,w=m.load_estimation()
        self.assertEqual(len(panel),96)
        self.assertEqual(panel.month.iloc[0],"2015-01")
        self.assertEqual(panel.month.iloc[-1],"2022-12")
        self.assertAlmostEqual(w.sum(),1,places=9)

    def test_run_all_m1_cases_and_m3_static_returns(self):
        with tempfile.TemporaryDirectory() as d:
            summary=m.run(d)
            self.assertEqual(len(summary),3)
            rows=pd.read_csv(Path(d)/"portfolio_comparison.csv")
            weights=pd.read_csv(Path(d)/"exact_allocations.csv")
            series=pd.read_csv(Path(d)/"growth_static_returns_2015_2022.csv")
            stress=pd.read_csv(Path(d)/"combined_stress.csv")
            self.assertEqual(len(rows),15)
            self.assertEqual(len(weights),15*12)
            self.assertEqual(series.shape,(96,16))
            self.assertEqual(len(stress),8)
            for (sc,po),g in weights.groupby(["scenario","policy"]):
                self.assertAlmostEqual(g.exact_weight.sum(),1,places=7)
                self.assertTrue(np.isfinite(g.exact_purchase_USD).all())
            self.assertEqual(summary.scenario.tolist()[0],"Original frozen")
            self.assertGreater(summary.required_2030_equity_CAGR.iloc[1],summary.required_2030_equity_CAGR.iloc[0])
            self.assertLess(summary.required_2030_equity_CAGR.iloc[2],summary.required_2030_equity_CAGR.iloc[1])

    def test_mutated_post_cutoff_month_rejected(self):
        x=pd.read_csv(m.RETURNS)
        x.loc[x.index[-1],"month"]="2023-01"
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/"invalid.csv"; x.to_csv(file,index=False)
            with self.assertRaises(ValueError):
                m.load_estimation(returns=file)

    def test_adversarial_m1_holdings_rejected(self):
        import shutil
        with tempfile.TemporaryDirectory() as d:
            source=m.M1_PATH
            for name in ("revised_holdings.csv","revised_funding_summary.csv"):
                shutil.copy2(source/name,Path(d)/name)
            p=Path(d)/"revised_funding_summary.csv"
            p.write_text(p.read_text().replace("5429776.178571429","5429777.178571429"))
            with self.assertRaises(AssertionError):
                m.load_funding(d)

if __name__=="__main__":
    unittest.main()
