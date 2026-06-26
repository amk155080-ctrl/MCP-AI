class RebalanceService:

    @staticmethod
    def recommend(summary: dict):

        total = summary.get("total_asset", 0)

        if total <= 0:
            return {
                "action": "NO_DATA"
            }

        stock_ratio = (
            summary.get("stock", 0)
            / total
            * 100
        )

        cash_ratio = (
            summary.get("cash", 0)
            / total
            * 100
        )

        if stock_ratio > 70:

            excess = (
                summary["stock"]
                - total * 0.60
            )

            return {
                "action": "REBALANCE",
                "sell_stock": round(excess),
                "buy_bond": round(excess * 0.3),
                "keep_cash": round(excess * 0.7),
                "message": "주식 비중이 높습니다."
            }

        if cash_ratio > 50:

            invest = (
                summary["cash"]
                - total * 0.30
            )

            return {
                "action": "INVEST",
                "amount": round(invest),
                "message": "현금 비중이 과도합니다."
            }

        return {
            "action": "KEEP",
            "message": "현재 자산배분 유지"
        }
