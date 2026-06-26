from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(prefix="/api/v4/ranking", tags=["ranking-v4"])


EXCLUDE_NAME_SQL = """
    s.stock_name NOT LIKE '%우'
    AND s.stock_name NOT LIKE '%우B'
    AND s.stock_name NOT LIKE '%스팩%'
    AND s.stock_name NOT LIKE '%SPAC%'
    AND s.stock_name NOT LIKE '%리츠%'
    AND s.stock_name NOT LIKE '%TIGER%'
    AND s.stock_name NOT LIKE '%KODEX%'
    AND s.stock_name NOT LIKE '%ARIRANG%'
    AND s.stock_name NOT LIKE '%KBSTAR%'
    AND s.stock_name NOT LIKE '%HANARO%'
    AND s.stock_name NOT LIKE '%ACE%'
    AND s.stock_name NOT LIKE '%SOL%'
"""


@router.get("/top100")
def top100(limit: int = 100):
    db = SessionLocal()
    try:
        rows = db.execute(text(f"""
            SELECT
                s.trade_date,
                s.stock_code,
                s.stock_name,
                s.supply_score,
                s.momentum_score,
                s.macro_score,
                s.semiconductor_score,
                s.risk_score,
                s.total_score,
                s.grade,
                p.close_price,
                p.trade_value,
                p.market_cap,
                s.created_at
            FROM mcp4.stock_score_daily s
            JOIN mcp4.stock_price_daily p
              ON s.trade_date = p.trade_date
             AND s.stock_code = p.stock_code
            WHERE {EXCLUDE_NAME_SQL}
              AND COALESCE(p.trade_value, 0) >= 5000000000
              AND COALESCE(p.close_price, 0) >= 1000
            ORDER BY s.trade_date DESC, s.total_score DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()

        return [dict(r) for r in rows]
    finally:
        db.close()


@router.get("/buy")
def buy_candidates(limit: int = 30):
    db = SessionLocal()
    try:
        rows = db.execute(text(f"""
            SELECT
                s.trade_date,
                s.stock_code,
                s.stock_name,
                s.total_score,
                s.grade,
                p.close_price,
                p.trade_value,
                p.market_cap
            FROM mcp4.stock_score_daily s
            JOIN mcp4.stock_price_daily p
              ON s.trade_date = p.trade_date
             AND s.stock_code = p.stock_code
            WHERE s.grade IN ('A', 'B')
              AND {EXCLUDE_NAME_SQL}
              AND COALESCE(p.trade_value, 0) >= 5000000000
              AND COALESCE(p.close_price, 0) >= 1000
            ORDER BY s.trade_date DESC, s.total_score DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()

        return [dict(r) for r in rows]
    finally:
        db.close()


@router.get("/filtered")
def filtered_rank(
    limit: int = 100,
    min_trade_value: int = 5000000000,
    min_price: int = 1000,
):
    db = SessionLocal()
    try:
        rows = db.execute(text(f"""
            SELECT
                s.trade_date,
                s.stock_code,
                s.stock_name,
                s.total_score,
                s.grade,
                p.close_price,
                p.trade_value,
                p.market_cap
            FROM mcp4.stock_score_daily s
            JOIN mcp4.stock_price_daily p
              ON s.trade_date = p.trade_date
             AND s.stock_code = p.stock_code
            WHERE {EXCLUDE_NAME_SQL}
              AND COALESCE(p.trade_value, 0) >= :min_trade_value
              AND COALESCE(p.close_price, 0) >= :min_price
            ORDER BY s.trade_date DESC, s.total_score DESC
            LIMIT :limit
        """), {
            "limit": limit,
            "min_trade_value": min_trade_value,
            "min_price": min_price,
        }).mappings().all()

        return [dict(r) for r in rows]
    finally:
        db.close()


@router.get("/strong_buy")
def strong_buy(limit: int = 30):
    db = SessionLocal()
    try:
        rows = db.execute(text(f"""
            SELECT
                s.trade_date,
                s.stock_code,
                s.stock_name,
                s.total_score,
                'STRONG_BUY' AS signal,
                p.close_price,
                p.trade_value,
                p.market_cap
            FROM mcp4.stock_score_daily s
            JOIN mcp4.stock_price_daily p
              ON s.trade_date = p.trade_date
             AND s.stock_code = p.stock_code
            WHERE s.total_score >= 80
              AND {EXCLUDE_NAME_SQL}
              AND COALESCE(p.trade_value, 0) >= 5000000000
              AND COALESCE(p.close_price, 0) >= 1000
            ORDER BY s.trade_date DESC, s.total_score DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()

        return [dict(r) for r in rows]
    finally:
        db.close()


@router.get("/watch")
def watch(limit: int = 50):
    db = SessionLocal()
    try:
        rows = db.execute(text(f"""
            SELECT
                s.trade_date,
                s.stock_code,
                s.stock_name,
                s.total_score,
                CASE
                    WHEN s.total_score >= 80 THEN 'STRONG_BUY'
                    WHEN s.total_score >= 70 THEN 'BUY'
                    WHEN s.total_score >= 60 THEN 'WATCH'
                    ELSE 'AVOID'
                END AS signal,
                p.close_price,
                p.trade_value,
                p.market_cap
            FROM mcp4.stock_score_daily s
            JOIN mcp4.stock_price_daily p
              ON s.trade_date = p.trade_date
             AND s.stock_code = p.stock_code
            WHERE s.total_score >= 60
              AND s.total_score < 70
              AND {EXCLUDE_NAME_SQL}
              AND COALESCE(p.trade_value, 0) >= 5000000000
              AND COALESCE(p.close_price, 0) >= 1000
            ORDER BY s.trade_date DESC, s.total_score DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()

        return [dict(r) for r in rows]
    finally:
        db.close()


@router.get("/signals")
def signals(limit: int = 100):
    db = SessionLocal()
    try:
        rows = db.execute(text(f"""
            SELECT
                s.trade_date,
                s.stock_code,
                s.stock_name,
                s.total_score,
                s.grade,
                CASE
                    WHEN s.total_score >= 80 THEN 'STRONG_BUY'
                    WHEN s.total_score >= 70 THEN 'BUY'
                    WHEN s.total_score >= 60 THEN 'WATCH'
                    ELSE 'AVOID'
                END AS signal,
                p.close_price,
                p.trade_value,
                p.market_cap
            FROM mcp4.stock_score_daily s
            JOIN mcp4.stock_price_daily p
              ON s.trade_date = p.trade_date
             AND s.stock_code = p.stock_code
            WHERE {EXCLUDE_NAME_SQL}
              AND COALESCE(p.trade_value, 0) >= 5000000000
              AND COALESCE(p.close_price, 0) >= 1000
            ORDER BY s.trade_date DESC, s.total_score DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()

        return [dict(r) for r in rows]
    finally:
        db.close()
