## Final group submission

The current committee memo (PDF and Word), 17-slide presentation (PDF and PowerPoint), decision record, full analysis archive and single group ZIP are in **[Final Submission](Final%20Submission/)**. This folder is the reader-facing handoff; the original model and raw-source folders remain available below. All results are case-date scenarios except the separately labeled 2023 to 2025 observed equity evaluation. Human signatures and institutional acceptance cannot be inferred from CI.

## Portfolio files for the final assignment

The portfolio part of our submission is in **[Portfolio Final](portfolio_construction/Portfolio%20Final/)**. Read **Portfolio Report.pdf** first; use **Portfolio Report.docx** to edit, **Results.xlsx** to inspect nine sheets of calculated outputs, and **Sources** for the dated original Yahoo responses and evidence. Results.xlsx is an exported results workbook, not a live formula-based equity optimizer; rerun the included Python files to recalculate results. A single **Portfolio Files.zip** contains the same handoff files.

The original 2022 decision, revised funding code and factor analysis remain in their existing repository folders. The final Analysis.zip now also includes the memo Markdown and presentation-building scripts. After extracting Final Submission.zip and its Analysis.zip, run `python "Final Submission/build_final.py" --rebuild-offline` from the extracted project root with Python 3.12 and the supplied requirements to regenerate the data checks, reader files, memo, slides and archives without live downloads.

The archived Yahoo results are reproducible. A dated university email containing the group's first draft ZIP was confirmed directly; the message asks whether Moodle upload is required, so LMS/instructor acceptance and exact emailed ZIP-member SHA256s remain unverified. The group reports collective agreement on principal matching and the frozen equity choice. A named Member 2 review of Member 1's analysis is already recorded; individual sign-offs on the other workstreams have not been authenticated. The evidence/AI role distinction is documented in `quality_assurance/Group Review and AI Use.md`, and JNJ vendor checks are separate from the confirmed issuer-event interpretation.

---

# Kappa Foundation - Liability-First, Risk-Constrained Investment Policy

**BFIN WS2026 - Group Assignment (Group 4)**
Case decision date: 31 December 2022 | Package: initial submission 22 October 2026 (preserved) plus revised-mandate material for the final submission, 29 October 2026

This repository contains the reproducible analysis behind the group's investment-policy recommendation for the Kappa Foundation
(USD 12.0m initial assets, USD 2.4m due 2024, USD 3.6m due 2027, and a 2030 goal of preserving USD 8.0m of December 2022 purchasing power).
The package is rebuilt **offline** from saved raw data; no figure depends on a live download.

## Contents of the 22 October submission

| Required item | Location |
|---|---|
| Initial decision record (two pages) | `portfolio_construction/docs/Kappa Foundation- Initial Decision.pdf` (editable source: `.docx`, same folder) |
| Working Python file | `run_pipeline.py` (single entry point), with the modules under `portfolio_construction/src/`, `factor_analysis/` and `quality_assurance/` |
| Dated data record | `portfolio_construction/evidence/yahoo_source_record.csv`, `portfolio_construction/evidence/yahoo_original_yfinance_manifest.csv`, `factor_analysis/data/raw/french/french_source_record.json`, `quality_assurance/source_manifest.csv` |
| Frozen policy weights | `portfolio_construction/evidence/decision_weights_confirmed.csv` |

The committee memo, slide deck, contribution statement and decision log belong to the later submissions and are not part of this package.

## Repository structure

