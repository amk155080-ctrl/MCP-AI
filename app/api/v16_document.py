import os
import shutil

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import UploadFile

from sqlalchemy.orm import Session

from app.core.database import SessionLocal

from app.schemas.auction_document_schema import (
    AuctionDocumentCreate,
    AuctionDocumentUpdate,
)

from app.services.auction_document_service import (
    AuctionDocumentService,
)
from app.services.auction_ocr_service import AuctionOCRService

router = APIRouter(
    prefix="/api/v16/document",
    tags=["MCP16 Document Center"],
)


UPLOAD_DIR = "uploads/documents"

os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload")
async def upload_document(
    auction_id: int,
    document_type: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename,
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    data = AuctionDocumentCreate(
        auction_id=auction_id,
        document_type=document_type,
        file_name=file.filename,
        file_path=file_path,
        pages=0,
        ocr_status="READY",
        analysis_status="READY",
    )

    row = AuctionDocumentService.create(db, data)

    return {
        "found": True,
        "version": "MCP 16.1",
        "document": AuctionDocumentService.to_dict(row),
        "message": "문서 업로드 완료",
    }


@router.get("/list")
def get_documents(
    db: Session = Depends(get_db),
):

    items = AuctionDocumentService.get_all(db)

    return {
        "found": True,
        "version": "MCP 16.1",
        "count": len(items),
        "items": items,
    }


@router.get("/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):

    item = AuctionDocumentService.get_by_id(
        db,
        document_id,
    )

    if not item:
        return {
            "found": False,
            "message": "문서를 찾을 수 없습니다.",
        }

    return {
        "found": True,
        "version": "MCP 16.1",
        "document": item,
    }


@router.get("/auction/{auction_id}")
def get_auction_documents(
    auction_id: int,
    db: Session = Depends(get_db),
):

    items = AuctionDocumentService.get_by_auction_id(
        db,
        auction_id,
    )

    return {
        "found": True,
        "version": "MCP 16.1",
        "count": len(items),
        "items": items,
    }


@router.put("/{document_id}")
def update_document(
    document_id: int,
    data: AuctionDocumentUpdate,
    db: Session = Depends(get_db),
):

    row = AuctionDocumentService.update(
        db,
        document_id,
        data,
    )

    if not row:
        return {
            "found": False,
            "message": "문서를 찾을 수 없습니다.",
        }

    return {
        "found": True,
        "version": "MCP 16.1",
        "document": AuctionDocumentService.to_dict(row),
    }


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
):

    deleted = AuctionDocumentService.delete(
        db,
        document_id,
    )

    return {
        "found": deleted,
        "version": "MCP 16.1",
    }
@router.post("/ocr/{document_id}")
def run_document_ocr(
    document_id: int,
    db: Session = Depends(get_db),
):

    result = AuctionOCRService.run_ocr(
        db,
        document_id,
    )

    if result is None:
        return {
            "found": False,
            "version": "MCP 16.2",
            "message": "문서를 찾을 수 없습니다.",
        }

    return {
        "found": True,
        "version": "MCP 16.2",
        "ocr": result,
        "message": "문서 OCR/Text Extract 완료",
    }
