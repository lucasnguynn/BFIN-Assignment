#!/usr/bin/env python3
"""BFIN Kappa M2-02: real Yahoo-yfinance retrieval -> archived raw -> monthly returns.

Run from any directory; --project-root points to the BFIN_M2_Gate02 directory.
Real downloaded data only. Synthetic fixtures are restricted to tests/.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.metadata
import json
import pickle
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd

ASSETS = ['AAPL','MSFT','JPM','BAC','JNJ','PFE','PG','KO','XOM','CAT','VTV','IWM']
BENCHMARK = 'VTI'
TICKERS = ASSETS + [BENCHMARK]
ESTIMATION = ('2014-12-01','2023-01-01')  # calendar boundaries, Yahoo end EXCLUSIVE
EVALUATION = ('2022-12-01','2026-01-01')  # never needed to decide 2022 allocation
START_MONTH = '2014-12'
END_MONTH = '2022-12'
EXPECTED_MONTHS = pd.period_range('2015-01','2022-12',freq='M')


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def app_ver(name):
    try: return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError: return 'NOT_INSTALLED'


def ensure_folders(root):
    for sub in ['data/raw/yahoo','data/processed','outputs/qa','logs']:
        (root/sub).mkdir(parents=True, exist_ok=True)


def manifest_path(root):
    return root/'data'/'raw'/'yahoo'/'source_manifest.jsonl'


def append_manifest(root, record):
    with manifest_path(root).open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(record,sort_keys=True,default=str)+'\n')
    export_source_manifest_csv(root)


def export_source_manifest_csv(root):
    """Create the source record expected by the group framework. Failures are included."""
    fields=['source_name','download_url','retrieval_datetime','ticker_or_dataset',
        'requested_start','requested_end','frequency','yfinance_args_or_factor_archive',
        'package_version','raw_filepath','file_sha256','missing_data_notes',
        'failures_and_resolution','owner','status','partition']
    path=root/'data/source_manifest.csv'
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.tmp')
    with temp.open('w',newline='',encoding='utf-8') as handle:
        w=csv.DictWriter(handle,fieldnames=fields);w.writeheader()
        for rec in get_manifest(root):
            w.writerow(dict(source_name=rec.get('source','Yahoo Finance via yfinance'),
                download_url=rec.get('source_url','https://finance.yahoo.com/'),
                retrieval_datetime=rec.get('retrieved_utc',''),
                ticker_or_dataset=rec.get('ticker',''),
                requested_start=rec.get('date_start_inclusive',''),
                requested_end=rec.get('date_end_exclusive',''),frequency='1d',
                yfinance_args_or_factor_archive=json.dumps(rec.get('settings',{}),sort_keys=True),
                package_version=json.dumps(rec.get('package_versions',{}),sort_keys=True),
                raw_filepath=rec.get('raw_path',''),file_sha256=rec.get('sha256',''),
                missing_data_notes='',failures_and_resolution=rec.get('error',''),
                owner='Member 2',status=rec.get('status',''),partition=rec.get('partition','')))
    temp.replace(path)


def get_manifest(root):
    path = manifest_path(root)
    if not path.exists(): return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def download(root:Path, partition:str='estimation', tickers:list[str]|None=None, frozen_policy:Path|None=None):
    ensure_folders(root)
    if partition not in ('estimation','evaluation'):
        raise ValueError('Unknown data partition')
    if partition=='evaluation' and (frozen_policy is None or not frozen_policy.is_file()):
        raise ValueError('Evaluation data retrieval requires an existing frozen October 22 policy file')
    start, end = ESTIMATION if partition=='estimation' else EVALUATION
    targets = tickers or TICKERS
    if len(set(targets)) != len(targets) or not set(targets).issubset(TICKERS):
        raise ValueError('Tickers must be unique members of the predeclared candidate set')
    args = dict(start=start,end=end,interval='1d',auto_adjust=False,
                actions=True,repair=False,keepna=True,ignore_tz=True,
                multi_level_index=True,progress=False,threads=False,timeout=25)
    # Log failed dependency rather than masking it or substituting external data.
    try:
        import yfinance as yf
    except Exception as exc:
        for ticker in targets:
            append_manifest(root,dict(ticker=ticker,partition=partition,source='Yahoo Finance via yfinance',
                retrieved_utc=utc_now(),date_start_inclusive=start,date_end_exclusive=end,
                settings=args,package_versions={'yfinance':app_ver('yfinance'),'pandas':pd.__version__},
                status='FAILED',error=f'{type(exc).__name__}: {exc}',raw_path='',sha256=''))
        raise RuntimeError('yfinance is not available; install the common environment on an internet-enabled machine') from exc
    failed = 0
    for ticker in targets:
        entry = dict(ticker=ticker,partition=partition,source='Yahoo Finance via yfinance',
              source_url='https://finance.yahoo.com/',retrieved_utc=utc_now(),
              date_start_inclusive=start,date_end_exclusive=end,settings=args,
              package_versions={'yfinance':yf.__version__,'pandas':pd.__version__},
              status='FAILED',error='',raw_path='',sha256='')
        try:
            raw=yf.download(tickers=ticker,**args)
            if raw is None or not isinstance(raw,pd.DataFrame) or raw.empty:
                raise ValueError('Missing or empty Yahoo response')
            if not isinstance(raw.index,pd.DatetimeIndex):
                raise ValueError('Unexpected Yahoo index; requires daily dates')
            rawdir=root/'data/raw/yahoo'
            out=rawdir/f'{ticker}_{partition}_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}_{uuid.uuid4().hex[:8]}.pkl'
            # Preserve the exact returned DataFrame without dropping actions or adjusting columns.
            with out.open('xb') as handle: pickle.dump(raw,handle,protocol=pickle.HIGHEST_PROTOCOL)
            entry.update(status='OK',raw_path=str(out.relative_to(root)),sha256=sha256(out),
                         number_daily_rows=len(raw),column_layout='MULTIINDEX' if isinstance(raw.columns,pd.MultiIndex) else 'FLAT')
        except Exception as exc:
            entry['error']=f'{type(exc).__name__}: {exc}'
            failed+=1
        finally:
            append_manifest(root,entry)
            print(f'{partition:10} {ticker:5} {entry["status"]} {entry["error"][:85]}',flush=True)
    if failed:
        raise RuntimeError(f'{failed} download(s) failed; see {manifest_path(root)}. No missing returns were invented.')


def selected_manifest(root,partition):
    records=get_manifest(root)
    latest={}
    for row in records:
        if row.get('partition')==partition and row.get('status')=='OK' and row.get('ticker') in TICKERS:
            latest[row['ticker']]=row
    absent=sorted(set(TICKERS)-set(latest))
    if absent: raise ValueError(f'Missing archived raw yfinance data for: {absent}')
    return latest


def read_checked_raw(root,record):
    path = root/record['raw_path']
    if not path.exists(): raise FileNotFoundError(path)
    if sha256(path)!=record['sha256']: raise ValueError(f'Raw file checksum mismatch: {path.name}')
    # ONLY unpickle DataFrames produced by this team's own retrieval code; pickle is unsafe for untrusted files.
    with path.open('rb') as handle: frame=pickle.load(handle)
    if not isinstance(frame,pd.DataFrame): raise TypeError('Archived response was not a DataFrame')
    return frame


def _column(frame,ticker,field):
    if isinstance(frame.columns,pd.MultiIndex):
        cols=[c for c in frame.columns if field in tuple(map(str,c)) and ticker in tuple(map(str,c))]
        if len(cols)==1: return frame[cols[0]]
        cols=[c for c in frame.columns if field in tuple(map(str,c))]
        if len(cols)==1: return frame[cols[0]]
    elif field in frame.columns:
        return frame[field]
    raise ValueError(f'{ticker}: cannot uniquely locate {field!r} in archived data')


def convert_raw_monthly(frame,ticker,partition='estimation',start_month='2015-01'):
    if frame.empty or not isinstance(frame.index,pd.DatetimeIndex):
        raise ValueError(f'{ticker}: missing daily dates')
    if frame.index.has_duplicates: raise ValueError(f'{ticker}: duplicate trading dates')
    idx=frame.index.tz_localize(None) if frame.index.tz is not None else frame.index
    if idx.isna().any(): raise ValueError(f'{ticker}: invalid trading date')
    raw=_column(frame,ticker,'Adj Close')
    price=pd.Series(pd.to_numeric(raw,errors='coerce').to_numpy(dtype=float),index=idx).sort_index()
    if price.isna().any():
        raise ValueError(f'{ticker}: missing adjusted close; investigate raw response rather than fill')
    if not np.isfinite(price.to_numpy()).all() or (price<=0).any():
        raise ValueError(f'{ticker}: invalid adjusted close')
    if partition=='estimation':
        if not ('2015-01' <= start_month <= '2018-01'):
            raise ValueError('Estimation must end 2022-12 and include at least 60 months since Jan 2015')
        boundary_month=str(pd.Period(start_month,freq='M')-1)
        price=price.loc[(price.index>=pd.Timestamp(boundary_month+'-01')) & (price.index<pd.Timestamp(ESTIMATION[1]))]
        month_range=pd.period_range(boundary_month,END_MONTH,freq='M')
        output_start, output_end=start_month,'2022-12'
    else:
        price=price.loc[(price.index>=pd.Timestamp(EVALUATION[0])) & (price.index<pd.Timestamp(EVALUATION[1]))]
        month_range=pd.period_range('2022-12','2025-12',freq='M')
        output_start, output_end='2023-01','2025-12'
    if price.empty: raise ValueError(f'{ticker}: no prices inside {partition} requested window')
    by_month=price.groupby(price.index.to_period('M'))
    monthly=by_month.last().reindex(month_range)
    last_dates=by_month.apply(lambda z:z.index.max()).reindex(month_range)
    if monthly.isna().any():
        raise ValueError(f'{ticker}: missing month-end price(s) {list(monthly[monthly.isna()].index.astype(str))}')
    missing_end=[]
    for month,last in last_dates.items():
        if pd.isna(last) or (month.end_time.normalize()-last.normalize()).days>7:
            missing_end.append(str(month))
    if missing_end:
        raise ValueError(f'{ticker}: price does not reach month end for {missing_end}')
    returns=monthly.pct_change(fill_method=None)
    returns=returns.loc[output_start:output_end]
    if not returns.index.equals(month_range[1:]): raise AssertionError('Month keys did not align')
    if returns.isna().any() or not np.isfinite(returns.to_numpy()).all():
        raise ValueError(f'{ticker}: missing/nonfinite monthly total return')
    if (returns<=-1).any(): raise ValueError(f'{ticker}: impossible monthly return without bankruptcy investigation')
    jumps=returns[returns.abs()>0.4]
    diagnostics=dict(ticker=ticker,months=len(returns),first_month=str(returns.index[0]),
         last_month=str(returns.index[-1]),boundary_price_month=str(month_range[0]),
         large_absolute_monthly_returns_gt_40pct=[{'month':str(k),'return_decimal':float(v)} for k,v in jumps.items()],
         min_return_decimal=float(returns.min()), max_return_decimal=float(returns.max()))
    return returns.astype(float), diagnostics


def atomic_csv(frame,path):
    path=Path(path); temp=path.with_name(path.name+'.tmp')
    frame.to_csv(temp,index=False,float_format='%.17g')
    temp.replace(path)


def build(root:Path,partition='estimation',start_month='2015-01',window_approval:Path|None=None):
    ensure_folders(root)
    if partition not in ('estimation','evaluation'): raise ValueError('Unknown data partition')
    if partition=='estimation' and start_month!='2015-01' and (window_approval is None or not window_approval.is_file()):
        raise ValueError('Shorter estimation window requires an existing documented team window approval')
    latest=selected_manifest(root,partition)
    series=[]; quality=[]
    for ticker in TICKERS:
        frame=read_checked_raw(root,latest[ticker]); returns,diagnostics=convert_raw_monthly(frame,ticker,partition,start_month=start_month)
        returns.name=ticker
        series.append(returns)
        diagnostics['source_sha256']=latest[ticker]['sha256']
        diagnostics['source_file']=latest[ticker]['raw_path']
        quality.append(diagnostics)
    aligned=pd.concat(series,axis=1)
    start,end=(start_month,'2022-12') if partition=='estimation' else ('2023-01','2025-12')
    expected=pd.period_range(start,end,freq='M')
    if not aligned.index.equals(expected) or aligned.isna().any().any() or len(aligned)<(60 if partition=='estimation' else 36):
        raise ValueError(f'Invalid common monthly coverage in {partition}')
    for symbol in TICKERS:
        if (aligned[symbol]<=-1).any(): raise ValueError(f'{symbol}: impossible return')
    result=aligned.copy(); result.index=result.index.astype(str);result.index.name='month'; result.reset_index(inplace=True)
    path=root/'data/processed'/f'asset_monthly_returns_{partition}.csv'
    atomic_csv(result,path)
    # Current group framework canonical estimation handoff (no future observations!)
    if partition=='estimation':
        atomic_csv(result,root/'data/processed/asset_monthly_returns.csv')
        # Explicit compatibility with earlier Member 3 V2 code, schema-equivalent by design.
        atomic_csv(result,root/'data/processed/security_returns_monthly.csv')
    report={'status':'PASSED_SOURCE_INTEGRITY_AND_RETURN_COVERAGE',
       'caveat':'Historical Yahoo adjusted-close prices are provider-revised; case-date vintage cannot be guaranteed.',
       'partition':partition,'expected_months':len(expected),'actual_months':len(result),
       'window_approval_reference':str(window_approval) if window_approval else None,
       'month_start':start,'month_end':end,'all_assets':TICKERS,
       'input_source':'Archived Yahoo Finance / yfinance DataFrames',
       'number_verified_archived_sources':len(latest),
       'output_file':str(path.relative_to(root)),'output_sha256':sha256(path),
       'raw_quality':quality, 'generated_utc':utc_now()}
    out=root/'outputs/qa'/f'M2_02_{partition}_report.json';out.write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS {partition}: {len(result)} common months, {len(TICKERS)} assets; {path}')
    return report


def status(root:Path):
    records=get_manifest(root)
    last={}
    for entry in records:
        last[(entry['partition'],entry['ticker'])]=entry
    missing=[t for t in TICKERS if ('estimation',t) not in last or last['estimation',t]['status']!='OK']
    successful_report=root/'outputs/qa/M2_02_estimation_report.json'
    processed=root/'data/processed/asset_monthly_returns_estimation.csv'
    evidence_ok=False
    if not missing and successful_report.exists() and processed.exists():
        try:
            existing=json.loads(successful_report.read_text())
            evidence_ok=existing.get('output_sha256')==sha256(processed) and existing.get('number_verified_archived_sources')==len(TICKERS)
        except (ValueError,OSError):pass
    code_status='PASSED_DATA_GATE' if evidence_ok else ('BLOCKED' if missing else 'RAW_AVAILABLE_PROCESSING_REQUIRED')
    report=dict(gate='M2-02',status=code_status,
       required_tickers=TICKERS,received_ok_estimation=len(TICKERS)-len(missing),
       missing_or_failed_estimation=missing,record_count=len(records),
       market_data_computation_performed=evidence_ok, generated_utc=utc_now(),
       next_command='python src/m2_data_pipeline.py build --project-root .')
    out=root/'outputs/qa/M2_02_live_data_status.json'; out.parent.mkdir(exist_ok=True,parents=True)
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return report


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation',choices=['fetch','build','status'])
    p.add_argument('--project-root',default=str(Path(__file__).resolve().parent.parent))
    p.add_argument('--partition',choices=['estimation','evaluation'],default='estimation')
    p.add_argument('--tickers',nargs='+',help='Optional subset for debugging; full build requires all 13')
    p.add_argument('--frozen-policy',help='Mandatory for downloading evaluation data')
    p.add_argument('--start-month',default='2015-01',help='Approved estimation start (YYYY-MM; at least 60 months)')
    p.add_argument('--window-approval',help='Required written team approval for estimation start later than 2015-01')
    a=p.parse_args(argv)
    root=Path(a.project_root).resolve()
    if a.operation=='fetch':download(root,a.partition,a.tickers,Path(a.frozen_policy) if a.frozen_policy else None)
    elif a.operation=='build':build(root,a.partition,a.start_month,Path(a.window_approval) if a.window_approval else None)
    else:status(root)

if __name__=='__main__':main()
