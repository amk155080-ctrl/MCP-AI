from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v6/buy-priority",
    tags=["buy-priority-v6"]
)


@router.get("/top")
def buy_priority_top(
    limit: int = Query(5, description="매수 우선순위 종목 수")
):
    db = SessionLocal()

    try:
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

        if not rows:
            return {
                "found": False,
                "message": "매수 우선순위 대상 종목이 없습니다."
            }

        candidates = []

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

            if final_signal in ["STRONG_BUY", "BUY"]:
                candidates.append({
                    "stock_code": row["stock_code"],
                    "stock_name": row["stock_name"],
                    "committee_score": committee_score,
                    "final_signal": final_signal,
                    "total_score": total_score,
                    "risk_score": risk_score,
                    "confidence": confidence,
                    "target_price": float(row["target_price"] or 0),
                    "stop_loss": float(row["stop_loss"] or 0),
                    "smart_money_net": int(row["smart_money_net"] or 0),
                })

        candidates.sort(
            key=lambda x: x["committee_score"],
            reverse=True
        )

        buy_priority = []

        for idx, item in enumerate(candidates, start=1):
            buy_priority.append({
                "rank": idx,
                "stock_code": item["stock_code"],
                "stock_name": item["stock_name"],
                "committee_score": item["committee_score"],
                "final_signal": item["final_signal"],
                "total_score": item["total_score"],
                "risk_score": item["risk_score"],
                "confidence": item["confidence"],
                "target_price": item["target_price"],
                "stop_loss": item["stop_loss"],
                "smart_money_net": item["smart_money_net"],
                "action": make_action(
                    item["committee_score"],
                    item["final_signal"],
                    item["risk_score"]
                )
            })

        return {
            "found": True,
            "version": "MCP 6.1",
            "total_buy_candidates": len(buy_priority),
            "top_buy": buy_priority[0] if buy_priority else None,
            "buy_priority": buy_priority,
            "comment": "매수 우선순위 산출 완료"
        }

    finally:
        db.close()


def make_action(
    committee_score: float,
    final_signal: str,
    risk_score: float
):
    if final_signal == "STRONG_BUY" and risk_score >= 70:
        return "우선 매수 후보"
    elif committee_score >= 75 and risk_score >= 65:
        return "분할 매수 후보"
    elif committee_score >= 70:
        return "관찰 후 매수 후보"
    else:
        return "매수 보류"
