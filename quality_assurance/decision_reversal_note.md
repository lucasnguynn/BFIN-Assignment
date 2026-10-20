# Decision reversal: wording for the memo section "Risk, utilities and reversal threshold"

Source of every number: `quality_assurance/decision_reversal.py` (gate `REVERSAL.*` in `qa_report.json`), tables
`decision_threshold_reconfirmation.csv` and `decision_threshold_reoptimization_contrast.csv`.

## Draft paragraph 

The recommended Sample Mean-Variance (MV) policy is preferred to the rejected Minimum-Variance policy at the base
assumptions (risk aversion A = 3, weight of 25% on each security's own historical mean): fund-level utility is 0.05347
versus 0.04937. Holding the two weight vectors fixed, the preference reverses under two measurable conditions. First, if
risk aversion rises above A* = 8.91 (about three times the base value), Minimum Variance is preferred. Second, if the
weight on historical security means falls below lambda* = 0.0842 (about one third of the base 0.25), the noisy sample
means are shrunk so strongly towards the market mean that the lower-volatility portfolio wins. Both thresholds were
re-derived independently from the 96 monthly returns (closed form and root finder agree to 1e-14), and the utility
formula U = F*E(r) - (A/2)*F^2*Var(r) with F = 0.5191 reproduces the reported utilities. The thresholds apply only to
these two fixed allocations. If the portfolio is re-optimised, the switching point differs: at A = 8.91 a re-optimised
portfolio beats both fixed policies by 0.0016 utility, and as lambda approaches 0 the optimum converges to Minimum
Variance. We therefore treat the thresholds as review triggers, not as automatic switching rules.

## Facts that support the paragraph

| Item | Value | Where it comes from |
|---|---|---|
| Base utility, Sample MV / Min-Var | 0.053469 / 0.049374 | `REVERSAL.utility_formula_matches_shipped` |
| lambda* (A = 3) | 0.084171 | `decision_threshold_reconfirmation.csv` |
| A* (lambda = 0.25) | 8.9104 | `decision_threshold_reconfirmation.csv` |
| Utility of both policies at A* | 0.03561 | contrast table, row "at A*" |
| Re-optimised utility at A* | 0.03720 (+0.0016) | contrast table |
| Weights at lambda = 0, re-optimised vs Min-Var | identical (max gap 0) | contrast table, row "lambda=0" |
| A = 20, lambda = 0.25 | Min-Var fixed policy beats frozen Sample MV (0.00978 vs 0.00210) | contrast table |

## Limits to keep in the memo
- The comparison is between two fixed weight vectors under the same covariance matrix and expected-return rule; it is not
  a statement about the best portfolio at each (A, lambda).
- The thresholds depend on the 10 bp entry cost and the 2022 funding split through F = 0.5191.
- A* is not "the foundation's risk aversion": the trustees have not stated one, so A is varied rather than chosen.
