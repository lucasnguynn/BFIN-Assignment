"""Workstream 4: market-only and multifactor regressions, OFFLINE.

Inputs (all saved files, no network):
  portfolio_construction/data/processed/asset_monthly_returns_estimation.csv   monthly simple returns, decimals
  portfolio_construction/evidence/decision_weights_confirmed.csv               frozen growth weights (22 Oct policy)
  portfolio_construction/outputs/policy_weights.csv                            rejected Minimum_Variance weights
  factor_analysis/data/raw/french/F-F_Research_Data_Factors_CSV.zip            Kenneth French FF3 monthly (raw bytes)

Return construction for the growth strategy over 2015-2022: constant (static) weights applied to monthly
asset returns, i.e. the same "static exposure" series the portfolio module hands off. It is NOT the buy-and-hold drifting
series used for 2023-25 evaluation; for a 96-month estimation sample this is the standard exposure proxy.
"""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np
import pandas as pd

from factor_analysis import french_data
from factor_analysis.ols import ols, nested_f, diagnostics

HELD = ["AAPL", "MSFT", "JPM", "JNJ", "PFE", "PG", "KO", "CAT"]
REQUIRED_SECURITIES = ["MSFT", "PG"]  # required securities; the others are reported as robustness
MODELS = {"CAPM": ["Mkt-RF"], "FF3": ["Mkt-RF", "SMB", "HML"]}


def load_inputs(root):
    root = Path(root)
    pc = root / "portfolio_construction"
    rets = pd.read_csv(pc / "data/processed/asset_monthly_returns_estimation.csv")
    w = pd.read_csv(pc / "evidence/decision_weights_confirmed.csv").set_index("security")["weight_of_growth_sleeve"]
    pw = pd.read_csv(pc / "outputs/policy_weights.csv")
    mv = pw[pw.policy == "Minimum_Variance"].set_index("ticker")["growth_weight"]
    assets = [c for c in rets.columns if c not in ("month", "VTI")]
    subjects = {
        "GROWTH_FROZEN_SAMPLE_MV": rets[assets].to_numpy() @ w.loc[assets].to_numpy(),
        "REJECTED_MIN_VARIANCE": rets[assets].to_numpy() @ mv.loc[assets].to_numpy(),
    }
    for t in HELD:
        subjects[t] = rets[t].to_numpy()
    subjects["VTI_BENCHMARK"] = rets["VTI"].to_numpy()
    return rets, pd.DataFrame(subjects, index=rets.month)


def run_factor_models(root, out_dir=None):
    """Full FF3 workflow. Raises FileNotFoundError if the raw French file is absent (no fallback)."""
    root = Path(root)
    out = Path(out_dir) if out_dir else root / "factor_analysis" / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    zpath = root / "factor_analysis" / "data" / "raw" / "french" / french_data.RAW_ZIP
    if not zpath.exists():
        raise FileNotFoundError(f"{zpath} missing - run `python -m factor_analysis.french_data fetch` on a networked machine")
    fac, _ = french_data.parse_ff3_zip(zpath)
    rets, subj = load_inputs(root)
    if list(fac.month) != list(subj.index):
        raise ValueError("factor and return months do not align")
    rf = fac["RF"].to_numpy()
    F = fac.set_index("month")
    rows, comp, diag, fits = [], [], [], {}
    for name in subj.columns:
        y = subj[name].to_numpy() - rf  # excess return, decimals
        res = {}
        for mname, facs in MODELS.items():
            r = ols(y, F[facs].to_numpy(), facs)
            res[mname] = r
            fits[(name, mname)] = r
            row = dict(strategy_or_ticker=name, model=mname, n=r["n"], r2=r["r2"], r2_adj=r["adj_r2"],
                       resid_sd_monthly=r["resid_sd"], hac_lags=r["hac_lags"])
            for term, b, se, t, p, lo, hi, seh, th in zip(r["names"], r["b"], r["se"], r["t"], r["p"],
                                                           r["ci_lo"], r["ci_hi"], r["se_hac"], r["t_hac"]):
                key = "alpha" if term == "const" else term.replace("-", "_")
                row.update({f"{key}": b, f"{key}_se": se, f"{key}_t": t, f"{key}_p": p, f"{key}_ci95_lo": lo,
                            f"{key}_ci95_hi": hi, f"{key}_se_hac": seh, f"{key}_t_hac": th})
            row["alpha_annualized_compound"] = (1 + r["b"][0]) ** 12 - 1
            rows.append(row)
            d = diagnostics(r)
            diag.append(dict(strategy_or_ticker=name, model=mname, n=r["n"], **d))
        Fv, Fp, q = nested_f(res["CAPM"], res["FF3"])
        c, f3 = res["CAPM"], res["FF3"]
        comp.append(dict(
            strategy_or_ticker=name, n=c["n"],
            alpha_capm=c["b"][0], alpha_capm_t=c["t"][0], alpha_ff3=f3["b"][0], alpha_ff3_t=f3["t"][0],
            alpha_change_monthly=f3["b"][0] - c["b"][0], alpha_sign_flip=bool(np.sign(c["b"][0]) != np.sign(f3["b"][0])),
            alpha_significant_5pct_capm=bool(c["p"][0] < .05), alpha_significant_5pct_ff3=bool(f3["p"][0] < .05),
            r2_adj_capm=c["adj_r2"], r2_adj_ff3=f3["adj_r2"], r2_adj_gain=f3["adj_r2"] - c["adj_r2"],
            nested_F_SMB_HML=Fv, nested_F_p=Fp, nested_F_q=q,
            aic_capm=c["aic"], aic_ff3=f3["aic"], bic_capm=c["bic"], bic_ff3=f3["bic"],
            bic_preferred="FF3" if f3["bic"] < c["bic"] else "CAPM"))
    coef = pd.DataFrame(rows)
    cmp_ = pd.DataFrame(comp)
    dg = pd.DataFrame(diag)
    coef.to_csv(out / "factor_coefficients.csv", index=False, float_format="%.10g")
    cmp_.to_csv(out / "factor_model_comparison.csv", index=False, float_format="%.10g")
    dg.to_csv(out / "factor_diagnostics.csv", index=False, float_format="%.10g")
    plot_exposures(coef, out / "factor_exposures.png")
    return coef, cmp_, dg


