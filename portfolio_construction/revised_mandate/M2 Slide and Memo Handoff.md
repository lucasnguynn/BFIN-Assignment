# M2 final memo and slide handoff (English, for Member 3 integration)

**Draft evidence, 24 October 2026. M1 funding not approved; 2023–2025 evaluation is still pending.** Keep these within the group memo's 8-page body and presentation PDF/editable source constraints. Do not paste figures that have not been generated from named outputs.

## Slide A — What the new trustee commitments change

Headline: **Earlier 2025 payment changes the affordable growth sleeve, even though mandatory nominal liabilities remain USD 6.0m.**

| Scenario | Bond cost USDm | Net equities USDm | Retained 2030 cash USDm | 2030 equity CAGR hurdle |
|---|---:|---:|---:|---:|
| Original 22 Oct | 5.7645 | 6.2292 | 0.6300 | 4.6577% |
| Revised principal matching | 5.7842 | 6.2096 | 0.5640 | 4.7951% |
| Revised M1 coupon funding | 5.4298 | 6.5637 | 0.1680 | 4.6309% |

Evidence: M1 revised_funding_summary.csv and original_vs_revised_mandate.csv; independent M2 m1_integration.py and policy_sensitivity.py. Do not label the coupon alternative as chosen without group approval.

Visual direction: one 3-scenario horizontal bar comparison for net equity and retained cash. No claim that arithmetic 12.05% is a forecast of realized 8-year CAGR.

## Slide B — What changed because of the mandate vs the financing method

Headline: **Retain frozen equity weights as the mandate-only counterfactual; distinguish bond financing from portfolio-method changes.**

Use mandate_effect_bridge.csv and mandate_funding_method_contrast.csv as sole quantitative source. The attribution has three sequential contributions:

1. Original frozen -> revised principal/frozen: payment timing and principal matching under unchanged 2022 model.
2. Revised principal/frozen -> revised coupon/frozen: additional use of contractual coupons to fund revised commitments; a separate financing choice.
3. Revised coupon/frozen -> revised coupon/reoptimized: normalized equity weights change under the same revised bond funding.

Footnote: reported utility is only the **equity contribution** under a fixed bond-sleeve approximation, not the full fund's investor utility. Fixed-weight A* and lambda* must not be called reoptimized switch thresholds.

## Slide C — Risk and 2030 goal sensitivities

Headline: **Cheaper funding means a larger equity allocation and thinner 2025 liquidity.**

- After the 2025 payment, principal matching retains roughly USD 396,000 cash; M1 coupon funding is near zero.
- A hypothetical instantaneous equity −25% / parallel bond +100bp scenario corresponds to initial-fund losses around 14.42% (principal) versus 15.08% (coupon). This is NOT the rolling 12-month, withdrawal-adjusted 12% warning / 15% mandatory-review measure.
- Present selected inflation (2.0%, 2.3%, 3.0%, 4.0%) and untouched initial cash buffers (0, 250k, 500k). Clearly label buffer as kept unspent at 0% through 2030.

Evidence: combined_stress.csv, 2030_inflation_buffer_sensitivity.csv, M1 Cashflow Independent Check.csv. Status: policy-selection discussion, not authorized decision.

## Mandatory final evaluation slide placeholder (DO NOT insert invented numbers)

Use only real, audited output of post_freeze_evaluation/evaluate.py, after original LMS confirmation and later dated raw archive. Report the frozen 2023–2025 growth strategy versus VTI, 36 monthly returns, after-fee CAGR, volatility, maximum drawdown, tracking error, annualized active return, and source/corporate-action caveats including JNJ/Kenvue. If evidence remains unavailable, accurately mark the empirical test incomplete and explain the limitation. Static 2015–2022 factor-exposure proxies cannot substitute for this slide.

## Final approvals required

Member 1 selects revised bond funding and documents the 2025 liquidity trade-off. Member 3 performs independent factor/handoff review and owns the integrated memo, deck PDF and editable deck. Member 2 validates actual evaluation and adds a documented critique. No contributor signs on behalf of another.


## Slide D — Observed frozen evaluation (provisional evidence, 24 October 2026)

**Headline: The frozen Sample MV growth portfolio generated a 17.69% after-fee CAGR but trailed VTI's 22.45% CAGR over 2023–2025.**

- 752 shared Yahoo trading dates and 36 monthly observations, retrieved after documented original email submission.
- After-fee CAGR: 17.6864% Sample MV versus 22.4469% VTI; compounded shortfall: −4.7605 pp.
- Annualized monthly volatility: 11.8036% versus 12.6028%; maximum monthly NAV drawdown: −8.7010% versus −9.1098%; annualized tracking error: 6.9062%; arithmetic annualized active return: −4.1069%.
- Observed equity-only terminal values: USD 10,151,162.71 Sample MV vs USD 11,430,109.15 VTI.
- JNJ no-tender alternative ordinary-dividend proxy changes portfolio terminal value only by −USD 188.33. Do not credit KVUE tender shares.
- Label this slide **CONDITIONAL OBSERVED DATA — email transmission documented, not LMS acceptance; JNJ human review pending**. It must not be represented as a verified final LMS-frozen outcome.
- Strict source: `M2 Actual Observed Evaluation Evidence.md` and GitHub [observed-data artifact #12560420593](https://github.com/lucasnguynn/BFIN-Assignment/actions/runs/40093744756/artifacts/12560420593). Do not transfer unrounded historical returns from an unrelated scenario.

The previous placeholder above is superseded by this numerically supported *provisional* slide, not by an invented verified result.
