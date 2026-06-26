from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(prefix="/api/v5/backtest", tags=["backtest-v5"])


@router.get("/top")
def backtest_top(
    date: str = Query(..., description="기준일 YYYYMMDD"),
    days: int = Query(5, description="N영업일 후"),
    limit: int = Query(20, description="추천 종목 수"),
):
    trade_date = f"{date[0:4]}-{date[4:6]}-{date[6:8]}"

    db = SessionLocal()

    try:
        target_date_row = db.execute(text("""
            SELECT trade_date
            FROM mcp4.stock_price_daily
            WHERE trade_date > :trade_date
            GROUP BY trade_date
            ORDER BY trade_date
            OFFSET :offset_days
            LIMIT 1
        """), {
            "trade_date": trade_date,
            "offset_days": max(days - 1, 0),
        }).fetchone()

        if not target_date_row:
            return {
                "found": False,
                "message": "N영업일 후 가격 데이터가 없습니다.",
                "trade_date": trade_date,
                "days": days,
            }

        target_date = target_date_row[0]

        rows = db.execute(text("""
            SELECT
                r.trade_date AS buy_date,
                :target_date AS sell_date,
                r.stock_code,
                r.stock_name,
                r.total_score,
                r.signal,
                r.confidence,
                r.target_price,
                r.stop_loss,
                r.smart_money_net,

                buy.close_price AS buy_price,
                sell.close_price AS sell_price,

                ROUND(
                    (
                        (sell.close_price - buy.close_price)
                        / NULLIF(buy.close_price, 0)
                    ) * 100,
                    2
                ) AS return_percent,

                CASE
                    WHEN sell.close_price > buy.close_price THEN 1
                    ELSE 0
                END AS win

            FROM mcp4.recommendation_history r

            JOIN mcp4.stock_price_daily buy
              ON r.trade_date = buy.trade_date
             AND r.stock_code = buy.stock_code

            JOIN mcp4.stock_price_daily sell
              ON sell.trade_date = :target_date
             AND r.stock_code = sell.stock_code

            WHERE r.trade_date = :trade_date

            ORDER BY r.total_score DESC

            LIMIT :limit
        """), {
            "trade_date": trade_date,
            "target_date": target_date,
            "limit": limit,
        }).mappings().all()

        if not rows:
            return {
                "found": False,
                "message": "백테스트 대상 추천 이력이 없습니다.",
                "trade_date": trade_date,
                "target_date": str(target_date),
            }

        items = [dict(r) for r in rows]

        returns = [
            float(r["return_percent"] or 0)
            for r in items
        ]

        win_count = sum(
            int(r["win"] or 0)
            for r in items
        )

        avg_return = round(
            sum(returns) / len(returns),
            2
        )

        win_rate = round(
            win_count / len(items) * 100,
            2
        )

        best = max(returns)
        worst = min(returns)

        return {
            "found": True,
            "trade_date": trade_date,
            "target_date": str(target_date),
            "days": days,
            "count": len(items),
            "average_return_percent": avg_return,
            "win_rate_percent": win_rate,
            "best_return_percent": best,
            "worst_return_percent": worst,
            "items": items,
        }

    finally:
        db.close()



