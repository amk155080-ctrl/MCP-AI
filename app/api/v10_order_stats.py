from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v10",
    tags=["MCP 10.5 Order Stats"]
)


@router.get("/orders/stats")
def order_stats(days: int = 30):

    db = SessionLocal()

    try:

        summary_rows = db.execute(
            text("""
                SELECT
                    status,
                    COUNT(*) AS count
                FROM mcp4.order_queue
                WHERE created_at >= NOW() - (:days || ' days')::interval
                GROUP BY status
                ORDER BY count DESC
            """),
            {"days": days}
        ).mappings().all()

        total_count = db.execute(
            text("""
                SELECT COUNT(*) AS count
                FROM mcp4.order_queue
                WHERE created_at >= NOW() - (:days || ' days')::interval
            """),
            {"days": days}
        ).mappings().first()["count"]

        latest_orders = db.execute(
            text("""
                SELECT *
                FROM mcp4.order_queue
                ORDER BY id DESC
                LIMIT 10
            """)
        ).mappings().all()

        stats = {
            "READY": 0,
            "APPROVED": 0,
            "CANCELLED": 0
        }

        for row in summary_rows:
            stats[row["status"]] = row["count"]

        return {
            "found": True,
            "version": "MCP 10.5",
            "period_days": days,
            "total_orders": total_count,
            "ready_count": stats.get("READY", 0),
            "approved_count": stats.get("APPROVED", 0),
            "cancelled_count": stats.get("CANCELLED", 0),
            "summary": [dict(x) for x in summary_rows],
            "latest_orders": [dict(x) for x in latest_orders],
            "message": "주문 통계 조회 완료"
        }

    finally:
        db.close()
