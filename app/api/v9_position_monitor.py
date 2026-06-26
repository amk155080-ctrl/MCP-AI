from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal
from app.api.v9_quote import get_quote

router = APIRouter(
    prefix="/api/v9",
    tags=["MCP 9.4 Position Monitor"]
)


@router.get("/position-monitor")
def position_monitor():

    db = SessionLocal()

    try:

        rows = db.execute(
            text("""
                SELECT *
                FROM mcp4.portfolio_position
                ORDER BY id
            """)
        ).mappings().all()

        positions = []

        total_buy_amount = 0
        total_current_value = 0

        for row in rows:

            quote = get_quote(row["stock_code"])

            if not quote.get("found"):
                continue

            current_price = quote["current_price"]

            quantity = int(row["quantity"])
            buy_price = float(row["buy_price"])

            buy_amount = quantity * buy_price
            current_value = quantity * current_price

            profit_loss = current_value - buy_amount

            profit_rate = round(
                (profit_loss / buy_amount) * 100,
                2
            )

            target_price = float(row["target_price"] or 0)
            stop_price = float(row["stop_price"] or 0)

            target_reached = (
                current_price >= target_price
                if target_price > 0
                else False
            )

            stop_broken = (
                current_price <= stop_price
                if stop_price > 0
                else False
            )

            if stop_broken:
                action = "SELL"
                status = "STOP_LOSS"

            elif target_reached:
                action = "TAKE_PROFIT"
                status = "TARGET_HIT"

            else:
                action = "HOLD"
                status = "NORMAL"

            total_buy_amount += buy_amount
            total_current_value += current_value

            positions.append({
                "stock_code": row["stock_code"],
                "stock_name": row["stock_name"],
                "current_price": current_price,
                "buy_price": buy_price,
                "quantity": quantity,
                "profit_loss": profit_loss,
                "profit_rate": profit_rate,
                "target_price": target_price,
                "stop_price": stop_price,
                "target_reached": target_reached,
                "stop_broken": stop_broken,
                "status": status,
                "action": action
            })

        total_profit_loss = (
            total_current_value - total_buy_amount
        )

        total_profit_rate = round(
            (total_profit_loss / total_buy_amount) * 100,
            2
        ) if total_buy_amount > 0 else 0

        return {
            "found": True,
            "version": "MCP 9.4",
            "position_count": len(positions),
            "total_buy_amount": total_buy_amount,
            "total_current_value": total_current_value,
            "total_profit_loss": total_profit_loss,
            "total_profit_rate": total_profit_rate,
            "positions": positions,
            "message": "실시간 포지션 모니터 완료"
        }

    finally:
        db.close()
