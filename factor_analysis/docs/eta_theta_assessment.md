# Factor Analysis of the Growth Allocation

**Empirical findings, economic interpretation and implications for the investment policy (Workstream 4)**

| Item | Detail |
|---|---|
| Project | Kappa Foundation: liability-first, risk-constrained investment policy (BFIN WS2026) |
| Case decision date / information cutoff | 31 December 2022 (estimation uses data to December 2022 only) |
| Estimation window | January 2015 to December 2022, 96 monthly observations |
| Data sources | Yahoo Finance adjusted-close returns (via `yfinance`); Kenneth R. French Data Library, `F-F_Research_Data_Factors` (monthly) |
| Models | Market-only (CAPM) and Fama-French three-factor (FF3), estimated by ordinary least squares |
| Document status | Final empirical results. The three-factor model is part of the Lecture 7 model menu (Fama-French three-factor, Carhart four-factor and five-factor models). |
| Version / date | 1.0, 20 October 2026 |

## Summary of findings

1. **Market exposure dominates.** The frozen growth sleeve has a market loading of 0.87 (95% confidence interval 0.79 to 0.94). Adding SMB and HML raises adjusted R² from 0.785 to 0.844, and the two factors are jointly significant (p < 0.001).
2. **The sleeve is tilted towards large-capitalisation stocks.** The size loading is −0.43 (t = −6.10). The value loading is statistically indistinguishable from zero (0.010), reflecting offsetting growth and value holdings rather than an absence of style exposure.
3. **Estimated alpha is positive and statistically significant in sample, but it is not evidence of skill or of persistence.** As Lecture 7 states, a significant positive alpha is evidence of outperformance relative to the chosen model and does not establish skill by itself. It is 0.57% per month under FF3 (p = 0.0019) and is estimated on the same window used to construct the portfolio, from an ex post selected universe.
4. **Factor evidence relates to the decision mainly through risk and through the expected-return inputs, not through alpha.** A factor-implied cross-check places the expected return below the 12.05% forecast in the Initial Decision Record, which supports the use of shrinkage and cautious interpretation (Section 6).
5. **The evidence does not support allocating on estimated alpha (Theta's position) and does not by itself validate selection on historical risk-adjusted performance (Eta's position).** Both positions are assessed in Section 5.

## 1. Purpose and scope

The case brief requires a comparison of a market-only model with at least one multifactor model for the growth portfolio and at least two selected securities, an explanation of economic exposures and uncertainty, and a statement of what an estimated alpha does and does not establish. This document addresses three questions:

1. To what extent are the historical returns of the growth allocation explained by market exposure, by systematic factors, or by abnormal return?
2. What can, and what cannot, be concluded from the estimated alpha?
3. What do the results imply for the expected-return inputs and for the competing positions of Eta (the treasurer) and Theta (the external adviser)?

## 2. Data and methodology

### 2.1 Data

Security returns are monthly simple returns, in decimal units, computed from Yahoo Finance adjusted closing prices for January 2015 to December 2022 (96 observations; no missing values). Factor data are the monthly Mkt-RF, SMB, HML and RF series of the Kenneth R. French Data Library. French publishes these series in percent; they were divided by 100 so that all variables are in decimal units. The factor and return series were aligned by calendar month, and the factor window was verified to contain exactly 96 months from 2015-01 to 2022-12.

The source file carries the header "This file was created using the 202608 CRSP database". Both the Yahoo and the French series are the latest vintages available in October 2026 and may incorporate revisions made after the case date. This is disclosed as a limitation (Section 7).

### 2.2 Return series analysed

The growth sleeve is constructed by applying the frozen Sample Mean-Variance weights of the Initial Decision Record as constant weights to the monthly security returns. This is the standard exposure proxy for an estimation window. It differs from the buy-and-hold series with drifting weights that governs the 2023 to 2025 evaluation. The rejected Minimum-Variance sleeve is constructed in the same way, as a comparison policy. The subjects are the growth sleeve, the rejected sleeve, the two required securities (MSFT and PG), the other six holdings (AAPL, JPM, JNJ, PFE, KO, CAT) as robustness cases, and the VTI benchmark.

