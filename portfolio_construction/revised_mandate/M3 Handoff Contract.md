# M2 to M3 revised mandate — handoff contract

**Status: scenario research only; no group funding approval, LMS receipt or actual 2023–2025 results.**

## Build

From the repository root run:

    python portfolio_construction/revised_mandate/m3_handoff.py

The builder runs only saved 2015–2022 original estimation returns and Member 1 committed revised funding outputs, with no live downloads. It writes to portfolio_construction/revised_mandate/m3_handoff/.

- M3 Static Returns Long.csv — 1,440 rows; columns scenario_id, month, monthly_simple_return_decimal. Exactly 15 unique scenarios times 96 months (2015-01 to 2022-12).
- M3 Scenario Registry.csv — policy/scenario IDs and pre-2023 static-proxy warning.
- M3 Exact Portfolio Weights.csv — full-precision 12-asset weights and USD allocations; no rounded input weights.
- M3 Handoff Manifest.json — source and output SHA-256, decision cutoff and explicit incomplete-evidence flags.
- m2_calculations/ — M2 funding, risk, optimization and static-exposure calculation evidence.

The 15 combinations comprise 3 funding cases (Original, Revised Principal, Revised Coupon) and 5 equity portfolios each (Frozen Sample MV, Reoptimized Sample MV A3, Single-Index MV A3, constrained Minimum Variance and Sample MV A6).

## Member 3 reviewer protocol

1. Join the handoff month to original French factor month with n=96 and decimal return units; subtract French RF exactly once.
2. Verify ORIGINAL_FROZEN__FROZEN_SAMPLE_MV against the existing M3 growth proxy. Funding changes alone cannot alter its normalized portfolio returns: all three frozen-weight series must match within 1e-12.
3. Reject any factor panel containing a post-2022 policy input, mismatched month, duplicate key or return in percent units.
4. Refit FF3/CAPM for a genuinely changed normalized weight vector; explain why unchanged frozen weights imply unchanged factor exposure.
5. Treat ALL 2015–2022 series as static-estimation proxies, not observed 2023–2025 buy-and-hold results. These files contain no new factor estimates.
6. Post independent, dated human review on draft PR #6, including findings and resolutions.

## Freeze consistency check

Run:

    python portfolio_construction/post_freeze_evaluation/reconcile_submission.py --candidate-zip "/local/Kappa 22 Oct Submission.zip" --repository-weights "portfolio_construction/evidence/decision_weights_confirmed.csv"

This tool only compares local archive bytes and economic policy identity; it never claims the LMS accepted that archive. The candidate 22 October ZIP prepared by M2 has economic weights identical to GitHub but metadata-different bytes and a distinct SHA-256. Only actual LMS uploaded files and a real receipt establish the frozen policy. The post-freeze evaluator must use the exact submitted Code and Raw Data root if the LMS received that archive, never a hash-different GitHub copy.

## Remaining sign-off gates

M1/group selected funding; real 22-Oct receipt; dated post-freeze daily Yahoo source archive, JNJ/Kenvue action check and realized 36-month VTI evaluation; M3 peer review; final English memo/slide integration.
