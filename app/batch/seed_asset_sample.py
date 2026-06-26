from app.core.database import SessionLocal
from app.models.asset import AssetAccount


def main():
    db = SessionLocal()

    try:
        samples = [
            AssetAccount(
                asset_type="cash",
                asset_name="증권 예수금",
                quantity=1,
                amount=7000000,
                currency="KRW",
                memo="주문 가능 현금"
            ),
            AssetAccount(
                asset_type="stock",
                asset_name="한전기술",
                quantity=25,
                amount=2882500,
                currency="KRW",
                memo="MCP 추천 보유 종목"
            ),
            AssetAccount(
                asset_type="etf",
                asset_name="TIGER 미국나스닥100",
                quantity=100,
                amount=2500000,
                currency="KRW",
                memo="장기 성장 ETF"
            ),
            AssetAccount(
                asset_type="usd",
                asset_name="달러 예수금",
                quantity=3000,
                amount=4200000,
                currency="USD",
                memo="환율 방어 자산"
            ),
            AssetAccount(
                asset_type="bond",
                asset_name="채권형 ETF",
                quantity=50,
                amount=1500000,
                currency="KRW",
                memo="안정형 자산"
            ),
        ]

        db.add_all(samples)
        db.commit()

        print("MCP 14 sample asset data inserted successfully")

    finally:
        db.close()


if __name__ == "__main__":
    main()
