import json
import pickle
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(HERE/'src'))
import m2_data_pipeline as m


def fake_frame(ticker, monthly_growth=0.006):
    dates=pd.date_range('2014-12-01','2022-12-31',freq='B')
    # deterministic, no simulated price series included in the student's downloaded outputs
    months=dates.to_period('M'); keys=pd.Index(months.unique())
    monthly_price={mon:100.0*(1+monthly_growth)**i for i,mon in enumerate(keys)}
    adj=pd.Series([monthly_price[k] for k in months],index=dates,dtype=float)
    df=pd.DataFrame({('Adj Close',ticker):adj,('Close',ticker):adj,
                     ('Dividends',ticker):np.zeros(len(dates)),('Stock Splits',ticker):np.zeros(len(dates))})
    df.columns=pd.MultiIndex.from_tuples(df.columns)
    return df


class Gate02Tests(unittest.TestCase):
    def test_adjusted_price_return_and_boundaries(self):
        x,d=m.convert_raw_monthly(fake_frame('AAPL',0.012),'AAPL')
        self.assertEqual(len(x),96)
        self.assertEqual(str(x.index[0]),'2015-01')
        self.assertEqual(str(x.index[-1]),'2022-12')
        self.assertAlmostEqual(float(x.iloc[0]),0.012,places=10)
        self.assertEqual(d['boundary_price_month'],'2014-12')

    def test_approved_60_month_minimum_and_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with self.assertRaisesRegex(ValueError,'team window approval'):
                m.build(root,'estimation',start_month='2018-01')
            x,d=m.convert_raw_monthly(fake_frame('AAPL'),'AAPL',start_month='2018-01')
            self.assertEqual(len(x),60)
            self.assertEqual((str(x.index[0]),str(x.index[-1])),('2018-01','2022-12'))
            with self.assertRaisesRegex(ValueError,'at least 60 months'):
                m.convert_raw_monthly(fake_frame('AAPL'),'AAPL',start_month='2018-02')

    def test_no_imputed_missing_prices(self):
        frame=fake_frame('AAPL')
        frame=frame.drop(frame.loc['2020-04'].index)
        with self.assertRaisesRegex(ValueError,'missing month-end'):
            m.convert_raw_monthly(frame,'AAPL')

    def test_bad_checksum_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);m.ensure_folders(root)
            f=root/'data/raw/yahoo/a.pkl';f.write_bytes(b'not a real archive')
            with self.assertRaisesRegex(ValueError,'checksum mismatch'):
                m.read_checked_raw(root,{'raw_path':'data/raw/yahoo/a.pkl','sha256':'abc'})

    def test_failed_provenance_and_eval_freeze_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with self.assertRaisesRegex(ValueError,'frozen October 22 policy'):
                m.download(root,'evaluation',tickers=['AAPL'])
            with self.assertRaisesRegex(ValueError,'predeclared'):
                m.download(root,'estimation',tickers=['TSLA'])

    def test_end_to_end_download_mock_and_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            module=SimpleNamespace(__version__='TEST_FIXTURE',download=lambda tickers,**kwargs:fake_frame(tickers))
            old=sys.modules.get('yfinance')
            sys.modules['yfinance']=module
            try:
                m.download(root,'estimation')
            finally:
                if old is None:sys.modules.pop('yfinance',None)
                else:sys.modules['yfinance']=old
            report=m.build(root,'estimation')
            self.assertEqual(report['actual_months'],96)
            self.assertEqual(report['number_verified_archived_sources'],13)
            out=pd.read_csv(root/'data/processed/asset_monthly_returns.csv')
            self.assertEqual(out.shape,(96,14))
            self.assertEqual(out.iloc[0,0],'2015-01')
            alias=(root/'data/processed/security_returns_monthly.csv').read_bytes()
            self.assertEqual(alias,(root/'data/processed/asset_monthly_returns.csv').read_bytes())
            self.assertNotIn('2023-01',out.month.values)
            self.assertTrue(all(x['status']=='OK' for x in m.get_manifest(root)))
            source=pd.read_csv(root/'data/source_manifest.csv')
            self.assertEqual(len(source),13)
            self.assertIn('file_sha256',source.columns)

    def test_evaluation_is_separated_and_requires_policy(self):
        dates=pd.date_range('2022-12-01','2025-12-31',freq='B')
        mon=dates.to_period('M'); keys=pd.Index(mon.unique())
        vals=[80.0*1.004**(keys.get_loc(k)) for k in mon]
        frame=pd.DataFrame({('Adj Close','AAPL'):vals},index=dates)
        frame.columns=pd.MultiIndex.from_tuples(frame.columns)
        x,d=m.convert_raw_monthly(frame,'AAPL','evaluation')
        self.assertEqual(len(x),36)
        self.assertEqual((str(x.index[0]),str(x.index[-1])),('2023-01','2025-12'))

    def test_incomplete_or_recent_months_do_not_pass(self):
        frame=fake_frame('AAPL').iloc[:-17]
        with self.assertRaisesRegex(ValueError,'does not reach month end'):
            m.convert_raw_monthly(frame,'AAPL')

if __name__=='__main__':unittest.main()
