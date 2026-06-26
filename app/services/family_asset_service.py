from sqlalchemy.orm import Session

from app.models.family_asset import FamilyAsset


class FamilyAssetService:

    @staticmethod
    def get_all(db: Session):
        rows = (
            db.query(FamilyAsset)
            .order_by(FamilyAsset.id.asc())
            .all()
        )

        return [
            {
                "id": r.id,
                "owner": r.owner,
                "asset_category": r.asset_category,
                "asset_name": r.asset_name,
                "purchase_price": float(r.purchase_price or 0),
                "current_value": float(r.current_value or 0),
                "profit_loss": float((r.current_value or 0) - (r.purchase_price or 0)),
                "memo": r.memo,
                "created_at": str(r.created_at),
            }
            for r in rows
        ]

    @staticmethod
    def get_summary(db: Session):
        rows = db.query(FamilyAsset).all()

        total_purchase = 0
        total_current = 0

        by_owner = {}
        by_category = {}

        for r in rows:
            purchase = float(r.purchase_price or 0)
            current = float(r.current_value or 0)

            total_purchase += purchase
            total_current += current

            if r.owner not in by_owner:
                by_owner[r.owner] = {
                    "purchase_price": 0,
                    "current_value": 0,
                    "profit_loss": 0,
                    "count": 0,
                }

            by_owner[r.owner]["purchase_price"] += purchase
            by_owner[r.owner]["current_value"] += current
            by_owner[r.owner]["profit_loss"] += current - purchase
            by_owner[r.owner]["count"] += 1

            if r.asset_category not in by_category:
                by_category[r.asset_category] = {
                    "purchase_price": 0,
                    "current_value": 0,
                    "profit_loss": 0,
                    "count": 0,
                }

            by_category[r.asset_category]["purchase_price"] += purchase
            by_category[r.asset_category]["current_value"] += current
            by_category[r.asset_category]["profit_loss"] += current - purchase
            by_category[r.asset_category]["count"] += 1

        return {
            "total_purchase": total_purchase,
            "total_current": total_current,
            "total_profit_loss": total_current - total_purchase,
            "asset_count": len(rows),
            "by_owner": by_owner,
            "by_category": by_category,
        }

    @staticmethod
    def get_family(db: Session):
        summary = FamilyAssetService.get_summary(db)
        by_owner = summary.get("by_owner", {})

        my_asset = by_owner.get("본인", {}).get("current_value", 0)
        wife_asset = by_owner.get("배우자", {}).get("current_value", 0)

        return {
            "my_asset": my_asset,
            "wife_asset": wife_asset,
            "family_asset": my_asset + wife_asset,
            "owners": by_owner,
        }
