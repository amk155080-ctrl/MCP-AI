from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v10",
    tags=["MCP 10.2 Order Approve"]
)


@router.post("/orders/approve/{order_id}")
def approve_order(order_id: int):

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
                "approved": False,
                "version": "MCP 10.2",
                "message": "주문을 찾을 수 없습니다."
            }

        db.execute(
            text("""
                UPDATE mcp4.order_queue
                SET status = 'APPROVED'
                WHERE id = :id
            """),
            {"id": order_id}
        )

        db.commit()

        return {
            "approved": True,
            "version": "MCP 10.2",
            "order_id": order_id,
            "stock_code": row["stock_code"],
            "stock_name": row["stock_name"],
            "action": row["action"],
            "message": "주문 승인 완료"
        }

    finally:
        db.close()
