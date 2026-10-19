#!/usr/bin/env python3
"""Offline integrity/chronology checks for case-date evidence; NOT a replacement for SEC original-byte archival."""
import argparse,csv,hashlib,json
from pathlib import Path
ASSETS={'AAPL','MSFT','JPM','BAC','JNJ','PFE','PG','KO','XOM','CAT','VTV','IWM','VTI'}
STOCKS={'AAPL','MSFT','JPM','BAC','JNJ','PFE','PG','KO','XOM','CAT'}
ETFS={'VTV','IWM'}
def validate(root):
    root=Path(root)
    fp=root/'evidence/SEC_CASE_DATE_WEB_VERIFICATION_20261018.csv'
    with fp.open(encoding='utf8',newline='') as f: rows=list(csv.DictReader(f))
    errors=[]
    def must(condition,msg):
        if not condition: errors.append(msg)
    tickers=[r['ticker'] for r in rows]
    must(len(rows)==13,'Must contain 13 source decisions')
    must(set(tickers)==ASSETS,'Candidate tickers or benchmark changed')
    must(len(tickers)==len(set(tickers)),'Duplicate tickers')
    must(all(r['original_bytes_archived']=='NO' and not r['original_sha256'] for r in rows),
         'Web verification is not SEC-original-byte archival: no fabricated hashes permitted')
    for r in rows:
        t=r['ticker'];date=r['filing_date_as_recorded']
        must('2015-01-01'<=date<='2022-12-31',f'{t} filing date after case cutoff')
        must(r['primary_sec_url'].startswith('https://www.sec.gov/Archives/edgar/'),f'{t}: invalid SEC source')
        must(r['verification_level_20261018'] in {
          'PRIMARY_DOCUMENT_OPENED','SEC_INDEX_OPENED','REGISTER_NOT_INDEPENDENTLY_REVERIFIED',
          'SEC_INDEX_AND_2019_PRIMARY_PROSPECTUS_OPENED','SEC_INDEX_AND_2022_SECONDARY_DESCRIPTION_OPENED',
          '2021_PRIMARY_PROSPECTUS_OPENED'},f'{t}: unrecognized evidence status')
        must(r['case_cutoff_test']=='PASS_RECORDED_DATE',f'{t}: unverified recorded chronology')
    for t in STOCKS: must(next(r for r in rows if r['ticker']==t)['asset_type']=='US_COMMON_STOCK',f'{t}: stock class changed')
    must(all(next(r for r in rows if r['ticker']==t)['supplemental_pre2023_url'].startswith('https://www.sec.gov/') for t in ETFS),'Pre-2023 ETF mandate evidence missing')
    yzip=root/'data/raw/yfinance_estimation_2015_2022.zip'
    must(yzip.is_file() and yzip.stat().st_size>100000,'Original Yahoo archive missing')
    report={'status':'PASS' if not errors else 'FAIL','ticker_count':len(rows),'stock_count':len(STOCKS),
            'candidate_etfs':sorted(ETFS),'comparator':'VTI','raw_sec_byte_archival':'INCOMPLETE',
            'pre_2023_case_date_register':'PRESENT','errors':errors,
            'yahoo_archive_sha256':hashlib.sha256(yzip.read_bytes()).hexdigest() if yzip.exists() else None}
    return report
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',default=str(Path(__file__).resolve().parent.parent));args=ap.parse_args()
    r=validate(args.root);print(json.dumps(r,indent=2));raise SystemExit(0 if r['status']=='PASS' else 1)
