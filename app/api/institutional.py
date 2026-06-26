from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(prefix="/institutional", tags=["Institutional"])


@router.get("/top")
def get_institutional_top(limit: int = 10):
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT *
            FROM mcp4.institutional_score_daily
            ORDER BY trade_date DESC, total_score DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()

        return [dict(r) for r in rows]
    finally:
        db.close()


@router.get("/portfolio")
def get_portfolio():
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT *
            FROM mcp4.portfolio_position_daily
            ORDER BY trade_date DESC, weight DESC
        """)).mappings().all()

        return [dict(r) for r in rows]
    finally:
        db.close()


@router.get("/risk")
def get_risk():
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT *
            FROM mcp4.portfolio_risk_daily
            ORDER BY trade_date DESC
            LIMIT 20
        """)).mappings().all()

        return [dict(r) for r in rows]
    finally:
        db.close()


@router.get("/backtest")
def get_backtest():
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT *
            FROM mcp4.backtest_report
            ORDER BY trade_date DESC
            LIMIT 20
        """)).mappings().all()

        return [dict(r) for r in rows]
    finally:
        db.close()
