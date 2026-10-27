# Growth-only 2023-2025 evaluation: execute after the real policy freeze

**Do not run on observed 2023-2025 prices before the actual 22 October 2026 initial submission.** Observed 2023-2025 Yahoo response data and 36 monthly results have now been archived under Portfolio Final/Sources. They were collected after the documented 22 October course-submission email, but the institution's acceptance and exact emailed ZIP-member fingerprints are not independently verified. They remain a conditional post-freeze check, never an input to the 2022 decision.

## Required records after the course upload

1. Preserve the **actual submitted PDF** and genuine dated course submission reference. Create `receipt.json` from `templates/freeze_receipt_BLANK.json`. Supply `submitted_at_hcm` as an offset-aware ISO timestamp (HCMC +07:00) not later than **22 October 2026, 16:00**; do not invent or backdate. The PDF SHA-256 must identify the submitted bytes, and `frozen_weights_sha256` must match the genuine pre-2023 policy weights (`evidence/decision_weights_confirmed.csv`).
2. Obtain 2023-01-03 through 2025-12-31 **daily** adjusted closes through the designated yfinance retrieval on a network-enabled machine *after* submission. Keep raw, untransformed responses in a ZIP and record SHA-256 along with package version and a real `retrieved_at_hcm` timestamp in `evaluation_source_record.json`. Save a distinct processed daily adjusted-price CSV with `date`, AAPL, MSFT, JPM, JNJ, PFE, PG, KO, CAT, VTI. Zero-weight candidates need not be included. The 3 January 2023 close must be present.
3. During evaluation, independently verify JNJ/Kenvue corporate-action accounting, including whether the retrospectively adjusted price series represents the original **no-voluntary-exchange** rule. This review names a subsequently observed event only for post-freeze QA and must not be read into the case-date decision. Fill `jnj_action_review.json` only after examining real source documents; include reviewer, date, source and treatment.
4. Run from the package root:

```
python post_freeze_evaluation/evaluate.py --prices /path/to/daily_adjusted_prices.csv \
  --receipt /path/to/receipt.json \
  --source-record /path/to/evaluation_source_record.json \
  --corporate-actions /path/to/jnj_action_review.json \
  --out /path/to/growth_outputs
```

5. Compare frozen portfolio against frozen VTI, report monthly/net returns, CAGR, volatility, drawdown, annualized active arithmetic return and tracking error. Critically interpret uncertainty and vendor adjustments. **Do not** represent three years of growth results as proof the 2030 goal was achieved.

## Separate fictional-bond scenario monitor

```
python post_freeze_evaluation/modeled_fund_monitor.py \
  --growth-monthly /path/to/growth_outputs/growth_2023_2025_monthly.csv \
  --out /path/to/modeled_fund_returns.csv
```

The illustrative Beta/Delta mark-to-model uses yields implied by 2022 prices and discounts contractual payments with **exact coupon-anniversary year fractions**. It matches initial quoted prices exactly and strips the 2024 withdrawal from modeled investment performance; this is NOT observed 2023-2025 bond market performance. An independently documented monthly rate-shift scenario is optional.

The gate checks internal consistency of human-provided receipt/source documents; it cannot independently authenticate the university platform or whether the user has genuinely completed the JNJ check. **Never create fake signoffs or source dates.**
