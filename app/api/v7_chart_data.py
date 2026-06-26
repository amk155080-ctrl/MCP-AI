from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v7/dashboard",
    tags=["chart-data-v7"]
)


@router.get("/chart-data")
def chart_data():
    db = SessionLocal()

    try:
        log = db.execute(text("""
            SELECT *
            FROM mcp4.execution_log
            ORDER BY id DESC
            LIMIT 1
        """)).mappings().first()

        if not log:
            return {
                "found": False,
                "message": "실행 로그가 없습니다."
            }

        rows = db.execute(text("""
            SELECT
                stock_code,
                stock_name,
                total_score,
                risk_score,
                confidence,
                target_price,
                stop_loss,
                smart_money_net
            FROM mcp4.recommendation_history
            WHERE trade_date = (
                SELECT MAX(trade_date)
                FROM mcp4.recommendation_history
            )
            ORDER BY total_score DESC
            LIMIT 5
        """)).mappings().all()

        top5_scores = []
        entry_status_count = {
            "ENTRY_OK": 0,
            "ENTRY_WAIT": 0,
            "ENTRY_BLOCK": 0
        }

        smart_money_data = []

        for row in rows:
            total_score = float(row["total_score"] or 0)
            risk_score = float(row["risk_score"] or 0)
            confidence = float(row["confidence"] or 0)

            committee_score = round(
                total_score * 0.5 +
                risk_score * 0.2 +
                confidence * 0.3,
                2
            )

            if committee_score >= 80:
                final_signal = "STRONG_BUY"
            elif committee_score >= 70:
                final_signal = "BUY"
            elif committee_score >= 60:
                final_signal = "HOLD"
            else:
                final_signal = "SELL"

            if final_signal in ["STRONG_BUY", "BUY"] and risk_score >= 60:
                entry_status = "ENTRY_OK"
            elif final_signal in ["STRONG_BUY", "BUY"]:
                entry_status = "ENTRY_WAIT"
            else:
                entry_status = "ENTRY_BLOCK"

            entry_status_count[entry_status] += 1

            top5_scores.append({
                "stock_code": row["stock_code"],
                "stock_name": row["stock_name"],
                "committee_score": committee_score,
                "total_score": total_score,
                "risk_score": risk_score,
                "confidence": confidence,
                "entry_status": entry_status,
                "final_signal": final_signal
            })

            smart_money_data.append({
                "stock_code": row["stock_code"],
                "stock_name": row["stock_name"],
                "smart_money_net": int(row["smart_money_net"] or 0)
            })

        loss_compare = [
            {
                "name": "원래 손실률",
                "value": float(log["raw_portfolio_loss_percent"] or 0)
            },
            {
                "name": "안전 손실률",
                "value": float(log["safe_portfolio_loss_percent"] or 0)
            }
        ]

        capital_allocation = [
            {
                "name": "안전 주문금액",
                "value": int(log["safe_total_order_amount"] or 0)
            },
            {
                "name": "현금",
                "value": int(log["cash"] or 0)
            }
        ]

        entry_status_distribution = [
            {
                "name": "ENTRY_OK",
                "value": entry_status_count["ENTRY_OK"]
            },
            {
                "name": "ENTRY_WAIT",
                "value": entry_status_count["ENTRY_WAIT"]
            },
            {
                "name": "ENTRY_BLOCK",
                "value": entry_status_count["ENTRY_BLOCK"]
            }
        ]

        return {
            "found": True,
            "version": "MCP 7.5",
            "trade_date": str(log["trade_date"]),
            "dashboard_status": "READY"
            if log["final_execution"] == "SAFE_EXECUTE"
            else "CAUTION",
            "summary": {
                "final_execution": log["final_execution"],
                "strategy_grade": log["strategy_grade"],
                "top_stock_code": log["top_stock_code"],
                "top_stock_name": log["top_stock_name"],
                "safe_total_order_amount": int(log["safe_total_order_amount"] or 0),
                "cash": int(log["cash"] or 0),
                "safe_portfolio_loss_percent": float(log["safe_portfolio_loss_percent"] or 0),
                "raw_portfolio_loss_percent": float(log["raw_portfolio_loss_percent"] or 0),
                "reduce_ratio": float(log["reduce_ratio"] or 0)
            },
            "charts": {
                "loss_compare": loss_compare,
                "capital_allocation": capital_allocation,
                "top5_scores": top5_scores,
                "entry_status_distribution": entry_status_distribution,
                "smart_money": smart_money_data
            },
            "comment": "차트 데이터 조회 완료"
        }

    finally:
        db.close()
