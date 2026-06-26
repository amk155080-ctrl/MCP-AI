from app.core.database import SessionLocal
from app.models.auction_rights import AuctionRights


def main():
    db = SessionLocal()

    try:
        rows = [

            AuctionRights(
                auction_id=1,
                base_right="근저당",
                tenant_priority="없음",
                lease_deposit=0,
                takeover_amount=0,
                occupancy="소유자",
                eviction_level="LOW",
                comment="권리관계 양호"
            ),

            AuctionRights(
                auction_id=2,
                base_right="근저당",
                tenant_priority="선순위",
                lease_deposit=80000000,
                takeover_amount=50000000,
                occupancy="임차인",
                eviction_level="HIGH",
                comment="인수금액 확인 필요"
            )

        ]

        db.add_all(rows)
        db.commit()

        print("MCP 15.13 rights sample inserted")

    finally:
        db.close()


if __name__ == "__main__":
    main()
