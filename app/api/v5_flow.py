from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(prefix="/api/v5/flow", tags=["flow-v5"])


@router.get("/smart_money")
def smart_money_v5(limit: int = Query(100, description="조회 개수")):
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT
                d.trade_date,
                d.stock_code,
                m.stock_name,

                d.foreign_net,
                d.institution_net,
                d.financial_investment_net,
                d.trust_net,
                d.insurance_net,
                d.private_fund_net,
                d.bank_net,
                d.pension_net,
                d.program_net,

                (
                    COALESCE(d.foreign_net,0)
                  + COALESCE(d.financial_investment_net,0)
                  + COALESCE(d.trust_net,0)
                  + COALESCE(d.pension_net,0)
                ) AS smart_money_core,

                (
                    COALESCE(d.foreign_net,0)
                  + COALESCE(d.institution_net,0)
                  + COALESCE(d.pension_net,0)
                ) AS smart_money_total

            FROM mcp4.investor_flow_detail_daily d
            LEFT JOIN mcp4.stock_master m
              ON d.stock_code = m.stock_code
            WHERE d.trade_date = (
                SELECT MAX(trade_date)
                FROM mcp4.investor_flow_detail_daily
            )
            ORDER BY smart_money_core DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()

        return [dict(r) for r in rows]
    finally:
        db.close()


@router.get("/detail")
def flow_detail(
    stock_code: str = Query(..., description="종목코드 6자리"),
):
    db = SessionLocal()
    try:
        row = db.execute(text("""
            SELECT
                d.trade_date,
                d.stock_code,
                m.stock_name,

                d.foreign_net,
                d.institution_net,
                d.financial_investment_net,
                d.trust_net,
                d.insurance_net,
                d.private_fund_net,
                d.bank_net,
                d.pension_net,
                d.program_net,

                (
                    COALESCE(d.foreign_net,0)
                  + COALESCE(d.financial_investment_net,0)
                  + COALESCE(d.trust_net,0)
                  + COALESCE(d.pension_net,0)
                ) AS smart_money_core,

                (
                    COALESCE(d.foreign_net,0)
                  + COALESCE(d.institution_net,0)
                  + COALESCE(d.pension_net,0)
                ) AS smart_money_total

            FROM mcp4.investor_flow_detail_daily d
            LEFT JOIN mcp4.stock_master m
              ON d.stock_code = m.stock_code
            WHERE d.stock_code = :stock_code
            ORDER BY d.trade_date DESC
            LIMIT 1
        """), {"stock_code": stock_code}).mappings().first()

        if not row:
            return {
                "found": False,
                "stock_code": stock_code,
                "message": "상세 수급 데이터가 없습니다.",
            }

        result = dict(row)
        result["found"] = True
        return result
    finally:
        db.close()


@router.get("/institution_detail")
def institution_detail_v5(limit: int = Query(100, description="조회 개수")):
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT
                d.trade_date,
                d.stock_code,
                m.stock_name,

                d.institution_net,
                d.financial_investment_net,
                d.trust_net,
                d.insurance_net,
                d.private_fund_net,
                d.bank_net,
                d.pension_net,

                (
                    COALESCE(d.financial_investment_net,0)
                  + COALESCE(d.trust_net,0)
                  + COALESCE(d.pension_net,0)
                ) AS core_institution_net

            FROM mcp4.investor_flow_detail_daily d
            LEFT JOIN mcp4.stock_master m
              ON d.stock_code = m.stock_code
            WHERE d.trade_date = (
                SELECT MAX(trade_date)
                FROM mcp4.investor_flow_detail_daily
            )
            ORDER BY core_institution_net DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()

        return [dict(r) for r in rows]
    finally:
        db.close()
