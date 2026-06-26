from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auction_portfolio_service import AuctionPortfolioService


router = APIRouter(
    prefix="/api/v15/auction",
    tags=["MCP 15 Auction Portfolio"]
)


@router.get("/portfolio")
def get_auction_portfolio(db: Session = Depends(get_db)):
    return {
        "found": True,
        "version": "MCP 15.4",
        "portfolio": AuctionPortfolioService.portfolio(db),
        "message": "경매 포트폴리오 분석 완료",
    }


@router.get("/optimize-bid")
def get_auction_optimized_bid(db: Session = Depends(get_db)):
    return {
        "found": True,
        "version": "MCP 15.4",
        "items": AuctionPortfolioService.optimize_bid(db),
        "message": "AI 낙찰가 최적화 완료",
    }
