#!/usr/bin/env python3
"""Fetch 2023-2025 Yahoo daily adjusted prices only AFTER original October-22 submission.

Original return decision remains immutable. This file does not retrieve actual prices
until the user provides a REAL original submission receipt and current local time is
later than the original-policy deadline. Offline tests use fake downloaded frames.

Usage after valid freeze:
 python post_freeze_evaluation/retrieve_evaluation_yahoo.py --root /path/to/analysis \
   --receipt /path/to/receipt.json --out-dir /path/to/post_freeze_data

The source record and processed daily CSV are compatible with evaluate.py.
Archived yfinance DataFrames are trusted team-created pickle data: DO NOT load
arbitrary, external or user-supplied pickle files.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
import hashlib
import json
import pickle
import zipfile
import importlib.metadata
import numpy as np
import pandas as pd

try:
    from . import evaluate as ev
except ImportError:
    import evaluate as ev

TICKERS=("AAPL","MSFT","JPM","JNJ","PFE","PG","KO","CAT","VTI")
START="2023-01-03"
END_EXCLUSIVE="2026-01-01"
TZ=ZoneInfo("Asia/Ho_Chi_Minh")


def sha(data: bytes)->str:
    return hashlib.sha256(data).hexdigest()


def _package_version(pkg):
    try: return importlib.metadata.version(pkg)
    except importlib.metadata.PackageNotFoundError: return 'UNKNOWN'


def check_genuine_freeze(root, receipt_path, now=None):
    """Receipt consistency plus real machine clock; cannot authenticate LMS externally."""
    root=Path(root).resolve()
    weights=root/'evidence'/'decision_weights_confirmed.csv'
    if not weights.is_file(): raise FileNotFoundError('Frozen confirmed-weight CSV missing')
    receipt=json.loads(Path(receipt_path).read_text(encoding='utf-8'))
    needed=['submitted_at_hcm','submission_reference','submitted_pdf_sha256',
            'submitted_pdf_path','frozen_weights_sha256']
    if any(not str(receipt.get(k,'')).strip() for k in needed):
        raise ValueError('Real submission metadata and fingerprints are required; cannot invent a receipt')
    submission=ev.dated(receipt['submitted_at_hcm'],'submitted_at_hcm')
    if submission>ev.POLICY_DEADLINE: raise ValueError('Submitted after the original deadline')
    if submission.date().isoformat()<'2026-10-01': raise ValueError('Implausibly early decision receipt')
    current=now if now is not None else datetime.now(timezone.utc)
    if current.tzinfo is None: raise ValueError('System clock must be timezone aware')
    if current.astimezone(TZ)<=ev.POLICY_DEADLINE:
        raise ValueError('Do not fetch 2023-2025 evaluation data until after 22 October 2026 16:00 HCMC')
    if current.astimezone(TZ)<=submission:
        raise ValueError('Evaluation retrieval must occur after the original submission')
    if ev.sha(weights)!=receipt['frozen_weights_sha256']:
        raise ValueError('Original submitted decision weights changed')
    pdf=ev.resolved(receipt['submitted_pdf_path'],Path(receipt_path).parent)
    if not pdf.is_file() or ev.sha(pdf)!=receipt['submitted_pdf_sha256']:
        raise ValueError('Submitted PDF missing or fingerprint mismatch')
    return receipt


def adjusted_price(raw: pd.DataFrame,ticker:str)->pd.Series:
    if raw is None or not isinstance(raw,pd.DataFrame) or raw.empty:
        raise ValueError(f'{ticker}: no daily Yahoo DataFrame')
    if not isinstance(raw.index,pd.DatetimeIndex) or raw.index.has_duplicates:
        raise ValueError(f'{ticker}: timestamps missing/duplicated')
    idx=raw.index.tz_localize(None) if raw.index.tz is not None else raw.index
    idx=idx.normalize()
    if idx.has_duplicates: raise ValueError(f'{ticker}: date collision after timezone conversion')
    if isinstance(raw.columns,pd.MultiIndex):
        exact=[c for c in raw.columns if 'Adj Close' in tuple(map(str,c)) and ticker in tuple(map(str,c))]
        if len(exact)!=1:
            raise ValueError(f'{ticker}: exactly one Adj Close column expected; got {len(exact)}')
        col=exact[0]
    else:
        if 'Adj Close' not in raw.columns: raise ValueError(f'{ticker}: missing Adj Close with auto_adjust=False')
        col='Adj Close'
    values=pd.to_numeric(raw[col],errors='coerce').to_numpy(dtype=float)
    p=pd.Series(values,index=idx,name=ticker).sort_index()
    if p.empty or not np.isfinite(values).all() or (values<=0).any():
        raise ValueError(f'{ticker}: invalid/nonpositive adjusted prices; do not interpolate')
    p=p.loc[(p.index>=pd.Timestamp(START)) & (p.index<pd.Timestamp(END_EXCLUSIVE))]
    if p.empty: raise ValueError(f'{ticker}: no observations in frozen evaluation period')
    return p


def build_common_prices(responses:dict[str,pd.DataFrame])->pd.DataFrame:
    if set(responses)!=set(TICKERS):
        raise ValueError('Must retrieve exactly original invested names plus benchmark (no universe changes)')
    series={t:adjusted_price(responses[t],t) for t in TICKERS}
    common=series[TICKERS[0]].index
    for name,ser in series.items():
        if not common.equals(ser.index):
            extra=common.difference(ser.index)
            missing=ser.index.difference(common)
            raise ValueError(f'{name}: daily calendar mismatch, missing={len(extra)}, extra={len(missing)}; review raw inputs')
    prices=pd.DataFrame({'date':common})
    for t in TICKERS:prices[t]=series[t].to_numpy()
    if prices.date.iloc[0]!=pd.Timestamp(START):
        raise ValueError('3 January 2023 actual close is required, do not use December 2022 or Jan 4 proxy')
    # Validate source shape with frozen-rule numerical calculator using reference weights.
    testweights=pd.DataFrame({'security':TICKERS[:-1], 'weight_of_growth_sleeve':[1/8]*8})
    ev.compute_buyhold(prices,testweights,require_daily=True)
    return prices


def retrieval_args():
    return dict(start=START,end=END_EXCLUSIVE,interval='1d',auto_adjust=False,
                actions=True,repair=False,keepna=True,ignore_tz=True,
                multi_level_index=True,progress=False,threads=False,timeout=30)


def fetch_all(downloader,settings):
    return {t:downloader(tickers=t,**settings) for t in TICKERS}


def create_artifacts(responses, outdir, retrieved_at, yfinance_version, settings=None,
                     source='Yahoo Finance via yfinance'):
    """Deterministic price/manifest contents; raw ZIP may include ZIP timestamps."""
    outdir=Path(outdir); outdir.mkdir(parents=True,exist_ok=True)
    if list(outdir.iterdir()): raise FileExistsError('Output folder must be empty; never overwrite prior evidence')
    try:
        prices=build_common_prices(responses)
        # Preserve each FULL vendor-returned DataFrame including unmodified actions.
        rawfiles={t:pickle.dumps(responses[t],protocol=pickle.HIGHEST_PROTOCOL) for t in TICKERS}
        rawmanifest={t:sha(rawfiles[t]) for t in TICKERS}
        rawzip=outdir/'yfinance_evaluation_RAW.zip'
        with zipfile.ZipFile(rawzip,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for t in TICKERS:z.writestr(f'{t}.pkl',rawfiles[t])
            z.writestr('RAW_SOURCE_DETAILS.json',json.dumps({
                'purpose':'2023-2025 original frozen-policy evaluation only',
                'source':source,'retrieved_at_hcm':retrieved_at,
                'settings':settings or retrieval_args(),
                'yfinance_version':yfinance_version,
                'tickers':list(TICKERS),'raw_sha256_by_ticker':rawmanifest,
                'dates':'03 Jan 2023 close through last 2025 trading session',
                'data_integrity':'Vendor frames stored without edits or synthetic missing rows',
                'corporate_actions':'manual JNJ/Kenvue review required'},indent=2))
        processed=outdir/'daily_adjusted_prices_2023_2025.csv'
        prices.to_csv(processed,index=False,date_format='%Y-%m-%d',float_format='%.14g')
        record={'retrieved_at_hcm':retrieved_at,'source':source,
           'yfinance_version':yfinance_version,'raw_archive_path':rawzip.name,
           'raw_archive_sha256':ev.sha(rawzip),
           'processed_price_csv_sha256':ev.sha(processed),
           'requested_start_inclusive':START,'requested_end_exclusive':END_EXCLUSIVE,
           'tickers':list(TICKERS),'download_settings':settings or retrieval_args(),
           'pandas_version':pd.__version__,
           'number_daily_rows':len(prices),
           'raw_responses_sha256':rawmanifest,
           'JNJ_action_status':'NOT_REVIEWED_MANUALLY: evaluator will block until real dated review'}
        sourcepath=outdir/'evaluation_source_record.json'
        sourcepath.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
        return record
    except Exception:
        # Failed conversions must not leave an official-looking partial source record.
        for p in outdir.glob('*'):
            if p.is_file():p.unlink()
        raise


def retrieve(root,receipt_path,outdir,now=None, downloader=None):
    check_genuine_freeze(root,receipt_path,now=now)  # MUST precede imports/network
    if downloader is None:
        try:import yfinance as yf
        except ImportError as e:raise RuntimeError('Install yfinance on a network-enabled machine, AFTER freeze') from e
        downloader=yf.download
        yfver=yf.__version__
    else:yfver='SYNTHETIC_FIXTURE_TEST_ONLY'
    settings=retrieval_args()
    responses=fetch_all(downloader,settings)
    retrieved_at=datetime.now(TZ).isoformat(timespec='seconds') if now is None else now.astimezone(TZ).isoformat(timespec='seconds')
    return create_artifacts(responses,outdir,retrieved_at,yfver,settings)


def cli():
    p=argparse.ArgumentParser(description='AFTER REAL FREEZE ONLY: archive 2023-2025 yfinance data')
    p.add_argument('--root',required=True,help='Path to frozen analysis/ directory')
    p.add_argument('--receipt',required=True,help='Genuine LMS receipt metadata with original PDF')
    p.add_argument('--out-dir',required=True,help='Must be empty NEW directory')
    a=p.parse_args()
    print(json.dumps(retrieve(a.root,a.receipt,a.out_dir),indent=2))

if __name__=='__main__':cli()