@router.get("/summary")
def backtest_summary(
    date: str = Query(..., description="기준일 YYYYMMDD"),
    days: int = Query(5, description="N영업일 후"),
    limit: int = Query(20, description="추천 종목 수"),
):
    trade_date = f"{date[0:4]}-{date[4:6]}-{date[6:8]}"

    db = SessionLocal()

    try:
        target_date_row = db.execute(text("""
            SELECT trade_date
            FROM mcp4.stock_price_daily
            WHERE trade_date > :trade_date
            GROUP BY trade_date
            ORDER BY trade_date
            OFFSET :offset_days
            LIMIT 1
        """), {
            "trade_date": trade_date,
            "offset_days": max(days - 1, 0),
        }).fetchone()

        if not target_date_row:
            return {
                "found": False,
                "message": "N영업일 후 가격 데이터가 없습니다.",
                "trade_date": trade_date,
                "days": days,
            }

        target_date = target_date_row[0]

        rows = db.execute(text("""
            SELECT
                r.stock_code,
                r.stock_name,
                buy.close_price AS buy_price,
                sell.close_price AS sell_price,
                ROUND(
                    (
                        (sell.close_price - buy.close_price)
                        / NULLIF(buy.close_price, 0)
                    ) * 100,
                    2
                ) AS return_percent,
                CASE
                    WHEN sell.close_price > buy.close_price THEN 1
                    ELSE 0
                END AS win
            FROM mcp4.recommendation_history r
            JOIN mcp4.stock_price_daily buy
              ON r.trade_date = buy.trade_date
             AND r.stock_code = buy.stock_code
            JOIN mcp4.stock_price_daily sell
              ON sell.trade_date = :target_date
             AND r.stock_code = sell.stock_code
            WHERE r.trade_date = :trade_date
            ORDER BY r.total_score DESC
            LIMIT :limit
        """), {
            "trade_date": trade_date,
            "target_date": target_date,
            "limit": limit,
        }).mappings().all()

        if not rows:
            return {
                "found": False,
                "message": "백테스트 대상 추천 이력이 없습니다.",
                "trade_date": trade_date,
            }

        returns = [float(r["return_percent"] or 0) for r in rows]
        win_count = sum(int(r["win"] or 0) for r in rows)

        avg_return = round(sum(returns) / len(returns), 2)
        win_rate = round(win_count / len(rows) * 100, 2)
        best = round(max(returns), 2)
        worst = round(min(returns), 2)

        db.execute(text("""
            INSERT INTO mcp4.backtest_summary_daily
            (
                trade_date,
                target_date,
                days,
                strategy_name,
                recommendation_count,
                average_return_percent,
                win_rate_percent,
                best_return_percent,
                worst_return_percent,
                created_at
            )
            VALUES
            (
                :trade_date,
                :target_date,
                :days,
                'MCP5_TOP20',
                :recommendation_count,
                :average_return_percent,
                :win_rate_percent,
                :best_return_percent,
                :worst_return_percent,
                NOW()
            )
            ON CONFLICT (trade_date, days, strategy_name)
            DO UPDATE SET
                target_date = EXCLUDED.target_date,
                recommendation_count = EXCLUDED.recommendation_count,
                average_return_percent = EXCLUDED.average_return_percent,
                win_rate_percent = EXCLUDED.win_rate_percent,
                best_return_percent = EXCLUDED.best_return_percent,
                worst_return_percent = EXCLUDED.worst_return_percent,
                created_at = NOW()
        """), {
            "trade_date": trade_date,
            "target_date": target_date,
            "days": days,
            "recommendation_count": len(rows),
            "average_return_percent": avg_return,
            "win_rate_percent": win_rate,
            "best_return_percent": best,
            "worst_return_percent": worst,
        })

        db.commit()

        return {
            "found": True,
            "saved": True,
            "trade_date": trade_date,
            "target_date": str(target_date),
            "days": days,
            "strategy_name": "MCP5_TOP20",
            "recommendation_count": len(rows),
            "average_return_percent": avg_return,
            "win_rate_percent": win_rate,
            "best_return_percent": best,
            "worst_return_percent": worst,
        }

    finally:
        db.close()

@router.get("/grade")
def backtest_grade():

    metrics = backtest_metrics()

    if not metrics.get("found"):
        return metrics

    win_rate = metrics["win_rate_percent"]
    profit_factor = metrics["profit_factor"] or 0
    sharpe_ratio = metrics["sharpe_ratio"] or 0
    mdd = metrics["max_drawdown_percent"]

    score = 0
    score += min(win_rate, 100) * 0.30
    score += min(profit_factor / 3.0, 1.0) * 30
    score += min(sharpe_ratio / 2.0, 1.0) * 20

    if mdd >= -10:
        score += 20
    elif mdd >= -15:
        score += 15
    elif mdd >= -20:
        score += 10
    elif mdd >= -30:
        score += 5

    score = round(score, 2)

    if win_rate >= 70 and profit_factor >= 2.5 and sharpe_ratio >= 1.0 and mdd > -15:
        grade = "A+"
        comment = "매우 우수한 전략"
    elif win_rate >= 60 and profit_factor >= 2.0 and sharpe_ratio >= 0.5 and mdd > -20:
        grade = "A"
        comment = "실전 운용 가능"
    elif win_rate >= 50 and profit_factor >= 1.5:
        grade = "B"
        comment = "개선 여지 존재"
    else:
        grade = "C"
        comment = "전략 개선 필요"

    return {
        "found": True,
        "grade": grade,
        "score": score,
        "win_rate_percent": win_rate,
        "profit_factor": profit_factor,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown_percent": mdd,
        "comment": comment
    }

