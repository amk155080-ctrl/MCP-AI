from fastapi import APIRouter
from sqlalchemy import text
from app.core.database import SessionLocal
router=APIRouter(prefix="/api/v2/semiconductor", tags=["semiconductor-v2"])
@router.get("/top20")
def top20(trade_date: str):
    db=SessionLocal()
    try:
        rows=db.execute(text('SELECT trade_date, stock_code, stock_name, total_score, grade FROM mcp4.semiconductor_score_daily WHERE trade_date=:d ORDER BY total_score DESC LIMIT 20'), {"d":trade_date}).fetchall()
        return {"trade_date":trade_date, "items":[dict(r._mapping) for r in rows]}
    finally: db.close()
