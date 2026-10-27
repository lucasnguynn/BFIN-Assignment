# Slide text: market and factor evidence (2 slides)

## Slide A. What drives the growth sleeve's returns (2015 to 2022, n = 96)
**Title (message):** Mostly market risk, with a large-company tilt; the positive alpha is not evidence of skill

- Market beta 0.87 (95% CI 0.79 to 0.94); three-factor adjusted R-squared 0.844 vs 0.785 for CAPM
- Size loading -0.43 (t = -6.1): large-company tilt. Value loading 0.01: growth and value holdings offset
- FF3 alpha 0.57% per month (t = 3.2): in-sample, ex post stock selection, model-relative. Not used to set weights
- Visual: `factor_analysis/outputs/factor_exposures.png` (exhibit F5) and Table 5.1 (exhibit F1)
- Speaker note: Microsoft's alpha is significant (t = 2.5); Procter & Gamble's is not (t = 0.9) and its beta (0.46) is less than half of Microsoft's (1.06)

## Slide B. Does the revised mandate change the evidence?
**Title (message):** No. The revised schedule changes funding, not the stock returns

- The USD 1.2m payment moves from 2027 to 2025; stock weights and monthly returns are the same
- Frozen growth series identical in all three funding scenarios (gap 0.0): every CAPM and FF3 estimate is unchanged
- Re-optimizing weights moves beta by 0.0004 (principal matching) to 0.006 (coupon funding), far inside the 0.038 standard error
- What did change: bond cost +USD 19,704; net equity -USD 19,684; 2030 cash USD 564,000; required equity CAGR 4.66% to 4.80% (exhibits B1, P2)
- Visual: table from `factor_analysis/outputs/revised_mandate_factor_scenarios.csv` (exhibit F2)
- Speaker note: QA verdict GO, 48 PASS, 1 WARN (presentation label in the original workbook), 0 FAIL
