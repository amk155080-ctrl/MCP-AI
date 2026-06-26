from fastapi import APIRouter, Query
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(
    prefix="/api/v5/advisor",
    tags=["advisor-v5"]
)


def build_judgement(score, risk, smart):
    reasons = []

    signal = "HOLD"
    action = "관망"
    confidence = 50

    if smart >= 10000000000:
        reasons.append("스마트머니 강한 순유입")
        confidence += 15
    elif smart > 0:
        reasons.append("기관/외국인 순매수")
        confidence += 8
    elif smart < 0:
        reasons.append("기관/외국인 순매도")
        confidence -= 15

    if score >= 80:
        reasons.append("종합점수 매우 우수")
        confidence += 20
    elif score >= 70:
        reasons.append("종합점수 우수")
        confidence += 12
    elif score >= 65:
        reasons.append("종합점수 양호")
        confidence += 8
    elif score < 55:
        reasons.append("종합점수 부진")
        confidence -= 15

    if risk >= 70:
        reasons.append("리스크 양호")
        confidence += 8
    elif risk < 60:
        reasons.append("변동성 주의")
        confidence -= 8

    # V5.1 판단 로직
    if score >= 80 and smart > 0 and risk >= 65:
        signal = "STRONG_BUY"
        action = "적극 매수관심"

    elif score >= 70 and smart > 0:
        signal = "BUY"
        action = "매수관심"

    elif score >= 65 and smart >= 10000000000 and risk >= 70:
        signal = "BUY"
        action = "스마트머니 기반 매수관심"

    elif score < 45 and smart < 0:
        signal = "STRONG_SELL"
        action = "강한 비중축소"

    elif score < 55 and smart < 0:
        signal = "SELL"
        action = "비중축소"

    elif smart > 0 and score >= 60:
        signal = "WATCH"
        action = "관심관찰"

    confidence = max(0, min(100, confidence))

    return signal, action, confidence, reasons


@router.get("/check")
def advisor_check(
    stock_code: str = Query(..., description="종목코드")
):
    db = SessionLocal()

    try:
        row = db.execute(text("""
            SELECT
                s.trade_date,
                s.stock_code,
                s.stock_name,

                s.total_score,
                s.risk_score,
                s.grade,

                p.close_price,
                p.change_rate,

                COALESCE(f.foreign_net,0) AS foreign_net,
                COALESCE(f.institution_net,0) AS institution_net,
                COALESCE(f.pension_net,0) AS pension_net,
                COALESCE(f.program_net,0) AS program_net,

                (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
                ) AS smart_money_net

            FROM mcp4.stock_score_daily s

            LEFT JOIN mcp4.stock_price_daily p
              ON s.trade_date = p.trade_date
             AND s.stock_code = p.stock_code

            LEFT JOIN mcp4.investor_flow_daily f
              ON s.trade_date = f.trade_date
             AND s.stock_code = f.stock_code

            WHERE s.stock_code = :stock_code
            ORDER BY s.trade_date DESC
            LIMIT 1
        """), {
            "stock_code": stock_code
        }).mappings().first()

        if not row:
            return {
                "found": False,
                "message": "종목을 찾을 수 없습니다."
            }

        score = float(row["total_score"] or 0)
        risk = float(row["risk_score"] or 0)
        smart = float(row["smart_money_net"] or 0)

        signal, action, confidence, reasons = build_judgement(
            score,
            risk,
            smart,
        )

        return {
            "found": True,
            "trade_date": row["trade_date"],
            "stock_code": row["stock_code"],
            "stock_name": row["stock_name"],

            "close_price": float(row["close_price"] or 0),
            "change_rate": float(row["change_rate"] or 0),

            "total_score": score,
            "risk_score": risk,
            "grade": row["grade"],

            "foreign_net": float(row["foreign_net"]),
            "institution_net": float(row["institution_net"]),
            "pension_net": float(row["pension_net"]),
            "smart_money_net": smart,

            "signal": signal,
            "action": action,
            "confidence": confidence,
            "reasons": reasons,
        }

    finally:
        db.close()


