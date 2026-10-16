# Source verification and assignment controls

GitHub repository: https://github.com/ranaroussi/yfinance
Verified main-branch commit: `5cae563642b59f49adf6a04a5ad6744f8b0e084d` (as retrieved October 16, 2026).
Python API: `yfinance.download(tickers, start, end, interval="1d", auto_adjust=False, actions=True, repair=False, keepna=True, progress=False, threads=False, multi_level_index=True)`.

The inspected upstream `yfinance/multi.py` explicitly defines `start` as inclusive, `end` as exclusive, and exposes the adjustment and corporate-action parameters. The configured estimation fetch is 2014-12-01 to 2023-01-01 (exclusive), which provides the December 2014 starting price required to compute January 2015 returns. Annualized mean is 12 times the monthly arithmetic mean; annualized covariance is 12 times monthly sample covariance. No annualized Sharpe is computed unless monthly RF is separately sourced from Kenneth French.

Case-date eligibility research, corporate-action anomalies, survivorship bias, and provider revisions must be disclosed in the committee memo. The initial decision date remains 2022-12-31 even though the software may be installed in 2026.

The git repository supplies code only; after the user runs the workflow, daily price data arrive from Yahoo Finance. Historical data availability and download success cannot be determined from GitHub code inspection alone.
