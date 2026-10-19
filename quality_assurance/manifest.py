"""Build source_manifest.csv (framework template B1) from the archived Yahoo manifest plus the other project sources."""
from __future__ import annotations
import io, json, zipfile
from pathlib import Path
import pandas as pd

COLS = ["source_name", "download_url", "retrieval_datetime", "ticker_or_dataset", "requested_start", "requested_end",
        "frequency", "yfinance_args_or_factor_archive", "package_version", "raw_filepath", "file_sha256",
        "missing_data_notes", "failures_and_resolution", "owner", "status"]


def build(root):
    root = Path(root)
    z = root / "portfolio_construction/data/raw/yfinance_estimation_2015_2022.zip"
    with zipfile.ZipFile(z) as zf:
        m = pd.read_csv(io.BytesIO(zf.read("data/source_manifest.csv")))
    m = m[m.partition == "estimation"].copy()
    m["owner"] = "Portfolio construction workstream"
    m["raw_filepath"] = "portfolio_construction/data/raw/yfinance_estimation_2015_2022.zip::" + m.raw_filepath
    m["missing_data_notes"] = "none logged by the retrieval step (no fills); Yahoo Adj Close is vendor-revised, retrieved 2026"
    m["failures_and_resolution"] = "none"
    rows = [m[COLS]]
    import hashlib
    def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    extra = [
        dict(source_name="Yahoo archive container (13 Yahoo responses + processed panel)", download_url="n/a (local archive)",
             retrieval_datetime="2026-10-16T16:52Z (archived responses)", ticker_or_dataset="yfinance_estimation_2015_2022.zip",
             requested_start="2014-12-01", requested_end="2023-01-01 (exclusive)", frequency="1d",
             yfinance_args_or_factor_archive="see per-ticker rows", package_version="pandas 2.3.3; yfinance 1.7.0 (at retrieval)",
             raw_filepath="portfolio_construction/data/raw/yfinance_estimation_2015_2022.zip", file_sha256=sha(z),
             missing_data_notes="", failures_and_resolution="", owner="Portfolio construction workstream", status="OK"),
        dict(source_name="Bond funding workbook (original file)", download_url="n/a (group file)", retrieval_datetime="received 2026-10-19",
             ticker_or_dataset="Copy_of_BFIN_THAO_AN_FIXED.xlsx", requested_start="", requested_end="", frequency="n/a",
             yfinance_args_or_factor_archive="case bond quotes typed from official brief Exhibits 1-2", package_version="openpyxl 3.1.5 (read)",
             raw_filepath="bond_funding/Kappa_Bond_Funding_Model.xlsx", file_sha256=sha(root / "bond_funding/Kappa_Bond_Funding_Model.xlsx"),
             missing_data_notes="", failures_and_resolution="differs in bytes (not cell content) from the copy pinned by the portfolio rebuild", owner="Bond funding workstream", status="OK"),
        dict(source_name="Bond funding workbook (copy pinned by the portfolio rebuild)", download_url="n/a (group file)", retrieval_datetime="2026-10-16",
             ticker_or_dataset="bond_funding_model_pinned.xlsx", requested_start="", requested_end="", frequency="n/a",
             yfinance_args_or_factor_archive="", package_version="", raw_filepath="portfolio_construction/evidence/bond_funding_model_pinned.xlsx",
             file_sha256=sha(root / "portfolio_construction/evidence/bond_funding_model_pinned.xlsx"), missing_data_notes="", failures_and_resolution="", owner="Bond funding workstream", status="OK"),
    ]
    fz = root / "factor_analysis/data/raw/french/F-F_Research_Data_Factors_CSV.zip"
    rec = root / "factor_analysis/data/raw/french/french_source_record.json"
    if fz.exists() and rec.exists():
        r = json.loads(rec.read_text())
        extra.append(dict(source_name=r["source_name"], download_url=r["download_url"], retrieval_datetime=r["retrieved_utc"],
                          ticker_or_dataset=r["dataset"], requested_start="2015-01", requested_end="2022-12", frequency="monthly",
                          yfinance_args_or_factor_archive="urllib GET of original ZIP; Last-Modified=" + r.get("http_last_modified", ""),
                          package_version="python stdlib urllib", raw_filepath="factor_analysis/data/raw/french/" + fz.name, file_sha256=sha(fz),
                          missing_data_notes="", failures_and_resolution="", owner="Factor analysis workstream", status="OK"))
    else:
        extra.append(dict(source_name="Kenneth R. French Data Library", download_url="https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip",
                          retrieval_datetime="", ticker_or_dataset="F-F_Research_Data_Factors (monthly)", requested_start="2015-01", requested_end="2022-12",
                          frequency="monthly", yfinance_args_or_factor_archive="to be retrieved with: python -m factor_analysis.french_data fetch",
                          package_version="", raw_filepath="factor_analysis/data/raw/french/F-F_Research_Data_Factors_CSV.zip", file_sha256="",
                          missing_data_notes="", failures_and_resolution="NOT YET RETRIEVED: build environment had no route to mba.tuck.dartmouth.edu (outside egress allow-list). No data substituted.",
                          owner="Factor analysis workstream", status="PENDING"))
    df = pd.concat(rows + [pd.DataFrame(extra)], ignore_index=True)[COLS]
    df.to_csv(root / "quality_assurance" / "source_manifest.csv", index=False)
    return df
