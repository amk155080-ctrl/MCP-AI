from fastapi import APIRouter
from sqlalchemy import text
from app.core.database import SessionLocal

from app.api.v9_quote import get_quote

router = APIRouter(
    prefix="/api/v9/portfolio",
    tags=["MCP 9.1 Portfolio Evaluate"]
)


def to_float(value):
    try:
        return float(value)
    except:
        return 0.0


@router.get("/evaluate")
def evaluate_portfolio():
    db = SessionLocal()

    try:
        rows = db.execute(
            text("""
                SELECT
                    id,
                    stock_code,
                    stock_name,
                    quantity,
                    buy_price,
                    created_at
                FROM mcp4.portfolio_position
                ORDER BY id ASC
            """)
        ).mappings().all()

        if not rows:
            return {
                "found": False,
                "version": "MCP 9.1",
                "message": "보유 포지션이 없습니다."
            }

        positions = []

        total_buy_amount = 0
        total_current_value = 0

        for row in rows:
            stock_code = row["stock_code"]
            quantity = int(row["quantity"])
            buy_price = to_float(row["buy_price"])

            quote = get_quote(stock_code)

            current_price = quote.get("current_price") if quote.get("found") else None

            buy_amount = int(quantity * buy_price)

            if current_price:
                current_value = int(quantity * current_price)
                profit_loss = current_value - buy_amount
                profit_rate = round((profit_loss / buy_amount) * 100, 2) if buy_amount > 0 else 0
            else:
                current_value = 0
                profit_loss = 0
                profit_rate = 0

            total_buy_amount += buy_amount
            total_current_value += current_value

            positions.append({
                "id": row["id"],
                "stock_code": stock_code,
                "stock_name": row["stock_name"],
                "quantity": quantity,
                "buy_price": buy_price,
                "buy_amount": buy_amount,
                "current_price": current_price,
                "current_value": current_value,
                "profit_loss": profit_loss,
                "profit_rate": profit_rate,
                "quote_base_date": quote.get("base_date"),
                "quote_source": quote.get("source"),
                "quote_message": quote.get("message")
            })

        total_profit_loss = total_current_value - total_buy_amount
        total_profit_rate = round((total_profit_loss / total_buy_amount) * 100, 2) if total_buy_amount > 0 else 0

        return {
            "found": True,
            "version": "MCP 9.1",
            "position_count": len(positions),
            "total_buy_amount": total_buy_amount,
            "total_current_value": total_current_value,
            "total_profit_loss": total_profit_loss,
            "total_profit_rate": total_profit_rate,
            "positions": positions,
            "message": "포트폴리오 실시간 평가 완료"
        }

    finally:
        db.close()

