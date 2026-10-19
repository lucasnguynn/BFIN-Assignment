"""Synthetic-only verification. NO Yahoo 2023-2025 price data are fetched here."""
from __future__ import annotations
import json,sys,tempfile,hashlib,io
from contextlib import redirect_stdout
from datetime import datetime,timezone
from pathlib import Path
import unittest
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'post_freeze_evaluation'))
import evaluate as ev
import create_freeze_receipt as receipt_mod
import retrieve_evaluation_yahoo as rx

class PostFreezeUnitTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/'evidence').mkdir(); (self.root/'evidence/decision_weights_confirmed.csv').write_bytes(
            (ROOT/'tests/fixtures/decision_weights_reference.csv').read_bytes())
        self.pdf=self.root/'submitted.pdf';self.pdf.write_bytes(b'%PDF-1.4 synthetic test fixture (not official evidence)')
        self.receipt=self.root/'real_receipt_fixture.json'
        self.record={
            'submitted_at_hcm':'2026-10-22T15:30:00+07:00',
            'submission_reference':'SYNTHETIC_TEST_ONLY_LMS_REF',
            'submitted_pdf_path':str(self.pdf),
            'submitted_pdf_sha256':ev.sha(self.pdf),
            'frozen_weights_sha256':ev.sha(self.root/'evidence/decision_weights_confirmed.csv')}
        self.receipt.write_text(json.dumps(self.record))
        self.after=datetime(2026,10,23,9,0,tzinfo=rx.TZ)
        self.before=datetime(2026,10,21,9,0,tzinfo=rx.TZ)

    def synthetic(self, skip=None, duplicate=False, corrupt=None):
        idx=pd.bdate_range('2023-01-03','2025-12-31')
        responses={}
        for i,t in enumerate(rx.TICKERS):
            dates=idx
            if t==skip:dates=idx.delete(50)
            if duplicate and t=='PG':dates=dates.append(dates[-1:])
            arr=(100+np.arange(len(dates))*0.018)*(1+i/20)
            if t==corrupt:arr[20]=np.nan
            raw=pd.DataFrame({'Adj Close':arr,'Close':arr+0.01,
                              'Dividends':np.zeros(len(dates))},index=dates)
            responses[t]=raw
        return responses

    def test_unfrozen_denied_even_with_synthetic_own_receipt(self):
        with self.assertRaisesRegex(ValueError,'until after 22'):
            rx.check_genuine_freeze(self.root,self.receipt,now=self.before)

    def test_missing_receipt_denied(self):
        with self.assertRaises(FileNotFoundError):
            rx.check_genuine_freeze(self.root,self.root/'no_receipt.json',now=self.after)

    def test_wrong_receipt_fingerprint_denied(self):
        self.record['frozen_weights_sha256']='wrong';self.receipt.write_text(json.dumps(self.record))
        with self.assertRaisesRegex(ValueError,'weights changed'):
            rx.check_genuine_freeze(self.root,self.receipt,now=self.after)

    def test_submit_late_denied(self):
        self.record['submitted_at_hcm']='2026-10-22T16:05:00+07:00'
        self.receipt.write_text(json.dumps(self.record))
        with self.assertRaisesRegex(ValueError,'after the original deadline'):
            rx.check_genuine_freeze(self.root,self.receipt,now=self.after)

    def test_only_invested_and_vti(self):
        self.assertEqual(len(rx.TICKERS),9)
        self.assertNotIn('BAC',rx.TICKERS)
        self.assertNotIn('IWM',rx.TICKERS)

    def test_valid_daily_synthetic_prices(self):
        prices=rx.build_common_prices(self.synthetic())
        self.assertEqual(prices.columns.tolist(),['date']+list(rx.TICKERS))
        self.assertEqual(prices.date.iloc[0],pd.Timestamp('2023-01-03'))
        self.assertEqual(prices.date.iloc[-1],pd.Timestamp('2025-12-31'))

    def test_no_silent_calendar_intersection(self):
        with self.assertRaisesRegex(ValueError,'daily calendar mismatch'):
            rx.build_common_prices(self.synthetic(skip='JNJ'))

    def test_duplicates_refused(self):
        with self.assertRaisesRegex(ValueError,'duplicated'):
            rx.build_common_prices(self.synthetic(duplicate=True))

    def test_missing_price_refused(self):
        with self.assertRaisesRegex(ValueError,'invalid/nonpositive'):
            rx.build_common_prices(self.synthetic(corrupt='AAPL'))

    def test_missing_entry_refused(self):
        src=self.synthetic()
        for k in src:src[k]=src[k].loc['2023-01-04':]
        with self.assertRaisesRegex(ValueError,'3 January 2023'):
            rx.build_common_prices(src)

    def test_archive_schema_matches_original_evaluator(self):
        out=self.root/'afterfreeze'
        data=rx.create_artifacts(self.synthetic(),out,'2026-10-23T09:00:00+07:00',
                                 'SYNTHETIC_FIXTURE_ONLY',rx.retrieval_args())
        p=out/'daily_adjusted_prices_2023_2025.csv'
        self.assertEqual(ev.sha(p),data['processed_price_csv_sha256'])
        self.assertEqual(ev.sha(out/'yfinance_evaluation_RAW.zip'),data['raw_archive_sha256'])
        weights=ev.read_weights(self.root/'evidence/decision_weights_confirmed.csv')
        monthly,metrics=ev.compute_buyhold(pd.read_csv(p),weights)
        self.assertEqual(len(monthly),36)
        self.assertIn('CAGR_after_initial_cost',metrics['policy'])
        with self.assertRaises(FileExistsError):
            rx.create_artifacts(self.synthetic(),out,'2026-10-23T09:00:00+07:00','SYNTHETIC')

    def test_retrieval_cannot_call_downloader_before_freeze(self):
        called=[]
        def fake_download(**kwargs):called.append(kwargs);return pd.DataFrame()
        with self.assertRaisesRegex(ValueError,'until after 22'):
            rx.retrieve(self.root,self.receipt,self.root/'result',now=self.before,downloader=fake_download)
        self.assertEqual(called,[])

    def test_retrieval_synthetic_injection_only(self):
        fake=self.synthetic();calls=[]
        def downloader(*,tickers,**kwargs):
            calls.append((tickers,kwargs));return fake[tickers]
        record=rx.retrieve(self.root,self.receipt,self.root/'generated',now=self.after,downloader=downloader)
        self.assertEqual(len(calls),9)
        self.assertEqual(record['yfinance_version'],'SYNTHETIC_FIXTURE_TEST_ONLY')
        self.assertTrue((self.root/'generated/evaluation_source_record.json').exists())

    def test_synthetic_complete_evaluator_chain(self):
        out=self.root/'synthetic_retrieval'
        rx.create_artifacts(self.synthetic(),out,'2026-10-23T09:00:00+07:00','SYNTHETIC_FIXTURE')
        actions=self.root/'jnj_action_synthetic_fixture.json'
        actions.write_text(json.dumps({'JNJ_2023_Kenvue_adjusted_price_policy_verified':True,
            'reviewer':'TEST FIXTURE NOT A REAL REVIEW',
            'source':'SYNTHETIC ONLY',
            'reviewed_at_hcm':'2026-10-23T09:30:00+07:00',
            'treatment':'No voluntary exchange in SYNTHETIC TEST ONLY'}))
        with redirect_stdout(io.StringIO()):
            monthly,report=ev.evaluate(self.root,out/'daily_adjusted_prices_2023_2025.csv',
                self.receipt,actions,self.root/'synthetic_outputs',out/'evaluation_source_record.json')
        self.assertEqual(len(monthly),36)
        self.assertEqual(report['scope'],'Growth sleeve only; not a measured whole-fund return')

    def test_create_receipt_rejects_future(self):
        with self.assertRaisesRegex(ValueError,'Future-dated'):
            receipt_mod.create_receipt(self.root/'evidence/decision_weights_confirmed.csv',self.pdf,'COURSE_REF_999',
                '2026-10-22T15:30:00+07:00',self.root/'proof.json',now=self.before)

    def test_create_receipt_keeps_actual_sha(self):
        new=receipt_mod.create_receipt(self.root/'evidence/decision_weights_confirmed.csv',self.pdf,'COURSE_REF_999',
                '2026-10-22T15:30:00+07:00',self.root/'proof.json',now=self.after)
        self.assertEqual(new['frozen_weights_sha256'],self.record['frozen_weights_sha256'])
        self.assertEqual(new['submitted_pdf_sha256'],ev.sha(self.pdf))
        self.assertEqual(new['submitted_pdf_path'],'ORIGINAL_SUBMITTED_DECISION_RECORD.pdf')
        self.assertEqual(ev.sha(self.root/new['submitted_pdf_path']),ev.sha(self.pdf))

if __name__=='__main__':unittest.main()
