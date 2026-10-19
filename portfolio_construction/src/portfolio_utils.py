"""Portfolio analytics for Kappa. All returns are decimals, annual figures are arithmetic unless labeled CAGR."""
import numpy as np
from scipy.optimize import minimize
STOCKS=['AAPL','MSFT','JPM','BAC','JNJ','PFE','PG','KO','XOM','CAT']
ETFS=['VTV','IWM']
ASSETS=STOCKS+ETFS
MARKET='VTI'
SECTORS={'Technology':[0,1],'Financials':[2,3],'Healthcare':[4,5], 'Consumer staples':[6,7], 'Energy':[8], 'Industrials':[9]}
BOND_COST=2_400*922.78+3_600*986.07
GROWTH_BUDGET=12_000_000-BOND_COST
ENTRY_COST=0.001
PURCHASE=GROWTH_BUDGET/(1+ENTRY_COST)
F=PURCHASE/12_000_000

def parameters(data, lam=0.25):
    X=data[ASSETS].to_numpy(float)
    M=data[MARKET].to_numpy(float)
    if X.shape!=(96,12) or not np.isfinite(X).all() or not np.isfinite(M).all():
        raise ValueError('Estimation requires 96 complete monthly returns through Dec 2022')
    mean=12*(lam*X.mean(0)+(1-lam)*M.mean())
    C=12*np.cov(X,rowvar=False,ddof=1)
    vm=M.var(ddof=1)
    beta=np.cov(X.T,M,ddof=1)[-1,:-1]/vm
    intercept=X.mean(0)-beta*M.mean()
    residual=X-intercept[None,:]-M[:,None]*beta[None,:]
    S=12*(vm*np.outer(beta,beta)+np.diag(residual.var(axis=0,ddof=1)))
    return mean,C,S,beta,residual

def constraints(stockcap=.15,sectorcap=.30):
    rows=[{'type':'eq','fun':lambda w:float(w.sum()-1),'jac':lambda w:np.ones(12)}]
    for ids in SECTORS.values():
        v=np.zeros(12);v[ids]=1
        rows.append({'type':'ineq','fun':lambda w,v=v,c=sectorcap:float(c-v@w), 'jac':lambda w,v=v:-v})
    v=np.r_[np.zeros(10),np.ones(2)]
    rows.append({'type':'ineq','fun':lambda w,v=v:float(.40-v@w), 'jac':lambda w,v=v:-v})
    return [(0,stockcap)]*10+[(0,.30)]*2, rows

def optimize(mu,C,A=3,minvar=False,stockcap=.15,sectorcap=.30):
    b,c=constraints(stockcap,sectorcap)
    if minvar:
        fun=lambda w:float(w@C@w)
        grad=lambda w:2*C@w
    else:
        fun=lambda w:float(-(mu@w-0.5*A*F*w@C@w))
        grad=lambda w:-(mu-A*F*C@w)
    r=minimize(fun,np.ones(12)/12,method='SLSQP',jac=grad,bounds=b,constraints=c,options={'ftol':1e-13,'maxiter':5000})
    if not r.success:raise ArithmeticError(f'Optimization failed: {r.message}')
    w=r.x.copy(); w[np.abs(w)<1e-11]=0
    if abs(w.sum()-1)>1e-7 or (w<-1e-8).any() or (w[:10]>stockcap+1e-7).any() or sum(w[10:])>.4000001:
        raise ArithmeticError('Constraint failure')
    return w

def measures(w,mu,S,A=3):
    r=float(w@mu);v=float(w@S@w)
    return {'annual_expected_arithmetic_return':r,'annual_volatility':v**.5, 'equity_component_of_fund_utility':F*r-A*F*F*v/2,'equity_component_of_fund_volatility':F*v**.5}

def stress_equity_weighted(w,shock):
    return float(np.dot(w,np.array([shock[x] for x in ASSETS])))

def fixed_weight_threshold(w1,w2,mu_hist,mu_prior,C,A=3):
    """Historical-mean lambda cutoff for two FIXED allocations."""
    d=w1-w2
    k=0.5*A*F*(w1@C@w1-w2@C@w2)
    base=d@mu_prior
    slope=d@(mu_hist-mu_prior)
    return (k-base)/slope if abs(slope)>1e-12 else float('nan')
