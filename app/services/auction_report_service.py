from app.services.auction_asset_service import AuctionAssetService
from app.services.auction_ai_service import AuctionAIService
from app.services.auction_portfolio_service import AuctionPortfolioService
from app.services.auction_risk_service import AuctionRiskService


class AuctionReportService:

    @staticmethod
    def dashboard(db):
        summary = AuctionAssetService.get_summary(db)
        profit = AuctionAIService.get_profit_analysis(db)
        recommend = AuctionAIService.get_ai_recommendation(db)
        portfolio = AuctionPortfolioService.portfolio(db)
        optimized_bid = AuctionPortfolioService.optimize_bid(db)
        risk_summary = AuctionRiskService.summary(db)

        return {
            "title": "MCP 15.6 경매 종합 대시보드",
            "auction_summary": summary,
            "portfolio": {
                "total_count": portfolio.get("total_count"),
                "total_expected_bid_price": portfolio.get("total_expected_bid_price"),
                "total_expected_sale_price": portfolio.get("total_expected_sale_price"),
                "total_expected_profit": portfolio.get("total_expected_profit"),
                "portfolio_roi_percent": portfolio.get("portfolio_roi_percent"),
            },
            "risk": {
                "low_count": risk_summary.get("low_count"),
                "normal_count": risk_summary.get("normal_count"),
                "high_count": risk_summary.get("high_count"),
                "very_high_count": risk_summary.get("very_high_count"),
            },
            "profit_items": profit,
            "recommend_items": recommend,
            "optimized_bid_items": optimized_bid,
            "risk_items": risk_summary.get("items", []),
        }

    @staticmethod
    def kakao_report(db):
        dashboard = AuctionReportService.dashboard(db)

        summary = dashboard.get("auction_summary", {})
        portfolio = dashboard.get("portfolio", {})
        risk = dashboard.get("risk", {})
        recommend_items = dashboard.get("recommend_items", [])
        optimized_items = dashboard.get("optimized_bid_items", [])

        top_recommend = recommend_items[0] if recommend_items else {}
        top_bid = optimized_items[0] if optimized_items else {}

        text = f"""
[MCP 15.6 경매 종합 리포트]

경매 물건 현황
총 물건: {summary.get("total_count", 0)}건
관심: {summary.get("watch_count", 0)}건
입찰: {summary.get("bid_count", 0)}건
낙찰: {summary.get("win_count", 0)}건

포트폴리오
예상 입찰금액: {portfolio.get("total_expected_bid_price", 0):,.0f}원
예상 매각금액: {portfolio.get("total_expected_sale_price", 0):,.0f}원
예상 수익: {portfolio.get("total_expected_profit", 0):,.0f}원
예상 ROI: {portfolio.get("portfolio_roi_percent", 0)}%

리스크
LOW: {risk.get("low_count", 0)}건
NORMAL: {risk.get("normal_count", 0)}건
HIGH: {risk.get("high_count", 0)}건
VERY_HIGH: {risk.get("very_high_count", 0)}건

AI 최우선 추천
사건번호: {top_recommend.get("case_number", "-")}
주소: {top_recommend.get("address", "-")}
추천: {top_recommend.get("recommendation", "-")}
점수: {top_recommend.get("score", 0)}점
ROI: {top_recommend.get("roi_percent", 0)}%

AI 낙찰가 제안
사건번호: {top_bid.get("case_number", "-")}
추천 입찰가: {top_bid.get("recommended_bid_price", 0):,.0f}원
판단: {top_bid.get("action", "-")}

AI 의견
현재 경매 포트폴리오는 예상 수익성과 리스크가 양호합니다.
다만 실제 입찰 전에는 권리분석, 임차인, 미납관리비, 명도 리스크를 반드시 별도 확인해야 합니다.
""".strip()

        return {
            "title": "MCP 15.6 경매 카카오 리포트",
            "text": text,
        }
