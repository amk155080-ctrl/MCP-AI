from app.core.database import SessionLocal

from app.models.auction_asset import AuctionAsset


def main():
    db = SessionLocal()

    try:

        rows = [

            AuctionAsset(
                case_number="2026타경10001",
                item_number="1",
                address="서울 중랑구 면목동",
                appraisal_price=500000000,
                minimum_price=400000000,
                expected_bid_price=420000000,
                expected_sale_price=500000000,
                status="WATCH",
                bid_date="2026-08-10"
            ),

            AuctionAsset(
                case_number="2026타경10002",
                item_number="1",
                address="경기 남양주시",
                appraisal_price=300000000,
                minimum_price=240000000,
                expected_bid_price=250000000,
                expected_sale_price=320000000,
                status="BID",
                bid_date="2026-07-20"
            )

        ]

        db.add_all(rows)
        db.commit()

        print(
            "MCP 15.2 auction asset sample inserted"
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()
