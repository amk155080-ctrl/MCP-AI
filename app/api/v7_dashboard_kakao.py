from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v7/dashboard",
    tags=["dashboard-kakao-v7"]
)


@router.get("/kakao")
def dashboard_kakao():
    db = SessionLocal()

    try:

        row = db.execute(text("""
            SELECT
                *
            FROM mcp4.execution_log
            ORDER BY id DESC
            LIMIT 1
        """)).mappings().first()

        if not row:
            return {
                "found": False,
                "message": "실행 로그가 없습니다."
            }

        message = f"""
📊 MCP 투자보고서

등급: {row['strategy_grade']}
실행판단: {row['final_execution']}

TOP PICK
{row['top_stock_name']} ({row['top_stock_code']})

진입가능: {row['entry_ok_count']}개
관찰대상: {row['entry_wait_count']}개

안전주문금액: {int(row['safe_total_order_amount']):,}원
현금보유: {int(row['cash']):,}원

예상손실률: {float(row['safe_portfolio_loss_percent'])}%
원래손실률: {float(row['raw_portfolio_loss_percent'])}%

의견:
{row['comment']}
""".strip()

        return {
            "found": True,
            "version": "MCP 7.2",
            "trade_date": str(row["trade_date"]),
            "message": message
        }

    finally:
        db.close()
