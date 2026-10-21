#!/usr/bin/env python3
"""Offline Kappa raw Yahoo -> 96 monthly returns -> risk models -> exact allocations.

This reads ONLY the team's October 2026 archived estimation responses, validates their
individual SHA-256 against the contemporaneous source manifest and an archive checksum,
then applies a restricted Python pickle allow-list. Never apply this to unknown pickles.
Run: python src/rebuild.py --root .
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,os,pickle,pickletools,sys,zipfile
from pathlib import Path
import numpy as np,pandas as pd
from portfolio_utils import ASSETS,MARKET,SECTORS,BOND_COST,GROWTH_BUDGET,ENTRY_COST,PURCHASE,F,parameters,optimize,measures,fixed_weight_threshold

EXPECTED_ARCHIVE='a8abafbc27be0ab5c1fe2d9c72138c770ac68ee7b441d2f43400e4019b9b972c'
EXPECTED_WORKBOOK='43c9baadb250fd5ed0329e5337d41757b2a7be9fc1d96f965bbd807a9e9ce939'
T=ASSETS+[MARKET]

# Restrict executable class/function loading in the specifically SHA-verified
# researcher-created DataFrame pickles; malicious pickle remains an intrinsic risk.
SAFE={'builtins':{'slice','set','frozenset','list','dict','tuple','range','complex','bytearray'},
  'numpy':{'dtype','ndarray'},'numpy._core.numeric':{'_frombuffer'},
  'numpy.core.numeric':{'_frombuffer'},'numpy._core.multiarray':{'_reconstruct','scalar'},
  'numpy.core.multiarray':{'_reconstruct','scalar'},'pandas.core.frame':{'DataFrame'},
  'pandas.core.series':{'Series'},'pandas.core.indexes.base':{'_new_Index','Index'},
  'pandas.core.indexes.multi':{'MultiIndex'},'pandas.core.indexes.datetimes':{'DatetimeIndex','_new_DatetimeIndex'},
  'pandas.core.internals.managers':{'BlockManager','SingleBlockManager'},
  'pandas._libs.internals':{'_unpickle_block'},'pandas._libs.arrays':{'__pyx_unpickle_NDArrayBacked'},'pandas.core.arrays.datetimes':{'DatetimeArray'},'pandas._libs.tslibs.timestamps':{'_unpickle_timestamp','Timestamp'},
  'pandas._libs.tslibs.nattype':{'NaTType'},'pandas._libs.tslibs.offsets':{'_get_offset'},
  'pandas._libs.tslibs.timezones':{'UTC'},'datetime':{'datetime','timedelta','timezone'}}
class CheckedPandasUnpickler(pickle.Unpickler):
    def find_class(self,module,name):
        if name not in SAFE.get(module,set()):
            raise pickle.UnpicklingError(f'Archived pickle uses unapproved class {module}.{name}')
        return super().find_class(module,name)

def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha_file(p):return sha_bytes(Path(p).read_bytes())

def raw_price_series(frame,ticker):
    if not isinstance(frame,pd.DataFrame) or not isinstance(frame.index,pd.DatetimeIndex):
        raise TypeError(f'{ticker}: archived Yahoo response must be date-indexed DataFrame')
    if frame.index.has_duplicates:raise ValueError(f'{ticker}: repeated daily dates')
    if isinstance(frame.columns,pd.MultiIndex):
        cols=[col for col in frame.columns if 'Adj Close' in tuple(map(str,col)) and ticker in tuple(map(str,col))]
        if len(cols)!=1:raise ValueError(f'{ticker}: missing or ambiguous adjusted close column: {cols}')
        raw=frame[cols[0]]
    else:
        if 'Adj Close' not in frame.columns:raise ValueError(f'{ticker}: missing adjusted close')
        raw=frame['Adj Close']
    values=pd.to_numeric(raw,errors='coerce')
    if values.isna().any() or (values<=0).any() or not np.isfinite(values.to_numpy(float)).all():
        raise ValueError(f'{ticker}: bad adjusted daily price, do not fill')
    values.index=values.index.tz_localize(None) if values.index.tz is not None else values.index
    values=values.sort_index()
    return values

def month_returns(frame,ticker):
    s=raw_price_series(frame,ticker)
    periods=pd.period_range('2014-12','2022-12',freq='M')
    eligible=s[(s.index>=pd.Timestamp('2014-12-01'))&(s.index<=pd.Timestamp('2022-12-31'))]
    grp=eligible.groupby(eligible.index.to_period('M'))
    month_end=grp.last().reindex(periods)
    actual_date=grp.apply(lambda s:s.index.max()).reindex(periods)
    if month_end.isna().any():raise ValueError(f'{ticker}: no month-end prices')
    for period,date in actual_date.items():
        if (period.end_time.normalize()-date.normalize()).days>7:
            raise ValueError(f'{ticker}: stale month end for {period}')
    r=month_end.pct_change(fill_method=None).iloc[1:]
    if r.isna().any() or not np.isfinite(r.to_numpy(float)).all() or (r<=-1).any():
        raise ValueError(f'{ticker}: invalid return')
    return pd.Series(r.to_numpy(float),index=periods[1:].astype(str),name=ticker)

def write_csv(df,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(path,index=False,float_format='%.17g')

def run(root):
    root=Path(root).resolve()
    out=root/'outputs';out.mkdir(exist_ok=True,parents=True)
    archive=root/'data/raw/yfinance_estimation_2015_2022.zip'
    if sha_file(archive)!=EXPECTED_ARCHIVE:raise ValueError('Original Yahoo archive modified')
    if sha_file(root/'evidence/bond_funding_model_pinned.xlsx')!=EXPECTED_WORKBOOK:raise ValueError('Bond funding workbook version differs')
    rec=[];responses={}
    with zipfile.ZipFile(archive) as z:
        manifest=pd.read_csv(io.BytesIO(z.read('data/source_manifest.csv')))
        if len(manifest)!=13 or manifest.ticker_or_dataset.nunique()!=13:raise ValueError('Expected exactly 13 sources')
        if (manifest.status!='OK').any() or (manifest.partition!='estimation').any():raise ValueError('Failed estimation retrieval present')
        for record in manifest.itertuples(index=False):
            t=record.ticker_or_dataset
            if t not in T:raise ValueError(f'Unexpected ticker {t}')
            raw=z.read(record.raw_filepath)
            if sha_bytes(raw)!=record.file_sha256:raise ValueError(f'{t}: raw checksum mismatch')
            if any(op.name in {'GLOBAL','EXT1','EXT2','EXT4','PERSID','BINPERSID'} for op,arg,pos in pickletools.genops(raw)):
                raise ValueError(f'{t}: pickle unexpected global/ext/persistent-ID instruction')
            frame=CheckedPandasUnpickler(io.BytesIO(raw)).load()
            responses[t]=month_returns(frame,t)
            rec.append({'ticker':t,'original_raw_sha256':record.file_sha256,'original_response_filepath':record.raw_filepath,
                        'download_utc':record.retrieval_datetime,'requested_start':record.requested_start,
                        'requested_end_exclusive':record.requested_end,'source':record.download_url,
                        'frequency':record.frequency,'version':record.package_version})
        reference=pd.read_csv(io.BytesIO(z.read('data/processed/asset_monthly_returns_estimation.csv')))
    df=pd.DataFrame({'month':[f'{y:04d}-{m:02d}' for y in range(2015,2023) for m in range(1,13)]})
    for t in T:df[t]=responses[t].reindex(df.month).to_numpy(float)
    if df.isna().any().any() or not df.month.equals(reference.month):raise ValueError('Misaligned monthly panel')
    diffs=(df[T].to_numpy(float)-reference[T].to_numpy(float))
    delta=float(np.max(np.abs(diffs)))
    if delta>3e-14:raise AssertionError(f'Raw->processed discrepancy max={delta}')
    write_csv(df,root/'data/processed/asset_monthly_returns_estimation.csv')
    write_csv(pd.DataFrame(rec),root/'evidence/yahoo_source_record.csv')
    mean,S,SI,beta,res=parameters(df)
    models={'Sample_MV_A3':optimize(mean,S,3),'Single_Index_MV_A3':optimize(mean,SI,3),
       'Minimum_Variance':optimize(mean,S,3,minvar=True),'Sample_MV_A6_sensitivity':optimize(mean,S,6)}
    frozen=pd.read_csv(root/'evidence/decision_weights_confirmed.csv').set_index('security').loc[ASSETS]['weight_of_growth_sleeve'].to_numpy(float)
    diff=float(np.max(np.abs(frozen-models['Sample_MV_A3'])))
    if diff>2e-7:raise AssertionError(f'Frozen A=3 weight differs: {diff}')
    weights=[];metrics=[]
    for label,w in models.items():
        for tick,weight in zip(ASSETS,w):weights.append({'policy':label,'ticker':tick,'growth_weight':weight,'equity_purchase_USD':weight*PURCHASE})
        row={'policy':label,**measures(w,mean,S,A=6 if 'A6' in label else 3)}
        row.update({'sample_covariance_vol':float(np.sqrt(w@S@w)), 'single_index_covariance_vol':float(np.sqrt(w@SI@w))})
        metrics.append(row)
    write_csv(pd.DataFrame(weights),out/'policy_weights.csv')
    write_csv(pd.DataFrame(metrics),out/'portfolio_comparison.csv')
    write_csv(pd.DataFrame({'ticker':ASSETS,'beta_to_VTI':beta,'annual_arithmetic_mean':12*df[ASSETS].mean().to_numpy(),
       'annual_volatility':(12*df[ASSETS].cov().to_numpy().diagonal())**.5}),out/'security_diagnostics.csv')
    write_csv(pd.DataFrame(S,index=ASSETS,columns=ASSETS).rename_axis('ticker').reset_index(),out/'sample_covariance_annual.csv')
    write_csv(pd.DataFrame(SI,index=ASSETS,columns=ASSETS).rename_axis('ticker').reset_index(),out/'single_index_covariance_annual.csv')
    static=pd.DataFrame({'month':df.month,'growth_static_exposure_monthly':df[ASSETS].to_numpy()@frozen,
                        'rejected_minvar_static_exposure_monthly':df[ASSETS].to_numpy()@models['Minimum_Variance'],
                        'MSFT_monthly':df.MSFT,'PG_monthly':df.PG,'VTI_monthly':df.VTI})
    write_csv(static,out/'growth_static_exposure_returns.csv')
    # Compare frozen fixed weights with contemporaneously simulated alternatives; infer vs reoptimize explicitly.
    h=12*df[ASSETS].mean().to_numpy();prior=np.full(12,12*df.VTI.mean());minw=models['Minimum_Variance'];
    lam_star=fixed_weight_threshold(frozen,minw,h,prior,S,3)
    dr=float((frozen-minw)@mean)
    dv=float(frozen@S@frozen-minw@S@minw)
    Astar=2*dr/(F*dv)
    sensitivity=pd.DataFrame([{'test':'Historical-mean prior weight lambda, two fixed policies','threshold':lam_star,
       'base_assumption':.25,'interpretation':'Min variance preferred below threshold under fund A=3'},
       {'test':'Foundation risk aversion A, two fixed policies','threshold':Astar,'base_assumption':3,
       'interpretation':'Min variance preferred above threshold at lambda=.25'}])
    write_csv(sensitivity,out/'fixed_weight_reversal.csv')
    # Independent time-sequenced diagnostic, not a truly unseen out of sample test.
    X=df[ASSETS].to_numpy(float);m=df.VTI.to_numpy(float)
    train= pd.DataFrame({'month':df.month.iloc[:60].tolist(),**{t:df[t].iloc[:60].to_numpy() for t in T}})
    # parameters() requires full 96 months by design; proper 60-month time-series diagnostic uses explicit subset.
    tx=train[ASSETS].to_numpy();tm=train.VTI.to_numpy()
    tm_mu=12*(.25*tx.mean(0)+.75*tm.mean());tcov=12*np.cov(tx,rowvar=False,ddof=1)
    tw=optimize(tm_mu,tcov,3); mintrain=optimize(tm_mu,tcov,3,minvar=True)
    validation=[]
    for tag,w in [('Sample_MV_caps15_30',tw),('MinVar_caps15_30',mintrain),('Equal_Weight',np.ones(12)/12)]:
        ret=X[60:]@w
        wealth=np.cumprod(1+ret); wealth=np.r_[1,wealth]
        validation.append({'policy':tag,'years':'2020-2022 diagnostic, constructed retrospectively',
            'annualized_geometric_growth':float(wealth[-1]**(1/3)-1),
            'max_drawdown':float((wealth/np.maximum.accumulate(wealth)-1).min()),
            'annualized_volatility':float(np.std(ret,ddof=1)*np.sqrt(12))})
    write_csv(pd.DataFrame(validation),out/'pre2023_chronological_diagnostic.csv')
    # Bond and equity stress calculations are illustrative 2022 decision-date repricing,
    # never a fabricated 2023-2025 bond quote series.
    from scipy.optimize import brentq
    yf_beta=(1000/922.78)**(1/2)-1
    def delta_price(y):return sum(35/(1+y)**t for t in range(1,6))+1000/(1+y)**5
    yf_delta=brentq(lambda y:delta_price(y)-986.07,-.5,.5)
    beta_shock=2400*1000/(1+yf_beta+.01)**2
    delta_shock=3600*delta_price(yf_delta+.01)
    bond_change=beta_shock+delta_shock-BOND_COST
    fee=GROWTH_BUDGET-PURCHASE
    uniform=-.30
    sector_shocks={'AAPL':-.45,'MSFT':-.45,'JPM':-.30,'BAC':-.30,
       'JNJ':-.20,'PFE':-.20,'PG':-.10,'KO':-.10,'XOM':-.20,'CAT':-.40,
       'VTV':-.25,'IWM':-.40}
    scenarios=[]
    for modelname,ww in [('Sample_MV_A3',frozen),('Minimum_Variance',models['Minimum_Variance']),('Sample_MV_A6_sensitivity',models['Sample_MV_A6_sensitivity'])]:
        for name,shock,rateshift in [('Equity -30%, constant bond yields',uniform,0),
                ('Equity -30%, bond yields +100bp',uniform,1),
                ('Sector selloff, bond yields +100bp',sum(ww[i]*sector_shocks[t] for i,t in enumerate(ASSETS)),1)]:
            change= (-fee+PURCHASE*shock+(bond_change if rateshift else 0))/12_000_000
            scenarios.append({'policy':modelname,'scenario':name,'foundation_valuation_return':change,
                'foundation_loss_pct_of_initial_capital':-100*change,
                'equity_purchase_cost_included':fee,'bond_value_delta_USD':bond_change if rateshift else 0})
    write_csv(pd.DataFrame(scenarios),out/'bond_equity_instantaneous_stress.csv')
    tgt=8_000_000*(1.023)**8
    hurdle=((tgt-630_000)/PURCHASE)**(1/8)-1
    write_csv(pd.DataFrame([{'initial_foundation_USD':12_000_000,'target_real_2022_USD':8_000_000,
       'inflation_assumed':.023,'2030_nominal_hurdle_USD':tgt,
       'retained_delta_coupon_cash_USD':630_000,'net_equity_purchase_USD':PURCHASE,
       'required_equity_8yr_geometric_CAGR':hurdle}]),out/'2030_hurdle.csv')
    # Factor-independent security diagnostics and residual overlap from the same panel.
    rr=np.corrcoef(res,rowvar=False)
    diag=[]
    for i,t in enumerate(ASSETS):
        vol=float(np.std(X[:,i],ddof=1)*np.sqrt(12))
        beta_i=float(beta[i]);r2=float(np.corrcoef(X[:,i],m)[0,1]**2)
        rc=float(frozen[i]*(S@frozen)[i]/(frozen@S@frozen))
        diag.append({'ticker':t,'growth_weight':frozen[i],'market_beta_to_VTI':beta_i,
         'market_regression_R_squared':r2,'annual_volatility':vol,'risk_variance_contribution_fraction':rc})
    write_csv(pd.DataFrame(diag),out/'security_beta_r2_risk_contributions.csv')
    pairs=[]
    for i in range(len(ASSETS)):
        for j in range(i+1,len(ASSETS)):
            pairs.append({'ticker1':ASSETS[i],'ticker2':ASSETS[j],
                          'residual_corr_after_VTI':rr[i,j]})
    write_csv(pd.DataFrame(pairs).sort_values('residual_corr_after_VTI',ascending=False),out/'single_index_residual_overlap.csv')
    # Grid includes exactly the sample and single-index risk models on the same 12 assets/caps.
    grid=[]
    for la in [0,.05,.10,.25,.50]:
        ml=12*(la*X.mean(0)+(1-la)*m.mean())
        for af in [3,6]:
            for riskname,cov in [('sample',S),('single_index',SI)]:
                sol=optimize(ml,cov,af)
                row={'history_weight_lambda':la,'foundation_risk_aversion':af,
                     'risk_model':riskname,**measures(sol,ml,S,af)}
                row['number_positive_assets']=int((sol>1e-8).sum())
                row['maximum_single_stock_weight']=float(sol[:10].max())
                grid.append(row)
    write_csv(pd.DataFrame(grid),out/'forecast_model_and_A_sensitivity.csv')
    # Separate covariance and concentration challenger: these are comparisons, NOT a retroactive policy replacement.
    looser=optimize(mean,S,3,stockcap=.20,sectorcap=.35)
    equal=np.ones(12)/12
    compare=[]
    for key,w in [('selected_cap15_sector30',frozen),('looser_cap20_sector35',looser),('equal_12_candidate_assets',equal)]:
        row={'candidate':key,**measures(w,mean,S,3)}
        row['max_two_stock_weight']=float(sum(sorted(w[:10],reverse=True)[:2]))
        compare.append(row)
    write_csv(pd.DataFrame(compare),out/'concentration_cap_challenge.csv')
    # Moving block bootstrap: retrospective robustness only, fixed universe selected in 2026.
    rng=np.random.default_rng(20222026); bw=[]
    for k in range(120):
        blocks=[(int(a)+np.arange(6))%96 for a in rng.integers(0,96,size=16)]
        inds=np.concatenate(blocks)
        bx=X[inds]; bm=m[inds]
        bmu=12*(.25*bx.mean(0)+.75*bm.mean()); bS=12*np.cov(bx,rowvar=False,ddof=1)
        ww=optimize(bmu,bS,3)
        bw.append(ww)
    bws=np.array(bw)
    write_csv(pd.DataFrame({'ticker':ASSETS,'selection_frequency':(bws>1e-8).mean(0),
       'mean_weight':bws.mean(0),'p10_weight':np.quantile(bws,.1,axis=0),
       'p90_weight':np.quantile(bws,.9,axis=0),
       'individual_stock_cap_binding_frequency':[(bws[:,i]>=.149999).mean() if i<10 else np.nan for i in range(12)]}),out/'moving_block_bootstrap_120.csv')
    qa={'status':'PASS','raw_archived_response_count':13,'months':96,'raw_to_existing_processed_max_absolute_difference':delta,
       'frozen_vs_rebuilt_weight_max_absolute_difference':diff,'frozen_policy':'Sample_MV_A3_15pct_stock_30pct_sector',
       'zip_sha256':EXPECTED_ARCHIVE,'funding_workbook_sha256':EXPECTED_WORKBOOK,
       'notes':['The 2022 policy remains a retrospective exercise; adjusted prices retrieved in 2026 can be revised.',
                'Restricted unpickling was used ONLY after archived file hashes were checked; never load arbitrary pickle files.',
                'No post-2022 observations were read or calculated.','Case bonds have no true historical market quotes.']}
    (root/'qa/rebuild_report.json').write_text(json.dumps(qa,indent=2)+'\n')
    print(json.dumps(qa,indent=2))
    print('Portfolio metrics:',pd.DataFrame(metrics).to_string(index=False))
    print('Decision reversal:',sensitivity.to_string(index=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',default=str(Path(__file__).resolve().parent.parent));args=parser.parse_args()
    run(args.root)
