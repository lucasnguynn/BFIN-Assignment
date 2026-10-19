#!/usr/bin/env python3
"""Optional evidence fetch on a network-enabled machine. Does not run during offline model rebuild.

Uses only pre-2023 URLs already listed in the eligibility register. SEC may rate-limit;
never create a fake archived document or SHA on failure.
"""
import argparse,hashlib,time,urllib.request,urllib.parse
from pathlib import Path
import pandas as pd

def run(root,user_agent):
    root=Path(root);dest=root/'evidence/sec_originals';dest.mkdir(exist_ok=True,parents=True)
    reg=pd.read_csv(root/'evidence/security_eligibility_2022.csv').fillna('')
    log=[]
    for row in reg.itertuples(index=False):
        t=row.ticker; date=str(row.public_filing_date)
        url=str(row.primary_document_url)
        entry={'ticker':t,'filing_date':date,'url':url,'status':'FAILED','sha256':'','file_path':'','error':''}
        try:
            if not date or date>'2022-12-31':raise ValueError('Not confirmed available before case cutoff')
            p=urllib.parse.urlparse(url)
            if p.scheme!='https' or p.netloc!='www.sec.gov':raise ValueError('Primary archival URL not SEC HTTPS')
            q=urllib.request.Request(url,headers={'User-Agent':user_agent,'Accept':'text/html,application/pdf,*/*'})
            with urllib.request.urlopen(q,timeout=30) as resp:
                body=resp.read(40_000_001)
                if len(body)>40_000_000:raise ValueError('File too large')
                ct=resp.headers.get('Content-Type','')
                if len(body)<300 or ('html' not in ct and 'pdf' not in ct):raise ValueError('Non-document SEC response')
            if b'Access Denied' in body[:300] or b'Your Request Originates' in body[:1000]:raise ValueError('SEC access throttled')
            ext='.pdf' if body.startswith(b'%PDF') else '.html'
            rel=Path('evidence/sec_originals')/f'{t}_{date}{ext}'
            (root/rel).write_bytes(body)
            entry.update(status='ARCHIVED',sha256=hashlib.sha256(body).hexdigest(),file_path=str(rel))
        except Exception as exc:entry['error']=f'{type(exc).__name__}: {exc}'
        log.append(entry)
        time.sleep(.15)
    pd.DataFrame(log).to_csv(root/'evidence/sec_archival_status.csv',index=False)
    n=sum(x['status']=='ARCHIVED' for x in log)
    print(f'Archived {n}/{len(log)} pre-2023 issuer documents; failures are reported, not hidden.')
    if n!=len(log):raise SystemExit(2)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(Path(__file__).resolve().parent.parent));p.add_argument('--user-agent',required=True,help='Your real academic research contact string, e.g., institution plus email');a=p.parse_args()
    run(Path(a.root),a.user_agent)
