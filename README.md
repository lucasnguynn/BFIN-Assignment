# Kappa Foundation - Liability-First, Risk-Constrained Investment Policy

**BFIN WS2026 - Group Assignment** | 
Case decision date: 31 December 2022 

This repository contains the reproducible analysis behind the group's investment-policy recommendation for the Kappa Foundation
(USD 12.0m initial assets, USD 2.4m due 2024, USD 3.6m due 2027, and a 2030 goal of preserving USD 8.0m of December 2022 purchasing power).
The package is rebuilt **offline** from saved raw data; no figure depends on a live download.

## Repository structure

```
.
├── README.md
├── requirements.txt                 pinned environment for the offline rebuild
├── run_pipeline.py                  single entry point: source manifest -> QA gates -> factor models -> QA report
│
├── bond_funding/                    Workstream 2 - bond valuation, funding and rate risk
│   └── Kappa_Bond_Funding_Model.xlsx      tabs: DATA & ASSUMPTIONS | BOND & FUNDING ANALYSIS | RATE RISK & DECISION
│
├── portfolio_construction/          Workstreams 3, 5, 6 - equity universe, portfolio design, policy comparison, frozen evaluation
│   ├── data/raw/                          untouched Yahoo Finance responses (SHA-256 pinned)
│   ├── data/processed/                    monthly simple returns, 2015-01 to 2022-12 (decimals)
│   ├── evidence/                          frozen weights, 2022 eligibility record, source records, pinned funding workbook
│   ├── src/                               retrieval, rebuild and portfolio analytics
│   ├── outputs/                           regenerated result tables (CSV)
│   ├── notebooks/portfolio_evaluation.ipynb
│   ├── docs/                              Initial Decision Record (.docx/.pdf), conventions, limitations, contribution statement
│   ├── post_freeze_evaluation/            2023-2025 evaluation code - NOT to be run before the 22 Oct submission is frozen
│   ├── tests/                             unit tests (synthetic fixtures only)
│   └── qa/rebuild_report.json
│
├── factor_analysis/                 Workstream 4 - market-only (CAPM) and Fama-French three-factor regressions
│   ├── ols.py  french_data.py  models.py
│   ├── data/raw/french/                   Kenneth French factor file (raw bytes + source record) - see Step 2
│   ├── outputs/                           factor_coefficients.csv, factor_model_comparison.csv, factor_diagnostics.csv, factor_exposures.png
│   ├── docs/eta_theta_assessment.md
│   └── tests/test_factor_analysis.py
│
├── quality_assurance/               Workstream 7 - cross-workstream verification and provenance
│   ├── checks.py  manifest.py
│   ├── qa_report.json                     machine-generated gate results
│   ├── source_manifest.csv                provenance of every raw input
│   └── cross_workstream_review.md
│
└── .github/                         CI workflow, factor-analysis workflow, pull-request template
```

## Reproducing the results

1. **Environment** (Python 3.12):
   `python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt`
2. **Retrieve the Kenneth French factors (online, once):**
   `python -m factor_analysis.french_data fetch`
   Saves the original ZIP plus `french_source_record.json` (URL, UTC time, HTTP headers, size, SHA-256) to `factor_analysis/data/raw/french/`.
   If the download fails, keep the error text and report it as a failed retrieval; do not enter factor values by hand.
3. **Rebuild (offline):** `python run_pipeline.py`
   Exit code 0 = all gates PASS (WARN allowed); 1 = a gate FAILED; 2 = a required input is BLOCKED.
   Writes `quality_assurance/qa_report.json`, `quality_assurance/source_manifest.csv` and `factor_analysis/outputs/*`.
4. **Unit tests:**
   `python -m unittest discover -s portfolio_construction/tests`
   `python -m unittest discover -s factor_analysis/tests -v`

## Current status

| Item | Status |
|---|---|
| Bond funding (YTM, duration, convexity, spot curve, 2024/2027 coverage) | Independently recomputed - PASS |
| Full allocation reconciles to USD 12,000,000.00 | PASS (exact decimal arithmetic) |
| Portfolio rebuild from raw Yahoo data, shipped outputs reproduced | PASS |
| Factor regressions (CAPM, FF3) | **Pending** - French raw data not yet retrieved (Step 2) |
| Overall verdict | NO-GO (blocked: factor evidence missing) until Steps 2-3 are completed |

Open points are listed in `quality_assurance/cross_workstream_review.md`.

## Methodological conventions

- Monthly simple total returns in decimals; estimation window 2015-01 to 2022-12 (96 observations); no observation after 2022-12 enters the 2022 decision.
- Growth-sleeve series for 2015-2022 uses constant (static) weights; the 2023-2025 buy-and-hold evaluation is a separate object.
- Excess returns use the French risk-free rate; French percentages are converted to decimals explicitly and the -99.99 sentinel aborts the run.
- The Lecture 7 factor-model menu is still to be verified; FF3 is assumed. Only the `MODELS` dictionary in `factor_analysis/models.py` and the French file name would change.
- Raw files are never edited by hand and missing observations are never filled.

## Collaboration rules

- Work on a feature branch and open a pull request; the reviewer must differ from the author. Protect `main` (pull request and green CI required).
- Any change to weights, funding amounts, universe, estimation dates or policy rules is versioned and recorded in the decision log.
- The 22 October submission is preserved intact; later changes are logged with timestamp, prior and new decision, source of change and quantified impact.
