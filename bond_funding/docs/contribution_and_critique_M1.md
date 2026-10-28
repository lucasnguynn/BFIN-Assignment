# Member 1 Contribution, Peer Review and Critique

**Member:** Nguyễn Ngọc Thảo An - Member 1  
**Workstream:** Bond Valuation and Liability Funding

## Contribution

I prepared the bond valuation and liability-funding analysis, including contractual cash flows, yields to maturity, treatment of the incomplete spot curve, duration, convexity and interest-rate scenarios. I compared the original funding candidates and updated the Excel model and Python notebook for the revised mandate.

For the revised mandate, I compared principal matching with coupon funding, prepared the cash-flow ledgers for 2023–2030, reconciled the USD 12 million initial allocation and calculated the required equity CAGR. I also prepared the bond-funding memo and decision log, distinguishing the effects of the revised payment schedule from changes in funding policy.

The group selected principal matching: 2,400 Beta, 1,200 Gamma and 2,400 Delta bonds. The bond purchases cost USD 5,784,228, leaving USD 6,209,562.44 for equity purchases after an entry fee of USD 6,209.56. Unspent coupons are retained as cash earning 0%, with a closing cash balance of USD 564,000 by the end of 2030 after the mandatory payments.

## Checks Performed

Checks covered consistency between the key Excel and Python results, bond purchase costs, annual cash flows, mandatory-payment coverage and the initial capital reconciliation. Retained coupons are counted only once, and the original mandate is preserved for comparison.

The independent cash-flow checking script passed all 112 comparisons across the principal-matching and coupon-funding ledgers, with discrepancies below USD 0.01.

Interest-rate scenarios distinguish changes in market value from contractual payment coverage. Under the case’s default-free assumption, holding the matched bonds to maturity preserves the contractual cash flows required for the scheduled payments.

## Peer Review

**Reviewer:** Nguyễn Đặng Quốc Đạt - Member 2  
**Review date:** 27 October 2026  
**Models/data checked:** Bond holdings and purchase costs, mandatory-payment coverage, coupon cash-flow ledgers, the USD 12 million initial allocation reconciliation, and consistency with the equity-funding inputs.  
**Review outcome:** The review identified no material discrepancies in the funding figures or payment ledgers. Both principal matching and coupon funding cover the revised mandatory payments under the stated assumptions.  
**Reviewer confirmation:** Nguyễn Đặng Quốc Đạt reviewed Nguyễn Ngọc Thảo An’s bond-funding analysis and confirmed the findings on 27 October 2026.

## Critique of the Final Recommendation

Principal matching meets the mandatory payments without relying on equity sales. However, retaining coupons at 0% has an opportunity cost. Coupon funding provides more initial growth capital and a lower required equity CAGR: approximately 4.63%, compared with 4.80% under principal matching.

Our recommendation prioritises principal receipts on each payment date and a larger retained cash reserve. Under principal matching, approximately USD 396,000 remains immediately after the 2025 payment, while coupon funding leaves effectively no cash at that point. Both alternatives remain feasible under the stated contractual cash-flow assumptions.

Principal matching does not establish superior terminal wealth or guarantee achievement of the 2030 purchasing-power goal. The equity allocation remains exposed to investment losses, and the bonds remain exposed to market-value changes before maturity. The trustees should understand the opportunity cost of the larger cash reserve and the distinction between payment coverage and investment performance.

## Material AI Assistance and Verification

AI assisted with Python code development and review, source research, quantitative comparisons, drafting, editing and document preparation. The students retained responsibility for selecting the funding approach, valuation methods, assumptions and alternatives, and for interpreting the results and choosing the recommendation.

Verification included recalculating bond cash flows and purchase costs, comparing Excel and Python results, checking the case bond quotes and contractual payments, and reconciling the initial USD 12 million allocation.

The human peer review is documented above. Automated checks support numerical verification but do not replace that review. I remain responsible for understanding and explaining the bond-funding analysis submitted under my name.