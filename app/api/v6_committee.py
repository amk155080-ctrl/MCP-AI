from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v6/investment",
    tags=["committee-v6"]
)


@router.get("/committee")
def investment_committee(
    limit: int = Query(5)
):

    db = SessionLocal()

    try:

        rows = db.execute(text("""
            SELECT
                trade_date,
                stock_code,
                stock_name,
                total_score,
                risk_score,
                signal,
                confidence,
                target_price,
                stop_loss,
                smart_money_net
            FROM mcp4.recommendation_history
            WHERE trade_date = (
                SELECT MAX(trade_date)
                FROM mcp4.recommendation_history
            )
            ORDER BY total_score DESC
            LIMIT :limit
        """), {
            "limit": limit
        }).mappings().all()

        if not rows:
            return {
                "found": False
            }

        results = []

        for row in rows:

            total_score = float(row["total_score"] or 0)
            risk_score = float(row["risk_score"] or 0)
            confidence = float(row["confidence"] or 0)

            committee_score = (
                total_score * 0.5 +
                risk_score * 0.2 +
                confidence * 0.3
            )

            committee_score = round(
                committee_score,
                2
            )

            if committee_score >= 80:
                final_signal = "STRONG_BUY"

            elif committee_score >= 70:
                final_signal = "BUY"

            elif committee_score >= 60:
                final_signal = "HOLD"

            else:
                final_signal = "SELL"

            results.append({
                "stock_code": row["stock_code"],
                "stock_name": row["stock_name"],
                "committee_score": committee_score,
                "final_signal": final_signal,
                "total_score": total_score,
                "risk_score": risk_score,
                "confidence": confidence,
                "target_price": float(
                    row["target_price"] or 0
                ),
                "stop_loss": float(
                    row["stop_loss"] or 0
                ),
                "smart_money_net": int(
                    row["smart_money_net"] or 0
                )
            })

        results.sort(
            key=lambda x: x["committee_score"],
            reverse=True
        )

        return {
            "found": True,
            "version": "MCP 6.0",
            "candidate_count": len(results),
            "top_pick": results[0],
            "candidates": results
        }

    finally:
        db.close()
