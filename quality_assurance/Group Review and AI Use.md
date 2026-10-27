# Group review, source evidence and AI use

Kappa Foundation | Group 4 | Record prepared 28 October 2026

## Group decisions and review status

A group representative reports that all three members agree with the final investment recommendation and the cross-workstream work. This is a **group-reported consensus**, not separately authenticated written approvals by every member. It must not be presented as individual signatures, a dated vote, a peer-review certificate or proof that any named person opened and approved a specific file.

The team's stated allocation of responsibility is that the students originated and controlled the investment concept; chose the suitable course theories and formulas, bonds, stocks, sources, assumptions and constraints; tested feasibility and the financial logic; decided which results to accept; and chose the presentation/document structure and design. The human group retains the responsibility for explaining, evaluating and submitting the work. AI assisted with code, literature and source discovery, data acquisition and organization, execution of calculations, reproducibility checks, numerical comparisons, layout implementation and editing. Technical output from AI was subject to the group's financial decisions and supervision. This description reflects the account supplied by the group's representative and does not independently authenticate each member's activity.

| Workstream | Evidence of review | Status |
| --- | --- | --- |
| Member 1: bonds and funding | Named Member 2 peer review is documented in bond_funding/docs/contribution_and_critique_M1.md (27 October); 112 cash-flow checks described there | Named review recorded in source; no separate signature newly generated |
| Member 2: equity construction | Frozen weights, purchase allocation, constraints, 96-month history, stress tests and observed evaluation have reproducible code and unit tests | Group-reported acceptance; separate reviewer identity, date and signed review remain unverified |
| Member 3: CAPM, FF3 and QA | Saved 96-month factor data, regression results and 48 PASS / 1 WARN / 0 FAIL pipeline | Group-reported acceptance; independent named review and signed approval remain unverified |
| Integrated memo, deck and submission | Common recommendation and source-linked figures; source, package and SHA256 verification in GitHub Actions | Group-reported agreement; individual sign-offs and actual LMS acknowledgement remain unverified |

The pending sign-off cells in quality_assurance/decision_log.csv are intentionally unchanged. They can be completed only from the actual dated confirmation of each owner/reviewer.

## Original 22 October transmission: what is established

The connected university mailbox contains a message with subject **BFIN Group Assignment Submission**, dated 22 October 2026 at 08:44:53 UTC (15:44:53 Vietnam time). The message includes the attachment `BFIN-Assignment Group 4-22.10.zip` (2,555,738 bytes), describes the attachment as the **first draft** and explicitly asks whether more files or a Moodle upload are needed. An original saved email source record and conditional receipt appear in portfolio_construction/post_freeze_evaluation/evidence. Existing recorded ZIP SHA256: `d54fafc9b39e7fbf374f1c0f29911cd177c537ab1b09ffafa86de6c93a32b2db`. Original-policy PDF and frozen-weights SHA256 identifiers and earlier ZIP CRC32/size comparisons are in the same source record.

Evidence grade: **SENT UNIVERSITY EMAIL DOCUMENTED, NOT AN LMS RECEIPT**. The mailbox attachment is not retrievable through the currently connected attachment reader; no new extraction/hash of the exact emailed members has been claimed. No LMS receipt, instructor reply approving that mode of submission, Moodle confirmation or final-submission acceptance has been independently obtained. A matching email header cannot replace that evidence. Do not change the false acceptance flags in the original evidence JSON without authentic institutional proof.

## JNJ/Kenvue treatment

JNJ's 24 July 2023 release describes a shareholder **option** to exchange all, some or none of their shares. The completed tender results were reported 23 August 2023; only shares accepted through the election were exchanged, with proration for eligible tenders. Under the group's frozen **no voluntary tender, no discretionary exchange** rule, this portfolio retains JNJ and does not add any KVUE position.

Official sources:
- https://www.jnj.com/media-center/press-releases/johnson-johnson-launches-exchange-offer-for-separation-of-kenvue-inc
- https://www.jnj.com/media-center/press-releases/johnson-johnson-announces-final-results-of-exchange-offer-and-finalizes-separation-of-kenvue-inc
- https://www.sec.gov/Archives/edgar/data/200406/000020040623000086/jnj-20230823.htm

A saved-data verification script, portfolio_construction/post_freeze_evaluation/jnj_vendor_check.py, checks the pinned raw Yahoo response, processed adjusted closes, event window, ordinary dividends, and a no-tender close-plus-cash-dividend-reinvestment benchmark. This is a technical sensitivity check: it does not certify actual executed purchases, the vendor's historical adjustment policy, dividend reinvestment timing or an individual human sign-off. Thus the final 2023-2025 comparison remains clearly conditional in the memo.

## Academic integrity and outstanding records

Use the above role description when disclosing material AI involvement; do not minimize AI's role in generating or editing code, data processing, tables, checks or documents. Do not present the machine-built files as untouched manual work. Do not supply forged course acknowledgement, retrospective signatures, reviewer dates or claims of human testing that cannot be individually corroborated.

Still needed for stronger evidence: authenticated LMS submission/acceptance (or explicit written instructor acceptance of email), exact emailed ZIP-member bytes and independent hashes, each named reviewer confirmation if the course requires it, and personal validation of JNJ adjusted-price handling. The officially supplied revised-mandate PDF should be kept alongside the submission evidence when available.
