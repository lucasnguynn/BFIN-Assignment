#!/usr/bin/env python3
"""M2 independent numerical peer-check of M1's 2023–2030 revised bond ledgers.

Checks contractual cash flows and capital identities, but is NOT a human
signed review or the group's approved funding recommendation.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from m1_integration import (M1_PATH,CAPITAL,BOND_PRICE,COUPON,
                            MATURITY,REVISED_LIABILITY,load_funding)

PUBLISHED={
    "Revised M1 Principal matching":"principal_matching_ledger.csv",
    "Revised M1 Coupon funding":"coupon_funding_ledger.csv"
}
BONDS=("Beta","Gamma","Delta")

def check(out,m1=M1_PATH):
    m1=Path(m1)
    funding=load_funding(m1)
    evidence=[];issues=[]
    for label,filename in PUBLISHED.items():
        units=funding[label]["units"]
        published=pd.read_csv(m1/filename)
        if published["Year"].astype(int).tolist()!=list(range(2023,2031)):
            raise AssertionError("Committed M1 ledger has incorrect year coverage")
        cash=0.
        for i,year in enumerate(range(2023,2031)):
            src=published.iloc[i]
            expected={}
            for b in BONDS:
                expected[b+" cash flow"]=float(units[b])*(COUPON[b]*(year<=MATURITY[b])+
                                        1000.*(year==MATURITY[b]))
            receipt=sum(expected.values())
            payment=REVISED_LIABILITY.get(year,0.)
            nextcash=cash+receipt-payment
            expected.update({"Opening cash":cash,"Total inflow":receipt,
                             "Mandatory payment":payment,"Closing cash":nextcash})
            for metric,expected_value in expected.items():
                observed=float(src[metric])
                error=observed-expected_value
                evidence.append(dict(scenario=label,year=year,metric=metric,
                    M1_reported_USD=observed,M2_independent_USD=expected_value,
                    discrepancy_USD=error,pass_at_1_cent=abs(error)<=.01))
                if abs(error)>.01:
                    issues.append((label,year,metric,error))
            if nextcash < -.01:
                raise AssertionError("Cash shortfall in {} at year {}".format(label,year))
            cash=nextcash
        if abs(cash-funding[label]["cash"])>.01:
            raise AssertionError("2030 cash amount fails M2 independent check")
        net=funding[label]["net"];fee=funding[label]["fee"];bond=funding[label]["cost"]
        if abs(bond+net+fee-CAPITAL)>.01:
            raise AssertionError("Initial USD 12m reconciliation failure")
    if issues:
        raise AssertionError("M1 cash flow ledger mismatches: {}".format(issues[:6]))
    df=pd.DataFrame(evidence)
    if len(df)!=112:
        raise AssertionError("Expected 2 scenarios x 8 years x 7 metrics")
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(out,index=False,float_format="%.16g")
    return df

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="portfolio_construction/revised_mandate/outputs/M1 Cashflow Independent Check.csv")
    a=p.parse_args()
    df=check(a.out)
    print("PASS: {} independent comparisons, max discrepancy {:.8f} USD".format(len(df),df.discrepancy_USD.abs().max()))
    print("CONDITIONAL: human M1/M2 funding approval is not automatically established")
