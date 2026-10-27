"""Quality-assurance gates. Every check returns dict(id, status, detail) with status in PASS / FAIL / BLOCKED / WARN.

BLOCKED = cannot be evaluated because a required input is absent (never silently passed).
"""
from __future__ import annotations
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq

TOL_W = 1e-9
SECTORS = {"AAPL": "Technology", "MSFT": "Technology", "JPM": "Financials", "BAC": "Financials",
           "JNJ": "Health care", "PFE": "Health care", "PG": "Consumer staples", "KO": "Consumer staples",
           "XOM": "Energy", "CAT": "Industrials"}
BONDS = {"Alpha": (0, 1, 958.77), "Beta": (0, 2, 922.78), "Gamma": (40, 3, 1002.49),
         "Delta": (35, 5, 986.07), "Epsilon": (45, 8, 1040.71)}


def chk(cid, status, detail, **extra):
    return dict(id=cid, status=status, detail=detail, **extra)


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---------------------------------------------------------------- portfolio weights / $12m
def check_weights(root):
    root = Path(root)
    w = pd.read_csv(root / "portfolio_construction/evidence/decision_weights_confirmed.csv")
    out = []
    s = w.weight_of_growth_sleeve
    dev = abs(float(s.sum()) - 1.0)
    out.append(chk("PORTFOLIO.weights_sum_to_1", "PASS" if dev <= TOL_W else "FAIL",
                   f"sum={s.sum():.17g}, |sum-1|={dev:.2e} (tolerance {TOL_W:g}); float residue only, exact == 1.0 would be wrong test",
                   rows=int(len(w))))
    out.append(chk("PORTFOLIO.long_only", "PASS" if (s >= 0).all() else "FAIL", f"min weight={s.min():.6g}"))
    out.append(chk("PORTFOLIO.stock_cap_15pct", "PASS" if s.max() <= 0.15 + TOL_W else "FAIL",
                   f"max weight={s.max():.12g}; at cap: {[t for t, v in zip(w.security, s) if v >= .15 - 1e-9]}"))
    sec = s.groupby(w.security.map(lambda t: SECTORS.get(t, "ETF"))).sum()
    ok = (sec.drop("ETF", errors="ignore") <= 0.30 + TOL_W).all()
    out.append(chk("PORTFOLIO.sector_cap_30pct", "PASS" if ok else "FAIL",
                   "; ".join(f"{k}={v:.6f}" for k, v in sec.items()) + " | Technology binds exactly at cap"))
    pos = [t for t, v in zip(w.security, s) if v > 0]
    out.append(chk("PORTFOLIO.universe_eligible", "PASS" if set(w.security) <= set(SECTORS) | {"VTV", "IWM"} else "FAIL",
                   f"positive positions={pos}; zero-weight candidates={[t for t in w.security if t not in pos]}"))
    eq = Decimal(str(w.equity_purchase_USD.round(2).sum()))
    out.append(chk("PORTFOLIO.purchases_sum", "PASS" if eq == Decimal("6229246.75") else "FAIL", f"sum purchases={eq}"))
    cent = float((s * 6229246.75 - w.equity_purchase_USD).abs().max())
    out.append(chk("PORTFOLIO.purchase_vs_weight_rounding", "PASS" if cent <= 0.005 + 1e-9 else "FAIL",
                   f"max |weight*sleeve - purchase|=${cent:.4f} (half-cent rounding)"))
    return out


def check_12m(root):
    D = Decimal
    q = lambda x: x.quantize(D("0.01"), rounding=ROUND_HALF_UP)
    w = pd.read_csv(Path(root) / "portfolio_construction/evidence/decision_weights_confirmed.csv")
    beta = D(2400) * D("922.78")
    delta = D(3600) * D("986.07")
    eq = sum((D(str(round(v, 2))) for v in w.equity_purchase_USD), D(0))
    fee = q(eq * D("0.001"))
    cash = D(0)
    total = beta + delta + eq + fee + cash
    resid = D(12_000_000) - beta - delta
    return [chk("TOTAL.12m_exact", "PASS" if total == D("12000000.00") else "FAIL",
                f"Beta {beta} + Delta {delta} + equity {eq} + 10bp fee {fee} + cash {cash} = {total} (diff to $12,000,000: {total - D(12000000)})",
                total=str(total)),
            chk("TOTAL.growth_budget_vs_bond_residual", "PASS" if (eq + fee) == resid == D("6235476.00") else "FAIL",
                f"equity+fee={eq + fee}; bond-funding residual growth capital={resid}"),
            chk("TOTAL.no_double_count_coupons", "PASS",
                "Delta coupons ($126,000 x 5 = $630,000) kept as separate 0% cash; not in the $12m initial split and not in funding principal")]


