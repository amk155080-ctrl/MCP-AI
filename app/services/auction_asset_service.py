from sqlalchemy.orm import Session

from app.models.auction_asset import AuctionAsset


class AuctionAssetService:

    @staticmethod
    def _to_float(value):
        try:
            return float(value or 0)
        except Exception:
            return 0.0

    @staticmethod
    def get_all(db: Session):
        rows = (
            db.query(AuctionAsset)
            .order_by(AuctionAsset.id.desc())
            .all()
        )

        result = []

        for r in rows:
            expected_sale_price = AuctionAssetService._to_float(r.expected_sale_price)
            expected_bid_price = AuctionAssetService._to_float(r.expected_bid_price)

            profit = expected_sale_price - expected_bid_price

            result.append(
                {
                    "id": r.id,
                    "case_number": r.case_number,
                    "item_number": r.item_number,
                    "address": r.address,
                    "appraisal_price": AuctionAssetService._to_float(r.appraisal_price),
                    "minimum_price": AuctionAssetService._to_float(r.minimum_price),
                    "expected_bid_price": expected_bid_price,
                    "expected_sale_price": expected_sale_price,
                    "expected_profit": profit,
                    "status": r.status,
                    "bid_date": r.bid_date,
                }
            )

        return result

    @staticmethod
    def get_summary(db: Session):
        rows = db.query(AuctionAsset).all()

        watch_count = 0
        bid_count = 0
        win_count = 0
        expected_profit = 0

        for r in rows:
            if r.status == "WATCH":
                watch_count += 1
            elif r.status == "BID":
                bid_count += 1
            elif r.status == "WIN":
                win_count += 1

            expected_profit += (
                AuctionAssetService._to_float(r.expected_sale_price)
                - AuctionAssetService._to_float(r.expected_bid_price)
            )

        return {
            "total_count": len(rows),
            "watch_count": watch_count,
            "bid_count": bid_count,
            "win_count": win_count,
            "expected_profit": expected_profit,
        }
