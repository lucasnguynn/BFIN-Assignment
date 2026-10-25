"""Check reader-facing portfolio deliverables actually committed to GitHub main."""
from pathlib import Path
import hashlib
import json
import unittest
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
FINAL = ROOT / "portfolio_construction" / "Portfolio Final"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

class FinalPortfolioAcceptance(unittest.TestCase):
    def test_files_present_and_openable(self):
        names=("Portfolio Report.pdf","Portfolio Report.docx","Results.xlsx",
               "Portfolio Files.zip","Sources/Yahoo Raw.zip","Sources/Original Decision.pdf")
        for name in names:
            p=FINAL/name
            self.assertTrue(p.is_file() and p.stat().st_size>500,name)
        from pypdf import PdfReader
        from docx import Document
        reader=PdfReader(FINAL/"Portfolio Report.pdf")
        self.assertGreaterEqual(len(reader.pages),2)
        text=" ".join(p.extract_text() or "" for p in reader.pages)
        for phrase in ("Our recommendation","What changed","VTI","JNJ"):
            self.assertIn(phrase,text)
        doc=Document(FINAL/"Portfolio Report.docx")
        self.assertGreater(len(doc.paragraphs),12)
        self.assertGreaterEqual(len(doc.tables),1)

    def test_nine_sheet_workbook(self):
        with zipfile.ZipFile(FINAL/"Results.xlsx") as z:
            self.assertIsNone(z.testzip())
            workbook=ET.fromstring(z.read("xl/workbook.xml"))
            ns="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
            names=[x.attrib["name"] for x in workbook.find(ns+"sheets")]
            self.assertEqual(names,["Summary","Funding","Investments","Models","Cash Flows",
                                    "Risk and Goal","Observed","Factors","Sources and Status"])
            for n in range(1,10):
                self.assertIn("sheetData",z.read(f"xl/worksheets/sheet{n}.xml").decode())

    def test_real_vendor_archive_and_period(self):
        record=json.loads((FINAL/"Sources/Market Source.json").read_text())
        self.assertEqual(digest(FINAL/"Sources/Yahoo Raw.zip"),record["raw_archive_sha256"])
        self.assertEqual(digest(FINAL/"Sources/Observed Prices.csv"),record["processed_price_csv_sha256"])
        with zipfile.ZipFile(FINAL/"Sources/Yahoo Raw.zip") as raw:
            self.assertIsNone(raw.testzip())
        import csv
        for name,count in (("Observed Prices.csv",752),("Observed Monthly.csv",36)):
            with (FINAL/"Sources"/name).open(encoding="utf-8",newline="") as fh:
                self.assertEqual(len(list(csv.DictReader(fh))),count)

    def test_package_matches_actual_files(self):
        lines=(FINAL/"Sources/Checksums.txt").read_text().splitlines()
        self.assertGreater(len(lines),7)
        for line in lines:
            expected,name=line.split("  ",1)
            self.assertEqual(digest(FINAL/name),expected,name)
        with zipfile.ZipFile(FINAL/"Portfolio Files.zip") as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(set(archive.namelist()),
                {p.relative_to(FINAL).as_posix() for p in FINAL.rglob("*")
                 if p.is_file() and p.name!="Portfolio Files.zip"})

if __name__=="__main__":
    unittest.main()
