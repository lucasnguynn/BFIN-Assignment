"""Unit tests for the decision-reversal re-confirmation (synthetic data, plus one integration test on the repository)."""
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from quality_assurance import decision_reversal as dr  # noqa: E402


def synthetic(seed=7):
    rng = np.random.default_rng(seed)
    X = rng.normal(0.008, 0.05, size=(96, 12))
    M = rng.normal(0.007, 0.04, size=96)
    C = dr.annual_cov(X)
    w1 = np.r_[0.15, 0.15, 0.10, 0.10, 0.10, 0.05, 0.10, 0.05, 0.05, 0.05, 0.05, 0.05]
    w2 = np.r_[0.05, 0.05, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.05, 0.05]
    return X, M, C, w1, w2


class ReversalMath(unittest.TestCase):
    def test_capital_fraction_matches_case_numbers(self):
        # 12m - (2,400*922.78 + 3,600*986.07) = 6,235,476; / 1.001 = 6,229,246.75 -> F = 0.5191039
        self.assertAlmostEqual(dr.capital_fraction(), 6_229_246.753 / 12_000_000, places=6)

    def test_utility_is_quadratic_penalised_return(self):
        X, M, C, w1, _ = synthetic()
        mu = dr.expected_returns(X, M, 0.25)
        F = 0.5
        self.assertAlmostEqual(dr.fund_utility(w1, mu, C, 3.0, F), F * (w1 @ mu) - 1.5 * F * F * (w1 @ C @ w1), places=14)

    def test_lambda_star_closed_form_equals_root_finder_and_equalises_utility(self):
        X, M, C, w1, w2 = synthetic()
        F, A = 0.5191, 3.0
        d = lambda lam: dr.fund_utility(w1, dr.expected_returns(X, M, lam), C, A, F) - dr.fund_utility(w2, dr.expected_returns(X, M, lam), C, A, F)
        cf = dr.lambda_star_closed_form(w1, w2, X, M, C, A, F)
        rf, ok = dr._bracket_root(d, -50.0, 50.0)
        self.assertTrue(ok)
        self.assertAlmostEqual(cf, rf, places=9)
        self.assertAlmostEqual(d(cf), 0.0, places=12)
        self.assertLess(d(cf - 0.1) * d(cf + 0.1), 0)  # the preference really flips

    def test_a_star_closed_form_equals_root_finder_and_equalises_utility(self):
        X, M, C, w1, w2 = synthetic()
        F = 0.5191
        mu = dr.expected_returns(X, M, 0.25)
        d = lambda a: dr.fund_utility(w1, mu, C, a, F) - dr.fund_utility(w2, mu, C, a, F)
        cf = dr.a_star_closed_form(w1, w2, mu, C, F)
        rf, ok = dr._bracket_root(d, -500.0, 500.0)
        self.assertTrue(ok)
        self.assertAlmostEqual(cf, rf, places=9)
        self.assertAlmostEqual(d(cf), 0.0, places=12)

    def test_formula_scales_with_F(self):
        X, M, C, w1, w2 = synthetic()
        mu = dr.expected_returns(X, M, 0.25)
        a1 = dr.a_star_closed_form(w1, w2, mu, C, 0.5)
        a2 = dr.a_star_closed_form(w1, w2, mu, C, 1.0)
        self.assertAlmostEqual(a1, 2 * a2, places=12)  # A* is inversely proportional to F

    def test_no_root_is_reported_when_signs_do_not_change(self):
        _, ok = dr._bracket_root(lambda x: x * x + 1.0, -1.0, 1.0)
        self.assertFalse(ok)


class ReversalOptimiser(unittest.TestCase):
    def test_constraint_violation_detects_breaches(self):
        good = np.r_[np.full(10, 0.09), 0.05, 0.05]
        self.assertLess(dr.constraint_violation(good), 1e-12)
        over_stock = np.r_[0.25, np.full(9, 0.65 / 9), 0.05, 0.05]          # one stock above the 15% cap
        self.assertAlmostEqual(dr.constraint_violation(over_stock), 0.10, places=9)
        over_etf = np.r_[np.full(10, 0.05), 0.30, 0.20]                      # ETFs total 50% > 40% cap
        self.assertAlmostEqual(dr.constraint_violation(over_etf), 0.10, places=9)
        not_summing = np.r_[np.full(10, 0.09), 0.05, 0.0]                    # sums to 0.95
        self.assertAlmostEqual(dr.constraint_violation(not_summing), 0.05, places=9)
        negative = np.r_[-0.05, np.full(9, 0.1), 0.15, 0.0]                  # short position
        self.assertGreater(dr.constraint_violation(negative), 0.04)

    def test_reoptimised_portfolio_is_feasible_and_never_worse_than_fixed_policies(self):
        X, M, C, w1, w2 = synthetic()
        F = 0.5191
        for lam, A in ((0.25, 3.0), (0.25, 20.0), (0.0, 3.0)):
            mu = dr.expected_returns(X, M, lam)
            w = dr.solve(mu, C, A, F)
            self.assertLess(dr.constraint_violation(w), 1e-7)
            u = dr.fund_utility(w, mu, C, A, F)
            for fixed in (w1, w2):
                self.assertGreaterEqual(u, dr.fund_utility(fixed, mu, C, A, F) - 1e-10)

    def test_with_equal_mu_the_optimum_is_minimum_variance(self):
        X, M, C, _, _ = synthetic()
        F = 0.5191
        mu_equal = dr.expected_returns(X, M, 0.0)  # lambda=0 -> same prior mean for every asset
        w_sample = dr.solve(mu_equal, C, 3.0, F)
        w_minvar = dr.solve(mu_equal, C, 3.0, F, min_variance=True)
        self.assertLess(float(np.max(np.abs(w_sample - w_minvar))), 1e-5)


class ReversalOnRepository(unittest.TestCase):
    def test_all_checks_pass_on_the_frozen_inputs(self):
        res = dr.check_decision_reversal(ROOT, write_outputs=False)
        self.assertEqual(len(res), 7)
        self.assertEqual([c["id"] for c in res if c["status"] != "PASS"], [])


if __name__ == "__main__":
    unittest.main()
