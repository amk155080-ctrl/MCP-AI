from fastapi import APIRouter

from app.services.auction_decision.engine import (
    analyze_auction_decision,
)

router = APIRouter(
    prefix="/api/v17",
    tags=["MCP17 Auction Decision"],
)


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
        "version": "MCP 17.0",
        "decision": result,
        "message": "경매 종합 판정 완료",
    }
