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

@router.get("/decision/results")
def list_decision_results(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    rows = db.execute(
        text("""
            SELECT
                id,
                document_id,
                auction_id,
                rights_result_id,
                appraisal_price,
                minimum_bid_price,
                expected_sale_price,
                rights_score,
                recommended_bid,
                expected_profit,
                expected_roi,
                profit_score,
                risk_score,
                auction_score,
                decision,
                confidence,
                created_at
            FROM auction_decision_results
            ORDER BY created_at DESC, id DESC
            LIMIT :limit
        """),
        {"limit": limit},
    ).mappings().all()

    return {
        "found": True,
        "version": "MCP 17.3",
        "count": len(rows),
        "items": [dict(row) for row in rows],
        "message": "경매 종합 판정 결과 목록 조회 완료",
    }

def _build_decision_report(row: dict) -> dict:
    decision = row.get("decision")
    auction_score = row.get("auction_score")
    expected_roi = row.get("expected_roi")
    expected_profit = row.get("expected_profit")

    if decision == "BID":
        headline = "수익성과 위험 조건이 양호하여 입찰 검토가 가능합니다."
    elif decision == "CAUTION_BID":
        headline = "수익성은 있으나 일부 위험요소가 있어 보수적 입찰이 필요합니다."
    else:
        headline = "현재 조건에서는 입찰을 보류하는 것이 안전합니다."

    return {
        "title": "MCP17 경매 종합 판정 리포트",
        "headline": headline,
        "result_id": row.get("id"),
        "document_id": row.get("document_id"),
        "auction_id": row.get("auction_id"),
        "rights_result_id": row.get("rights_result_id"),
        "scores": {
            "auction_score": auction_score,
            "rights_score": row.get("rights_score"),
            "profit_score": row.get("profit_score"),
            "risk_score": row.get("risk_score"),
            "confidence": row.get("confidence"),
        },
        "price": {
            "appraisal_price": row.get("appraisal_price"),
            "minimum_bid_price": row.get("minimum_bid_price"),
            "expected_sale_price": row.get("expected_sale_price"),
            "recommended_bid": row.get("recommended_bid"),
            "bid_to_appraisal_rate": row.get("bid_to_appraisal_rate"),
        },
        "profit": {
            "total_cost": row.get("total_cost"),
            "expected_profit": expected_profit,
            "expected_roi": expected_roi,
            "target_roi": row.get("target_roi"),
        },
        "risk": {
            "takeover_amount": row.get("takeover_amount"),
            "risk_score": row.get("risk_score"),
        },
        "decision": decision,
        "summary": row.get("summary"),
        "created_at": row.get("created_at"),
    }


@router.get("/decision/report/{result_id}")
def get_decision_report(
    result_id: int,
    db: Session = Depends(get_db),
):
    row = db.execute(
        text("""
            SELECT *
            FROM auction_decision_results
            WHERE id = :result_id
        """),
        {"result_id": result_id},
    ).mappings().first()

    if not row:
        return {
            "found": False,
            "version": "MCP 17.4",
            "result_id": result_id,
            "message": "리포트를 생성할 경매 종합 판정 결과가 없습니다.",
        }

    report = _build_decision_report(dict(row))

    return {
        "found": True,
        "version": "MCP 17.4",
        "report": report,
        "message": "경매 종합 판정 리포트 생성 완료",
    }


@router.get("/decision/report/latest/{document_id}")
def get_latest_decision_report(
    document_id: int,
    db: Session = Depends(get_db),
):
    row = db.execute(
        text("""
            SELECT *
            FROM auction_decision_results
            WHERE document_id = :document_id
            ORDER BY created_at DESC, id DESC
            LIMIT 1
        """),
        {"document_id": document_id},
    ).mappings().first()

    if not row:
        return {
            "found": False,
            "version": "MCP 17.4",
            "document_id": document_id,
            "message": "리포트를 생성할 최신 경매 종합 판정 결과가 없습니다.",
        }

    report = _build_decision_report(dict(row))

    return {
        "found": True,
        "version": "MCP 17.4",
        "report": report,
        "message": "최신 경매 종합 판정 리포트 생성 완료",
    }

@router.get("/decision/result/latest/{document_id}")
def get_latest_decision_result_by_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    row = db.execute(
        text("""
            SELECT *
            FROM auction_decision_results
            WHERE document_id = :document_id
            ORDER BY created_at DESC, id DESC
            LIMIT 1
        """),
        {"document_id": document_id},
    ).mappings().first()

    if not row:
        return {
            "found": False,
            "version": "MCP 17.3",
            "document_id": document_id,
            "message": "저장된 경매 종합 판정 결과가 없습니다.",
        }

    return {
        "found": True,
        "version": "MCP 17.3",
        "result": dict(row),
        "message": "최신 경매 종합 판정 결과 조회 완료",
    }


@router.get("/decision/result/{result_id}")
def get_decision_result(
    result_id: int,
    db: Session = Depends(get_db),
):
    row = db.execute(
        text("""
            SELECT *
            FROM auction_decision_results
            WHERE id = :result_id
        """),
        {"result_id": result_id},
    ).mappings().first()

    if not row:
        return {
            "found": False,
            "version": "MCP 17.3",
            "result_id": result_id,
            "message": "경매 종합 판정 결과가 없습니다.",
        }

    return {
        "found": True,
        "version": "MCP 17.3",
        "result": dict(row),
        "message": "경매 종합 판정 결과 상세 조회 완료",
    }

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
