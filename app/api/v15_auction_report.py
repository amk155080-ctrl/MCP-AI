from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auction_report_service import AuctionReportService


router = APIRouter(
    prefix="/api/v15/auction",
    tags=["MCP 15 Auction Report"]
)


@router.get("/dashboard")
def get_auction_dashboard(db: Session = Depends(get_db)):
    return {
        "found": True,
        "version": "MCP 15.6",
        "dashboard": AuctionReportService.dashboard(db),
        "message": "경매 종합 대시보드 생성 완료",
    }


@router.get("/kakao")
def get_auction_kakao_report(db: Session = Depends(get_db)):
    return {
        "found": True,
        "version": "MCP 15.6",
        "kakao": AuctionReportService.kakao_report(db),
        "message": "경매 카카오 리포트 생성 완료",
    }
