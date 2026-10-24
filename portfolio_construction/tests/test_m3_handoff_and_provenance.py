"""M2→M3 and policy-byte audit: synthetic ZIP fixtures, no fabricated receipt."""
import importlib.util
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
GATE=ROOT/"portfolio_construction/post_freeze_evaluation/reconcile_submission.py"
S=importlib.util.spec_from_file_location("submission_gate",GATE)
gate=importlib.util.module_from_spec(S);S.loader.exec_module(gate)
HANDOFF=ROOT/"portfolio_construction/revised_mandate/m3_handoff.py"
sys.path.insert(0,str(HANDOFF.parent))
T=importlib.util.spec_from_file_location("m3_handoff",HANDOFF)
handoff=importlib.util.module_from_spec(T);T.loader.exec_module(handoff)

class M2NextEvidenceChecks(unittest.TestCase):
    def make_bundle(self,d,weight_bytes):
        blob=io.BytesIO()
        with zipfile.ZipFile(blob,"w") as nested:
            nested.writestr("evidence/decision_weights_confirmed.csv",weight_bytes)
        candidate=Path(d)/"synthetic.zip"
        with zipfile.ZipFile(candidate,"w") as outer:
            outer.writestr("Code and Raw Data.zip",blob.getvalue())
            outer.writestr("Initial Decision Record.pdf",b"SYNTHETIC PDF PLACEHOLDER, NOT REAL LMS")
        return candidate

    def test_metadata_only_variation_is_not_lms_proof(self):
        original=(ROOT/"portfolio_construction/evidence/decision_weights_confirmed.csv").read_bytes()
        altered=original.replace(b"CONTENT_CONFIRMED_BY_USER_2026_10_17",
                                 b"SELECTED_FOR_2022_CASE_DECISION")
        self.assertNotEqual(original,altered)
        with tempfile.TemporaryDirectory() as d:
            candidate=self.make_bundle(d,altered)
            result=gate.reconcile(candidate,
                      ROOT/"portfolio_construction/evidence/decision_weights_confirmed.csv")
        self.assertTrue(result["same_economic_policy"])
        self.assertFalse(result["weight_bytes_identical"])
        self.assertFalse(result["lms_receipt_verified"])
        self.assertNotEqual(result["candidate_weight_sha256"],result["repository_weight_sha256"])

    def test_tampered_economic_weights_rejected(self):
        original=(ROOT/"portfolio_construction/evidence/decision_weights_confirmed.csv").read_bytes()
        altered=original.replace(b"0.150000000000000",b"0.140000000000000",1)
        with tempfile.TemporaryDirectory() as d:
            candidate=self.make_bundle(d,altered)
            with self.assertRaises(ValueError):
                gate.reconcile(candidate,ROOT/"portfolio_construction/evidence/decision_weights_confirmed.csv")

    def test_m3_handoff_unique_15_times_96(self):
        with tempfile.TemporaryDirectory() as d:
            manifest=handoff.build(d)
            panel=pd.read_csv(Path(d)/"M3 Static Returns Long.csv")
            registry=pd.read_csv(Path(d)/"M3 Scenario Registry.csv")
            allocations=pd.read_csv(Path(d)/"M3 Exact Portfolio Weights.csv")
            self.assertEqual(manifest["scenario_count"],15)
            self.assertEqual(manifest["long_panel_rows"],1440)
            self.assertEqual(panel.shape,(1440,3))
            self.assertEqual(len(registry),15)
            self.assertEqual(len(allocations),180)
            self.assertFalse(panel.duplicated(["scenario_id","month"]).any())
            self.assertEqual(panel.month.min(),"2015-01")
            self.assertEqual(panel.month.max(),"2022-12")
            self.assertTrue((registry.months==96).all())
            self.assertFalse(manifest["evaluation_2023_2025_included"])
            import hashlib, json
            baseline={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(d).iterdir() if p.is_file()}
            next_manifest=handoff.build(d)
            after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(d).iterdir() if p.is_file()}
            self.assertEqual(baseline,after,"Second offline build must regenerate byte-identical outputs")
            self.assertNotIn("M3 Handoff Manifest.json",next_manifest["handoff_shas"])
            for name,digest in next_manifest["handoff_shas"].items():
                self.assertEqual(digest,after[name])
            self.assertEqual(manifest,next_manifest)

if __name__=="__main__":
    unittest.main()
