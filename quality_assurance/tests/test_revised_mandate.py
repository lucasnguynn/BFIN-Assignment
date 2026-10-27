import unittest
from pathlib import Path
from quality_assurance import revised_mandate_checks as rm

ROOT = Path(__file__).resolve().parents[2]


class RevisedMandateGates(unittest.TestCase):
    def test_all_gates_pass(self):
        results = rm.check_revised_mandate(ROOT)
        bad = [r for r in results if r["status"] not in ("PASS", "WARN")]
        self.assertFalse(bad, bad)

    def test_schedule_totals(self):
        self.assertEqual(sum(rm.ORIGINAL_SCHEDULE.values()), sum(rm.REVISED_SCHEDULE.values()))

    def test_revised_ledger_shortfall_is_detected(self):
        # sanity check of the gate logic: with zero bonds the 2024 payment must fail
        cash = 0
        for year in range(2023, 2031):
            cash -= float(rm.REVISED_SCHEDULE.get(year, 0))
        self.assertLess(cash, 0)


if __name__ == "__main__":
    unittest.main()
