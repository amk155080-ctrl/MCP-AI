from sqlalchemy.orm import Session

from app.models.asset import AssetAccount


class AssetService:

    @staticmethod
    def get_all_assets(db: Session):
        rows = (
            db.query(AssetAccount)
            .order_by(AssetAccount.id.asc())
            .all()
        )

        return [
            {
                "id": r.id,
                "asset_type": r.asset_type,
                "asset_name": r.asset_name,
                "quantity": float(r.quantity or 0),
                "amount": float(r.amount or 0),
                "currency": r.currency,
                "memo": r.memo,
                "updated_at": str(r.updated_at),
            }
            for r in rows
        ]

    @staticmethod
    def get_summary(db: Session):
        rows = db.query(AssetAccount).all()

        result = {
            "cash": 0,
            "stock": 0,
            "etf": 0,
            "usd": 0,
            "bond": 0,
            "etc": 0,
        }

        total_asset = 0

        for r in rows:
            amount = float(r.amount or 0)
            asset_type = r.asset_type

            total_asset += amount

            if asset_type in result:
                result[asset_type] += amount
            else:
                result["etc"] += amount

        result["total_asset"] = total_asset
        result["count"] = len(rows)

        return result
