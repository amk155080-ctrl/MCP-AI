from pydantic import BaseModel
from typing import Optional


class AuctionDocumentCreate(BaseModel):
    auction_id: int
    document_type: str
    file_name: str
    file_path: str
    pages: int = 0
    ocr_status: str = "READY"
    analysis_status: str = "READY"
    summary: Optional[str] = None


class AuctionDocumentUpdate(BaseModel):
    ocr_status: Optional[str] = None
    analysis_status: Optional[str] = None
    summary: Optional[str] = None
    pages: Optional[int] = None
