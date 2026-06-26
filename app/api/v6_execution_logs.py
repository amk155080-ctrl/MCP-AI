from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v6/execution",
    tags=["execution-logs-v6"]
)


@router.get("/logs")
def execution_logs(
    limit: int = Query(10, description="조회할 실행 로그 수")
):
    db = SessionLocal()

    try:
        rows = db.execute(text("""
            SELECT
                id,
                trade_date,
                version,
                capital,
                max_loss_percent,
                final_execution,
                strategy_grade,
                candidate_count,
                entry_ok_count,
                entry_wait_count,
                top_stock_code,
                top_stock_name,
                safe_total_order_amount,
                cash,
                safe_total_expected_loss,
                safe_portfolio_loss_percent,
                raw_portfolio_loss_percent,
                reduce_ratio,
                comment,
                created_at
            FROM mcp4.execution_log
            ORDER BY id DESC
            LIMIT :limit
        """), {
            "limit": limit
        }).mappings().all()

        items = []

        for row in rows:
            items.append({
                "id": row["id"],
                "trade_date": str(row["trade_date"]),
                "version": row["version"],
                "capital": int(row["capital"] or 0),
                "max_loss_percent": float(row["max_loss_percent"] or 0),
                "final_execution": row["final_execution"],
                "strategy_grade": row["strategy_grade"],
                "candidate_count": int(row["candidate_count"] or 0),
                "entry_ok_count": int(row["entry_ok_count"] or 0),
                "entry_wait_count": int(row["entry_wait_count"] or 0),
                "top_stock_code": row["top_stock_code"],
                "top_stock_name": row["top_stock_name"],
                "safe_total_order_amount": int(row["safe_total_order_amount"] or 0),
                "cash": int(row["cash"] or 0),
                "safe_total_expected_loss": int(row["safe_total_expected_loss"] or 0),
                "safe_portfolio_loss_percent": float(row["safe_portfolio_loss_percent"] or 0),
                "raw_portfolio_loss_percent": float(row["raw_portfolio_loss_percent"] or 0),
                "reduce_ratio": float(row["reduce_ratio"] or 0),
                "comment": row["comment"],
                "created_at": str(row["created_at"])
            })

        return {
            "found": True,
            "version": "MCP 6.9",
            "count": len(items),
            "latest": items[0] if items else None,
            "items": items,
            "comment": "실행 로그 조회 완료"
        }

    finally:
        db.close()
