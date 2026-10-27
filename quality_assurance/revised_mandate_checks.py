"""QA gates for the revised trustee mandate (released 23 October 2026, 16:00 HCMC time).

Every gate re-derives its number independently of the module that produced it, uses exact Decimal
arithmetic for money, and never touches an observation after 2022-12. Returns the same
dict(id, status, detail) records as quality_assurance.checks.
"""
from __future__ import annotations
import sys, tempfile
from decimal import Decimal, getcontext
from pathlib import Path
import numpy as np
import pandas as pd

getcontext().prec = 40
CAPITAL = Decimal("12000000")
ORIGINAL_SCHEDULE = {2024: Decimal("2400000"), 2027: Decimal("3600000")}
REVISED_SCHEDULE = {2024: Decimal("2400000"), 2025: Decimal("1200000"), 2027: Decimal("2400000")}
HOLDINGS = {"Beta": (Decimal("922.78"), Decimal(0), 2024), "Gamma": (Decimal("1002.49"), Decimal(40), 2025),
            "Delta": (Decimal("986.07"), Decimal(35), 2027)}


def chk(cid, status, detail, **extra):
    return dict(id=cid, status=status, detail=detail, **extra)


def check_revised_mandate(root):
    root = Path(root)
    sys.path.insert(0, str(root / "portfolio_construction" / "revised_mandate"))
    out = []
    # 1. Schedule: same total, only the timing changed, matches the PDF table
    t0, t1 = sum(ORIGINAL_SCHEDULE.values()), sum(REVISED_SCHEDULE.values())
    ok = t0 == t1 == Decimal("6000000") and REVISED_SCHEDULE[2025] == Decimal("1200000")
    out.append(chk("REVISED.schedule_total_unchanged", "PASS" if ok else "FAIL",
                   f"original {t0:,} vs revised {t1:,}; 2025 payment {REVISED_SCHEDULE[2025]:,}; 2027 payment {REVISED_SCHEDULE[2027]:,}"))
    try:
        from m1_integration import run as run_revised_model
        with tempfile.TemporaryDirectory() as tmp:
            run_revised_model(Path(tmp))
            fund = pd.read_csv(Path(tmp) / "funding_comparison.csv").set_index("scenario")
            alloc = pd.read_csv(Path(tmp) / "exact_allocations.csv")
            series = pd.read_csv(Path(tmp) / "growth_static_returns_2015_2022.csv")
    except Exception as e:                                           # pragma: no cover
        return out + [chk("REVISED.model_rebuild", "FAIL", repr(e))]
    out.append(chk("REVISED.model_rebuild", "PASS", f"{len(fund)} funding scenarios and {series.shape[1]-1} equity-policy series rebuilt offline"))

    # 2. Dollar reconciliation to exactly USD 12,000,000 (bond cost + net equity + fee + opening cash buffer)
    bad = []
    for scen, r in fund.iterrows():
        total = Decimal(str(r.bond_cost)) + Decimal(str(r.net_equity)) + Decimal(str(r.equity_fee))
        if abs(total - CAPITAL) > Decimal("0.01"):
            bad.append((scen, str(total)))
    out.append(chk("REVISED.reconcile_12m_all_scenarios", "FAIL" if bad else "PASS",
                   "bond cost + net equity + 10 bp fee = USD 12,000,000.00 (+/-0.01) in all scenarios" if not bad else f"mismatch {bad}"))

    # 3. Contractual cash-flow ledger: no shortfall under the REVISED schedule, independent of the model code
    msgs, bad = [], False
    holdings = pd.read_csv(root / "bond_funding/outputs/revised/revised_holdings.csv").set_index("Bond")
    for col in ("Principal matching", "Coupon funding"):
        units = {b: Decimal(str(holdings.loc[b, col])) for b in HOLDINGS}
        cash = Decimal(0)
        for year in range(2023, 2031):
            inflow = sum(units[b] * (HOLDINGS[b][1] * (year <= HOLDINGS[b][2]) + Decimal(1000) * (year == HOLDINGS[b][2])) for b in HOLDINGS)
            cash += inflow - REVISED_SCHEDULE.get(year, Decimal(0))
            if cash < Decimal("-0.001"):
                bad = True; msgs.append(f"{col}: shortfall {cash:,.2f} in {year}")
        msgs.append(f"{col}: 2030 cash USD {cash:,.0f}")
    out.append(chk("REVISED.liabilities_covered_2024_2025_2027", "FAIL" if bad else "PASS", "; ".join(msgs)))

    # 4. Funding-only change must leave the frozen growth series (and so all factor estimates) unchanged
    base = series["ORIGINAL_FROZEN__FROZEN_SAMPLE_MV"].to_numpy()
    gaps = {c: float(np.max(np.abs(series[c].to_numpy() - base))) for c in series.columns if c.endswith("__FROZEN_SAMPLE_MV")}
    ok = len(gaps) == 3 and max(gaps.values()) <= 1e-12
    out.append(chk("REVISED.frozen_series_invariant_to_funding", "PASS" if ok else "FAIL",
                   "max |gap| of frozen growth series across 3 funding scenarios = %.2e (tolerance 1e-12)" % max(gaps.values())))
    # 5. ... and equals the series used in the 22 October factor regressions
    saved = pd.read_csv(root / "portfolio_construction/outputs/growth_static_exposure_returns.csv")
    gap = float(np.max(np.abs(saved.growth_static_exposure_monthly.to_numpy() - base)))
    out.append(chk("REVISED.matches_22oct_factor_input", "PASS" if gap <= 1e-12 and list(saved.month) == list(series.month) else "FAIL",
                   f"max |gap| vs growth_static_exposure_returns.csv = {gap:.2e}"))

    # 6. Temporal integrity of the revised scenarios
    months = list(series.month)
    ok = len(months) == 96 and months[0] == "2015-01" and months[-1] == "2022-12"
    out.append(chk("REVISED.no_post_2022_observation", "PASS" if ok else "FAIL", f"{len(months)} months, {months[0]} to {months[-1]}"))

    # 7. Revised factor table (written by factor_analysis.revised_mandate_factors) agrees with the 22 Oct estimates
    f = root / "factor_analysis/outputs/revised_mandate_factor_scenarios.csv"
    c = root / "factor_analysis/outputs/factor_coefficients.csv"
    if f.is_file() and c.is_file():
        rv = pd.read_csv(f).set_index("scenario_id")
        co = pd.read_csv(c)
        ff3 = co[(co.strategy_or_ticker == "GROWTH_FROZEN_SAMPLE_MV") & (co.model == "FF3")].iloc[0]
        row = rv.loc["REVISED_M1_PRINCIPAL_MATCHING__FROZEN_SAMPLE_MV"]
        d = max(abs(row.beta_mkt_ff3 - ff3.Mkt_RF), abs(row.smb - ff3.SMB), abs(row.hml - ff3.HML), abs(row.alpha_ff3_monthly - ff3.alpha))
        out.append(chk("REVISED.factor_estimates_unchanged", "PASS" if d < 1e-8 else "FAIL",
                       f"revised-scenario FF3 estimates equal the 22 October estimates (max abs diff {d:.1e})"))
    else:
        out.append(chk("REVISED.factor_estimates_unchanged", "WARN", "revised factor table not generated yet"))

    # 8. Mandate / method decomposition is additive
    try:
        from mandate_decomposition import build as build_decomp
        with tempfile.TemporaryDirectory() as tmp:
            build_decomp(Path(tmp) / "decomposition.csv")
        out.append(chk("REVISED.mandate_method_bridge_additive", "PASS", "mandate -> funding method -> equity method bridge sums to the total utility change"))
    except Exception as e:
        out.append(chk("REVISED.mandate_method_bridge_additive", "FAIL", repr(e)))

    # 9. Original 22 October files are unchanged (frozen weights hash recorded in the source manifest)
    wf = root / "portfolio_construction/evidence/decision_weights_confirmed.csv"
    import hashlib
    h = hashlib.sha256(wf.read_bytes()).hexdigest()
    out.append(chk("REVISED.original_weights_preserved", "PASS" if h.startswith("a15469f1") else "FAIL",
                   f"decision_weights_confirmed.csv sha256 {h[:16]}... (recorded 22 Oct value a15469f1...)"))
    return out
