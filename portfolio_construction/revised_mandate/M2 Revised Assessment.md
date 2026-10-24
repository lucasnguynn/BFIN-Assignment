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


## Post-freeze observed 2023–2025 evaluation update (conditional evidence)

After the documented 22 October 2026 course submission email, GitHub Actions used yfinance 1.7.0 to archive 9 real original 2023–2025 Yahoo daily response frames (752 trading dates) and independently produced the frozen Sample MV versus VTI 36-month comparison. **Observed Sample MV after-fee CAGR is 17.6864% versus VTI 22.4469%**, a **−4.7605 pp CAGR difference**, with 11.8036% versus 12.6028% annualized monthly volatility, −8.7010% versus −9.1098% max monthly drawdown, 6.9062% tracking error, and −4.1069% annualized arithmetic active return. The observed growth-only terminal values are USD 10,151,162.71 and 11,430,109.15, respectively. These values constitute observed price-based **provisional** analysis, not verified institutional acceptance or whole-fund performance.

A separate JNJ no-tender holder-return sensitivity reconstructs its ordinary cash-dividend reinvestment from original Close and Dividends, **without any KVUE shares**; the full portfolio's 2025 terminal value differs from the vendor adjusted-close proxy by only −USD 188.33. Archived original JNJ did not record a 2023 stock split and shows nearly stable adjusted-to-unadjusted ratio across the August voluntary exchange. This supports, but does not replace, a signed corporate-action review.

Primary implementation/source: `portfolio_construction/revised_mandate/M2 Actual Observed Evaluation Evidence.md` and [GitHub Actions raw observed artifact](https://github.com/lucasnguynn/BFIN-Assignment/actions/runs/40093744756/artifacts/12560420593). University emailed archive members and LMS acceptance remain not independently cryptographically authenticated; reviewer and funding approval are outside the assistant's authority. Original policy selection remains entirely based on 2015–2022 data.
