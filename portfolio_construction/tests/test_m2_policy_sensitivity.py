"""Revised full-fund mandate sensitivity gates, static 2022 inputs only."""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
MODROOT=ROOT/"portfolio_construction"/"revised_mandate"
sys.path.insert(0,str(MODROOT))
P=importlib.util.spec_from_file_location("policy_sensitivity",MODROOT/"policy_sensitivity.py")
sens=importlib.util.module_from_spec(P);P.loader.exec_module(sens)
M=importlib.util.spec_from_file_location("m1_integration",MODROOT/"m1_integration.py")
m2=importlib.util.module_from_spec(M);M.loader.exec_module(m2)

class SensitivityAcceptanceTests(unittest.TestCase):
    def test_full_inflation_buffer_grid_and_reconciliation(self):
        with tempfile.TemporaryDirectory() as d:
            x=sens.build(Path(d)/"sensitivity.csv")
            self.assertEqual(len(x),36)
            self.assertEqual(x.scenario.nunique(),3)
            self.assertTrue(np.allclose(x.initial_capital_reconciliation_USD,12_000_000,atol=1e-6,rtol=0))
            self.assertEqual(set(x.inflation),{.02,.023,.03,.04})
            self.assertEqual(set(x.initial_operating_buffer_USD),{0.,250000.,500000.})

    def test_base_reproduces_m1_hurdle_numbers(self):
        with tempfile.TemporaryDirectory() as d:
            x=sens.build(Path(d)/"sensitivity.csv")
            y=x[(x.inflation==0.023)&(x.initial_operating_buffer_USD==0)].set_index("scenario")
            self.assertAlmostEqual(y.loc["Original frozen","required_8yr_equity_CAGR"],0.046576658312956543,places=10)
            self.assertAlmostEqual(y.loc["Revised M1 Principal matching","required_8yr_equity_CAGR"],0.04795107162727974,places=10)
            self.assertAlmostEqual(y.loc["Revised M1 Coupon funding","required_8yr_equity_CAGR"],0.04630860914613377,places=10)

    def test_required_cagr_increases_with_inflation(self):
        with tempfile.TemporaryDirectory() as d:
            x=sens.build(Path(d)/"sensitivity.csv")
            for _,g in x.groupby(["scenario","initial_operating_buffer_USD"]):
                ordered=g.sort_values("inflation").required_8yr_equity_CAGR.to_numpy()
                self.assertTrue((np.diff(ordered)>0).all())

    def test_net_equity_falls_as_cash_buffer_rises(self):
        with tempfile.TemporaryDirectory() as d:
            x=sens.build(Path(d)/"sensitivity.csv")
            for _,g in x.groupby(["scenario","inflation"]):
                ordered=g.sort_values("initial_operating_buffer_USD").net_equity_investment_USD.to_numpy()
                self.assertTrue((np.diff(ordered)<0).all())

    def test_common_risk_comparison_and_weight_constraints(self):
        with tempfile.TemporaryDirectory() as d:
            m2.run(d)
            p=pd.read_csv(Path(d)/"portfolio_comparison.csv")
            x=pd.read_csv(Path(d)/"exact_allocations.csv")
            self.assertEqual(len(p),15)
            self.assertTrue(np.allclose(p.annual_volatility,p.annual_volatility_sample_covariance))
            self.assertTrue((p.annual_volatility_single_index_covariance>0).all())
            for (sc,pol),g in x.groupby(["scenario","policy"]):
                w=g.set_index("ticker").exact_weight.reindex(m2.ASSETS).to_numpy(float)
                self.assertAlmostEqual(w.sum(),1,places=7)
                self.assertTrue((w>=-1e-8).all())
                self.assertTrue((w[:10]<=.15+1e-7).all())
                self.assertTrue((w[10:]<=.30+1e-7).all())
                self.assertLessEqual(w[10:].sum(),.40+1e-7)
                for inds in m2.constraints()[1]:
                    if inds["type"]=="ineq":
                        self.assertGreaterEqual(inds["fun"](w),-1e-7)

    def test_mandate_funding_equity_method_attribution_identity(self):
        import importlib.util
        with tempfile.TemporaryDirectory() as d:
            path=ROOT/"portfolio_construction/revised_mandate/mandate_decomposition.py"
            spec=importlib.util.spec_from_file_location("mandate_decomposition",path)
            mod=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            delta=mod.build(Path(d)/"bridge.csv")
            self.assertEqual(len(delta),4)
            self.assertAlmostEqual(delta.incremental_utility.iloc[0],0.,places=12)
            self.assertAlmostEqual(delta.incremental_utility.sum(),
                                   delta.cumulative_utility.iloc[-1]-delta.cumulative_utility.iloc[0],places=12)
            self.assertIn("MANDATE ONLY UNDER PRINCIPAL MATCHING",delta.change_class.tolist())
            self.assertIn("FUNDING METHOD CHANGE",delta.change_class.tolist())
            self.assertIn("EQUITY METHOD CHANGE",delta.change_class.tolist())

if __name__=="__main__":
    unittest.main()
