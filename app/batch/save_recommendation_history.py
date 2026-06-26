import argparse
from datetime import datetime

from sqlalchemy import text

from app.core.database import SessionLocal


def calc_signal(score, risk, smart):
    score = float(score or 0)
    risk = float(risk or 0)
    smart = float(smart or 0)

    if score >= 80 and smart > 0 and risk >= 65:
        return "STRONG_BUY", 85
    if score >= 70 and smart > 0:
        return "BUY", 75
    if score >= 65 and smart >= 10000000000 and risk >= 70:
        return "BUY", 80
    if score < 45 and smart < 0:
        return "STRONG_SELL", 25
    if score < 55 and smart < 0:
        return "SELL", 30
    return "WATCH", 60


def calc_target_price(close_price, total_score, risk_score, smart_money_net, market_cap):
    close_price = float(close_price or 0)
    total_score = float(total_score or 0)
    risk_score = float(risk_score or 0)
    smart_money_net = float(smart_money_net or 0)
    market_cap = float(market_cap or 0)

    if close_price <= 0:
        return 0, 0

    smart_ratio = smart_money_net / market_cap if market_cap > 0 else 0

    upside_pct = 8.0

    if smart_ratio >= 0.005:
        upside_pct += 15
    elif smart_ratio >= 0.003:
        upside_pct += 10
    elif smart_ratio >= 0.001:
        upside_pct += 5

    if total_score >= 80:
        upside_pct += 5
    elif total_score >= 70:
        upside_pct += 3

    if risk_score < 60:
        upside_pct -= 5
    elif risk_score < 70:
        upside_pct -= 2

    stop_pct = -7.0
    if risk_score < 60:
        stop_pct = -5.0

    target_price = round(close_price * (1 + upside_pct / 100), 0)
    stop_loss = round(close_price * (1 + stop_pct / 100), 0)

    return target_price, stop_loss


def run(bas_dd, limit):
    trade_date = f"{bas_dd[0:4]}-{bas_dd[4:6]}-{bas_dd[6:8]}"

    db = SessionLocal()
    saved = 0

    try:
        rows = db.execute(text("""
            SELECT
                s.trade_date,
                s.stock_code,
                s.stock_name,
                s.total_score,
                s.risk_score,
                p.close_price,
                p.market_cap,
                (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
                ) AS smart_money_net
            FROM mcp4.stock_score_daily s
            JOIN mcp4.stock_price_daily p
              ON s.trade_date = p.trade_date
             AND s.stock_code = p.stock_code
            LEFT JOIN mcp4.investor_flow_daily f
              ON s.trade_date = f.trade_date
             AND s.stock_code = f.stock_code
            WHERE s.trade_date = :trade_date
              AND s.total_score >= 65
              AND (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
              ) > 0
              AND COALESCE(p.trade_value,0) >= 10000000000
              AND COALESCE(p.market_cap,0) >= 100000000000
            ORDER BY
                s.total_score DESC,
                smart_money_net DESC
            LIMIT :limit
        """), {
            "trade_date": trade_date,
            "limit": limit,
        }).mappings().all()

        for r in rows:
            signal, confidence = calc_signal(
                r["total_score"],
                r["risk_score"],
                r["smart_money_net"],
            )

            target_price, stop_loss = calc_target_price(
                r["close_price"],
                r["total_score"],
                r["risk_score"],
                r["smart_money_net"],
                r["market_cap"],
            )

            db.execute(text("""
                INSERT INTO mcp4.recommendation_history
                (
                    trade_date,
                    stock_code,
                    stock_name,
                    total_score,
                    risk_score,
                    signal,
                    confidence,
                    target_price,
                    stop_loss,
                    smart_money_net,
                    created_at
                )
                VALUES
                (
                    :trade_date,
                    :stock_code,
                    :stock_name,
                    :total_score,
                    :risk_score,
                    :signal,
                    :confidence,
                    :target_price,
                    :stop_loss,
                    :smart_money_net,
                    NOW()
                )
                ON CONFLICT (trade_date, stock_code)
                DO UPDATE SET
                    stock_name = EXCLUDED.stock_name,
                    total_score = EXCLUDED.total_score,
                    risk_score = EXCLUDED.risk_score,
                    signal = EXCLUDED.signal,
                    confidence = EXCLUDED.confidence,
                    target_price = EXCLUDED.target_price,
                    stop_loss = EXCLUDED.stop_loss,
                    smart_money_net = EXCLUDED.smart_money_net,
                    created_at = NOW()
            """), {
                "trade_date": trade_date,
                "stock_code": r["stock_code"],
                "stock_name": r["stock_name"],
                "total_score": r["total_score"],
                "risk_score": r["risk_score"],
                "signal": signal,
                "confidence": confidence,
                "target_price": target_price,
                "stop_loss": stop_loss,
                "smart_money_net": r["smart_money_net"],
            })

            saved += 1

        db.commit()

    finally:
        db.close()

    print("[RECOMMENDATION HISTORY]", trade_date, "saved:", saved)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    run(args.date, args.limit)
