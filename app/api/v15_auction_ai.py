from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.auction_ai_service import (
    AuctionAIService
)

router = APIRouter(
    prefix="/api/v15/auction",
    tags=["MCP 15 Auction AI"]
)


@router.get("/profit")
def get_profit_analysis(
    db: Session = Depends(get_db)
):
    return {
        "found": True,
        "version": "MCP 15.3",
        "items": AuctionAIService.get_profit_analysis(db)
    }


@router.get("/recommend")
def get_recommendation(
    db: Session = Depends(get_db)
):
    return {
        "found": True,
        "version": "MCP 15.3",
        "items": AuctionAIService.get_ai_recommendation(db)
    }
