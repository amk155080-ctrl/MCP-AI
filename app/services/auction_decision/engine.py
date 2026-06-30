from app.services.auction_decision.bid_price import calculate_recommended_bid
from app.services.auction_decision.profit import calculate_profit
from app.services.auction_decision.score import (
    calculate_profit_score,
    calculate_risk_score,
    calculate_auction_score,
    make_decision,
    calculate_confidence,
)
from app.services.auction_decision.summary import build_decision_summary


def analyze_auction_decision(
    appraisal_price: int,
    minimum_bid_price: int,
    expected_sale_price: int,
    rights_score: int,
    takeover_amount: int = 0,
    repair_cost: int = 0,
    eviction_cost: int = 0,
    tax_cost: int = 0,
    etc_cost: int = 0,
    target_roi: float = 15.0,
) -> dict:
    bid_result = calculate_recommended_bid(
        appraisal_price=appraisal_price,
        minimum_bid_price=minimum_bid_price,
        expected_sale_price=expected_sale_price,
        rights_score=rights_score,
        target_roi=target_roi,
    )

    profit_result = calculate_profit(
        expected_sale_price=expected_sale_price,
        bid_price=bid_result["recommended_bid"],
        repair_cost=repair_cost,
        eviction_cost=eviction_cost,
        tax_cost=tax_cost,
        etc_cost=etc_cost,
    )

    profit_score = calculate_profit_score(
        expected_roi=profit_result["expected_roi"]
    )

    risk_score = calculate_risk_score(
        rights_score=rights_score,
        expected_roi=profit_result["expected_roi"],
        takeover_amount=takeover_amount,
    )

    auction_score = calculate_auction_score(
        rights_score=rights_score,
        profit_score=profit_score,
        risk_score=risk_score,
    )

    decision = make_decision(
        auction_score=auction_score,
        rights_score=rights_score,
        expected_roi=profit_result["expected_roi"],
        risk_score=risk_score,
    )

    confidence = calculate_confidence(
        auction_score=auction_score,
        rights_score=rights_score,
        profit_score=profit_score,
    )

    result = {
        "version": "MCP17-AUCTION-DECISION-ENGINE-1.0",
        "appraisal_price": appraisal_price,
        "minimum_bid_price": minimum_bid_price,
        "expected_sale_price": expected_sale_price,
        "rights_score": rights_score,
        "takeover_amount": takeover_amount,
        **bid_result,
        **profit_result,
        "profit_score": profit_score,
        "risk_score": risk_score,
        "auction_score": auction_score,
        "decision": decision,
        "confidence": confidence,
    }

    result["summary"] = build_decision_summary(result)

    return result
