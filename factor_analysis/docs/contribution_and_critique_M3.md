# Individual Critique - Member 3 (QA & Factor Analysis)

**Member:** Lê Hồ Thu Giang - Member 3  
**Updated:** 28 October 2026  
**Scope:** Final submission under the revised mandate. Original and revised policy comparisons are retained in the supporting analysis.

## 1. The Strongest Argument Against Our Recommendation

The strongest argument against the recommended Sample Mean-Variance portfolio is its dependence on uncertain expected-return estimates and its concentration in selected individual stocks. AAPL and MSFT together reach the 30% direct-stock Technology sector cap, while PG also reaches the 15% individual-stock cap.

The assumed risk aversion A = 3 determines the penalty assigned to estimated portfolio variance. Separately, the historical-mean confidence weight lambda = 0.25 determines the contribution of security-level sample means to the expected-return forecasts. These assumptions affect the portfolio choice through different channels.

Although expected returns are shrunk towards a VTI-based prior, historical performance still influences the allocation. The relatively small estimated utility advantage over Single-Index Mean-Variance and the sensitivity of optimized weights to inputs weaken any claim that the selected portfolio is reliably superior. The constrained Minimum Variance portfolio remains a credible lower-risk alternative.

## 2. The Most Significant Data Limitation

The analysis uses 96 monthly observations from January 2015 to December 2022. This provides a common estimation window within the permitted period, but historical volatility, correlations and factor relationships may not represent future market regimes.

The sample includes different market conditions, including the pandemic and the 2022 tightening period. It does not establish that future downside risk will necessarily be higher or lower than estimated. Historical estimates should therefore be supplemented by stress scenarios and sensitivity analysis.

Yahoo Finance and Kenneth French data retrieved in 2026 may incorporate retrospective revisions. The exercise is a retrospective case rather than a genuinely unseen live investment experiment. The candidate universe and portfolio selection also remain exposed to selection and survivorship bias.

## 3. Conditions for Reconsidering the Decision

For the two fixed portfolios being compared, preference reverses at approximately A = 8.94 under revised principal matching and A = 8.46 under revised coupon funding, compared with approximately A = 8.91 under the original plan.

Under principal matching with A = 3, reducing the historical-mean confidence weight below approximately lambda = 0.0839 favours the fixed Minimum Variance alternative. The corresponding original-plan threshold is approximately 0.0842.

These thresholds compare two fixed weight vectors. They are not switching points between portfolios reoptimized at every parameter value. A material change in trustee risk preferences or forecast confidence should prompt reassessment and reoptimization rather than automatic adoption of the old Minimum Variance weights.

Higher inflation raises the geometric growth rate required to achieve the 2030 purchasing-power goal. The estimated 12.05% annual arithmetic return is not directly comparable with the required CAGR and does not establish a reliable funding margin. Goal feasibility should instead be assessed through explicit terminal-wealth scenarios and the associated risk and liquidity trade-offs.

## 4. Challenge and Cross-Workstream Contribution

I challenged the interpretation of the growth portfolio’s positive FF3 alpha. The estimated alpha of approximately 0.569% per month is an in-sample, model-relative intercept. It does not establish persistent stock-picking skill, particularly because the same estimation period helped select the securities and portfolio weights.

I checked that the estimation inputs end in December 2022 and that the separate 2023–2025 evaluation is not used to select the original portfolio. This observation cutoff does not eliminate the limitations of retrospectively revised historical data or retrospective security selection.

I also checked the distinction between the static-weight historical exposure series used for factor analysis and the drifting-weight buy-and-hold strategy used for the frozen evaluation. These series serve different analytical purposes.

Eta’s proposal to support mandatory payments with high-quality bonds provides a useful funding principle. However, historical risk-adjusted performance alone is insufficient to determine the growth allocation. Theta’s emphasis on factor exposures helps explain economic risks, but the persistence of abnormal returns is not established by a positive alpha in a single selection sample.

## 5. Material AI Assistance and Checks

### Scope of AI Assistance

AI materially assisted with regression and figure code, source discovery and organization, statistical calculations, QA checks, drafting, editing and document preparation.

The students retained responsibility for selecting the CAPM/FF3 framework, research questions, estimation window, assumptions, interpretation and final recommendation. Material assistance is disclosed in `quality_assurance/Group Review and AI Use.md`.

