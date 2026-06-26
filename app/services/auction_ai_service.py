from sqlalchemy.orm import Session

from app.models.auction_asset import AuctionAsset


class AuctionAIService:

    @staticmethod
    def get_profit_analysis(db: Session):

        rows = db.query(AuctionAsset).all()

        result = []

        for r in rows:

            bid_price = float(r.expected_bid_price or 0)
            sale_price = float(r.expected_sale_price or 0)

            profit = sale_price - bid_price

            roi = 0

            if bid_price > 0:
                roi = round(
                    (profit / bid_price) * 100,
                    2
                )

            result.append(
                {
                    "case_number": r.case_number,
                    "address": r.address,
                    "expected_profit": profit,
                    "roi_percent": roi,
                    "status": r.status,
                }
            )

        return result

    @staticmethod
    def get_ai_recommendation(db: Session):

        rows = db.query(AuctionAsset).all()

        items = []

        for r in rows:

            bid_price = float(r.expected_bid_price or 0)
            sale_price = float(r.expected_sale_price or 0)

            profit = sale_price - bid_price

            roi = 0

            if bid_price > 0:
                roi = (profit / bid_price) * 100

            score = 50

            if roi >= 30:
                score += 30

            elif roi >= 20:
                score += 20

            elif roi >= 10:
                score += 10

            if r.status == "WATCH":
                score += 5

            recommendation = "PASS"

            if score >= 80:
                recommendation = "STRONG_BUY"

            elif score >= 70:
                recommendation = "BUY"

            elif score >= 60:
                recommendation = "WATCH"

            items.append(
                {
                    "case_number": r.case_number,
                    "address": r.address,
                    "score": score,
                    "recommendation": recommendation,
                    "roi_percent": round(roi, 2),
                }
            )

        items.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return items
