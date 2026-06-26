from fastapi import APIRouter
from sqlalchemy import text
from app.core.database import SessionLocal

router = APIRouter(prefix="/api/v3/portfolio", tags=["portfolio-v3"])


@router.get("/ai_semiconductor")
def ai_semiconductor(trade_date: str):
    db = SessionLocal()

    try:
        rows = db.execute(
            text(
                """
                SELECT
                    trade_date,
                    portfolio_type,
                    rank_no,
                    stock_code,
                    stock_name,
                    total_score,
                    signal,
                    weight
                FROM mcp4.portfolio_position_daily
                WHERE trade_date = :trade_date
                  AND portfolio_type = 'AI_SEMICONDUCTOR'
                ORDER BY rank_no
                """
            ),
            {"trade_date": trade_date},
        ).fetchall()

        items = [dict(r._mapping) for r in rows]

        invested_weight = round(
            sum(float(i["weight"]) for i in items),
            2,
        )

        cash_weight = round(
            100 - invested_weight,
            2,
        )

        return {
            "trade_date": trade_date,
            "portfolio_type": "AI_SEMICONDUCTOR",
            "invested_weight": invested_weight,
            "cash_weight": cash_weight,
            "items": items,
        }

    finally:
        db.close()
