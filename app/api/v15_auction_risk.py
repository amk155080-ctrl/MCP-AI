from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auction_risk_service import AuctionRiskService


router = APIRouter(
    prefix="/api/v15/auction",
    tags=["MCP 15 Auction Risk"]
)


@router.get("/risk")
def get_auction_risk(db: Session = Depends(get_db)):
    return {
        "found": True,
        "version": "MCP 15.5",
        "items": AuctionRiskService.analyze(db),
        "message": "경매 리스크 분석 완료",
    }


@router.get("/risk-summary")
def get_auction_risk_summary(db: Session = Depends(get_db)):
    return {
        "found": True,
        "version": "MCP 15.5",
        "summary": AuctionRiskService.summary(db),
        "message": "경매 리스크 요약 완료",
    }
