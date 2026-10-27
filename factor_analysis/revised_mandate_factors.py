#!/usr/bin/env python3
"""Factor evidence under the revised trustee mandate (information set: 31 Dec 2022).

Question answered: does the revised payment schedule (or the funding method chosen for it)
change the market-only (CAPM) and Fama-French three-factor (FF3) evidence?

Method
------
1. Rebuild the 15 scenario growth series (3 funding scenarios x 5 equity policies) with the
   committed revised-mandate model; every series is 96 static-weight monthly simple returns
   (2015-01 to 2022-12, decimals). No 2023-2025 observation is used.
2. Estimate CAPM and FF3 on each series with the same OLS code and the same archived Kenneth
   French file as the 22 October factor analysis.
3. Write one row per scenario and flag whether its series is numerically identical to the
   frozen 22 October growth series. A funding-only change must leave the frozen series, and
   hence every factor estimate, unchanged.

Run:  python -m factor_analysis.revised_mandate_factors   (offline; ~seconds)
"""
from __future__ import annotations
import sys, tempfile
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "portfolio_construction" / "revised_mandate"))
from factor_analysis import french_data                      # noqa: E402
from factor_analysis.models import MODELS                    # noqa: E402
from factor_analysis.ols import ols, nested_f                # noqa: E402

TOL = 1e-12
OUT = ROOT / "factor_analysis" / "outputs" / "revised_mandate_factor_scenarios.csv"


def scenario_series(root=ROOT):
    """Return DataFrame(month + 15 scenario columns) from the committed revised-mandate model."""
    from m1_integration import run as run_revised_model      # noqa: E402
    with tempfile.TemporaryDirectory() as tmp:
        run_revised_model(Path(tmp))
        return pd.read_csv(Path(tmp) / "growth_static_returns_2015_2022.csv")


def build(root=ROOT, out=OUT):
    root = Path(root)
    series = scenario_series(root)
    fac, _ = french_data.parse_ff3_zip(root / "factor_analysis/data/raw/french" / french_data.RAW_ZIP)
    if list(fac.month) != list(series.month):
        raise ValueError("factor and scenario months do not align")
    F = fac.set_index("month")
    rf = fac["RF"].to_numpy()
    base = series["ORIGINAL_FROZEN__FROZEN_SAMPLE_MV"].to_numpy()
    rows = []
    for name in series.columns[1:]:
        funding, policy = name.split("__")
        y = series[name].to_numpy() - rf
        capm = ols(y, F[MODELS["CAPM"]].to_numpy(), MODELS["CAPM"])
        ff3 = ols(y, F[MODELS["FF3"]].to_numpy(), MODELS["FF3"])
        Fv, Fp, _ = nested_f(capm, ff3)
        gap = float(np.max(np.abs(series[name].to_numpy() - base)))
        rows.append(dict(
            scenario_id=name, funding_scenario=funding, portfolio_policy=policy, n=ff3["n"],
            max_abs_gap_vs_frozen_series=gap, identical_to_frozen_series=bool(gap <= TOL),
            beta_capm=capm["b"][1], alpha_capm_monthly=capm["b"][0], alpha_capm_t=capm["t"][0], r2_adj_capm=capm["adj_r2"],
            beta_mkt_ff3=ff3["b"][1], smb=ff3["b"][2], hml=ff3["b"][3],
            alpha_ff3_monthly=ff3["b"][0], alpha_ff3_t=ff3["t"][0], alpha_ff3_p=ff3["p"][0],
            r2_adj_ff3=ff3["adj_r2"], nested_F_SMB_HML=Fv, nested_F_p=Fp))
    df = pd.DataFrame(rows)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, float_format="%.10g")
    return df


if __name__ == "__main__":
    d = build()
    print(d[["scenario_id", "identical_to_frozen_series", "beta_mkt_ff3", "smb", "hml", "alpha_ff3_monthly", "r2_adj_ff3"]].to_string(index=False))
