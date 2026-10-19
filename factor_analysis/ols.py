"""Plain-numpy OLS with classical + Newey-West SEs and residual diagnostics.

No statsmodels dependency: every formula is visible and unit-tested against numpy.linalg.lstsq.
"""
from __future__ import annotations
import numpy as np
from scipy import stats


def ols(y, X, names):
    """y: (n,), X: (n,k0) regressors WITHOUT the constant. Returns a dict of results."""
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    if X.ndim == 1:
        X = X[:, None]
    n, k0 = X.shape
    Z = np.column_stack([np.ones(n), X])
    k = Z.shape[1]
    df = n - k
    if df <= 0:
        raise ValueError("not enough observations")
    ZtZi = np.linalg.inv(Z.T @ Z)
    b = ZtZi @ Z.T @ y
    e = y - Z @ b
    ssr = float(e @ e)
    sst = float(((y - y.mean()) ** 2).sum())
    s2 = ssr / df
    se = np.sqrt(np.diag(s2 * ZtZi))
    t = b / se
    p = 2 * stats.t.sf(np.abs(t), df)
    tc = stats.t.ppf(0.975, df)
    r2 = 1 - ssr / sst
    adj = 1 - (1 - r2) * (n - 1) / df
    # Newey-West (Bartlett kernel), L = floor(4 (n/100)^(2/9)), no small-sample correction
    L = int(np.floor(4 * (n / 100) ** (2 / 9)))
    G0 = Z * e[:, None]
    S = G0.T @ G0
    for lag in range(1, L + 1):
        w = 1 - lag / (L + 1)
        G = G0[lag:].T @ G0[:-lag]
        S += w * (G + G.T)
    Vh = ZtZi @ S @ ZtZi
    seh = np.sqrt(np.diag(Vh))
    th = b / seh
    ph = 2 * stats.t.sf(np.abs(th), df)
    fstat = (r2 / (k - 1)) / ((1 - r2) / df) if (k > 1 and r2 < 1) else np.nan
    return dict(
        names=["const"] + list(names), n=n, k=k, df=df, b=b, se=se, t=t, p=p,
        ci_lo=b - tc * se, ci_hi=b + tc * se, se_hac=seh, t_hac=th, p_hac=ph, hac_lags=L,
        r2=r2, adj_r2=adj, ssr=ssr, resid=e, F=fstat,
        F_p=float(stats.f.sf(fstat, k - 1, df)) if np.isfinite(fstat) else np.nan,
        aic=n * np.log(ssr / n) + 2 * k, bic=n * np.log(ssr / n) + k * np.log(n),
        resid_sd=float(np.sqrt(s2)), Z=Z,
    )


def nested_f(restricted, full):
    """F-test that the extra regressors in `full` are jointly zero."""
    q = full["k"] - restricted["k"]
    F = ((restricted["ssr"] - full["ssr"]) / q) / (full["ssr"] / full["df"])
    return float(F), float(stats.f.sf(F, q, full["df"])), q


def diagnostics(res, lb_lags=12):
    e = res["resid"]
    n = res["n"]
    Z = res["Z"]
    dw = float(np.sum(np.diff(e) ** 2) / np.sum(e ** 2))
    jb, jbp = stats.jarque_bera(e)
    # Breusch-Pagan (Koenker n*R^2 form): regress e^2 on the regressors
    e2 = e ** 2
    g = np.linalg.lstsq(Z, e2, rcond=None)[0]
    fit = Z @ g
    r2a = 1 - np.sum((e2 - fit) ** 2) / np.sum((e2 - e2.mean()) ** 2)
    bp = n * r2a
    bpp = float(stats.chi2.sf(bp, res["k"] - 1)) if res["k"] > 1 else np.nan
    ec = e - e.mean()
    den = np.sum(ec ** 2)
    ac = np.array([np.sum(ec[l:] * ec[:-l]) / den for l in range(1, lb_lags + 1)])
    q = n * (n + 2) * np.sum(ac ** 2 / (n - np.arange(1, lb_lags + 1)))
    X = Z[:, 1:]
    vif = []
    if X.shape[1] > 1:
        for j in range(X.shape[1]):
            others = np.column_stack([np.ones(n), np.delete(X, j, axis=1)])
            gj = np.linalg.lstsq(others, X[:, j], rcond=None)[0]
            r2j = 1 - np.sum((X[:, j] - others @ gj) ** 2) / np.sum((X[:, j] - X[:, j].mean()) ** 2)
            vif.append(1 / (1 - r2j))
    h = np.einsum("ij,jk,ik->i", Z, np.linalg.inv(Z.T @ Z), Z)
    return dict(
        durbin_watson=dw, resid_lag1_autocorr=float(ac[0]), ljung_box_Q=float(q),
        ljung_box_p=float(stats.chi2.sf(q, lb_lags)), ljung_box_lags=lb_lags,
        jarque_bera=float(jb), jarque_bera_p=float(jbp),
        resid_skew=float(stats.skew(e)), resid_excess_kurtosis=float(stats.kurtosis(e)),
        breusch_pagan_LM=float(bp), breusch_pagan_p=bpp,
        max_vif=float(max(vif)) if vif else np.nan,
        max_leverage=float(h.max()), max_abs_std_resid=float(np.max(np.abs(e)) / res["resid_sd"]),
    )
