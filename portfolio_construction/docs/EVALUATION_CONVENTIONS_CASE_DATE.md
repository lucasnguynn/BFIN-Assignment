# Implementation conventions fixed before outcome evaluation

**Decision information date:** 31 December 2022. **Planned execution proxy:** 3 January 2023 closing adjusted-price anchor. The actual course submission and freeze are future events relative to the preparation of this package; no submission receipt is asserted.

1. **No discretionary trading.** Purchase the selected portfolio once at the stated entry-date closing-price proxy. Do not rebalance back to initial weights. Market movements and reinvested dividends cause weights to drift.
2. **Dividend reinvestment accounting.** Reinvest distributions within each paying security. A vendor adjusted-close series is a retrospective total-return proxy for this convention. Holding fixed *adjusted-price index units* is a mathematical implementation of reinvestment; it does **not** imply unchanged physical share counts. Do not add dividends to those index returns a second time.
3. **Corporate actions.** Do not elect voluntary tender/exchange offers. Mandatory events are handled consistently and documented. A later event may be investigated only during the post-freeze data-quality review; it must not be anticipated by name or used to revise the original 2022 decision. Vendor-adjusted histories may not match a particular holder's election, so any unresolved discrepancy must be disclosed.
4. **Benchmarks and costs.** Apply the same 3 January 2023 entry anchor and 10 bp initial cost to the frozen VTI comparator. Record the purchase budget inclusive of that cost; no routine rebalance costs arise under the passive policy.
5. **Evaluation timing.** Acquire and archive 2023-2025 actual data only after the real course submission and freeze. Calculations before that point may use synthetic fixtures to test software, never observed future returns to alter the 2022 weights.

The portfolio universe, initial weights, cash-flow funding plan, foundation risk aversion A=3 (A=6 sensitivity), covariance forecasts, benchmark and trustee review triggers are unchanged by this wording clarification.
