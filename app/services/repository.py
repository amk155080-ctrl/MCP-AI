from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import text
from app.core.database import SessionLocal
from app.models.tables import StockPriceDaily, StockScoreDaily

def upsert_stock_prices(records):
    if not records:
        return 0
    db = SessionLocal()
    try:
        stmt = insert(StockPriceDaily).values(records)
        stmt = stmt.on_conflict_do_update(
            index_elements=["trade_date", "stock_code"],
            set_={k: getattr(stmt.excluded, k) for k in records[0].keys() if k not in ("trade_date", "stock_code")}
        )
        db.execute(stmt)
        db.commit()
        return len(records)
    finally:
        db.close()

def save_scores(records):
    if not records:
        return 0
    db = SessionLocal()
    try:
        stmt = insert(StockScoreDaily).values(records)
        stmt = stmt.on_conflict_do_update(
            index_elements=["trade_date", "stock_code"],
            set_={k: getattr(stmt.excluded, k) for k in records[0].keys() if k not in ("trade_date", "stock_code")}
        )
        db.execute(stmt)
        db.commit()
        return len(records)
    finally:
        db.close()

def query_top20(trade_date):
    db = SessionLocal()
    try:
        sql = text('''
            SELECT trade_date, stock_code, stock_name, total_score, grade
            FROM mcp4.stock_score_daily
            WHERE trade_date = :trade_date
            ORDER BY total_score DESC
            LIMIT 20
        ''')
        return [dict(r._mapping) for r in db.execute(sql, {"trade_date": trade_date}).fetchall()]
    finally:
        db.close()
