"""All synthetic fixtures are generated within tests, never distributed as market observations."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from m2_portfolio_model import (ASSETS,ALL,forecast_monthly,check_weights,optimize,
    risk_stats,compare_models,sensitivity,require_verified_gate02,run,read_approved_config)
from audit_universe_metrics import load_data,run_audit

CFG_PATH=Path(__file__).resolve().parents[1]/'config/portfolio_assumptions_PROPOSED.json'

@pytest.fixture
def cfg():
    return read_approved_config(CFG_PATH)

@pytest.fixture
def x():
    rng=np.random.default_rng(20221016)
    months=pd.period_range('2015-01','2022-12',freq='M')
    market=rng.normal(0.006,0.036,len(months))
    frame={'VTI':market}
    for i,t in enumerate(ASSETS):
        frame[t]=(0.4+0.07*i)*market+rng.normal(0.002,0.024,len(months))
    return pd.DataFrame(frame,index=months)[ALL]

def test_exact_expected_return_shrink(cfg,x):
    m=forecast_monthly(x,0.25)
    assert np.allclose(m.to_numpy(),(0.25*x[ASSETS].mean()+0.75*x.VTI.mean()).to_numpy())
    assert np.allclose(forecast_monthly(x,1),x[ASSETS].mean())
    with pytest.raises(ValueError): forecast_monthly(x,-0.1)

def test_optimizer_obeys_all_investment_constraints(cfg,x):
    audit=run_audit(x)
    mean=12*forecast_monthly(x,0.25).to_numpy()
    for cov in [12*audit[1].to_numpy(),12*audit[3].to_numpy()]:
        w,diag=optimize(mean,cov,cfg)
        assert diag['optimization_success']
        assert abs(sum(w)-1)<1e-7
        assert w.min()>=-1e-7
        assert np.isfinite(risk_stats(w,mean,cov)['annual_volatility'])
        assert diag['etf_total']<=0.400001

def test_full_cross_model_comparison_and_alternative(cfg,x):
    a=run_audit(x)
    weights,risk,forecast,diagnostics=compare_models(x,a,cfg)
    assert len(weights)==12
    assert set(weights.columns)=={'ticker','recommended_candidate_sample','single_index_optimized','rejected_candidate_equal_weight'}
    assert len(risk)==6
    assert risk.groupby('portfolio').evaluation_covariance.nunique().eq(2).all()
    assert np.allclose(weights.rejected_candidate_equal_weight,1/12)
    assert len(forecast)==12
    assert diagnostics['L1_sample_vs_SI']>=0

def test_sensitivity_declared_grid(cfg,x):
    o=sensitivity(x,run_audit(x),cfg)
    assert len(o)==len(cfg['historical_mean_weight_sensitivity'])*len(cfg['risk_aversion_sensitivity'])*2
    assert o['annual_volatility'].ge(0).all()
    assert set(o.optimization_model)=={'sample','single_index'}

def test_infeasible_weights_rejected(cfg):
    w=np.zeros(12);w[0]=1
    with pytest.raises(ValueError):check_weights(w,cfg)

def test_negative_variance_and_non_psd_rejected(cfg):
    mean=np.ones(12)*0.07
    cov=np.eye(12)*0.02
    cov[0,0]=-0.01
    with pytest.raises(ValueError,match='PSD'): optimize(mean,cov,cfg)

def test_requires_verified_m2_02(tmp_path):
    with pytest.raises(RuntimeError,match='M2-02 blocked'):
        require_verified_gate02(tmp_path)

def write_fake_verified_gate02(tmp_path,x):
    """Test-only synthetic archive carrying the same structural hashes as Gate02 outputs."""
    root=tmp_path
    (root/'data/processed').mkdir(parents=True)
    (root/'data/raw/yahoo').mkdir(parents=True)
    (root/'outputs/qa').mkdir(parents=True)
    out=x.copy();out.index=out.index.astype(str);out.index.name='month';out=out.reset_index()
    processed=root/'data/processed/asset_monthly_returns_estimation.csv'
    alias=root/'data/processed/asset_monthly_returns.csv'
    out.to_csv(processed,index=False)
    alias.write_bytes(processed.read_bytes())
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    report={'status':'PASSED_SOURCE_INTEGRITY_AND_RETURN_COVERAGE','partition':'estimation',
            'output_sha256':sha(processed),'number_verified_archived_sources':13,
            'month_start':'2015-01','month_end':'2022-12','actual_months':96}
    (root/'outputs/qa/M2_02_estimation_report.json').write_text(json.dumps(report))
    manifest=[]
    for t in ALL:
        p=root/f'data/raw/yahoo/{t}_estimation_test_only.mock'
        p.write_bytes(('SYNTHETIC_TEST_FIXTURE:'+t).encode())
        manifest.append({'ticker':t,'partition':'estimation','source':'Yahoo Finance via yfinance',
                         'status':'OK','raw_path':str(p.relative_to(root)), 'sha256':sha(p)})
    (root/'data/raw/yahoo/source_manifest.jsonl').write_text('\n'.join(map(json.dumps,manifest))+'\n')
    (root/'config').mkdir()
    cp=root/'config/portfolio_assumptions_PROPOSED.json'
    cp.write_bytes(CFG_PATH.read_bytes())
    return root,cp,processed

def test_end_to_end_mocked_pipeline_and_status(x,tmp_path):
    root,cp,returns=write_fake_verified_gate02(tmp_path,x)
    out=run(root,cp)
    assert out['technical_computation']=='PASS_WITH_VERIFIED_INPUTS'
    assert out['investment_policy_status']=='PROVISIONAL_NOT_FROZEN_OR_AUTHORIZED'
    files={z['output'] for z in out['output_manifest']}
    assert 'outputs/portfolio/weights_model_comparison_PROVISIONAL.csv' in files
    assert 'outputs/portfolio/growth_returns_estimation_PROVISIONAL.csv' in files
    assert 'outputs/portfolio/forecast_risk_sensitivity_PROVISIONAL.csv' in files
    for row in out['output_manifest']:
        p=root/row['output']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']

def test_detects_tampered_monthly_returns(x,tmp_path):
    root,cp,processed=write_fake_verified_gate02(tmp_path,x)
    processed.write_text(processed.read_text()+'\n')
    with pytest.raises(ValueError,match='hash'):
        require_verified_gate02(root)

def test_detects_tampered_raw_archive(x,tmp_path):
    root,cp,processed=write_fake_verified_gate02(tmp_path,x)
    (root/'data/raw/yahoo/AAPL_estimation_test_only.mock').write_bytes(b'CHANGED')
    with pytest.raises(ValueError,match='integrity'):
        require_verified_gate02(root)

def test_rejects_post_cutoff_and_incomplete_months(x,tmp_path):
    path=tmp_path/'returns.csv'
    out=x.copy();out.index=out.index.astype(str);out.index.name='month';out.reset_index().to_csv(path,index=False)
    load_data(path,'2015-01','2022-12')
    bad=pd.read_csv(path)
    bad=bad[bad.month!='2019-01']
    bad.to_csv(path,index=False)
    with pytest.raises(ValueError,match='Missing months'):
        load_data(path,'2015-01','2022-12')
    with pytest.raises(ValueError):load_data(path,'2015-01','2023-01')

def test_model_beta_and_r_squared_against_constructed_known_model():
    from audit_universe_metrics import market_model
    m=np.array([-0.02,0.01,0.03,-0.04,0.08,0.02,0.05,-0.01,0.00,0.04],float)
    y=0.004+1.35*m
    result=market_model(y,m)
    assert abs(result['beta']-1.35)<1e-12
    assert abs(result['alpha']-0.004)<1e-12
    assert abs(result['r2']-1)<1e-12

def test_risk_contributions_add_to_volatility(cfg,x):
    from m2_portfolio_model import risk_contributions
    a=run_audit(x)
    weights,_,_,_=compare_models(x,a,cfg)
    cova={'sample':12*a[1].to_numpy(),'single_index':12*a[3].to_numpy()}
    rc=risk_contributions(weights,cova)
    assert len(rc)==3*2*12
    for _, group in rc.groupby(['portfolio','risk_model']):
        assert abs(group.volatility_risk_contribution.sum()-group.portfolio_volatility.iloc[0]) < 1e-9
        assert abs(group.fraction_of_total_volatility.sum()-1) < 1e-9
