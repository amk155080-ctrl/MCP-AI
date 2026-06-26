from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(prefix="/api/v4/holding", tags=["holding-v4"])


def make_signal(total_score, smart_money_net):
    total_score = float(total_score or 0)
    smart_money_net = float(smart_money_net or 0)

    if total_score >= 80 and smart_money_net > 0:
        return "STRONG_BUY"

    if total_score >= 70 and smart_money_net > 0:
        return "BUY"

    if total_score >= 60:
        return "WATCH"

    if total_score <= 45 and smart_money_net < 0:
        return "STRONG_SELL"

    if total_score <= 55 and smart_money_net < 0:
        return "SELL"

    return "HOLD"


def make_summary(signal, stock_name, total_score, smart_money_net):
    total_score = float(total_score or 0)
    smart_money_net = float(smart_money_net or 0)

    if signal == "STRONG_BUY":
        return f"{stock_name}은 점수와 스마트머니 수급이 모두 강한 강한 매수 후보입니다."

    if signal == "BUY":
        return f"{stock_name}은 기관/외국인 수급이 양호하고 종합점수도 우수한 매수 관심 종목입니다."

    if signal == "WATCH":
        return f"{stock_name}은 관찰 구간입니다. 추가 수급 유입이나 점수 개선 여부를 확인하는 것이 좋습니다."

    if signal == "SELL":
        return f"{stock_name}은 스마트머니 순매도가 발생하고 점수가 낮아 비중 축소 검토가 필요합니다."

    if signal == "STRONG_SELL":
        return f"{stock_name}은 점수와 수급 모두 약해 강한 주의가 필요한 종목입니다."

    return f"{stock_name}은 현재 뚜렷한 매수/매도 신호가 약한 중립 상태입니다."


@router.get("/check")
def holding_check(stock_code: str = Query(..., description="종목코드 6자리")):
    db = SessionLocal()

    try:
        row = db.execute(text("""
            SELECT
                s.trade_date,
                s.stock_code,
                s.stock_name,
                s.supply_score,
                s.momentum_score,
                s.macro_score,
                s.semiconductor_score,
                s.risk_score,
                s.total_score,
                s.grade,

                p.close_price,
                p.change_rate,
                p.trade_value,
                p.market_cap,

                COALESCE(f.foreign_net, 0) AS foreign_net,
                COALESCE(f.institution_net, 0) AS institution_net,
                COALESCE(f.pension_net, 0) AS pension_net,
                COALESCE(f.program_net, 0) AS program_net,

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

            WHERE s.stock_code = :stock_code

            ORDER BY s.trade_date DESC

            LIMIT 1
        """), {"stock_code": stock_code}).mappings().first()

        if not row:
            return {
                "stock_code": stock_code,
                "found": False,
                "message": "해당 종목의 점수 데이터가 없습니다.",
            }

        result = dict(row)

        signal = make_signal(
            result.get("total_score"),
            result.get("smart_money_net"),
        )

        result["found"] = True
        result["signal"] = signal
        result["summary"] = make_summary(
            signal,
            result.get("stock_name"),
            result.get("total_score"),
            result.get("smart_money_net"),
        )

        return result

    finally:
        db.close()
