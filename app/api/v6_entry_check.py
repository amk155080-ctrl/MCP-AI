from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v6/entry",
    tags=["entry-check-v6"]
)


@router.get("/check")
def entry_check(
    limit: int = Query(5, description="진입 판단 종목 수")
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
                "message": "진입 판단 대상 종목이 없습니다."
            }

        results = []

        for row in rows:
            total_score = float(row["total_score"] or 0)
            risk_score = float(row["risk_score"] or 0)
            confidence = float(row["confidence"] or 0)
            target_price = float(row["target_price"] or 0)
            stop_loss = float(row["stop_loss"] or 0)

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

            passed_conditions = []
            failed_conditions = []

            if final_signal in ["STRONG_BUY", "BUY"]:
                passed_conditions.append("BUY 이상 신호")
            else:
                failed_conditions.append("BUY 이상 신호 미충족")

            if committee_score >= 70:
                passed_conditions.append("위원회 점수 70점 이상")
            else:
                failed_conditions.append("위원회 점수 70점 미만")

            if risk_score >= 60:
                passed_conditions.append("리스크 점수 60점 이상")
            else:
                failed_conditions.append("리스크 점수 60점 미만")

            if confidence >= 70:
                passed_conditions.append("신뢰도 70점 이상")
            else:
                failed_conditions.append("신뢰도 70점 미만")

            if target_price > 0 and stop_loss > 0:
                passed_conditions.append("목표가/손절가 존재")
            else:
                failed_conditions.append("목표가/손절가 없음")

            if len(failed_conditions) == 0:
                entry_status = "ENTRY_OK"
                action = "진입 가능"
            elif len(failed_conditions) <= 2 and final_signal in ["STRONG_BUY", "BUY"]:
                entry_status = "ENTRY_WAIT"
                action = "분할 진입 또는 관찰"
            else:
                entry_status = "ENTRY_BLOCK"
                action = "진입 보류"

            results.append({
                "stock_code": row["stock_code"],
                "stock_name": row["stock_name"],
                "committee_score": committee_score,
                "final_signal": final_signal,
                "entry_status": entry_status,
                "action": action,
                "total_score": total_score,
                "risk_score": risk_score,
                "confidence": confidence,
                "target_price": target_price,
                "stop_loss": stop_loss,
                "smart_money_net": int(row["smart_money_net"] or 0),
                "passed_conditions": passed_conditions,
                "failed_conditions": failed_conditions
            })

        results.sort(
            key=lambda x: (
                x["entry_status"] != "ENTRY_OK",
                x["entry_status"] != "ENTRY_WAIT",
                -x["committee_score"]
            )
        )

        return {
            "found": True,
            "version": "MCP 6.2",
            "entry_ok_count": len([
                item for item in results
                if item["entry_status"] == "ENTRY_OK"
            ]),
            "entry_wait_count": len([
                item for item in results
                if item["entry_status"] == "ENTRY_WAIT"
            ]),
            "entry_block_count": len([
                item for item in results
                if item["entry_status"] == "ENTRY_BLOCK"
            ]),
            "top_entry": results[0] if results else None,
            "items": results,
            "comment": "진입 가능 여부 판단 완료"
        }

    finally:
        db.close()