```
.
├── README.md
├── requirements.txt                 pinned environment for the offline rebuild
├── run_pipeline.py                  single entry point: source manifest -> QA gates -> factor models -> QA report
│
├── bond_funding/                    Bond valuation, funding and rate risk
│   ├── Kappa_Bond_Funding_Model.xlsx      tabs: DATA & ASSUMPTIONS | BOND & FUNDING ANALYSIS | RATE RISK & DECISION
│   └── notebooks/bond_funding_analysis.ipynb   executed notebook: YTM, spot curve, duration/convexity, funding candidates, rate scenarios, 2030 hurdle; cross-checked against the workbook
│
├── portfolio_construction/          Equity universe, portfolio design, policy comparison, frozen evaluation rule
│   ├── data/raw/                          untouched Yahoo Finance responses (SHA-256 pinned)
│   ├── data/processed/                    monthly simple returns, 2015-01 to 2022-12 (decimals)
│   ├── evidence/                          frozen weights, 2022 eligibility record, source records, pinned funding workbook
│   ├── src/                               retrieval, rebuild and portfolio analytics
│   ├── outputs/                           regenerated result tables (CSV)
│   ├── notebooks/portfolio_evaluation.ipynb
│   ├── docs/                              Initial Decision Record (.pdf/.docx), evaluation conventions, risk and valuation rules,
│   │                                      data limitations and AI disclosure, case-date source verification
│   ├── post_freeze_evaluation/            2023-2025 evaluation code - NOT to be run before the 22 Oct submission is frozen
│   ├── tests/                             unit tests (synthetic fixtures only)
│   └── qa/rebuild_report.json
│
├── factor_analysis/                 Market-only (CAPM) and Fama-French three-factor regressions
│   ├── ols.py  french_data.py  models.py  figures.py
│   ├── data/raw/french/                   Kenneth French factor file (raw bytes + source record)
│   ├── outputs/                           factor_coefficients.csv, factor_model_comparison.csv, factor_diagnostics.csv, factor_exposures.png
│   │   └── figures/                       alpha, adjusted R-squared and actual-versus-fitted figures (generated by run_pipeline.py)
│   ├── notebooks/factor_analysis.ipynb    executed notebook: re-estimation, tables, figures and attribution; checks reproduction of the committed results
│   ├── docs/eta_theta_assessment.md
│   └── tests/test_factor_analysis.py
│
├── quality_assurance/               Threshold re-confirmation, cross-checks, provenance
│   ├── checks.py  manifest.py  decision_reversal.py
│   ├── qa_report.json                     machine-generated gate results
│   ├── source_manifest.csv                provenance of every raw input
│   ├── decision_threshold_reconfirmation.csv
│   ├── decision_threshold_reoptimization_contrast.csv
│   ├── decision_reversal_note.md          wording and supporting figures for the reversal-threshold section of the memo
│   ├── cross_workstream_review.md
│   └── tests/
│
└── .github/                         CI workflow, factor-analysis workflow, pull-request template
```

## Reproducing the results

1. **Environment** (Python 3.12):
   `python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt`
2. **Yahoo Finance data:** the original yfinance responses are archived in `portfolio_construction/data/raw/yfinance_estimation_2015_2022.zip`
   (SHA-256 recorded in `portfolio_construction/evidence/yahoo_source_record.csv`). The retrieval code is `portfolio_construction/src/yahoo_retrieval_original.py`.
   Do not re-download unless the archive is missing: a new download is a later data vintage and would change the recorded hash.
3. **Kenneth French factors:** the original file is archived in `factor_analysis/data/raw/french/` together with
   `french_source_record.json` (URL, UTC time, HTTP status, size, SHA-256). The retrieval code is `python -m factor_analysis.french_data fetch`;
   run it only if the file is missing. If a download fails, keep the error text and report it as a failed retrieval; do not enter factor values by hand.
4. **Rebuild (offline):** `python run_pipeline.py`
   Exit code 0 = all gates PASS (WARN allowed); 1 = a gate FAILED; 2 = a required input is BLOCKED.
   Writes `quality_assurance/qa_report.json`, `quality_assurance/source_manifest.csv`, the two `decision_threshold_*.csv` files
   and `factor_analysis/outputs/*` (result tables and figures).
5. **Unit tests:**
   `python -m unittest discover -s portfolio_construction/tests`
   `python -m unittest discover -s factor_analysis/tests`
   `python -m unittest discover -s quality_assurance/tests`

## Current status

`quality_assurance/qa_report.json` is the authoritative record of the last full run of `run_pipeline.py` (27 October 2026: GO, 48 PASS, 1 WARN, 0 FAIL); re-run the pipeline before submission and confirm the verdict there. The consequential decision log is `quality_assurance/decision_log.csv` and the exhibit-to-generator map is `quality_assurance/memo_assets_manifest.csv`.

| Item | What is checked |
|---|---|
| Bond funding | YTM, duration, convexity, spot curve and 2024/2027 coverage recomputed independently |
| Full allocation | Reconciles to USD 12,000,000.00 (exact decimal arithmetic) |
| Portfolio rebuild | Shipped outputs reproduced from the raw Yahoo data |
| Decision-reversal thresholds | lambda* = 0.0842 and A* = 8.91 re-derived independently; valid only while the two weight vectors are held fixed |
| Factor regressions | CAPM and FF3; 11 subjects, 22 regressions, n = 96 |
| Temporal integrity | No observation after 2022-12 enters the 2022 decision |
| Revised mandate | USD 6.0m total unchanged; USD 12m reconciles in all three funding scenarios; both revised plans cover 2024, 2025 and 2027; frozen growth series, and so all factor estimates, unchanged (`quality_assurance/revised_mandate_checks.py`; `factor_analysis/revised_mandate_factors.py`) |