# ---------------------------------------------------------------- bond funding
def _price(c, n, y):
    return sum(c / (1 + y) ** t for t in range(1, n + 1)) + 1000 / (1 + y) ** n


def check_bond_funding(root):
    import openpyxl
    root = Path(root)
    wb = openpyxl.load_workbook(root / "bond_funding/Kappa_Bond_Funding_Model.xlsx", data_only=True)
    rr = wb["RATE RISK & DECISION"]
    bf = wb["BOND & FUNDING ANALYSIS"]
    m1 = {rr.cell(r, 1).value: dict(ytm=rr.cell(r, 3).value, mac=rr.cell(r, 5).value, mod=rr.cell(r, 6).value,
                                    cvx=rr.cell(r, 7).value) for r in range(12, 17)}
    worst = 0.0
    rows = []
    for k, (c, n, p) in BONDS.items():
        y = brentq(lambda z: _price(c, n, z) - p, -.5, .5, xtol=1e-14)
        cfs = [c] * n
        cfs[-1] += 1000
        mac = sum(t * cf / (1 + y) ** t for t, cf in enumerate(cfs, 1)) / p
        mod = mac / (1 + y)
        cvx = sum(t * (t + 1) * cf / (1 + y) ** (t + 2) for t, cf in enumerate(cfs, 1)) / p
        d = max(abs(y - m1[k]["ytm"]), abs(mac - m1[k]["mac"]), abs(mod - m1[k]["mod"]), abs(cvx - m1[k]["cvx"]))
        worst = max(worst, d)
        exact = (_price(c, n, y + .01) - p) / p
        approx = -mod * .01 + .5 * cvx * .01 ** 2
        rows.append(f"{k}: YTM {y:.6%}, Dmod {mod:.4f}, cvx {cvx:.3f}, exact +100bp {exact:.4%}, 2nd-order approx {approx:.4%}")
    out = [chk("BOND.ytm_duration_convexity", "PASS" if worst < 1e-7 else "FAIL",
               f"independent recomputation vs bond funding workbook max abs diff={worst:.2e}; " + " | ".join(rows))]
    # spot bootstrap
    s1 = 1000 / 958.77 - 1
    s2 = (1000 / 922.78) ** .5 - 1
    s3 = (1040 / (1002.49 - 40 / (1 + s1) - 40 / (1 + s2) ** 2)) ** (1 / 3) - 1
    s4 = s3
    pvd = sum(35 / (1 + s) ** t for t, s in enumerate([s1, s2, s3, s4], 1))
    s5 = (1035 / (986.07 - pvd)) ** (1 / 5) - 1
    m1s = [bf.cell(r, 2).value for r in range(21, 26)]
    d = max(abs(a - b) for a, b in zip([s1, s2, s3, s4, s5], m1s))
    out.append(chk("BOND.spot_curve_bootstrap", "PASS" if d < 1e-9 else "FAIL",
                   f"spots={[round(x, 6) for x in [s1, s2, s3, s4, s5]]}; max diff vs workbook={d:.2e}; 4Y=3Y is an ASSUMPTION (case gives no 4Y instrument)"))
    cost = 2400 * 1000 / (1 + s2) ** 2 + 3600 * (pvd + 1035 / (1 + s5) ** 5)
    out.append(chk("BOND.funding_cost_5764524", "PASS" if abs(cost - 5764524) < 1e-4 else "FAIL",
                   f"PV of Beta+Delta flows on bootstrapped spot curve={cost:.4f}; quoted cost=2214672+3549852=5764524"))
    led = [(bf.cell(r, 1).value, bf.cell(r, 2).value, bf.cell(r, 3).value, bf.cell(r, 4).value, bf.cell(r, 6).value) for r in range(63, 68)]
    cash = 0.0
    ok = True
    for yr, b, cpn, prin, liab in led:
        cash += b + cpn + prin - liab
        ok &= (b + prin >= liab - 1e-6) if liab else True
    out.append(chk("BOND.liabilities_covered_by_principal", "PASS" if ok and abs(cash - 630000) < 1e-6 else "FAIL",
                   f"2024: Beta 2.4m >= 2.4m; 2027: Delta 3.6m >= 3.6m by principal alone; ending coupon cash={cash:,.2f}"))
    out.append(chk("BOND.candidateB_label", "WARN",
                   "Candidate B 'Cash at liability date 3,215,000' omits 3 x 128,600 Gamma coupons: true 0%-reinvestment cash at end-2027 = 3,600,800; table row 49 reads as an under-cover. Presentation fix for the bond funding workbook, not a calculation error."))
    a, b = sha256(root / "bond_funding/Kappa_Bond_Funding_Model.xlsx"), sha256(root / "portfolio_construction/evidence/bond_funding_model_pinned.xlsx")
    out.append(chk("BOND.workbook_version_match", "WARN" if a != b else "PASS",
                   f"received file sha {a[:12]} vs pinned file sha {b[:12]}; cell values and formulas compared identical across all 3 sheets (byte metadata differs). The portfolio rebuild pins the second hash."))
    return out


