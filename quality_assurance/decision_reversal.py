"""Independent re-confirmation of the decision-reversal thresholds (Workstream 6, "Sensitivity & Decision Reversal").

Purpose
-------
The portfolio-construction workstream reports two switching thresholds between the two FIXED allocations
(recommended Sample-MV policy vs rejected Minimum-Variance policy):

    lambda* ~ 0.0842   weight on each security's own historical mean (rest on the VTI mean) below which Min-Var is preferred
    A*      ~ 8.91     foundation risk aversion above which Min-Var is preferred (at lambda = 0.25)

This module re-derives both numbers WITHOUT importing any portfolio_construction code:

    * inputs: monthly decimal returns 2015-01..2022-12 (processed panel, byte-checked against the raw Yahoo archive by the
      portfolio rebuild gate PORTFOLIO.shipped_outputs_reproduced), the frozen weights and the rejected Min-Var weights;
    * utility is written out from first principles:  U(w) = F * w'mu - (A/2) * F^2 * w'Cw,  F = equity purchase / 12m;
    * each threshold is obtained twice (closed form and a bracketed root finder) and compared with the shipped CSV;
    * the optimisers are re-run from a different starting point to confirm that the two weight sets are what they claim to be;
    * a re-optimisation contrast shows why the thresholds are valid ONLY while both weight sets are held fixed.

Everything is deterministic and offline. Status values follow quality_assurance.checks: PASS / FAIL / WARN / BLOCKED.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq, minimize

STOCKS = ["AAPL", "MSFT", "JPM", "BAC", "JNJ", "PFE", "PG", "KO", "XOM", "CAT"]
ETFS = ["VTV", "IWM"]
ASSETS = STOCKS + ETFS
MARKET = "VTI"
# Sector groups (indices into ASSETS) and caps, as stated in the Initial Decision Record.
SECTORS = {"Technology": [0, 1], "Financials": [2, 3], "Health care": [4, 5],
           "Consumer staples": [6, 7], "Energy": [8], "Industrials": [9]}
STOCK_CAP, SECTOR_CAP, ETF_EACH_CAP, ETF_TOTAL_CAP = 0.15, 0.30, 0.30, 0.40
BASE_A, BASE_LAMBDA = 3.0, 0.25
ENTRY_COST = 0.001                      # 10 bp on equity purchases
CAPITAL = 12_000_000.0
BOND_COST = 2_400 * 922.78 + 3_600 * 986.07   # case quotes: 2,400 Beta + 3,600 Delta bonds

SHIPPED = "portfolio_construction/outputs/fixed_weight_reversal.csv"
FROZEN = "portfolio_construction/evidence/decision_weights_confirmed.csv"
POLICY_W = "portfolio_construction/outputs/policy_weights.csv"
COMPARISON = "portfolio_construction/outputs/portfolio_comparison.csv"
PANEL = "portfolio_construction/data/processed/asset_monthly_returns_estimation.csv"
OUT_RECONFIRM = "quality_assurance/decision_threshold_reconfirmation.csv"
OUT_CONTRAST = "quality_assurance/decision_threshold_reoptimization_contrast.csv"


def chk(cid, status, detail, **extra):
    return dict(id=cid, status=status, detail=detail, **extra)


# ------------------------------------------------------------------ model primitives (first principles)
def capital_fraction() -> float:
    """F = share of the USD 12m that is actually invested in the equity sleeve (after the 10 bp entry cost)."""
    purchase = (CAPITAL - BOND_COST) / (1.0 + ENTRY_COST)
    return purchase / CAPITAL


def expected_returns(X: np.ndarray, M: np.ndarray, lam: float) -> np.ndarray:
    """mu(lambda) = 12 * (lambda * own historical monthly mean + (1 - lambda) * VTI monthly mean)."""
    return 12.0 * (lam * X.mean(axis=0) + (1.0 - lam) * M.mean())


def annual_cov(X: np.ndarray) -> np.ndarray:
    return 12.0 * np.cov(X, rowvar=False, ddof=1)


def fund_utility(w, mu, C, A, F) -> float:
    """Equity-component utility of the whole USD 12m fund: F*E(r) - (A/2) * F^2 * variance."""
    w = np.asarray(w, float)
    return float(F * (w @ mu) - 0.5 * A * F * F * (w @ C @ w))


def lambda_star_closed_form(w1, w2, X, M, C, A, F) -> float:
    """Root of U(w1;lambda) - U(w2;lambda) = 0. mu(lambda) is linear in lambda, hence the difference is too."""
    d = np.asarray(w1, float) - np.asarray(w2, float)
    prior = 12.0 * M.mean() * np.ones(len(d))
    slope = d @ (12.0 * X.mean(axis=0) - prior)
    k = 0.5 * A * F * (w1 @ C @ w1 - w2 @ C @ w2)
    return float((k - d @ prior) / slope)


def a_star_closed_form(w1, w2, mu, C, F) -> float:
    """Root of U(w1;A) - U(w2;A) = 0; the difference is linear in A."""
    d = np.asarray(w1, float) - np.asarray(w2, float)
    dv = float(w1 @ C @ w1 - w2 @ C @ w2)
    return float(2.0 * (d @ mu) / (F * dv))


def _bracket_root(fun, lo, hi):
    """brentq with an explicit sign-change test; returns (root, bracket_ok)."""
    flo, fhi = fun(lo), fun(hi)
    if flo * fhi > 0:
        return float("nan"), False
    return float(brentq(fun, lo, hi, xtol=1e-14, rtol=1e-14, maxiter=500)), True


def feasible_constraints():
    cons = [{"type": "eq", "fun": lambda w: float(w.sum() - 1.0), "jac": lambda w: np.ones(12)}]
    for ids in SECTORS.values():
        v = np.zeros(12)
        v[ids] = 1.0
        cons.append({"type": "ineq", "fun": lambda w, v=v: float(SECTOR_CAP - v @ w), "jac": lambda w, v=v: -v})
    v = np.r_[np.zeros(10), np.ones(2)]
    cons.append({"type": "ineq", "fun": lambda w, v=v: float(ETF_TOTAL_CAP - v @ w), "jac": lambda w, v=v: -v})
    bounds = [(0.0, STOCK_CAP)] * 10 + [(0.0, ETF_EACH_CAP)] * 2
    return bounds, cons


def solve(mu, C, A, F, min_variance=False, start=None) -> np.ndarray:
    """Independent optimiser: different start point than the portfolio code (10 stocks at 10%, ETFs at 0)."""
    bounds, cons = feasible_constraints()
    x0 = np.r_[np.full(10, 0.10), np.zeros(2)] if start is None else start
    if min_variance:
        fun, jac = (lambda w: float(w @ C @ w)), (lambda w: 2.0 * C @ w)
    else:
        fun = lambda w: float(-(mu @ w - 0.5 * A * F * (w @ C @ w)))
        jac = lambda w: -(mu - A * F * (C @ w))
    r = minimize(fun, x0, jac=jac, method="SLSQP", bounds=bounds, constraints=cons,
                 options={"ftol": 1e-14, "maxiter": 10000})
    if not r.success:
        raise ArithmeticError(f"independent optimiser failed: {r.message}")
    w = r.x.copy()
    w[np.abs(w) < 1e-11] = 0.0
    return w


def constraint_violation(w) -> float:
    """Largest breach of any constraint in the Decision Record (0 = feasible)."""
    w = np.asarray(w, float)
    v = [abs(w.sum() - 1.0), float(max(0.0, -w.min())), float(max(0.0, (w[:10] - STOCK_CAP).max())),
         float(max(0.0, (w[10:] - ETF_EACH_CAP).max())), float(max(0.0, w[10:].sum() - ETF_TOTAL_CAP))]
    v += [float(max(0.0, w[ids].sum() - SECTOR_CAP)) for ids in SECTORS.values()]
    return max(v)


# ------------------------------------------------------------------ input loading
def load_inputs(root: Path) -> dict:
    root = Path(root)
    panel = pd.read_csv(root / PANEL)
    exp = [f"{y}-{m:02d}" for y in range(2015, 2023) for m in range(1, 13)]
    if list(panel.month) != exp:
        raise ValueError("processed panel is not the 96 months 2015-01..2022-12")
    X = panel[ASSETS].to_numpy(float)
    M = panel[MARKET].to_numpy(float)
    if not (np.isfinite(X).all() and np.isfinite(M).all()):
        raise ValueError("non-finite returns in processed panel")
    frozen = pd.read_csv(root / FROZEN).set_index("security").loc[ASSETS, "weight_of_growth_sleeve"].to_numpy(float)
    pw = pd.read_csv(root / POLICY_W)
    minvar = pw[pw.policy == "Minimum_Variance"].set_index("ticker").loc[ASSETS, "growth_weight"].to_numpy(float)
    shipped = pd.read_csv(root / SHIPPED)
    comparison = pd.read_csv(root / COMPARISON).set_index("policy")
    return dict(X=X, M=M, frozen=frozen, minvar=minvar, shipped=shipped, comparison=comparison)


# ------------------------------------------------------------------ the checks
def check_decision_reversal(root, write_outputs: bool = True):
    root = Path(root)
    out = []
    try:
        d = load_inputs(root)
    except Exception as e:  # missing or malformed input must never pass silently
        return [chk("REVERSAL.inputs_loaded", "BLOCKED", f"required input missing or malformed: {e!r}")]
    X, M, w_f, w_m = d["X"], d["M"], d["frozen"], d["minvar"]
    F = capital_fraction()
    C = annual_cov(X)
    mu0 = expected_returns(X, M, BASE_LAMBDA)

    # 1. inputs ---------------------------------------------------------------------------------------------------
    viol = max(constraint_violation(w_f), constraint_violation(w_m))
    ok = viol < 1e-7 and 0.51 < F < 0.53
    out.append(chk("REVERSAL.inputs_and_constraints", "PASS" if ok else "FAIL",
                   f"96x12 panel + VTI loaded; F={F:.8f}; max constraint breach of frozen/min-var weights={viol:.2e} "
                   f"(15% stock, 30% sector, 30% ETF, 40% ETF total, long-only, sum=1)"))

    # 2. utility formula vs the shipped comparison table ------------------------------------------------------------
    cmp_ = d["comparison"]
    rows, worst = [], 0.0
    for label, w in (("Sample_MV_A3", w_f), ("Minimum_Variance", w_m)):
        r, v = float(w @ mu0), float(w @ C @ w)
        mine = dict(ret=r, vol=v ** 0.5, util=fund_utility(w, mu0, C, BASE_A, F))
        theirs = dict(ret=float(cmp_.loc[label, "annual_expected_arithmetic_return"]),
                      vol=float(cmp_.loc[label, "annual_volatility"]),
                      util=float(cmp_.loc[label, "equity_component_of_fund_utility"]))
        diff = max(abs(mine[k] - theirs[k]) for k in mine)
        worst = max(worst, diff)
        rows.append(f"{label}: U={mine['util']:.6f}")
    out.append(chk("REVERSAL.utility_formula_matches_shipped", "PASS" if worst < 1e-9 else "FAIL",
                   f"U = F*E(r) - (A/2)*F^2*var recomputed from raw-derived mu and C at A=3, lambda=0.25; "
                   f"max |diff| vs portfolio_comparison.csv = {worst:.2e}; " + "; ".join(rows)))

    # 3/4. thresholds: closed form vs root finder vs shipped -------------------------------------------------------
    ship = d["shipped"]
    lam_ship, a_ship = float(ship.threshold.iloc[0]), float(ship.threshold.iloc[1])
    dU_lam = lambda lam: fund_utility(w_f, expected_returns(X, M, lam), C, BASE_A, F) - fund_utility(w_m, expected_returns(X, M, lam), C, BASE_A, F)
    dU_a = lambda a: fund_utility(w_f, mu0, C, a, F) - fund_utility(w_m, mu0, C, a, F)
    lam_cf = lambda_star_closed_form(w_f, w_m, X, M, C, BASE_A, F)
    a_cf = a_star_closed_form(w_f, w_m, mu0, C, F)
    lam_rf, lam_br = _bracket_root(dU_lam, -2.0, 2.0)
    a_rf, a_br = _bracket_root(dU_a, 0.01, 200.0)

    # same thresholds from independently re-solved weights (guards against a wrong shipped Min-Var vector)
    w_f_re = solve(mu0, C, BASE_A, F)
    w_m_re = solve(mu0, C, BASE_A, F, min_variance=True)
    lam_re = lambda_star_closed_form(w_f_re, w_m_re, X, M, C, BASE_A, F)
    a_re = a_star_closed_form(w_f_re, w_m_re, mu0, C, F)

    lam_diff = max(abs(lam_cf - lam_rf), abs(lam_cf - lam_ship))
    a_diff = max(abs(a_cf - a_rf), abs(a_cf - a_ship))
    lam_dom = 0.0 < lam_cf < 1.0
    out.append(chk("REVERSAL.lambda_star_reconfirmed", "PASS" if lam_br and lam_diff < 1e-8 and lam_dom else "FAIL",
                   f"closed form={lam_cf:.10f}; root finder={lam_rf:.10f}; shipped={lam_ship:.10f}; re-solved weights={lam_re:.10f}; "
                   f"max |diff|={lam_diff:.2e}; inside feasible domain (0,1)={lam_dom}; fixed weights, A=3"))
    out.append(chk("REVERSAL.A_star_reconfirmed", "PASS" if a_br and a_diff < 1e-8 and a_cf > 0 else "FAIL",
                   f"closed form={a_cf:.10f}; root finder={a_rf:.10f}; shipped={a_ship:.10f}; re-solved weights={a_re:.10f}; "
                   f"max |diff|={a_diff:.2e}; A*>0={a_cf > 0}; fixed weights, lambda=0.25"))

    # 5. direction of the switch ----------------------------------------------------------------------------------
    eps_l, eps_a = 0.01, 0.5
    sign = {
        "base (A=3, lam=.25): Sample-MV preferred": dU_a(BASE_A) > 0,
        "lam just below lam*: Min-Var preferred": dU_lam(lam_cf - eps_l) < 0,
        "lam just above lam*: Sample-MV preferred": dU_lam(lam_cf + eps_l) > 0,
        "A just below A*: Sample-MV preferred": dU_a(a_cf - eps_a) > 0,
        "A just above A*: Min-Var preferred": dU_a(a_cf + eps_a) < 0,
        "dv>0 and d.mu>0 (Sample-MV riskier and higher return)": (w_f @ C @ w_f > w_m @ C @ w_m) and ((w_f - w_m) @ mu0 > 0),
    }
    bad = [k for k, v in sign.items() if not v]
    out.append(chk("REVERSAL.direction_of_switch", "PASS" if not bad else "FAIL",
                   f"{sum(sign.values())}/{len(sign)} sign tests pass; failures={bad}. Reading: the recommendation is displaced "
                   f"only if lambda < {lam_cf:.4f} (base 0.25) or A > {a_cf:.2f} (base 3)."))

    # 6. the two weight sets are what they claim -------------------------------------------------------------------
    dw_f = float(np.max(np.abs(w_f - w_f_re)))
    dw_m = float(np.max(np.abs(w_m - w_m_re)))
    du_f = abs(fund_utility(w_f, mu0, C, BASE_A, F) - fund_utility(w_f_re, mu0, C, BASE_A, F))
    dv_m = abs(float(w_m @ C @ w_m) - float(w_m_re @ C @ w_m_re))
    ok = dw_f < 1e-5 and dw_m < 1e-5 and du_f < 1e-10 and dv_m < 1e-10
    out.append(chk("REVERSAL.weight_sets_reproduced_independently", "PASS" if ok else "FAIL",
                   f"re-optimised from a different start: max |w diff| frozen Sample-MV={dw_f:.2e}, Min-Var={dw_m:.2e}; "
                   f"utility diff={du_f:.2e}; variance diff={dv_m:.2e}"))

    # 7. scope: thresholds hold for the two fixed vectors only ------------------------------------------------------
    scenarios = [("base", BASE_A, BASE_LAMBDA), ("at A*", a_cf, BASE_LAMBDA), ("at lambda*", BASE_A, lam_cf),
                 ("A=6", 6.0, BASE_LAMBDA), ("A=20", 20.0, BASE_LAMBDA), ("lambda=0", BASE_A, 0.0)]
    contrast = []
    for name, a, lam in scenarios:
        mu = expected_returns(X, M, lam)
        w_opt = solve(mu, C, a, F)
        u_opt = fund_utility(w_opt, mu, C, a, F)
        u_fr, u_mv = fund_utility(w_f, mu, C, a, F), fund_utility(w_m, mu, C, a, F)
        contrast.append(dict(scenario=name, A=a, lam=lam, utility_frozen_sample_mv=u_fr, utility_min_var=u_mv,
                             utility_reoptimised=u_opt, best_fixed=("Sample_MV" if u_fr >= u_mv else "Min_Var"),
                             reopt_gain_over_best_fixed=u_opt - max(u_fr, u_mv),
                             reopt_max_abs_weight_change_vs_frozen=float(np.max(np.abs(w_opt - w_f))),
                             reopt_max_abs_weight_gap_vs_min_var=float(np.max(np.abs(w_opt - w_m)))))
    ct = pd.DataFrame(contrast)
    never_worse = bool((ct.reopt_gain_over_best_fixed > -1e-10).all())
    at_a = ct[ct.scenario == "at A*"].iloc[0]
    out.append(chk("REVERSAL.scope_fixed_weights_only", "PASS" if never_worse else "FAIL",
                   f"re-optimising at each (A, lambda) never does worse than the better fixed policy (min gain {ct.reopt_gain_over_best_fixed.min():.2e}); "
                   f"at A*={a_cf:.2f} the re-optimised portfolio beats both fixed policies by {at_a.reopt_gain_over_best_fixed:.4f} of fund utility "
                   f"and moves up to {at_a.reopt_max_abs_weight_change_vs_frozen:.1%} in a single weight. The thresholds therefore describe a switch between "
                   f"the two FIXED weight vectors, not a reoptimised switching point."))

    # outputs -----------------------------------------------------------------------------------------------------
    if write_outputs:
        rec = pd.DataFrame([
            dict(test="Historical-mean weight lambda (fixed weights, A=3)", symbol="lambda*", shipped=lam_ship, closed_form=lam_cf,
                 root_finder=lam_rf, from_resolved_weights=lam_re, max_abs_diff=lam_diff, base_assumption=BASE_LAMBDA,
                 feasible_domain="(0,1)", meaning="Min-Var preferred below the threshold"),
            dict(test="Foundation risk aversion A (fixed weights, lambda=0.25)", symbol="A*", shipped=a_ship, closed_form=a_cf,
                 root_finder=a_rf, from_resolved_weights=a_re, max_abs_diff=a_diff, base_assumption=BASE_A,
                 feasible_domain="(0,inf)", meaning="Min-Var preferred above the threshold")])
        rec.to_csv(root / OUT_RECONFIRM, index=False, float_format="%.12g")
        ct.to_csv(root / OUT_CONTRAST, index=False, float_format="%.12g")
    return out


if __name__ == "__main__":
    here = Path(__file__).resolve().parent.parent
    for c in check_decision_reversal(here):
        print(f"[{c['status']:7}] {c['id']}: {c['detail']}")
