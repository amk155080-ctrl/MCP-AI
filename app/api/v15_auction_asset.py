from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.auction_asset_service import (
    AuctionAssetService
)

router = APIRouter(
    prefix="/api/v15/auction",
    tags=["MCP 15 Auction"]
)


@router.get("/list")
def get_auction_assets(
    db: Session = Depends(get_db)
):
    return {
        "found": True,
        "version": "MCP 15.2",
        "items": AuctionAssetService.get_all(db)
    }


@router.get("/summary")
def get_auction_summary(
    db: Session = Depends(get_db)
):
    return {
        "found": True,
        "version": "MCP 15.2",
        "summary": AuctionAssetService.get_summary(db)
    }
