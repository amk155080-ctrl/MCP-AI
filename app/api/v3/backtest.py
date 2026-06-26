from fastapi import APIRouter
from sqlalchemy import text
from app.core.database import SessionLocal

router = APIRouter(prefix="/api/v3/backtest", tags=["backtest-v3"])


@router.get("/report")
def backtest_report(trade_date: str, portfolio_type: str = "AI_SEMICONDUCTOR"):
    db = SessionLocal()

    try:
        row = db.execute(
            text(
                """
                SELECT *
                FROM mcp4.backtest_report
                WHERE trade_date = :trade_date
                  AND portfolio_type = :portfolio_type
                LIMIT 1
                """
            ),
            {
                "trade_date": trade_date,
                "portfolio_type": portfolio_type,
            },
        ).fetchone()

        if not row:
            return {
                "trade_date": trade_date,
                "portfolio_type": portfolio_type,
                "message": "no backtest data",
            }

        return dict(row._mapping)

    finally:
        db.close()
