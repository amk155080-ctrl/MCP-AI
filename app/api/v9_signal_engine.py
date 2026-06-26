from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal
from app.api.v9_quote import get_quote

router = APIRouter(
    prefix="/api/v9",
    tags=["MCP 9.6 Signal Engine"]
)


@router.get("/signals")
def signal_engine():

    db = SessionLocal()

    try:

        rows = db.execute(
            text("""
                SELECT *
                FROM mcp4.portfolio_position
                ORDER BY id
            """)
        ).mappings().all()

        signals = []

        sell_count = 0
        take_profit_count = 0
        hold_count = 0

        for row in rows:

            quote = get_quote(row["stock_code"])

            if not quote.get("found"):
                continue

            current_price = quote["current_price"]

            target_price = float(row["target_price"] or 0)
            stop_price = float(row["stop_price"] or 0)

            signal = "HOLD"
            reason = "정상 보유"

            if stop_price > 0 and current_price <= stop_price:

                signal = "SELL"
                reason = "손절가 이탈"

                sell_count += 1

            elif target_price > 0 and current_price >= target_price:

                signal = "TAKE_PROFIT"
                reason = "목표가 도달"

                take_profit_count += 1

            else:

                hold_count += 1

            signals.append({
                "stock_code": row["stock_code"],
                "stock_name": row["stock_name"],
                "current_price": current_price,
                "target_price": target_price,
                "stop_price": stop_price,
                "signal": signal,
                "reason": reason
            })

        if sell_count > 0:
            overall_signal = "RISK"

        elif take_profit_count > 0:
            overall_signal = "PROFIT"

        else:
            overall_signal = "NORMAL"

        return {
            "found": True,
            "version": "MCP 9.6",
            "overall_signal": overall_signal,
            "sell_count": sell_count,
            "take_profit_count": take_profit_count,
            "hold_count": hold_count,
            "signals": signals,
            "message": "자동 매매 신호 생성 완료"
        }

    finally:
        db.close()
