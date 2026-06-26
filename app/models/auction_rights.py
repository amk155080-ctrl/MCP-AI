from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Text
from sqlalchemy import DateTime

from app.core.database import Base


class AuctionRights(Base):
    __tablename__ = "auction_rights"
    __table_args__ = {"schema": "mcp4"}

    id = Column(Integer, primary_key=True, index=True)

    auction_id = Column(Integer, nullable=False, index=True)
    document_id = Column(Integer, nullable=False, index=True)

    base_right = Column(String(200))
    tenant_priority = Column(String(100))
    occupancy = Column(String(100))

    lease_deposit = Column(Float)
    takeover_amount = Column(Float)

    confidence = Column(Float)
    parser_version = Column(String(50))
    raw_summary = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
