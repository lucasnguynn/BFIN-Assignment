# Portfolio review

Kappa Foundation | Working material for the final group assignment | 25 October 2026

## Our recommendation

We would keep the stock weights selected on 31 December 2022. The revised trustee payments make the bond funding decision more important, but we have not found enough improvement from optimizing the stock weights again to justify replacing the frozen portfolio. The group has selected principal matching as its final revised funding recommendation. Coupon funding remains a feasible alternative with more initial growth capital, but it leaves almost no cash just after the 2025 payment and a smaller reserve at the end of 2030.

The revised schedule moves USD 1.2 million of the learning-centre payment from December 2027 to December 2025. Total promised payments stay at USD 6 million.

| Plan | Cost of bonds | Net equity after 10 bp fee | Cash in 2030 | Equity CAGR needed |
|---|---:|---:|---:|---:|
| Original | USD 5,764,524 | USD 6,229,247 | USD 630,000 | 4.66% |
| Revised principal | USD 5,784,228 | USD 6,209,562 | USD 564,000 | 4.80% |
| Revised coupon | USD 5,429,776 | USD 6,563,660 | USD 168,000 | 4.63% |

These growth hurdles use a 2.3% annual inflation assumption and the 2030 real purchasing-power target of USD 8 million in 2022 dollars. They are not forecasts of future investment performance.

## Why retain the stocks?

The candidate list contains ten common stocks across six sectors plus two US equity ETFs. The selected allocation actually buys eight individual stocks: AAPL, MSFT, JPM, JNJ, PFE, PG, KO and CAT. It does not hold either ETF. That is an important concentration risk even though the candidate list is broader.

We used 96 common monthly returns from 2015 to 2022, with expected returns based on 25% own-stock history and 75% of a VTI market prior. The model limits any direct stock to 15%, any direct-stock sector to 30%, each ETF to 30% and the combined ETF allocation to 40%. We compared Sample Mean-Variance with a Single-Index version and a constrained Minimum Variance alternative. We also tested foundation risk aversion at A = 3 and A = 6.

Under revised principal funding, reoptimization only increases the modeled equity utility from 0.053328705 to 0.053328718 at A = 3. Under revised coupon funding it rises from 0.055826785 to 0.055830594. We judge the gains too small to make a confident case for changing the frozen weights. Against the fixed Minimum Variance alternative, the preference would change at about A = 8.94 under principal funding or A = 8.46 under coupon funding. These are comparisons between fixed stock portfolios, not cutoffs for a fully reoptimized fund.

With a 25% instantaneous equity fall and a parallel 100 basis point bond-rate increase, the starting fund would lose roughly 14.42% under revised principal funding and 15.08% under revised coupon funding. These instantaneous shocks are not the 12-month withdrawal-adjusted measures behind our proposed 12% warning and 15% review levels. The trustees have not approved those thresholds.

## What we learned from the actual market test

The frozen equity position was evaluated from the 3 January 2023 closing-price proxy to the final trading date of 2025, without discretionary rebalancing. Both the selected shares and VTI were charged the same 10 basis point starting cost. The archived Yahoo source contains nine original responses, 752 shared trading dates and 36 monthly observations.

| Observed growth measure | Selected stocks | VTI |
|---|---:|---:|
| CAGR after entry fee | 17.69% | 22.45% |
| Annualized volatility | 11.80% | 12.60% |
| Largest monthly NAV drawdown | -8.70% | -9.11% |
| End-2025 growth value | USD 10.15m | USD 11.43m |

The annualized arithmetic active return is -4.11%, with 6.91% tracking error. The chosen stocks delivered a positive return but did not beat the simpler benchmark. We cannot use this future period to revise what the team knew in December 2022.

The JNJ/Kenvue separation was an optional exchange. Our frozen policy does not elect the exchange or add any KVUE shares. Using JNJ closing prices and ordinary cash dividends instead of adjusted prices changes the portfolio's final value by only about USD 188. This supports our treatment, but the final check of dividend timing and action mechanics remains a human responsibility.

## What the factor regressions add

The group's factor analysis used the same 96 historical months. For the growth portfolio, adjusted R-squared rises from about 0.785 with CAPM to 0.844 with the Fama-French three-factor model. Market beta is around 0.867 and the SMB loading is around -0.426, consistent with a large-company tilt. The sample's positive monthly alpha is not evidence of a reliable future abnormal return. Microsoft's exposure to market risk is stronger than Procter & Gamble's; PG's historical factor alpha is not statistically distinguishable from zero. Keeping the same normalized stock weights under different bond funding leaves these historical stock-factor estimates unchanged.

## Checks, files and open decisions

The supporting Python runs from saved data without internet and covers three funding plans, five stock portfolios per plan, a 36-case inflation and cash-buffer comparison, the bond cash-flow ledger and the 2023 to 2025 observed returns. The original selection is kept separate from the later evaluation.

For the group handoff, the **Portfolio Final** folder contains a PDF report, an editable Word copy, a nine-sheet workbook and saved Yahoo data. **Portfolio Files.zip** contains the same material. The historical model, original 2022 decision, bond analysis, factor data and Python scripts stay in their existing repository folders so the group does not have to manage duplicate copies.

The group has selected principal matching as its final revised funding recommendation and has approved retaining the original growth-portfolio weights. The remaining work is to verify the original-submission evidence and integrate the portfolio analysis into the final committee memo and presentation.

The 22 October course-submission email is documented, but we cannot independently confirm the university's acceptance or hash every member of the emailed ZIP. The observed figures therefore remain conditional on original-submission verification. The course's complete final archive is a **group** responsibility; this portfolio handoff should not be described as that archive.

Sources: official BFIN group assignment and 23 October revised mandate; Member 1 revised bond outputs; original and observed Yahoo data; Kenneth French factors retrieved by the factor workstream; JNJ issuer and SEC documentation. Reproduction code is in this repository and the dated Yahoo evidence is preserved in [the acquisition artifact](https://github.com/lucasnguynn/BFIN-Assignment/actions/runs/40093744756/artifacts/12560420593).

Material AI assistance was used for coding, source checks and editing. The source data and calculation steps remain available so each contributor can review and explain the work. No student or lecturer approval has been assumed.
