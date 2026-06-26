from sqlalchemy.orm import Session

from app.models.auction_document import AuctionDocument
from app.models.auction_rights import AuctionRights
from app.services.rights_parser import parse_rights_from_text


def analyze_rights_by_document_id(db: Session, document_id: int):

    document = (
        db.query(AuctionDocument)
        .filter(AuctionDocument.id == document_id)
        .first()
    )

    if not document:
        return {
            "found": False,
            "version": "MCP 16.3",
            "message": "Document not found",
            "document_id": document_id,
        }

    # 현재 auction_document 모델 기준 OCR Text는 summary 컬럼에 저장됨
    ocr_text = document.summary

    if not ocr_text:
        return {
            "found": False,
            "version": "MCP 16.3",
            "message": "OCR text is empty. auction_document.summary is empty.",
            "document_id": document.id,
            "ocr_status": document.ocr_status,
            "analysis_status": document.analysis_status,
        }

    parsed = parse_rights_from_text(ocr_text)

    rights = (
        db.query(AuctionRights)
        .filter(AuctionRights.document_id == document.id)
        .first()
    )

    if not rights:
        rights = AuctionRights(
            auction_id=document.auction_id,
            document_id=document.id,
        )
        db.add(rights)

    rights.base_right = parsed["base_right"]
    rights.tenant_priority = parsed["tenant_priority"]
    rights.occupancy = parsed["occupancy"]
    rights.lease_deposit = parsed["lease_deposit"]
    rights.takeover_amount = parsed["takeover_amount"]
    rights.confidence = parsed["confidence"]
    rights.parser_version = parsed["parser_version"]
    rights.raw_summary = parsed["raw_summary"]

    document.analysis_status = "RIGHTS_DONE"

    db.commit()
    db.refresh(rights)
    db.refresh(document)

    return {
        "found": True,
        "version": "MCP 16.3",
        "message": "Rights intelligence analysis completed",
        "document_id": document.id,
        "auction_id": document.auction_id,
        "ocr_status": document.ocr_status,
        "analysis_status": document.analysis_status,
        "rights_id": rights.id,
        "base_right": rights.base_right,
        "tenant_priority": rights.tenant_priority,
        "occupancy": rights.occupancy,
        "lease_deposit": rights.lease_deposit,
        "takeover_amount": rights.takeover_amount,
        "confidence": rights.confidence,
        "parser_version": rights.parser_version,
        "raw_summary": rights.raw_summary,
    }
