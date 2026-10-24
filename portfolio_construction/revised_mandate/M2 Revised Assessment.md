# Member 2 Revised Mandate — Equity Assessment

**Status: technical draft for group review, 24 October 2026.** No approval, LMS receipt or actual 2023–2025 evaluation is claimed. All policy comparisons are made as of 31 December 2022, with information restricted to 2015–2022, original bond quotes and unchanged case assumptions.

## Comparing the original and revised commitments

The revised trustees' schedule retains the USD 2.4 million payment on 31 December 2024, moves USD 1.2 million into 31 December 2025 and reduces the 2027 payment from USD 3.6 million to USD 2.4 million. Total commitments remain USD 6 million. The Member 1 funding outputs contain two alternatives:

| Measure | Original | Revised principal | Revised coupon |
|---|---:|---:|---:|
| Bond cost (USD) | 5,764,524 | 5,784,228 | 5,429,776.18 |
| Net growth equity (USD) | 6,229,246.75 | 6,209,562.44 | 6,563,660.16 |
| Retained cash in 2030 (USD) | 630,000 | 564,000 | 168,000 |
| Equity CAGR required to meet 2030 goal | 4.6577% | 4.7951% | 4.6309% |

The coupon alternative makes USD 354,097.72 more available for equities than principal matching, but retains USD 396,000 less cash. When the two equity sleeves earn the same hypothetical eight-year geometric return, their 2030 wealth projections break even at approximately **1.408% per annum**. This conditional projection is not an expected-return estimate.

## Portfolio construction and robustness

For the mandate-only counterfactual, the original Sample Mean-Variance weights remain fixed. Separate reoptimization trials retain foundation risk aversion A=3, the 25% stock-specific/75% VTI historical-return shrinkage assumption, sample or single-index covariance and original stock, sector, ETF and long-only caps; A=6 is a sensitivity.

Under revised principal matching, Sample MV equity utility is approximately **0.053328705** with frozen weights, versus **0.053328718** after reoptimization. Under the Member 1 coupon alternative, the corresponding figures are **0.055826785** and **0.055830594**. These conditional equity-utility contributions are not full-foundation utility estimates: bond–equity covariance, reinvestment opportunities and future withdrawal-adjusted wealth are not jointly optimized. The Sample MV versus constrained Minimum Variance fixed-weight A-switch thresholds are roughly **8.94** and **8.46**, respectively. They do not describe reoptimized switching points.

## Risk and governance

Coupon funding leaves essentially no cash immediately following the 2025 payment, whereas principal matching leaves approximately USD 396,000. Fractional Gamma holdings are permitted by the case; cash-flow slack and the more equity-heavy exposure are the material concerns. Combining Member 1 exact bond repricing under +100 bp and a simultaneous instantaneous 25% equity-value decline implies an initial-fund loss of approximately **14.42%** under principal matching versus **15.08%** under coupon funding. This is a hypothetical instantaneous stress, **not** the rolling 12-month, withdrawal-adjusted loss that governs the 12% early-warning and 15% mandatory-review triggers. Neither risk threshold is a guaranteed cap.

## Provisional recommendation and open gates

Subject to Member 1's selected funding policy and independent peer review, **retain the frozen Sample MV equity weights** because in these scenarios reoptimization brings little incremental modeled utility. Document mandate-only changes separately from optional changes in method or weights, without altering the genuine 22 October original submission.

The repository does not establish that an LMS receipt has been verified. Existing evaluation code and synthetic tests do not constitute realized 2023–2025 results. The final evaluation requires genuine freeze provenance, post-submission original daily Yahoo responses and hashes, verified JNJ/Kenvue treatment, and 36 monthly observations versus the frozen VTI comparator, including CAGR, volatility, drawdown, active returns and tracking error.

**Source trace:** Original course case; official 23 October 2026 revised mandate; original frozen policy; committed Member 1 revised funding holdings, summary, cash ledgers and rate shocks; 2015–2022 monthly returns; Member 2 revised integration code and generated outputs. Figures above are rounded for presentation, not for calculations.
