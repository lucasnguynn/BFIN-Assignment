# Run BFIN Member 2 via the official yfinance GitHub source

The yfinance GitHub repository contains **software**, not a downloadable archive of our historical returns. Its implementation fetches Yahoo Finance data when executed in a network-capable Python runtime. GitHub's **Actions** runner can provide that runtime, provided your own repository has GitHub Actions enabled and Yahoo permits the requests.

1. Create or use your own private GitHub repository for the BFIN project. Upload the contents of this package **including `.github/workflows/bfin_member2_yfinance.yml`**. Do not upload confidential data to a public repository.
2. Open **Actions** > **BFIN Kappa Member 2 historical data — yfinance** > **Run workflow**. Keep the default estimation start `2015-01`.
3. Confirm the execution jobs: install from pinned upstream commit; run tests; retrieve 13 symbols using `yfinance`; build 96 common 2015–2022 monthly returns; run security statistics and covariance/portfolio comparison. Any failure should be investigated and logged; do not fabricate missing observations.
4. Download the `BFIN-M2-yfinance-evidence-<run>` artifact. GitHub Actions artifacts may be automatically deleted after their retention window. Preserve both the downloaded ZIP and the repository source separately for submission.
5. Review `outputs/qa/github_workflow_gate.json`, `data/source_manifest.csv`, all raw Yahoo pickle responses, and model outputs. A `PASS_TECHNICAL_REAL_DATA_GATES` result means local evidence checks passed; it does not approve investment decisions.
6. Upload the resulting artifact ZIP into the ChatGPT project or share it with Member 3. Only then can quantitative estimates be interpreted and the recommendation considered.

## Alternative: Google Colab or local machine

```bash
python -m pip install -r requirements_github.txt
python src/m2_github_orchestrator.py env --project-root .
python -m pytest -q -p no:cacheprovider tests
python src/m2_data_pipeline.py fetch --partition estimation --project-root .
python src/m2_data_pipeline.py build --partition estimation --project-root . --start-month 2015-01
python src/m2_portfolio_model.py run --project-root .
python src/m2_github_orchestrator.py gate --project-root .
```

The code deliberately does **not** download 2023–2025 prices as part of its initial 2022 policy-selection path. That later dataset is permitted only for separate frozen-strategy evaluation after submission of the actual October 22 policy record.

## Common potential failures

- HTTP 429/Yahoo blocking: preserve failed request logs; retry later; do not invent returns.
- Missing `Adj Close`: investigate `yfinance` output schema and corporate actions; do not silently use non-dividend-adjusted `Close`.
- Missing dividend/split data: inspect saved raw responses, document any correction and rerun from raw.
- One ticker has an incomplete period: the assignment permits at least 60 common observations ending 2022-12 with a predeclared window; any change needs group approval, not an automatic retrospective change.
- No dates after 2022 in the estimation file. The later evaluation file must remain separate.

The implementation pins an official repo commit to make code installation reproducible. Exact resolved versions and archive hashes must still be documented. Its output is research support, not a guarantee of data completeness or investment performance.
