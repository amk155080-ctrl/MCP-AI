from fastapi import APIRouter
from sqlalchemy import text
from datetime import date

from app.core.database import SessionLocal
from app.api.v9_signal_engine import signal_engine

router = APIRouter(
    prefix="/api/v9",
    tags=["MCP 9.7 Signal Save"]
)


@router.get("/signals/save")
def save_signals():

    db = SessionLocal()

    try:

        result = signal_engine()

        if not result.get("found"):
            return {
                "saved": False,
                "message": "신호 생성 실패"
            }

        saved_count = 0

        for item in result["signals"]:

            db.execute(
                text("""
                    INSERT INTO mcp4.signal_log (
                        signal_date,
                        stock_code,
                        stock_name,
                        signal,
                        reason,
                        current_price,
                        target_price,
                        stop_price
                    )
                    VALUES (
                        :signal_date,
                        :stock_code,
                        :stock_name,
                        :signal,
                        :reason,
                        :current_price,
                        :target_price,
                        :stop_price
                    )
                """),
                {
                    "signal_date": date.today(),
                    "stock_code": item["stock_code"],
                    "stock_name": item["stock_name"],
                    "signal": item["signal"],
                    "reason": item["reason"],
                    "current_price": item["current_price"],
                    "target_price": item["target_price"],
                    "stop_price": item["stop_price"]
                }
            )

            saved_count += 1

        db.commit()

        return {
            "saved": True,
            "version": "MCP 9.7",
            "saved_count": saved_count,
            "overall_signal": result["overall_signal"],
            "message": "신호 로그 저장 완료"
        }

    finally:
        db.close()
