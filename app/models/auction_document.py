from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime

from app.core.database import Base


class AuctionDocument(Base):
    __tablename__ = "auction_document"
    __table_args__ = {"schema": "mcp4"}

    id = Column(Integer, primary_key=True, index=True)

    auction_id = Column(Integer, nullable=False)

    document_type = Column(String(50), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)

    pages = Column(Integer, default=0)

    ocr_status = Column(String(30), default="READY")
    analysis_status = Column(String(30), default="READY")

    summary = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
