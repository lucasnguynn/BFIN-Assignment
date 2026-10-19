# Cross-workstream QA review (19 October 2026)

**Gate conclusion:** all financial checks PASS and the USD 12,000,000.00 reconciliation is exact (`Decimal` arithmetic). The project is **NO-GO solely because the Kenneth French factor data have not yet been retrieved** (factor-analysis workstream). There are no FAIL results.

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
| 5 | Bond funding | Low | Candidate B row "Cash at liability date 3,215,000" omits 3 x 128,600 Gamma coupons; the true 0%-reinvestment cash is 3,600,800, so row 49 reads as an under-cover. | Correct the label. The decision (Candidate A) is unaffected. |
| 6 | Bond funding | Low | The framework (section 4.3) states a hurdle of 4.64% (base USD 6,235,476); the Decision Record uses 4.66% (base USD 6,229,246.75 after the fee). Both are correct under their own conventions. | Use 4.66% in the memo (matches the code) and state the base. |
| 7 | Whole group | Info | Four constraints bind simultaneously (AAPL, MSFT, PG at 15% and Technology at 30%); the mean-variance optimum is highly input-sensitive (disclosed in the record). | Carry into the risk and threshold section of the memo. |
| 8 | Factor analysis | **Blocking** | French factor data not retrieved; Lecture 7 model menu not yet confirmed. | See `README.md`, Steps 2-3. |
