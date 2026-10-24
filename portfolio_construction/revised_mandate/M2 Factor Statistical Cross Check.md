# M2 independent statistical reading of the Member 3 factor results

**Evidence-based technical review, 24 October 2026 — not a signed Member 3 peer approval.** Source: `factor_analysis/outputs/factor_coefficients.csv` and `factor_model_comparison.csv` (2015-01 to 2022-12, n=96 monthly observations). The corresponding tests run in the GitHub CI; this note checks interpretation and the exposure handoff rather than claiming that a second econometric system was fitted independently.

| Historical FF3 coefficient or statistic | Frozen growth | MSFT | PG |
|---|---:|---:|---:|
| Monthly alpha, decimal | 0.005691 | 0.010673 | 0.003828 |
| Conventional alpha p-value | 0.001879 | 0.015551 | 0.353838 |
| HAC alpha t-statistic | 3.848 | 3.035 | 1.030 |
| Market (Mkt−RF) beta | 0.8667 | 1.0598 | 0.4642 |
| SMB exposure | −0.4265 | −0.6209 | −0.6715 |
| HML exposure | 0.0101 | −0.3649 | 0.0442 |
| Adjusted R² | 0.8437 | 0.5889 | 0.2585 |

**Interpretation.** The growth sleeve has a positive FF3 in-sample intercept, below-market beta and negative SMB loading; it is closer to large-cap exposure than to a small-stock tilt. The HML coefficient is close to zero. The model explains more within-sample variation than CAPM (adjusted R² **0.84365 versus 0.78499**), with a reported nested F-test p-value approximately **1.60 × 10⁻⁷** for adding SMB and HML. This supports a richer explanation of historical co-movement, **not** a conclusion that the return forecast should incorporate a persistent 0.569% monthly abnormal return.

MSFT and PG are appropriate contrasts: MSFT's market beta is slightly above one with negative SMB and HML loadings; PG's market beta is about 0.464 and its individual FF3 alpha is not conventionally distinguishable from zero (p≈0.354). A blanket assertion that all selected stocks produce significant alpha would conflict with the actual regression results. Values are in decimals per month for the intercept and decimal units for factor returns, not annual percentages.

**Required boundary tests for M3.** Confirm the factor month key and RF subtraction once; do not confuse 2015–2022 constant-weight return proxies with the 2023–2025 buy-and-hold performance path. Under M1 principal/coupon changes with frozen normalized weights, the growth CAPM/FF3 exposures should be identical. Only the contribution of equity exposure to foundation-level allocation risk changes. When revised weights are reoptimized, a corresponding factor regression must be rerun before assigning a new alpha/beta to the changed portfolio.

**Limitations.** One 96-month sample, multiple modeled securities, possibly autocorrelated/heteroskedastic residuals, retrospective selection of surviving tickers, and vendor-adjusted historical data substantially weaken claims of *persistent* alpha. The conventional p-values and HAC t-statistics describe estimates under the chosen model; they do not solve selection bias or establish out-of-sample predictability. The observed 2023–2025 growth underperformance against VTI strengthens the case for a skeptical interpretation.

**Source mapping:** `factor_analysis/models.py`, `factor_analysis/data/raw/french/F-F_Research_Data_Factors_CSV.zip`, `factor_analysis/outputs/factor_coefficients.csv`, `factor_analysis/outputs/factor_model_comparison.csv`, original M2 frozen weights/returns, `portfolio_construction/revised_mandate/m3_handoff.py`.

**Review status:** M2 statistical interpretation check documented, not a signed human reviewer attestation.