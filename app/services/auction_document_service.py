from sqlalchemy.orm import Session

from app.models.auction_document import AuctionDocument


class AuctionDocumentService:

    @staticmethod
    def create(db: Session, data):
        row = AuctionDocument(**data.dict())

        db.add(row)
        db.commit()
        db.refresh(row)

        return row

    @staticmethod
    def get_all(db: Session):
        rows = (
            db.query(AuctionDocument)
            .order_by(AuctionDocument.id.desc())
            .all()
        )

        return [
            AuctionDocumentService.to_dict(row)
            for row in rows
        ]

    @staticmethod
    def get_by_id(db: Session, document_id: int):
        row = (
            db.query(AuctionDocument)
            .filter(AuctionDocument.id == document_id)
            .first()
        )

        if not row:
            return None

        return AuctionDocumentService.to_dict(row)

    @staticmethod
    def get_by_auction_id(db: Session, auction_id: int):
        rows = (
            db.query(AuctionDocument)
            .filter(AuctionDocument.auction_id == auction_id)
            .order_by(AuctionDocument.id.desc())
            .all()
        )

        return [
            AuctionDocumentService.to_dict(row)
            for row in rows
        ]

    @staticmethod
    def update(db: Session, document_id: int, data):
        row = (
            db.query(AuctionDocument)
            .filter(AuctionDocument.id == document_id)
            .first()
        )

        if not row:
            return None

        values = data.dict(exclude_none=True)

        for key, value in values.items():
            setattr(row, key, value)

        db.commit()
        db.refresh(row)

        return row

    @staticmethod
    def delete(db: Session, document_id: int):
        row = (
            db.query(AuctionDocument)
            .filter(AuctionDocument.id == document_id)
            .first()
        )

        if not row:
            return False

        db.delete(row)
        db.commit()

        return True

    @staticmethod
    def to_dict(row: AuctionDocument):
        return {
            "id": row.id,
            "auction_id": row.auction_id,
            "document_type": row.document_type,
            "file_name": row.file_name,
            "file_path": row.file_path,
            "pages": row.pages,
            "ocr_status": row.ocr_status,
            "analysis_status": row.analysis_status,
            "summary": row.summary,
            "created_at": str(row.created_at),
        }
