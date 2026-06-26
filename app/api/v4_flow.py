from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(prefix="/api/v4/flow", tags=["flow-v4"])


@router.get("/foreign/top100")
def foreign_top100(limit: int = 100):
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT
                f.trade_date,
                f.stock_code,
                m.stock_name,
                f.foreign_net,
                f.institution_net,
                f.pension_net,
                f.program_net
            FROM mcp4.investor_flow_daily f
            LEFT JOIN mcp4.stock_master m
              ON f.stock_code = m.stock_code
            WHERE f.trade_date = (
                SELECT MAX(trade_date)
                FROM mcp4.investor_flow_daily
            )
            ORDER BY f.foreign_net DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()

        return [dict(r) for r in rows]
    finally:
        db.close()


@router.get("/institution/top100")
def institution_top100(limit: int = 100):
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT
                f.trade_date,
                f.stock_code,
                m.stock_name,
                f.foreign_net,
                f.institution_net,
                f.pension_net,
                f.program_net
            FROM mcp4.investor_flow_daily f
            LEFT JOIN mcp4.stock_master m
              ON f.stock_code = m.stock_code
            WHERE f.trade_date = (
                SELECT MAX(trade_date)
                FROM mcp4.investor_flow_daily
            )
            ORDER BY f.institution_net DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()

        return [dict(r) for r in rows]
    finally:
        db.close()


@router.get("/smart_money/top100")
def smart_money_top100(limit: int = 100):
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT
                f.trade_date,
                f.stock_code,
                m.stock_name,
                f.foreign_net,
                f.institution_net,
                f.pension_net,
                f.program_net,
                COALESCE(f.foreign_net, 0)
                + COALESCE(f.institution_net, 0)
                + COALESCE(f.pension_net, 0) AS smart_money_net
            FROM mcp4.investor_flow_daily f
            LEFT JOIN mcp4.stock_master m
              ON f.stock_code = m.stock_code
            WHERE f.trade_date = (
                SELECT MAX(trade_date)
                FROM mcp4.investor_flow_daily
            )
            ORDER BY smart_money_net DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()

        return [dict(r) for r in rows]
    finally:
        db.close()
