from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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
            "version": "MCP 16.5",
            "message": "문서를 찾을 수 없습니다.",
        }

    text = document.summary or ""

    if not text.strip():
        return {
            "found": False,
            "version": "MCP 16.5",
            "document_id": document_id,
            "message": "OCR summary/text가 비어 있습니다. 먼저 /api/v16/document/ocr/{document_id}를 실행하세요.",
        }

    result = analyze(text)

    return {
        "found": True,
        "version": "MCP 16.5",
        "document_id": document.id,
        "auction_id": document.auction_id,
        "document_type": document.document_type,
        "file_name": document.file_name,
        "rights_analysis": result,
        "message": "Rights Engine V2 분석 완료",
    }
