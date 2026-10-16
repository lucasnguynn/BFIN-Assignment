#!/usr/bin/env python3
"""Kappa M2 evidence recorder and conservative gate classifier for GitHub Actions.

No code path manufactures or fetches substitute market data. The gate verifies
manifest hashes and required model files but does not certify Yahoo truthfulness.
"""
from __future__ import annotations
import argparse, hashlib, importlib.metadata, json, platform, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

EXPECTED = ['AAPL','MSFT','JPM','BAC','JNJ','PFE','PG','KO','XOM','CAT','VTV','IWM','VTI']
GITHUB_REPO = 'https://github.com/ranaroussi/yfinance'
GITHUB_SHA = '5cae563642b59f49adf6a04a5ad6744f8b0e084d'

def write_json(path, item):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(item, indent=2, sort_keys=True)+'\n', encoding='utf-8')

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def environment(root):
    packages={}
    for p in ['yfinance','pandas','numpy','scipy','statsmodels','pytest']:
        try:packages[p]=importlib.metadata.version(p)
        except importlib.metadata.PackageNotFoundError:packages[p]='NOT_INSTALLED'
    proc=subprocess.run([sys.executable,'-m','pip','freeze'],capture_output=True,text=True)
    freeze_path=root/'logs/pip_freeze.txt'
    freeze_path.parent.mkdir(parents=True,exist_ok=True)
    freeze_path.write_text(proc.stdout+(proc.stderr if proc.returncode else ''),encoding='utf-8')
    distribution = importlib.metadata.distribution('yfinance') if packages['yfinance'] != 'NOT_INSTALLED' else None
    direct_url_raw = distribution.read_text('direct_url.json') if distribution else None
    direct_url = json.loads(direct_url_raw) if direct_url_raw else {}
    actual_git_commit = direct_url.get('vcs_info', {}).get('commit_id')
    pinned_origin_verified = (actual_git_commit == GITHUB_SHA and
                              'github.com/ranaroussi/yfinance' in direct_url.get('url', ''))
    record={'checked_utc':datetime.now(timezone.utc).isoformat(),
           'package_install_source':'github_pinned_commit',
           'official_repository':GITHUB_REPO,'official_commit_sha':GITHUB_SHA,
           'python_version':sys.version,'platform':platform.platform(),
           'installed_git_commit_sha':actual_git_commit,
           'installed_source_verified':pinned_origin_verified,
           'package_versions':packages,'pip_freeze_sha256':digest(freeze_path),
           'pip_freeze_returncode':proc.returncode}
    write_json(root/'outputs/qa/github_install_record.json',record)
    print(json.dumps(record,indent=2))
    if proc.returncode:raise SystemExit('pip freeze failed: check environment')
    if packages['yfinance']=='NOT_INSTALLED':raise SystemExit('yfinance is not installed')
    if not pinned_origin_verified:raise SystemExit('Installed yfinance is not verified as the pinned GitHub source. Reinstall from requirements_github.txt')
    return record

def gate(root):
    raw=root/'data/raw/yahoo/source_manifest.jsonl'
    processed=root/'data/processed/asset_monthly_returns_estimation.csv'
    report=root/'outputs/qa/M2_02_estimation_report.json'
    model=root/'outputs/qa/M2_03_status.json'
    env=root/'outputs/qa/github_install_record.json'
    blockers=[]
    records=[]
    if raw.exists():
        for line in raw.read_text(encoding='utf-8').splitlines():
            if line.strip():records.append(json.loads(line))
    else:blockers.append('Missing genuine Yahoo retrieval manifest')
    valid={}
    for rec in records:
        if rec.get('status')!='OK' or rec.get('partition')!='estimation':continue
        ticker=rec.get('ticker')
        if ticker not in EXPECTED:continue
        path=root/rec.get('raw_path','')
        if path.is_file() and digest(path)==rec.get('sha256'):
            valid[ticker]=rec
    missing=sorted(set(EXPECTED)-set(valid))
    if missing:blockers.append('Missing 13 checksum-verified raw responses: '+','.join(missing))
    if not processed.exists() or not report.exists():
        blockers.append('Missing the built common monthly returns and/or QA report')
    else:
        r=json.loads(report.read_text())
        if r.get('partition')!='estimation' or r.get('month_end')!='2022-12' or r.get('actual_months',0)<60:
            blockers.append('Inadequate pre-2023 estimation sample')
        if digest(processed)!=r.get('output_sha256'):blockers.append('Monthly-return output checksum mismatch')
    if not env.exists():
        blockers.append('Missing pinned GitHub installation evidence')
    else:
        try:
            installed = json.loads(env.read_text())
            if not installed.get('installed_source_verified') or installed.get('installed_git_commit_sha') != GITHUB_SHA:
                blockers.append('Pinned source installation not verified against Git commit')
        except (json.JSONDecodeError,OSError):
            blockers.append('Invalid GitHub installation evidence')
    if not model.exists():blockers.append('Provisional M2-03 model outputs not generated')
    state='PASS_TECHNICAL_REAL_DATA_GATES' if not blockers else 'BLOCKED'
    outcome={'gate':'M2-02_to_M2-03','status':state,'generated_utc':datetime.now(timezone.utc).isoformat(),
             'raw_successful_tickers':sorted(valid),'remaining_blockers':blockers,
             'reinvestment_and_full_fund_status':'NOT_DETERMINED',
             'initial_allocation_policy':'PROVISIONAL_NOT_FROZEN',
             'no_post_2022_selection_asserted':True,
             'warning':'A checksum checks local preservation, not Yahoo response authenticity or case-date vintage.'}
    write_json(root/'outputs/qa/github_workflow_gate.json',outcome)
    print(json.dumps(outcome,indent=2))
    return outcome

def main():
    p=argparse.ArgumentParser()
    p.add_argument('action',choices=['env','gate'])
    p.add_argument('--project-root',default=str(Path(__file__).resolve().parent.parent))
    args=p.parse_args()
    root=Path(args.project_root).resolve()
    if args.action=='env':environment(root)
    else:gate(root)
if __name__=='__main__':main()
