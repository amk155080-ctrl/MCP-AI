from sqlalchemy.orm import Session

from app.models.auction_asset import AuctionAsset
from app.models.auction_rights import AuctionRights


class AuctionImportService:

    @staticmethod
    def _to_float(value):
        try:
            return float(str(value).replace(",", "").replace("원", "").strip() or 0)
        except Exception:
            return 0.0

    @staticmethod
    def _normalize_text(value):
        if value is None:
            return ""
        return str(value).strip()

    @staticmethod
    def import_items(db: Session, items: list):
        inserted = []
        updated = []
        skipped = []

        for item in items:
            case_number = AuctionImportService._normalize_text(
                item.get("case_number") or item.get("사건번호")
            )

            item_number = AuctionImportService._normalize_text(
                item.get("item_number") or item.get("물건번호") or "1"
            )

            if not case_number:
                skipped.append({
                    "reason": "사건번호 없음",
                    "item": item,
                })
                continue

            address = AuctionImportService._normalize_text(
                item.get("address") or item.get("주소")
            )

            appraisal_price = AuctionImportService._to_float(
                item.get("appraisal_price") or item.get("감정가")
            )

            minimum_price = AuctionImportService._to_float(
                item.get("minimum_price") or item.get("최저가")
            )

            expected_bid_price = AuctionImportService._to_float(
                item.get("expected_bid_price") or item.get("예상입찰가") or minimum_price
            )

            expected_sale_price = AuctionImportService._to_float(
                item.get("expected_sale_price") or item.get("예상매각가") or appraisal_price
            )

            bid_date = AuctionImportService._normalize_text(
                item.get("bid_date") or item.get("입찰일")
            )

            status = AuctionImportService._normalize_text(
                item.get("status") or item.get("상태") or "WATCH"
            )

            row = (
                db.query(AuctionAsset)
                .filter(
                    AuctionAsset.case_number == case_number,
                    AuctionAsset.item_number == item_number,
                )
                .first()
            )

            if row:
                row.address = address
                row.appraisal_price = appraisal_price
                row.minimum_price = minimum_price
                row.expected_bid_price = expected_bid_price
                row.expected_sale_price = expected_sale_price
                row.bid_date = bid_date
                row.status = status

                updated.append(case_number)

            else:
                row = AuctionAsset(
                    case_number=case_number,
                    item_number=item_number,
                    address=address,
                    appraisal_price=appraisal_price,
                    minimum_price=minimum_price,
                    expected_bid_price=expected_bid_price,
                    expected_sale_price=expected_sale_price,
                    bid_date=bid_date,
                    status=status,
                )

                db.add(row)
                db.flush()

                default_rights = AuctionRights(
                    auction_id=row.id,
                    base_right="확인필요",
                    tenant_priority="확인필요",
                    lease_deposit=0,
                    takeover_amount=0,
                    occupancy="확인필요",
                    eviction_level="NORMAL",
                    comment="CSV Import 후 권리분석 필요"
                )

                db.add(default_rights)
                inserted.append(case_number)

        db.commit()

        return {
            "inserted_count": len(inserted),
            "updated_count": len(updated),
            "skipped_count": len(skipped),
            "inserted": inserted,
            "updated": updated,
            "skipped": skipped,
            "message": "경매 데이터 Import 완료",
        }
