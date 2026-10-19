#!/usr/bin/env python3
"""Post-freeze, GROWTH-ONLY 2023-2025 evaluation.

Never used for 2022 policy selection. No future prices are included in this package.
The pure `compute_buyhold` routine is tested with clearly SYNTHETIC daily series;
real execution requires an original dated course receipt and archived price lineage.
"""
import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

TZ=ZoneInfo('Asia/Ho_Chi_Minh')
POLICY_DEADLINE=datetime(2026,10,22,16,0,tzinfo=TZ)
ENTRY=pd.Timestamp('2023-01-03')
END=pd.Timestamp('2025-12-31')
MONTHS=[f'{y}-{m:02d}' for y in range(2023,2026) for m in range(1,13)]
BUDGET=6_235_476.0
FEE=0.001

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def dated(value, field):
    d=datetime.fromisoformat(str(value))
    if d.tzinfo is None or d.utcoffset() is None:
        raise ValueError(f'{field} must have explicit timezone offset')
    return d.astimezone(TZ)

def resolved(path, base):
    p=Path(path)
    return p if p.is_absolute() else Path(base)/p

def validate_freeze(root, receipt_path, source_record_path, prices_path, action_path):
    root=Path(root).resolve()
    receipt=json.loads(Path(receipt_path).read_text(encoding='utf-8'))
    keys=['submitted_at_hcm','submission_reference','submitted_pdf_sha256','submitted_pdf_path','frozen_weights_sha256']
    if any(not receipt.get(k) for k in keys):raise ValueError('Missing real course submission proof / fingerprint / frozen weights fingerprint')
    submitted=dated(receipt['submitted_at_hcm'],'submitted_at_hcm')
    if submitted>POLICY_DEADLINE:raise ValueError('Submission later than 2026-10-22 16:00 HCMC')
    if submitted.date().isoformat()<'2026-10-01':raise ValueError('Unreasonably early original decision receipt; check recorded date')
    pdf=resolved(receipt['submitted_pdf_path'],Path(receipt_path).parent)
    if not pdf.is_file() or sha(pdf)!=receipt['submitted_pdf_sha256']:
        raise ValueError('Original submitted PDF differs from recorded fingerprint')
    weights=root/'evidence/decision_weights_confirmed.csv'
    if sha(weights)!=receipt['frozen_weights_sha256']:
        raise ValueError('Frozen weight file differs from recorded policy')
    record=json.loads(Path(source_record_path).read_text(encoding='utf-8'))
    keys=['retrieved_at_hcm','processed_price_csv_sha256','raw_archive_path','raw_archive_sha256','source','yfinance_version']
    if any(not record.get(k) for k in keys):raise ValueError('Incomplete post-freeze yfinance source record')
    fetched=dated(record['retrieved_at_hcm'],'retrieved_at_hcm')
    if fetched<=submitted:raise ValueError('Evaluation data not archived after actual original policy submission')
    if sha(prices_path)!=record['processed_price_csv_sha256']:
        raise ValueError('Evaluation price CSV hash does not match archived source record')
    raw_archive=resolved(record['raw_archive_path'],Path(source_record_path).parent)
    if not raw_archive.is_file() or sha(raw_archive)!=record['raw_archive_sha256']:
        raise ValueError('Original evaluation responses missing or checksum mismatch')
    action=json.loads(Path(action_path).read_text(encoding='utf-8'))
    keys=['JNJ_2023_Kenvue_adjusted_price_policy_verified','reviewer','source','reviewed_at_hcm','treatment']
    if any(not action.get(k) for k in keys) or action[keys[0]] is not True:
        raise ValueError('A real dated JNJ/Kenvue corporate-action reviewer check is required')
    if dated(action['reviewed_at_hcm'],'reviewed_at_hcm')<submitted:
        raise ValueError('Post-freeze corporate-action check predates original submission')
    if 'no voluntary exchange' not in action['treatment'].lower():
        raise ValueError('JNJ treatment must specify original no-voluntary-exchange rule')
    # These records are manually provided evidence; this code checks consistency,
    # not independently that a course website accepted the receipt or SEC facts.
    return receipt,record,action

def read_weights(weights_path):
    w=pd.read_csv(weights_path)
    cols={'security','weight_of_growth_sleeve'}
    if not cols.issubset(w.columns):raise ValueError('Frozen decision weights missing required fields')
    if not w.security.is_unique:raise ValueError('Duplicate security in frozen policy')
    a=w.weight_of_growth_sleeve.to_numpy(float)
    if not np.isfinite(a).all() or (a<0).any() or not np.isclose(a.sum(),1,atol=1e-8):
        raise ValueError('Frozen weights must be nonnegative and sum to 1')
    if 'JNJ' not in w.security.tolist() or w.security.eq('JNJ').sum()!=1:
        raise ValueError('Policy JNJ holding is missing or ambiguous')
    return w[w.weight_of_growth_sleeve>1e-10].copy()