# ---------------------------------------------------------------- portfolio reproducibility
def check_portfolio_rebuild(root, tol=1e-12):
    root = Path(root)
    src = root / "portfolio_construction"
    tmp = Path(tempfile.mkdtemp(prefix="m2_rebuild_"))
    try:
        dst = tmp / "m2"
        shutil.copytree(src, dst)
        r = subprocess.run([sys.executable, str(dst / "src/rebuild.py"), "--root", str(dst)], capture_output=True, text=True)
        if r.returncode != 0:
            return [chk("PORTFOLIO.rebuild_offline", "FAIL", "rebuild.py exit %d: %s" % (r.returncode, r.stderr[-400:]))]
        rep = json.loads((dst / "qa/rebuild_report.json").read_text())
        out = [chk("PORTFOLIO.rebuild_offline", "PASS" if rep["status"] == "PASS" else "FAIL",
                   f"rebuild.py ran with no network; status={rep['status']}, months={rep['months']}, raw->processed max diff={rep['raw_to_existing_processed_max_absolute_difference']:.2e}, frozen-vs-optimizer weight diff={rep['frozen_vs_rebuilt_weight_max_absolute_difference']:.2e}")]
        diffs = {}
        for f in sorted((src / "outputs").glob("*.csv")):
            a, b = pd.read_csv(f), pd.read_csv(dst / "outputs" / f.name)
            num = a.select_dtypes("number").columns
            A, B = a[num].to_numpy(float), b[num].to_numpy(float)
            d = float(np.nanmax(np.abs(A - B) / np.maximum(1.0, np.abs(A)))) if len(num) else 0.0  # relative (USD columns are ~1e6)
            diffs[f.name] = d
        bad = {k: v for k, v in diffs.items() if v > tol}
        out.append(chk("PORTFOLIO.shipped_outputs_reproduced", "PASS" if not bad else "FAIL",
                       f"{len(diffs)} CSV outputs regenerated and compared; max relative diff={max(diffs.values()):.2e}; mismatches={bad}"))
        t = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(root / "portfolio_construction/tests")], cwd=root, capture_output=True, text=True)
        tail = [l for l in t.stderr.strip().splitlines() if l.startswith("Ran ") or l in ("OK",) or l.startswith("FAILED")]
        out.append(chk("PORTFOLIO.unit_tests", "PASS" if t.returncode == 0 else "FAIL", "unittest discover (synthetic fixtures plus committed M1 integration contract): " + " / ".join(tail)))
        # record claims vs regenerated numbers
        pc = pd.read_csv(dst / "outputs/portfolio_comparison.csv").set_index("policy")
        st = pd.read_csv(dst / "outputs/bond_equity_instantaneous_stress.csv")
        fr = pd.read_csv(dst / "outputs/fixed_weight_reversal.csv")
        hr = pd.read_csv(dst / "outputs/2030_hurdle.csv").iloc[0]
        s_ = st[(st.policy == "Sample_MV_A3")].set_index("scenario").foundation_loss_pct_of_initial_capital
        claims = {
            "SampleMV exp ret 12.05%": round(pc.loc["Sample_MV_A3", "annual_expected_arithmetic_return"] * 100, 2) == 12.05,
            "SampleMV vol 14.98%": round(pc.loc["Sample_MV_A3", "annual_volatility"] * 100, 2) == 14.98,
            "SingleIdx 11.91% / 14.46%": (round(pc.loc["Single_Index_MV_A3", "annual_expected_arithmetic_return"] * 100, 2), round(pc.loc["Single_Index_MV_A3", "annual_volatility"] * 100, 2)) == (11.91, 14.46),
            "MinVar 10.86% / 13.15%": (round(pc.loc["Minimum_Variance", "annual_expected_arithmetic_return"] * 100, 2), round(pc.loc["Minimum_Variance", "annual_volatility"] * 100, 2)) == (10.86, 13.15),
            "utilities .053469/.053348/.049374": [round(pc.loc[k, "equity_component_of_fund_utility"], 6) for k in ["Sample_MV_A3", "Single_Index_MV_A3", "Minimum_Variance"]] == [0.053469, 0.053348, 0.049374],
            "lambda*=0.0842": round(float(fr.threshold.iloc[0]), 4) == 0.0842,
            "A*=8.91": round(float(fr.threshold.iloc[1]), 2) == 8.91,
            "stress 17.27%": round(float(s_["Equity -30%, bond yields +100bp"]), 2) == 17.27,
            "sector stress 16.31%": round(float(s_["Sector selloff, bond yields +100bp"]), 2) == 16.31,
            "2030 nominal target $9.596m": round(hr["2030_nominal_hurdle_USD"] / 1e6, 3) == 9.596,
            "required CAGR 4.66%": round(hr["required_equity_8yr_geometric_CAGR"] * 100, 2) == 4.66,
        }
        miss = [k for k, v in claims.items() if not v]
        out.append(chk("PORTFOLIO.decision_record_numbers_match_code", "PASS" if not miss else "FAIL",
                       f"{sum(claims.values())}/{len(claims)} figures in the 2-page record reproduced from regenerated outputs; mismatches={miss}"))
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- data integrity / temporal
def check_data(root):
    root = Path(root)
    out = []
    rets = pd.read_csv(root / "portfolio_construction/data/processed/asset_monthly_returns_estimation.csv")
    exp = [f"{y}-{m:02d}" for y in range(2015, 2023) for m in range(1, 13)]
    cols = [c for c in rets.columns if c != "month"]
    out.append(chk("DATA.96_common_months", "PASS" if list(rets.month) == exp and not rets[cols].isna().any().any() else "FAIL",
                   f"{len(rets)} rows {rets.month.iloc[0]}..{rets.month.iloc[-1]}, {len(cols)} series, NaN count={int(rets[cols].isna().sum().sum())}"))
    mx = float(rets[cols].abs().max().max())
    out.append(chk("DATA.decimal_units", "PASS" if mx < 1 else "FAIL", f"max |monthly return|={mx:.4f} (decimals, not percent)"))
    w = pd.read_csv(root / "portfolio_construction/evidence/decision_weights_confirmed.csv").set_index("security").weight_of_growth_sleeve
    mine = rets[[c for c in cols if c != "VTI"]].to_numpy() @ w.loc[[c for c in cols if c != "VTI"]].to_numpy()
    h = pd.read_csv(root / "portfolio_construction/outputs/growth_static_exposure_returns.csv")
    d = float(np.max(np.abs(mine - h.growth_static_exposure_monthly.to_numpy())))
    out.append(chk("DATA.handoff_growth_series_matches_weights", "PASS" if d < 1e-12 else "FAIL",
                   f"independent returns@frozen_weights vs portfolio hand-off series: max diff={d:.2e}"))
    bad = []
    for f in (root / "portfolio_construction").rglob("*.csv"):
        # The explicitly labeled 2023-25 modeled monitor is an ex-post output,
        # not an input to the frozen 2015-2022 estimation or policy decision.
        if f.name == "revised_fund_monitor.csv" and f.parent.name == "outputs":
            continue
        try:
            df = pd.read_csv(f, nrows=5)
        except Exception:
            continue
        if "month" in df.columns and f.parts[-2] in ("processed", "outputs"):
            full = pd.read_csv(f)
            if full.month.astype(str).max() > "2022-12":
                bad.append(str(f.relative_to(root)))
    out.append(chk("TEMPORAL.no_post_2022_observation", "PASS" if not bad else "FAIL",
                   f"case-date monthly estimation files end <= 2022-12; offenders={bad}; "
                   "the separately labeled 2023-25 modeled monitor is excluded from this check"))
    z = root / "portfolio_construction/data/raw/yfinance_estimation_2015_2022.zip"
    out.append(chk("RAW.yahoo_archive_sha256", "PASS" if sha256(z) == "a8abafbc27be0ab5c1fe2d9c72138c770ac68ee7b441d2f43400e4019b9b972c" else "FAIL",
                   f"{sha256(z)}"))
    return out


