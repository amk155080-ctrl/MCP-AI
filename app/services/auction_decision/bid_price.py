def calculate_recommended_bid(
    appraisal_price: int,
    minimum_bid_price: int,
    expected_sale_price: int,
    rights_score: int,
    target_roi: float = 15.0,
) -> dict:
    safe_bid_by_roi = int(expected_sale_price / (1 + target_roi / 100))

    if rights_score >= 80:
        rights_discount_rate = 0.95
    elif rights_score >= 60:
        rights_discount_rate = 0.88
    else:
        rights_discount_rate = 0.78

    safe_bid_by_rights = int(appraisal_price * rights_discount_rate)

    recommended_bid = min(
        safe_bid_by_roi,
        safe_bid_by_rights,
        expected_sale_price,
    )

    recommended_bid = max(recommended_bid, minimum_bid_price)

    bid_to_appraisal_rate = round((recommended_bid / appraisal_price) * 100, 2)

    return {
        "recommended_bid": recommended_bid,
        "safe_bid_by_roi": safe_bid_by_roi,
        "safe_bid_by_rights": safe_bid_by_rights,
        "bid_to_appraisal_rate": bid_to_appraisal_rate,
        "target_roi": target_roi,
    }