def compute_buyhold(prices,weights,require_daily=True):
    """Pure, testable price-index accounting. No policy or real submission claims.

    Assumptions: 03 Jan 2023 close is purchase proxy; vendor adjusted closes
    approximate dividend-reinvested index; positions held at fixed entry units;
    VTI benchmark is purchased same day with identical bps entry cost.
    """
    df=prices.copy()
    if 'date' not in df:raise ValueError('Missing date column')
    df['date']=pd.to_datetime(df['date'],errors='raise')
    if df.date.isna().any() or not df.date.is_unique:raise ValueError('Duplicate/missing session dates')
    if not df.date.is_monotonic_increasing:raise ValueError('Prices must be sorted by trade date')
    if df.date.min()<ENTRY or df.date.max()>END:raise ValueError('Input must be restricted to 2023-01-03 through 2025-12-31')
    if (df.date==ENTRY).sum()!=1:raise ValueError('2023-01-03 actual purchase closing-price anchor missing')
    if (END-df.date.max()).days>7:raise ValueError('Missing final December 2025 trading session')
    if (df.date.dt.weekday>4).any():raise ValueError('Weekend quote rows found in daily trading series')
    names=weights.security.tolist()+['VTI']
    if not set(names).issubset(set(df.columns)):raise ValueError('Missing invested tickers or VTI comparator')
    for name in names:
        v=pd.to_numeric(df[name],errors='coerce').to_numpy(float)
        if not np.isfinite(v).all() or (v<=0).any():raise ValueError(f'Invalid adjusted-price series for {name}')
    if require_daily:
        # A monthly-index CSV is not acceptable as proof of the Jan 3 execution price.
        for year in (2023,2024,2025):
            if (df.date.dt.year==year).sum()<200:
                raise ValueError(f'Insufficient DAILY trading sessions for {year}')
        gaps=df.date.diff().dt.days.dropna()
        if gaps.max()>10:raise ValueError('Unexplained trading-series gap over 10 calendar days')
    df['month']=df.date.dt.to_period('M').astype(str)
    ends=df.groupby('month',sort=True).tail(1).copy()
    if ends.month.tolist()!=MONTHS:raise ValueError('Missing/duplicate monthly end prices')
    initial=df.iloc[0]
    w=weights.weight_of_growth_sleeve.to_numpy(float)
    gross=BUDGET/(1+FEE)
    # Each weight buys constant adjusted-price index units; not actual trade shares.
    wealth=(ends[weights.security].to_numpy(float)/initial[weights.security].to_numpy(float))@(w*gross)
    bench=gross*(ends.VTI.to_numpy(float)/float(initial.VTI))
    if not np.isfinite(wealth).all() or not (wealth>0).all():raise ArithmeticError('Invalid buy-and-hold portfolio values')
    r=np.r_[wealth[0]/BUDGET-1,wealth[1:]/wealth[:-1]-1]
    b=np.r_[bench[0]/BUDGET-1,bench[1:]/bench[:-1]-1]
    monthly=pd.DataFrame({'month':MONTHS,'growth_value':wealth,'VTI_value':bench,
        'growth_return_net_initial_fee':r,'VTI_return_net_initial_fee':b,'active_monthly':r-b})
    yrs=(ends.date.iloc[-1]-ENTRY).days/365.25
    def summary(values,ret):
        full=np.r_[BUDGET,values]
        return {'terminal_growth_USD':float(values[-1]),
            'CAGR_after_initial_cost':float((values[-1]/BUDGET)**(1/yrs)-1),
            'volatility_annualized':float(np.std(ret,ddof=1)*np.sqrt(12)),
            'maximum_drawdown':float(np.min(full/np.maximum.accumulate(full)-1))}
    report={'time_window':'2023-01-03 close through final December 2025 trading session',
        'scope':'Growth sleeve only; not a measured whole-fund return',
        'policy':summary(wealth,r),'VTI':summary(bench,b),
        'annualized_active_arithmetic_return':float(np.mean(r-b)*12),
        'tracking_error_annualized':float(np.std(r-b,ddof=1)*np.sqrt(12)),
        'annualized_volatility_definition':'std of 36 monthly returns, with initial fee included in first partial month',
        'method_notes':['Index units held constant from Jan 3; economic no-discretionary-rebalancing rule',
            'Retrospectively adjusted Yahoo close approximates dividend reinvestment, not trade fills',
            '2023 JNJ/Kenvue exchange must be checked against original no-voluntary-exchange policy',
            'Do not infer the 2030 real-wealth goal from a 2023-2025 growth-only test']}
    return monthly,report

def evaluate(root,prices,receipt,action_check,out,source_record=None):
    root=Path(root).resolve(); out=Path(out)
    if source_record is None:
        # Read receipt first, preserving the original missing-proof error.
        Path(receipt).read_text(encoding="utf-8")
        raise ValueError("A post-freeze source record is required")
    validate_freeze(root,receipt,source_record,prices,action_check)
    weights=read_weights(root/'evidence/decision_weights_confirmed.csv')
    raw=pd.read_csv(prices)
    monthly,report=compute_buyhold(raw,weights)
    report['receipt_reference_file']=str(receipt)
    out.mkdir(parents=True,exist_ok=True)
    monthly.to_csv(out/'growth_2023_2025_monthly.csv',index=False,float_format='%.12g')
    (out/'growth_2023_2025_summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    return monthly,report

if __name__=='__main__':
    p=argparse.ArgumentParser(description='Gated original 2022-policy growth evaluation; AFTER ACTUAL OCT 22 FREEZE ONLY')
    p.add_argument('--root',default=str(Path(__file__).resolve().parent.parent))
    p.add_argument('--prices',required=True)
    p.add_argument('--receipt',required=True)
    p.add_argument('--source-record',required=True)
    p.add_argument('--corporate-actions',required=True)
    p.add_argument('--out',required=True)
    a=p.parse_args()
    evaluate(a.root,a.prices,a.receipt,a.corporate_actions,a.out,a.source_record)