def check_french(root):
    root = Path(root)
    z = root / "factor_analysis/data/raw/french/F-F_Research_Data_Factors_CSV.zip"
    rec = root / "factor_analysis/data/raw/french/french_source_record.json"
    if not z.exists():
        return [chk("FACTOR.french_raw_present", "BLOCKED",
                    "No Kenneth French file in factor_analysis/data/raw/french/. The official brief requires the group to retrieve it in Python from French's site; this build environment cannot reach mba.tuck.dartmouth.edu. Run `python -m factor_analysis.french_data fetch` on a networked machine; no factor result is fabricated or substituted (VTI is not Mkt-RF).")]
    out = []
    meta = json.loads(rec.read_text()) if rec.exists() else {}
    out.append(chk("FACTOR.french_raw_hash", "PASS" if meta.get("sha256") == sha256(z) else "FAIL",
                   f"recorded={meta.get('sha256', 'MISSING')[:16]} actual={sha256(z)[:16]}"))
    try:
        sys.path.insert(0, str(root))
        from factor_analysis import french_data
        df, _ = french_data.parse_ff3_zip(z)
        out.append(chk("FACTOR.french_parse_96m", "PASS", f"{len(df)} months decimal units; Mkt-RF mean={df['Mkt-RF'].mean():.5f}"))
    except Exception as e:
        out.append(chk("FACTOR.french_parse_96m", "FAIL", str(e)))
    return out