### 2.3 Models

For subject *i* in month *t*, with excess return r<sub>i,t</sub> − RF<sub>t</sub>:

- **Model A (market-only):** r<sub>i,t</sub> − RF<sub>t</sub> = α<sub>i</sub> + β<sub>M,i</sub> (Mkt-RF)<sub>t</sub> + ε<sub>i,t</sub>
- **Model B (three-factor):** r<sub>i,t</sub> − RF<sub>t</sub> = α<sub>i</sub> + β<sub>M,i</sub> (Mkt-RF)<sub>t</sub> + s<sub>i</sub> SMB<sub>t</sub> + h<sub>i</sub> HML<sub>t</sub> + ε<sub>i,t</sub>

Model B is the Fama-French three-factor regression presented in Lecture 7, estimated on the same French data series (`F-F_Research_Data_Factors`) that the lecture uses. Lecture 7 also presents the Carhart four-factor model (adding momentum) and the Fama-French five-factor model (adding profitability and investment). The case brief requires at least one multifactor model from the lecture, so those two models are not estimated here.

### 2.4 Inference and diagnostics

Coefficients are estimated by ordinary least squares. Reported uncertainty comprises classical standard errors with t-based 95% confidence intervals and, as a robustness check, Newey-West standard errors (Bartlett kernel, three lags). The joint contribution of SMB and HML is tested with a nested F-test, and the two models are compared by adjusted R² and the Bayesian information criterion (BIC). Residuals are examined with the Durbin-Watson and Ljung-Box (12 lags) tests for serial correlation, the Jarque-Bera test for normality, the Breusch-Pagan test for heteroskedasticity, and variance inflation factors for multicollinearity. The growth-sleeve coefficients were verified independently with a separate least-squares routine, and a full rerun of the pipeline from the saved raw files reproduces every reported coefficient exactly.

## 3. Results

### 3.1 Growth sleeve

**Table 1. Growth sleeve: market-only and three-factor estimates (monthly excess returns, n = 96)**

| Statistic | Model A: market-only (CAPM) | Model B: three-factor (FF3) |
|---|---|---|
| Alpha, monthly | 0.65% | 0.57% |
|   95% confidence interval | [0.23%, 1.06%] | [0.22%, 0.92%] |
|   t-statistic (classical / Newey-West) | 3.11 / 3.50 | 3.20 / 3.85 |
|   p-value | 0.0025 | 0.0019 |
| Alpha, annualised (12 × monthly) | 7.76% | 6.83% |
| Alpha, annualised (compounded) | 8.04% | 7.05% |
| Market loading (Mkt-RF) | 0.805 [0.719, 0.891] | 0.867 [0.791, 0.943] |
| Size loading (SMB) | n/a | −0.426 [−0.565, −0.288] |
|   t-statistic (classical / Newey-West) | n/a | −6.10 / −6.46 |
| Value loading (HML) | n/a | 0.010 [−0.081, 0.101] |
|   t-statistic (classical / Newey-West) | n/a | 0.22 / 0.27 |
| Adjusted R² | 0.785 | 0.844 |
| Observations | 96 | 96 |

*Notes: confidence intervals are 95%, t-based. Alpha is in decimal return per month and shown as a percentage.*

### 3.2 Comparison with the rejected policy and the required securities

**Table 2. Three-factor estimates for the policies and the two required securities**

| Subject | Alpha per month, CAPM → FF3 | Alpha t (FF3) | β Mkt-RF | s SMB (t) | h HML (t) | Adj. R², CAPM → FF3 | p-value, SMB and HML jointly zero |
|---|---|---|---|---|---|---|---|
| Growth sleeve (frozen Sample-MV) | 0.65% → 0.57% | 3.20 | 0.867 | −0.426 (−6.10) | 0.010 (0.22) | 0.785 → 0.844 | < 0.0001 |
| Minimum-Variance sleeve (rejected) | 0.34% → 0.28% | 1.70 | 0.745 | −0.395 (−6.09) | 0.109 (2.57) | 0.749 → 0.825 | < 0.0001 |
| MSFT | 1.21% → 1.07% | 2.47 | 1.060 | −0.621 (−3.65) | −0.365 (−3.28) | 0.490 → 0.589 | < 0.0001 |
| PG | 0.50% → 0.38% | 0.93 | 0.464 | −0.672 (−4.16) | 0.044 (0.42) | 0.137 → 0.259 | 0.0003 |

