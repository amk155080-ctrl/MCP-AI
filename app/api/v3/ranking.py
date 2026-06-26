from fastapi import APIRouter
from sqlalchemy import text
from app.core.database import SessionLocal
router=APIRouter(prefix="/api/v3/ranking", tags=["ranking-v3"])
@router.get("/institutional_top100")
def institutional_top100(trade_date: str):
    db=SessionLocal()
    try:
        rows=db.execute(text('SELECT trade_date, stock_code, stock_name, total_score, grade, signal FROM mcp4.institutional_score_daily WHERE trade_date=:d ORDER BY total_score DESC LIMIT 100'), {"d":trade_date}).fetchall()
        return {"trade_date":trade_date, "items":[dict(r._mapping) for r in rows]}
    finally: db.close()
