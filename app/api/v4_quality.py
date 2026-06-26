from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(prefix="/api/v4/ranking", tags=["quality-buy-v4"])


@router.get("/quality_buy")
def quality_buy(limit: int = 30):
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT
                s.trade_date,
                s.stock_code,
                s.stock_name,
                s.total_score,
                s.grade,
                p.close_price,
                p.trade_value,
                p.market_cap,
                (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
                ) AS smart_money_net
            FROM mcp4.stock_score_daily s
            JOIN mcp4.stock_price_daily p
              ON s.trade_date = p.trade_date
             AND s.stock_code = p.stock_code
            LEFT JOIN mcp4.investor_flow_daily f
              ON s.trade_date = f.trade_date
             AND s.stock_code = f.stock_code
            WHERE s.total_score >= 70
              AND p.market_cap >= 100000000000
              AND p.trade_value >= 10000000000
              AND (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
              ) > 0
            ORDER BY s.total_score DESC, smart_money_net DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()

        return [dict(r) for r in rows]
    finally:
        db.close()

@router.get("/institutional_quality_buy")
def institutional_quality_buy(limit: int = 30):
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT
                s.trade_date,
                s.stock_code,
                s.stock_name,
                s.total_score,
                s.grade,
                p.close_price,
                p.trade_value,
                p.market_cap,
                COALESCE(f.foreign_net, 0) AS foreign_net,
                COALESCE(f.institution_net, 0) AS institution_net,
                COALESCE(f.pension_net, 0) AS pension_net,
                (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
                ) AS smart_money_net,
                CASE
                    WHEN s.total_score >= 80 THEN 'STRONG_BUY'
                    WHEN s.total_score >= 70 THEN 'BUY'
                    WHEN s.total_score >= 60 THEN 'WATCH'
                    ELSE 'AVOID'
                END AS signal
            FROM mcp4.stock_score_daily s
            JOIN mcp4.stock_price_daily p
              ON s.trade_date = p.trade_date
             AND s.stock_code = p.stock_code
            LEFT JOIN mcp4.investor_flow_daily f
              ON s.trade_date = f.trade_date
             AND s.stock_code = f.stock_code
            WHERE s.total_score >= 70
              AND p.market_cap >= 500000000000
              AND p.trade_value >= 30000000000
              AND (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
              ) >= 5000000000
            ORDER BY
                smart_money_net DESC,
                s.total_score DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()

        return [dict(r) for r in rows]
    finally:
        db.close()


@router.get("/institutional_quality_sell")
def institutional_quality_sell(limit: int = 30):
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT
                s.trade_date,
                s.stock_code,
                s.stock_name,
                s.total_score,
                s.grade,
                p.close_price,
                p.trade_value,
                p.market_cap,
                COALESCE(f.foreign_net, 0) AS foreign_net,
                COALESCE(f.institution_net, 0) AS institution_net,
                COALESCE(f.pension_net, 0) AS pension_net,
                (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
                ) AS smart_money_net,
                CASE
                    WHEN s.total_score <= 45 THEN 'STRONG_SELL'
                    WHEN s.total_score <= 55 THEN 'SELL'
                    WHEN s.total_score <= 60 THEN 'REDUCE'
                    ELSE 'HOLD'
                END AS signal
            FROM mcp4.stock_score_daily s
            JOIN mcp4.stock_price_daily p
              ON s.trade_date = p.trade_date
             AND s.stock_code = p.stock_code
            LEFT JOIN mcp4.investor_flow_daily f
              ON s.trade_date = f.trade_date
             AND s.stock_code = f.stock_code
            WHERE s.total_score <= 55
              AND p.market_cap >= 100000000000
              AND p.trade_value >= 10000000000
              AND COALESCE(f.foreign_net,0) < 0
              AND COALESCE(f.institution_net,0) < 0
              AND (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
              ) < 0
            ORDER BY
                smart_money_net ASC,
                s.total_score ASC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()

        return [dict(r) for r in rows]
    finally:
        db.close()
