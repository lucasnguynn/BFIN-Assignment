#!/usr/bin/env python3
"""Disentangle trustee mandate, funding-method and optimization changes.

All utilities are pre-2023 conditional equity contributions under a fixed
bond-sleeve approximation. No actual performance or 2026 method lookahead.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from m1_integration import run

ORIGINAL="Original frozen"
PRINCIPAL="Revised M1 Principal matching"
COUPON="Revised M1 Coupon funding"
FROZEN="Frozen Sample MV"
OPT="Reoptimized Sample MV A3"

def build(out):
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    calc=out.parent/"m2_decomposition_source"
    run(calc)
    q=pd.read_csv(calc/"portfolio_comparison.csv").set_index(["scenario","policy"])
    f=pd.read_csv(calc/"funding_comparison.csv").set_index("scenario")
    def u(s,p):return float(q.loc[(s,p),"equity_utility"])
    base=u(ORIGINAL,FROZEN)
    pf=u(PRINCIPAL,FROZEN);po=u(PRINCIPAL,OPT)
    cf=u(COUPON,FROZEN);co=u(COUPON,OPT)
    rows=[
        dict(component="Original frozen 22-Oct baseline",risk_measure="Equity utility contribution",
             incremental_utility=0.,cumulative_utility=base,
             comparison="Original mandate, originally chosen stock weights",change_class="ORIGINAL POLICY"),
        dict(component="Trustee revised payment schedule, principal-matched bonds, frozen weights",
             risk_measure="Equity utility contribution",
             incremental_utility=pf-base,cumulative_utility=pf,
             comparison="Original frozen -> M1 revised principal / frozen",
             change_class="MANDATE ONLY UNDER PRINCIPAL MATCHING"),
        dict(component="Alternative use of coupon flows under same revised schedule, frozen weights",
             risk_measure="Equity utility contribution",
             incremental_utility=cf-pf,cumulative_utility=cf,
             comparison="Revised principal / frozen -> Revised coupon / frozen",
             change_class="FUNDING METHOD CHANGE"),
        dict(component="Reoptimize normalized equity weights only within revised coupon funding",
             risk_measure="Equity utility contribution",
             incremental_utility=co-cf,cumulative_utility=co,
             comparison="Revised coupon / frozen -> Revised coupon / optimized",
             change_class="EQUITY METHOD CHANGE"),
    ]
    df=pd.DataFrame(rows)
    if abs(df.incremental_utility.sum()-(co-base))>1e-12:
        raise AssertionError("Mandate/funding/method bridge not additive")
    contrast=[
        dict(scenario=ORIGINAL,frozen_utility=base,reoptimized_utility=u(ORIGINAL,OPT),
             optimizer_gain=u(ORIGINAL,OPT)-base,
             net_equity_USD=f.loc[ORIGINAL,"net_equity"],
             required_equity_CAGR=f.loc[ORIGINAL,"required_2030_equity_CAGR"]),
        dict(scenario=PRINCIPAL,frozen_utility=pf,reoptimized_utility=po,
             optimizer_gain=po-pf,net_equity_USD=f.loc[PRINCIPAL,"net_equity"],
             required_equity_CAGR=f.loc[PRINCIPAL,"required_2030_equity_CAGR"]),
        dict(scenario=COUPON,frozen_utility=cf,reoptimized_utility=co,
             optimizer_gain=co-cf,net_equity_USD=f.loc[COUPON,"net_equity"],
             required_equity_CAGR=f.loc[COUPON,"required_2030_equity_CAGR"])]
    out_path=out
    df.to_csv(out_path,index=False,float_format="%.16g")
    pd.DataFrame(contrast).to_csv(out.with_name("mandate_funding_method_contrast.csv"),index=False,float_format="%.16g")
    return df

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="portfolio_construction/revised_mandate/outputs/mandate_effect_bridge.csv")
    args=p.parse_args()
    print(build(args.out).to_string(index=False))
