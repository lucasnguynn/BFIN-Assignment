#!/usr/bin/env python3
"""Source-hashed JNJ no-tender price diagnostic, separate from human review.

Runs entirely from the archived October 2026 Yahoo response. No network access,
no KVUE entitlement and no fabricated corporate-action sign-off.
"""
from __future__ import annotations
import hashlib
import json
import pickle
import sys
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "portfolio_construction/Portfolio Final/Sources"

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def series(frame, label):
    if isinstance(frame.columns, pd.MultiIndex):
        matches = [col for col in frame.columns if label in [str(v) for v in col]]
        if len(matches) != 1:
            raise ValueError(f"Ambiguous {label} in JNJ archive: {matches}")
        return pd.to_numeric(frame[matches[0]], errors="coerce")
    if label not in frame.columns:
        if label in ("Dividends", "Stock Splits"):
            return pd.Series(0.0, index=frame.index)
        raise ValueError(f"Missing {label} in JNJ archive")
    return pd.to_numeric(frame[label], errors="coerce")

def verify():
    manifest = json.loads((SOURCE/"Market Source.json").read_text())
    archive = SOURCE/"Yahoo Raw.zip"
    assert sha256(archive) == manifest["raw_archive_sha256"], "Archived Yahoo SHA256 mismatch"
    assert sha256(SOURCE/"Observed Prices.csv") == manifest["processed_price_csv_sha256"]
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert "JNJ.pkl" in z.namelist()
        # This pickle is the project's SHA256-pinned archived yfinance response;
        # never unpickle arbitrary, unverified third-party uploads.
        raw = pickle.loads(z.read("JNJ.pkl"))
    assert isinstance(raw, pd.DataFrame) and not raw.empty
    dates = pd.to_datetime(raw.index)
    if dates.tz is not None:
        dates = dates.tz_localize(None)
    frame = pd.DataFrame({
        "date": dates.normalize(),
        "close": series(raw, "Close").to_numpy(dtype=float),
        "adj": series(raw, "Adj Close").to_numpy(dtype=float),
        "dividend": series(raw, "Dividends").fillna(0).to_numpy(dtype=float),
        "split": series(raw, "Stock Splits").fillna(0).to_numpy(dtype=float),
    })
    prices = pd.read_csv(SOURCE/"Observed Prices.csv", parse_dates=["date"])
    aligned = prices[["date","JNJ"]].merge(frame,on="date",how="left",validate="one_to_one")
    assert len(aligned)==len(prices) == 752, "Unexpected JNJ date count"
    assert np.isfinite(aligned[["JNJ","close","adj","dividend","split"]].to_numpy(dtype=float)).all()
    assert (aligned[["close","adj","JNJ"]].to_numpy(dtype=float)>0).all()
    rel = np.abs(aligned["JNJ"].to_numpy()-aligned["adj"].to_numpy()) / aligned["adj"].to_numpy()
    max_gap=float(rel.max())
    assert max_gap<2e-6, f"Saved processed JNJ prices differ from archived adjusted closes: {max_gap}"
    # Cash dividend reinvested on its ex-date at that day's close; shares retain
    # JNJ exposure throughout, with no voluntary Kenvue exchange and no KVUE units.
    close=aligned["close"].to_numpy()
    adj=aligned["adj"].to_numpy()
    div=aligned["dividend"].to_numpy()
    splits=aligned["split"].to_numpy()
    assert not np.any(splits!=0), "Recheck JNJ split handling before using close-return formula"
    cash_factor=(close[1:]+div[1:])/close[:-1]
    assert np.isfinite(cash_factor).all() and np.all(cash_factor>0)
    no_tender_growth=float(np.prod(cash_factor))
    vendor_growth=float(adj[-1]/adj[0])
    weights=pd.read_csv(ROOT/"portfolio_construction/evidence/decision_weights_confirmed.csv")
    w=float(weights.loc[weights.security=="JNJ","weight_of_growth_sleeve"].iloc[0])
    original_equity_usd=6229246.753246753
    effect_usd=float((no_tender_growth-vendor_growth)*w*original_equity_usd)
    around=aligned[(aligned.date>="2023-08-15")&(aligned.date<="2023-08-25")]
    assert len(around)>=6
    result={
        "status":"PASS_SOURCE_HASHED_VENDOR_DIAGNOSTIC_NOT_HUMAN_APPROVAL",
        "raw_archive_sha256":sha256(archive),
        "processed_prices_sha256":sha256(SOURCE/"Observed Prices.csv"),
        "jnj_rows":len(aligned),
        "processed_vs_vendor_adjusted_close_max_relative_error":max_gap,
        "jnj_total_dividends_per_original_share":float(div.sum()),
        "no_tender_cash_dividend_reinvestment_growth":no_tender_growth,
        "archived_vendor_adjusted_close_growth":vendor_growth,
        "estimated_whole_equity_value_difference_usd":effect_usd,
        "effect_is_approximate":True,
        "event_window":[{"date":str(row.date.date()),"close":round(float(row.close),6),
                         "adjusted_close":round(float(row.adj),6),
                         "dividend":round(float(row.dividend),6)}
                        for row in around.itertuples()],
        "issuer_event_ruling":"Offer voluntary. Frozen portfolio holds JNJ; does not elect to tender or add KVUE shares.",
        "does_not_verify_real_fill_or_dividend_reinvestment_timing":True,
        "individual_human_review_attested":False,
        "LMS_acceptance_verified":False
    }
    return result

if __name__=="__main__":
    print(json.dumps(verify(),indent=2))