@router.get("/ask")
def advisor_ask(
    stock_code: str = Query(..., description="종목코드")
):
    db = SessionLocal()

    try:
        row = db.execute(text("""
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

            LEFT JOIN mcp4.stock_price_daily p
              ON s.trade_date = p.trade_date
             AND s.stock_code = p.stock_code

            LEFT JOIN mcp4.investor_flow_daily f
              ON s.trade_date = f.trade_date
             AND s.stock_code = f.stock_code

            WHERE s.stock_code = :stock_code
            ORDER BY s.trade_date DESC
            LIMIT 1
        """), {
            "stock_code": stock_code
        }).mappings().first()

        if not row:
            return {
                "found": False,
                "message": "해당 종목 데이터를 찾을 수 없습니다."
            }

        score = float(row["total_score"] or 0)
        risk = float(row["risk_score"] or 0)
        smart = float(row["smart_money_net"] or 0)

        signal, action, confidence, reasons = build_judgement(
            score,
            risk,
            smart,
        )

        stock_name = row["stock_name"]
        close_price = float(row["close_price"] or 0)
        change_rate = float(row["change_rate"] or 0)
        foreign_net = float(row["foreign_net"] or 0)
        institution_net = float(row["institution_net"] or 0)
        pension_net = float(row["pension_net"] or 0)

        if signal in ["BUY", "STRONG_BUY"]:
            final_comment = (
                f"{stock_name}은 현재 {signal} 의견입니다. "
                f"스마트머니 유입과 리스크 조건이 양호해 매수 관심 종목으로 볼 수 있습니다."
            )
        elif signal in ["SELL", "STRONG_SELL"]:
            final_comment = (
                f"{stock_name}은 현재 {signal} 의견입니다. "
                f"외국인·기관 수급이 약하고 점수도 낮아 비중 축소를 검토할 구간입니다."
            )
        elif signal == "WATCH":
            final_comment = (
                f"{stock_name}은 현재 WATCH 구간입니다. "
                f"수급은 나쁘지 않지만 추가 점수 개선을 확인하는 것이 좋습니다."
            )
        else:
            final_comment = (
                f"{stock_name}은 현재 HOLD 의견입니다. "
                f"뚜렷한 매수 또는 매도 신호가 강하지 않아 관망이 적절합니다."
            )

        return {
            "found": True,
            "stock_code": row["stock_code"],
            "stock_name": stock_name,
            "trade_date": row["trade_date"],
            "answer": final_comment,
            "signal": signal,
            "action": action,
            "confidence": confidence,
            "summary": {
                "close_price": close_price,
                "change_rate": change_rate,
                "total_score": score,
                "risk_score": risk,
                "grade": row["grade"],
                "smart_money_net": smart,
            },
            "flow": {
                "foreign_net": foreign_net,
                "institution_net": institution_net,
                "pension_net": pension_net,
            },
            "reasons": reasons,
        }

    finally:
        db.close()


@router.get("/price_plan")
def advisor_price_plan(
    stock_code: str = Query(..., description="종목코드")
):
    db = SessionLocal()

    try:
        row = db.execute(text("""
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

            LEFT JOIN mcp4.stock_price_daily p
              ON s.trade_date = p.trade_date
             AND s.stock_code = p.stock_code

            LEFT JOIN mcp4.investor_flow_daily f
              ON s.trade_date = f.trade_date
             AND s.stock_code = f.stock_code

            WHERE s.stock_code = :stock_code
            ORDER BY s.trade_date DESC
            LIMIT 1
        """), {
            "stock_code": stock_code
        }).mappings().first()

        if not row:
            return {
                "found": False,
                "message": "종목 데이터를 찾을 수 없습니다."
            }

        current_price = float(row["close_price"] or 0)
        score = float(row["total_score"] or 0)
        risk = float(row["risk_score"] or 0)
        smart = float(row["smart_money_net"] or 0)

        signal, action, confidence, reasons = build_judgement(
            score,
            risk,
            smart,
        )

        # 기대 상승률 산정
        if signal == "STRONG_BUY":
            upside_pct = 20.0
            stop_pct = -8.0
        elif signal == "BUY":
            upside_pct = 15.0
            stop_pct = -7.0
        elif signal == "WATCH":
            upside_pct = 8.0
            stop_pct = -6.0
        elif signal == "SELL":
            upside_pct = 3.0
            stop_pct = -5.0
        elif signal == "STRONG_SELL":
            upside_pct = 0.0
            stop_pct = -4.0
        else:
            upside_pct = 5.0
            stop_pct = -5.0

        # 스마트머니 강도 보정
        if smart >= 30000000000 and signal in ["BUY", "STRONG_BUY"]:
            upside_pct += 3.0

        if risk < 60:
            stop_pct += 2.0

        target_price = round(current_price * (1 + upside_pct / 100), 0)
        stop_loss = round(current_price * (1 + stop_pct / 100), 0)

        return {
            "found": True,
            "trade_date": row["trade_date"],
            "stock_code": row["stock_code"],
            "stock_name": row["stock_name"],

            "current_price": current_price,
            "target_price": target_price,
            "stop_loss": stop_loss,

            "expected_upside_percent": upside_pct,
            "risk_downside_percent": stop_pct,

            "total_score": score,
            "risk_score": risk,
            "grade": row["grade"],
            "smart_money_net": smart,

            "signal": signal,
            "action": action,
            "confidence": confidence,
            "reasons": reasons,
        }

    finally:
        db.close()


