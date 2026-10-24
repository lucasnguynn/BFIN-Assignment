# Kappa Foundation — Member 2 Comprehensive Evidence Audit and Remediation Register

**As assessed:** 24 October 2026. **Decision date:** 31 December 2022. **Final deadline:** 29 October 2026 at 16:00 HCMC. **Status:** technical-revision branch; NOT all Member 2 final submission gates have been met.

## 1. Sources, hierarchy and controls

The controlling instructions are the official BFIN WS2026 Group Assignment (four pages), the one-page Revised Mandate released 23 October, the team framework, and BFIN_Phan_Cong_3_Nguoi.xlsx (Member 2 task codes 2-01 to 2-12). The revised mandate does not authorize retroactive replacement of the 22 October submission or use of post-2022 observations to choose a 2022 investment policy.

Evidence examined: 2022 raw Yahoo archive and 96-month processed estimation panel; original decision PDF and confirmed weights; original Sample MV/SI/MinVar models, factor files; latest published M1 revised holdings, full ledgers, funding summary and rate shocks; M2 code on feature PR #6; GitHub Actions logs; original prepared submission ZIP (a local *candidate*, NOT a university confirmation). JNJ/Kenvue 2023 corporate-action facts were checked against primary JNJ issuer and US SEC filings strictly as an ex-post evaluation review.

**Critical boundaries:** pre-2023 static equity-exposure proxies are not actual 2023–2025 buy-and-hold returns. The case bonds have no real post-2022 market series. All utilities in M2 are equity-sleeve contributions under a simplified fixed-funding approximation, not fully integrated bond+equity intertemporal utility.

## 2. Quantitative original-versus-revised results, verified from M1

| Policy scenario | Bond cost USD | Net equity USD | Retained cash by 2030 USD | Required 8y equity CAGR |
|---|---:|---:|---:|---:|
| Original frozen (2,400 Beta / 3,600 Delta) | 5,764,524.00 | 6,229,246.75 | 630,000 | 4.6577% |
| M1 revised principal matching (2,400 Beta / 1,200 Gamma / 2,400 Delta) | 5,784,228.00 | 6,209,562.44 | 564,000 | 4.7951% |
| M1 revised coupon funding (2,400 Beta / 846.428571 Gamma / 2,400 Delta) | 5,429,776.18 | 6,563,660.16 | 168,000 | 4.6309% |

All are at 2.3% inflation, zero initial cash buffer, zero reinvestment of contractual coupons, 10bp one-off equity entry cost and a nominal 2030 hurdle of approximately USD 9.596m. Fractional case-bond holdings ARE permitted by the official brief. The difference between two revised scenarios is a choice of **funding method**, not solely the trustees' revised mandate.

Source ledger checks: 2 cases x 8 annual dates x 7 cashflow/cash-balance metrics = 112 independent comparisons within one cent. Neither M1 candidate has been approved by a human in this PR.

For Sample MV original frozen normalized weights, the revised principal utility contribution is approximately 0.053328705 and optimized approximately 0.053328718; the coupon case is 0.055826785 and optimized approximately 0.055830594. Marginal utility benefits from reoptimizing are small; this supports **conditionally** keeping frozen equity weights, not claiming that the whole-fund optimal strategy has been proved. Recomputed fixed-weight A* values are about 8.94 (principal) and 8.46 (coupon), not reoptimized switching boundaries.

An instantaneous equity -25% plus +100bp bond stress is about 14.42% of initial fund assets (revised principal) and 15.08% (coupon); it is NOT a rolling 12-month investment return or an automatic trigger under the defined withdrawal-adjusted review rule. Coupon funding leaves cash approximately zero after the 2025 payment, versus approximately USD 396k under principal matching.

## 3. Member 2 task-by-task acceptance

