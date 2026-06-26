from fastapi import APIRouter
from sqlalchemy import text
from app.core.database import SessionLocal
router=APIRouter(prefix="/api/v2/market", tags=["market-v2"])
@router.get("/regime")
def market_regime():
    db=SessionLocal()
    try:
        row=db.execute(text('SELECT * FROM mcp4.market_regime_daily ORDER BY trade_date DESC LIMIT 1')).fetchone()
        return dict(row._mapping) if row else {"message":"no market regime data"}
    finally: db.close()
