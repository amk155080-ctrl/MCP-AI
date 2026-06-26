from fastapi import APIRouter
from sqlalchemy import text
from datetime import date

from app.core.database import SessionLocal
from app.api.v9_position_monitor import position_monitor
from app.api.v9_signal_engine import signal_engine

router = APIRouter(
    prefix="/api/v12",
    tags=["MCP 12.12 Performance"]
)


@router.post("/performance/update")
def update_performance():
    db = SessionLocal()

    try:
        monitor = position_monitor()
        signals = signal_engine()

        total_return = monitor.get("total_profit_rate", 0)
        total_profit_loss = monitor.get("total_profit_loss", 0)
        position_count = monitor.get("position_count", 0)

        positions = monitor.get("positions", [])
        profitable = [p for p in positions if p.get("profit_loss", 0) > 0]

        win_rate = round((len(profitable) / len(positions)) * 100, 2) if positions else 0

        avg_profit_rate = round(
            sum([p.get("profit_rate", 0) for p in positions]) / len(positions),
            2
        ) if positions else 0

        signal_count = len(signals.get("signals", []))

        order_count = db.execute(
            text("""
                SELECT COUNT(*) AS count
                FROM mcp4.order_queue
                WHERE order_date = CURRENT_DATE
            """)
        ).mappings().first()["count"]

        db.execute(
            text("""
                INSERT INTO mcp4.strategy_performance (
                    trade_date,
                    total_return,
                    win_rate,
                    avg_profit_rate,
                    total_profit_loss,
                    position_count,
                    signal_count,
                    order_count
                )
                VALUES (
                    :trade_date,
                    :total_return,
                    :win_rate,
                    :avg_profit_rate,
                    :total_profit_loss,
                    :position_count,
                    :signal_count,
                    :order_count
                )
            """),
            {
                "trade_date": date.today(),
                "total_return": total_return,
                "win_rate": win_rate,
                "avg_profit_rate": avg_profit_rate,
                "total_profit_loss": total_profit_loss,
                "position_count": position_count,
                "signal_count": signal_count,
                "order_count": order_count,
            }
        )

        db.commit()

        return {
            "saved": True,
            "version": "MCP 12.12",
            "trade_date": str(date.today()),
            "total_return": total_return,
            "win_rate": win_rate,
            "avg_profit_rate": avg_profit_rate,
            "total_profit_loss": total_profit_loss,
            "position_count": position_count,
            "signal_count": signal_count,
            "order_count": order_count,
            "message": "성과 분석 저장 완료"
        }

    finally:
        db.close()


@router.get("/performance/latest")
def get_latest_performance():
    db = SessionLocal()

    try:
        row = db.execute(
            text("""
                SELECT *
                FROM mcp4.strategy_performance
                ORDER BY id DESC
                LIMIT 1
            """)
        ).mappings().first()

        if not row:
            return {
                "found": False,
                "version": "MCP 12.12",
                "message": "저장된 성과 분석이 없습니다."
            }

        return {
            "found": True,
            "version": "MCP 12.12",
            "item": dict(row),
            "message": "최신 성과 분석 조회 완료"
        }

    finally:
        db.close()


@router.get("/performance/history")
def get_performance_history(limit: int = 30):
    db = SessionLocal()

    try:
        rows = db.execute(
            text("""
                SELECT *
                FROM mcp4.strategy_performance
                ORDER BY id DESC
                LIMIT :limit
            """),
            {"limit": limit}
        ).mappings().all()

        return {
            "found": True,
            "version": "MCP 12.12",
            "count": len(rows),
            "items": [dict(row) for row in rows],
            "message": "성과 분석 이력 조회 완료"
        }

    finally:
        db.close()

