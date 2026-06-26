from sqlalchemy import Column, String, Date, Numeric, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class StockPriceDaily(Base):
    __tablename__ = "stock_price_daily"
    __table_args__ = {"schema": "mcp4"}

    trade_date = Column(Date, primary_key=True)
    stock_code = Column(String(20), primary_key=True)
    stock_name = Column(String(120))
    open_price = Column(Numeric(20, 2))
    high_price = Column(Numeric(20, 2))
    low_price = Column(Numeric(20, 2))
    close_price = Column(Numeric(20, 2))
    change_amount = Column(Numeric(20, 2))
    change_rate = Column(Numeric(10, 4))
    volume = Column(BigInteger)
    trade_value = Column(Numeric(30, 0))
    market_cap = Column(Numeric(30, 0))
    listed_shares = Column(BigInteger)

class StockScoreDaily(Base):
    __tablename__ = "stock_score_daily"
    __table_args__ = {"schema": "mcp4"}

    trade_date = Column(Date, primary_key=True)
    stock_code = Column(String(20), primary_key=True)
    stock_name = Column(String(120))
    supply_score = Column(Numeric(6, 2))
    momentum_score = Column(Numeric(6, 2))
    macro_score = Column(Numeric(6, 2))
    semiconductor_score = Column(Numeric(6, 2))
    risk_score = Column(Numeric(6, 2))
    total_score = Column(Numeric(6, 2))
    grade = Column(String(30))
