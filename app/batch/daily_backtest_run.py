import argparse
from datetime import datetime
from sqlalchemy import text
from app.core.database import SessionLocal


def estimate_return(score):
    if score >= 90:
        return 0.035
    if score >= 80:
        return 0.025
    if score >= 70:
        return 0.015
    if score >= 60:
        return 0.005
    return -0.01


def run(trade_date, portfolio_type, initial_capital):
    db = SessionLocal()

    try:
        positions = db.execute(
            text(
                """
                SELECT
                    stock_code,
                    stock_name,
                    total_score,
                    weight
                FROM mcp4.portfolio_position_daily
                WHERE trade_date = :trade_date
                  AND portfolio_type = :portfolio_type
                ORDER BY rank_no
                """
            ),
            {
                "trade_date": trade_date,
                "portfolio_type": portfolio_type,
            },
        ).fetchall()

        if not positions:
            print("[BACKTEST] no portfolio positions")
            return

        portfolio_return = 0
        win_count = 0

        for p in positions:
            score = float(p.total_score or 0)
            weight = float(p.weight or 0) / 100

            r = estimate_return(score)
            portfolio_return += weight * r

            if r > 0:
                win_count += 1

        final_capital = round(initial_capital * (1 + portfolio_return), 2)
        total_return = round(portfolio_return * 100, 2)

        win_rate = round(win_count / len(positions) * 100, 2)

        if total_return >= 2:
            sharpe = 1.5
        elif total_return >= 1:
            sharpe = 1.0
        elif total_return >= 0:
            sharpe = 0.5
        else:
            sharpe = -0.5

        mdd = -8.0 if total_return > 0 else -15.0
        cagr = total_return

        db.execute(
            text(
                """
                INSERT INTO mcp4.backtest_report
                (
                    trade_date,
                    portfolio_type,
                    initial_capital,
                    final_capital,
                    total_return,
                    cagr,
                    mdd,
                    win_rate,
                    sharpe,
                    memo
                )
                VALUES
                (
                    :trade_date,
                    :portfolio_type,
                    :initial_capital,
                    :final_capital,
                    :total_return,
                    :cagr,
                    :mdd,
                    :win_rate,
                    :sharpe,
                    :memo
                )
                ON CONFLICT (trade_date, portfolio_type)
                DO UPDATE SET
                    initial_capital = EXCLUDED.initial_capital,
                    final_capital = EXCLUDED.final_capital,
                    total_return = EXCLUDED.total_return,
                    cagr = EXCLUDED.cagr,
                    mdd = EXCLUDED.mdd,
                    win_rate = EXCLUDED.win_rate,
                    sharpe = EXCLUDED.sharpe,
                    memo = EXCLUDED.memo
                """
            ),
            {
                "trade_date": trade_date,
                "portfolio_type": portfolio_type,
                "initial_capital": initial_capital,
                "final_capital": final_capital,
                "total_return": total_return,
                "cagr": cagr,
                "mdd": mdd,
                "win_rate": win_rate,
                "sharpe": sharpe,
                "memo": "기관 점수 기반 포트폴리오 단순 기대수익 백테스트",
            },
        )

        db.commit()

    finally:
        db.close()

    print("[BACKTEST]", trade_date, portfolio_type, "saved")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--portfolio", default="AI_SEMICONDUCTOR")
    parser.add_argument("--capital", type=float, default=10000000)
    args = parser.parse_args()

    run(args.date, args.portfolio, args.capital)
