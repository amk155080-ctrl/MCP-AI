import argparse
from datetime import datetime

from sqlalchemy import text

from app.core.database import SessionLocal


def grade(score):
    if score >= 65:
        return "A"
    if score >= 58:
        return "B"
    if score >= 50:
        return "C"
    return "D"


def clamp(v, low=0, high=100):
    return max(low, min(high, v))


def flow_component_score(net_value, market_cap):
    net_value = float(net_value or 0)
    market_cap = float(market_cap or 0)

    if market_cap <= 0:
        return 50

    ratio = net_value / market_cap * 100

    if ratio >= 0.30:
        return 95
    if ratio >= 0.15:
        return 85
    if ratio >= 0.05:
        return 75
    if ratio > 0:
        return 60
    if ratio == 0:
        return 50
    if ratio >= -0.05:
        return 40
    if ratio >= -0.15:
        return 30
    return 20


def calc_supply_score(foreign_net, institution_net, pension_net, program_net, market_cap):
    foreign_score = flow_component_score(foreign_net, market_cap)
    institution_score = flow_component_score(institution_net, market_cap)
    pension_score = flow_component_score(pension_net, market_cap)
    program_score = flow_component_score(program_net, market_cap)

    return round(
        foreign_score * 0.35 +
        institution_score * 0.35 +
        pension_score * 0.20 +
        program_score * 0.10,
        2
    )


def run(bas_dd):
    trade_date = f"{bas_dd[0:4]}-{bas_dd[4:6]}-{bas_dd[6:8]}"

    db = SessionLocal()

    try:
        rows = db.execute(text("""
            SELECT
                p.trade_date,
                p.stock_code,
                p.stock_name,
                COALESCE(p.change_rate, 0) AS change_rate,
                COALESCE(p.trade_value, 0) AS trade_value,
                COALESCE(p.market_cap, 0) AS market_cap,
                COALESCE(f.foreign_net, 0) AS foreign_net,
                COALESCE(f.institution_net, 0) AS institution_net,
                COALESCE(f.pension_net, 0) AS pension_net,
                COALESCE(f.program_net, 0) AS program_net
            FROM mcp4.stock_price_daily p
            LEFT JOIN mcp4.investor_flow_daily f
              ON p.trade_date = f.trade_date
             AND p.stock_code = f.stock_code
            WHERE p.trade_date = :trade_date
        """), {"trade_date": trade_date}).mappings().all()

        saved = 0

        for r in rows:
            change_rate = float(r["change_rate"] or 0)
            trade_value = float(r["trade_value"] or 0)
            market_cap = float(r["market_cap"] or 0)

            supply_score = calc_supply_score(
                r["foreign_net"],
                r["institution_net"],
                r["pension_net"],
                r["program_net"],
                market_cap,
            )

            momentum_score = clamp(50 + change_rate * 3)

            liquidity_score = 50
            if trade_value >= 100000000000:
                liquidity_score = 80
            elif trade_value >= 30000000000:
                liquidity_score = 70
            elif trade_value >= 10000000000:
                liquidity_score = 60
            elif trade_value <= 1000000000:
                liquidity_score = 35

            size_score = 50
            if market_cap >= 10000000000000:
                size_score = 75
            elif market_cap >= 1000000000000:
                size_score = 65
            elif market_cap <= 100000000000:
                size_score = 40

            macro_score = 56
            semiconductor_score = 50
            risk_score = round(size_score * 0.6 + liquidity_score * 0.4, 2)

            total_score = round(
                supply_score * 0.40 +
                momentum_score * 0.20 +
                macro_score * 0.15 +
                semiconductor_score * 0.10 +
                risk_score * 0.15,
                2
            )

            db.execute(text("""
                INSERT INTO mcp4.stock_score_daily
                (
                    trade_date,
                    stock_code,
                    stock_name,
                    supply_score,
                    momentum_score,
                    macro_score,
                    semiconductor_score,
                    risk_score,
                    total_score,
                    grade,
                    created_at
                )
                VALUES
                (
                    :trade_date,
                    :stock_code,
                    :stock_name,
                    :supply_score,
                    :momentum_score,
                    :macro_score,
                    :semiconductor_score,
                    :risk_score,
                    :total_score,
                    :grade,
                    NOW()
                )
                ON CONFLICT (trade_date, stock_code)
                DO UPDATE SET
                    stock_name = EXCLUDED.stock_name,
                    supply_score = EXCLUDED.supply_score,
                    momentum_score = EXCLUDED.momentum_score,
                    macro_score = EXCLUDED.macro_score,
                    semiconductor_score = EXCLUDED.semiconductor_score,
                    risk_score = EXCLUDED.risk_score,
                    total_score = EXCLUDED.total_score,
                    grade = EXCLUDED.grade
            """), {
                "trade_date": trade_date,
                "stock_code": r["stock_code"],
                "stock_name": r["stock_name"],
                "supply_score": supply_score,
                "momentum_score": momentum_score,
                "macro_score": macro_score,
                "semiconductor_score": semiconductor_score,
                "risk_score": risk_score,
                "total_score": total_score,
                "grade": grade(total_score),
            })

            saved += 1

        db.commit()

    finally:
        db.close()

    print("[STOCK SCORE ALL V4.2 FLOW]", trade_date, "saved:", saved)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    run(args.date)
