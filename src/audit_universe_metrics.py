#!/usr/bin/env python3
"""Member 2 empirical universe audit, using ONLY archived historical MONTHLY total returns.

This program does not fetch data, choose securities, optimize portfolios, or infer missing returns.
The original Yahoo Finance retrieval step must be executed separately using yfinance,
with original responses and source manifest retained for the course submission.

Input: one CSV with columns month (YYYY-MM) and AAPL, MSFT, JPM, BAC, JNJ,
PFE, PG, KO, XOM, CAT, VTV, IWM, VTI; values are simple total returns as decimals.
Optional: Kenneth French monthly risk-free CSV containing month,RF (decimal).
For non-2015-start windows: use --start YYYY-MM, within 2015-01 to 2022-12.
The sample must end in December 2022 and contain at least 60 complete common months.

Outputs are diagnostic evidence, NOT a mechanical accept/reject stock selector.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import t as student_t

STOCKS = ['AAPL','MSFT','JPM','BAC','JNJ','PFE','PG','KO','XOM','CAT']
ETFS = ['VTV','IWM']
BENCHMARK = 'VTI'
ASSETS = STOCKS + ETFS
ALL = ASSETS + [BENCHMARK]
FOCUS_PAIRS = [('AAPL','MSFT'),('JPM','BAC'),('JNJ','PFE'),('PG','KO'),('JPM','VTV'),('PG','VTV'),('IWM','VTI')]


def load_data(csv_path, start='2015-01', end='2022-12', rf_path=None):
    if not ('2015-01' <= start <= '2022-12') or end != '2022-12':
        raise ValueError('Estimation must lie within Jan 2015-Dec 2022 and end Dec 2022.')
    raw = pd.read_csv(csv_path, dtype={'month': str})
    if 'month' not in raw.columns or raw['month'].duplicated().any():
        raise ValueError('A unique YYYY-MM month key is required.')
    missing_cols = sorted(set(ALL) - set(raw.columns))
    if missing_cols: raise ValueError('Missing requested assets: '+', '.join(missing_cols))
    try:
        p = pd.PeriodIndex(raw['month'], freq='M')
    except Exception as exc:
        raise ValueError('month must be YYYY-MM') from exc
    if any(p.astype(str) != raw['month'].to_numpy()):
        raise ValueError('month must use exactly YYYY-MM format')
    x=raw.set_index(p).drop(columns=['month']).sort_index()
    x=x.loc[start:end, ALL].apply(pd.to_numeric, errors='raise')
    if x.empty or str(x.index[-1]) != end:
        raise ValueError('December 2022 observation is required.')
    months=pd.period_range(start, end, freq='M')
    absent=months.difference(x.index)
    if len(absent):
        raise ValueError('Missing months (do not impute): '+', '.join(map(str,absent[:12])))
    if x.isna().any().any():
        failures=x.isna().sum(); raise ValueError('Missing asset returns (do not impute): '+str(failures[failures>0].to_dict()))
    if not np.isfinite(x.to_numpy()).all(): raise ValueError('Non-finite return observed')
    if (x <= -1).any().any(): raise ValueError('A monthly simple return <= -100% requires investigation')
    if len(x)<60: raise ValueError('Fewer than 60 common monthly return observations')
    rf=None
    if rf_path:
        d=pd.read_csv(rf_path,dtype={'month':str})
        if 'RF' not in d or 'month' not in d: raise ValueError('RF file requires month,RF')
        if d.month.duplicated().any(): raise ValueError('Duplicate RF months')
        rd=d.set_index(pd.PeriodIndex(d.month,freq='M'))['RF'].astype(float)
        rf=rd.reindex(x.index)
        if rf.isna().any(): raise ValueError('Risk-free monthly rate missing; do not default to zero')
    return x,rf


def market_model(y, m):
    """Single-index OLS with intercept on *simple total returns* for covariance estimation."""
    n=len(y); X=np.column_stack([np.ones(n), m]); b=np.linalg.lstsq(X,y,rcond=None)[0]
    resid=y-X@b; var_y=np.var(y, ddof=1); sse=resid@resid; sst=(n-1)*var_y
    if sst <= 0: raise ValueError('Zero asset variance')
    if np.var(m,ddof=1)<=0: raise ValueError('Zero market variance')
    inv=np.linalg.inv(X.T@X)
    se=np.sqrt((sse/(n-2))*np.diag(inv))
    critical=student_t.ppf(0.975, n-2)
    return {'alpha':float(b[0]),'beta':float(b[1]),'r2':float(1-sse/sst),
            'beta_se':float(se[1]),'beta_ci_low':float(b[1]-critical*se[1]),
            'beta_ci_high':float(b[1]+critical*se[1]),
            'residual_std_monthly':float(np.sqrt(sse/(n-2))),
            'resid':resid}


def run_audit(x, rf=None):
    n=len(x); m=x[BENCHMARK].to_numpy(); res={}
    rows=[]
    for ticker in ASSETS:
        a=x[ticker].to_numpy(); r=market_model(a,m); res[ticker]=r
        years=n/12; annual_arith=float(12*a.mean()); ann_sd=float(np.std(a,ddof=1)*np.sqrt(12))
        cagr=float(np.prod(1+a)**(1/years)-1)
        beta=r['beta']; r2=r['r2']
        row={'ticker':ticker,'n_common_months':n,'annual_arithmetic_mean':annual_arith,
            'sample_cagr':cagr,'annualized_std':ann_sd,'annualized_downside_semideviation':float(np.sqrt(12*np.mean(np.minimum(a,0)**2))),
            'minimum_monthly_return':float(np.min(a)),'maximum_monthly_return':float(np.max(a)),
            'market_beta_VTI':beta,'market_beta_standard_error_OLS':r['beta_se'],
            'market_beta_95CI_low':r['beta_ci_low'],'market_beta_95CI_high':r['beta_ci_high'],
            'market_only_R_squared':r2,'market_correlation_VTI':float(np.corrcoef(a,m)[0,1]),
            'residual_std_monthly':r['residual_std_monthly'],'monthly_market_model_alpha_descriptive':r['alpha']}
        if rf is not None:
            prem=a-rf.to_numpy()
            excess_ann=float(np.mean(prem)*12)
            row['annualized_excess_return_arithmetic']=excess_ann
            row['historical_sharpe_arithmetic']=float(excess_ann/ann_sd)
        else:
            row['annualized_excess_return_arithmetic']=None
            row['historical_sharpe_arithmetic']=None
        # Stability diagnostic: first/second subperiod, both are within pre-2023 sample.
        z=x[ticker]; mr=x[BENCHMARK]; a0=z.index <= pd.Period('2019-12'); a1=z.index >= pd.Period('2020-01')
        row['beta_2015_2019']=float(market_model(z[a0].to_numpy(),mr[a0].to_numpy())['beta']) if a0.sum()>=24 else None
        row['beta_2020_2022']=float(market_model(z[a1].to_numpy(),mr[a1].to_numpy())['beta']) if a1.sum()>=24 else None
        rows.append(row)
    metrics=pd.DataFrame(rows)
    sample_cov=x[ASSETS].cov()
    corr=x[ASSETS].corr()
    betas=np.array([res[t]['beta'] for t in ASSETS]); market_var=float(x[BENCHMARK].var(ddof=1))
    # With intercept, residuals are orthogonal to VTI. Classical SI covariance assumes uncorrelated residuals.
    si_cov=np.outer(betas,betas)*market_var
    # Use unbiased residual variance for variance of raw asset returns, sigma^2_e with ddof=1.
    resids=np.column_stack([res[t]['resid'] for t in ASSETS]); resid_var=resids.var(axis=0,ddof=1)
    si_cov+=np.diag(resid_var)
    si_cov=pd.DataFrame(si_cov,index=ASSETS,columns=ASSETS)
    resid_corr=pd.DataFrame(np.corrcoef(resids,rowvar=False),index=ASSETS,columns=ASSETS)
    pairs=[]
    for i,j in FOCUS_PAIRS:
        # VTI not included in si covariance but part of focus pair market comparison
        c=float(x[i].corr(x[j]))
        ec=float(resid_corr.loc[i,j]) if i in res and j in res else None
        pairs.append({'asset_1':i,'asset_2':j,'monthly_correlation':c,
                      'residual_correlation_after_VTI':ec,
                      'flag_strong_total_correlation_abs_ge_0p80':abs(c)>=0.8,
                      'flag_strong_residual_correlation_abs_ge_0p50':abs(ec)>=0.5 if ec is not None else None,
                      'comment':'FLAG = analyst review only, not an automatic exclusion criterion'})
    pairs=pd.DataFrame(pairs)
    diffs=(sample_cov-si_cov)
    summary={'status':'REAL_INPUT_METRICS_UNVERIFIED_SOURCE_ORIGIN_MUST_BE_AUDITED',
             'note':'This script cannot certify that supplied CSV was genuinely derived from Yahoo Finance.',
             'period_start':str(x.index[0]),'period_end':str(x.index[-1]),
             'n_months':n,'candidate_stock_count':len(STOCKS),'candidate_etf_count':len(ETFS),
             'benchmark':BENCHMARK,'risk_model_market_proxy':BENCHMARK,
             'factor_CAPM_market_may_differ':'M3 uses Kenneth French Mkt-RF for FF3; do not silently equate it to VTI',
             'maximum_pairwise_covariance_discrepancy':float(np.abs(diffs.to_numpy()).max()),
             'number_high_correlation_focus_pairs':int(pairs.flag_strong_total_correlation_abs_ge_0p80.sum()),
             'sample_cov_min_eigenvalue':float(np.linalg.eigvalsh(sample_cov).min()),
             'si_cov_min_eigenvalue':float(np.linalg.eigvalsh(si_cov).min()),
             'missing_rf':rf is None,
             'interpretation':'All flags trigger qualitative review and controlled portfolio comparisons, not automatic stock removal.'}
    return metrics,sample_cov,corr,si_cov,resid_corr,pairs,summary


def main():
    p=argparse.ArgumentParser(); p.add_argument('--monthly-returns',required=True)
    p.add_argument('--rf-monthly'); p.add_argument('--start',default='2015-01')
    p.add_argument('--out',required=True); args=p.parse_args()
    x,rf=load_data(args.monthly_returns,args.start,rf_path=args.rf_monthly)
    results=run_audit(x,rf)
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    names=['security_diagnostics.csv','sample_covariance.csv','correlation_matrix.csv','single_index_covariance.csv',
           'single_index_residual_correlation.csv','priority_pair_checks.csv']
    for frame,path in zip(results[:6],names):frame.to_csv(out/path, index=frame.index.name is not None or path not in (names[0],names[-1]))
    (out/'quantitative_audit.json').write_text(json.dumps(results[-1],indent=2)+'\n')
    print(json.dumps(results[-1],indent=2))

if __name__=='__main__':main()
