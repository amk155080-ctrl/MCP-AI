import argparse
from datetime import datetime
from sqlalchemy import text
from app.core.database import SessionLocal


def risk_grade(avg_risk_score):
    if avg_risk_score >= 85:
        return "LOW_RISK"
    if avg_risk_score >= 70:
        return "NORMAL_RISK"
    if avg_risk_score >= 55:
        return "ELEVATED_RISK"
    return "HIGH_RISK"


def estimate_var95(avg_risk_score):
    # 점수가 높을수록 손실 위험 낮음
    if avg_risk_score >= 85:
        return -3.0
    if avg_risk_score >= 70:
        return -5.0
    if avg_risk_score >= 55:
        return -8.0
    return -12.0


def estimate_drawdown(avg_risk_score):
    if avg_risk_score >= 85:
        return -10.0
    if avg_risk_score >= 70:
        return -18.0
    if avg_risk_score >= 55:
        return -25.0
    return -35.0


def run(trade_date, portfolio_type):
    db = SessionLocal()

    try:
        positions = db.execute(
            text(
                """
                SELECT
                    p.stock_code,
                    p.stock_name,
                    p.weight,
                    p.total_score,
                    COALESCE(i.risk_score, 50) AS risk_score
                FROM mcp4.portfolio_position_daily p
                LEFT JOIN mcp4.institutional_score_daily i
                    ON p.trade_date = i.trade_date
                   AND p.stock_code = i.stock_code
                WHERE p.trade_date = :trade_date
                  AND p.portfolio_type = :portfolio_type
                """
            ),
            {
                "trade_date": trade_date,
                "portfolio_type": portfolio_type,
            },
        ).fetchall()

        if not positions:
            print("[RISK] no portfolio positions")
            return

        invested_weight = round(
            sum(float(p.weight or 0) for p in positions),
            2,
        )

        cash_weight = round(100 - invested_weight, 2)

        weighted_score_sum = 0
        weighted_risk_sum = 0

        for p in positions:
            w = float(p.weight or 0)

            weighted_score_sum += float(p.total_score or 0) * w
            weighted_risk_sum += float(p.risk_score or 0) * w

        avg_score = round(weighted_score_sum / invested_weight, 2)
        avg_risk_score = round(weighted_risk_sum / invested_weight, 2)

        grade = risk_grade(avg_risk_score)
        var95 = estimate_var95(avg_risk_score)
        drawdown = estimate_drawdown(avg_risk_score)

        db.execute(
            text(
                """
                INSERT INTO mcp4.portfolio_risk_daily
                (
                    trade_date,
                    portfolio_type,
                    invested_weight,
                    cash_weight,
                    avg_score,
                    avg_risk_score,
                    portfolio_risk_grade,
                    var95,
                    expected_drawdown,
                    memo
                )
                VALUES
                (
                    :trade_date,
                    :portfolio_type,
                    :invested_weight,
                    :cash_weight,
                    :avg_score,
                    :avg_risk_score,
                    :portfolio_risk_grade,
                    :var95,
                    :expected_drawdown,
                    :memo
                )
                ON CONFLICT (trade_date, portfolio_type)
                DO UPDATE SET
                    invested_weight = EXCLUDED.invested_weight,
                    cash_weight = EXCLUDED.cash_weight,
                    avg_score = EXCLUDED.avg_score,
                    avg_risk_score = EXCLUDED.avg_risk_score,
                    portfolio_risk_grade = EXCLUDED.portfolio_risk_grade,
                    var95 = EXCLUDED.var95,
                    expected_drawdown = EXCLUDED.expected_drawdown,
                    memo = EXCLUDED.memo
                """
            ),
            {
                "trade_date": trade_date,
                "portfolio_type": portfolio_type,
                "invested_weight": invested_weight,
                "cash_weight": cash_weight,
                "avg_score": avg_score,
                "avg_risk_score": avg_risk_score,
                "portfolio_risk_grade": grade,
                "var95": var95,
                "expected_drawdown": drawdown,
                "memo": "포트폴리오 구성 종목 risk_score 가중평균 기반 리스크 추정",
            },
        )

        db.commit()

    finally:
        db.close()

    print("[RISK]", trade_date, portfolio_type, "saved")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--portfolio", default="AI_SEMICONDUCTOR")
    args = parser.parse_args()

    run(args.date, args.portfolio)
