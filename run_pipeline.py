#!/usr/bin/env python3
"""BFIN Kappa Foundation - end-to-end offline pipeline.   python run_pipeline.py
Steps: source manifest -> QA gates (bond funding, portfolio rebuild, decision reversal, $12m, data, temporal, French raw) -> factor models
(if French raw data are present) -> quality_assurance/qa_report.json.  No network access is used anywhere in this script.
Exit code: 0 all PASS (WARN allowed) | 2 BLOCKED present | 1 FAIL present."""
from __future__ import annotations
import datetime, json, platform, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import numpy, pandas, scipy
from factor_analysis import models as factor_models
from quality_assurance import checks as qa_checks, decision_reversal, manifest as source_manifest

def main():
    manifest = source_manifest.build(ROOT)
    checks = []
    checks += qa_checks.check_weights(ROOT)
    checks += qa_checks.check_12m(ROOT)
    checks += qa_checks.check_bond_funding(ROOT)
    checks += qa_checks.check_data(ROOT)
    checks += qa_checks.check_portfolio_rebuild(ROOT)
    checks += decision_reversal.check_decision_reversal(ROOT)
    fr = qa_checks.check_french(ROOT)
    checks += fr
    factor_status = "BLOCKED"
    if all(c["status"] == "PASS" for c in fr):
        try:
            coef, cmp_, dg = factor_models.run_factor_models(ROOT)
            factor_status = "PASS"
            checks.append(dict(id="FACTOR.models_estimated", status="PASS",
                               detail=f"{len(coef)} regressions (CAPM+FF3) over {coef.strategy_or_ticker.nunique()} subjects, n=96; outputs in factor_analysis/outputs/"))
        except Exception as e:
            factor_status = "FAIL"
            checks.append(dict(id="FACTOR.models_estimated", status="FAIL", detail=repr(e)))
    else:
        factor_models.preliminary_vti_proxy(ROOT)
        checks.append(dict(id="FACTOR.models_estimated", status="BLOCKED",
                           detail="Requires raw French factors. Only factor_analysis/outputs/PRELIMINARY_vti_proxy_market_model.csv written (VTI proxy, raw returns; not a deliverable)."))
    counts = {s: sum(c["status"] == s for c in checks) for s in ("PASS", "WARN", "FAIL", "BLOCKED")}
    verdict = "NO-GO" if counts["FAIL"] else ("NO-GO (blocked: factor evidence missing)" if counts["BLOCKED"] else "GO")
    report = dict(generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), verdict=verdict, counts=counts,
                  environment=dict(python=platform.python_version(), numpy=numpy.__version__, pandas=pandas.__version__, scipy=scipy.__version__),
                  checks=checks)
    (ROOT / "quality_assurance" / "qa_report.json").write_text(json.dumps(report, indent=2, default=str) + "\n")
    for c in checks:
        print(f"[{c['status']:7}] {c['id']}")
    print("VERDICT:", verdict, counts)
    return 1 if counts["FAIL"] else (2 if counts["BLOCKED"] else 0)

if __name__ == "__main__":
    sys.exit(main())
