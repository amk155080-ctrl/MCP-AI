from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db


router = APIRouter(
    prefix="/api/v19/cases",
    tags=["MCP19 Auction Cases"],
)


@router.post("/create")
def create_auction_case(
    document_id: int = None,
    auction_id: int = None,
    case_no: str = "",
    court_name: str = "",
    property_address: str = "",
    property_type: str = "",
    appraisal_price: int = 0,
    minimum_bid_price: int = 0,
    expected_sale_price: int = 0,
    status: str = "WATCH",
    memo: str = "",
    db: Session = Depends(get_db),
):
    saved = db.execute(
        text("""
            INSERT INTO auction_cases (
                document_id,
                auction_id,
                case_no,
                court_name,
                property_address,
                property_type,
                appraisal_price,
                minimum_bid_price,
                expected_sale_price,
                status,
                memo
            )
            VALUES (
                :document_id,
                :auction_id,
                :case_no,
                :court_name,
                :property_address,
                :property_type,
                :appraisal_price,
                :minimum_bid_price,
                :expected_sale_price,
                :status,
                :memo
            )
            RETURNING id
        """),
        {
            "document_id": document_id,
            "auction_id": auction_id,
            "case_no": case_no,
            "court_name": court_name,
            "property_address": property_address,
            "property_type": property_type,
            "appraisal_price": appraisal_price,
            "minimum_bid_price": minimum_bid_price,
            "expected_sale_price": expected_sale_price,
            "status": status,
            "memo": memo,
        },
    )

    case_id = saved.scalar()
    db.commit()

    return {
        "found": True,
        "version": "MCP 19.2",
        "case_id": case_id,
        "message": "경매 후보 물건 등록 완료",
    }

@router.get("")
def list_auction_cases(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    rows = db.execute(
        text("""
            SELECT *
            FROM auction_cases
            ORDER BY created_at DESC, id DESC
            LIMIT :limit
        """),
        {"limit": limit},
    ).mappings().all()

    return {
        "found": True,
        "version": "MCP 19.3",
        "count": len(rows),
        "items": [dict(row) for row in rows],
        "message": "경매 후보 물건 목록 조회 완료",
    }


@router.get("/{case_id}")
def get_auction_case(
    case_id: int,
    db: Session = Depends(get_db),
):
    row = db.execute(
        text("""
            SELECT *
            FROM auction_cases
            WHERE id = :case_id
        """),
        {"case_id": case_id},
    ).mappings().first()

    if not row:
        return {
            "found": False,
            "version": "MCP 19.3",
            "case_id": case_id,
            "message": "경매 후보 물건을 찾을 수 없습니다.",
        }

    return {
        "found": True,
        "version": "MCP 19.3",
        "case": dict(row),
        "message": "경매 후보 물건 상세 조회 완료",
    }


@router.get("/document/{document_id}")
def get_auction_case_by_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    row = db.execute(
        text("""
            SELECT *
            FROM auction_cases
            WHERE document_id = :document_id
            ORDER BY created_at DESC, id DESC
            LIMIT 1
        """),
        {"document_id": document_id},
    ).mappings().first()

    if not row:
        return {
            "found": False,
            "version": "MCP 19.3",
            "document_id": document_id,
            "message": "document_id에 해당하는 후보 물건이 없습니다.",
        }

    return {
        "found": True,
        "version": "MCP 19.3",
        "case": dict(row),
        "message": "document_id 기반 후보 물건 조회 완료",
    }
@router.put("/{case_id}/status")
def update_case_status(
    case_id: int,
    status: str,
    memo: str = "",
    db: Session = Depends(get_db),
):
    row = db.execute(
        text("""
            SELECT id
            FROM auction_cases
            WHERE id=:case_id
        """),
        {"case_id": case_id},
    ).first()

    if not row:
        return {
            "found": False,
            "version": "MCP 19.4",
            "case_id": case_id,
            "message": "후보 물건을 찾을 수 없습니다.",
        }

    db.execute(
        text("""
            UPDATE auction_cases
            SET
                status=:status,
                memo=:memo,
                updated_at=NOW()
            WHERE id=:case_id
        """),
        {
            "case_id": case_id,
            "status": status,
            "memo": memo,
        },
    )

    db.commit()

    updated = db.execute(
        text("""
            SELECT *
            FROM auction_cases
            WHERE id=:case_id
        """),
        {"case_id": case_id},
    ).mappings().first()

    return {
        "found": True,
        "version": "MCP 19.4",
        "case": dict(updated),
        "message": "후보 물건 상태 변경 완료",
    }
