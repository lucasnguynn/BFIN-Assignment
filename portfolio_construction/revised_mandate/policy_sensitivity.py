#!/usr/bin/env python3
"""Transparent 2030 goal sensitivities for original and M1 revised funded sleeves.

Decision-time cashflow scenarios only. No post-2022 realized market returns,
new model forecasts, group-selected funding policy or LMS freeze are claimed.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from m1_integration import CAPITAL, ENTRY_FEE, BOND_PRICE, bond_cash, load_funding

INFLATIONS=(0.02,0.023,0.03,0.04)
BUFFERS=(0.0,250000.0,500000.0)
GROWTH_CASES=(0.0,0.03,0.06,0.10)
REAL_TARGET=8000000.0
HORIZON_YEARS=8

def model():
    revised=load_funding()
    units={"Beta":2400.0,"Delta":3600.0}
    cash,led=bond_cash(units,{2024:2400000.0,2027:3600000.0})
    original={"Original frozen":dict(cost=sum(BOND_PRICE[t]*q for t,q in units.items()),
                                     cash=cash,ledger=led)}
    return {**original,**revised}

def build(out, inflations=INFLATIONS,buffers=BUFFERS,growth_cases=GROWTH_CASES):
    scenarios=model()
    rows=[]
    for name,fund in scenarios.items():
        for pi in inflations:
            goal=REAL_TARGET*(1+pi)**HORIZON_YEARS
            for cash_buffer in buffers:
                gross=CAPITAL-fund["cost"]-cash_buffer
                if gross<=0:
                    raise ValueError("Funding and cash buffer exceed foundation initial assets")
                net=gross/(1+ENTRY_FEE)
                fee=gross-net
                # Operating cash is explicitly assumed unspent, held at 0%
                # through 2030. Alternative emergency spending must be a
                # separate case and cannot count this same balance at 2030.
                terminal_cash=fund["cash"]+cash_buffer
                gap=goal-terminal_cash
                if gap<=0:
                    required=0.0
                else:
                    required=(gap/net)**(1/HORIZON_YEARS)-1
                row=dict(scenario=name,inflation=pi,
                    initial_operating_buffer_USD=cash_buffer,
                    initial_bond_funding_USD=fund["cost"],gross_growth_USD=gross,
                    net_equity_investment_USD=net,entry_fee_USD=fee,
                    initial_capital_reconciliation_USD=fund["cost"]+net+fee+cash_buffer,
                    assumed_unspent_2030_operating_buffer_USD=cash_buffer,
                    retained_bond_coupon_cash_2030_USD=fund["cash"],
                    terminal_cash_total_USD=terminal_cash,
                    goal_2030_nominal_USD=goal,
                    required_8yr_equity_CAGR=required,
                    cash_after_2025_payment_before_buffer_USD=fund["ledger"][2]["closing_cash"],
                    cash_after_2025_payment_with_buffer_USD=fund["ledger"][2]["closing_cash"]+cash_buffer,
                    note="0pct cash reinvestment; buffer unspent through 2030; illustrative not forecast")
                for g in growth_cases:
                    tag=int(round(g*100))
                    wealth=net*(1+g)**HORIZON_YEARS+terminal_cash
                    row[f"terminal_wealth_if_equity_CAGR_{tag}pct_USD"]=wealth
                    row[f"goal_gap_if_equity_CAGR_{tag}pct_USD"]=wealth-goal
                if abs(row["initial_capital_reconciliation_USD"]-CAPITAL)>1e-6:
                    raise AssertionError("12m capital accounting failed")
                rows.append(row)
    df=pd.DataFrame(rows)
    expected=len(scenarios)*len(inflations)*len(buffers)
    if len(df)!=expected or not df.scenario.nunique()==3:
        raise AssertionError("Sensitivity matrix incomplete")
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(out,index=False,float_format="%.16g")
    return df

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="portfolio_construction/revised_mandate/outputs/2030_inflation_buffer_sensitivity.csv")
    a=p.parse_args()
    result=build(a.out)
    print(result[(result.inflation==0.023)&(result.initial_operating_buffer_USD==0)]
          [["scenario","required_8yr_equity_CAGR","terminal_cash_total_USD"]].to_string(index=False))
