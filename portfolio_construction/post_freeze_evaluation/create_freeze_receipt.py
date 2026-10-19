#!/usr/bin/env python3
"""Create locally verified receipt metadata only from ACTUAL course submission evidence.

This script cannot authenticate the learning management system. Never invent the
submission reference, timestamp, PDF path or claim confirmation before upload.
"""
from __future__ import annotations
import argparse,hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
from zoneinfo import ZoneInfo
try:
    from . import evaluate as ev
except ImportError:
    import evaluate as ev


def create_receipt(weights_file,submitted_pdf,submission_reference,submitted_at_hcm,out,now=None):
    pdf=Path(submitted_pdf).resolve();weights=Path(weights_file).resolve();out=Path(out).resolve()
    if not pdf.is_file() or pdf.suffix.lower()!='.pdf':raise ValueError('Use the exact actual submitted PDF bytes')
    if not weights.is_file():raise ValueError('Confirmed weights CSV does not exist')
    if not submission_reference.strip() or submission_reference.strip().upper() in ('TEST','PENDING','TBD','NONE'):
        raise ValueError('A genuine non-placeholder course upload reference is required')
    submitted=ev.dated(submitted_at_hcm,'submitted_at_hcm')
    current=now if now is not None else datetime.now(timezone.utc)
    if current.tzinfo is None:raise ValueError('Current time must be timezone aware')
    if submitted>ev.POLICY_DEADLINE:raise ValueError('Submission after official course deadline')
    if submitted>current.astimezone(ZoneInfo('Asia/Ho_Chi_Minh')):
        raise ValueError('Future-dated submission receipt is forbidden')
    if submitted.date().isoformat()<'2026-10-01':raise ValueError('Submission date inconsistent with assignment calendar')
    if out.exists():raise FileExistsError('Never overwrite original evidence')
    # Copy the actual already-submitted PDF unchanged alongside receipt for portability.
    out.parent.mkdir(parents=True,exist_ok=True)
    frozen_copy=out.parent/'ORIGINAL_SUBMITTED_DECISION_RECORD.pdf'
    if frozen_copy.exists() and frozen_copy.resolve()!=pdf:
        raise FileExistsError('A submitted PDF copy already exists; never overwrite evidence')
    if frozen_copy.resolve()!=pdf:
        shutil.copy2(pdf,frozen_copy)
    if ev.sha(frozen_copy)!=ev.sha(pdf):
        raise IOError('Submission PDF copy changed bytes')
    record={
        'submitted_at_hcm':submitted.isoformat(timespec='seconds'),
        'submission_reference':submission_reference.strip(),
        'submitted_pdf_path':frozen_copy.name,
        'submitted_pdf_sha256':ev.sha(pdf),
        'frozen_weights_sha256':ev.sha(weights),
        'freeze_evidence_note':'User supplied real LMS receipt reference; tool cannot independently authenticate university platform'
    }
    out.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    return record


def cli():
    p=argparse.ArgumentParser(description='Run ONLY after real university submission')
    p.add_argument('--weights',required=True)
    p.add_argument('--submitted-pdf',required=True)
    p.add_argument('--reference',required=True)
    p.add_argument('--submitted-at-hcm',required=True,help='2026-10-22T15:32:00+07:00 actual LMS time, example format only')
    p.add_argument('--out',required=True)
    a=p.parse_args()
    print(json.dumps(create_receipt(a.weights,a.submitted_pdf,a.reference,a.submitted_at_hcm,a.out),indent=2))

if __name__=='__main__':cli()
