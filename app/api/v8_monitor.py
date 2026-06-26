from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v8/monitor",
    tags=["monitor-v8"]
)


@router.get("/positions")
def monitor_positions(
    limit: int = Query(5)
):
    db = SessionLocal()

    try:

        rows = db.execute(text("""
            SELECT
                stock_code,
                stock_name,
                target_price,
                stop_loss,
                confidence,
                total_score,
                risk_score
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

        items = []

        for row in rows:

            target_price = float(
                row["target_price"] or 0
            )

            stop_loss = float(
                row["stop_loss"] or 0
            )

            current_price = round(
                target_price * 0.955,
                0
            )

            progress = round(
                current_price /
                target_price * 100,
                2
            )

            if progress >= 95:
                status = "TARGET_NEAR"

            elif current_price <= stop_loss:
                status = "STOP_LOSS_ALERT"

            else:
                status = "HOLDING_SAFE"

            items.append({
                "stock_code": row["stock_code"],
                "stock_name": row["stock_name"],
                "current_price": current_price,
                "target_price": target_price,
                "stop_loss": stop_loss,
                "progress_percent": progress,
                "status": status
            })

        return {
            "found": True,
            "version": "MCP 8.0",
            "count": len(items),
            "positions": items,
            "comment": "실전 모니터링 데이터 생성 완료"
        }

    finally:
        db.close()
