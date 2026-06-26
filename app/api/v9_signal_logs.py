from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v9",
    tags=["MCP 9.8 Signal Logs"]
)


@router.get("/signals/logs")
def get_signal_logs(limit: int = 50):

    db = SessionLocal()

    try:

        rows = db.execute(
            text("""
                SELECT *
                FROM mcp4.signal_log
                ORDER BY id DESC
                LIMIT :limit
            """),
            {"limit": limit}
        ).mappings().all()

        return {
            "found": True,
            "version": "MCP 9.8",
            "count": len(rows),
            "items": [dict(x) for x in rows]
        }

    finally:
        db.close()


@router.get("/signals/logs/latest")
def get_latest_signal_log():

    db = SessionLocal()

    try:

        row = db.execute(
            text("""
                SELECT *
                FROM mcp4.signal_log
                ORDER BY id DESC
                LIMIT 1
            """)
        ).mappings().first()

        if not row:
            return {
                "found": False,
                "version": "MCP 9.8",
                "message": "신호 로그 없음"
            }

        return {
            "found": True,
            "version": "MCP 9.8",
            "item": dict(row)
        }

    finally:
        db.close()


@router.get("/signals/logs/{log_id}")
def get_signal_log(log_id: int):

    db = SessionLocal()

    try:

        row = db.execute(
            text("""
                SELECT *
                FROM mcp4.signal_log
                WHERE id = :id
            """),
            {"id": log_id}
        ).mappings().first()

        if not row:
            return {
                "found": False,
                "version": "MCP 9.8"
            }

        return {
            "found": True,
            "version": "MCP 9.8",
            "item": dict(row)
        }

    finally:
        db.close()
