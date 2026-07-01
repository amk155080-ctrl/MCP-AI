from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from fastapi.responses import HTMLResponse


router = APIRouter(
    prefix="/api/v18",
    tags=["MCP18 Auction Dashboard"],
)


def _make_dashboard_summary(
    rights_row: dict,
    decision_row: dict,
) -> str:
    decision = decision_row.get("decision")
    auction_score = decision_row.get("auction_score")
    rights_score = rights_row.get("rights_score")
    expected_profit = decision_row.get("expected_profit")
    expected_roi = decision_row.get("expected_roi")
    recommended_bid = decision_row.get("recommended_bid")

    return (
        f"권리점수는 {rights_score}점이며, "
        f"경매 종합점수는 {auction_score}점입니다. "
        f"추천 입찰가는 {recommended_bid:,}원이고, "
        f"예상 수익은 {expected_profit:,}원, "
        f"예상 수익률은 {expected_roi}%입니다. "
        f"최종 판단은 {decision}입니다."
    )

def _build_dashboard_html(data: dict) -> str:

    rights = data["rights"]
    decision = data["decision"]

    return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>MCP18 Auction Dashboard</title>

<style>

body {{
    font-family: Arial, sans-serif;
    margin:40px;
    background:#f5f5f5;
}}

.container {{
    background:white;
    padding:30px;
    border-radius:10px;
}}

h1 {{
    color:#2c3e50;
}}

.card {{
    margin-top:20px;
    padding:20px;
    border:1px solid #ddd;
    border-radius:8px;
}}

.score {{
    font-size:34px;
    color:#1976d2;
    font-weight:bold;
}}

.summary {{
    background:#fafafa;
    padding:15px;
    line-height:1.7;
}}

table {{
    width:100%;
    border-collapse:collapse;
}}

td {{
    padding:8px;
    border-bottom:1px solid #eee;
}}

</style>

</head>

<body>

<div class="container">

<h1>MCP18 통합 경매 Dashboard</h1>

<div class="card">

<h2>권리분석</h2>

<table>

<tr><td>권리점수</td><td>{rights["rights_score"]}</td></tr>
<tr><td>위험등급</td><td>{rights["risk_level"]}</td></tr>
<tr><td>추천</td><td>{rights["recommendation"]}</td></tr>
<tr><td>말소기준권리</td><td>{rights["base_right"]}</td></tr>
<tr><td>임차인</td><td>{rights["tenant_priority"]}</td></tr>
<tr><td>점유</td><td>{rights["occupancy"]}</td></tr>

</table>

</div>

<div class="card">

<h2>경매 종합판정</h2>

<div class="score">
{decision["auction_score"]} 점
</div>

<table>

<tr><td>최종판단</td><td>{decision["decision"]}</td></tr>

<tr><td>추천입찰가</td><td>{decision["recommended_bid"]:,} 원</td></tr>

<tr><td>예상수익</td><td>{decision["expected_profit"]:,} 원</td></tr>

<tr><td>예상수익률</td><td>{decision["expected_roi"]}%</td></tr>

<tr><td>신뢰도</td><td>{decision["confidence"]}</td></tr>

</table>

</div>

<div class="card summary">

<h2>AI 종합 의견</h2>

<p>{data["summary"]}</p>

</div>

</div>

