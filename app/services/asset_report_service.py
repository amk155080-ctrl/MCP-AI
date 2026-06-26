class AssetReportService:

    @staticmethod
    def make_dashboard(summary: dict, allocation: dict, health: dict, rebalance: dict):
        return {
            "title": "MCP 자산관리 대시보드",
            "total_asset": summary.get("total_asset", 0),
            "asset_count": summary.get("count", 0),
            "allocation": allocation,
            "health_score": health.get("score"),
            "health_grade": health.get("grade"),
            "risk_level": health.get("risk_level"),
            "rebalance_action": rebalance.get("action"),
            "rebalance_message": rebalance.get("message"),
            "summary_cards": [
                {
                    "name": "현금",
                    "amount": summary.get("cash", 0),
                    "ratio": allocation.get("cash_ratio", 0),
                },
                {
                    "name": "주식",
                    "amount": summary.get("stock", 0),
                    "ratio": allocation.get("stock_ratio", 0),
                },
                {
                    "name": "ETF",
                    "amount": summary.get("etf", 0),
                    "ratio": allocation.get("etf_ratio", 0),
                },
                {
                    "name": "달러",
                    "amount": summary.get("usd", 0),
                    "ratio": allocation.get("usd_ratio", 0),
                },
                {
                    "name": "채권",
                    "amount": summary.get("bond", 0),
                    "ratio": allocation.get("bond_ratio", 0),
                },
            ],
        }

    @staticmethod
    def make_kakao_report(summary: dict, allocation: dict, health: dict, rebalance: dict):
        total_asset = int(summary.get("total_asset", 0))

        text = f"""
[MCP 14 자산관리 리포트]

총자산
{total_asset:,}원

자산배분
현금: {summary.get("cash", 0):,.0f}원 ({allocation.get("cash_ratio", 0)}%)
주식: {summary.get("stock", 0):,.0f}원 ({allocation.get("stock_ratio", 0)}%)
ETF: {summary.get("etf", 0):,.0f}원 ({allocation.get("etf_ratio", 0)}%)
달러: {summary.get("usd", 0):,.0f}원 ({allocation.get("usd_ratio", 0)}%)
채권: {summary.get("bond", 0):,.0f}원 ({allocation.get("bond_ratio", 0)}%)

자산건전성
점수: {health.get("score")}점
등급: {health.get("grade")}
리스크: {health.get("risk_level")}

리밸런싱 의견
{rebalance.get("action")}
{rebalance.get("message")}

AI 의견
현재 자산배분은 {health.get("grade")}등급이며, 리스크 수준은 {health.get("risk_level")}입니다.
""".strip()

        return {
            "title": "MCP 14 자산관리 카카오 리포트",
            "text": text,
        }
