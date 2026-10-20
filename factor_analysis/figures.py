"""Workstream 4 figures, OFFLINE and matplotlib-only (no seaborn / statsmodels dependency).

Reads the result tables written by `factor_analysis.models.run_factor_models` and the saved raw files.
Writes three figures to factor_analysis/outputs/figures/:
  figure_alpha_capm_vs_ff3.png            annualised alpha (12 x monthly) under CAPM and FF3, significance marked
  figure_adjusted_r2_capm_vs_ff3.png      adjusted R-squared under CAPM and FF3
  figure_actual_vs_fitted_growth.png      growth sleeve: actual vs FF3-fitted monthly excess returns
(The FF3 exposure figure with 95% confidence intervals is factor_analysis/outputs/factor_exposures.png.)
"""
from __future__ import annotations
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from factor_analysis import french_data, models

SUBJECTS = ["GROWTH_FROZEN_SAMPLE_MV", "REJECTED_MIN_VARIANCE", "AAPL", "MSFT", "JPM", "JNJ", "PFE", "PG", "KO", "CAT"]
LABELS = {"GROWTH_FROZEN_SAMPLE_MV": "Growth sleeve (frozen)", "REJECTED_MIN_VARIANCE": "Min-Variance (rejected)"}
C_CAPM, C_FF3 = "#1F3864", "#C55A11"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False})


def _label(s):
    return LABELS.get(s, s)


def _split(coef):
    capm = coef[coef.model == "CAPM"].set_index("strategy_or_ticker").loc[SUBJECTS]
    ff3 = coef[coef.model == "FF3"].set_index("strategy_or_ticker").loc[SUBJECTS]
    return capm, ff3


def figure_alpha(coef, path):
    capm, ff3 = _split(coef)
    y = np.arange(len(SUBJECTS))[::-1]
    h = 0.38
    fig, ax = plt.subplots(figsize=(9.5, 6))
    ax.barh(y + h / 2, capm["alpha"] * 1200, h, color=C_CAPM, label="CAPM (market-only)")
    ax.barh(y - h / 2, ff3["alpha"] * 1200, h, color=C_FF3, label="FF3 (three-factor)")
    for yy, (_, a), (_, b) in zip(y, capm.iterrows(), ff3.iterrows()):
        for off, r in ((h / 2, a), (-h / 2, b)):
            star = "*" if r["alpha_p"] < 0.05 else ""
            ax.text(r["alpha"] * 1200 + 0.2, yy + off, f"{r['alpha'] * 1200:.1f}%{star}", va="center", fontsize=8)
    ax.set_yticks(y)
    ax.set_yticklabels([_label(s) for s in SUBJECTS])
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlabel("Annualised alpha (12 × monthly alpha), % per year")
    ax.set_title("Estimated alpha under CAPM and FF3, January 2015 to December 2022", fontsize=11, fontweight="bold", loc="left")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", alpha=0.3)
    fig.text(0.01, 0.01, "* significant at the 5% level (classical t-test). All other estimates are not distinguishable from zero. "
             "Alphas are in-sample and are not evidence of skill or persistence.", fontsize=8, color="#595959")
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(path, dpi=200)
    plt.close(fig)


def figure_r2(coef, path):
    capm, ff3 = _split(coef)
    x = np.arange(len(SUBJECTS))
    w = 0.38
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.bar(x - w / 2, capm["r2_adj"], w, color=C_CAPM, label="CAPM (market-only)")
    ax.bar(x + w / 2, ff3["r2_adj"], w, color=C_FF3, label="FF3 (three-factor)")
    for xx, a, b in zip(x, capm["r2_adj"], ff3["r2_adj"]):
        ax.text(xx - w / 2, a + 0.01, f"{a:.2f}", ha="center", fontsize=8)
        ax.text(xx + w / 2, b + 0.01, f"{b:.2f}", ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([_label(s).replace(" (", "\n(") for s in SUBJECTS], fontsize=8)
    ax.set_ylabel("Adjusted R²")
    ax.set_ylim(0, 1)
    ax.set_title("Explanatory power: adjusted R² under CAPM and FF3", fontsize=11, fontweight="bold", loc="left")
    ax.legend(frameon=False, loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def figure_fit(root, coef, path):
    root = Path(root)
    fac, _ = french_data.parse_ff3_zip(root / "factor_analysis/data/raw/french" / french_data.RAW_ZIP)
    _, subj = models.load_inputs(root)
    c = coef[(coef.model == "FF3") & (coef.strategy_or_ticker == "GROWTH_FROZEN_SAMPLE_MV")].iloc[0]
    actual = subj["GROWTH_FROZEN_SAMPLE_MV"].to_numpy() - fac["RF"].to_numpy()
    fitted = c["alpha"] + c["Mkt_RF"] * fac["Mkt-RF"].to_numpy() + c["SMB"] * fac["SMB"].to_numpy() + c["HML"] * fac["HML"].to_numpy()
    lim = float(max(np.abs(actual).max(), np.abs(fitted).max()) * 100) + 1
    fig, ax = plt.subplots(figsize=(6.4, 6))
    ax.scatter(fitted * 100, actual * 100, s=28, color=C_CAPM, alpha=0.8, edgecolor="white", linewidth=0.5)
    ax.plot([-lim, lim], [-lim, lim], color=C_FF3, lw=1.5, label="45° line (perfect fit)")
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_xlabel("FF3-fitted monthly excess return, %")
    ax.set_ylabel("Actual monthly excess return, %")
    ax.set_title("Growth sleeve: actual versus FF3-fitted returns", fontsize=11, fontweight="bold", loc="left")
    ax.text(0.04, 0.95, f"R² = {c['r2']:.3f}   adjusted R² = {c['r2_adj']:.3f}\nn = {int(c['n'])} months", transform=ax.transAxes,
            va="top", fontsize=9, bbox=dict(facecolor="white", edgecolor="#BFBFBF"))
    ax.legend(frameon=False, loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def make_figures(root, coef=None, out_dir=None):
    root = Path(root)
    out = Path(out_dir) if out_dir else root / "factor_analysis" / "outputs" / "figures"
    out.mkdir(parents=True, exist_ok=True)
    if coef is None:
        coef = pd.read_csv(root / "factor_analysis/outputs/factor_coefficients.csv")
    paths = [out / "figure_alpha_capm_vs_ff3.png", out / "figure_adjusted_r2_capm_vs_ff3.png", out / "figure_actual_vs_fitted_growth.png"]
    figure_alpha(coef, paths[0])
    figure_r2(coef, paths[1])
    figure_fit(root, coef, paths[2])
    return paths
