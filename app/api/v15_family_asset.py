from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.family_asset_service import FamilyAssetService


router = APIRouter(
    prefix="/api/v15",
    tags=["MCP 15 Family Asset"]
)


@router.get("/assets")
def get_family_assets(db: Session = Depends(get_db)):
    return {
        "found": True,
        "version": "MCP 15.0",
        "items": FamilyAssetService.get_all(db),
        "message": "가족 자산 목록 조회 완료",
    }


@router.get("/summary")
def get_family_asset_summary(db: Session = Depends(get_db)):
    return {
        "found": True,
        "version": "MCP 15.0",
        "summary": FamilyAssetService.get_summary(db),
        "message": "가족 자산 요약 조회 완료",
    }


@router.get("/family")
def get_family_asset_total(db: Session = Depends(get_db)):
    return {
        "found": True,
        "version": "MCP 15.0",
        "family": FamilyAssetService.get_family(db),
        "message": "가족 합산 자산 조회 완료",
    }
