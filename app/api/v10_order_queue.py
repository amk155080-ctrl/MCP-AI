from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v10",
    tags=["MCP 10.1 Order Queue"]
)


@router.get("/orders/queue")
def get_order_queue(limit: int = 50):
    db = SessionLocal()

    try:
        rows = db.execute(
            text("""
                SELECT *
                FROM mcp4.order_queue
                ORDER BY id DESC
                LIMIT :limit
            """),
            {"limit": limit}
        ).mappings().all()

        return {
            "found": True,
            "version": "MCP 10.1",
            "count": len(rows),
            "items": [dict(row) for row in rows],
            "message": "주문 큐 조회 완료"
        }

    finally:
        db.close()


@router.get("/orders/queue/latest")
def get_latest_order_queue():
    db = SessionLocal()

    try:
        row = db.execute(
            text("""
                SELECT *
                FROM mcp4.order_queue
                ORDER BY id DESC
                LIMIT 1
            """)
        ).mappings().first()

        if not row:
            return {
                "found": False,
                "version": "MCP 10.1",
                "message": "주문 큐가 비어 있습니다."
            }

        return {
            "found": True,
            "version": "MCP 10.1",
            "item": dict(row),
            "message": "최신 주문 큐 조회 완료"
        }

    finally:
        db.close()


@router.get("/orders/queue/{order_id}")
def get_order_queue_by_id(order_id: int):
    db = SessionLocal()

    try:
        row = db.execute(
            text("""
                SELECT *
                FROM mcp4.order_queue
                WHERE id = :order_id
            """),
            {"order_id": order_id}
        ).mappings().first()

        if not row:
            return {
                "found": False,
                "version": "MCP 10.1",
                "message": "해당 주문 큐를 찾을 수 없습니다."
            }

        return {
            "found": True,
            "version": "MCP 10.1",
            "item": dict(row),
            "message": "주문 큐 단건 조회 완료"
        }

    finally:
        db.close()
