#!/usr/bin/env python3
"""Real post-freeze Yahoo evaluation PREVIEW, until JNJ human price audit/acceptance.

This routine does NOT override the original evaluate.py manual action gate. It
only computes a numerically reproducible, clearly PROVISIONAL 36-month sample
from genuine post-submission raw Yahoo downloads with all integrity checks.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pickle
import sys
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
try:
    from . import evaluate as ev
    from . import retrieve_evaluation_yahoo as dl
except ImportError:
    import evaluate as ev
    import retrieve_evaluation_yahoo as dl

PRIMARY_SOURCES=[
 "https://www.jnj.com/media-center/press-releases/johnson-johnson-launches-exchange-offer-for-separation-of-kenvue-inc",
 "https://www.jnj.com/media-center/press-releases/johnson-johnson-announces-final-results-of-exchange-offer-and-finalizes-separation-of-kenvue-inc"
]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def one_column(frame,col):
    if isinstance(frame.columns,pd.MultiIndex):
        choices=[x for x in frame.columns if col in tuple(map(str,x))]
        if len(choices)!=1:
            raise ValueError("Ambiguous JNJ raw vendor column: {}".format(col))
        return frame[choices[0]]
    if col not in frame.columns:raise ValueError("Missing JNJ raw column {}".format(col))
    return frame[col]

def jnj_numerical_audit(raw):
    with zipfile.ZipFile(raw) as z:
        if "JNJ.pkl" not in z.namelist():
            raise ValueError("No original JNJ raw response")
        # This trusted pickle is created by our own download in the same workflow
        # from documented yfinance responses, not from user-uploaded arbitrary bytes.
        j=pickle.loads(z.read("JNJ.pkl"))
    if not isinstance(j,pd.DataFrame) or j.empty:raise ValueError("JNJ raw frame missing")
    idx=pd.to_datetime(j.index).tz_localize(None).normalize() if j.index.tz is not None else pd.to_datetime(j.index).normalize()
    dates=np.asarray(idx)
    diagnostics={"source":"Archived yfinance JNJ.pkl only",
        "primary_sources":PRIMARY_SOURCES,
        "policy":"NO VOLUNTARY EXCHANGE: keep original JNJ, do not credit KVUE shares",
        "jnj_action_manually_verified":False,
        "reviewer":None,
        "status":"AUTOMATED_VENDOR_EVENT_DIAGNOSTIC_NOT_JNJ_MANUAL_PRICE_AUDIT",
        "split_off_date":"2023-08-23",
        "jnj_exchange_expiration":"2023-08-18"}
    for col in ("Close","Adj Close","Dividends","Stock Splits"):
        try:
            ser=one_column(j,col)
            d=pd.DataFrame({"date":idx,"value":pd.to_numeric(ser,errors="coerce")})
            aug=d[(d.date>=pd.Timestamp("2023-08-15"))&(d.date<=pd.Timestamp("2023-09-01"))]
            vals=[{"date":str(x.date.date()),"value":None if pd.isna(x.value) else float(x.value)} for x in aug.itertuples()]
            diagnostics[col.replace(" ","_").lower()+"_aug_2023"]=vals
        except ValueError:
            if col in ("Close","Adj Close"):raise
            diagnostics[col.replace(" ","_").lower()+"_aug_2023"]=None
    diagnostics["no_voluntary_tender_ruling_based_on_primary_sources"]=True
    diagnostics["actual_adjusted_close_fidelity_verified"]=False
    return diagnostics

def run(root,receipt,prices,source_record,raw_archive,out_dir):
    root=Path(root);out=Path(out_dir)
    proof=json.loads(Path(receipt).read_text())
    if proof.get("evidence_channel")!="UNIVERSITY_EMAIL_SUBMISSION_CC_COPY" or proof.get("instructor_or_lms_acceptance_verified") is not False:
        raise ValueError("Only the explicitly conditional documented October-22 email evidence is supported")
    dl.check_genuine_freeze(root,receipt)
    rec=json.loads(Path(source_record).read_text())
    submitted=ev.dated(proof["submitted_at_hcm"],"submitted_at_hcm")
    if ev.dated(rec["retrieved_at_hcm"],"retrieved_at_hcm")<=submitted:
        raise AssertionError("Evaluated responses were not downloaded AFTER real documented email")
    if sha(prices)!=rec.get("processed_price_csv_sha256") or sha(raw_archive)!=rec.get("raw_archive_sha256"):
        raise AssertionError("Untransformed downloaded responses/processed quote hashes invalid")
    if rec.get("yfinance_version") in ("UNKNOWN","SYNTHETIC_FIXTURE_TEST_ONLY"):
        raise AssertionError("Real yfinance version not present")
    if rec.get("JNJ_action_status") is None:
        raise AssertionError("No action audit status")
    original=ev.read_weights(root/"evidence/decision_weights_confirmed.csv")
    prices_df=pd.read_csv(prices)
    monthly,metrics=ev.compute_buyhold(prices_df,original,require_daily=True)
    if monthly.month.nunique()!=36 or not np.isfinite(monthly.select_dtypes("number")).to_numpy().all():
        raise AssertionError("Unreliable 36-month realized price panel")
    jnj=jnj_numerical_audit(raw_archive)
    metrics.update({
       "evidence_grade":"PROVISIONAL_REAL_YAHOO_DAILY_NOT_FINAL_FROZEN_EVALUATION",
       "data_source":"Raw yfinance 2023-2025 daily original response, retrieved after documented 22 Oct course email",
       "documented_email_submission":True,
       "university_lms_or_instructor_acceptance_verified":False,
       "original_attached_zip_member_bytes_cryptographically_verified":False,
       "JNJ_no_tender_corporate_action_manually_verified":False,
       "portfolio_weights_source_sha256":sha(root/"evidence/decision_weights_confirmed.csv"),
       "raw_market_archive_sha256":sha(raw_archive),
       "processed_market_csv_sha256":sha(prices),
       "reported_monthly_return_count":36,
       "not_usable_as_final_verified_claim_without_manual_JNJ_and_submission_acceptance":True
    })
    out.mkdir(parents=True,exist_ok=False)
    monthly.to_csv(out/"PROVISIONAL observed 2023-2025 monthly growth VTI.csv",index=False,float_format="%.16g")
    (out/"PROVISIONAL observed performance summary.json").write_text(json.dumps(metrics,indent=2)+"\n")
    (out/"JNJ Vendor Audit PENDING.json").write_text(json.dumps(jnj,indent=2)+"\n")
    source={"receipt_sha256":sha(receipt),"raw_market_archive_sha256":sha(raw_archive),
        "market_source_record_sha256":sha(source_record),"monthly_output_sha256":sha(out/"PROVISIONAL observed 2023-2025 monthly growth VTI.csv"),
        "status":"CONDITIONAL_NOT_FINAL","contains_synthetic_prices":False}
    (out/"Data and Evaluation Provenance.json").write_text(json.dumps(source,indent=2)+"\n")
    print("REAL observed price-derived provisional results written; FINAL action-review gate remains UNVERIFIED")
    print(json.dumps(metrics,indent=2))
    return metrics

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for key in ("root","receipt","prices","source-record","raw-archive","out-dir"):
        p.add_argument("--"+key,required=True)
    args=p.parse_args()
    run(args.root,args.receipt,args.prices,args.source_record,args.raw_archive,args.out_dir)
