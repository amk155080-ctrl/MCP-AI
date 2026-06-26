class BidPredictor:

    @staticmethod
    def _to_float(value):
        try:
            return float(value or 0)
        except Exception:
            return 0.0

    @staticmethod
    def predict(auction):
        appraisal_price = BidPredictor._to_float(
            auction.appraisal_price
        )
        minimum_price = BidPredictor._to_float(
            auction.minimum_price
        )
        expected_sale_price = BidPredictor._to_float(
            auction.expected_sale_price
        )

        target_profit_rate = 0.15
        safety_margin = 0.03

        if expected_sale_price <= 0:
            return {
                "recommended_bid_price": 0,
                "action": "PASS",
                "reason": "예상 매각가가 없어 입찰가 산정 불가"
            }

        max_bid_price = expected_sale_price / (
            1 + target_profit_rate
        )

        recommended_bid_price = max_bid_price * (
            1 - safety_margin
        )

        if recommended_bid_price < minimum_price:
            action = "PASS"
            reason = "추천 입찰가가 최저가보다 낮아 수익성 부족"
        else:
            action = "BID_OK"
            reason = "목표 수익률 기준 입찰 가능"

        discount_rate = 0

        if appraisal_price > 0:
            discount_rate = round(
                (1 - recommended_bid_price / appraisal_price) * 100,
                2
            )

        return {
            "recommended_bid_price": round(recommended_bid_price),
            "target_profit_rate_percent": 15,
            "safety_margin_percent": 3,
            "discount_rate_percent": discount_rate,
            "action": action,
            "reason": reason
        }
