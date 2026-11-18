from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class Market:
    rate: float = .03
    dividend: float = .02
    volatility: float = .20
    def __post_init__(self):
        if not all(np.isfinite(x) for x in (self.rate,self.dividend,self.volatility)) or self.volatility <= 0 or self.volatility > 3:
            raise ValueError('Invalid market assumptions')

@dataclass(frozen=True)
class Valuation:
    value: float
    standard_error: float
    call_probability: float
    principal_loss_probability: float
    expected_coupons: float
    paths: int
    seed: int

class GBMMonteCarloPricer:
    def __init__(self, paths=50000, seed=42):
        if paths < 1000 or paths > 2000000:
            raise ValueError('Paths must be between 1,000 and 2,000,000')
        self.paths=int(paths)
        self.seed=int(seed)

    def price(self, product, market):
        rng=np.random.default_rng(self.seed)
        n=self.paths
        ratio=np.ones(n)
        active=np.ones(n,dtype=bool)
        pv=np.zeros(n)
        total_coupons=np.zeros(n)
        redemption=np.zeros(n)
        called=np.zeros(n,dtype=bool)
        dt=1/product.frequency
        for i in range(1,product.periods+1):
            z=rng.standard_normal(n)
            ratio*=np.exp((market.rate-market.dividend-.5*market.volatility**2)*dt + market.volatility*np.sqrt(dt)*z)
            t=i*dt
            coupon=active & (ratio >= product.coupon_barrier)
            amount=coupon*product.notional*product.coupon_rate/product.frequency
            pv+=amount*np.exp(-market.rate*t)
            total_coupons+=amount
            if i < product.periods:
                hit=active & (i >= product.first_call) & (ratio >= product.call_barrier)
                pv+=hit*product.notional*np.exp(-market.rate*t)
                redemption[hit]=product.notional
                called|=hit
                active[hit]=False
            else:
                principal=np.where(ratio >= product.protection_barrier,product.notional,product.notional*ratio)
                pv+=active*principal*np.exp(-market.rate*t)
                redemption[active]=principal[active]
        return Valuation(float(pv.mean()),float(pv.std(ddof=1)/np.sqrt(n)),float(called.mean()),float(np.mean(redemption < product.notional-1e-8)),float(total_coupons.mean()),n,self.seed)