@router.get("/summary/list")
def backtest_summary_list(
    limit: int = Query(30, description="조회 개수"),
):
    db = SessionLocal()

    try:
        rows = db.execute(text("""
            SELECT
                trade_date,
                target_date,
                days,
                strategy_name,
                recommendation_count,
                average_return_percent,
                win_rate_percent,
                best_return_percent,
                worst_return_percent,
                created_at
            FROM mcp4.backtest_summary_daily
            ORDER BY trade_date DESC, days ASC
            LIMIT :limit
        """), {
            "limit": limit
        }).mappings().all()

        return {
            "found": True,
            "count": len(rows),
            "items": [dict(r) for r in rows],
        }

    finally:
        db.close()


@router.get("/performance")
def performance():
    db = SessionLocal()

    try:
        row = db.execute(text("""
            SELECT
                COUNT(*) AS trades,

                ROUND(
                    AVG(return_percent),
                    2
                ) AS avg_return,

                ROUND(
                    AVG(
                        CASE
                            WHEN return_percent > 0
                            THEN 1
                            ELSE 0
                        END
                    ) * 100,
                    2
                ) AS win_rate,

                MAX(return_percent) AS best_trade,

                MIN(return_percent) AS worst_trade

            FROM mcp4.backtest_result_daily
        """)).mappings().first()

        return dict(row)

    finally:
        db.close()


@router.get("/metrics")
def backtest_metrics():
    db = SessionLocal()

    try:
        rows = db.execute(text("""
            SELECT
                return_percent
            FROM mcp4.backtest_result_daily
            ORDER BY buy_date, stock_code
        """)).fetchall()

        returns = [
            float(r[0])
            for r in rows
            if r[0] is not None
        ]

        if not returns:
            return {
                "found": False,
                "message": "백테스트 결과 데이터가 없습니다."
            }

        trades = len(returns)

        wins = [r for r in returns if r > 0]
        losses = [r for r in returns if r < 0]

        avg_return = round(sum(returns) / trades, 2)
        win_rate = round(len(wins) / trades * 100, 2)

        avg_win = round(sum(wins) / len(wins), 2) if wins else 0
        avg_loss = round(sum(losses) / len(losses), 2) if losses else 0

        total_profit = sum(wins)
        total_loss = abs(sum(losses))

        profit_factor = round(total_profit / total_loss, 2) if total_loss > 0 else None
        payoff_ratio = round(avg_win / abs(avg_loss), 2) if avg_loss < 0 else None

        # 샤프비율: 단순 수익률 기준, 무위험수익률 0 가정
        mean = sum(returns) / trades
        variance = sum((r - mean) ** 2 for r in returns) / trades
        std = variance ** 0.5

        sharpe_ratio = round(mean / std, 2) if std > 0 else None

        # MDD 계산: 수익률을 순차 누적한 equity curve 기준
        equity = 1.0
        peak = 1.0
        mdd = 0.0

        for r in returns:
            equity *= (1 + r / 100)
            if equity > peak:
                peak = equity
            drawdown = (equity - peak) / peak * 100
            if drawdown < mdd:
                mdd = drawdown

        mdd = round(mdd, 2)

        return {
            "found": True,
            "strategy_name": "MCP5_TOP20",
            "trades": trades,

            "average_return_percent": avg_return,
            "win_rate_percent": win_rate,

            "average_win_percent": avg_win,
            "average_loss_percent": avg_loss,

            "profit_factor": profit_factor,
            "payoff_ratio": payoff_ratio,

            "sharpe_ratio": sharpe_ratio,
            "max_drawdown_percent": mdd,

            "best_trade_percent": round(max(returns), 2),
            "worst_trade_percent": round(min(returns), 2),
        }

    finally:
        db.close()
