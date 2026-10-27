# Member 1 Contribution and Critique

## Contribution

I prepared the bond valuation and liability-funding analysis, including contractual cash flows, yields to maturity, the incomplete spot curve, duration, convexity and interest-rate scenarios. I compared the original funding candidates and updated the Excel model and Python notebook for the revised mandate.

For the revised mandate, I compared principal matching with coupon funding, prepared the cash-flow ledgers for 2023–2030, reconciled the USD 12 million initial allocation and calculated the required equity CAGR. I also prepared the bond-funding memo and decision log, distinguishing the effects of the revised payment schedule from changes in funding policy.

The group selected principal matching: 2,400 Beta, 1,200 Gamma and 2,400 Delta bonds. The bond purchases cost USD 5,784,228, leaving USD 6,209,562.44 for equity purchases after an entry fee of USD 6,209.56. Coupons are retained as cash earning 0%, accumulating to USD 564,000 by the end of 2030.

## Checks Performed

Checks covered consistency between the key Excel and Python results, bond purchase costs, annual cash flows, mandatory-payment coverage and the initial capital reconciliation. Retained coupons are counted only once, and the original mandate is preserved for comparison.

Independent recalculation confirmed the funding figures. The cash-flow checking script passed all 112 comparisons across the principal-matching and coupon-funding ledgers, with discrepancies below USD 0.01.

Interest-rate scenario changes in market value are distinguished from contractual payment coverage. Under the case’s default-free assumption, holding the bonds to maturity preserves their contractual cash flows.

## Review by Another Member

**Reviewer:** Nguyen Dang Quoc Dat

**Review date:** 27 October 2026

**Review scope:** Bond holdings and purchase costs, mandatory-payment coverage, the coupon cash ledger, the USD 12 million allocation reconciliation and consistency with the growth-allocation inputs.

**Technical findings:** The numerical checks identified no material discrepancies in the funding figures or payment ledgers. Both funding alternatives cover the revised mandatory payments under the stated assumptions.

**Reviewer confirmation:** Nguyen Dang Quoc Dat reviewed the Member 1 funding analysis and confirmed the findings on 27 October 2026.

## Critique of the Final Recommendation

Principal matching meets the mandatory payments without relying on equity sales. However, retaining coupons at 0% has an opportunity cost. Coupon funding provides more initial growth capital and a lower required equity CAGR: approximately 4.63%, compared with 4.80% under principal matching.

Our recommendation prioritises principal receipts on each payment date and a larger retained cash reserve. It does not establish superior terminal wealth or guarantee achievement of the 2030 purchasing-power goal. The growth allocation remains exposed to investment losses.

## Group control, AI assistance and verification

The group representative describes the students as the decision-makers: they selected the bond-funding concept, lecture valuation methods, assumptions, alternatives and liquidity trade-off, then judged the chosen result and submission format. AI provided execution support, code, data/source research, comparisons and document editing. The dated Member 2 review recorded above predates this note and is retained as recorded; this update does not create any new reviewer's signature or certify new personal actions. See `quality_assurance/Group Review and AI Use.md`.

## AI Assistance and Verification

I used AI to explain Python coding steps, help identify potential data and calculation inconsistencies, and support drafting and editing of the funding memo, decision log and contribution statement.

Verification included independent recalculation, comparisons between Excel and Python outputs, checks against the case’s bond quotes and contractual cash flows, and reconciliation of the initial allocation and payment ledgers. AI-assisted checks do not replace review by another group member. I remain responsible for understanding and explaining the analysis submitted under my name.