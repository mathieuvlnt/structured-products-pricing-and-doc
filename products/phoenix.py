from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True)
class Phoenix:
    underlying: str = 'EURO STOXX 50 Index'
    underlying_type: str = 'Equity index'
    currency: str = 'EUR'
    notional: float = 100000.0
    spot: float = 100.0
    years: int = 3
    frequency: int = 4
    coupon_rate: float = .08
    coupon_barrier: float = .70
    call_barrier: float = 1.00
    protection_barrier: float = .60
    first_call: int = 4
    memory: bool = False

    def __post_init__(self):
        if not self.underlying.strip() or self.underlying_type not in ('Equity index','Share','ETF / Fund','FX','Commodity'):
            raise ValueError('A supported underlying name and type are required')
        if self.currency not in ('EUR','USD','GBP','CHF') or self.notional <= 0 or self.spot <= 0:
            raise ValueError('Invalid currency, notional or spot')
        if self.years not in range(1,11) or self.frequency not in (1,2,4,12):
            raise ValueError('Unsupported tenor or observation frequency')
        if not (1 <= self.first_call < self.periods):
            raise ValueError('First autocall observation must be before maturity')
        if not (0 <= self.coupon_rate <= 1 and 0 < self.coupon_barrier <= 2 and 0 < self.call_barrier <= 2 and 0 < self.protection_barrier < 1):
            raise ValueError('Invalid coupon or barrier')
        if self.memory:
            raise ValueError('Coupon memory is not implemented in V2')

    @property
    def periods(self):
        return self.years * self.frequency

    def cashflows(self, ratios: Sequence[float]):
        if len(ratios) != self.periods:
            raise ValueError('One underlying ratio is required per observation')
        flows=[]
        for i, ratio in enumerate(ratios, 1):
            if ratio < 0:
                raise ValueError('Underlying ratio cannot be negative')
            coupon = self.notional*self.coupon_rate/self.frequency if ratio >= self.coupon_barrier else 0.0
            called = i >= self.first_call and i < self.periods and ratio >= self.call_barrier
            redemption = self.notional if called else (self.notional if ratio >= self.protection_barrier else self.notional*ratio) if i == self.periods else 0.0
            flows.append(dict(obs=i, time=i/self.frequency, ratio=float(ratio), coupon=coupon, redemption=redemption, called=called))
            if called:
                break
        return flows
