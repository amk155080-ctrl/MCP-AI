from fastapi import APIRouter
from sqlalchemy import text
from datetime import date
import json

from app.core.database import SessionLocal
from app.api.v9_signal_engine import signal_engine
from app.api.v9_position_monitor import position_monitor
from app.api.v10_order_prepare import prepare_orders
from app.api.v11_kis_trading import place_order
from app.api.v8_daily_report import daily_report

router = APIRouter(
    prefix="/api/v12",
    tags=["MCP 12 Auto Trading Manager"]
)


def json_safe(data):
    return json.dumps(data, ensure_ascii=False, default=str)


def get_config(db):
    row = db.execute(
        text("""
            SELECT *
            FROM mcp4.auto_trading_config
            ORDER BY id DESC
            LIMIT 1
        """)
    ).mappings().first()

    return row


def save_log(db, event_type, message, detail=None):
    db.execute(
        text("""
            INSERT INTO mcp4.auto_trading_log (
                event_type,
                message,
                detail
            )
            VALUES (
                :event_type,
                :message,
                CAST(:detail AS JSONB)
            )
        """),
        {
            "event_type": event_type,
            "message": message,
            "detail": json_safe(detail or {})
        }
    )
    db.commit()


@router.get("/config")
def get_auto_trading_config():
    db = SessionLocal()

    try:
        config = get_config(db)

        if not config:
            return {
                "found": False,
                "version": "MCP 12.0",
                "message": "자동매매 설정이 없습니다."
            }

        return {
            "found": True,
            "version": "MCP 12.0",
            "config": dict(config),
            "message": "자동매매 설정 조회 완료"
        }

    finally:
        db.close()


@router.post("/config/enable")
def enable_auto_trading():
    db = SessionLocal()

    try:
        db.execute(
            text("""
                UPDATE mcp4.auto_trading_config
                SET enabled = TRUE
                WHERE id = (
                    SELECT id
                    FROM mcp4.auto_trading_config
                    ORDER BY id DESC
                    LIMIT 1
                )
            """)
        )
        db.commit()

        save_log(db, "CONFIG", "자동매매 활성화", {"enabled": True})

        return {
            "updated": True,
            "version": "MCP 12.0",
            "enabled": True,
            "message": "자동매매 활성화 완료"
        }

    finally:
        db.close()


@router.post("/config/disable")
def disable_auto_trading():
    db = SessionLocal()

    try:
        db.execute(
            text("""
                UPDATE mcp4.auto_trading_config
                SET enabled = FALSE
                WHERE id = (
                    SELECT id
                    FROM mcp4.auto_trading_config
                    ORDER BY id DESC
                    LIMIT 1
                )
            """)
        )
        db.commit()

        save_log(db, "CONFIG", "자동매매 비활성화", {"enabled": False})

        return {
            "updated": True,
            "version": "MCP 12.0",
            "enabled": False,
            "message": "자동매매 비활성화 완료"
        }

    finally:
        db.close()


@router.post("/config/auto-order/enable")
def enable_auto_order():
    db = SessionLocal()

    try:
        db.execute(
            text("""
                UPDATE mcp4.auto_trading_config
                SET auto_order_enabled = TRUE
                WHERE id = (
                    SELECT id
                    FROM mcp4.auto_trading_config
                    ORDER BY id DESC
                    LIMIT 1
                )
            """)
        )
        db.commit()

        save_log(db, "CONFIG", "자동 실주문 활성화", {"auto_order_enabled": True})

        return {
            "updated": True,
            "version": "MCP 12.0",
            "auto_order_enabled": True,
            "message": "자동 실주문 활성화 완료"
        }

    finally:
        db.close()


@router.post("/config/auto-order/disable")
def disable_auto_order():
    db = SessionLocal()

    try:
        db.execute(
            text("""
                UPDATE mcp4.auto_trading_config
                SET auto_order_enabled = FALSE
                WHERE id = (
                    SELECT id
                    FROM mcp4.auto_trading_config
                    ORDER BY id DESC
                    LIMIT 1
                )
            """)
        )
        db.commit()

        save_log(db, "CONFIG", "자동 실주문 비활성화", {"auto_order_enabled": False})

        return {
            "updated": True,
            "version": "MCP 12.0",
            "auto_order_enabled": False,
            "message": "자동 실주문 비활성화 완료"
        }

    finally:
        db.close()


@router.post("/run-auto-buy")
def run_auto_buy():
    db = SessionLocal()

    try:
        config = get_config(db)

        if not config or not config["enabled"]:
            return {
                "executed": False,
                "version": "MCP 12.1~12.4",
                "message": "자동매매가 비활성화되어 있습니다."
            }

        result = prepare_orders()

        save_log(
            db,
            "AUTO_BUY",
            "자동 매수 준비 실행",
            result
        )

        return {
            "executed": True,
            "version": "MCP 12.1~12.4",
            "result": result,
            "message": "자동 매수 준비 완료"
        }

    finally:
        db.close()


