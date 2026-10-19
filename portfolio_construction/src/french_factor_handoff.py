#!/usr/bin/env python3
"""Optional helper: fetch and archive monthly French FF3 from original Ken French ZIP.
Download is NOT executed by the offline rebuild. All generated 2022 decision
inputs are strictly restricted to 2015-2022. Later factor observations ignored.
"""
import argparse,datetime,hashlib,io,json,urllib.request,zipfile
from pathlib import Path
import pandas as pd

URL='https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip'

def download(root):
    root=Path(root);rawdir=root/'evidence';rawdir.mkdir(parents=True,exist_ok=True)
    request=urllib.request.Request(URL,headers={'User-Agent':'Kappa Foundation BFIN academic source retrieval'})
    with urllib.request.urlopen(request,timeout=30) as reply:raw=reply.read()
    zpath=rawdir/'Kenneth_French_FF3_original.zip';zpath.write_bytes(raw)
    meta={'source_url':URL,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw),
       'case_decision_cutoff':'2022-12','note':'Retrospectively retrieved factor history may itself be revised.'}
    (rawdir/'Kenneth_French_source.json').write_text(json.dumps(meta,indent=2)+'\n')
    return zpath

def build(root,rawzip):
    root=Path(root)
    with zipfile.ZipFile(rawzip) as z:
        names=z.namelist();csv=[x for x in names if x.lower().endswith('.csv')]
        if len(csv)!=1:raise ValueError(f'Expected one CSV in Kenneth French archive, got: {names}')
        lines=z.read(csv[0]).decode('latin1').splitlines()
    rows=[];started=False
    for line in lines:
        bits=[x.strip() for x in line.split(',')]
        if len(bits)>=5 and bits[0]=='' and bits[1]=='Mkt-RF':started=True;continue
        if not started:continue
        if bits[0] and len(bits[0])==6 and bits[0].isdigit() and len(bits)>=5:
            if '201501'<=bits[0]<='202212':
                rows.append({'month':f'{bits[0][:4]}-{bits[0][4:]}','Mkt-RF':float(bits[1])/100,
                    'SMB':float(bits[2])/100,'HML':float(bits[3])/100,'RF':float(bits[4])/100})
        elif rows:break
    out=pd.DataFrame(rows)
    if len(out)!=96 or out.month.iloc[0]!='2015-01' or out.month.iloc[-1]!='2022-12':
        raise ValueError(f'Monthly factor parse failed: {len(out)} months')
    dest=root/'outputs/French_FF3_monthly_2015_2022.csv'
    out.to_csv(dest,index=False,float_format='%.12g')
    print('Wrote 96 month decimal French factor handoff:',dest)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(Path(__file__).resolve().parent.parent));p.add_argument('--archive-only',action='store_true');p.add_argument('--saved-zip')
    args=p.parse_args();r=Path(args.root)
    path=Path(args.saved_zip) if args.saved_zip else download(r)
    if not args.archive_only:build(r,path)
