from sqlalchemy.orm import Session

from app.models.auction_asset import AuctionAsset


class AuctionRiskService:

    @staticmethod
    def _to_float(value):
        try:
            return float(value or 0)
        except Exception:
            return 0.0

    @staticmethod
    def analyze(db: Session):
        rows = db.query(AuctionAsset).all()

        items = []

        for r in rows:
            appraisal_price = AuctionRiskService._to_float(r.appraisal_price)
            minimum_price = AuctionRiskService._to_float(r.minimum_price)
            bid_price = AuctionRiskService._to_float(r.expected_bid_price)
            sale_price = AuctionRiskService._to_float(r.expected_sale_price)

            risk_score = 100
            risk_flags = []

            if appraisal_price <= 0 or minimum_price <= 0:
                risk_score -= 30
                risk_flags.append("가격 데이터 부족")

            if bid_price <= 0:
                risk_score -= 30
                risk_flags.append("예상 입찰가 없음")

            profit = sale_price - bid_price
            roi = round((profit / bid_price) * 100, 2) if bid_price > 0 else 0

            if roi < 10:
                risk_score -= 25
                risk_flags.append("예상 수익률 낮음")
            elif roi < 20:
                risk_score -= 10
                risk_flags.append("예상 수익률 보통")

            bid_to_appraisal = 0
            if appraisal_price > 0:
                bid_to_appraisal = round((bid_price / appraisal_price) * 100, 2)

            if bid_to_appraisal > 90:
                risk_score -= 15
                risk_flags.append("감정가 대비 입찰가 높음")
            elif bid_to_appraisal > 80:
                risk_score -= 5
                risk_flags.append("감정가 대비 입찰가 다소 높음")

            if r.status == "BID":
                risk_score -= 5
                risk_flags.append("입찰 진행 중")

            if risk_score >= 85:
                risk_level = "LOW"
            elif risk_score >= 70:
                risk_level = "NORMAL"
            elif risk_score >= 55:
                risk_level = "HIGH"
            else:
                risk_level = "VERY_HIGH"

            items.append({
                "case_number": r.case_number,
                "address": r.address,
                "status": r.status,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "roi_percent": roi,
                "bid_to_appraisal_percent": bid_to_appraisal,
                "risk_flags": risk_flags,
            })

        items.sort(
            key=lambda x: x["risk_score"]
        )

        return items

    @staticmethod
    def summary(db: Session):
        items = AuctionRiskService.analyze(db)

        low = 0
        normal = 0
        high = 0
        very_high = 0

        for item in items:
            level = item.get("risk_level")

            if level == "LOW":
                low += 1
            elif level == "NORMAL":
                normal += 1
            elif level == "HIGH":
                high += 1
            elif level == "VERY_HIGH":
                very_high += 1

        total = len(items)

        return {
            "total_count": total,
            "low_count": low,
            "normal_count": normal,
            "high_count": high,
            "very_high_count": very_high,
            "items": items,
        }
