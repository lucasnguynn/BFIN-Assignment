#!/usr/bin/env python3
"""BFIN Kappa WS2026 Member 2 Gate M2-03: AUDITABLE portfolio diagnostics & risk-model comparison.

Only runs on genuine, verified Gate M2-02 archived yfinance returns. It NEVER downloads data
or manufactures returns. Forecasts/constraints here remain PROPOSED until group approval.
Benchmark VTI is excluded from optimization assets and is used as a single-index proxy.
No 2023-25 data are used anywhere in this module.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from audit_universe_metrics import ALL, ASSETS, BENCHMARK, STOCKS, ETFS, load_data, run_audit

SECTORS = {
    'AAPL': 'Information Technology', 'MSFT': 'Information Technology',
    'JPM': 'Financials', 'BAC': 'Financials',
    'JNJ': 'Health Care', 'PFE': 'Health Care',
    'PG': 'Consumer Staples', 'KO': 'Consumer Staples',
    'XOM': 'Energy', 'CAT': 'Industrials'
}


def digest(file: Path) -> str:
    return hashlib.sha256(Path(file).read_bytes()).hexdigest()


def require_verified_gate02(root: Path) -> tuple[Path, dict]:
    """Verify hashes of original 13 archived raw responses and the processed estimation output.
    This checks provenance consistency, not authenticity of remote provider content.
    """
    data_file = root/'data/processed/asset_monthly_returns_estimation.csv'
    alias = root/'data/processed/asset_monthly_returns.csv'
    report_file = root/'outputs/qa/M2_02_estimation_report.json'
    log_file = root/'data/raw/yahoo/source_manifest.jsonl'
    for p in (data_file, alias, report_file, log_file):
        if not p.is_file():
            raise RuntimeError(f'M2-02 blocked: required verified input is missing: {p}')
    report = json.loads(report_file.read_text(encoding='utf-8'))
    if report.get('status') != 'PASSED_SOURCE_INTEGRITY_AND_RETURN_COVERAGE' or report.get('partition') != 'estimation':
        raise ValueError('M2-02 verification report is not a passed estimation report')
    if digest(data_file) != report.get('output_sha256') or digest(alias) != digest(data_file):
        raise ValueError('M2-02 estimation return output hash or canonical alias disagrees')
    if report.get('number_verified_archived_sources') != len(ALL):
        raise ValueError('M2-02 expected archived 13 symbols')
    records = [json.loads(s) for s in log_file.read_text(encoding='utf-8').splitlines() if s.strip()]
    latest = {}
    for row in records:
        if row.get('partition') == 'estimation' and row.get('ticker') in ALL and row.get('status') == 'OK':
            latest[row['ticker']] = row
    if set(latest) != set(ALL):
        raise ValueError('Missing validated real yfinance raw archives')
    for ticker, row in latest.items():
        src = root/row.get('raw_path', '')
        if not src.is_file() or digest(src) != row.get('sha256'):
            raise ValueError(f'Archived raw response integrity check failed for {ticker}')
        if row.get('source') != 'Yahoo Finance via yfinance':
            raise ValueError(f'Unexpected source in manifest: {ticker}')
    if report.get('month_end') != '2022-12':
        raise ValueError('Post-2022 estimation is prohibited')
    return data_file, report


def read_approved_config(path: Path) -> dict:
    cfg = json.loads(path.read_text(encoding='utf-8'))
    if cfg.get('case_date') != '2022-12-31' or cfg.get('estimation_end') != '2022-12':
        raise ValueError('Wrong case date or estimation end')
    if cfg.get('benchmark') != 'VTI' or cfg.get('candidate_assets') != ASSETS:
        raise ValueError('Wrong benchmark/universe; follow formal change-control to alter')
    if cfg.get('expected_return_method') != 'sample_mean_shrunk_toward_VTI_sample_mean':
        raise ValueError('Unsupported/undeclared expected-return model')
    fields = ['historical_mean_weight','max_individual_stock_weight',
        'max_individual_equity_etf_weight','max_equity_etf_total_weight',
        'max_direct_stock_sector_weight']
    for k in fields:
        val = float(cfg[k])
        if not 0 <= val <= 1:
            raise ValueError(f'{k} must be a decimal in [0,1]')
    if cfg['risk_aversion_A'] <= 0:
        raise ValueError('A must be positive')
    return cfg


def forecast_monthly(data: pd.DataFrame, hist_weight: float) -> pd.Series:
    """Provisional, explicitly heuristic equity forecast; only pre-2023 sample inputs."""
    if not 0 <= hist_weight <= 1:
        raise ValueError('hist_weight outside [0,1]')
    sample_mu = data[ASSETS].mean()
    vti_anchor = float(data[BENCHMARK].mean())
    return hist_weight * sample_mu + (1.0 - hist_weight) * vti_anchor


def portfolio_constraints(cfg: dict):
    n = len(ASSETS)
    caps = np.array([float(cfg['max_individual_stock_weight']) if t in STOCKS else
                     float(cfg['max_individual_equity_etf_weight']) for t in ASSETS], dtype=float)
    etf_indices = np.array([ASSETS.index(t) for t in ETFS], dtype=int)
    sectors = sorted(set(SECTORS.values()))
    sector_indices = {s: np.array([ASSETS.index(t) for t in STOCKS if SECTORS[t] == s], dtype=int) for s in sectors}
    inequalities = []
    max_etf = float(cfg['max_equity_etf_total_weight'])
    max_sector = float(cfg['max_direct_stock_sector_weight'])
    inequalities.append({'type': 'ineq', 'fun': lambda w, inds=etf_indices, lim=max_etf: lim - w[inds].sum(),
                          'jac': lambda w, inds=etf_indices: -np.isin(np.arange(n), inds).astype(float)})
    for inds in sector_indices.values():
        inequalities.append({'type':'ineq','fun':lambda w,inds=inds,lim=max_sector:lim-w[inds].sum(),
                             'jac':lambda w,inds=inds:-np.isin(np.arange(n),inds).astype(float)})
    return caps, [{'type':'eq','fun': lambda w: w.sum()-1,
                   'jac':lambda w:np.ones(n)}]+inequalities,sector_indices


def check_weights(w: np.ndarray, cfg: dict, tol=2e-6) -> dict:
    w=np.asarray(w,float)
    if w.shape!=(len(ASSETS),) or not np.isfinite(w).all():
        raise ValueError('Invalid weight vector')
    caps,_,sector_idx=portfolio_constraints(cfg)
    violations={}
    if abs(w.sum()-1)>tol: violations['sum'] = float(w.sum())
    if (w < -tol).any(): violations['short'] = float(w.min())
    if (w-caps > tol).any(): violations['position'] = float((w-caps).max())
    etf_w=float(w[[ASSETS.index(t) for t in ETFS]].sum())
    if etf_w > float(cfg['max_equity_etf_total_weight'])+tol:
        violations['etf_total'] = etf_w
    sectors={s:float(w[ix].sum()) for s,ix in sector_idx.items()}
    for s, amount in sectors.items():
        if amount>float(cfg['max_direct_stock_sector_weight'])+tol:
            violations[f'sector_{s}'] = amount
    if violations: raise ValueError(f'Infeasible portfolio weights: {violations}')
    return {'sum':float(w.sum()), 'etf_total':etf_w, 'direct_sector_weights':sectors,
            'number_positive_holdings':int((w>1e-6).sum()),
            'hhi':float((w*w).sum()), 'max_weight':float(w.max())}


def optimize(mu_annual, covariance_annual, cfg:dict, A:float|None=None) -> tuple[np.ndarray,dict]:
    """Constrained long-only mean-variance utility; annual mu and variance must share units."""
    mu=np.asarray(mu_annual,float); sigma=np.asarray(covariance_annual,float)
    n=len(ASSETS)
    if mu.shape!=(n,) or sigma.shape!=(n,n): raise ValueError('Expected 12-asset mu and covariance')
    if not np.isfinite(mu).all() or not np.isfinite(sigma).all(): raise ValueError('Nonfinite model inputs')
    if not np.allclose(sigma,sigma.T,atol=1e-10): raise ValueError('Covariance is asymmetric')
    if np.linalg.eigvalsh(sigma).min() < -1e-9: raise ValueError('Covariance is not PSD')
    a=float(cfg['risk_aversion_A'] if A is None else A)
    if a<=0: raise ValueError('Risk-aversion must be positive')
    max_w,cons,_=portfolio_constraints(cfg)
    init=np.repeat(1/n,n)
    check_weights(init,cfg)
    def loss(w): return -(mu@w - 0.5*a*(w@sigma@w))
    def jac(w): return -(mu-a*sigma@w)
    result=minimize(loss,init,jac=jac,method='SLSQP',bounds=[(0,float(x)) for x in max_w],
                    constraints=cons,options={'maxiter':1500,'ftol':1e-12})
    if not result.success: raise RuntimeError(f'Optimizer did not converge: {result.message}')
    w=np.array(result.x,float)
    report=check_weights(w,cfg)
    if loss(w)>loss(init)+1e-8: raise RuntimeError('Optimization unexpectedly worse than feasible equal weights')
    report.update({'optimization_success':True,'utility':float(-loss(w)),
                   'risk_aversion':a,'solver':'scipy SLSQP','message':str(result.message)})
    return w,report


def risk_stats(w,mu_ann,cov_ann,A=3.0):
    mu=float(np.asarray(mu_ann)@w)
    var=float(w@np.asarray(cov_ann)@w)
    if var < -1e-9: raise ValueError('Negative portfolio variance')
    var=max(var,0.0)
    return {'expected_arithmetic_annual_return':mu,'annual_variance':var,
            'annual_volatility':math.sqrt(var),
            'utility':mu-0.5*A*var}


def compare_models(x, audit, cfg):
    """Core required comparison: one universe, forecast, objective and constraints; only Sigma differs."""
    _, sample_cov, _, si_cov, _, _, _ = audit
    mu_month=forecast_monthly(x,float(cfg['historical_mean_weight']))
    mu=12*mu_month.to_numpy()
    matrices={'sample':12*sample_cov.loc[ASSETS,ASSETS].to_numpy(),
              'single_index':12*si_cov.loc[ASSETS,ASSETS].to_numpy()}
    a=float(cfg['risk_aversion_A'])
    w_sample,diag_sample=optimize(mu,matrices['sample'],cfg,A=a)
    w_si,diag_si=optimize(mu,matrices['single_index'],cfg,A=a)
    w_ew=np.repeat(1/len(ASSETS),len(ASSETS))
    check_weights(w_ew,cfg)
    strategies={'recommended_candidate_sample':w_sample,
                'single_index_optimized':w_si,
                'rejected_candidate_equal_weight':w_ew}
    risk_rows=[]
    for key,w in strategies.items():
        for model,cov in matrices.items():
            risk_rows.append({'portfolio':key,'evaluation_covariance':model,
                              **risk_stats(w,mu,cov,a)})
    weights=pd.DataFrame({'ticker':ASSETS,**{k:w for k,w in strategies.items()}})
    risk=pd.DataFrame(risk_rows)
    forecast=pd.DataFrame({'ticker':ASSETS,'historical_mean_monthly':x[ASSETS].mean().to_numpy(),
         'benchmark_mean_monthly':float(x[BENCHMARK].mean()),
         'shrink_weight_historical':float(cfg['historical_mean_weight']),
         'forecast_arithmetic_monthly':mu_month.to_numpy(),
         'forecast_arithmetic_annual':mu})
    distances={'L1_sample_vs_SI':float(np.abs(w_sample-w_si).sum()),
               'maximum_position_difference':float(np.max(np.abs(w_sample-w_si))),
               'sample':diag_sample,'single_index':diag_si,
               'equal_weight':check_weights(w_ew,cfg)}
    return weights,risk,forecast,distances


def sensitivity(x,audit,cfg):
    _,s_cov,_,si_cov,_,_,_=audit
    mats={'sample':12*s_cov.to_numpy(),'single_index':12*si_cov.to_numpy()}
    output=[]
    for h in cfg['historical_mean_weight_sensitivity']:
        mu=12*forecast_monthly(x,float(h)).to_numpy()
        for a in cfg['risk_aversion_sensitivity']:
            for model,cov in mats.items():
                w,_=optimize(mu,cov,cfg,A=float(a))
                r=risk_stats(w,mu,cov,float(a))
                output.append({'historical_weight':h,'risk_aversion':a,'optimization_model':model,
                   'annual_expected_return':r['expected_arithmetic_annual_return'],
                   'annual_volatility':r['annual_volatility'],
                   'max_position':float(w.max()),
                   'hhi':float((w*w).sum()),
                   **{f'w_{t}':float(w[i]) for i,t in enumerate(ASSETS)}})
    return pd.DataFrame(output)


def risk_contributions(weights:pd.DataFrame, covariances:dict) -> pd.DataFrame:
    """Volatility risk contributions; signed contributions sum to portfolio volatility."""
    out=[]
    for name in ('recommended_candidate_sample','single_index_optimized','rejected_candidate_equal_weight'):
        w=weights[name].to_numpy(dtype=float)
        for risk_model, sigma in covariances.items():
            var=float(w@sigma@w)
            if var<=0: raise ValueError('Cannot allocate nonpositive volatility risk')
            vol=math.sqrt(var)
            component=w*(sigma@w)/vol
            if not np.isclose(component.sum(),vol,rtol=1e-8,atol=1e-10):
                raise RuntimeError('Component risk does not reconcile to portfolio volatility')
            for i,ticker in enumerate(ASSETS):
                out.append({'portfolio':name,'risk_model':risk_model,'ticker':ticker,
                    'weight':float(w[i]),'volatility_risk_contribution':float(component[i]),
                    'fraction_of_total_volatility':float(component[i]/vol),
                    'portfolio_volatility':vol})
    return pd.DataFrame(out)


def export_results(root,x,audit,cfg_path,cfg):
    output=root/'outputs/portfolio';output.mkdir(parents=True,exist_ok=True)
    metrics,sample_cov,corr,si_cov,resid_corr,pairs,model_qc=audit
    frames={'security_diagnostics.csv':metrics,'sample_covariance.csv':sample_cov,
      'correlation_matrix.csv':corr,'single_index_covariance.csv':si_cov,
      'single_index_residual_correlation.csv':resid_corr,'priority_pair_checks.csv':pairs}
    w,risk,forecast,comparison=compare_models(x,audit,cfg)
    cova={'sample':12*sample_cov.loc[ASSETS,ASSETS].to_numpy(),
          'single_index':12*si_cov.loc[ASSETS,ASSETS].to_numpy()}
    components=risk_contributions(w,cova)
    benchmark=pd.DataFrame([{'benchmark':'VTI',
          'historical_arithmetic_mean_annual':float(12*x[BENCHMARK].mean()),
          'historical_volatility_annual':float(np.sqrt(12)*x[BENCHMARK].std(ddof=1)),
          'note':'Descriptive 2015-22 historical benchmark, not a future return forecast or candidate holding'}])
    frames.update({'risk_contributions_PROVISIONAL.csv':components,
                   'benchmark_historical_reference_PROVISIONAL.csv':benchmark,
                   'weights_model_comparison_PROVISIONAL.csv':w,
                   'risk_model_comparison_PROVISIONAL.csv':risk,
                   'expected_returns_PROVISIONAL.csv':forecast,
                   'forecast_risk_sensitivity_PROVISIONAL.csv':sensitivity(x,audit,cfg)})
    manifests=[]
    for name,frame in frames.items():
        fp=output/name
        frame.to_csv(fp,index=frame.index.name is not None or name in
                     {'sample_covariance.csv','correlation_matrix.csv','single_index_covariance.csv',
                      'single_index_residual_correlation.csv'},float_format='%.12g')
        manifests.append({'output':str(fp.relative_to(root)),'sha256':digest(fp),
                          'owner':'Member 2','input_window':'2015-2022_or_documented_60plus'})
    # Export in-sample return series for M3, but do not call them frozen/approved or out-of-sample.
    w_sample=w['recommended_candidate_sample'].to_numpy()
    grow=x[ASSETS].to_numpy()@w_sample
    est=pd.DataFrame({'month':x.index.astype(str),'decimal_return':grow})
    est_path=output/'growth_returns_estimation_PROVISIONAL.csv'
    est.to_csv(est_path,index=False,float_format='%.12g')
    manifests.append({'output':str(est_path.relative_to(root)),'sha256':digest(est_path),
                      'owner':'Member 2','input_window':'pre_2023','interpretation':'in_sample_constant_target_weight_reconstruction_only'})
    status={'gate':'M2-03','technical_computation':'PASS_WITH_VERIFIED_INPUTS',
      'investment_policy_status':'PROVISIONAL_NOT_FROZEN_OR_AUTHORIZED',
      'primary_risk_model_comparison':'Same assets, means, A, constraints; only covariance estimator varies',
      'samples':{'n_months':len(x),'first_month':str(x.index[0]),'last_month':str(x.index[-1])},
      'expected_return_status':'HEURISTIC_2022_SAMPLE_ONLY',
      'risk_model_diagnostics':model_qc,'comparison_diagnostics':comparison,
      'configuration_path':str(cfg_path.relative_to(root)),
      'configuration_sha256':digest(cfg_path),
      'output_manifest':manifests,
      'quality_notes':['No claims of superior historical returns from optimizing on the same sample.',
           'VTI serves as benchmark/index proxy; Kenneth French market factor can differ.',
           'This growth-sleeve analysis cannot certify full-fund policy or 2030 attainment.',
           'ETF underlying sector exposures are not captured by direct-stock sector caps.',
           'No 2023-2025 evaluation is performed or consulted in this module.',
           'Provisional weights must not be labeled frozen/approved until group signs off.']}
    qa=root/'outputs/qa/M2_03_status.json';qa.parent.mkdir(parents=True,exist_ok=True)
    qa.write_text(json.dumps(status,indent=2)+'\n')
    return status


def run(root:Path, cfg_path:Path, rf_file:Path|None=None):
    data_file,gate02=require_verified_gate02(root)
    cfg=read_approved_config(cfg_path)
    start=gate02.get('month_start','2015-01')
    x,rf=load_data(data_file,start=start,end='2022-12',rf_path=rf_file)
    if len(x)!=gate02.get('actual_months'):
        raise ValueError('Return count inconsistent with archived M2-02 report')
    audit=run_audit(x,rf)
    result=export_results(root,x,audit,cfg_path,cfg)
    result['risk_free_data_status']='Genuine aligned RF supplied' if rf is not None else 'NOT_SUPPLIED; Sharpe metrics omitted rather than imputed'
    (root/'outputs/qa/M2_03_status.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'gate':'M2-03','technical_computation':result['technical_computation'],
                      'investment_policy_status':result['investment_policy_status'],
                      'n_months':len(x)},indent=2))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['run','status'])
    parser.add_argument('--project-root',default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument('--config',default='config/portfolio_assumptions_PROPOSED.json')
    parser.add_argument('--rf-file', help='Optional Member 3 French RF monthly CSV: month,RF in decimals; never substitute zero')
    args=parser.parse_args()
    root=Path(args.project_root).resolve()
    cfg_path=(root/args.config).resolve()
    if args.command=='status':
        try:
            file,rep=require_verified_gate02(root)
            print(json.dumps({'gate':'M2-03','input_status':'GATE02_VERIFIED','input_file':str(file),'window':rep.get('month_start')}))
        except Exception as exc:
            qa=root/'outputs/qa/M2_03_status.json';qa.parent.mkdir(parents=True,exist_ok=True)
            msg={'gate':'M2-03','status':'BLOCKED_PENDING_REAL_YFINANCE_INPUTS','reason':str(exc),
                 'no_real_analytics_performed':True}
            qa.write_text(json.dumps(msg,indent=2)+'\n')
            print(json.dumps(msg,indent=2))
    else:
        run(root,cfg_path,Path(args.rf_file).resolve() if args.rf_file else None)

if __name__=='__main__':
    main()
