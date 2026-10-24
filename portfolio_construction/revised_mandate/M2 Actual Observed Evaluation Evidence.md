# M2 — Observed 2023–2025 growth evaluation (CONDITIONAL SOURCE EVIDENCE)

**Status, 24 October 2026:** Real Yahoo responses were downloaded **after** a documented 22 October course-submission *email*, but LMS/instructor acceptance and independently SHA-verified bytes inside the original emailed ZIP are **not** established. The JNJ/Kenvue independent numeric audit is complete; a named human corporate-action reviewer is not. Hence these are provisional, source-backed **observed prices**, not a verified final course submission result.

## Reproducible source

- [GitHub Actions acquisition and evaluation run #40093744756](https://github.com/lucasnguynn/BFIN-Assignment/actions/runs/40093744756) — workflow **SUCCESS**.
- [Original raw data + processed daily prices + provisional evaluation artifact #12560420593](https://github.com/lucasnguynn/BFIN-Assignment/actions/runs/40093744756/artifacts/12560420593) — nine yfinance original DataFrame responses, **752 shared US trading dates**, 2023-01-03 to 2025-12-31, version **yfinance 1.7.0**, retrieved **2026-10-24T19:24:06+07:00**.
- Original Yahoo ZIP SHA256 `10d080c004564a35c9fd76f2f9584e92068ea558d71b730b60992da8b7c5d334`; processed prices CSV SHA256 `df18559454a41b36eb99af0fce1d892fdb822e4378e0fd19802e9232eb13e23d`. Both hashes, all nine original response hashes, and ZIP CRC were independently reverified from the downloaded GitHub artifact.
- Original frozen full-precision policy weights have repo SHA256 `a15469f1478370e2d9399cae8ab7aae215545fe2e040d02435bdc3ea7d10672d`. This differs from the assistant's locally *prepared* submission ZIP because of metadata, despite equal financial weights. The documentary 22 October email source record associated the submitted group ZIP with the *repo* version by size and ZIP CRC; this does not cryptographically validate original emailed member bytes.

## Measured growth-only comparison, provisional

| Statistic | Frozen Sample MV | Frozen VTI |
|---|---:|---:|
| After-initial-10bp CAGR | **17.6864%** | **22.4469%** |
| Annualized monthly-volatility estimate | 11.8036% | 12.6028% |
| Maximum monthly NAV drawdown | −8.7010% | −9.1098% |
| Growth-sleeve terminal value | USD **10,151,162.71** | USD **11,430,109.15** |

- Compounded CAGR shortfall: **−4.7605 percentage points**.
- Annualized *arithmetic* active return: **−4.1069%**.
- Tracking error, annualized from monthly returns: **6.9062%**.
- The 36 monthly NAV/return observations, all raw vendor responses and exact source provenance are archived in the linked artifact. No new weights were selected from these realized observations, and the result is **not a measured total-foundation return** because case bonds have no observed future price series.

## Independent JNJ/Kenvue split-off numerical robustness

Contemporaneous JNJ issuer releases describe the 2023 KVUE split-off as an **optional voluntary tender/exchange**; the original frozen rule is **hold JNJ, elect no tender, receive no KVUE shares**. In the saved Yahoo JNJ original response:

- No `Stock Splits` entries occur in 2023, including the tender window.
- `Adj Close / Close` remains nearly constant from August 18 through August 24 (maximum relative drift ≈ **1.80 × 10⁻⁷**), before the ordinary **USD 1.19 cash dividend** on August 25.
- Replacing JNJ's adjusted-close equity-return index with a separate no-tender shareholder index built only from raw JNJ **Close + ordinary Dividends**, reinvested at the respective ex-date closes, changes 2025 frozen-sleeve terminal value by just **−USD 188.33** (from USD 10,151,162.71 to USD 10,150,974.38), and CAGR by about **−0.00073 percentage points**. Seven other invested holdings are kept untouched.

These diagnostics strongly support that the Yahoo proxy did **not** insert a KVUE share windfall into the 2023 frozen JNJ position. They are a transparent alternative-investment-convention sensitivity, **not** a falsely signed human review or a guarantee of perfect vendor adjustments. The original strict evaluator still requires a dated action record and must not be silently bypassed.

## Revised mandate integration and final academic status

M1 Principal Matching and M1 Coupon Funding are analyzed against Original in PR #6, with Sample MV / Single Index MV / Minimum Variance, A=3/A=6, full-precision allocations, fixed-weight A*/λ* thresholds, 36-cell inflation/buffer sensitivity, exact bond/equity combined stress, 112-cell independent M1 cashflow audit, M3 factor handoff and mandate-versus-funding-versus-method decomposition. The original 2015–2022 data-only portfolio choice has not been altered.

**Technical work is substantially complete.** Remaining acceptance gates are documentary proof of institutional receipt/attachment bytes and actual human reviews/funding selection and M3 approval. This memo does not claim those gates passed. Detailed downloadable technical evidence remains preserved in the GitHub Actions artifact. 

**Sources:** [JNJ voluntary exchange announcement](https://www.jnj.com/media-center/press-releases/johnson-johnson-launches-exchange-offer-for-separation-of-kenvue-inc) and [final results](https://www.jnj.com/media-center/press-releases/johnson-johnson-announces-final-results-of-exchange-offer-and-finalizes-separation-of-kenvue-inc); original group BFIN case, official revised mandate, M1 published outputs; archived Yahoo raw responses and PR #6.

**AI disclosure:** AI-assisted independent calculations, code and data quality assurance, numerical corporate-action analysis and English drafting. Neither university acceptance nor human approvals were invented.
