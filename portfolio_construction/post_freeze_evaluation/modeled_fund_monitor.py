#!/usr/bin/env python3
"""Scenario-only foundation TWR using fictional bonds valued at CASE implied YTM.

DO NOT describe outputs as observed bond returns. This tool supplements, not replaces,
the growth-only 2023-2025 market evaluation. External payments are stripped from returns.
Monthly growth values come from the post-freeze evaluator only.
"""
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd
from scipy.optimize import brentq

DECISION=pd.Timestamp('2022-12-31')

def elapsed_coupon_years(date):
    """Case bonds use EXACT annual 31 Dec coupon anniversaries.

    Actual-day interpolation within each coupon year preserves the initial
    1-,2-,..,5-year discount exponents on 2022-12-31 and December anniversaries.
    These dates are a MODEL day-count choice, not observed resale bond prices.
    """
    t=pd.Timestamp(date).normalize()
    if t<DECISION:raise ValueError('No bond valuation before the case date')
    if t==DECISION:return 0.0
    anchor=pd.Timestamp(f'{t.year-1}-12-31')
    next_anniv=pd.Timestamp(f'{t.year}-12-31')
    return float(t.year-2023)+(t-anchor).days/(next_anniv-anchor).days

BETA=2400;DELTA=3600
PRICE_BETA=922.78;PRICE_DELTA=986.07
Y_BETA=(1000/PRICE_BETA)**(1/2)-1
Y_DELTA=brentq(lambda y:sum(35/(1+y)**k for k in range(1,6))+1000/(1+y)**5-PRICE_DELTA,0,.3)

def values_at(date,shift_beta=0,shift_delta=0):
    t=pd.Timestamp(date).normalize(); total=0.
    elapsed=elapsed_coupon_years(t)
    payments={pd.Timestamp('2024-12-31'):BETA*1000}
    for year in range(2023,2028):
        due=pd.Timestamp(f'{year}-12-31')
        payments[due]=payments.get(due,0)+DELTA*35
    payments[pd.Timestamp('2027-12-31')]+=DELTA*1000
    for pay,amount in payments.items():
        if pay>t:
            annual=(Y_BETA+shift_beta if pay==pd.Timestamp('2024-12-31') else Y_DELTA+shift_delta)
            # 2024 may also include Delta coupon; distinguish by splitting cash flow.
            if pay==pd.Timestamp('2024-12-31'):
                exponent=float(pay.year-2022)-elapsed
                total+=BETA*1000/(1+Y_BETA+shift_beta)**exponent
                total+=DELTA*35/(1+Y_DELTA+shift_delta)**exponent
            else:
                total+=amount/(1+annual)**(float(pay.year-2022)-elapsed)
    coupons=DELTA*35*max(0,min(t.year,2027)-2022) if t.month==12 else DELTA*35*max(0,min(t.year-1,2027)-2022)
    # Only coupons as of year-end; for 2028+, five coupons already retained.
    if t.year>2027:coupons=630_000
    mandatory=2_400_000 if t.year>=2024 else 0
    mandatory+=3_600_000 if t.year>=2027 else 0
    return total, coupons, mandatory

def main(growth_file,output,scenario_file=None):
    g=pd.read_csv(growth_file)
    dates=pd.PeriodIndex(g.month,freq='M')
    expected=pd.period_range('2023-01','2025-12',freq='M')
    if not dates.equals(expected) or g.growth_value.isna().any():raise ValueError('Growth evaluation must have 36 observed monthly values')
    shifts={}
    if scenario_file:
        s=pd.read_csv(scenario_file)
        if s.month.tolist()!=g.month.tolist():raise ValueError('Rate shocks must align to all 36 months')
        for rec in s.itertuples(index=False):
            shifts[rec.month]=(float(rec.beta_shift_decimal),float(rec.delta_shift_decimal))
    # Starting cash after equity entry cost already reflected by subsequent growth value.
    old_nav=12_000_000;rows=[]
    for rec in g.itertuples(index=False):
        m=rec.month
        date=pd.Period(m,freq='M').end_time.normalize()
        b,d=shifts.get(m,(0.,0.))
        bond,cash,cum_withdraw=values_at(date,b,d)
        nav=float(rec.growth_value)+bond+cash
        pay=2_400_000 if m=='2024-12' else (3_600_000 if m=='2027-12' else 0)
        # External withdrawal occurs at month end; time-weighted return over this month.
        r=(nav+pay)/old_nav-1
        rows.append({'month':m,'modeled_bonds':bond,'retained_coupon_cash':cash,
          'growth_observed_adjusted_index_value':float(rec.growth_value),
          'external_mandatory_payment':pay,'modeled_fund_NAV_after_payment':nav,
          'cashflow_adjusted_modeled_fund_monthly_return':r,
          'bond_yield_shift_beta':b,'bond_yield_shift_delta':d})
        old_nav=nav
    out=pd.DataFrame(rows)
    x=out.cashflow_adjusted_modeled_fund_monthly_return
    out['modeled_trailing_12m_TWR']=(1+x).rolling(12).apply(np.prod,raw=True)-1
    out['risk_review_status']=np.where(out.modeled_trailing_12m_TWR<=-.15,'REVIEW_15PCT',np.where(out.modeled_trailing_12m_TWR<=-.12,'WARNING_12PCT','NO_TRIGGER'))
    dest=Path(output);dest.parent.mkdir(parents=True,exist_ok=True);out.to_csv(dest,index=False,float_format='%.12g')
    print('MODELED foundation TWR ONLY; no observed fictional-bond quotes:',dest)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--growth-monthly',required=True);p.add_argument('--out',required=True)
    p.add_argument('--rate-shifts',help='Optional 36-month illustrative yield shift scenario (decimal)');a=p.parse_args()
    main(a.growth_monthly,a.out,a.rate_shifts)
