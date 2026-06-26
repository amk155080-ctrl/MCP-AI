class AllocationService:

    @staticmethod
    def analyze(summary: dict):
        total = summary.get("total_asset", 0)

        if total <= 0:
            return {
                "total_asset": 0,
                "cash_ratio": 0,
                "stock_ratio": 0,
                "etf_ratio": 0,
                "usd_ratio": 0,
                "bond_ratio": 0,
                "etc_ratio": 0,
            }

        return {
            "total_asset": total,
            "cash_ratio": round(summary.get("cash", 0) / total * 100, 2),
            "stock_ratio": round(summary.get("stock", 0) / total * 100, 2),
            "etf_ratio": round(summary.get("etf", 0) / total * 100, 2),
            "usd_ratio": round(summary.get("usd", 0) / total * 100, 2),
            "bond_ratio": round(summary.get("bond", 0) / total * 100, 2),
            "etc_ratio": round(summary.get("etc", 0) / total * 100, 2),
        }
