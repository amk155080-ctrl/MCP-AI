from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v10",
    tags=["MCP 10.4 Order Status"]
)


@router.get("/orders/status/{status}")
def get_orders_by_status(status: str):

    db = SessionLocal()

    try:

        rows = db.execute(
            text("""
                SELECT *
                FROM mcp4.order_queue
                WHERE UPPER(status) = UPPER(:status)
                ORDER BY id DESC
            """),
            {"status": status}
        ).mappings().all()

        return {
            "found": True,
            "version": "MCP 10.4",
            "status": status.upper(),
            "count": len(rows),
            "items": [dict(row) for row in rows],
            "message": "주문 상태 조회 완료"
        }

    finally:
        db.close()