*Notes: t-statistics are classical. The final column is the p-value of the nested F-test that the SMB and HML coefficients are jointly zero.*

Estimates for the remaining holdings and the benchmark are reported in the Appendix (Table A1).

## 4. Economic interpretation

### 4.1 Market exposure

The growth sleeve has a market loading of 0.87, below one, as expected for a portfolio containing several defensive holdings (PG, KO, JNJ, PFE). The rejected Minimum-Variance sleeve has a lower loading (0.75). The two required securities illustrate the dispersion in the sleeve: MSFT has a loading near one (1.06) but an adjusted R² of only 0.59, so roughly 40% of its variance is idiosyncratic, whereas PG is defensive (loading 0.46; adjusted R² 0.26). Market exposure is the principal source of the sleeve's risk, which is relevant to the trustees' loss concern (Section 6).

### 4.2 Size exposure

The sleeve's size loading is −0.43 (95% confidence interval −0.57 to −0.29), and it remains significant under Newey-West standard errors. A negative SMB loading means the sleeve behaves like large-capitalisation stocks and is positioned opposite to the small-cap premium. Five of the eight holdings (MSFT, JNJ, PFE, PG, KO) have individually significant negative loadings at the 5% level. This is consistent with the allocation of zero weight to the small-cap ETF (IWM).

### 4.3 Value exposure

The sleeve's value loading is close to zero (0.010; 95% confidence interval −0.08 to 0.10). This neutrality results from offsetting positions: AAPL (−0.54) and MSFT (−0.36) load on growth, while JPM (0.84), CAT (0.56) and KO (0.21) load on value. The rejected Minimum-Variance sleeve carries a significant positive value loading (0.11; t = 2.57).

### 4.4 Alpha and its sensitivity to the model

For the growth sleeve, alpha is 0.65% per month under the market-only model and 0.57% under the three-factor model, a reduction of about 0.08 percentage points per month. The reduction is attributable to the higher estimated market loading (about 0.05 percentage points) and to the interaction of the negative size loading with the negative SMB premium realised in the sample (about 0.03 percentage points). The sign and the statistical significance of alpha are unchanged. A high adjusted R² (0.84) coexists with a significant alpha, which is consistent with the point in Lecture 7 that a high R² does not rule out positive alpha. For the individual holdings, alpha under the three-factor model ranges from 0.19% (KO) to 1.07% (MSFT) per month, and it is significant at the 5% level only for the sleeve and for MSFT (two of eleven subjects).

### 4.5 Attribution of the sample mean excess return

Over the estimation window the sleeve's mean excess return was 15.77% per year, using simple monthly means multiplied by twelve. Applying the three-factor loadings to the mean factor premia of the same window gives the decomposition in Table 3.

**Table 3. Attribution of the growth sleeve's mean excess return, 2015 to 2022 (per year, arithmetic)**

| Component | Contribution | Share of total |
|---|---|---|
| Market | 8.63% | 54.7% |
| Size | 0.32% | 2.0% |
| Value | −0.01% | −0.1% |
| Alpha | 6.83% | 43.3% |
| **Total mean excess return** | **15.77%** | **100.0%** |

Market exposure accounts for a little over half of the sleeve's historical excess return. The size tilt contributed little because the SMB premium was slightly negative in the sample, and the value tilt contributed nothing. The remaining 43% is the in-sample intercept, whose interpretation is constrained as set out in Section 7.

## 5. Assessment of the Eta and Theta positions

**Eta** proposes investing the balance in the portfolio with the strongest historical risk-adjusted performance. The factor results show that the sleeve's strong historical return is partly a market-exposure effect and partly an in-sample intercept. Selection on historical performance mechanically favours securities with large positive in-sample alphas, which is the source of the selection bias discussed in Section 7. The Initial Decision Record limits this effect by shrinking security-level mean returns towards the VTI mean (weights of 25% and 75%) and by imposing 15% security and 30% sector limits. Eta's criterion is therefore informative as an input but is not sufficient as a decision rule.