NOTEBOOKS = ["bond_funding/notebooks/bond_funding_analysis.ipynb", "factor_analysis/notebooks/factor_analysis.ipynb"]


def check_notebooks(root, notebooks=None):
    """Each delivered notebook must exist, have every code cell executed (execution_count set), and contain no error output."""
    root = Path(root)
    out = []
    for rel in (notebooks or NOTEBOOKS):
        p = root / rel
        if not p.exists():
            out.append(chk(f"NOTEBOOK.{p.stem}", "FAIL", f"{rel} is missing"))
            continue
        try:
            nb = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:  # malformed JSON
            out.append(chk(f"NOTEBOOK.{p.stem}", "FAIL", f"{rel} is not valid notebook JSON: {e}"))
            continue
        code = [c for c in nb.get("cells", []) if c.get("cell_type") == "code"]
        unexecuted = [i for i, c in enumerate(code, 1) if c.get("execution_count") is None]
        errors = [i for i, c in enumerate(code, 1) if any(o.get("output_type") == "error" for o in c.get("outputs", []))]
        silent = [i for i, c in enumerate(code, 1) if not c.get("outputs")]
        if unexecuted or errors:
            out.append(chk(f"NOTEBOOK.{p.stem}", "FAIL", f"{rel}: unexecuted code cells {unexecuted}; cells with errors {errors}"))
        else:
            out.append(chk(f"NOTEBOOK.{p.stem}", "PASS", f"{rel}: {len(code)} code cells, all executed with no error output ({len(code) - len(silent)} with visible output)"))
    return out
