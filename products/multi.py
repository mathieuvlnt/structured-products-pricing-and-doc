"""Contractual simplified payoff definitions for additional illustrative product families."""
from dataclasses import dataclass
import math

KINDS=('Share','Equity index','ETF / Fund','FX','Commodity','Credit reference')

@dataclass(frozen=True)
class Note:
    family: str
    underlying: str
    kind: str
    currency: str = 'EUR'
    notional: float = 100000.0
    spot: float = 100.0
    years: int = 3
    frequency: int = 4
    coupon_rate: float = .08
    coupon_barrier: float = .70
    call_barrier: float = 1.0
    protection_barrier: float = .60
    first_call: int = 4
    strike: float = 1.0
    participation: float = 1.0
    protection: float = 1.0
    credit_hazard: float = .025
    recovery: float = .40
    reference_entity: str = ''
    option_type: str = 'Call'

    def __post_init__(self):
        if self.family not in ('European Option','Athena Autocall','Capital Protected Note','Credit Linked Note'):
            raise ValueError('Unsupported family')
        if self.kind not in KINDS or not self.underlying.strip():raise ValueError('Invalid underlying')
        if self.family=='Credit Linked Note' and not self.reference_entity.strip():raise ValueError('Credit reference entity is required')
        if self.family=='Credit Linked Note' and self.kind != 'Credit reference':
            raise ValueError('CLN requires a credit reference')
        if self.family!='Credit Linked Note' and self.kind=='Credit reference':raise ValueError('Credit reference only available for CLN')
        if self.family=='Capital Protected Note' and self.kind not in ('Share','Equity index','ETF / Fund'):
            raise ValueError('Protected-note decomposition is implemented only for equity-style references')
        if self.currency not in ('EUR','USD','GBP','CHF') or not (self.notional>0 and self.spot>0 and 1<=self.years<=10):raise ValueError('Invalid amount or tenor')
        if self.frequency not in (1,2,4,12) or not (0<=self.coupon_rate<=1):raise ValueError('Invalid coupon')
        if not (0<self.strike<=3 and 0<self.protection<=1 and 0<=self.participation<=3):raise ValueError('Invalid strike/protection/participation')
        if not (0<self.coupon_barrier<=2 and 0<self.call_barrier<=2 and 0<self.protection_barrier<1):raise ValueError('Invalid barriers')
        if self.family=='Athena Autocall' and not (1<=self.first_call<self.periods):raise ValueError('Invalid first autocall observation')
        if not (0<=self.credit_hazard<=1 and 0<=self.recovery<=1):raise ValueError('Invalid credit assumptions')
        if self.option_type not in ('Call','Put'):raise ValueError('Invalid option type')

    @property
    def periods(self):return self.years*self.frequency

    def cashflows(self, ratios):
        """Return undiscounted dated cashflows. European option pays premium-equivalent payoff at T.
        CLN uses separate stochastic credit simulation; no equity cashflow path is asserted.
        """
        if len(ratios)!=self.periods:raise ValueError('Observation path length mismatch')
        if any(not math.isfinite(float(x)) or x<0 for x in ratios):raise ValueError('Invalid observation level')
        if self.family=='Credit Linked Note':raise ValueError('CLN credit-event paths are handled by the credit pricer')
        out=[]
        for i,x in enumerate(ratios,1):
            coupon=0.; principal=0.; called=False
            if self.family=='European Option' and i==self.periods:
                principal=self.notional*max(x-self.strike,0) if self.option_type=='Call' else self.notional*max(self.strike-x,0)
            elif self.family=='Capital Protected Note' and i==self.periods:
                principal=self.notional*(self.protection+self.participation*max(x-self.strike,0))
            elif self.family=='Athena Autocall':
                if i<self.periods and i>=self.first_call and x>=self.call_barrier:
                    principal=self.notional*(1+self.coupon_rate*i/self.frequency);called=True
                elif i==self.periods:
                    principal=self.notional*(1+self.coupon_rate*self.years) if x>=self.call_barrier else self.notional*(1 if x>=self.protection_barrier else x)
            out.append(dict(obs=i,time=i/self.frequency,ratio=float(x),coupon=coupon,redemption=principal,called=called))
            if called:break
        return out
