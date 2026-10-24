#!/usr/bin/env python3
"""Offline, source-hashed Yahoo raw-to-processed and observed-metric verification.

Only open original team-created, checksum-verified yfinance pickle responses;
never unpickle untrusted user/download files. No requests or yfinance network.
This verifies numerical reproducibility, NOT LMS acceptance or JNJ sign-off.
"""
from __future__ import annotations
import argparse, hashlib, json, pickle, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
try:
    from . import retrieve_evaluation_yahoo as dl
    from . import evaluate as ev
except ImportError:
    import retrieve_evaluation_yahoo as dl
    import evaluate as ev

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify(root, source_record, raw_archive, processed_prices, provisional_summary):
    root=Path(root)
    source_record=Path(source_record)
    record=json.loads(source_record.read_text())
    raw_archive=Path(raw_archive)
    processed_prices=Path(processed_prices)
    provisional_summary=Path(provisional_summary)
    if sha(raw_archive)!=record["raw_archive_sha256"]:
        raise AssertionError("Original source archive SHA256 mismatch")
    if sha(processed_prices)!=record["processed_price_csv_sha256"]:
        raise AssertionError("Processed price SHA256 mismatch")
    if set(record["tickers"])!=set(dl.TICKERS):
        raise ValueError("Original nine security names changed")
    frames={}
    with zipfile.ZipFile(raw_archive) as archive:
        if archive.testzip() is not None:
            raise AssertionError("Corrupt raw archive")
        for ticker in dl.TICKERS:
            blob=archive.read(ticker+".pkl")
            if hashlib.sha256(blob).hexdigest()!=record["raw_responses_sha256"][ticker]:
                raise AssertionError("Untransformed raw response changed: "+ticker)
            # The downloaded original frames and their raw-data hashes are
            # trusted team-created inputs. Pickle is unsafe for unknown files.
            frames[ticker]=pickle.loads(blob)
    regenerated=dl.build_common_prices(frames)
    published=pd.read_csv(processed_prices)
    expected_dates=pd.to_datetime(published.date)
    if not expected_dates.equals(pd.to_datetime(regenerated.date)):
        raise AssertionError("Raw-versus-processed dates differ")
    if len(published)!=752 or len(expected_dates.dt.to_period("M").unique())!=36:
        raise AssertionError("Expected 752 common days and 36 months")
    per_ticker={}
    for ticker in dl.TICKERS:
        original=regenerated[ticker].to_numpy(dtype=float)
        processed=published[ticker].to_numpy(dtype=float)
        if not np.isfinite(original).all() or not np.isfinite(processed).all():
            raise AssertionError("Nonfinite original/processed price: "+ticker)
        relative=np.max(np.abs(original-processed)/np.maximum(np.abs(original),1.0))
        if not np.allclose(original,processed,rtol=5e-12,atol=5e-10):
            raise AssertionError("Original Yahoo/processed close mismatch: "+ticker)
        per_ticker[ticker]=float(relative)
    weights=ev.read_weights(root/"evidence"/"decision_weights_confirmed.csv")
    _,measured=ev.compute_buyhold(regenerated,weights,require_daily=True)
    reported=json.loads(provisional_summary.read_text())
    comparisons={}
    for section in ("policy","VTI"):
        for metric in ("terminal_growth_USD","CAGR_after_initial_cost","volatility_annualized","maximum_drawdown"):
            raw=float(measured[section][metric])
            previous=float(reported[section][metric])
            if abs(raw-previous)>max(1e-7,abs(raw)*2e-10):
                raise AssertionError("Rebuilt measured metric disagrees: {} / {}".format(section,metric))
            comparisons[section+"."+metric]=raw
    for metric in ("annualized_active_arithmetic_return","tracking_error_annualized"):
        raw=float(measured[metric]);previous=float(reported[metric])
        if abs(raw-previous)>2e-10:
            raise AssertionError("Rebuilt active metric disagrees: "+metric)
        comparisons[metric]=raw
    return {"result":"PASS_SOURCE_HASHED_OFFLINE_REBUILD",
            "archive_sha256":sha(raw_archive),"price_sha256":sha(processed_prices),
            "observations":len(published),"months":36,"tickers":list(dl.TICKERS),
            "max_relative_raw_processed_difference":max(per_ticker.values()),
            "per_ticker_max_relative_error":per_ticker,
            "regenerated_performance":comparisons,
            "LMS_acceptance_verified":False,"human_JNJ_review_verified":False}

if __name__=="__main__":
    p=argparse.ArgumentParser(description="Reproduce observed 2023-2025 outcomes offline from verified raw vendor ZIP")
    p.add_argument("--root",required=True)
    p.add_argument("--source-record",required=True)
    p.add_argument("--raw-archive",required=True)
    p.add_argument("--processed-prices",required=True)
    p.add_argument("--provisional-summary",required=True)
    args=p.parse_args()
    print(json.dumps(verify(args.root,args.source_record,args.raw_archive,args.processed_prices,args.provisional_summary),indent=2))
