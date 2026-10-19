"""Unit tests for the factor-analysis module. All fixtures are SYNTHETIC and exist only to test software;
no synthetic number is ever written to the package deliverables."""
import io, shutil, sys, tempfile, unittest, zipfile
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from factor_analysis import ols as ols_mod, french_data, models as factor_models


def synthetic_french_zip(path, months=None, sentinel=False):
    rng = np.random.default_rng(7)
    allm = [f"{y}{m:02d}" for y in range(2012, 2024) for m in range(1, 13)]
    lines = ["This file was created by CMPT_ME_BEME_RETS using the 202401 CRSP database.", "", "",
             ",Mkt-RF,SMB,HML,RF"]
    for ym in allm:
        mk, sm, hm = rng.normal([.8, .1, .1], [4, 2, 2]); rf = 0.2
        if sentinel and ym == "201706": mk = -99.99
        lines.append(f"{ym}, {mk:.2f}, {sm:.2f}, {hm:.2f}, {rf:.2f}")
    lines += ["", " Annual Factors: January-December", ",Mkt-RF,SMB,HML,RF", "2015, 1.0, 2.0, 3.0, 0.1"]
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("F-F_Research_Data_Factors.CSV", "\n".join(lines))


class TestOLS(unittest.TestCase):
    def test_matches_lstsq_and_closed_form(self):
        rng = np.random.default_rng(1); n = 96
        X = rng.normal(size=(n, 3)); y = 0.01 + X @ [1.1, -.3, .4] + rng.normal(scale=.02, size=n)
        r = ols_mod.ols(y, X, ["a", "b", "c"])
        Z = np.column_stack([np.ones(n), X]); b = np.linalg.lstsq(Z, y, rcond=None)[0]
        self.assertTrue(np.allclose(r["b"], b, atol=1e-12))
        e = y - Z @ b; s2 = e @ e / (n - 4)
        self.assertTrue(np.allclose(r["se"], np.sqrt(np.diag(s2 * np.linalg.inv(Z.T @ Z)))))
        adj = 1 - (e @ e / (n - 4)) / (((y - y.mean()) ** 2).sum() / (n - 1))
        self.assertAlmostEqual(r["adj_r2"], adj, places=12)
        self.assertTrue(np.all(r["ci_lo"] < r["b"]) and np.all(r["ci_hi"] > r["b"]))

    def test_recovers_known_params(self):
        rng = np.random.default_rng(2); n = 20000
        X = rng.normal(size=(n, 2)); y = 0.003 + X @ [0.9, 0.2] + rng.normal(scale=.01, size=n)
        r = ols_mod.ols(y, X, ["m", "s"]); self.assertTrue(np.allclose(r["b"], [.003, .9, .2], atol=5e-4))

    def test_nested_f_equals_t2_for_single_restriction(self):
        rng = np.random.default_rng(3); n = 96
        X = rng.normal(size=(n, 2)); y = X @ [1, .3] + rng.normal(scale=.5, size=n)
        full = ols_mod.ols(y, X, ["a", "b"]); rest = ols_mod.ols(y, X[:, :1], ["a"])
        F, p, q = ols_mod.nested_f(rest, full)
        self.assertEqual(q, 1); self.assertAlmostEqual(F, full["t"][2] ** 2, places=8)

    def test_hac_equals_classical_scale_when_white_noise(self):
        rng = np.random.default_rng(4); n = 5000
        X = rng.normal(size=(n, 1)); y = X[:, 0] + rng.normal(size=n)
        r = ols_mod.ols(y, X, ["m"]); self.assertAlmostEqual(r["se_hac"][1] / r["se"][1], 1, delta=.1)

    def test_diagnostics_detect_autocorrelation(self):
        rng = np.random.default_rng(5); n = 400; e = np.zeros(n)
        for i in range(1, n): e[i] = .8 * e[i - 1] + rng.normal()
        X = rng.normal(size=(n, 1)); r = ols_mod.ols(X[:, 0] + e, X, ["m"]); d = ols_mod.diagnostics(r)
        self.assertLess(d["durbin_watson"], 1.0); self.assertLess(d["ljung_box_p"], .01)


class TestFrench(unittest.TestCase):
    def test_parse_units_and_window(self):
        with tempfile.TemporaryDirectory() as t:
            z = Path(t) / "f.zip"; synthetic_french_zip(z)
            df, hdr = french_data.parse_ff3_zip(z)
            self.assertEqual((len(df), df.month.iloc[0], df.month.iloc[-1]), (96, "2015-01", "2022-12"))
            self.assertTrue(df["Mkt-RF"].abs().max() < 1)  # decimals
            self.assertTrue(np.allclose(df.RF, .002))       # 0.20% -> 0.002

    def test_sentinel_raises(self):
        with tempfile.TemporaryDirectory() as t:
            z = Path(t) / "f.zip"; synthetic_french_zip(z, sentinel=True)
            with self.assertRaises(ValueError): french_data.parse_ff3_zip(z)


class TestPipelinePath(unittest.TestCase):
    def test_missing_french_blocks_not_fabricates(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(FileNotFoundError): factor_models.run_factor_models(Path(t))

    def test_end_to_end_with_synthetic_french_in_temp_copy(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            shutil.copytree(ROOT / "portfolio_construction", tmp / "portfolio_construction")
            (tmp / "factor_analysis/data/raw/french").mkdir(parents=True)
            synthetic_french_zip(tmp / "factor_analysis/data/raw/french/F-F_Research_Data_Factors_CSV.zip")
            coef, cmp_, dg = factor_models.run_factor_models(tmp)
            self.assertEqual(len(coef), 22); self.assertEqual(len(cmp_), 11); self.assertEqual(len(dg), 22)
            for f in ["factor_coefficients.csv", "factor_model_comparison.csv", "factor_diagnostics.csv", "factor_exposures.png"]:
                self.assertTrue((tmp / "factor_analysis/outputs" / f).exists(), f)
            self.assertTrue({"MSFT", "PG", "GROWTH_FROZEN_SAMPLE_MV"} <= set(coef.strategy_or_ticker))
            self.assertTrue((coef.n == 96).all())

if __name__ == "__main__":
    unittest.main()