@router.get("/report")
def advisor_report(
    stock_code: str = Query(..., description="종목코드")
):
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

                COALESCE(f.foreign_net,0) AS foreign_net,
                COALESCE(f.institution_net,0) AS institution_net,
                COALESCE(f.pension_net,0) AS pension_net,
                COALESCE(f.program_net,0) AS program_net,

                COALESCE(d.financial_investment_net,0) AS financial_investment_net,
                COALESCE(d.trust_net,0) AS trust_net,
                COALESCE(d.insurance_net,0) AS insurance_net,
                COALESCE(d.private_fund_net,0) AS private_fund_net,
                COALESCE(d.bank_net,0) AS bank_net,

                (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
                ) AS smart_money_net,

                (
                    COALESCE(d.foreign_net,0)
                  + COALESCE(d.financial_investment_net,0)
                  + COALESCE(d.trust_net,0)
                  + COALESCE(d.pension_net,0)
                ) AS smart_money_core

            FROM mcp4.stock_score_daily s

            LEFT JOIN mcp4.stock_price_daily p
              ON s.trade_date = p.trade_date
             AND s.stock_code = p.stock_code

            LEFT JOIN mcp4.investor_flow_daily f
              ON s.trade_date = f.trade_date
             AND s.stock_code = f.stock_code

            LEFT JOIN mcp4.investor_flow_detail_daily d
              ON s.trade_date = d.trade_date
             AND s.stock_code = d.stock_code

            WHERE s.stock_code = :stock_code
            ORDER BY s.trade_date DESC
            LIMIT 1
        """), {
            "stock_code": stock_code
        }).mappings().first()

        if not row:
            return {
                "found": False,
                "stock_code": stock_code,
                "message": "종합 리포트 데이터를 찾을 수 없습니다."
            }

        score = float(row["total_score"] or 0)
        risk = float(row["risk_score"] or 0)
        smart = float(row["smart_money_net"] or 0)
        current_price = float(row["close_price"] or 0)

        signal, action, confidence, reasons = build_judgement(
            score,
            risk,
            smart,
        )

        if signal == "STRONG_BUY":
            upside_pct = 20.0
            stop_pct = -8.0
        elif signal == "BUY":
            upside_pct = 15.0
            stop_pct = -7.0
        elif signal == "WATCH":
            upside_pct = 8.0
            stop_pct = -6.0
        elif signal == "SELL":
            upside_pct = 3.0
            stop_pct = -5.0
        elif signal == "STRONG_SELL":
            upside_pct = 0.0
            stop_pct = -4.0
        else:
            upside_pct = 5.0
            stop_pct = -5.0

        if smart >= 30000000000 and signal in ["BUY", "STRONG_BUY"]:
            upside_pct += 3.0

        if risk < 60:
            stop_pct += 2.0

        target_price = round(current_price * (1 + upside_pct / 100), 0)
        stop_loss = round(current_price * (1 + stop_pct / 100), 0)

        stock_name = row["stock_name"]

        if signal in ["BUY", "STRONG_BUY"]:
            final_opinion = (
                f"{stock_name}은 현재 {signal} 의견입니다. "
                f"스마트머니 수급과 리스크 조건이 양호해 매수 관심 종목으로 볼 수 있습니다."
            )
        elif signal in ["SELL", "STRONG_SELL"]:
            final_opinion = (
                f"{stock_name}은 현재 {signal} 의견입니다. "
                f"외국인·기관 수급이 약하고 종합점수도 낮아 비중 축소 검토가 필요합니다."
            )
        elif signal == "WATCH":
            final_opinion = (
                f"{stock_name}은 현재 WATCH 구간입니다. "
                f"추가 수급 유입과 점수 개선 여부를 확인하는 것이 좋습니다."
            )
        else:
            final_opinion = (
                f"{stock_name}은 현재 HOLD 의견입니다. "
                f"뚜렷한 매수·매도 신호가 강하지 않아 관망이 적절합니다."
            )

        return {
            "found": True,
            "report_type": "MCP5_ADVISOR_FULL_REPORT",

            "basic": {
                "trade_date": row["trade_date"],
                "stock_code": row["stock_code"],
                "stock_name": stock_name,
                "close_price": current_price,
                "change_rate": float(row["change_rate"] or 0),
                "trade_value": float(row["trade_value"] or 0),
                "market_cap": float(row["market_cap"] or 0),
            },

            "scores": {
                "supply_score": float(row["supply_score"] or 0),
                "momentum_score": float(row["momentum_score"] or 0),
                "macro_score": float(row["macro_score"] or 0),
                "semiconductor_score": float(row["semiconductor_score"] or 0),
                "risk_score": risk,
                "total_score": score,
                "grade": row["grade"],
            },

            "flow": {
                "foreign_net": float(row["foreign_net"] or 0),
                "institution_net": float(row["institution_net"] or 0),
                "pension_net": float(row["pension_net"] or 0),
                "program_net": float(row["program_net"] or 0),
                "smart_money_net": smart,
            },

            "flow_detail": {
                "financial_investment_net": float(row["financial_investment_net"] or 0),
                "trust_net": float(row["trust_net"] or 0),
                "insurance_net": float(row["insurance_net"] or 0),
                "private_fund_net": float(row["private_fund_net"] or 0),
                "bank_net": float(row["bank_net"] or 0),
                "smart_money_core": float(row["smart_money_core"] or 0),
            },

            "advisor": {
                "signal": signal,
                "action": action,
                "confidence": confidence,
                "reasons": reasons,
                "final_opinion": final_opinion,
            },

            "price_plan": {
                "current_price": current_price,
                "target_price": target_price,
                "stop_loss": stop_loss,
                "expected_upside_percent": upside_pct,
                "risk_downside_percent": stop_pct,
            }
        }

    finally:
        db.close()


@router.get("/reports/top")
def advisor_reports_top(
    limit: int = Query(20, ge=1, le=100, description="조회 개수")
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
              AND s.total_score >= 65
              AND (
                    COALESCE(f.foreign_net,0)
                  + COALESCE(f.institution_net,0)
                  + COALESCE(f.pension_net,0)
              ) > 0
              AND COALESCE(p.trade_value,0) >= 10000000000
              AND COALESCE(p.market_cap,0) >= 100000000000

            ORDER BY
                s.total_score DESC,
                smart_money_net DESC

            LIMIT :limit
        """), {
            "limit": limit
        }).mappings().all()

        reports = []

        for idx, row in enumerate(rows, start=1):
            score = float(row["total_score"] or 0)
            risk = float(row["risk_score"] or 0)
            smart = float(row["smart_money_net"] or 0)
            current_price = float(row["close_price"] or 0)

            signal, action, confidence, reasons = build_judgement(
                score,
                risk,
                smart,
            )

            if signal == "STRONG_BUY":
                upside_pct = 20.0
                stop_pct = -8.0
            elif signal == "BUY":
                upside_pct = 15.0
                stop_pct = -7.0
            elif signal == "WATCH":
                upside_pct = 8.0
                stop_pct = -6.0
            elif signal == "SELL":
                upside_pct = 3.0
                stop_pct = -5.0
            elif signal == "STRONG_SELL":
                upside_pct = 0.0
                stop_pct = -4.0
            else:
                upside_pct = 5.0
                stop_pct = -5.0

            if smart >= 30000000000 and signal in ["BUY", "STRONG_BUY"]:
                upside_pct += 3.0

            target_price = round(current_price * (1 + upside_pct / 100), 0)
            stop_loss = round(current_price * (1 + stop_pct / 100), 0)

            reports.append({
                "rank": idx,
                "trade_date": row["trade_date"],
                "stock_code": row["stock_code"],
                "stock_name": row["stock_name"],
                "signal": signal,
                "action": action,
                "confidence": confidence,
                "reasons": reasons,
                "total_score": score,
                "risk_score": risk,
                "grade": row["grade"],
                "close_price": current_price,
                "change_rate": float(row["change_rate"] or 0),
                "trade_value": float(row["trade_value"] or 0),
                "market_cap": float(row["market_cap"] or 0),
                "foreign_net": float(row["foreign_net"] or 0),
                "institution_net": float(row["institution_net"] or 0),
                "pension_net": float(row["pension_net"] or 0),
                "smart_money_net": smart,
                "target_price": target_price,
                "stop_loss": stop_loss,
                "expected_upside_percent": upside_pct,
                "risk_downside_percent": stop_pct,
            })

        return {
            "found": True,
            "report_type": "MCP5_ADVISOR_TOP_REPORTS",
            "count": len(reports),
            "items": reports,
        }

    finally:
        db.close()
