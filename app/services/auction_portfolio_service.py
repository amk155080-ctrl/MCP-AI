from sqlalchemy.orm import Session

from app.models.auction_asset import AuctionAsset


class AuctionPortfolioService:

    @staticmethod
    def _to_float(value):
        try:
            return float(value or 0)
        except Exception:
            return 0.0

    @staticmethod
    def portfolio(db: Session):
        rows = db.query(AuctionAsset).all()

        total_minimum = 0
        total_expected_bid = 0
        total_expected_sale = 0
        total_expected_profit = 0

        items = []

        for r in rows:
            minimum_price = AuctionPortfolioService._to_float(r.minimum_price)
            bid_price = AuctionPortfolioService._to_float(r.expected_bid_price)
            sale_price = AuctionPortfolioService._to_float(r.expected_sale_price)

            profit = sale_price - bid_price
            roi = round((profit / bid_price) * 100, 2) if bid_price > 0 else 0

            total_minimum += minimum_price
            total_expected_bid += bid_price
            total_expected_sale += sale_price
            total_expected_profit += profit

            items.append({
                "case_number": r.case_number,
                "address": r.address,
                "status": r.status,
                "minimum_price": minimum_price,
                "expected_bid_price": bid_price,
                "expected_sale_price": sale_price,
                "expected_profit": profit,
                "roi_percent": roi,
            })

        portfolio_roi = 0
        if total_expected_bid > 0:
            portfolio_roi = round(
                total_expected_profit / total_expected_bid * 100,
                2
            )

        return {
            "total_count": len(rows),
            "total_minimum_price": total_minimum,
            "total_expected_bid_price": total_expected_bid,
            "total_expected_sale_price": total_expected_sale,
            "total_expected_profit": total_expected_profit,
            "portfolio_roi_percent": portfolio_roi,
            "items": items,
        }

    @staticmethod
    def optimize_bid(db: Session):
        rows = db.query(AuctionAsset).all()

        result = []

        for r in rows:
            appraisal_price = AuctionPortfolioService._to_float(r.appraisal_price)
            minimum_price = AuctionPortfolioService._to_float(r.minimum_price)
            sale_price = AuctionPortfolioService._to_float(r.expected_sale_price)

            target_profit_rate = 0.15
            safety_margin = 0.03

            max_bid_price = sale_price / (1 + target_profit_rate)

            safe_bid_price = max_bid_price * (1 - safety_margin)

            if safe_bid_price < minimum_price:
                action = "PASS"
                reason = "안전 입찰가가 최저가보다 낮아 수익성이 부족합니다."
            else:
                action = "BID_OK"
                reason = "목표 수익률 기준 입찰 가능 구간입니다."

            discount_rate = 0
            if appraisal_price > 0:
                discount_rate = round(
                    (1 - safe_bid_price / appraisal_price) * 100,
                    2
                )

            result.append({
                "case_number": r.case_number,
                "address": r.address,
                "appraisal_price": appraisal_price,
                "minimum_price": minimum_price,
                "expected_sale_price": sale_price,
                "recommended_bid_price": round(safe_bid_price),
                "discount_rate_percent": discount_rate,
                "target_profit_rate_percent": 15,
                "safety_margin_percent": 3,
                "action": action,
                "reason": reason,
            })

        result.sort(
            key=lambda x: x["recommended_bid_price"],
            reverse=True
        )

        return result
