# JNJ / Kenvue split-off: post-freeze evidence review

This note covers a corporate action **in 2023**, after the historical 31 December 2022 decision. It is not an input to the original portfolio choice.

## Issuer and SEC facts checked

On **24 July 2023**, Johnson & Johnson announced that holders could exchange **all, some or none** of their JNJ common shares for Kenvue (KVUE) shares. The offer expired at the end of **18 August 2023** (New York time). On **23 August 2023**, the issuer reported the completed oversubscribed exchange and proration. The related JNJ Form 8-K records the disposition. The original portfolio policy forbids voluntary exchanges and discretionary rebalancing. A non-tendering JNJ shareholder therefore retains JNJ and must **not** receive KVUE shares in this portfolio model.

Sources:
- JNJ launch: https://www.jnj.com/media-center/press-releases/johnson-johnson-launches-exchange-offer-for-separation-of-kenvue-inc
- JNJ final: https://www.jnj.com/media-center/press-releases/johnson-johnson-announces-final-results-of-exchange-offer-and-finalizes-separation-of-kenvue-inc
- SEC Form 8-K: https://www.sec.gov/Archives/edgar/data/200406/000020040623000086/jnj-20230823.htm

## Numerical checks and limitations

- Original post-submission Yahoo responses are archived in `portfolio_construction/Portfolio Final/Sources/Yahoo Raw.zip`. Their SHA256 and matching processed-price hash are pinned in `Market Source.json`, with a retrieval date of **24 October 2026**.
- `python portfolio_construction/post_freeze_evaluation/jnj_vendor_check.py` validates source hashes; compares saved processed JNJ adjusted closes to the raw response; lists prices/dividends around the August event; and computes a **separate** no-tender ordinary-cash-dividend-reinvestment return from unadjusted closing prices. It never allocates KVUE stock.
- The final memo's approximately **USD 188** whole-equity value difference is an existing reported sensitivity, not a promise of exact live trading replication. Dividend timing, vendor back-adjustments, tax assumptions and historical fills remain limitations. The script's recorded difference should be reviewed against that earlier approximation before declaring full economic equivalence.

**Review status:** Issuer event and no-voluntary-exchange treatment established from sources. Archived-vendor numerical verification is automated and must PASS in the final GitHub build. It is **not** a personal signed audit; the source record's human-review flag remains false unless a real individual supplies their review and date. The 2023-2025 observed comparison continues to be described as price-derived and conditional; case bonds are modeled, not observed.

This note does not certify that the university accepted the original emailed archive or that its members were independently SHA256-verified. See `quality_assurance/Group Review and AI Use.md`.
