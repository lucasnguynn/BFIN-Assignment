import csv, tempfile, shutil, unittest, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from verify_case_date_sources import validate
class TestCaseDateEvidence(unittest.TestCase):
 def test_case_date_evidence(self):
  r=validate(ROOT);self.assertEqual('PASS',r['status']);self.assertEqual(13,r['ticker_count'])
  self.assertEqual('INCOMPLETE',r['raw_sec_byte_archival'])
 def test_zero_post_2022_source_dates(self):
  with (ROOT/'evidence/SEC_CASE_DATE_WEB_VERIFICATION_20261018.csv').open() as f:
   rows=list(csv.DictReader(f))
  self.assertTrue(all(r['filing_date_as_recorded']<='2022-12-31' for r in rows))
 def test_false_archival_is_detected(self):
  with tempfile.TemporaryDirectory() as tmp:
   q=Path(tmp);(q/'evidence').mkdir();(q/'data/raw').mkdir(parents=True)
   name='SEC_CASE_DATE_WEB_VERIFICATION_20261018.csv'
   s=(ROOT/'evidence'/name).read_text();(q/'evidence'/name).write_text(s.replace('NO,','YES,',1))
   shutil.copy2(ROOT/'data/raw/yfinance_estimation_2015_2022.zip',q/'data/raw/yfinance_estimation_2015_2022.zip')
   r=validate(q);self.assertEqual('FAIL',r['status'])
 def test_mutated_future_date_is_detected(self):
  with tempfile.TemporaryDirectory() as tmp:
   q=Path(tmp);(q/'evidence').mkdir();(q/'data/raw').mkdir(parents=True)
   name='SEC_CASE_DATE_WEB_VERIFICATION_20261018.csv'
   s=(ROOT/'evidence'/name).read_text();(q/'evidence'/name).write_text(s.replace('2022-10-28','2024-10-28',1))
   shutil.copy2(ROOT/'data/raw/yfinance_estimation_2015_2022.zip',q/'data/raw/yfinance_estimation_2015_2022.zip')
   r=validate(q);self.assertEqual('FAIL',r['status'])
