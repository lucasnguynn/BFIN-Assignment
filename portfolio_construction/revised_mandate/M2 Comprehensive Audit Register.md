# Kappa Foundation | M2 compliance and independent quality audit

**Verified checkpoint: 24 October 2026, feature PR #6.** This supersedes earlier M2 status reports in which observed 2023–2025 evaluation was still labeled absent. The course's four-page original group assignment and one-page 23 October trustee update have priority over the team's 16 October framework, task spreadsheet, source readmes or commentary.

## Decision gates and current judgement

**M2 quantitative implementation is substantially complete, but the final group assignment is not yet verified as complete.** The original decision and revised counterfactual use data ending 31 December 2022; the 2023–2025 Yahoo test is genuinely observed but has a conditional submission-provenance qualification. PR #6 has not been merged or accepted by human reviewers, and the group's eight-page final memo, final PDF plus editable slide source and single submission archive have not been evidenced as complete.

Evidence consulted: official BFIN group assignment (pp. 1–4); 23 October revised mandate; 16 October group framework (workstreams 3/4/6, §9 final archive); BFIN_Phan_Cong_3_Nguoi.xlsx task codes 2-01 to 2-12; the original 22 October policy; source files and CI tests on PR #6; archived observed Yahoo run #40093744756; M1 revised funding CSVs; M3 factor regression outputs.

## Task-to-evidence matrix

| Task | Required outcome | Technical evidence today | Residual limitation |
|---|---|---|---|
| 2-01 | Frozen original weights, VTI and evaluation rule, real submission proof | Unmodified case-date policy; exact-weight and PDF hash checks; university-email transmission dated 22 Oct 15:44:53 HCMC | Course acceptance and independently extracted emailed ZIP member hashes NOT VERIFIED. Local prepared ZIP differs in metadata bytes; economic weights equal |
| 2-02 | Actual Yahoo 2023–2025 acquisition, raw archive, dated source | PASS: 9 original yfinance response frames, 752 shared dates, yfinance 1.7.0, request parameters, source SHA256, 36 monthly dates in GitHub artifact #12560420593 | Vendor data retrospectively revised; ZIP artifact alone has limited retention; preserve exact source archive in final group ZIP |
| 2-03 | Corporate action: JNJ/Kenvue | JNJ issuer/SEC elective tender documented; no KVUE credited; no 2023 JNJ split in raw Yahoo; −USD 188.33 no-tender Close+Dividends sensitivity | Dividend sensitivity reinvests at ex-date (not necessarily executable pay date); a named reviewer and final vendor-action acceptance remain unsigned |
| 2-04 | Recompute revised growth budget and USD12m split | PASS technical: direct M1 principal/coupon source import, 10bp fee, capital reconciliation | Which revised bond funding is approved remains a group decision |
| 2-05 | Original full-precision weights at revised equity size | PASS technical: 12 exact assets × relevant funding/portfolio scenarios; rounded display weights not used in model | No final authorized funding choice |
| 2-06 | Sample MV, Single-Index MV, constrained Minimum Variance | PASS technical: same 96 months, forecast assumptions, long-only + direct-stock/sector/ETF caps; model-implied and common-assessment risk now distinguished | Sample statistics and retrospective candidate selection remain uncertain; original selected portfolio invests in eight direct stocks and zero candidate ETFs |
| 2-07 | A=3/A=6, fixed switching thresholds | PASS technical: revised equity utility and fixed-policy A*, lambda* with correct foundation equity fraction | Pairwise fixed-weight cutoffs are NOT full reoptimized switching boundaries; utility is equity contribution, not dynamic whole-fund optimization |
| 2-08 | 2030 hurdle, inflation/buffer, combined bond/equity stress | PASS technical: 3 funded cases × 4 inflation × 3 buffer policies = 36 rows; 0/3/6/10% illustrative terminal growth and exact +100bp/stock shock | Buffer assumed unspent at 0%, hypothetical shock not measured rolling withdrawal-adjusted 12%/15% review return |
| 2-09 | Actual frozen 2023–2025 growth vs frozen VTI | PASS observed-price computation, CONDITIONAL final evidence: 36 months; after-fee 17.6864% Sample MV vs 22.4469% VTI CAGR; volatility, monthly max drawdown, annualized active and tracking error source-hashed | Institutional acceptance and final JNJ reviewer check absent; not actual future bond total-fund returns |
| 2-10 | Revised growth recommendation and M3 handoff | Conditional analyst recommendation: retain frozen Sample MV; revised principal funding as conservative reference; quantify alternative coupon liquidity/opportunity cost; 15×96 M3 static-factor handoff | Group must authorize funding, and reviewer must accept updated handoff |
| 2-11 | M2 portion of final memo, slides and source-mapped figures | Cleaned source-specific English assessment, concise 577-word committee excerpt, four-slide outline, historical and observed figures and raw data in technical evidence ZIP | These files are inputs for the GROUP memo/deck; they are not the final ≤8-page memo, slide PDF/editable deck or group final ZIP |
| 2-12 | Independent M1 funding check | PASS numerical: 112 annual cash-flow ledger checks for principal/coupon, USD12m identity and tampered input detection | Human review/signoff outstanding |

**Framework M2 statistical cross-check (WS4):** A separate `M2 Factor Statistical Cross Check.md` documents exact n=96 FF3 betas, alphas, HAC diagnostics and uncertainty for growth, MSFT and PG. Frozen growth FF3 adjusted R² 0.84365 versus CAPM 0.78499, beta 0.8667, SMB −0.4265. The alpha intercept is a selected-sample estimate, not a proof of persistence. Member 3 owns model estimation; M2's check is an interpretation audit, not a signed peer review.

