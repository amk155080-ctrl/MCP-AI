from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import json

from app.core.database import get_db
from app.services.auction_decision.engine import analyze_auction_decision


router = APIRouter(
    prefix="/api/v17",
    tags=["MCP17 Auction Decision"],
)


def _save_decision_result(
    db: Session,
    decision: dict,
    document_id: int = None,
    auction_id: int = None,
    rights_result_id: int = None,
) -> int:
    saved = db.execute(
        text("""
            INSERT INTO auction_decision_results (
                document_id,
                auction_id,
                rights_result_id,
                version,
                appraisal_price,
                minimum_bid_price,
                expected_sale_price,
                rights_score,
                takeover_amount,
                recommended_bid,
                safe_bid_by_roi,
                safe_bid_by_rights,
                bid_to_appraisal_rate,
                target_roi,
                total_cost,
                expected_profit,
                expected_roi,
                profit_score,
                risk_score,
                auction_score,
                decision,
                confidence,
                summary,
                raw_result
            )
            VALUES (
                :document_id,
                :auction_id,
                :rights_result_id,
                :version,
                :appraisal_price,
                :minimum_bid_price,
                :expected_sale_price,
                :rights_score,
                :takeover_amount,
                :recommended_bid,
                :safe_bid_by_roi,
                :safe_bid_by_rights,
                :bid_to_appraisal_rate,
                :target_roi,
                :total_cost,
                :expected_profit,
                :expected_roi,
                :profit_score,
                :risk_score,
                :auction_score,
                :decision,
                :confidence,
                :summary,
                :raw_result
            )
            RETURNING id
        """),
        {
            "document_id": document_id,
            "auction_id": auction_id,
            "rights_result_id": rights_result_id,
            "version": decision.get("version"),
            "appraisal_price": decision.get("appraisal_price"),
            "minimum_bid_price": decision.get("minimum_bid_price"),
            "expected_sale_price": decision.get("expected_sale_price"),
            "rights_score": decision.get("rights_score"),
            "takeover_amount": decision.get("takeover_amount"),
            "recommended_bid": decision.get("recommended_bid"),
            "safe_bid_by_roi": decision.get("safe_bid_by_roi"),
            "safe_bid_by_rights": decision.get("safe_bid_by_rights"),
            "bid_to_appraisal_rate": decision.get("bid_to_appraisal_rate"),
            "target_roi": decision.get("target_roi"),
            "total_cost": decision.get("total_cost"),
            "expected_profit": decision.get("expected_profit"),
            "expected_roi": decision.get("expected_roi"),
            "profit_score": decision.get("profit_score"),
            "risk_score": decision.get("risk_score"),
            "auction_score": decision.get("auction_score"),
            "decision": decision.get("decision"),
            "confidence": decision.get("confidence"),
            "summary": decision.get("summary"),
            "raw_result": json.dumps(decision, ensure_ascii=False),
        },
    )

    saved_id = saved.scalar()
    db.commit()
    return saved_id


@router.get("/decision")
def auction_decision(
    appraisal_price: int,
    minimum_bid_price: int,
    expected_sale_price: int,
    rights_score: int,
    repair_cost: int = 0,
    eviction_cost: int = 0,
    tax_cost: int = 0,
    etc_cost: int = 0,
    takeover_amount: int = 0,
):
    result = analyze_auction_decision(
        appraisal_price=appraisal_price,
        minimum_bid_price=minimum_bid_price,
        expected_sale_price=expected_sale_price,
        rights_score=rights_score,
        repair_cost=repair_cost,
        eviction_cost=eviction_cost,
        tax_cost=tax_cost,
        etc_cost=etc_cost,
        takeover_amount=takeover_amount,
    )

    return {
        "found": True,
        "version": "MCP 17.2",
        "decision": result,
        "message": "경매 종합 판정 완료",
    }


