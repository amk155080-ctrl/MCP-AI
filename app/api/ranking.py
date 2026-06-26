from fastapi import APIRouter
from app.services.repository import query_top20

router = APIRouter(prefix="/api/v1/ranking", tags=["ranking"])

@router.get("/top20")
def top20(trade_date: str):
    return {
        "trade_date": trade_date,
        "items": query_top20(trade_date),
    }