### Numerical Reproducibility Checks

Checks included reproducing factor estimates from saved factor and return data, comparing generated outputs with the reported results, and running the available numerical QA pipeline.

The pipeline reported 48 PASS, 1 WARN and 0 FAIL. This supports consistency within the checks performed. It does not, by itself, establish complete end-to-end regeneration of every output from raw inputs. That broader claim requires a successful rebuild after generated intermediate files have been removed.

### Data and Statistical Checks

Checks covered monthly decimal units, aligned dates, subtraction of the risk-free rate once, regression coefficients, adjusted R-squared and alpha uncertainty.

Conventional OLS estimates are supplemented by HAC standard errors with three lags. These measures describe model-conditional statistical uncertainty; they do not eliminate selection bias, omitted-factor risk or uncertainty about future performance.

### Academic Integrity

AI-assisted interpretations were reviewed against the selected course framework. Automated checks complement human review and do not replace it. Each member remains responsible for understanding and explaining the submitted analysis.

## 6. Contribution to the Revised Mandate

- I extended the QA pipeline with revised-mandate checks and prepared the revised-scenario factor table using `factor_analysis/revised_mandate_factors.py` and `quality_assurance/revised_mandate_checks.py`.
- I independently recalculated Member 1’s liability ledgers and checked that both revised funding alternatives cover the 2024, 2025 and 2027 payments and reconcile to USD 12 million.
- I checked that changing the funding allocation without changing normalized equity weights leaves the analytical growth-return series unchanged. The corresponding CAPM and FF3 estimates therefore remain unchanged.
- I prepared factor estimates for the alternative equity-policy scenarios, since reoptimized weights require their own factor analysis.
- I drafted the consequential decision log in `quality_assurance/decision_log.csv` and the exhibit manifest in `quality_assurance/memo_assets_manifest.csv`.
- I prepared the supporting factor-evidence text in `factor_analysis/docs/memo_section_factor_evidence.md` for the final memo’s factor-analysis section.

Unchanged factor estimates under unchanged equity weights do not independently prove that the original weights remain optimal. They show that a funding-only change does not alter the normalized equity exposure being analysed.

## 7. Strongest Remaining Weakness in the Factor Evidence

The FF3 alpha is estimated over the same historical window used to help select the securities and portfolio weights. A positive intercept may reflect selection effects, omitted factors or estimation error rather than persistent investment skill.

The separate 2023–2025 evaluation reports a portfolio CAGR of approximately 17.69%, compared with 22.45% for VTI. This underperformance weakens any claim of a reliable stock-selection advantage, despite positive absolute returns.

The 2015–2022 regressions describe historical exposures. They do not, by themselves, explain the later performance shortfall or establish the likelihood of meeting the 2030 purchasing-power goal.

## 8. Limits of My Checks

My checks assess numerical consistency, model implementation and the interpretation of the submitted evidence. They do not establish actual trade execution, future factor stability, a maximum investment loss or achievement of the 2030 goal.

Direct comparison of the supplied 22 October archive with the final project confirms that the retained initial decision record, frozen weights and key raw Yahoo/French inputs match. This supports preservation of the original policy, without asserting institutional acceptance of the submission.

The eligibility register contains dated source references, but not every original SEC document is archived. The scope of source verification should remain explicit.

Human approval of the analysis is separate from automated numerical validation. The peer review below records the agreed review of my work.

## 9. Peer Review

**Reviewer:** Nguyễn Ngọc Thảo An - Member 1  
**Review date:** 28 October 2026  
**Models/data checked:** The complete Member 3 workstream, including CAPM and FF3 specifications, factor-data units and timing, excess-return construction, regression outputs, interpretation of alpha and factor exposures, revised-mandate comparisons, QA checks and decision-reversal thresholds.  
**Review outcome:** Nguyễn Ngọc Thảo An reviewed the complete Member 3 workstream and approved the analysis and recommendation.  
**Reviewer confirmation:** Nguyễn Ngọc Thảo An confirmed her review and approval of Lê Hồ Thu Giang’s factor-analysis and QA work on 28 October 2026.

I remain responsible for updating the Member 3 documentation to reflect the agreed revisions and maintaining consistency with the final memo, group review record and decision log.