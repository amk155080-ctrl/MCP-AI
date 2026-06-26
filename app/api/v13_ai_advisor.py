from fastapi import APIRouter

from app.api.v9_quote import get_quote
from app.api.v12_dashboard import dashboard
from app.api.v12_performance import get_latest_performance

router = APIRouter(
    prefix="/api/v13",
    tags=["MCP 13 AI Advisor"]
)


@router.get("/market-brief")
def market_brief():
    perf = get_latest_performance()
    dash = dashboard()

    total_return = 0

    if perf.get("found"):
        total_return = float(perf["item"]["total_return"])

    if total_return > 5:
        market_status = "강세"
        recommendation = "공격적 매수 가능"
    elif total_return > 0:
        market_status = "중립"
        recommendation = "기존 포지션 유지"
    else:
        market_status = "약세"
        recommendation = "현금 비중 확대"

    return {
        "found": True,
        "version": "MCP 13.0",
        "market_status": market_status,
        "portfolio_return": total_return,
        "position_count": dash.get("position_count", 0),
        "recommendation": recommendation,
        "message": "AI 시장 브리핑 완료"
    }


@router.get("/stock-review/{stock_code}")
def stock_review(stock_code: str):
    quote = get_quote(stock_code)

    if not quote.get("found"):
        return {
            "found": False,
            "version": "MCP 13.1",
            "stock_code": stock_code,
            "message": "시세 조회 실패"
        }

    change_rate = float(quote.get("change_rate") or 0)

    if change_rate > 5:
        opinion = "강한 상승 추세"
    elif change_rate > 0:
        opinion = "상승 추세"
    elif change_rate > -5:
        opinion = "조정 구간"
    else:
        opinion = "위험 구간"

    return {
        "found": True,
        "version": "MCP 13.1",
        "stock_code": stock_code,
        "stock_name": quote.get("stock_name"),
        "current_price": quote.get("current_price"),
        "change_rate": change_rate,
        "ai_opinion": opinion,
        "message": "AI 종목 분석 완료"
    }


@router.get("/portfolio-review")
def portfolio_review():
    dash = dashboard()

    position_count = dash.get("position_count", 0)

    if position_count == 0:
        grade = "대기"
    elif position_count <= 3:
        grade = "집중 투자"
    else:
        grade = "분산 투자"

    return {
        "found": True,
        "version": "MCP 13.2",
        "position_count": position_count,
        "portfolio_grade": grade,
        "auto_trading_enabled": dash.get("auto_trading_enabled"),
        "auto_order_enabled": dash.get("auto_order_enabled"),
        "message": "AI 포트폴리오 평가 완료"
    }

@router.get("/risk-review")
def risk_review():

    perf = get_latest_performance()
    dash = dashboard()

    total_return = 0

    if perf.get("found"):
        total_return = float(
            perf["item"].get("total_return", 0)
        )

    position_count = dash.get(
        "position_count",
        0
    )

    risk_score = 0

    if total_return < 0:
        risk_score += 50

    if position_count > 5:
        risk_score += 20

    auto_trading = dash.get(
        "auto_trading_enabled",
        False
    )

    if auto_trading:
        risk_score += 10

    if risk_score >= 60:
        risk_level = "HIGH"

    elif risk_score >= 30:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    return {
        "found": True,
        "version": "MCP 13.3",
        "risk_score": risk_score,
        "risk_level": risk_level,
        "portfolio_return": total_return,
        "position_count": position_count,
        "message": "AI 리스크 평가 완료"
    }

@router.get("/investment-committee")
def investment_committee():
    brief = market_brief()
    review = portfolio_review()
    risk = risk_review()

    score = 100

    if risk["risk_level"] == "HIGH":
        score -= 40
    elif risk["risk_level"] == "MEDIUM":
        score -= 20

    if brief["market_status"] == "약세":
        score -= 20

    if score >= 80:
        decision = "BUY"
    elif score >= 60:
        decision = "HOLD"
    else:
        decision = "WAIT"

    return {
        "found": True,
        "version": "MCP 13.4",
        "committee_score": score,
        "decision": decision,
        "market_status": brief["market_status"],
        "risk_level": risk["risk_level"],
        "portfolio_grade": review["portfolio_grade"],
        "message": "AI 투자위원회 판단 완료"
    }


@router.get("/daily-report")
def ai_daily_report():
    brief = market_brief()
    review = portfolio_review()
    risk = risk_review()
    committee = investment_committee()

    return {
        "found": True,
        "version": "MCP 13.5",
        "market_brief": brief,
        "portfolio_review": review,
        "risk_review": risk,
        "committee": committee,
        "message": "AI 일일 리포트 생성 완료"
    }

@router.get("/ranking")
def ai_ranking():

    perf = get_latest_performance()
    dash = dashboard()

    positions = dash.get("positions", [])

    result = []

    for p in positions:

        score = 70

        current_price = float(
            p.get("buy_price", 0)
        )

        target_price = float(
            p.get("target_price", 0)
        )

        stop_price = float(
            p.get("stop_price", 0)
        )

        if target_price > 0:

            reward = (
                target_price - current_price
            ) / current_price * 100

            score += min(reward, 20)

        if stop_price > 0:

            risk = (
                current_price - stop_price
            ) / current_price * 100

            score -= min(risk, 10)

        if score >= 85:
            decision = "BUY"

        elif score >= 70:
            decision = "HOLD"

        else:
            decision = "WAIT"

        result.append({
            "stock_code": p["stock_code"],
            "stock_name": p["stock_name"],
            "ai_score": round(score, 2),
            "decision": decision
        })

    result.sort(
        key=lambda x: x["ai_score"],
        reverse=True
    )

    for idx, item in enumerate(result):
        item["rank"] = idx + 1

    return {
        "found": True,
        "version": "MCP 13.6",
        "count": len(result),
        "items": result,
        "message": "AI 종목 순위 분석 완료"
    }

