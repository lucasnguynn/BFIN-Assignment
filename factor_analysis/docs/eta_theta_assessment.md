# Eta vs Theta - Economic Significance Assessment of Factor Coefficients (Workstream 4)

> **STATUS: DRAFT FRAMEWORK - NO OFFICIAL REGRESSION RESULTS YET.**
> Kenneth French data (Mkt-RF, SMB, HML, RF) has not been downloaded yet (see `README.md`, step 2). All "RESULTS" items below will be populated from `factor_analysis/outputs/*.csv` after running `run_pipeline.py`. No SMB/HML/alpha figures in this file are estimated or fabricated.

## 1. What is known for certain (real data, but ONLY a preliminary proxy)
Source: `factor_analysis/outputs/PRELIMINARY_vti_proxy_market_model.csv` - raw return regression against VTI, 96 months 2015-01..2022-12.
**This is not CAPM/Jensen's alpha**: the risk-free rate is not deducted, VTI is not Mkt-RF, no SMB/HML yet.

| Asset | Beta vs VTI (95% CI) | Adjusted R² |
|---|---|---|
| Frozen growth portfolio (Sample MV) | 0.82 (0.73-0.90) | 0.79 |
| Min-Variance portfolio (rejected) | 0.71 (0.63-0.79) | 0.77 |
| MSFT | 0.96 (0.76-1.17) | 0.48 |
| PG | 0.39 (0.21-0.57) | 0.15 |

Interpretation (confidence level: medium, as it is a proxy): the growth portfolio's sensitivity to the market is **lower than 1** (around 0.8): about 80% of the monthly variance is explained by the broad market; the rest is idiosyncratic/factor risk. MSFT is close to beta 1 but has low R² (high idiosyncratic risk); PG is defensive (beta ~0.4, R² 0.15).
This aligns with the portfolio structure: max 15%/stock, many defensive tickers (PG, KO, JNJ, PFE).

## 2. Hypotheses to test (NOT results)
- **SMB (size)**: the portfolio is entirely large-cap (AAPL, MSFT, JPM, JNJ, PG, KO, CAT, PFE) and 0% IWM => expect negative or near-zero SMB loading.
- **HML (value)**: mixed - AAPL/MSFT are growth (negative HML), PG/KO/JNJ/PFE/JPM/CAT lean towards value/defensive (positive HML). The aggregate sign cannot be predicted yet; let the data decide.
- **Alpha**: expect positive in-sample CAPM alpha (see proxy: positive intercept), and **likely to decrease when adding SMB/HML** if the "outperformance" is actually a factor premium.

## 3. What estimated Alpha allows and DOES NOT allow us to conclude
1. **In-sample selection bias.** Weights were optimized using the exact 2015-2022 sample (25% individual historical mean + 75% VTI), plus a 12-ticker universe retroactively selected in 2026. Therefore, a positive in-sample alpha is partly **mechanical** (picking winners ex post), not skill.
2. **Alpha is not skill**: alpha = the portion of return unexplained by the *chosen model*. Different model, different alpha (will report `alpha_change_monthly`, `alpha_sign_flip`).
3. **Uncertainty**: with n=96, the monthly alpha's SE is wide; only conclude when the 95% CI (and Newey-West SE) does not contain 0. With 8 stocks + 2 portfolios + VTI x 2 models, there is a **multiple testing** problem (~1/20 results will be "significant" by chance at the 5% level).
4. **Data**: Yahoo's Adj Close (retrieved 2026) and the latest French vintage may have been adjusted/revised compared to the Dec 31, 2022 vintage.
5. **Persistence untested**: cannot claim that the 2015-22 alpha will persist into 2023-25 before conducting the frozen evaluation (WS6) with pre-declared criteria.

## 4. Eta (treasurer: historical Sharpe/risk-adjusted return) vs Theta (adviser: factors + sustainable alpha)
| | Eta | Theta |
|---|---|---|
| Logic | select assets with the highest historical Sharpe | select based on factor loadings and "sustainable" alpha |
| Strengths | simple, transparent | separates returns driven by beta/factors from the residual |
| Weaknesses | noisy sample, large estimation error for Sharpe, overfit | model-dependent alpha; persistence unproven; multiple testing |
| Relation to group recommendation | Sample-MV has a "historically selected" component, so it is **closer to Eta** than expected; the group shrank it 75% toward VTI and set 15%/30% caps to reduce overfitting | factors are used to **explain and monitor risk**, not using alpha as a basis for selecting weights |

**RESULTS (to be filled later):** `factor_coefficients.csv` table (alpha, beta, SE, t, CI, adj R²) and `factor_model_comparison.csv` (CAPM->FF3 alpha change, SMB+HML F-test, BIC) for GROWTH, MSFT, PG + 6 other tickers.
Filling rule: every concluding sentence must cite a specific cell in the CSV; if the CI contains 0, state "indistinguishable from 0".

