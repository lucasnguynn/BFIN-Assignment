#!/usr/bin/env python3
"""Inspect local candidate 22-Oct ZIP; never claim a genuine university LMS receipt."""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import zipfile
from decimal import Decimal
from pathlib import Path

ECONOMIC_FIELDS=("approved_policy_id","security","weight_of_growth_sleeve","equity_purchase_USD")

def sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def economic_rows(data:bytes):
    reader=csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
    if not set(ECONOMIC_FIELDS).issubset(reader.fieldnames or []):
        raise ValueError("Weight CSV missing economic policy columns")
    rows=[]; tickers=set()
    for row in reader:
        ticker=row["security"]
        if not ticker or ticker in tickers:
            raise ValueError("Empty or repeated ticker")
        tickers.add(ticker)
        rows.append((row["approved_policy_id"],ticker,
                     Decimal(row["weight_of_growth_sleeve"]),
                     Decimal(row["equity_purchase_USD"])))
    if len(rows)!=12:
        raise ValueError("Exactly twelve original candidate instruments required")
    if abs(sum(r[2] for r in rows)-1)>Decimal("1e-12"):
        raise ValueError("Growth weights must sum to one")
    return sorted(rows,key=lambda x:x[1])

def reconcile(archive:Path,repository_weights:Path):
    archive=Path(archive); repository_weights=Path(repository_weights)
    if not archive.is_file() or not repository_weights.is_file():
        raise FileNotFoundError("Supply local candidate ZIP and GitHub policy CSV")
    with zipfile.ZipFile(archive) as outer:
        if not {"Code and Raw Data.zip","Initial Decision Record.pdf"}.issubset(outer.namelist()):
            raise ValueError("Required candidate archive members absent")
        code=outer.read("Code and Raw Data.zip")
        pdf=outer.read("Initial Decision Record.pdf")
    with zipfile.ZipFile(io.BytesIO(code)) as nested:
        name="evidence/decision_weights_confirmed.csv"
        if nested.namelist().count(name)!=1:
            raise ValueError("Ambiguous or missing original exact-weight file")
        candidate=nested.read(name)
    repository=repository_weights.read_bytes()
    same=economic_rows(candidate)==economic_rows(repository)
    result={"candidate_zip_sha256":sha(archive.read_bytes()),
            "candidate_pdf_sha256":sha(pdf),
            "candidate_weight_sha256":sha(candidate),
            "repository_weight_sha256":sha(repository),
            "weight_bytes_identical":candidate==repository,
            "same_economic_policy":same,
            "difference_is_non_economic_when_true":same and candidate!=repository,
            "lms_receipt_verified":False,
            "status":"LOCAL_CANDIDATE_ONLY_NOT_INSTITUTIONAL_PROOF",
            "instruction":"Check real LMS receipt and exact uploaded file. If these candidate bytes were uploaded, use the exact submitted Code and Raw Data directory as evaluator --root; do not replace its weights with GitHub bytes."}
    if not same:
        result["warning"]="Economic policy differs; human investigation required"
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser(description="Candidate archive versus GitHub weights; never proves LMS submission")
    p.add_argument("--candidate-zip",type=Path,required=True)
    p.add_argument("--repository-weights",type=Path,required=True)
    p.add_argument("--report",type=Path)
    a=p.parse_args(); result=reconcile(a.candidate_zip,a.repository_weights)
    payload=json.dumps(result,indent=2)+"\n"
    print(payload,end="")
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(payload,encoding="utf-8")
    if not result["same_economic_policy"]:
        raise SystemExit(2)
