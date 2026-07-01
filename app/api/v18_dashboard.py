from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db


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
