#!/usr/bin/env python3
"""M2 revised-mandate cross-workstream model, original 2022 information set only.

Read M1's committed revised holdings/summary, validate contractual funding, and
recalculate original vs revised equity allocations and portfolio sensitivities.
This does NOT claim a 22-Oct LMS receipt, human sign-off or realized evaluation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "portfolio_construction" / "src"))
from portfolio_utils import ASSETS, parameters, constraints

CAPITAL = 12_000_000.0
ENTRY_FEE = 0.001
BOND_PRICE = {"Beta": 922.78, "Gamma": 1002.49, "Delta": 986.07}
COUPON = {"Beta": 0.0, "Gamma": 40.0, "Delta": 35.0}
MATURITY = {"Beta": 2024, "Gamma": 2025, "Delta": 2027}
REVISED_LIABILITY = {2024: 2_400_000.0, 2025: 1_200_000.0, 2027: 2_400_000.0}
NOMINAL_TARGET = 8_000_000.0 * (1.023 ** 8)
M1_PATH = ROOT / "bond_funding" / "outputs" / "revised"
RETURNS = ROOT / "portfolio_construction" / "data" / "processed" / "asset_monthly_returns_estimation.csv"
WEIGHTS = ROOT / "portfolio_construction" / "evidence" / "decision_weights_confirmed.csv"

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def bond_cash(units, liabilities):
    cash, rows = 0.0, []
    for year in range(2023, 2031):
        before = cash
        inflow = sum(float(n) * (COUPON[b] * (year <= MATURITY[b]) +
                                1000.0 * (year == MATURITY[b])) for b, n in units.items())
        payment = float(liabilities.get(year, 0))
        cash += inflow - payment
        if cash < -0.001:
            raise AssertionError(f"Liability shortfall in {year}: {cash}")
        rows.append({"year": year, "opening_cash": before, "receipts": inflow,
                     "payment": payment, "closing_cash": cash})
    return cash, rows

def load_funding(m1=M1_PATH):
    m1 = Path(m1)
    holdings = pd.read_csv(m1 / "revised_holdings.csv").set_index("Bond")
    table = pd.read_csv(m1 / "revised_funding_summary.csv").set_index("Metric")
    expected = {"Principal matching", "Coupon funding"}
    if set(holdings.columns) != expected or set(table.columns) != expected:
        raise ValueError("M1 funding schema mismatch")
    if set(holdings.index) != set(BOND_PRICE):
        raise ValueError("M1 bond universe mismatch")
    scenarios = {}
    for name in ("Principal matching", "Coupon funding"):
        units = holdings[name].astype(float).to_dict()
        if not all(np.isfinite(n) and n >= 0 for n in units.values()):
            raise ValueError("Invalid M1 bond holding")
        cost = sum(BOND_PRICE[b] * n for b, n in units.items())
        cash, ledger = bond_cash(units, REVISED_LIABILITY)
        gross = CAPITAL - cost
        net = gross / (1 + ENTRY_FEE)
        fee = gross - net
        hurdle = ((NOMINAL_TARGET - cash) / net) ** (1 / 8) - 1
        comparable = {"Bond cost": cost, "Gross growth budget": gross,
                      "Net equity purchases": net, "Entry fee": fee,
                      "Terminal cash": cash, "Required CAGR": hurdle}
        for key, value in comparable.items():
            if abs(float(table.loc[key, name]) - value) > 0.02:
                raise AssertionError(f"M1 inconsistent {name}: {key}")
        if abs(cost + net + fee - CAPITAL) > 1e-6:
            raise AssertionError("USD12m does not reconcile")
        scenarios["Revised M1 " + name] = dict(units=units, cost=cost, net=net, fee=fee,
                                                 cash=cash, hurdle=hurdle, ledger=ledger)
    return scenarios

def load_estimation(returns=RETURNS, weights=WEIGHTS):
    x = pd.read_csv(returns)
    months = [f"{y}-{m:02d}" for y in range(2015, 2023) for m in range(1, 13)]
    if x.month.astype(str).tolist() != months or not set(ASSETS + ["VTI"]).issubset(x):
        raise ValueError("Only 96 months 2015-01..2022-12 are authorized for the 2022 decision")
    if not np.isfinite(x[ASSETS + ["VTI"]].to_numpy(dtype=float)).all():
        raise ValueError("Missing or nonfinite historical return")
    w = pd.read_csv(weights).set_index("security").loc[ASSETS, "weight_of_growth_sleeve"].to_numpy(float)
    if abs(w.sum() - 1) > 1e-9 or min(w) < -1e-10:
        raise ValueError("Invalid frozen 2022 weights")
    return x, w

def solve(mu, cov, F, A=3, minvar=False, seed=None):
    bounds, cons = constraints()
    start = np.full(12, 1/12) if seed is None else seed
    obj = (lambda w: w @ cov @ w) if minvar else (lambda w: -(w @ mu - .5 * A * F * w @ cov @ w))
    jac = (lambda w: 2 * cov @ w) if minvar else (lambda w: -mu + A * F * cov @ w)
    z = minimize(obj, start, jac=jac, method="SLSQP", bounds=bounds,
                 constraints=cons, options={"ftol": 1e-13, "maxiter": 3000})
    if not z.success:
        raise ArithmeticError(f"Portfolio optimizer: {z.message}")
    w = z.x.copy()
    w[abs(w) < 1e-11] = 0
    if abs(w.sum() - 1) > 1e-7 or min(w) < -1e-8:
        raise AssertionError("Unacceptable weights")
    return w

def run(out, m1=M1_PATH, returns=RETURNS, weights=WEIGHTS):
    out = Path(out)
    scenarios = load_funding(m1)
    original = {"Beta": 2400.0, "Delta": 3600.0}
    ocost = sum(BOND_PRICE[b] * n for b, n in original.items())
    ocash, _ = bond_cash(original, {2024: 2_400_000, 2027: 3_600_000})
    onet = (CAPITAL - ocost) / (1 + ENTRY_FEE)
    scenarios = {"Original frozen": dict(units=original, cost=ocost, net=onet,
                  fee=(CAPITAL - ocost) - onet, cash=ocash,
                  hurdle=((NOMINAL_TARGET - ocash)/onet)**(1/8)-1), **scenarios}
    panel, frozen = load_estimation(returns, weights)
    mu, sample, single, _, _ = parameters(panel)
    history = 12 * panel[ASSETS].mean().to_numpy(float)
    prior = np.full(12, 12 * panel.VTI.mean())
    m1stresses = pd.read_csv(Path(m1) / "revised_rate_scenario_summary.csv")
    rows, allocations, details, shocks, static = [], [], [], [], {"month": panel.month.tolist()}
    for label, fund in scenarios.items():
        F = fund["net"] / CAPITAL
        policies = {"Frozen Sample MV": frozen,
                    "Reoptimized Sample MV A3": solve(mu, sample, F, seed=frozen),
                    "Reoptimized Single Index MV A3": solve(mu, single, F, seed=frozen),
                    "Constrained Minimum Variance": solve(mu, sample, F, minvar=True, seed=frozen),
                    "Reoptimized Sample MV A6": solve(mu, sample, F, A=6, seed=frozen)}
        for policy, w in policies.items():
            A = 6 if policy.endswith("A6") else 3
            ret = float(w @ mu)
            var = float(w @ sample @ w)
            rows.append(dict(scenario=label, policy=policy, A=A, net_equity=fund["net"],
                annual_arithmetic_expected_return=ret, annual_volatility=var**.5,
                equity_utility=F * ret - .5 * A * F * F * var,
                sum_weights=w.sum()))
            for ticker, weight in zip(ASSETS, w):
                allocations.append(dict(scenario=label, policy=policy, ticker=ticker,
                                        exact_weight=weight, exact_purchase_USD=weight*fund["net"]))
            key=label.upper().replace(" ", "_") + "__" + policy.upper().replace(" ","_")
            static[key]=(panel[ASSETS].to_numpy(float) @ w).tolist()
        d = frozen - policies["Constrained Minimum Variance"]
        dv = float(frozen @ sample @ frozen - policies["Constrained Minimum Variance"] @ sample @ policies["Constrained Minimum Variance"])
        slope = float(d @ (history - prior))
        details.append(dict(scenario=label, bond_cost=fund["cost"],
            net_equity=fund["net"], equity_fee=fund["fee"], retained_cash=fund["cash"],
            required_2030_equity_CAGR=fund["hurdle"],
            fixed_policy_A_star=2 * float(d @ mu) / (F * dv),
            fixed_policy_lambda_star=(.5 * 3 * F * dv - float(d @ prior)) / slope))
        if label.startswith("Revised M1"):
            name = label.removeprefix("Revised M1 ")
            b = m1stresses[(m1stresses.Policy == name) &
                           (m1stresses.Scenario == "Parallel +100 bp")]
            if len(b) != 1:
                raise ValueError("Missing unique M1 +100bp exact repricing")
            bond_pnl = float(b.iloc[0]["Bond sleeve gain/loss USD"])
            for shock in (-.10, -.20, -.25, -.30):
                shocks.append(dict(scenario=label, equity_shock=shock,
                    bond_yield_shock_bps=100,
                    instantaneous_fund_loss=-(fund["net"]*shock + bond_pnl)/CAPITAL,
                    note="Not a rolling 12-month withdrawal-adjusted 12%/15% review measure"))
    if len(static) != 16:
        raise AssertionError("15 distinct scenario series + month required")
    out.mkdir(parents=True, exist_ok=True)
    for name, values in (("funding_comparison.csv", details),
                         ("portfolio_comparison.csv", rows),
                         ("exact_allocations.csv", allocations),
                         ("combined_stress.csv", shocks)):
        pd.DataFrame(values).to_csv(out / name, index=False, float_format="%.16g")
    pd.DataFrame(static).to_csv(out / "growth_static_returns_2015_2022.csv", index=False, float_format="%.16g")
    metadata = dict(case_date="2022-12-31", cutoff="2022-12", real_evaluation_completed=False,
        original_policy_modified=False, group_funding_selection_confirmed=False,
        source_shas={"M1 holdings":sha(Path(m1)/"revised_holdings.csv"),
            "M1 summary":sha(Path(m1)/"revised_funding_summary.csv"),
            "M1 shocks":sha(Path(m1)/"revised_rate_scenario_summary.csv"),
            "2015-2022 returns":sha(returns),"frozen repository weights":sha(weights)},
        note="M1 Principal/Coupon inputs are committed source scenarios, not approved group choices. LMS receipt not independently verified.")
    (out / "m2_sources_and_gates.json").write_text(json.dumps(metadata, indent=2)+"\n")
    return pd.DataFrame(details)

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default="portfolio_construction/revised_mandate/outputs")
    args=parser.parse_args()
    print(run(args.out).to_string(index=False))
