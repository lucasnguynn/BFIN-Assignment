"""No-network synthetic fixture: rebuild processed observed data from source-hashed raw frames."""
from __future__ import annotations
import json, pathlib, shutil, sys, tempfile, unittest
import numpy as np
import pandas as pd
ROOT=pathlib.Path(__file__).resolve().parents[2]
MOD=ROOT/"portfolio_construction"/"post_freeze_evaluation"
sys.path.insert(0,str(MOD))
import evaluate as ev
import retrieve_evaluation_yahoo as dl
import verify_raw_processed_offline as audit

class OfflineObservedRawRebuildTest(unittest.TestCase):
    def test_full_raw_to_36_month_metrics_and_tamper_rejection(self):
        with tempfile.TemporaryDirectory() as temp:
            d=pathlib.Path(temp)
            root=d/"case"; (root/"evidence").mkdir(parents=True)
            shutil.copyfile(ROOT/"portfolio_construction/evidence/decision_weights_confirmed.csv",
                            root/"evidence/decision_weights_confirmed.csv")
            full=pd.bdate_range("2023-01-03","2025-12-31")
            # Labelled synthetic fixture: retain 752 unique dates across 36 months.
            dates=full[np.linspace(0,len(full)-1,752,dtype=int)]
            self.assertEqual(len(dates),752)
            synthetic={}
            for i,ticker in enumerate(dl.TICKERS):
                prices=50.0+i*10+np.linspace(0,15+i,752)+np.sin(np.arange(752)/13+i)
                synthetic[ticker]=pd.DataFrame({"Adj Close":prices,"Close":prices,
                    "Dividends":np.zeros(752),"Stock Splits":np.zeros(752)},index=dates)
            rawdir=d/"vendor"
            dl.create_artifacts(synthetic,rawdir,"2026-10-24T19:24:06+07:00",
                                "SYNTHETIC_FIXTURE_TEST_ONLY")
            prices=pd.read_csv(rawdir/"daily_adjusted_prices_2023_2025.csv")
            weights=ev.read_weights(root/"evidence/decision_weights_confirmed.csv")
            _,summary=ev.compute_buyhold(prices,weights,require_daily=True)
            s=d/"summary.json";s.write_text(json.dumps(summary,indent=2))
            args=(root,rawdir/"evaluation_source_record.json",
                  rawdir/"yfinance_evaluation_RAW.zip",
                  rawdir/"daily_adjusted_prices_2023_2025.csv",s)
            result=audit.verify(*args)
            self.assertEqual(result["result"],"PASS_SOURCE_HASHED_OFFLINE_REBUILD")
            self.assertEqual(result["observations"],752)
            self.assertEqual(result["months"],36)
            self.assertLess(result["max_relative_raw_processed_difference"],5e-12)
            # Changing even a single processed price without updating original source
            # invalidates the evidence; no backfilled synthetic market values allowed.
            file=rawdir/"daily_adjusted_prices_2023_2025.csv"
            text=file.read_text();file.write_text(text.replace("50.0","51.0",1))
            with self.assertRaises(AssertionError):
                audit.verify(*args)

if __name__=="__main__":unittest.main()
