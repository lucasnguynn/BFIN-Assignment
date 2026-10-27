"""Revised whole-fund monitoring uses frozen equity path and the selected funding."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location("monitor",ROOT/"portfolio_construction/post_freeze_evaluation/modeled_fund_monitor.py")
mod=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(mod)

class RevisedMonitorTests(unittest.TestCase):
    def test_prices_and_cash_on_2022_case_date(self):
        for scenario in ("original","principal","coupon"):
            units,net=mod.scenario(scenario)
            pv,cash=mod.price_and_cash("2022-12-31",units,mod.SCHEDULES[scenario])
            cost=sum(units[k]*mod.PRICE[k] for k in units)
            self.assertAlmostEqual(pv,cost,places=5)
            self.assertEqual(cash,0.)

    def test_annual_principal_2025_and_2030_coupons(self):
        units,net=mod.scenario("principal")
        for date,expected in [("2024-12-31",264000.),("2025-12-31",396000.),("2027-12-31",564000.),("2030-12-31",564000.)]:
            pv,cash=mod.price_and_cash(date,units,mod.SCHEDULES["principal"])
            self.assertAlmostEqual(cash,expected,places=6)
        self.assertAlmostEqual(mod.price_and_cash("2030-12-31",units,mod.SCHEDULES["principal"])[0],0.,places=6)

    def test_revised_36_month_withdrawals_and_no_original_leakage(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"growth.csv"
            months=pd.period_range("2023-01","2025-12",freq="M").astype(str)
            pd.DataFrame({"month":months,"growth_value":[mod.ORIGINAL_GROWTH]*36}).to_csv(p,index=False)
            x=mod.monitor(p,Path(d)/"fund.csv","principal")
            self.assertEqual(len(x),36)
            self.assertAlmostEqual(x.loc[x.month=="2024-12","mandatory_external_payment_USD"].iloc[0],2400000.)
            self.assertAlmostEqual(x.loc[x.month=="2025-12","mandatory_external_payment_USD"].iloc[0],1200000.)
            self.assertNotIn(3600000.,x.mandatory_external_payment_USD.values)
            self.assertAlmostEqual(x.loc[x.month=="2025-12","retained_cash_USD"].iloc[0],396000.,places=5)
            self.assertTrue(np.isfinite(x.withdrawal_adjusted_monthly_TWR).all())
            self.assertTrue((x.funding_policy=="principal").all())

if __name__=="__main__":unittest.main()
