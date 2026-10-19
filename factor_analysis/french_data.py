"""Kenneth French FF3 monthly factors: retrieval (ONLINE, run once) and parsing (OFFLINE).

Retrieval:  python -m factor_analysis.french_data fetch   -> factor_analysis/data/raw/french/F-F_Research_Data_Factors_CSV.zip
                                                             factor_analysis/data/raw/french/french_source_record.json
Parsing is imported by factor_analysis/models.py and never touches the network.

Nothing here fabricates data: if the download or parse fails, an error is raised and the QA gate
stays BLOCKED/FAIL.
"""
from __future__ import annotations
import datetime
import hashlib
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip"
DATASET = "F-F_Research_Data_Factors (monthly)"
RAW_ZIP = "F-F_Research_Data_Factors_CSV.zip"
RECORD = "french_source_record.json"
START, END = "201501", "202212"


def fetch(root):
    raw_dir = Path(root) / "factor_analysis" / "data" / "raw" / "french"
    raw_dir.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (BFIN WS2026 academic retrieval)"})
    with urllib.request.urlopen(req, timeout=60) as reply:
        raw = reply.read()
        headers = {k: v for k, v in reply.headers.items()}
        status = reply.status
    zp = raw_dir / RAW_ZIP
    zp.write_bytes(raw)  # untransformed bytes
    rec = {
        "source_name": "Kenneth R. French Data Library", "download_url": URL, "dataset": DATASET,
        "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "http_status": status, "http_last_modified": headers.get("Last-Modified", ""),
        "http_content_length": headers.get("Content-Length", ""), "size_bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(), "retrieval_code": "factor_analysis/french_data.py fetch (urllib)",
        "requested_window_used_in_analysis": "2015-01..2022-12 (file holds full history)",
        "note": "Latest vintage downloaded in 2026; may include revisions vs. the 31 Dec 2022 vintage.",
    }
    (raw_dir / RECORD).write_text(json.dumps(rec, indent=2) + "\n")
    print("saved", zp, rec["sha256"])
    return zp


def parse_ff3_zip(zip_path):
    """Return (DataFrame[month, Mkt-RF, SMB, HML, RF] in DECIMALS for 2015-01..2022-12, header_text)."""
    with zipfile.ZipFile(zip_path) as z:
        csvs = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(csvs) != 1:
            raise ValueError(f"expected exactly one CSV in the French archive, found {z.namelist()}")
        text = z.read(csvs[0]).decode("latin1")
    lines = text.splitlines()
    hdr = next((i for i, ln in enumerate(lines)
                if [c.strip() for c in ln.split(",")][:5] == ["", "Mkt-RF", "SMB", "HML", "RF"]), None)
    if hdr is None:
        raise ValueError("monthly header ',Mkt-RF,SMB,HML,RF' not found")
    rows = []
    for ln in lines[hdr + 1:]:
        bits = [b.strip() for b in ln.split(",")]
        if len(bits) >= 5 and len(bits[0]) == 6 and bits[0].isdigit():
            rows.append(bits[:5])
        elif rows:
            break  # end of monthly block (annual block follows)
    df = pd.DataFrame(rows, columns=["yyyymm", "Mkt-RF", "SMB", "HML", "RF"])
    df = df[(df.yyyymm >= START) & (df.yyyymm <= END)].copy()
    for c in ["Mkt-RF", "SMB", "HML", "RF"]:
        df[c] = df[c].astype(float)
    if (df[["Mkt-RF", "SMB", "HML", "RF"]] <= -99.0).any().any():  # test on RAW percent values, before scaling
        raise ValueError("French missing-value sentinel (-99.99) found in the window")
    for c in ["Mkt-RF", "SMB", "HML", "RF"]:
        df[c] = df[c] / 100.0  # percent -> decimal, explicit
    df.insert(0, "month", df.yyyymm.str[:4] + "-" + df.yyyymm.str[4:])
    df = df.drop(columns="yyyymm").reset_index(drop=True)
    if len(df) != 96 or df.month.iloc[0] != "2015-01" or df.month.iloc[-1] != "2022-12":
        raise ValueError(f"unexpected factor window: {len(df)} rows")
    return df, "\n".join(lines[:hdr])


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    if len(sys.argv) > 1 and sys.argv[1] == "fetch":
        fetch(root)
    else:
        print(__doc__)
