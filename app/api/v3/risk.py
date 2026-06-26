from fastapi import APIRouter
from sqlalchemy import text
from app.core.database import SessionLocal

router = APIRouter(prefix="/api/v3/risk", tags=["risk-v3"])


@router.get("/portfolio")
def portfolio_risk(trade_date: str, portfolio_type: str = "AI_SEMICONDUCTOR"):
    db = SessionLocal()

    try:
        row = db.execute(
            text(
                """
                SELECT
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
                FROM mcp4.portfolio_risk_daily
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
                "message": "no risk data",
            }

        return dict(row._mapping)

    finally:
        db.close()
