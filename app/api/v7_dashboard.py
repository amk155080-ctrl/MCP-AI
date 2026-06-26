from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v7",
    tags=["dashboard-v7"]
)


@router.get("/dashboard")
def dashboard(
    capital: int = Query(...),
    limit: int = Query(5),
    max_loss_percent: float = Query(5.0)
):
    db = SessionLocal()

    try:
        latest_log = db.execute(text("""
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
                orders_json,
                comment,
                created_at
            FROM mcp4.execution_log
            ORDER BY id DESC
            LIMIT 1
        """)).mappings().first()

        rows = db.execute(text("""
            SELECT
                trade_date,
                stock_code,
                stock_name,
                total_score,
                risk_score,
                signal,
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
            LIMIT :limit
        """), {
            "limit": limit
        }).mappings().all()

        recommendations = []

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

            recommendations.append({
                "stock_code": row["stock_code"],
                "stock_name": row["stock_name"],
                "committee_score": committee_score,
                "final_signal": final_signal,
                "entry_status": entry_status,
                "total_score": total_score,
                "risk_score": risk_score,
                "confidence": confidence,
                "target_price": float(row["target_price"] or 0),
                "stop_loss": float(row["stop_loss"] or 0),
                "smart_money_net": int(row["smart_money_net"] or 0)
            })

        if latest_log:
            execution_summary = {
                "log_id": latest_log["id"],
                "trade_date": str(latest_log["trade_date"]),
                "final_execution": latest_log["final_execution"],
                "strategy_grade": latest_log["strategy_grade"],
                "top_stock_code": latest_log["top_stock_code"],
                "top_stock_name": latest_log["top_stock_name"],
                "safe_total_order_amount": int(latest_log["safe_total_order_amount"] or 0),
                "cash": int(latest_log["cash"] or 0),
                "safe_total_expected_loss": int(latest_log["safe_total_expected_loss"] or 0),
                "safe_portfolio_loss_percent": float(latest_log["safe_portfolio_loss_percent"] or 0),
                "raw_portfolio_loss_percent": float(latest_log["raw_portfolio_loss_percent"] or 0),
                "reduce_ratio": float(latest_log["reduce_ratio"] or 0),
                "comment": latest_log["comment"],
                "created_at": str(latest_log["created_at"])
            }
        else:
            execution_summary = None

        dashboard_status = make_dashboard_status(execution_summary)

        return {
            "found": True,
            "version": "MCP 7.0",
            "dashboard_status": dashboard_status,
            "capital": capital,
            "max_loss_percent": max_loss_percent,
            "latest_execution": execution_summary,
            "recommendation_count": len(recommendations),
            "recommendations": recommendations,
            "summary_cards": make_summary_cards(
                execution_summary,
                recommendations
            ),
            "comment": "실전 대시보드 데이터 조회 완료"
        }

    finally:
        db.close()


def make_dashboard_status(execution_summary):
    if not execution_summary:
        return "NO_EXECUTION_LOG"

    final_execution = execution_summary.get("final_execution")

    if final_execution == "SAFE_EXECUTE":
        return "READY"
    elif final_execution == "PARTIAL_EXECUTE":
        return "CAUTION"
    else:
        return "WAIT"


def make_summary_cards(execution_summary, recommendations):
    if not execution_summary:
        return {
            "execution": "실행 로그 없음",
            "risk": "리스크 정보 없음",
            "top_pick": "상위 종목 없음"
        }

    top_pick = execution_summary.get("top_stock_name")

    entry_ok_count = len([
        item for item in recommendations
        if item["entry_status"] == "ENTRY_OK"
    ])

    entry_wait_count = len([
        item for item in recommendations
        if item["entry_status"] == "ENTRY_WAIT"
    ])

    return {
        "execution": execution_summary.get("final_execution"),
        "strategy_grade": execution_summary.get("strategy_grade"),
        "top_pick": top_pick,
        "safe_order_amount": execution_summary.get("safe_total_order_amount"),
        "cash": execution_summary.get("cash"),
        "safe_loss_percent": execution_summary.get("safe_portfolio_loss_percent"),
        "raw_loss_percent": execution_summary.get("raw_portfolio_loss_percent"),
        "entry_ok_count": entry_ok_count,
        "entry_wait_count": entry_wait_count
    }