def plot_exposures(coef, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ff = coef[coef.model == "FF3"].reset_index(drop=True)
    labels = [s.replace("GROWTH_FROZEN_SAMPLE_MV", "GROWTH\n(frozen)").replace("REJECTED_MIN_VARIANCE", "MIN-VAR\n(rejected)")
              .replace("VTI_BENCHMARK", "VTI") for s in ff.strategy_or_ticker]
    fig, ax = plt.subplots(1, 4, figsize=(17, 5.2), sharey=True)
    panels = [("alpha", "Alpha (monthly, decimal)"), ("Mkt_RF", "Market beta (Mkt-RF)"),
              ("SMB", "Size loading (SMB)"), ("HML", "Value loading (HML)")]
    y = np.arange(len(ff))[::-1]
    for a, (k, title) in zip(ax, panels):
        est = ff[k].to_numpy()
        lo = est - ff[f"{k}_ci95_lo"].to_numpy()
        hi = ff[f"{k}_ci95_hi"].to_numpy() - est
        cols = ["#c0392b" if s.startswith("GROWTH") else "#7f8c8d" for s in ff.strategy_or_ticker]
        a.errorbar(est, y, xerr=[lo, hi], fmt="none", ecolor="#555", elinewidth=1.2, capsize=3)
        a.scatter(est, y, c=cols, zorder=3, s=40)
        a.axvline(1.0 if k == "Mkt_RF" else 0.0, color="k", lw=.8, ls="--")
        a.set_title(title, fontsize=10)
        a.grid(axis="x", alpha=.3)
    ax[0].set_yticks(y)
    ax[0].set_yticklabels(labels, fontsize=8)
    fig.suptitle("FF3 exposures with 95% confidence intervals, monthly 2015-01..2022-12 (n=96). "
                 "Intervals wide = uncertain; alpha CI crossing 0 = not distinguishable from zero.", fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, .94])
    fig.savefig(path, dpi=150)
    plt.close(fig)


def preliminary_vti_proxy(root, out_dir=None):
    """NOT a deliverable. VTI used as market proxy on RAW returns (no risk-free rate, no SMB/HML).
    Intercept is therefore NOT Jensen's alpha. Written to a clearly named PRELIMINARY file only."""
    root = Path(root)
    out = Path(out_dir) if out_dir else root / "factor_analysis" / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    rets, subj = load_inputs(root)
    x = rets["VTI"].to_numpy()
    rows = []
    for name in [c for c in subj.columns if c != "VTI_BENCHMARK"]:  # VTI on itself is trivial
        r = ols(subj[name].to_numpy(), x, ["VTI"])
        rows.append(dict(strategy_or_ticker=name, n=r["n"], intercept_monthly=r["b"][0], intercept_se=r["se"][0],
                         intercept_t=r["t"][0], beta_vs_VTI=r["b"][1], beta_se=r["se"][1],
                         beta_ci95_lo=r["ci_lo"][1], beta_ci95_hi=r["ci_hi"][1], r2_adj=r["adj_r2"],
                         status="PRELIMINARY_VTI_PROXY_RAW_RETURNS_NOT_FRENCH_NOT_DELIVERABLE"))
    df = pd.DataFrame(rows)
    df.to_csv(out / "PRELIMINARY_vti_proxy_market_model.csv", index=False, float_format="%.10g")
    return df


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    try:
        run_factor_models(root)
        print("factor models written")
    except FileNotFoundError as e:
        print("BLOCKED:", e)
        print(preliminary_vti_proxy(root).round(4).to_string())
