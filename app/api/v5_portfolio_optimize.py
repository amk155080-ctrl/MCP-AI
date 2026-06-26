from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(prefix="/api/v5/portfolio", tags=["portfolio-v5"])


@router.get("/optimize")
def optimize_portfolio(
    limit: int = Query(5, description="포트폴리오 편입 종목 수")
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
                "message": "포트폴리오 최적화 대상 종목이 없습니다."
            }

        items = [dict(r) for r in rows]
        total_score = sum(float(item["total_score"] or 0) for item in items)

        portfolio = []

        for item in items:
            score = float(item["total_score"] or 0)
            risk_score = float(item["risk_score"] or 0)

            raw_weight = score / total_score * 100 if total_score > 0 else 0

            if risk_score < 50:
                raw_weight *= 0.7
            elif risk_score < 65:
                raw_weight *= 0.85

            weight = min(raw_weight, 30.0)

            if weight < 5:
                weight = 5.0

            portfolio.append({
                "trade_date": str(item["trade_date"]),
                "stock_code": item["stock_code"],
                "stock_name": item["stock_name"],
                "total_score": score,
                "risk_score": risk_score,
                "signal": item["signal"],
                "confidence": float(item["confidence"] or 0),
                "target_price": float(item["target_price"] or 0),
                "stop_loss": float(item["stop_loss"] or 0),
                "smart_money_net": int(item["smart_money_net"] or 0),
                "recommended_weight_percent": round(weight, 2),
                "reason": make_weight_reason(weight, risk_score)
            })

        weight_sum = sum(item["recommended_weight_percent"] for item in portfolio)

        for item in portfolio:
            item["recommended_weight_percent"] = round(
                item["recommended_weight_percent"] / weight_sum * 100,
                2
            )

        return {
            "found": True,
            "version": "MCP 5.9",
            "base": "total_score + risk_score",
            "count": len(portfolio),
            "total_weight_percent": round(
                sum(item["recommended_weight_percent"] for item in portfolio),
                2
            ),
            "max_weight_limit_percent": 30.0,
            "portfolio": portfolio,
            "comment": "점수와 리스크를 반영한 포트폴리오 최적화 완료"
        }

    finally:
        db.close()


def make_weight_reason(weight: float, risk_score: float):
    if risk_score < 50:
        return "리스크 점수 낮음, 비중 축소"
    elif weight >= 25:
        return "핵심 편입 종목"
    elif weight >= 15:
        return "중간 비중 편입"
    else:
        return "소액 분산 편입"
