from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Numeric
from sqlalchemy import DateTime

from app.core.database import Base


class FamilyAsset(Base):
    __tablename__ = "family_asset"
    __table_args__ = {"schema": "mcp4"}

    id = Column(Integer, primary_key=True, index=True)

    owner = Column(String(50), nullable=False)

    asset_category = Column(String(50), nullable=False)

    asset_name = Column(String(200), nullable=False)

    purchase_price = Column(
        Numeric(20, 2),
        default=0
    )

    current_value = Column(
        Numeric(20, 2),
        default=0
    )

    memo = Column(String(255))

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
