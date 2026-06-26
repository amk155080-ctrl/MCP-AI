from dataclasses import dataclass

@dataclass
class MarketRegimeResult:
    score: float
    regime: str
    sox_score: float
    vix_score: float
    us10y_score: float
    dxy_score: float
    liquidity_score: float

def calc_sox_score(r):
    return 30 if r >= 3 else 22 if r >= 1 else 15 if r >= 0 else 8 if r >= -1 else 0

def calc_vix_score(v):
    return 25 if v <= 15 else 20 if v <= 20 else 10 if v <= 25 else 5 if v <= 30 else 0

def calc_us10y_score(y):
    y = y / 10 if y and y > 20 else y
    return 20 if y <= 4 else 15 if y <= 4.5 else 8 if y <= 5 else 0

def calc_dxy_score(d):
    return 10 if d <= 100 else 6 if d <= 105 else 3 if d <= 110 else 0

def classify(total):
    return "STRONG_RISK_ON" if total >= 85 else "RISK_ON" if total >= 70 else "NEUTRAL" if total >= 50 else "RISK_OFF" if total >= 35 else "CRISIS"

def calculate_market_regime(sox_return, vix, us10y, dxy, deposit_change=0, margin_change=0):
    sox_score = calc_sox_score(sox_return or 0)
    vix_score = calc_vix_score(vix or 99)
    us10y_score = calc_us10y_score(us10y or 99)
    dxy_score = calc_dxy_score(dxy or 999)
    liquidity_score = (8 if deposit_change > 0 else 0) + (7 if margin_change > 0 else 0)
    total = round(sox_score + vix_score + us10y_score + dxy_score + liquidity_score, 2)
    return MarketRegimeResult(total, classify(total), sox_score, vix_score, us10y_score, dxy_score, liquidity_score)
