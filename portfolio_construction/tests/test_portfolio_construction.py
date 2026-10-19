import unittest,sys,hashlib,io,zipfile,pandas as pd,numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT))
from portfolio_utils import ASSETS,MARKET,PURCHASE,GROWTH_BUDGET,ENTRY_COST,F,BOND_COST,parameters,optimize
from rebuild import EXPECTED_ARCHIVE,EXPECTED_WORKBOOK

class PortfolioConstructionChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.returns=pd.read_csv(ROOT/'data/processed/asset_monthly_returns_estimation.csv')
        cls.mu,cls.S,cls.SI,cls.beta,cls.res=parameters(cls.returns)
    def test_source_manifest_archive(self):
        b=(ROOT/'data/raw/yfinance_estimation_2015_2022.zip').read_bytes()
        self.assertEqual(hashlib.sha256(b).hexdigest(),EXPECTED_ARCHIVE)
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            m=pd.read_csv(io.BytesIO(z.read('data/source_manifest.csv')))
            self.assertEqual(len(m),13)
            for row in m.itertuples(index=False):
                self.assertEqual(hashlib.sha256(z.read(row.raw_filepath)).hexdigest(),row.file_sha256)
    def test_funding_workbook_unchanged(self):
        self.assertEqual(hashlib.sha256((ROOT/'evidence/bond_funding_model_pinned.xlsx').read_bytes()).hexdigest(),EXPECTED_WORKBOOK)
    def test_estimation_window_and_no_future(self):
        r=self.returns
        self.assertEqual(r.shape,(96,14))
        self.assertEqual(r.month.iloc[0],'2015-01')
        self.assertEqual(r.month.iloc[-1],'2022-12')
        self.assertFalse(r.isna().any().any())
    def test_fee_budget_identity(self):
        self.assertAlmostEqual(BOND_COST+GROWTH_BUDGET,12_000_000,6)
        self.assertAlmostEqual(PURCHASE*(1+ENTRY_COST),GROWTH_BUDGET,6)
    def test_optimizer_cap_and_source_weights(self):
        x=optimize(self.mu,self.S,3)
        source=pd.read_csv(ROOT/'evidence/decision_weights_confirmed.csv').set_index('security').loc[ASSETS]['weight_of_growth_sleeve'].to_numpy(float)
        self.assertLess(np.max(np.abs(x-source)),1e-7)
        self.assertAlmostEqual(sum(x),1,8)
        self.assertLessEqual(max(x[:10]),.1500001)
        self.assertLessEqual(sum(x[10:]),.4000001)
        self.assertLessEqual(x[0]+x[1],.3000001)
    def test_same_caps_model_challengers(self):
        mv=optimize(self.mu,self.S,3)
        si=optimize(self.mu,self.SI,3)
        mn=optimize(self.mu,self.S,3,minvar=True)
        util=lambda w:F*(w@self.mu)-1.5*F**2*(w@self.S@w)
        self.assertGreaterEqual(util(mv)+1e-9,util(si))
        self.assertGreaterEqual(util(mv)+1e-9,util(mn))
        self.assertLess(mn@self.S@mn,mv@self.S@mv)
    def test_reversal_thresholds(self):
        x=pd.read_csv(ROOT/'outputs/fixed_weight_reversal.csv')
        self.assertAlmostEqual(float(x.threshold.iloc[0]),.08417,delta=.001)
        self.assertAlmostEqual(float(x.threshold.iloc[1]),8.91,delta=.1)
    def test_stress_and_hurdle(self):
        s=pd.read_csv(ROOT/'outputs/bond_equity_instantaneous_stress.csv')
        r=s[(s.policy=='Sample_MV_A3')&(s.scenario=='Equity -30%, bond yields +100bp')].iloc[0]
        self.assertAlmostEqual(r.foundation_loss_pct_of_initial_capital,17.2687,places=2)
        h=pd.read_csv(ROOT/'outputs/2030_hurdle.csv').iloc[0]
        self.assertAlmostEqual(h.required_equity_8yr_geometric_CAGR,.0465766,places=4)
    def test_case_bond_valuer_contracts(self):
        from post_freeze_evaluation.modeled_fund_monitor import values_at
        pv,cash,paid=values_at('2027-12-31')
        self.assertAlmostEqual(pv,0,places=5)
        self.assertEqual(cash,630000)
        self.assertEqual(paid,6000000)
        pv2,cash2,paid2=values_at('2024-12-31')
        self.assertGreater(pv2,0)
        self.assertEqual(cash2,252000)
        self.assertEqual(paid2,2400000)
    def test_evaluation_requires_real_receipt(self):
        from post_freeze_evaluation.evaluate import evaluate
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                evaluate(ROOT,Path(d)/'future_market_data.csv',Path(d)/'missing_receipt.json',Path(d)/'missing_actions.json',Path(d)/'out')

    def test_after_freeze_has_no_results(self):
        self.assertFalse(any((ROOT/'post_freeze_evaluation').glob('*2023_2025*.csv')))
        self.assertTrue((ROOT/'post_freeze_evaluation/evaluate.py').exists())

if __name__=='__main__':unittest.main()
