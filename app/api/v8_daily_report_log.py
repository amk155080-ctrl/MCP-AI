from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, datetime
from decimal import Decimal

from app.core.database import get_db

router = APIRouter(
    prefix="/api/v8/report/daily/logs",
    tags=["MCP 8.10 Daily Report Logs"],
)


def to_json_safe(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def row_to_dict(row):
    return {key: to_json_safe(value) for key, value in dict(row).items()}


@router.get("")
def list_daily_report_logs(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        text("""
            SELECT *
            FROM mcp4.daily_report_log
            ORDER BY created_at DESC
            LIMIT :limit
        """),
        {"limit": limit},
    ).mappings().all()

    return {
        "found": len(rows) > 0,
        "count": len(rows),
        "items": [row_to_dict(row) for row in rows],
    }


@router.get("/latest")
def get_latest_daily_report_log(db: Session = Depends(get_db)):
    row = db.execute(
        text("""
            SELECT *
            FROM mcp4.daily_report_log
            ORDER BY created_at DESC
            LIMIT 1
        """)
    ).mappings().first()

    if not row:
        return {
            "found": False,
            "message": "저장된 일일 투자 리포트가 없습니다.",
        }

    return {
        "found": True,
        "item": row_to_dict(row),
    }


@router.get("/{log_id}")
def get_daily_report_log(log_id: int, db: Session = Depends(get_db)):
    row = db.execute(
        text("""
            SELECT *
            FROM mcp4.daily_report_log
            WHERE id = :log_id
        """),
        {"log_id": log_id},
    ).mappings().first()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="해당 일일 투자 리포트를 찾을 수 없습니다.",
        )

    return {
        "found": True,
        "item": row_to_dict(row),
    }
