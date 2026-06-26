from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(prefix="/api/v5/signal", tags=["signal-v5"])


def classify_signal(total_score, risk_score, smart_money_net, change_rate):
    total_score = float(total_score or 0)
    risk_score = float(risk_score or 0)
    smart_money_net = float(smart_money_net or 0)
    change_rate = float(change_rate or 0)

    confidence = 50
    reasons = []
    signal = "WATCH"
    action = "관찰"

    overheated = False
    extreme_overheated = False

    if change_rate >= 25:
        extreme_overheated = True
        overheated = True
        confidence -= 25
        reasons.append("초단기 급등 과열")
    elif change_rate >= 20:
        overheated = True
        confidence -= 20
        reasons.append("단기 급등 과열")
    elif change_rate >= 15:
        confidence -= 10
        reasons.append("단기 상승폭 큼")

    if smart_money_net >= 10000000000:
        confidence += 15
        reasons.append("스마트머니 강한 순유입")
    elif smart_money_net > 0:
        confidence += 8
        reasons.append("스마트머니 순유입")
    elif smart_money_net < 0:
        confidence -= 15
        reasons.append("스마트머니 순유출")

    if total_score >= 80:
        confidence += 20
        reasons.append("종합점수 매우 우수")
    elif total_score >= 70:
        confidence += 12
        reasons.append("종합점수 우수")
    elif total_score < 55:
        confidence -= 15
        reasons.append("종합점수 부진")

    if risk_score >= 70:
        confidence += 8
        reasons.append("리스크 양호")
    elif risk_score < 60:
        confidence -= 8
        reasons.append("변동성 주의")

    if total_score >= 80 and smart_money_net > 0 and risk_score >= 65:
        signal = "STRONG_BUY"
        action = "강한 매수관심"
    elif total_score >= 70 and smart_money_net > 0:
        signal = "BUY"
        action = "매수관심"
    elif total_score >= 65 and smart_money_net >= 10000000000 and risk_score >= 70:
        signal = "BUY"
        action = "스마트머니 기반 매수관심"
    elif total_score < 45 and smart_money_net < 0:
        signal = "STRONG_SELL"
        action = "강한 비중축소"
    elif total_score < 55 and smart_money_net < 0:
        signal = "SELL"
        action = "비중축소"
    elif smart_money_net > 0 and total_score >= 60:
        signal = "WATCH"
        action = "관심관찰"

    # MCP 5.4 핵심: 과열 종목은 BUY를 WATCH로 낮춤
    if overheated and signal in ["BUY", "STRONG_BUY"]:
        signal = "WATCH"
        action = "과열 관찰"

    if extreme_overheated and signal in ["BUY", "STRONG_BUY", "WATCH"]:
        signal = "WATCH"
        action = "급등 과열 관망"

    confidence = max(0, min(100, confidence))

    return signal, action, confidence, reasons

@router.get("/realtime")
def realtime_signal(
    limit: int = Query(50, description="조회 개수"),
    signal_filter: str = Query("ALL", description="ALL, STRONG_BUY, BUY, WATCH, SELL"),
):
    db = SessionLocal()

    try:
        rows = db.execute(text("""
            SELECT
                s.trade_date,
                s.stock_code,
                s.stock_name,
                s.total_score,
                s.risk_score,
                s.grade,

                p.close_price,
                p.change_rate,
                p.trade_value,
                p.market_cap,

                COALESCE(f.foreign_net,0) AS foreign_net,
                COALESCE(f.institution_net,0) AS institution_net,
                COALESCE(f.pension_net,0) AS pension_net,

                (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
                ) AS smart_money_net

            FROM mcp4.stock_score_daily s

            JOIN mcp4.stock_price_daily p
              ON s.trade_date = p.trade_date
             AND s.stock_code = p.stock_code

            LEFT JOIN mcp4.investor_flow_daily f
              ON s.trade_date = f.trade_date
             AND s.stock_code = f.stock_code

            WHERE s.trade_date = (
                SELECT MAX(trade_date)
                FROM mcp4.stock_score_daily
            )
              AND COALESCE(p.trade_value,0) >= 10000000000
              AND COALESCE(p.market_cap,0) >= 100000000000

            ORDER BY
                s.total_score DESC,
                smart_money_net DESC

            LIMIT 500
        """)).mappings().all()

        result = []

        for r in rows:
            signal, action, confidence, reasons = classify_signal(
                r["total_score"],
                r["risk_score"],
                r["smart_money_net"],
                r["change_rate"],
            )

            if signal_filter != "ALL" and signal != signal_filter:
                continue

            item = dict(r)
            item["signal"] = signal
            item["action"] = action
            item["confidence"] = confidence
            item["reasons"] = reasons

            result.append(item)

            if len(result) >= limit:
                break

        return {
            "found": True,
            "count": len(result),
            "signal_filter": signal_filter,
            "items": result,
        }

    finally:
        db.close()
