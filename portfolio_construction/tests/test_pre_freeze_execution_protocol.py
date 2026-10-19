"""PRE-FREEZE UNIT TESTS. Synthetic price arrays ONLY; no observed 2023-25 evaluation."""
import hashlib
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from post_freeze_evaluation.evaluate import (
    BUDGET,FEE,ENTRY,END,MONTHS,
    compute_buyhold,read_weights,validate_freeze,sha,dated
)
from post_freeze_evaluation.modeled_fund_monitor import values_at,elapsed_coupon_years,main as modeled_main


def synthetic_daily():
    # Completely simulated price paths. No Yahoo future observations are loaded.
    dates=pd.bdate_range('2023-01-03','2025-12-31')
    t=np.arange(len(dates),dtype=float)
    return pd.DataFrame({'date':dates,'AAPL':100*np.exp(0.0004*t),
         'JNJ':80*np.exp(0.0002*t),'VTI':200*np.exp(0.0003*t)})


def synthetic_weights():
    return pd.DataFrame({'security':['AAPL','JNJ'],
        'weight_of_growth_sleeve':[0.6,0.4]})


class ExecutionContractTests(unittest.TestCase):
    def test_case_date_exact_quote(self):
        present,cash,withdraw=values_at('2022-12-31')
        self.assertAlmostEqual(present,5_764_524,places=6)
        self.assertEqual(cash,0)
        self.assertEqual(withdraw,0)

    def test_exact_anniversary_timing(self):
        self.assertEqual(elapsed_coupon_years('2022-12-31'),0)
        self.assertEqual(elapsed_coupon_years('2023-12-31'),1)
        self.assertEqual(elapsed_coupon_years('2024-12-31'),2)
        self.assertEqual(elapsed_coupon_years('2027-12-31'),5)

    def test_contractual_coupon_ledger(self):
        for year,reserve in [(2023,126000),(2024,252000),(2025,378000),(2026,504000),(2027,630000)]:
            bond,cash,paid=values_at(f'{year}-12-31')
            self.assertEqual(cash,reserve)
            self.assertEqual(paid,0 if year==2023 else 2400000 if year<2027 else 6000000)
            self.assertGreaterEqual(bond,-1e-6)

    def test_synthetic_buyhold_36_months(self):
        monthly,s=compute_buyhold(synthetic_daily(),synthetic_weights())
        self.assertEqual(monthly.month.tolist(),MONTHS)
        self.assertEqual(len(monthly),36)
        synthetic=synthetic_daily()
        first_jan=(synthetic.date.dt.year.eq(2023) & synthetic.date.dt.month.eq(1))
        jan_end=synthetic.loc[first_jan].iloc[-1]
        expected=BUDGET/(1+FEE)*(0.6*float(jan_end.AAPL)/100 + 0.4*float(jan_end.JNJ)/80)
        self.assertAlmostEqual(float(monthly.growth_value.iloc[0]),expected,places=2)
        self.assertGreater(s['policy']['terminal_growth_USD'],BUDGET)
        self.assertEqual(s['scope'],'Growth sleeve only; not a measured whole-fund return')
        self.assertAlmostEqual(s['annualized_active_arithmetic_return'],float(monthly.active_monthly.mean()*12),12)

    def test_explicit_fee_same_for_benchmark(self):
        p=synthetic_daily()
        p['AAPL']=100.;p['JNJ']=80.;p['VTI']=200.
        monthly,_=compute_buyhold(p,synthetic_weights())
        target=BUDGET/(1+FEE)
        self.assertTrue(np.allclose(monthly.growth_value,target))
        self.assertTrue(np.allclose(monthly.VTI_value,target))
        self.assertAlmostEqual(monthly.growth_return_net_initial_fee.iloc[0],1/(1+FEE)-1)
        self.assertTrue(np.allclose(monthly.active_monthly,0))

    def test_no_jan3_anchor_fails(self):
        p=synthetic_daily().iloc[1:].copy()
        with self.assertRaisesRegex(ValueError,'purchase'):
            compute_buyhold(p,synthetic_weights())

    def test_monthly_only_data_rejected(self):
        p=synthetic_daily()
        p['month']=p.date.dt.to_period('M')
        p=p.groupby('month').tail(1).drop(columns='month')
        p=pd.concat([synthetic_daily().iloc[[0]],p]).drop_duplicates('date').sort_values('date')
        with self.assertRaisesRegex(ValueError,'DAILY'):
            compute_buyhold(p,synthetic_weights())

    def test_missing_month_fails(self):
        p=synthetic_daily()
        p=p[~((p.date.dt.year==2024)&(p.date.dt.month==6))]
        with self.assertRaises(ValueError):compute_buyhold(p,synthetic_weights())

    def test_duplicate_and_nan_prices_fail(self):
        p=synthetic_daily()
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            compute_buyhold(pd.concat([p,p.iloc[[-1]]]),synthetic_weights())
        p.loc[p.index[30],'JNJ']=np.nan
        with self.assertRaisesRegex(ValueError,'Invalid adjusted-price'):
            compute_buyhold(p,synthetic_weights())

    def test_unsorted_or_date_overreach_fails(self):
        p=synthetic_daily()
        with self.assertRaisesRegex(ValueError,'sorted'):
            compute_buyhold(p.iloc[::-1].reset_index(drop=True),synthetic_weights())
        out=p.copy();out.loc[len(out)]=out.iloc[-1].tolist()
        out.loc[len(out)-1,'date']=pd.Timestamp('2026-01-02')
        with self.assertRaisesRegex(ValueError,'restricted'):
            compute_buyhold(out,synthetic_weights())

    def test_policy_weight_checks(self):
        read_weights(ROOT/'evidence/decision_weights_confirmed.csv')
        with tempfile.TemporaryDirectory() as d:
            fp=Path(d)/'bad.csv'
            pd.DataFrame({'security':['JNJ','AAPL'],
                'weight_of_growth_sleeve':[0.7,0.7]}).to_csv(fp,index=False)
            with self.assertRaisesRegex(ValueError,'sum to 1'):
                read_weights(fp)

    def test_time_zone_policy(self):
        self.assertEqual(dated('2026-10-22T15:10:00+07:00','x').hour,15)
        with self.assertRaisesRegex(ValueError,'timezone'):
            dated('2026-10-22T15:10:00','x')

    def test_no_submission_receipt_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            with self.assertRaises(FileNotFoundError):
                validate_freeze(ROOT,p/'absent.json',p/'also_absent.json',p/'prices.csv',p/'actions.json')

    def test_false_late_receipt_fails(self):
        # Pure gate test. These are explicitly SYNTHETIC temporary fixture files,
        # not documents submitted to the university.
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);pdf=p/'synthetic_only.pdf';pdf.write_bytes(b'synthetic fixture not a real submission')
            w=ROOT/'evidence/decision_weights_confirmed.csv'
            r={'submitted_at_hcm':'2026-10-22T17:01:00+07:00',
               'submission_reference':'SYNTHETIC_TEST_ONLY',
               'submitted_pdf_path':str(pdf),'submitted_pdf_sha256':sha(pdf),
               'frozen_weights_sha256':sha(w)}
            rec=p/'r.json';rec.write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,'later'):
                validate_freeze(ROOT,rec,p/'absent.json',p/'absent.csv',p/'absent_actions.json')

    def test_price_checksum_gate(self):
        # A fully synthetic integrity fixture; never evidence of actual submission.
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);pdf=p/'synthetic_only.pdf';pdf.write_bytes(b'synthetic, not submitted')
            w=ROOT/'evidence/decision_weights_confirmed.csv'
            r={'submitted_at_hcm':'2026-10-22T15:00:00+07:00','submission_reference':'SYNTHETIC_TEST_ONLY',
             'submitted_pdf_path':str(pdf),'submitted_pdf_sha256':sha(pdf),'frozen_weights_sha256':sha(w)}
            rec=p/'r.json';rec.write_text(json.dumps(r))
            f=p/'prices.csv';f.write_text('SYNTHETIC,no real market data\n')
            raw=p/'raw.zip';raw.write_bytes(b'SYNTHETIC_DATA')
            source={'retrieved_at_hcm':'2026-10-23T10:00:00+07:00',
              'processed_price_csv_sha256':'wrong hash','raw_archive_path':str(raw),
              'raw_archive_sha256':sha(raw),'source':'SYNTHETIC_ONLY', 'yfinance_version':'test'}
            s=p/'s.json';s.write_text(json.dumps(source))
            with self.assertRaisesRegex(ValueError,'price CSV hash'):
                validate_freeze(ROOT,rec,s,f,p/'actions.json')

    def test_source_download_before_freeze_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);pdf=p/'synthetic_only.pdf';pdf.write_bytes(b'SYNTHETIC_ONLY')
            w=ROOT/'evidence/decision_weights_confirmed.csv'
            r={'submitted_at_hcm':'2026-10-22T15:00:00+07:00','submission_reference':'SYNTHETIC_TEST_ONLY',
             'submitted_pdf_path':str(pdf),'submitted_pdf_sha256':sha(pdf),'frozen_weights_sha256':sha(w)}
            rec=p/'r.json';rec.write_text(json.dumps(r))
            f=p/'prices.csv';f.write_text('SYNTHETIC_ONLY')
            raw=p/'raw.zip';raw.write_bytes(b'SYNTHETIC_ONLY')
            source={'retrieved_at_hcm':'2026-10-21T22:00:00+07:00',
              'processed_price_csv_sha256':sha(f),'raw_archive_path':str(raw),
              'raw_archive_sha256':sha(raw),'source':'SYNTHETIC_ONLY','yfinance_version':'test'}
            s=p/'s.json';s.write_text(json.dumps(source))
            with self.assertRaisesRegex(ValueError,'not archived after'):
                validate_freeze(ROOT,rec,s,f,p/'actions.json')

    def test_modeled_fund_withdrawal_not_performance_loss(self):
        # Scenario-only mock growth value flat, not an observed 2023-2025 run.
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);f=p/'synthetic_flat_growth.csv'
            pd.DataFrame({'month':MONTHS,'growth_value':[6_229_246.75]*36}).to_csv(f,index=False)
            modeled_main(f,p/'scenario.csv')
            z=pd.read_csv(p/'scenario.csv')
            self.assertEqual(len(z),36)
            payment=z[z.month=='2024-12'].iloc[0]
            self.assertAlmostEqual(float(payment.external_mandatory_payment),2_400_000)
            self.assertGreater(float(payment.cashflow_adjusted_modeled_fund_monthly_return),-0.1)
            self.assertEqual(float(z.modeled_bonds.iloc[-1])>0,True)

if __name__=='__main__':unittest.main()