@router.get("/decision/save")
def auction_decision_save(
    appraisal_price: int,
    minimum_bid_price: int,
    expected_sale_price: int,
    rights_score: int,
    repair_cost: int = 0,
    eviction_cost: int = 0,
    tax_cost: int = 0,
    etc_cost: int = 0,
    takeover_amount: int = 0,
    db: Session = Depends(get_db),
):
    result = analyze_auction_decision(
        appraisal_price=appraisal_price,
        minimum_bid_price=minimum_bid_price,
        expected_sale_price=expected_sale_price,
        rights_score=rights_score,
        repair_cost=repair_cost,
        eviction_cost=eviction_cost,
        tax_cost=tax_cost,
        etc_cost=etc_cost,
        takeover_amount=takeover_amount,
    )

    saved_id = _save_decision_result(
        db=db,
        decision=result,
    )

    return {
        "found": True,
        "version": "MCP 17.2",
        "saved": True,
        "decision_result_id": saved_id,
        "decision": result,
        "message": "경매 종합 판정 및 저장 완료",
    }


@router.get("/decision/by-document/{document_id}")
def auction_decision_by_document(
    document_id: int,
    appraisal_price: int = 300_000_000,
    minimum_bid_price: int = 210_000_000,
    expected_sale_price: int = 320_000_000,
    repair_cost: int = 10_000_000,
    eviction_cost: int = 5_000_000,
    tax_cost: int = 8_000_000,
    etc_cost: int = 3_000_000,
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
            "version": "MCP 17.2",
            "document_id": document_id,
            "message": "MCP16 권리분석 결과가 없습니다. 먼저 /api/v16/rights-v2/analyze/{document_id}를 실행하세요.",
        }

    rights_score = rights_row.get("rights_score") or 0
    takeover_amount = rights_row.get("takeover_amount") or 0

    result = analyze_auction_decision(
        appraisal_price=appraisal_price,
        minimum_bid_price=minimum_bid_price,
        expected_sale_price=expected_sale_price,
        rights_score=rights_score,
        takeover_amount=takeover_amount,
        repair_cost=repair_cost,
        eviction_cost=eviction_cost,
        tax_cost=tax_cost,
        etc_cost=etc_cost,
    )

    return {
        "found": True,
        "version": "MCP 17.2",
        "document_id": document_id,
        "auction_id": rights_row.get("auction_id"),
        "rights_result_id": rights_row.get("id"),
        "rights_summary": {
            "rights_score": rights_score,
            "risk_level": rights_row.get("risk_level"),
            "recommendation": rights_row.get("recommendation"),
            "summary": rights_row.get("summary"),
        },
        "decision": result,
        "message": "MCP16 권리분석 결과 기반 경매 종합 판정 완료",
    }


@router.get("/decision/by-document/{document_id}/save")
def auction_decision_by_document_save(
    document_id: int,
    appraisal_price: int = 300_000_000,
    minimum_bid_price: int = 210_000_000,
    expected_sale_price: int = 320_000_000,
    repair_cost: int = 10_000_000,
    eviction_cost: int = 5_000_000,
    tax_cost: int = 8_000_000,
    etc_cost: int = 3_000_000,
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
            "version": "MCP 17.2",
            "document_id": document_id,
            "message": "MCP16 권리분석 결과가 없습니다. 먼저 /api/v16/rights-v2/analyze/{document_id}를 실행하세요.",
        }

    rights_score = rights_row.get("rights_score") or 0
    takeover_amount = rights_row.get("takeover_amount") or 0

    result = analyze_auction_decision(
        appraisal_price=appraisal_price,
        minimum_bid_price=minimum_bid_price,
        expected_sale_price=expected_sale_price,
        rights_score=rights_score,
        takeover_amount=takeover_amount,
        repair_cost=repair_cost,
        eviction_cost=eviction_cost,
        tax_cost=tax_cost,
        etc_cost=etc_cost,
    )

    saved_id = _save_decision_result(
        db=db,
        decision=result,
        document_id=document_id,
        auction_id=rights_row.get("auction_id"),
        rights_result_id=rights_row.get("id"),
    )

    return {
        "found": True,
        "version": "MCP 17.2",
        "document_id": document_id,
        "auction_id": rights_row.get("auction_id"),
        "rights_result_id": rights_row.get("id"),
        "saved": True,
        "decision_result_id": saved_id,
        "decision": result,
        "message": "MCP16 권리분석 기반 경매 종합 판정 및 저장 완료",
    }
