# Cross-workstream review

**Current status, 27 October 2026:** The revised mandate has been checked in `qa_report.json` (48 PASS, 1 WARN, 0 FAIL). Principal Matching has been selected and the frozen stock weights retained. The one remaining warning concerns the historical Candidate B display label, not a revised payment shortfall. The original note below is kept as a dated audit trail; its 20 October test counts and funding-choice status are superseded. The revised whole-fund monitor is separate from the frozen original version, and the group memo and nine-slide deck are stored in Final Submission. Independent human sign-offs and university acceptance still require actual evidence.

---

# Cross-workstream QA review (19 October 2026)

**Gate conclusion (updated 20 October 2026):** all checks PASS or WARN and the USD 12,000,000.00 reconciliation is exact (`Decimal` arithmetic). The project is **GO** (36 PASS, 2 WARN, 0 FAIL, 0 BLOCKED; `qa_report.json` is authoritative). The Kenneth French factor data were retrieved on 19 October 2026 and the factor regressions have been run. The two WARN items are listed below.

## Confirmed (PASS)
- **Total capital:** 2,214,672.00 (Beta) + 3,549,852.00 (Delta) + 6,229,246.75 (equities) + 6,229.25 (10 bp fee) + 0 (cash) = **12,000,000.00**; difference 0.00.
- **Portfolio weights** (`decision_weights_confirmed.csv`): 12 rows; sum = 1.000000000000001 (float residue of about 1e-15; an exact `== 1.0` test would be wrong); long-only; maximum 15.0000% (AAPL, MSFT and PG sit exactly at the cap); Technology = 30.0000% (exactly at the sector cap).
- **Bond funding:** YTM, Macaulay/modified duration, convexity and bootstrapped spot curve (s3 = 3.9000%, s5 = 3.7987%) recomputed independently; PV of Beta + Delta = 5,764,524.00; the 2024 and 2027 obligations are covered by bond *principal* alone; residual coupon cash at the end of the horizon = 630,000.
- **Portfolio reproducibility:** `rebuild.py` passes offline; 15 CSV outputs regenerate with relative error < 1e-12; 52/52 unit tests pass; 11/11 figures in the Initial Decision Record (12.05%, 14.98%, 0.053469, A* = 8.91, lambda* = 0.0842, 17.27%, 16.31%, USD 9.596m, 4.66%, ...) match the code.

## Items to resolve
| # | Component | Severity | Issue | Recommendation |
|---|---|---|---|---|
| 1 | Portfolio construction | Medium | Hand-off schema: the files delivered are `decision_weights_confirmed.csv` (column `weight_of_growth_sleeve`, no `case_date`) and `growth_static_exposure_returns.csv`, not `frozen_weights.csv` / `growth_returns.csv` as specified in the framework (WS7, section 7.4). The growth series uses **static weights**, not a drifting buy-and-hold path. | Rename or add columns, or state the convention explicitly in the memo. The factor analysis uses the static exposure series for 2015-22 and documents this in the README. |
| 2 | Portfolio construction | Low | `portfolio_construction/requirements.txt` declares `pandas<3`, although pandas 3.0.2 rebuilds identically; matplotlib/openpyxl are missing; version ranges are used instead of exact pins. | Use the pinned root `requirements.txt`. |
| 3 | Portfolio construction | Low | The rebuild pins the SHA-256 of the funding workbook (`ff490c...`); the original workbook has `a3ef7c...`. Every cell and formula in all 3 sheets was compared and is **identical**; only byte-level metadata differs. | Settle on a single workbook version and update the pinned hash. |
| 4 | Portfolio construction | Low (self-disclosed) | Original SEC filing bytes are not archived; JPM is not independently re-verified. | Keep the stated limitation in the memo; run `archive_sec_filings.py` when online. |
| 5 | Bond funding | Resolved in checked workbooks | Candidate B's 2027 coverage is USD 3,600,800, including Gamma principal and the three annual coupons retained at 0%. In the original and revised workbooks checked, `BOND & FUNDING ANALYSIS!H40` and `C49` both show USD 3,600,800. | No numerical correction is needed for these cells. Candidate B remains the original-mandate alternative; the revised coupon-funding alternative is analyzed separately. |
| 6 | Bond funding | Low | The framework (section 4.3) states a hurdle of 4.64% (base USD 6,235,476); the Decision Record uses 4.66% (base USD 6,229,246.75 after the fee). Both are correct under their own conventions. | Use 4.66% in the memo (matches the code) and state the base. |
| 7 | Whole group | Info | Four constraints bind simultaneously (AAPL, MSFT, PG at 15% and Technology at 30%); the mean-variance optimum is highly input-sensitive (disclosed in the record). | Carry into the risk and threshold section of the memo. |
| 8 | Factor analysis | Resolved | French factor data retrieved (19 October 2026, SHA-256 recorded in `french_source_record.json`); the three-factor model is part of the Lecture 7 model menu. | None. The Carhart and five-factor models are optional robustness checks. |

