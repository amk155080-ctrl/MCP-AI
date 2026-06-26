import argparse
from datetime import datetime
from sqlalchemy import text
from app.core.database import SessionLocal


def grade(score):
    if score >= 90:
        return "SS"
    if score >= 80:
        return "S"
    if score >= 70:
        return "A"
    if score >= 60:
        return "B"
    return "C"


def signal(score):
    if score >= 90:
        return "STRONG_BUY"
    if score >= 80:
        return "BUY"
    if score >= 60:
        return "HOLD"
    if score >= 40:
        return "WATCH"
    return "SELL"


def score_net_buy(value):
    value = float(value or 0)

    if value >= 100000000000:
        return 95
    if value >= 50000000000:
        return 85
    if value >= 10000000000:
        return 75
    if value > 0:
        return 65
    if value == 0:
        return 50
    if value > -10000000000:
        return 40
    return 30


def calc_flow_score(row):
    foreign_score = score_net_buy(row.foreign_net)
    institution_score = score_net_buy(row.institution_net)
    pension_score = score_net_buy(row.pension_net)
    program_score = score_net_buy(row.program_net)

    return round(
        foreign_score * 0.35 +
        institution_score * 0.35 +
        pension_score * 0.20 +
        program_score * 0.10,
        2,
    )


def run(trade_date):
    db = SessionLocal()

    try:
        market = db.execute(
            text(
                """
                SELECT total_score
                FROM mcp4.market_regime_daily
                WHERE trade_date = :trade_date
                LIMIT 1
                """
            ),
            {"trade_date": trade_date},
        ).fetchone()

        market_score = float(market.total_score) if market else 50.0

        rows = db.execute(
            text(
                """
                SELECT
                    s.trade_date,
                    s.stock_code,
                    s.stock_name,
                    s.total_score AS semiconductor_score,

                    i.foreign_net,
                    i.institution_net,
                    i.pension_net,
                    i.program_net,

                    COALESCE(e.total_score, 50) AS earnings_score,
                    COALESCE(sl.total_score, 50) AS short_loan_score

                FROM mcp4.semiconductor_score_daily s

                LEFT JOIN mcp4.investor_flow_daily i
                    ON s.trade_date = i.trade_date
                   AND s.stock_code = i.stock_code

                LEFT JOIN mcp4.earnings_score_manual e
                    ON s.trade_date = e.trade_date
                   AND s.stock_code = e.stock_code

                LEFT JOIN mcp4.short_loan_daily sl
                    ON s.trade_date = sl.trade_date
                   AND s.stock_code = sl.stock_code

                WHERE s.trade_date = :trade_date
                """
            ),
            {"trade_date": trade_date},
        ).fetchall()

        for r in rows:
            semiconductor_score = float(r.semiconductor_score or 0)

            if r.foreign_net is not None:
                flow_score = calc_flow_score(r)
            else:
                flow_score = 50.0

            earnings_score = float(r.earnings_score or 50)
            short_loan_score = float(r.short_loan_score or 50)

            valuation_score = 55.0
            risk_score = short_loan_score

            total = round(
                market_score * 0.10 +
                semiconductor_score * 0.30 +
                flow_score * 0.25 +
                earnings_score * 0.18 +
                valuation_score * 0.05 +
                risk_score * 0.12,
                2,
            )

            db.execute(
                text(
                    """
                    INSERT INTO mcp4.institutional_score_daily
                    (
                        trade_date,
                        stock_code,
                        stock_name,
                        market_score,
                        semiconductor_score,
                        flow_score,
                        earnings_score,
                        valuation_score,
                        risk_score,
                        total_score,
                        grade,
                        signal
                    )
                    VALUES
                    (
                        :trade_date,
                        :stock_code,
                        :stock_name,
                        :market_score,
                        :semiconductor_score,
                        :flow_score,
                        :earnings_score,
                        :valuation_score,
                        :risk_score,
                        :total_score,
                        :grade,
                        :signal
                    )
                    ON CONFLICT (trade_date, stock_code)
                    DO UPDATE SET
                        stock_name = EXCLUDED.stock_name,
                        market_score = EXCLUDED.market_score,
                        semiconductor_score = EXCLUDED.semiconductor_score,
                        flow_score = EXCLUDED.flow_score,
                        earnings_score = EXCLUDED.earnings_score,
                        valuation_score = EXCLUDED.valuation_score,
                        risk_score = EXCLUDED.risk_score,
                        total_score = EXCLUDED.total_score,
                        grade = EXCLUDED.grade,
                        signal = EXCLUDED.signal
                    """
                ),
                {
                    "trade_date": trade_date,
                    "stock_code": r.stock_code,
                    "stock_name": r.stock_name,
                    "market_score": market_score,
                    "semiconductor_score": semiconductor_score,
                    "flow_score": flow_score,
                    "earnings_score": earnings_score,
                    "valuation_score": valuation_score,
                    "risk_score": risk_score,
                    "total_score": total,
                    "grade": grade(total),
                    "signal": signal(total),
                },
            )

        db.commit()

    finally:
        db.close()

    print("[INSTITUTIONAL V5 SHORT LOAN]", trade_date, "saved")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    args = parser.parse_args()
    run(args.date)
