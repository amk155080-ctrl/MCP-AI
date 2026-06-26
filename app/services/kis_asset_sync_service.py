import requests
from sqlalchemy.orm import Session

from app.models.asset import AssetAccount


class KisAssetSyncService:

    BASE_URL = "http://127.0.0.1:8000"

    @staticmethod
    def _to_float(value):
        try:
            return float(str(value).replace(",", ""))
        except Exception:
            return 0.0

    @staticmethod
    def sync(db: Session):
        balance_url = f"{KisAssetSyncService.BASE_URL}/api/v11/kis/balance"
        positions_url = f"{KisAssetSyncService.BASE_URL}/api/v11/kis/positions"

        balance_res = requests.get(balance_url, timeout=10).json()
        positions_res = requests.get(positions_url, timeout=10).json()

        deleted_count = (
            db.query(AssetAccount)
            .filter(AssetAccount.memo.like("%자동동기화%"))
            .delete(synchronize_session=False)
        )

        inserted = []

        output2 = balance_res.get("output2", [])
        if output2:
            cash_data = output2[0]

            cash_amount = KisAssetSyncService._to_float(
                cash_data.get("dnca_tot_amt", 0)
            )

            total_eval = KisAssetSyncService._to_float(
                cash_data.get("tot_evlu_amt", 0)
            )

            net_asset = KisAssetSyncService._to_float(
                cash_data.get("nass_amt", 0)
            )

            db.add(
                AssetAccount(
                    asset_type="cash",
                    asset_name="KIS 예수금",
                    quantity=1,
                    amount=cash_amount,
                    currency="KRW",
                    memo="KIS 계좌 예수금 자동동기화"
                )
            )
            inserted.append("cash")

            if total_eval > 0:
                db.add(
                    AssetAccount(
                        asset_type="etc",
                        asset_name="KIS 총평가금액",
                        quantity=1,
                        amount=total_eval,
                        currency="KRW",
                        memo="KIS 계좌 총평가금액 자동동기화"
                    )
                )
                inserted.append("total_eval")

            if net_asset > 0:
                db.add(
                    AssetAccount(
                        asset_type="etc",
                        asset_name="KIS 순자산",
                        quantity=1,
                        amount=net_asset,
                        currency="KRW",
                        memo="KIS 계좌 순자산 자동동기화"
                    )
                )
                inserted.append("net_asset")

        positions = positions_res.get("output1", [])
        if not positions:
            positions = positions_res.get("positions", [])
        if not positions:
            positions = positions_res.get("items", [])

        for p in positions:
            stock_code = (
                p.get("pdno")
                or p.get("stock_code")
                or p.get("code")
                or ""
            )

            stock_name = (
                p.get("prdt_name")
                or p.get("stock_name")
                or p.get("name")
                or stock_code
            )

            quantity = KisAssetSyncService._to_float(
                p.get("hldg_qty")
                or p.get("quantity")
                or p.get("qty")
                or 0
            )

            amount = KisAssetSyncService._to_float(
                p.get("evlu_amt")
                or p.get("evaluation_amount")
                or p.get("amount")
                or 0
            )

            asset_type = "stock"

            upper_name = stock_name.upper()
            if (
                "ETF" in upper_name
                or "TIGER" in upper_name
                or "KODEX" in upper_name
            ):
                asset_type = "etf"

            db.add(
                AssetAccount(
                    asset_type=asset_type,
                    asset_name=stock_name,
                    quantity=quantity,
                    amount=amount,
                    currency="KRW",
                    memo=f"KIS 보유종목 자동동기화 {stock_code}"
                )
            )

            inserted.append(stock_name)

        db.commit()

        return {
            "found": True,
            "version": "MCP 14.8",
            "balance_rt_cd": balance_res.get("rt_cd"),
            "positions_found": len(positions),
            "deleted_auto_sync_count": deleted_count,
            "inserted_count": len(inserted),
            "inserted": inserted,
            "message": "KIS 자산 자동동기화 완료"
        }
