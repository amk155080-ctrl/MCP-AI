from app.core.database import SessionLocal

from app.models.family_asset import FamilyAsset


def main():
    db = SessionLocal()

    try:

        rows = [

            FamilyAsset(
                owner="본인",
                asset_category="stock",
                asset_name="한전기술",
                purchase_price=2500000,
                current_value=2882500,
                memo="MCP 추천"
            ),

            FamilyAsset(
                owner="본인",
                asset_category="cash",
                asset_name="예수금",
                purchase_price=7000000,
                current_value=7000000,
                memo="현금"
            ),

            FamilyAsset(
                owner="배우자",
                asset_category="deposit",
                asset_name="정기예금",
                purchase_price=20000000,
                current_value=20000000,
                memo="안전자산"
            )
        ]

        db.add_all(rows)
        db.commit()

        print(
            "MCP 15.0 family asset sample inserted"
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()
