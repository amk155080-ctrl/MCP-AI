from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import json

from app.core.database import get_db
from app.models.auction_document import AuctionDocument
from app.services.rights_engine_v2.engine_v2 import analyze

router = APIRouter(
    prefix="/api/v16/rights-v2",
    tags=["MCP16 Rights Engine V2"],
)


@router.get("/{document_id}")
def analyze_rights_v2(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(AuctionDocument)
        .filter(AuctionDocument.id == document_id)
        .first()
    )

    if not document:
        return {
            "found": False,
            "version": "MCP 16.6",
            "message": "문서를 찾을 수 없습니다.",
        }

    text_data = document.summary or ""

    if not text_data.strip():
        return {
            "found": False,
            "version": "MCP 16.6",
            "document_id": document_id,
            "message": "OCR summary/text가 비어 있습니다. 먼저 /api/v16/document/ocr/{document_id}를 실행하세요.",
        }

    result = analyze(text_data)

    insert_sql = text("""
        INSERT INTO rights_v2_results (
            document_id,
            auction_id,
            version,
            base_right,
            tenant_priority,
            occupancy,
            lease_deposit,
            takeover_amount,
            takeover_required,
            legal_risks,
            legal_risk_count,
            rights_score,
            risk_level,
            recommendation,
            summary
        )
        VALUES (
            :document_id,
            :auction_id,
            :version,
            :base_right,
            :tenant_priority,
            :occupancy,
            :lease_deposit,
            :takeover_amount,
            :takeover_required,
            :legal_risks,
            :legal_risk_count,
            :rights_score,
            :risk_level,
            :recommendation,
            :summary
        )
        RETURNING id
    """)

    saved = db.execute(
        insert_sql,
        {
            "document_id": document.id,
            "auction_id": document.auction_id,
            "version": result.get("version"),
            "base_right": result.get("base_right"),
            "tenant_priority": result.get("tenant_priority"),
            "occupancy": result.get("occupancy"),
            "lease_deposit": result.get("lease_deposit", 0),
            "takeover_amount": result.get("takeover_amount", 0),
            "takeover_required": result.get("takeover_required", False),
            "legal_risks": json.dumps(result.get("legal_risks", []), ensure_ascii=False),
            "legal_risk_count": result.get("legal_risk_count", 0),
            "rights_score": result.get("rights_score"),
            "risk_level": result.get("risk_level"),
            "recommendation": result.get("recommendation"),
            "summary": result.get("summary"),
        },
    )

    saved_id = saved.scalar()
    db.commit()

    return {
        "found": True,
        "version": "MCP 16.6",
        "document_id": document.id,
        "auction_id": document.auction_id,
        "document_type": document.document_type,
        "file_name": document.file_name,
        "saved": True,
        "rights_v2_result_id": saved_id,
        "rights_analysis": result,
        "message": "Rights Engine V2 분석 및 저장 완료",
    }


@router.get("/result/latest/{document_id}")
def get_latest_rights_v2_result(
    document_id: int,
    db: Session = Depends(get_db),
):
    row = db.execute(
        text("""
            SELECT *
            FROM rights_v2_results
            WHERE document_id = :document_id
            ORDER BY created_at DESC, id DESC
            LIMIT 1
        """),
        {"document_id": document_id},
    ).mappings().first()

    if not row:
        return {
            "found": False,
            "version": "MCP 16.6",
            "document_id": document_id,
            "message": "저장된 Rights V2 분석 결과가 없습니다.",
        }

    return {
        "found": True,
        "version": "MCP 16.6",
        "result": dict(row),
        "message": "최신 Rights V2 분석 결과 조회 완료",
    }