</body>
</html>
"""

def _build_bid_checklist(data: dict) -> list:
    rights = data["rights"]
    decision = data["decision"]

    checklist = []

    checklist.append({
        "category": "권리분석",
        "item": "말소기준권리 확인",
        "status": "PASS" if rights["base_right"] != "말소기준권리 없음" else "CHECK",
        "comment": rights["base_right"],
    })

    checklist.append({
        "category": "권리분석",
        "item": "임차인 권리 확인",
        "status": "PASS" if rights["tenant_priority"] == "임차인 없음" else "CHECK",
        "comment": rights["tenant_priority"],
    })

    checklist.append({
        "category": "점유/명도",
        "item": "점유상태 확인",
        "status": "PASS" if rights["occupancy"] in ["소유자 점유", "임차인 없음"] else "CHECK",
        "comment": rights["occupancy"],
    })

    checklist.append({
        "category": "인수위험",
        "item": "인수금액 확인",
        "status": "PASS" if (rights["takeover_amount"] or 0) == 0 else "RISK",
        "comment": f'{rights["takeover_amount"] or 0:,}원',
    })

    checklist.append({
        "category": "수익성",
        "item": "예상 수익률 확인",
        "status": "PASS" if decision["expected_roi"] >= 15 else "CHECK",
        "comment": f'{decision["expected_roi"]}%',
    })

    checklist.append({
        "category": "수익성",
        "item": "예상 수익 확인",
        "status": "PASS" if decision["expected_profit"] > 0 else "RISK",
        "comment": f'{decision["expected_profit"]:,}원',
    })

    checklist.append({
        "category": "입찰가",
        "item": "추천 입찰가 확인",
        "status": "PASS" if decision["recommended_bid"] > 0 else "CHECK",
        "comment": f'{decision["recommended_bid"]:,}원',
    })

    checklist.append({
        "category": "최종판단",
        "item": "AI 최종 판단 확인",
        "status": "PASS" if decision["decision"] == "BID" else "CHECK",
        "comment": decision["decision"],
    })

    return checklist
def _build_final_ai_comment(data: dict, checklist: list) -> dict:
    rights = data["rights"]
    decision = data["decision"]

    risk_items = [item for item in checklist if item["status"] == "RISK"]
    check_items = [item for item in checklist if item["status"] == "CHECK"]

    final_decision = decision["decision"]
    rights_score = rights["rights_score"]
    auction_score = decision["auction_score"]
    expected_roi = decision["expected_roi"]
    expected_profit = decision["expected_profit"]
    recommended_bid = decision["recommended_bid"]

    if final_decision == "BID":
        headline = "입찰 검토 가능"
        comment = (
            "권리와 수익성 조건이 비교적 양호합니다. "
            "다만 실제 입찰 전 현장 점유상태, 추가 권리관계, 시세를 다시 확인해야 합니다."
        )
    elif final_decision == "CAUTION_BID":
        headline = "주의 입찰"
        comment = (
            "수익성은 있으나 일부 위험요소가 존재합니다. "
            "추천 입찰가 이하에서만 보수적으로 접근하는 것이 좋습니다."
        )
    else:
        headline = "입찰 보류"
        comment = (
            "현재 분석 기준으로는 입찰을 보류하는 것이 안전합니다. "
            "특히 권리점수, 점유상태, 임차인 권리관계 확인이 필요합니다."
        )

    if risk_items:
        risk_summary = "위험 항목이 있어 추가 확인이 필요합니다."
    elif check_items:
        risk_summary = "즉시 위험은 아니지만 확인이 필요한 항목이 있습니다."
    else:
        risk_summary = "체크리스트 기준 주요 위험 항목은 낮은 편입니다."

    return {
        "headline": headline,
        "final_decision": final_decision,
        "auction_score": auction_score,
        "rights_score": rights_score,
        "expected_roi": expected_roi,
        "expected_profit": expected_profit,
        "recommended_bid": recommended_bid,
        "risk_summary": risk_summary,
        "risk_count": len(risk_items),
        "check_count": len(check_items),
        "comment": comment,
        "action": {
            "should_bid": final_decision == "BID",
            "max_bid_price": recommended_bid,
            "required_checks": [
                item for item in checklist
                if item["status"] in ["CHECK", "RISK"]
            ],
        },
    }

@router.get("/dashboard/{document_id}")
def auction_dashboard(
    document_id: int,
    db: Session = Depends(get_db),
):
    rights_row = db.execute(
        text("""
            SELECT *
            FROM rights_v2_results
            WHERE document_id = :document_id
            ORDER BY created_at DESC, id DESC
            LIMIT 1
        """),
        {"document_id": document_id},
    ).mappings().first()

    if not rights_row:
        return {
            "found": False,
            "version": "MCP 18.1",
            "document_id": document_id,
            "message": "MCP16 권리분석 결과가 없습니다.",
        }

    decision_row = db.execute(
        text("""
            SELECT *
            FROM auction_decision_results
            WHERE document_id = :document_id
            ORDER BY created_at DESC, id DESC
            LIMIT 1
        """),
        {"document_id": document_id},
    ).mappings().first()

    if not decision_row:
        return {
            "found": False,
            "version": "MCP 18.1",
            "document_id": document_id,
            "message": "MCP17 경매 종합 판정 결과가 없습니다.",
        }

    rights = dict(rights_row)
    decision = dict(decision_row)

    return {
        "found": True,
        "version": "MCP 18.1",
        "document_id": document_id,
        "auction_id": decision.get("auction_id") or rights.get("auction_id"),
        "rights": {
            "result_id": rights.get("id"),
            "rights_score": rights.get("rights_score"),
            "risk_level": rights.get("risk_level"),
            "recommendation": rights.get("recommendation"),
            "base_right": rights.get("base_right"),
            "tenant_priority": rights.get("tenant_priority"),
            "occupancy": rights.get("occupancy"),
            "takeover_amount": rights.get("takeover_amount"),
            "summary": rights.get("summary"),
            "created_at": rights.get("created_at"),
        },
        "decision": {
            "result_id": decision.get("id"),
            "auction_score": decision.get("auction_score"),
            "profit_score": decision.get("profit_score"),
            "risk_score": decision.get("risk_score"),
            "confidence": decision.get("confidence"),
            "decision": decision.get("decision"),
            "recommended_bid": decision.get("recommended_bid"),
            "expected_profit": decision.get("expected_profit"),
            "expected_roi": decision.get("expected_roi"),
            "total_cost": decision.get("total_cost"),
            "summary": decision.get("summary"),
            "created_at": decision.get("created_at"),
        },
        "summary": _make_dashboard_summary(
            rights_row=rights,
            decision_row=decision,
        ),
        "message": "MCP18 통합 대시보드 조회 완료",
    }

@router.get(
    "/dashboard/html/{document_id}",
    response_class=HTMLResponse,
)
def dashboard_html(
    document_id: int,
    db: Session = Depends(get_db),
):

    response = auction_dashboard(
        document_id=document_id,
        db=db,
    )

    if not response["found"]:
        return HTMLResponse(
            "<h1>Dashboard Not Found</h1>",
            status_code=404,
        )

    html = _build_dashboard_html(response)

    return HTMLResponse(html)

@router.get("/dashboard/checklist/{document_id}")
def dashboard_checklist(
    document_id: int,
    db: Session = Depends(get_db),
):
    response = auction_dashboard(
        document_id=document_id,
        db=db,
    )

    if not response["found"]:
        return response

    checklist = _build_bid_checklist(response)

    risk_count = len([
        item for item in checklist
        if item["status"] == "RISK"
    ])

    check_count = len([
        item for item in checklist
        if item["status"] == "CHECK"
    ])

    pass_count = len([
        item for item in checklist
        if item["status"] == "PASS"
    ])

    return {
        "found": True,
        "version": "MCP 18.3",
        "document_id": document_id,
        "auction_id": response.get("auction_id"),
        "pass_count": pass_count,
        "check_count": check_count,
        "risk_count": risk_count,
        "items": checklist,
        "message": "입찰 전 체크리스트 생성 완료",
    }
@router.get("/dashboard/final-comment/{document_id}")
def dashboard_final_comment(
    document_id: int,
    db: Session = Depends(get_db),
):
    response = auction_dashboard(
        document_id=document_id,
        db=db,
    )

    if not response["found"]:
        return response

    checklist = _build_bid_checklist(response)
    final_comment = _build_final_ai_comment(
        data=response,
        checklist=checklist,
    )

    return {
        "found": True,
        "version": "MCP 18.4",
        "document_id": document_id,
        "auction_id": response.get("auction_id"),
        "final_comment": final_comment,
        "message": "최종 AI 코멘트 생성 완료",
    }