@router.post("/run-monitor")
def run_monitor():
    db = SessionLocal()

    try:
        config = get_config(db)

        if not config or not config["enabled"]:
            return {
                "executed": False,
                "version": "MCP 12.5~12.7",
                "message": "자동매매가 비활성화되어 있습니다."
            }

        monitor = position_monitor()
        signals = signal_engine()

        sell_targets = [
            x for x in signals.get("signals", [])
            if x.get("signal") in ["SELL", "TAKE_PROFIT"]
        ]

        created_orders = 0

        for item in sell_targets:
            db.execute(
                text("""
                    INSERT INTO mcp4.order_queue (
                        order_date,
                        stock_code,
                        stock_name,
                        action,
                        quantity,
                        current_price,
                        reason,
                        status
                    )
                    VALUES (
                        :order_date,
                        :stock_code,
                        :stock_name,
                        :action,
                        0,
                        :current_price,
                        :reason,
                        'READY'
                    )
                """),
                {
                    "order_date": date.today(),
                    "stock_code": item["stock_code"],
                    "stock_name": item["stock_name"],
                    "action": item["signal"],
                    "current_price": item["current_price"],
                    "reason": item["reason"]
                }
            )
            created_orders += 1

        db.commit()

        result = {
            "monitor": monitor,
            "signals": signals,
            "sell_target_count": len(sell_targets),
            "created_orders": created_orders
        }

        save_log(
            db,
            "MONITOR",
            "장중 자동 모니터링 실행",
            result
        )

        return {
            "executed": True,
            "version": "MCP 12.5~12.7",
            "created_orders": created_orders,
            "sell_target_count": len(sell_targets),
            "result": result,
            "message": "자동 모니터링 완료"
        }

    finally:
        db.close()


@router.post("/run-approved-orders")
def run_approved_orders():
    db = SessionLocal()

    try:
        config = get_config(db)

        if not config or not config["enabled"]:
            return {
                "executed": False,
                "version": "MCP 12.4",
                "message": "자동매매가 비활성화되어 있습니다."
            }

        if not config["auto_order_enabled"]:
            return {
                "executed": False,
                "version": "MCP 12.4",
                "message": "자동 실주문이 비활성화되어 있습니다."
            }

        rows = db.execute(
            text("""
                SELECT *
                FROM mcp4.order_queue
                WHERE status = 'APPROVED'
                ORDER BY id ASC
            """)
        ).mappings().all()

        results = []

        for row in rows:
            order_result = place_order(row["id"])
            results.append(order_result)

        save_log(
            db,
            "AUTO_ORDER",
            "승인 주문 자동 실행",
            {"count": len(results), "results": results}
        )

        return {
            "executed": True,
            "version": "MCP 12.4",
            "approved_order_count": len(rows),
            "results": results,
            "message": "승인 주문 자동 실행 완료"
        }

    finally:
        db.close()


@router.post("/run-close")
def run_market_close():
    db = SessionLocal()

    try:
        config = get_config(db)

        if not config or not config["enabled"]:
            return {
                "executed": False,
                "version": "MCP 12.8",
                "message": "자동매매가 비활성화되어 있습니다."
            }

        db.execute(
            text("""
                UPDATE mcp4.order_queue
                SET status = 'CANCELLED'
                WHERE status = 'READY'
            """)
        )

        db.commit()

        stats = db.execute(
            text("""
                SELECT status, COUNT(*) AS count
                FROM mcp4.order_queue
                GROUP BY status
            """)
        ).mappings().all()

        result = {
            "order_status": [dict(x) for x in stats]
        }

        save_log(
            db,
            "MARKET_CLOSE",
            "장마감 정리 실행",
            result
        )

        return {
            "executed": True,
            "version": "MCP 12.8",
            "result": result,
            "message": "장마감 정리 완료"
        }

    finally:
        db.close()


@router.get("/report")
def get_auto_trading_report():
    db = SessionLocal()

    try:
        config = get_config(db)

        monitor = position_monitor()
        signals = signal_engine()

        order_stats = db.execute(
            text("""
                SELECT status, COUNT(*) AS count
                FROM mcp4.order_queue
                GROUP BY status
                ORDER BY status
            """)
        ).mappings().all()

        latest_logs = db.execute(
            text("""
                SELECT *
                FROM mcp4.auto_trading_log
                ORDER BY id DESC
                LIMIT 10
            """)
        ).mappings().all()

        return {
            "found": True,
            "version": "MCP 12.9",
            "config": dict(config) if config else None,
            "monitor": monitor,
            "signals": signals,
            "order_stats": [dict(x) for x in order_stats],
            "latest_logs": [dict(x) for x in latest_logs],
            "message": "자동매매 리포트 조회 완료"
        }

    finally:
        db.close()


@router.get("/logs")
def get_auto_trading_logs(limit: int = 50):
    db = SessionLocal()

    try:
        rows = db.execute(
            text("""
                SELECT *
                FROM mcp4.auto_trading_log
                ORDER BY id DESC
                LIMIT :limit
            """),
            {"limit": limit}
        ).mappings().all()

        return {
            "found": True,
            "version": "MCP 12.9",
            "count": len(rows),
            "items": [dict(x) for x in rows],
            "message": "자동매매 로그 조회 완료"
        }

    finally:
        db.close()