@router.get("/buy-timing/{stock_code}")
def buy_timing(stock_code: str):

    dash = dashboard()

    positions = dash.get("positions", [])

    target = None

    for p in positions:
        if p["stock_code"] == stock_code:
            target = p
            break

    if not target:
        return {
            "found": False,
            "version": "MCP 13.7",
            "message": "보유 종목을 찾을 수 없습니다."
        }

    buy_price = float(target.get("buy_price", 0))
    target_price = float(target.get("target_price", 0))
    stop_price = float(target.get("stop_price", 0))

    current_price = buy_price

    quote = get_quote(stock_code)

    if quote.get("found"):
        current_price = float(
            quote.get("current_price", buy_price)
        )

    upside = 0
    downside = 0

    if target_price > 0:
        upside = (
            (target_price - current_price)
            / current_price
        ) * 100

    if stop_price > 0:
        downside = (
            (current_price - stop_price)
            / current_price
        ) * 100

    if upside >= 10 and downside <= 5:
        timing = "매수 구간"

    elif upside >= 5:
        timing = "관망"

    else:
        timing = "추격매수 금지"

    return {
        "found": True,
        "version": "MCP 13.7",
        "stock_code": stock_code,
        "stock_name": target["stock_name"],
        "current_price": current_price,
        "target_price": target_price,
        "stop_price": stop_price,
        "upside_percent": round(upside, 2),
        "downside_percent": round(downside, 2),
        "timing": timing,
        "message": "AI 매수 타이밍 분석 완료"
    }
@router.get("/exit-strategy")
def exit_strategy():
    dash = dashboard()
    positions = dash.get("positions", [])

    results = []

    for p in positions:
        stock_code = p["stock_code"]
        stock_name = p["stock_name"]

        buy_price = float(p.get("buy_price", 0))
        target_price = float(p.get("target_price", 0))
        stop_price = float(p.get("stop_price", 0))

        quote = get_quote(stock_code)

        if quote.get("found"):
            current_price = float(quote.get("current_price", buy_price))
        else:
            current_price = buy_price

        profit_rate = 0
        if buy_price > 0:
            profit_rate = round(((current_price - buy_price) / buy_price) * 100, 2)

        target_gap = None
        stop_gap = None

        if target_price > 0:
            target_gap = round(((target_price - current_price) / current_price) * 100, 2)

        if stop_price > 0:
            stop_gap = round(((current_price - stop_price) / current_price) * 100, 2)

        if stop_price > 0 and current_price <= stop_price:
            action = "SELL"
            reason = "손절가 이탈"

        elif target_price > 0 and current_price >= target_price:
            action = "TAKE_PROFIT"
            reason = "목표가 도달"

        elif profit_rate >= 10:
            action = "PARTIAL_TAKE_PROFIT"
            reason = "수익률 10% 이상, 분할 익절 검토"

        elif profit_rate <= -3:
            action = "RISK_CHECK"
            reason = "손실 확대 구간, 리스크 점검 필요"

        else:
            action = "HOLD"
            reason = "목표가/손절가 미도달, 보유 유지"

        results.append({
            "stock_code": stock_code,
            "stock_name": stock_name,
            "buy_price": buy_price,
            "current_price": current_price,
            "target_price": target_price,
            "stop_price": stop_price,
            "profit_rate": profit_rate,
            "target_gap_percent": target_gap,
            "stop_gap_percent": stop_gap,
            "action": action,
            "reason": reason
        })

    sell_count = len([x for x in results if x["action"] == "SELL"])
    take_profit_count = len([x for x in results if x["action"] in ["TAKE_PROFIT", "PARTIAL_TAKE_PROFIT"]])
    hold_count = len([x for x in results if x["action"] == "HOLD"])

    return {
        "found": True,
        "version": "MCP 13.8",
        "count": len(results),
        "sell_count": sell_count,
        "take_profit_count": take_profit_count,
        "hold_count": hold_count,
        "items": results,
        "message": "AI 익절/손절 전략 분석 완료"
    }
@router.get("/final-opinion")
def final_opinion():

    brief = market_brief()
    risk = risk_review()
    committee = investment_committee()
    ranking = ai_ranking()
    exit_review = exit_strategy()

    score = 100

    if risk["risk_level"] == "HIGH":
        score -= 40

    elif risk["risk_level"] == "MEDIUM":
        score -= 20

    if brief["market_status"] == "약세":
        score -= 20

    if committee["decision"] == "WAIT":
        score -= 20

    if ranking["count"] > 0:

        top_score = ranking["items"][0]["ai_score"]

        if top_score < 70:
            score -= 20

        elif top_score < 80:
            score -= 10

    risk_action_count = 0

    for item in exit_review["items"]:

        if item["action"] in [
            "SELL",
            "RISK_CHECK"
        ]:
            risk_action_count += 1

    score -= risk_action_count * 10

    if score >= 90:
        opinion = "강력매수"

    elif score >= 80:
        opinion = "매수"

    elif score >= 60:
        opinion = "보유"

    elif score >= 40:
        opinion = "관망"

    else:
        opinion = "매도"

    return {
        "found": True,
        "version": "MCP 13.9",
        "final_score": score,
        "final_opinion": opinion,
        "market_status": brief["market_status"],
        "risk_level": risk["risk_level"],
        "committee_decision": committee["decision"],
        "top_ai_score": ranking["items"][0]["ai_score"] if ranking["count"] > 0 else 0,
        "risk_actions": risk_action_count,
        "message": "AI 종합 투자 의견 생성 완료"
    }