| Task | Requirement from group assignment | Status | Evidence / missing action |
|---|---|---|---|
| 2-01 | Preserve original weights, comparator and evaluation rule; actual LMS receipt | **PARTIAL** | Original files and comparison utility exist. GitHub original weights and locally prepared 22-Oct ZIP have same economic policy but different byte hashes because of internal metadata. Exact submitted files and true LMS receipt not confirmed. Never manufacture the receipt. |
| 2-02 | Retrieve actual 2023–2025 daily evaluation prices and archive original source, parameters and retrieval timestamp | **BLOCKED BY REAL PROOF/DATA** | Downloader, source checks and synthetic tests exist. No accepted actual post-freeze price archive in the audited PR/main. |
| 2-03 | Verify corporate actions incl JNJ/Kenvue | **PARTIAL** | New post-freeze primary-source event review documents voluntary tender offer (July–August 2023); original no-election rule implies do not tender. Actual Yahoo adjusted-close construction and human reviewer remain unverified. |
| 2-04 | Integrate M1 funding and exact USD12m allocation | **PASS — TECHNICAL** | M1 principal/coupon directly imported and checked, all three scenarios reconcile with entry fee. Pending human selection of one funding solution. |
| 2-05 | Recompute dollar purchases at the exact original normalized weights | **PASS — TECHNICAL** | Twelve full-precision asset weights and dollars for original/revised alternatives; no rounding fed into optimizer. |
| 2-06 | Sample-covariance MV vs single-index MV vs constrained minimum variance, common universe/method | **PASS — TECHNICAL** | Original 96-month data and common constraints used; both model-implied covariance risks and sample-covariance common assessment clearly labelled. |
| 2-07 | Foundation A=3/A=6 utility, A*, lambda* | **PASS — CONDITIONAL** | Recomputed for M1 scenarios, thresholds explicitly *fixed-weight only*; group must not equate equity contribution with complete foundation utility. |
| 2-08 | 2030 hurdle, inflation/buffer sensitivity and combined funding-equity stress | **PASS — TECHNICAL** | NEW 3 scenarios x 4 inflation rates x 3 unspent buffer policies (36 rows), terminal wealth/goal-gap sensitivities, M1 exact bond repricing plus equity shocks. Need group interpretation and chosen scenario. |
| 2-09 | Actual frozen 2023–2025 growth versus VTI: CAGR, vol, drawdown, active, tracking error | **BLOCKED BY REAL PROOF/DATA** | Existing functioning evaluator and synthetic tests are NOT empirical output. Requires receipt, later raw Yahoo archive and corporate-action QA. |
| 2-10 | Approve one growth choice and handoff original/new weights to M3 | **PARTIAL** | Conditional retained Sample MV recommendation and new 15-scenario M3 handoff are built. M1 and group have not approved bond funding; M3 review pending. |
| 2-11 | Memo portfolio/robustness/evaluation section and figures/slides | **PARTIAL** | English revised draft and source-mapped three-slide outline created; actual evaluation figure, final group memo/deck (owned by M3) and source-to-output acceptance pending. |
| 2-12 | Independent M2 review of M1 revised funding/ledgers | **PASS — NUMERIC ONLY** | NEW 112-cell annual bond coupon/principal/cash audit and data-tampering unit test. Human review/comment and funding recommendation still needed. |

The group spreadsheet lists these tasks as “Chưa bắt đầu”; those cells are not an accurate measure of the implementation already present in the repository. Conversely, a PASS of automated tests does not substitute for original LMS provenance, observed evaluation and M3/M1 sign-off.

## 4. Errors found and fixed in PR #6

1. Root GitHub CI previously failed on missing pypdf: pinned pypdf, corrected repository-weight test to match actual GitHub policy CSV without misrepresenting it as LMS receipt. Original 22-Oct investment records were not overwritten.
2. Group QA ran integration tests in a copied portfolio-only directory without M1 funding: preserved isolated historical rebuild but ran cross-workstream tests from the actual complete repository.
3. Original M2 manual workflow referenced nonexistent files and live-download configuration: replaced with reproducible offline revised scenario workflow.
4. M3 scenario IDs previously collided under casing, and a previous manifest self-hashed on second run: ensured 15 unique scenario IDs, 96 months each, and manifest excludes itself from SHA registry. NEW two-run same-directory byte-identity test catches regression.
5. Missing required inflation/buffer sensitivity: implemented and tested a 36-case grid, with operating buffer assumed unspent at 0% through 2030 (not an observed investment outcome). Changing this treatment is an explicitly separate policy sensitivity.
6. Portfolio comparison did not distinguish model-implied volatility from common sample-covariance performance assessment: now exposes both and validates stock/sector/ETF caps independently.
7. M1 cash-flow ledgers were not independently checked cell-by-cell from coupon/maturity conventions: 112 comparisons and tamper rejection added.
8. The revised mandate response did not explicitly separate changes driven by the mandate vs funding method vs equity reoptimization: a numerical additive bridge now identifies all three components, under a clearly stated equity-only utility approximation.
9. JNJ/Kenvue primary documents are now cited in an ex-post action research note. This does NOT establish the vendor adjusted-close treatment and does not complete the real 36-month evaluation.
10. A separate English memo/slide handoff identifies precisely which output generates each committee claim; no fabricated empirical chart is included.

## 5. Inconvenient findings and remaining conceptual limitations

- Earlier 2025 obligations do not change the USD 6m total, but change bond funding timing, equity capital and liquidity. Funding alternatives cannot be ranked only by cheaper entry prices or higher equity-sleeve utility; 2025 cash slack is materially different.
- The original 25% idiosyncratic-history/75% VTI prior is a judgment, not an estimated true future mean. Maximum stock, sector and ETF exposure constraints are governance choices. Sample-vs-single-index uncertainty persists.
- 2015–2022 Yahoo data were downloaded retrospectively in October 2026 and might include revised adjusted closes; ex-post candidate selection has survivor/look-ahead limitations. This is disclosed, not disguised.
- The original 2022 SEC eligibility register is not equivalent to a fully archived primary-source collection; outstanding source preservation should be disclosed.
- The 12% warning and 15% review are not hard loss caps, and contractual hold-to-maturity funding cannot be converted into observed fictional bond mark-to-market returns.
- Existing CAPM/FF3 factor results (M3-owned) use static estimation proxies; keeping frozen normalized weights under funding-only changes implies identical normalized equity factor exposures. Changing normalized weights requires a new M3 estimation using aligned French data, not copying an alpha estimate.
- The 2030 target is a nominal translation of an original real purchasing-power goal. A hypothetical eight-year CAGR hurdle is neither a realized growth statistic nor a claim of mission success.

