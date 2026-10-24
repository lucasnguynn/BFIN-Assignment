#!/usr/bin/env python3
"""M2-to-M3 2022-cutoff scenario handoff; NO realized 2023-25 returns."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from m1_integration import ROOT, run as run_m2, ASSETS, load_estimation

MONTHS=[f"{y}-{m:02d}" for y in range(2015,2023) for m in range(1,13)]
SCENARIOS={"ORIGINAL_FROZEN","REVISED_M1_PRINCIPAL_MATCHING","REVISED_M1_COUPON_FUNDING"}
PORTFOLIOS={"FROZEN_SAMPLE_MV","REOPTIMIZED_SAMPLE_MV_A3",
            "REOPTIMIZED_SINGLE_INDEX_MV_A3","CONSTRAINED_MINIMUM_VARIANCE",
            "REOPTIMIZED_SAMPLE_MV_A6"}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def build(out,portfolio_root=ROOT):
    out=Path(out); portfolio_root=Path(portfolio_root)
    source=out/"m2_calculations"
    out.mkdir(parents=True,exist_ok=True)
    run_m2(source)
    series=pd.read_csv(source/"growth_static_returns_2015_2022.csv")
    weights=pd.read_csv(source/"exact_allocations.csv")
    if series.month.tolist()!=MONTHS:
        raise ValueError("M3 handoff would breach 2022 cutoff / month completeness")
    if len(series.columns)!=16 or series.columns.duplicated().any():
        raise ValueError("Expected 15 distinct policy series plus month")
    panel,frozen=load_estimation()
    baseline=(panel[ASSETS].to_numpy(float)@frozen)
    for scen in SCENARIOS:
        key=scen+"__FROZEN_SAMPLE_MV"
        if key not in series or not np.allclose(series[key],baseline,rtol=0,atol=1e-12):
            raise AssertionError("Funding-only change must preserve normalized frozen growth return: "+scen)
    existing=portfolio_root/"portfolio_construction/outputs/growth_static_exposure_returns.csv"
    if existing.is_file():
        v=pd.read_csv(existing)
        if v.month.tolist()!=MONTHS or not np.allclose(v.growth_static_exposure_monthly,baseline,rtol=0,atol=1e-12):
            raise AssertionError("M2 handoff mismatches existing M3 factor-input series")
    records=[]; registry=[]
    for name in series.columns[1:]:
        parts=name.split("__")
        if len(parts)!=2 or parts[0] not in SCENARIOS or parts[1] not in PORTFOLIOS:
            raise ValueError("Invalid scenario ID: "+name)
        vals=series[name].to_numpy(float)
        if vals.shape!=(96,) or not np.isfinite(vals).all() or (np.abs(vals)>=1).any():
            raise ValueError("Handoff returns must be 96 monthly decimal simple returns")
        registry.append(dict(scenario_id=name,funding_scenario=parts[0],portfolio_policy=parts[1],
                             months=96,start_month="2015-01",end_month="2022-12",
                             input_type="STATIC_ESTIMATION_PROXY_NOT_REALIZED"))
        records.extend(dict(scenario_id=name,month=month,monthly_simple_return_decimal=float(value))
                       for month,value in zip(MONTHS,vals))
    if len(records)!=1440:
        raise ValueError("Handoff row count mismatch")
    long=pd.DataFrame(records)
    if long.duplicated(["scenario_id","month"]).any():
        raise ValueError("Duplicated factor panel keys")
    long.to_csv(out/"M3 Static Returns Long.csv",index=False,float_format="%.16g")
    pd.DataFrame(registry).to_csv(out/"M3 Scenario Registry.csv",index=False)
    weights.to_csv(out/"M3 Exact Portfolio Weights.csv",index=False,float_format="%.16g")
    manifest={"decision_date":"2022-12-31","cutoff":"2022-12",
       "status":"RESEARCH_HANDOFF_NOT_APPROVED",
       "series_type":"STATIC_EXPOSURE_MONTHLY_SIMPLE_RETURNS_DECIMAL_NOT_BUY_HOLD",
       "evaluation_2023_2025_included":False,"LMS_receipt_verified":False,
       "M1_funding_selected":False,"factor_results_computed":False,
       "scenario_count":len(registry),"long_panel_rows":len(records),
       "source_shas":{p.name:sha(p) for p in source.iterdir() if p.is_file()},
       "handoff_shas":{p.name:sha(p) for p in out.iterdir() if p.is_file()}}
    (out/"M3 Handoff Manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    return manifest

if __name__=="__main__":
    p=argparse.ArgumentParser(description="Generate audited M2-to-M3 revised scenario input")
    p.add_argument("--out",default="portfolio_construction/revised_mandate/m3_handoff")
    args=p.parse_args()
    print(json.dumps(build(args.out),indent=2))
