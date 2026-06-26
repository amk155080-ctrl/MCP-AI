from sqlalchemy import text
from app.core.database import SessionLocal
from app.services.repository import save_scores

SEMICONDUCTOR_CODES = {
    "005930", "000660", "042700", "058470",
    "095340", "089030", "240810", "222800",
}

def grade(score: float) -> str:
    if score >= 90:
        return "S"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    return "D"

def momentum_score(change_rate, trade_value) -> float:
    c = float(change_rate or 0)
    tv = float(trade_value or 0)
    score = 0
    if c >= 5:
        score += 15
    elif c >= 3:
        score += 10
    elif c >= 1:
        score += 6
    if tv >= 100_000_000_000:
        score += 10
    elif tv >= 30_000_000_000:
        score += 6
    return min(score, 25)

def semiconductor_score(stock_code: str) -> float:
    return 15 if stock_code in SEMICONDUCTOR_CODES else 3

def risk_score(change_rate) -> float:
    c = float(change_rate or 0)
    if c <= -7:
        return 2
    if c <= -4:
        return 6
    return 10

def calculate_daily_scores(trade_date: str):
    db = SessionLocal()
    try:
        rows = db.execute(text('''
            SELECT trade_date, stock_code, stock_name, change_rate, trade_value
            FROM mcp4.stock_price_daily
            WHERE trade_date = :trade_date
        '''), {"trade_date": trade_date}).fetchall()
    finally:
        db.close()

    records = []
    for r in rows:
        m = momentum_score(r.change_rate, r.trade_value)
        semi = semiconductor_score(r.stock_code)
        risk = risk_score(r.change_rate)
        supply = 10
        macro = 10
        total = round(float(m + semi + risk + supply + macro), 2)

        records.append({
            "trade_date": r.trade_date,
            "stock_code": r.stock_code,
            "stock_name": r.stock_name,
            "supply_score": supply,
            "momentum_score": m,
            "macro_score": macro,
            "semiconductor_score": semi,
            "risk_score": risk,
            "total_score": total,
            "grade": grade(total),
        })

    return save_scores(records)
