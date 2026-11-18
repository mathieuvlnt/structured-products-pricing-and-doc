"""Simplified risk-neutral valuations, no issuer spread or calibration."""
from dataclasses import dataclass
import math
import numpy as np
from pricing.monte_carlo import Market

@dataclass(frozen=True)
class Result:
    value: float
    standard_error: float
    call_probability: float
    principal_loss_probability: float
    expected_coupons: float
    paths: int
    seed: int
    model: str

def normal_cdf(x):return .5*(1+math.erf(x/math.sqrt(2)))

class MultiPricer:
    def __init__(self,paths=30000,seed=42):
        if not 1000<=paths<=1000000:raise ValueError('Invalid number of paths')
        self.paths=paths;self.seed=seed

    def price(self,p,m):
        T=p.years;r=m.rate;q=m.dividend;sig=m.volatility;N=p.notional
        if p.family=='European Option':
            d1=(math.log(1/p.strike)+(r-q+.5*sig**2)*T)/(sig*math.sqrt(T));d2=d1-sig*math.sqrt(T)
            if p.option_type=='Call':val=N*(math.exp(-q*T)*normal_cdf(d1)-p.strike*math.exp(-r*T)*normal_cdf(d2))
            else:val=N*(p.strike*math.exp(-r*T)*normal_cdf(-d2)-math.exp(-q*T)*normal_cdf(-d1))
            return Result(val,0,0,0,0,0,self.seed,'Black-Scholes-Merton (analytical)')
        if p.family=='Capital Protected Note':
            d1=(math.log(1/p.strike)+(r-q+.5*sig**2)*T)/(sig*math.sqrt(T));d2=d1-sig*math.sqrt(T)
            call=math.exp(-q*T)*normal_cdf(d1)-p.strike*math.exp(-r*T)*normal_cdf(d2)
            val=N*(p.protection*math.exp(-r*T)+p.participation*call)
            return Result(val,0,0,0,0,0,self.seed,'Discounted floor + Black-Scholes call')
        if p.family=='Credit Linked Note':
            # Continuous default with recovery paid at default; coupon until default, principal at maturity if survival.
            lam=p.credit_hazard; a=r+lam
            annuity=(-math.expm1(-a*T))/a if abs(a)>1e-12 else T
            val=N*(p.coupon_rate*annuity+lam*p.recovery*annuity+math.exp(-a*T))
            return Result(val,0,0,1-math.exp(-lam*T),N*p.coupon_rate*annuity,0,self.seed,'Flat hazard intensity / recovery-at-default')
        rng=np.random.default_rng(self.seed);ratio=np.ones(self.paths);active=np.ones(self.paths,bool)
        pv=np.zeros(self.paths);called=np.zeros(self.paths,bool);redeem=np.zeros(self.paths)
        dt=1/p.frequency
        for i in range(1,p.periods+1):
            ratio*=np.exp((r-q-.5*sig*sig)*dt+sig*math.sqrt(dt)*rng.standard_normal(self.paths))
            t=i*dt
            if i<p.periods:
                hit=active & (i>=p.first_call) & (ratio>=p.call_barrier)
                amount=N*(1+p.coupon_rate*t)
                pv+=hit*amount*math.exp(-r*t);redeem[hit]=amount;called|=hit;active[hit]=False
            else:
                amount=np.where(ratio>=p.call_barrier,N*(1+p.coupon_rate*T),np.where(ratio>=p.protection_barrier,N,N*ratio))
                pv+=active*amount*math.exp(-r*t);redeem[active]=amount[active]
        return Result(float(pv.mean()),float(pv.std(ddof=1)/math.sqrt(self.paths)),float(called.mean()),float(np.mean(redeem<N)),0,self.paths,self.seed,'GBM Monte Carlo / constant volatility')
