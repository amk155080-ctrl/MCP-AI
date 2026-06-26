from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v9",
    tags=["MCP 9.9 Signal Stats"]
)


@router.get("/signals/stats")
def signal_stats(days: int = 30):

    db = SessionLocal()

    try:
        summary_rows = db.execute(
            text("""
                SELECT
                    signal,
                    COUNT(*) AS count
                FROM mcp4.signal_log
                WHERE created_at >= NOW() - (:days || ' days')::interval
                GROUP BY signal
                ORDER BY count DESC
            """),
            {"days": days}
        ).mappings().all()

        total_count = db.execute(
            text("""
                SELECT COUNT(*) AS count
                FROM mcp4.signal_log
                WHERE created_at >= NOW() - (:days || ' days')::interval
            """),
            {"days": days}
        ).mappings().first()["count"]

        latest_rows = db.execute(
            text("""
                SELECT *
                FROM mcp4.signal_log
                ORDER BY id DESC
                LIMIT 10
            """)
        ).mappings().all()

        signal_counts = {
            "HOLD": 0,
            "SELL": 0,
            "TAKE_PROFIT": 0
        }

        for row in summary_rows:
            signal_counts[row["signal"]] = row["count"]

        return {
            "found": True,
            "version": "MCP 9.9",
            "period_days": days,
            "total_count": total_count,
            "hold_count": signal_counts.get("HOLD", 0),
            "sell_count": signal_counts.get("SELL", 0),
            "take_profit_count": signal_counts.get("TAKE_PROFIT", 0),
            "summary": [dict(row) for row in summary_rows],
            "latest": [dict(row) for row in latest_rows],
            "message": "신호 통계 조회 완료"
        }

    finally:
        db.close()
