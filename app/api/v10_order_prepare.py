from fastapi import APIRouter
from sqlalchemy import text
from datetime import date

from app.core.database import SessionLocal
from app.api.v9_signal_engine import signal_engine

router = APIRouter(
    prefix="/api/v10",
    tags=["MCP 10.0 Order Prepare"]
)


@router.get("/orders/prepare")
def prepare_orders():

    db = SessionLocal()

    try:

        signals = signal_engine()

        created = 0

        for item in signals["signals"]:

            if item["signal"] not in [
                "SELL",
                "TAKE_PROFIT"
            ]:
                continue

            db.execute(
                text("""
                    INSERT INTO mcp4.order_queue (
                        order_date,
                        stock_code,
                        stock_name,
                        action,
                        quantity,
                        current_price,
                        reason
                    )
                    VALUES (
                        :order_date,
                        :stock_code,
                        :stock_name,
                        :action,
                        0,
                        :current_price,
                        :reason
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

            created += 1

        db.commit()

        return {
            "found": True,
            "version": "MCP 10.0",
            "created_orders": created,
            "message": "주문 준비 완료"
        }

    finally:
        db.close()