Known WARN items concern the bond funding workbook (a presentation label in Candidate B, and a byte-level difference between the original workbook
and the copy pinned by the portfolio rebuild; cell values and formulas are identical). Details are in `quality_assurance/cross_workstream_review.md`.

## Methodological conventions

- Monthly simple total returns in decimals; estimation window 2015-01 to 2022-12 (96 observations); no observation after 2022-12 enters the 2022 decision.
- Growth-sleeve series for 2015-2022 uses constant (static) weights; the 2023-2025 buy-and-hold evaluation is a separate object.
- Excess returns use the French risk-free rate; French percentages are converted to decimals explicitly and the -99.99 sentinel aborts the run.
- The three-factor model (FF3) is used as the multifactor specification (Fama-French three-factor regression, Lecture 7). The Carhart four-factor and five-factor models are not estimated; adding them would change only the `MODELS` dictionary in `factor_analysis/models.py` and the French file name.
- Utility is U = F * E(r) - (A / 2) * F^2 * Var(r), with F the share of the USD 12m invested in equities. The reversal thresholds compare two fixed allocations; they are not re-optimised switching points.
- Data vintage: Yahoo and French series were retrieved in October 2026 and may include revisions made after 31 December 2022. Security selection is retrospective; see `portfolio_construction/docs/DATA_LIMITATIONS_AND_AI.md`.
- Raw files are never edited by hand and missing observations are never filled.

## Freeze and later submissions

- The 22 October submission is preserved intact. Weights, funding amounts, universe, estimation dates and policy rules are frozen in it.
- `portfolio_construction/post_freeze_evaluation/` contains the 2023-2025 evaluation code and blank templates. Do **not** run it on observed 2023-2025 prices until the submission has been made and a freeze receipt has been created with the genuine submission timestamp (see the README in that folder).
- The bond-funding decision log is available at `quality_assurance/Decision_Log_Bond_Funding.docx`. It records the funding decisions, alternatives and supporting evidence. Decisions from the other workstreams should be incorporated into the group decision log.

## Collaboration rules

- Work on a feature branch and open a pull request; the reviewer must differ from the author. Protect `main` (pull request and green CI required).
- Material AI assistance and the checks performed are disclosed in `portfolio_construction/docs/DATA_LIMITATIONS_AND_AI.md`; every member must be able to explain the analysis submitted under their name.

## Notebooks

`bond_funding/notebooks/bond_funding_analysis.ipynb` and `factor_analysis/notebooks/factor_analysis.ipynb` are delivered with their outputs.
Both run offline from the saved files in this repository and fail loudly if a result differs from the workbook (bond notebook) or from the committed result tables (factor notebook).
`run_pipeline.py` verifies that every code cell has been executed and shows no error output (see `NOTEBOOK.*` in `quality_assurance/qa_report.json`).
To re-execute a notebook, open it in Codespaces or VS Code, select the Python 3 kernel (`pip install ipykernel` if prompted) and choose Run All, then commit the refreshed file.

## Portfolio review for the revised trustee plan

Read [Portfolio Review](portfolio_construction/Portfolio%20Review.md) for our equity allocation, the two revised bond funding choices and the actual 2023 to 2025 test against VTI. The original 22 October investment decision is left unchanged. We have not assumed university acceptance of the original email or a human sign-off.

Rebuild the supporting models and tests from the repository root:

```bash
python -m pip install -r requirements.txt
python portfolio_construction/revised_mandate/m1_integration.py
python portfolio_construction/revised_mandate/policy_sensitivity.py
python portfolio_construction/revised_mandate/m3_handoff.py
python -m unittest discover -s portfolio_construction/tests
python run_pipeline.py
```

The observed Yahoo data are archived with source hashes in the dated [GitHub Actions artifact](https://github.com/lucasnguynn/BFIN-Assignment/actions/runs/40093744756/artifacts/12560420593). The cleaned reader-facing handoff is a short report and a workbook with nine tabs; the model scripts are kept separately for checks. This is portfolio material for the group, not the complete final group submission.
