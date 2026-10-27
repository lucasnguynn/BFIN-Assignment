#!/usr/bin/env python3
"""Illustrative 2023-25 whole-fund monitor using the approved revised cash schedule.

The equity path comes from archived real daily Yahoo prices. Case bonds are held
to maturity and marked at case-implied YTMs: there are NO observed bond prices.
All principal/coupon receipts and mandatory withdrawals occur at 31 December;
external withdrawals are removed from that month's time-weighted return.
No cash reinvestment return is assumed.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import brentq

ROOT=Path(__file__).resolve().parents[2]
M1=ROOT/"bond_funding/outputs/revised"
ORIGINAL_GROWTH=6229246.7532467535
FUND_START=12000000.0
PRICE={"Beta":922.78,"Gamma":1002.49,"Delta":986.07}
COUPON={"Beta":0.,"Gamma":40.,"Delta":35.}
MATURITY={"Beta":2024,"Gamma":2025,"Delta":2027}
YTM={
 "Beta":(1000/922.78)**.5-1,
 "Gamma":brentq(lambda r:40/(1+r)+(1040)/(1+r)**2-1002.49,-.1,.3),
 "Delta":brentq(lambda r:sum(35/(1+r)**k for k in range(1,6))+1000/(1+r)**5-986.07,-.1,.3),
}
SCHEDULES={
 "principal":{2024:2400000.,2025:1200000.,2027:2400000.},
 "coupon":{2024:2400000.,2025:1200000.,2027:2400000.},
 "original":{2024:2400000.,2027:3600000.},
}
ORIGINAL_UNITS={"Beta":2400.,"Gamma":0.,"Delta":3600.}

def scenario(name="principal"):
    if name not in SCHEDULES:raise ValueError("Choose original, principal or coupon")
    if name=="original":return ORIGINAL_UNITS.copy(),ORIGINAL_GROWTH
    h=pd.read_csv(M1/"revised_holdings.csv").set_index("Bond")
    f=pd.read_csv(M1/"revised_funding_summary.csv").set_index("Metric")
    col={"principal":"Principal matching","coupon":"Coupon funding"}[name]
    return {b:float(h.loc[b,col]) for b in PRICE},float(f.loc["Net equity purchases",col])

def price_and_cash(asof,units,schedule,shifts=None):
    """Return (remaining bond PV, retained cash net of liabilities, annual payment).

    Time fraction uses consecutive 31 December anniversaries, not a vendor bond
    quotation or observed resale price. Inputs are scenario assumptions.
    """
    date=pd.Timestamp(asof).normalize()
    if date<pd.Timestamp("2022-12-31"):raise ValueError("Before case date")
    shifts=shifts or {}
    # Last December anniversary, using actual day lengths per calendar year.
    anchor=pd.Timestamp(f"{date.year-1}-12-31")
    next_dec=pd.Timestamp(f"{date.year}-12-31")
    elapsed=(date.year-2023)+(date-anchor).days/(next_dec-anchor).days
    pv=0.
    for bond,n in units.items():
        yield_rate=YTM[bond]+float(shifts.get(bond,0.))
        if yield_rate<=-1:raise ValueError("Rate scenario too negative")
        for year in range(2023,MATURITY[bond]+1):
            due=pd.Timestamp(f"{year}-12-31")
            if due>date:
                cashflow=COUPON[bond]+(1000. if year==MATURITY[bond] else 0.)
                pv+=n*cashflow/(1+yield_rate)**(year-2022-elapsed)
    # Deliberately compute each coupon and principal from separate dated cash flows.
    retained=0.
    for year in range(2023,date.year+1):
        if date<pd.Timestamp(f"{year}-12-31"):continue
        for bond,n in units.items():
            if year<=MATURITY[bond]:retained+=n*COUPON[bond]
            if year==MATURITY[bond]:retained+=n*1000.
        retained-=schedule.get(year,0.)
        if retained < -0.01:
            raise AssertionError(f"Unfunded liability {year}: {retained:,.2f}")
    return pv,retained

def monitor(growth_file,output,policy="principal",rate_file=None):
    units,net_equity=scenario(policy)
    g=pd.read_csv(growth_file)
    months=pd.period_range("2023-01","2025-12",freq="M").astype(str).tolist()
    if g.month.astype(str).tolist()!=months or g.growth_value.isna().any():
        raise ValueError("Requires exactly 36 observed monthly growth NAVs")
    shocks={}
    if rate_file:
        s=pd.read_csv(rate_file)
        if s.month.tolist()!=months:raise ValueError("Rate scenario months must align")
        for item in s.to_dict("records"):
            shocks[item["month"]]={b:float(item.get(b.lower()+"_shift_decimal",0)) for b in PRICE}
    last=FUND_START
    rows=[]
    for item in g.to_dict("records"):
        month=item["month"]
        date=pd.Period(month,freq="M").end_time.normalize()
        pv,cash=price_and_cash(date,units,SCHEDULES[policy],shocks.get(month))
        equity=float(item["growth_value"])*net_equity/ORIGINAL_GROWTH
        nav=equity+pv+cash
        withdrawal=SCHEDULES[policy].get(date.year,0.) if date.month==12 else 0.
        twr=(nav+withdrawal)/last-1
        rows.append(dict(month=month,funding_policy=policy,
            observed_equity_proxy_USD=equity,modeled_bonds_USD=pv,
            retained_cash_USD=cash,mandatory_external_payment_USD=withdrawal,
            modeled_fund_NAV_after_payment_USD=nav,
            withdrawal_adjusted_monthly_TWR=twr,
            observed_bond_prices_available=False))
        last=nav
    df=pd.DataFrame(rows)
    monthly=df.withdrawal_adjusted_monthly_TWR
    df["modeled_rolling_12m_TWR"]=(1+monthly).rolling(12).apply(np.prod,raw=True)-1
    df["board_action"]=np.select([df.modeled_rolling_12m_TWR<=-.15,
                                   df.modeled_rolling_12m_TWR<=-.12],
                                   ["REVIEW_15PCT","WARNING_12PCT"],default="NO_TRIGGER")
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(output,index=False,float_format="%.15g")
    return df

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--growth-monthly",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--policy",choices=list(SCHEDULES),default="principal")
    p.add_argument("--rate-shifts")
    a=p.parse_args()
    result=monitor(a.growth_monthly,a.out,a.policy,a.rate_shifts)
    print("Modeled bond sleeve only; observed equity growth; chosen policy:",a.policy,
          "months:",len(result),"written:",a.out)