## Quantified decision evidence

| Measure | Original frozen | Revised principal | Revised coupon |
|---|---:|---:|---:|
| Bond funding cost (USD) | 5,764,524 | 5,784,228 | 5,429,776.18 |
| Net equity after 10bp fee (USD) | 6,229,246.75 | 6,209,562.44 | 6,563,660.16 |
| Contractual cash retained at 2030 (USD) | 630,000 | 564,000 | 168,000 |
| Required eight-year equity CAGR at 2.3% inflation | 4.6577% | 4.7951% | 4.6309% |

For revised principal funding, A=3 equity-utility contribution is 0.053328705 at frozen weights and 0.053328718 with reoptimization. For coupon funding, it is 0.055826785 versus 0.055830594. A pairwise frozen-versus-Minimum-Variance A-switch is about 8.94 or 8.46, respectively. The mandate-only/funding-choice/equity-method bridge is coded separately; no 2023–2025 prices are admitted to the 2022 decision set.

An instantaneous equity −25% and bond +100bp repricing shock indicates approximately 14.42% initial-fund loss for principal and 15.08% for coupon funding. These are NOT the same statistical measurement as a rolling 12-month withdrawal-adjusted review. The 2023–2025 traded growth sleeve earned positive absolute return but lagged VTI by 4.7605 percentage points of after-fee CAGR; arithmetic annualized active was −4.1069% with 6.9062% tracking error. This inconvenient result must remain visible in the final memo.

## Reproducibility and archive gate

- ZIP `Kappa M2 Completed Technical Evidence.zip` has 21 files, ZIP CRC PASS and 20/20 internal SHA256 checks PASS. It contains the observed raw/vendor/source records, not the complete revised M1/M2/M3 executable repository. It must **not** be submitted alone as the assignment's reproducible group archive.
- PR #6 contains the revised scenario code, peer checker, 2030 sensitivity, mandate attribution, M3 handoff, tests and source-mapped English drafts. Clean CI on the PR shows 69 Portfolio, 10 Factor and 15 group QA tests and group verdict 37 PASS / 1 WARN / 0 FAIL. The lone WARN `BOND.candidateB_label` is an original M1 label issue; no silent rewrite of byte-pinned historic evidence was performed.
- The original frozen 22 October policy and initial decision must remain physically available in the FINAL group archive, not merely as a GitHub URL. Group final also requires an eight-page committee memo (+at most one reference page), deck PDF **and editable source**, executed code/requirements, raw/processed/output data, dated source record, decision log, contribution/critique and disclosed material AI use.
- GitHub artifact #12560420593 is a dated data source but has 45-day retention. Include exact raw ZIP and versioned source records inside the final submitted group archive before expiry.
- Original 2022 SEC eligibility web register covers 10 common-stock candidates, two differentiated ETF candidates and VTI. Primary source URLs and recorded dates exist; **original SEC bytes remain unarchived**, with JPM not independently reverified in the old register. This is a documentation limitation, not a confirmed case-date eligibility failure.

## Writing and academic-integrity audit

Earlier English drafts had contradictory present-tense statements: a stale 'evaluation pending' slide alongside already computed real observed returns; an old audit matrix still marked 2-02 and 2-09 blocked; and repetitive AI-sounding process disclaimers. Those were replaced by `M2 Revised Assessment.md`, a single current four-slide outline, and the shorter `M2 Committee Excerpt.md`. The excerpt cites inconvenient benchmark underperformance and concrete model trade-offs rather than stock claims or vague policy assurances.

**No method can honestly certify that writing has no 'AI-generated signs', and a detector score does not establish true authorship.** More importantly, the official assignment explicitly requires disclosure of material AI assistance and the human checks performed. Never conceal AI involvement, invent first-person student work, create an artificial reviewer signature or present code as if it were independently written without explaining actual contributions. Students should review the final text in their own words, check every figure, and be ready to defend model choices orally. Technical fixes and accurate sourcing improve scholarly credibility; concealment would weaken compliance.

## Final verdict

**M2 technical research and source-backed observed evaluation: largely complete. Group final submission: NOT YET CERTIFIED COMPLETE.** Remaining external/human gates are actual course acceptance and source ZIP-member fingerprints, signed JNJ corporate-action review, M1 approved funding selection, M3 factor/portfolio review and group memo/deck/archive submission. Do not assert all 100 rubric points are satisfied until the single integrated final package is checked against the official assignment.

**Sources:** Original BFIN WS2026 assignment; BFIN-WS2026 Group Case Mandate Update (23 October); team development framework version 1.0; Member 2 task spreadsheet; M1 revised funding outputs; [PR #6](https://github.com/lucasnguynn/BFIN-Assignment/pull/6); [observed Yahoo artifact #12560420593](https://github.com/lucasnguynn/BFIN-Assignment/actions/runs/40093744756/artifacts/12560420593); [JNJ SEC exchange prospectus](https://www.sec.gov/Archives/edgar/data/1944048/000162828023029376/kenvue424b3.htm); [Yahoo adjusted close definition](https://in.help.yahoo.com/kb/adjusted-close-sln28256.html).

**Disclosure:** This audit and document repair used material AI assistance for source comparison, code review, numerical checks and academic writing. Institutional/human approval has not been fabricated.