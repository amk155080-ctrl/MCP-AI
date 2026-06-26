from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auction_rights_service import AuctionRightsService
from app.schemas.auction_rights_schema import AuctionRightsCreate
from app.schemas.auction_rights_schema import AuctionRightsUpdate


router = APIRouter(
    prefix="/api/v15/auction",
    tags=["MCP 15 Auction Rights"]
)


@router.get("/rights")
def get_all_auction_rights(db: Session = Depends(get_db)):
    return {
        "found": True,
        "version": "MCP 15.13",
        "items": AuctionRightsService.get_all(db),
        "message": "전체 권리분석 데이터 조회 완료",
    }


@router.get("/rights/{auction_id}")
def get_auction_rights(
    auction_id: int,
    db: Session = Depends(get_db)
):
    rights = AuctionRightsService.get_by_auction_id(db, auction_id)

    if rights is None:
        return {
            "found": False,
            "version": "MCP 15.13",
            "auction_id": auction_id,
            "message": "권리분석 데이터가 없습니다.",
        }

    return {
        "found": True,
        "version": "MCP 15.13",
        "rights": rights,
        "message": "권리분석 데이터 조회 완료",
    }

from fastapi import Body


@router.post("/rights")
def create_rights(

    data: AuctionRightsCreate,

    db: Session = Depends(get_db)

):

    row = AuctionRightsService.create(db, data)

    return {

        "found": True,

        "version": "MCP 15.14",

        "id": row.id,

        "message": "권리분석 등록 완료"

    }


@router.put("/rights/{auction_id}")
def update_rights(

    auction_id: int,

    data: AuctionRightsUpdate,

    db: Session = Depends(get_db)

):

    row = AuctionRightsService.update(

        db,

        auction_id,

        data

    )

    if not row:

        return {

            "found": False,

            "message": "데이터 없음"

        }

    return {

        "found": True,

        "version": "MCP 15.14",

        "message": "권리분석 수정 완료"

    }


@router.delete("/rights/{auction_id}")
def delete_rights(

    auction_id: int,

    db: Session = Depends(get_db)

):

    ok = AuctionRightsService.delete(

        db,

        auction_id

    )

    return {

        "found": ok,

        "version": "MCP 15.14",

        "message": "삭제 완료" if ok else "데이터 없음"

    }
