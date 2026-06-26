from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Numeric
from sqlalchemy import DateTime

from app.core.database import Base


class AuctionAsset(Base):
    __tablename__ = "auction_asset"
    __table_args__ = {"schema": "mcp4"}

    id = Column(Integer, primary_key=True, index=True)

    case_number = Column(String(100))
    item_number = Column(String(50))

    address = Column(String(500))

    appraisal_price = Column(
        Numeric(20, 2),
        default=0
    )

    minimum_price = Column(
        Numeric(20, 2),
        default=0
    )

    expected_bid_price = Column(
        Numeric(20, 2),
        default=0
    )

    expected_sale_price = Column(
        Numeric(20, 2),
        default=0
    )

    status = Column(
        String(30),
        default="WATCH"
    )

    bid_date = Column(String(50))

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