## 6. Human/external evidence blockers and exact handoff gates

**P0 — needed for final assignment:**
- Obtain actual university LMS receipt and exact originally uploaded PDF/data/code fingerprints. Local candidate ZIP has weights SHA256 9dd165122fbd2931679e903e8a59dbd32a15d4b7bfed53caa61e2b774d034ec0; GitHub current policy CSV SHA256 a15469f1478370e2d9399cae8ab7aae215545fe2e040d02435bdc3ea7d10672d. Same 12 economic weights, different byte-level metadata. Never rewrite authentic receipt/hash.
- After legitimate freeze verification, retrieve and preserve original daily yfinance responses for invested AAPL/MSFT/JPM/JNJ/PFE/PG/KO/CAT and VTI from 2023-01-03 to the last trading date of 2025, including yfinance version, retrieval time, request settings and source SHA. Audit JNJ/KVUE vendor-adjustment/no-election treatment against the original source documents and record a genuine reviewer. Run the original frozen policy vs VTI evaluator to produce 36 monthly returns, after-fee CAGR, volatility, max drawdown, tracking error and active return.
- Member 1 selects and signs off the bond funding policy and cash-flow assumptions. Member 3 independently reviews revised weights/factor implications and memo/slide integration. Final group decision log and contribution/critique/AI disclosures must reflect real human decisions.
- PR #6 remains unmerged until independent reviewer approval. A green CI on a feature branch is not final group archive or university submission.

**P1 — improve transparency if time permits:** complete original SEC archival sources, independently check the revised M1 Excel/notebook formula caches, verify final slides and memo against every named output, and ensure all datasets/figures are accessible from a single final offline package.

## 7. Reproduction and review commands

From GitHub feature PR #6's head, after installing root requirements on Python 3.12:

    python -m unittest discover -s portfolio_construction/tests -v
    python -m unittest discover -s factor_analysis/tests -v
    python -m unittest discover -s quality_assurance/tests -v
    python run_pipeline.py
    python portfolio_construction/revised_mandate/m1_integration.py
    python portfolio_construction/revised_mandate/policy_sensitivity.py
    python portfolio_construction/revised_mandate/m1_peer_check.py
    python portfolio_construction/revised_mandate/mandate_decomposition.py
    python portfolio_construction/revised_mandate/m3_handoff.py

Last known successful run on current implementation prior to audit note: **69 portfolio, 10 factor, 15 group QA unit tests; 37 PASS/1 WARN/0 FAIL/0 BLOCKED group QA**. Verify the last commit's CI URL before merge. The sole remaining group QA WARN is separate from an assertion of final empirical completeness; inspect the JSON reason, not merely the GO badge.

Actual LMS reviewer proof, 2023–2025 retrieval and pricing review are explicit *conditional* steps and must not be simulated with hand-authored records or assumed external connectivity.

## 8. Academic outcome and final decision recommendation

Technical M2 analysis, assumption sensitivity, and independent M1 ledger checks are substantially complete on the review branch. **The 12-task M2 obligation is NOT fully complete** because 2-01, 2-02, 2-03, 2-09, 2-10 and 2-11 require verifiable external/human or integrated evidence; group-wide manuscript/slides and signed contribution review remain outstanding.

The defensible provisional equity recommendation is to retain frozen Sample Mean-Variance weights as the baseline while presenting M1 Principal and M1 Coupon funding as distinct choices. A more aggressive revised whole-fund allocation increases potential growth exposure but reduces cash slack; the trustee-authorized choice cannot be delegated to an optimizer. The selection must reconcile payment certainty, financing trade-off, 2030 goal feasibility, and downside risk with actual institutional evidence. Do not claim that technical CI completion equals final 29 October submission readiness.

## Primary-source and repository links

- Official JNJ voluntary offer, July 2023: https://www.jnj.com/media-center/press-releases/johnson-johnson-launches-exchange-offer-for-separation-of-kenvue-inc
- JNJ final result, August 2023: https://www.jnj.com/media-center/press-releases/johnson-johnson-announces-final-results-of-exchange-offer-and-finalizes-separation-of-kenvue-inc
- JNJ SEC Form 8-K: https://www.sec.gov/Archives/edgar/data/200406/000020040623000086/jnj-20230823.htm
- Draft M2 PR (human review): https://github.com/lucasnguynn/BFIN-Assignment/pull/6
- Original M1 revised funding sources: https://github.com/lucasnguynn/BFIN-Assignment/tree/main/bond_funding/outputs/revised
- Group-wide integration issue: https://github.com/lucasnguynn/BFIN-Assignment/issues/5

**AI disclosure:** Material AI assistance was used for numerical review, code improvements, unit tests, source research, evidence tracing and English drafting. Tests and committed evidence should be independently examined by the named members. No human reviewer signature, financial result or university submission was fabricated.
