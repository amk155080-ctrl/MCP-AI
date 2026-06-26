from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v6/position",
    tags=["position-size-v6"]
)


@router.get("/size")
def position_size(
    capital: int = Query(..., description="총 투자금"),
    limit: int = Query(5, description="매수 후보 종목 수")
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
                "message": "매수 금액 계산 대상 종목이 없습니다."
            }

        candidates = []

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

            if (
                final_signal in ["STRONG_BUY", "BUY"]
                and committee_score >= 70
                and confidence >= 70
                and target_price > 0
                and stop_loss > 0
            ):
                entry_status = "ENTRY_OK" if risk_score >= 60 else "ENTRY_WAIT"
            else:
                entry_status = "ENTRY_BLOCK"

            if entry_status in ["ENTRY_OK", "ENTRY_WAIT"]:
                base_weight = committee_score

                if entry_status == "ENTRY_WAIT":
                    base_weight *= 0.5

                if risk_score < 60:
                    base_weight *= 0.8

                candidates.append({
                    "stock_code": row["stock_code"],
                    "stock_name": row["stock_name"],
                    "committee_score": committee_score,
                    "final_signal": final_signal,
                    "entry_status": entry_status,
                    "total_score": total_score,
                    "risk_score": risk_score,
                    "confidence": confidence,
                    "target_price": target_price,
                    "stop_loss": stop_loss,
                    "smart_money_net": int(row["smart_money_net"] or 0),
                    "base_weight": base_weight
                })

        if not candidates:
            return {
                "found": False,
                "message": "매수 가능 종목이 없습니다."
            }

        total_weight = sum(
            item["base_weight"]
            for item in candidates
        )

        positions = []

        for item in candidates:
            weight_percent = (
                item["base_weight"] / total_weight * 100
                if total_weight > 0
                else 0
            )

            if item["entry_status"] == "ENTRY_OK":
                max_weight = 35.0
            else:
                max_weight = 15.0

            weight_percent = min(weight_percent, max_weight)

            buy_amount = int(
                capital * weight_percent / 100
            )

            positions.append({
                "stock_code": item["stock_code"],
                "stock_name": item["stock_name"],
                "entry_status": item["entry_status"],
                "final_signal": item["final_signal"],
                "committee_score": item["committee_score"],
                "risk_score": item["risk_score"],
                "recommended_weight_percent": round(weight_percent, 2),
                "buy_amount": buy_amount,
                "target_price": item["target_price"],
                "stop_loss": item["stop_loss"],
                "action": make_position_action(
                    item["entry_status"],
                    weight_percent
                )
            })

        used_capital = sum(
            item["buy_amount"]
            for item in positions
        )

        cash = capital - used_capital

        return {
            "found": True,
            "version": "MCP 6.3",
            "capital": capital,
            "used_capital": used_capital,
            "cash": cash,
            "position_count": len(positions),
            "positions": positions,
            "comment": "진입 가능 여부와 리스크를 반영한 매수 금액 계산 완료"
        }

    finally:
        db.close()


def make_position_action(entry_status: str, weight_percent: float):
    if entry_status == "ENTRY_OK" and weight_percent >= 25:
        return "주력 매수"
    elif entry_status == "ENTRY_OK":
        return "정상 매수"
    elif entry_status == "ENTRY_WAIT":
        return "소액 분할 매수"
    else:
        return "매수 보류"
