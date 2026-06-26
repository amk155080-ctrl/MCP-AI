from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v10",
    tags=["MCP 10.3 Order Cancel"]
)


@router.post("/orders/cancel/{order_id}")
def cancel_order(order_id: int):
    db = SessionLocal()

    try:
        row = db.execute(
            text("""
                SELECT *
                FROM mcp4.order_queue
                WHERE id = :id
            """),
            {"id": order_id}
        ).mappings().first()

        if not row:
            return {
                "cancelled": False,
                "version": "MCP 10.3",
                "message": "주문을 찾을 수 없습니다."
            }

        if row["status"] == "CANCELLED":
            return {
                "cancelled": False,
                "version": "MCP 10.3",
                "order_id": order_id,
                "message": "이미 취소된 주문입니다."
            }

        db.execute(
            text("""
                UPDATE mcp4.order_queue
                SET status = 'CANCELLED'
                WHERE id = :id
            """),
            {"id": order_id}
        )

        db.commit()

        return {
            "cancelled": True,
            "version": "MCP 10.3",
            "order_id": order_id,
            "stock_code": row["stock_code"],
            "stock_name": row["stock_name"],
            "action": row["action"],
            "previous_status": row["status"],
            "new_status": "CANCELLED",
            "message": "주문 취소 완료"
        }

    finally:
        db.close()