**Theta** argues that factor exposures and persistent abnormal returns should determine the growth allocation. The exposure part of this thesis is supported descriptively: the size loading is large, precisely estimated and robust to the choice of standard error. The persistence part is not supported by this evidence. The analysis uses a single in-sample window and cannot test persistence. Alpha estimates are imprecise (the 95% interval for the sleeve's monthly alpha spans 0.22% to 0.92%), they differ widely across securities, and only two of eleven subjects are significant at the 5% level. Applying a Bonferroni threshold of 0.05/11 = 0.0045, only the sleeve (p = 0.0019) remains significant, and the sleeve is a weighted combination of securities selected on the same sample.

**Conclusion.** The factor evidence is best used to explain and monitor the sleeve's risk. It does not justify allocating on estimated alpha. The choice between the recommended and rejected policies rests on the utility trade-off and risk-aversion threshold documented in the Initial Decision Record, not on factor-based alpha.

## 6. Implications for expected returns and for the investment decision

**Expected-return inputs.** The Initial Decision Record forecasts an annual arithmetic return of 12.05% for the recommended sleeve. As an illustrative cross-check based on the Lecture 7 pricing equation E[R<sub>i</sub>] = β<sub>M</sub>λ<sub>M</sub> + β<sub>SMB</sub>λ<sub>SMB</sub> + β<sub>HML</sub>λ<sub>HML</sub> (alpha set to zero), the estimated loadings were combined with long-run factor premia computed only from data available at the cutoff (July 1926 to December 2022): Mkt-RF 8.03%, SMB 2.22% and HML 4.40% per year. The factor-implied expected excess return is 0.867 × 8.03% − 0.426 × 2.22% + 0.010 × 4.40% = 6.06% per year. Adding the December 2022 risk-free rate of 3.96% per year (0.33% per month in the French series) gives an arithmetic expectation of about 10.0%. Subtracting a volatility adjustment of about 1.1 percentage points (σ²/2 with σ = 14.98%, from the Initial Decision Record) gives about 8.9% as a geometric rate. Using the 2015 to 2022 sample premia instead would give a higher figure (8.95% excess). The 12.05% forecast lies above the long-run factor-implied value, which supports the use of shrinkage. Both values exceed the required growth return of about 4.66% per year (Initial Decision Record), but this margin is a forecast, not a guarantee. Historical premia are estimated with substantial error and are not used in the policy.

**Risk and the 15% concern.** With a market loading of 0.87, a 30% fall in the market factor corresponds, to a first-order approximation, to a decline of about 26% in the sleeve (0.867 × 30%), before size, value and idiosyncratic effects. The stress test in the Initial Decision Record applies a uniform 30% decline to the sleeve, which is more severe than this beta-implied response. Betas can rise in market stress, so the comparison indicates conservatism only on the basis of average relationships. Because market exposure dominates the sleeve's risk, review of the trustees' loss threshold should be anchored on market drawdowns.

**Choice between policies.** The recommended sleeve has a higher market loading (0.87 against 0.75) and a higher estimated alpha (0.57% against 0.28%, the latter not significant at the 5% level). Part of its higher expected return therefore comes from greater market risk and part from in-sample alpha that cannot be assumed to persist. The factor evidence does not contradict the recommendation, but it does not independently establish its superiority.

## 7. Limitations and statistical caveats

1. **In-sample selection.** Portfolio weights were optimised on the same 2015 to 2022 sample, and the universe of securities was identified retrospectively in 2026. A positive in-sample alpha is therefore partly mechanical.
2. **Multiple testing.** Eleven subjects were each tested under two models. At the 5% level roughly one rejection in twenty is expected by chance among independent tests. The sleeve and its constituents are not independent, so the Bonferroni adjustment in Section 5 is a conservative guide only.
3. **Return construction.** The estimation series uses constant weights; the evaluation series uses drifting buy-and-hold weights.
4. **Model specification.** Only market, size and value factors are included. Profitability, investment and momentum factors are not. The three-factor model is covered by Lecture 7. Its Carhart four-factor extension (momentum) and five-factor extension were not estimated, and they could be added as robustness checks if the momentum or five-factor series are retrieved from the French Data Library.
5. **Data vintage.** Yahoo and French series were retrieved in 2026 and may include revisions made after December 2022.
6. **Residual diagnostics.** For the three-factor models, there is no evidence of serial correlation (Durbin-Watson 1.68 to 2.39; all Ljung-Box p-values above 0.05) or multicollinearity (maximum variance inflation factor 1.08). Jarque-Bera rejects normality at the 1% level for AAPL, MSFT and PFE, so t-based intervals for those securities are approximations. Breusch-Pagan indicates heteroskedasticity at the 5% level for JPM, PG and KO, which is why Newey-West results are reported alongside classical ones.
7. **Sample size.** With 96 observations, estimates of alpha are imprecise. The analysis makes no statement about the 2023 to 2025 period or about the attainment of the 2030 goal. Persistence can be examined only through the frozen evaluation with pre-declared criteria.

## 8. Reproducibility and source record

| Item | Record |
|---|---|
| Factor file | `F-F_Research_Data_Factors.csv`, archived unmodified inside `F-F_Research_Data_Factors_CSV.zip` |
| SHA-256, ZIP archive | `593f4fbef03181bc0b22ff6292f217689dd1fb79355049ca905d95b262040a66` |
| SHA-256, CSV file | `d7d7fe37b150b5b15c9c069b3ba101dfe1af568c6d7b5db6e73cd0a6c0c9e5e5` |
| Source vintage | File header: created using the 202608 CRSP database; copyright 2026 Eugene F. Fama and Kenneth R. French |
| Retrieval | 19 October 2026, 21:10 UTC, by `factor_analysis/french_data.py` (`fetch`); HTTP status 200; the `Last-Modified` header was not recorded |
| Estimation code | `factor_analysis/models.py`, `factor_analysis/ols.py` |
| Result tables | `factor_coefficients.csv` (Tables 1 and 2, A1), `factor_model_comparison.csv` (nested F-tests, BIC), `factor_diagnostics.csv` (Section 7), `factor_exposures.png` (figure) |
| Verification | Independent least-squares recomputation of the growth sleeve coefficients; full pipeline rerun reproduces all coefficients with zero difference |

## Appendix

**Table A1. Three-factor estimates for the remaining holdings and the benchmark**

| Subject | Alpha per month, CAPM → FF3 | Alpha t (FF3) | β Mkt-RF | s SMB (t) | h HML (t) | Adj. R², CAPM → FF3 | p-value, SMB and HML jointly zero |
|---|---|---|---|---|---|---|---|
| AAPL | 1.01% → 0.92% | 1.52 | 1.265 | −0.290 (−1.22) | −0.541 (−3.48) | 0.463 → 0.523 | 0.0016 |
| JPM | 0.28% → 0.35% | 0.92 | 1.108 | 0.095 (0.63) | 0.843 (8.53) | 0.551 → 0.745 | < 0.0001 |
| JNJ | 0.37% → 0.29% | 0.77 | 0.587 | −0.433 (−2.91) | 0.037 (0.39) | 0.300 → 0.346 | 0.0166 |
| PFE | 0.47% → 0.37% | 0.61 | 0.746 | −0.511 (−2.14) | −0.062 (−0.40) | 0.219 → 0.241 | 0.0966 |
| KO | 0.31% → 0.19% | 0.53 | 0.614 | −0.750 (−5.31) | 0.208 (2.26) | 0.266 → 0.447 | < 0.0001 |
| CAT | 0.59% → 0.64% | 0.98 | 1.107 | 0.089 (0.34) | 0.556 (3.31) | 0.400 → 0.453 | 0.0052 |
| VTI (benchmark) | −0.01% → −0.02% | −0.79 | 0.991 | −0.019 (−2.35) | 0.014 (2.67) | 0.998 → 0.998 | 0.0030 |
