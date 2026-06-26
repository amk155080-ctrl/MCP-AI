from sqlalchemy.orm import Session

from app.models.auction_rights import AuctionRights


class AuctionRightsService:

    @staticmethod
    def _to_float(value):
        try:
            return float(value or 0)
        except Exception:
            return 0.0

    @staticmethod
    def get_by_auction_id(db: Session, auction_id: int):
        rights = (
            db.query(AuctionRights)
            .filter(AuctionRights.auction_id == auction_id)
            .order_by(AuctionRights.id.desc())
            .first()
        )

        if not rights:
            return None

        return {
            "id": rights.id,
            "auction_id": rights.auction_id,
            "base_right": rights.base_right,
            "tenant_priority": rights.tenant_priority,
            "lease_deposit": AuctionRightsService._to_float(rights.lease_deposit),
            "takeover_amount": AuctionRightsService._to_float(rights.takeover_amount),
            "occupancy": rights.occupancy,
            "eviction_level": rights.eviction_level,
            "comment": rights.comment,
            "created_at": str(rights.created_at),
        }

    @staticmethod
    def get_all(db: Session):
        rows = (
            db.query(AuctionRights)
            .order_by(AuctionRights.id.desc())
            .all()
        )

        return [
            {
                "id": r.id,
                "auction_id": r.auction_id,
                "base_right": r.base_right,
                "tenant_priority": r.tenant_priority,
                "lease_deposit": AuctionRightsService._to_float(r.lease_deposit),
                "takeover_amount": AuctionRightsService._to_float(r.takeover_amount),
                "occupancy": r.occupancy,
                "eviction_level": r.eviction_level,
                "comment": r.comment,
                "created_at": str(r.created_at),
            }
            for r in rows
        ]
    @staticmethod
    def create(db: Session, data):

        row = AuctionRights(**data.dict())

        db.add(row)

        db.commit()

        db.refresh(row)

        return row

    @staticmethod
    def update(db: Session, auction_id, data):

        row = (

            db.query(AuctionRights)

            .filter(

                AuctionRights.auction_id == auction_id

            )

            .first()

        )

        if not row:

            return None

        values = data.dict()

        for key, value in values.items():

            setattr(row, key, value)

        db.commit()

        db.refresh(row)

        return row

    @staticmethod
    def delete(db: Session, auction_id):

        row = (

            db.query(AuctionRights)

            .filter(

                AuctionRights.auction_id == auction_id

            )

            .first()

        )

        if not row:

            return False

        db.delete(row)

        db.commit()

        return True