---

# Update for the revised mandate (27 October 2026)

**Gate conclusion:** `run_pipeline.py` now returns **GO** with 48 PASS, 1 WARN, 0 FAIL, 0 BLOCKED (`qa_report.json` is authoritative). Ten `REVISED.*` gates and `FACTOR.revised_mandate_scenarios` were added (code: `quality_assurance/revised_mandate_checks.py`, `factor_analysis/revised_mandate_factors.py`). The 22 October artefacts were not modified; the three files the pipeline regenerates (`factor_exposures.png` and the two `decision_threshold_*.csv`) were restored to their 22 October bytes because the regenerated copies differ only by floating-point residue of order 1e-15.

## Confirmed (PASS)
- **Schedule:** USD 2.4m (2024) + 1.2m (2025) + 2.4m (2027) = USD 6.0m, the same total as the original.
- **USD 12m reconciliation:** bond cost + net equity + 10 bp fee equals USD 12,000,000.00 (+/-0.01) in the original, principal-matching and coupon-funding scenarios.
- **Liabilities covered, re-derived independently with `Decimal`:** principal matching (Beta 2,400, Gamma 1,200, Delta 2,400 units) leaves USD 564,000 in 2030; coupon funding leaves USD 168,000. No shortfall in any year.
- **Factor evidence unchanged:** the frozen growth series is identical (gap 0.0) in all three funding scenarios and matches `growth_static_exposure_returns.csv` (gap 1.1e-16), so CAPM/FF3 estimates cannot change. The other policies are reported in `revised_mandate_factor_scenarios.csv`.
- **Mandate/method bridge** is additive (mandate-only utility effect -0.000140 under principal matching; funding-method change +0.002498; equity re-optimization +0.0000038).
- **Temporal integrity:** all revised scenarios use 2015-01 to 2022-12 only.

## Items to resolve
| # | Component | Severity | Issue | Recommendation |
|---|---|---|---|---|
| 9 | Hand-off metadata | Medium | `m3_handoff.py` and `m1_integration.py` write constants `M1_funding_selected: false` and `group_funding_selection_confirmed: false`, but the group has since selected principal matching. A reader of the manifests would see an outdated status. | Update the constants (or state in the memo that the manifests pre-date the group's selection). The numbers are unaffected. |
| 10 | Evidence | Medium (self-disclosed) | The hash of each member of the emailed 22 October ZIP and the university's acceptance are not independently verified (README). | Keep the limitation wording in the memo; do not describe the receipt as verified. |
| 11 | Scope of thresholds | Info | A* = 8.94 (principal) and 8.46 (coupon), lambda* = 0.0839 and 0.0887, compare two fixed stock portfolios. They are not re-optimized switching points. | State the scope limit next to the numbers in the memo. |
| 12 | Stress measure | Info | The instantaneous -25% equity / +100 bp shock gives losses of 14.42% (principal) and 15.08% (coupon). It is not the 12-month withdrawal-adjusted measure behind the trustees' 12% / 15% levels. | Label the figure accordingly; coupon funding crosses 15% on this simplified measure and principal matching does not. |
| 13 | Decision log | Medium | `decision_log.csv` is drafted (D01 to D08) but signatures are pending. | Each owner and reviewer signs before 29 Oct 16:00. |

Items 1 to 8 above remain as recorded on 19 to 20 October. Item 5 stays resolved; the WARN `BOND.candidateB_label` is still a presentation fix in the original workbook and is not a calculation error.
