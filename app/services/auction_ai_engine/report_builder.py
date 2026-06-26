class AuctionEngineReportBuilder:

    @staticmethod
    def build(auction, rights, eviction, bid, risk, committee):
        return {
            "title": "MCP 15 Auction AI Engine Report",
            "auction": {
                "id": auction.id,
                "case_number": auction.case_number,
                "address": auction.address,
                "status": auction.status,
                "bid_date": auction.bid_date,
                "appraisal_price": float(auction.appraisal_price or 0),
                "minimum_price": float(auction.minimum_price or 0),
                "expected_bid_price": float(auction.expected_bid_price or 0),
                "expected_sale_price": float(auction.expected_sale_price or 0),
            },
            "rights_analysis": rights,
            "eviction_analysis": eviction,
            "bid_prediction": bid,
            "risk_analysis": risk,
            "committee": committee,
            "summary": {
                "final_score": committee.get("final_score"),
                "decision": committee.get("decision"),
                "final_opinion": committee.get("final_opinion"),
                "recommended_bid_price": bid.get("recommended_bid_price"),
                "risk_level": risk.get("risk_level"),
            },
        }

    @staticmethod
    def kakao(report):
        auction = report.get("auction", {})
        summary = report.get("summary", {})
        rights = report.get("rights_analysis", {})
        eviction = report.get("eviction_analysis", {})
        bid = report.get("bid_prediction", {})
        risk = report.get("risk_analysis", {})
        committee = report.get("committee", {})

        text = f"""
[MCP 15 Auction AI Engine]

사건번호: {auction.get("case_number")}
주소: {auction.get("address")}
상태: {auction.get("status")}
입찰일: {auction.get("bid_date")}

감정가: {auction.get("appraisal_price", 0):,.0f}원
최저가: {auction.get("minimum_price", 0):,.0f}원
예상 매각가: {auction.get("expected_sale_price", 0):,.0f}원

권리분석: {rights.get("risk_level")} / {rights.get("score")}점
명도위험: {eviction.get("risk_level")} / {eviction.get("score")}점
종합리스크: {risk.get("risk_level")} / {risk.get("score")}점

추천 입찰가: {bid.get("recommended_bid_price", 0):,.0f}원
입찰 판단: {bid.get("action")}

최종점수: {summary.get("final_score")}점
최종의견: {summary.get("final_opinion")}
결정: {summary.get("decision")}

AI 코멘트:
{", ".join(committee.get("comments", []))}
""".strip()

        return {
            "title": "MCP 15 Auction AI Engine 카카오 리포트",
            "text": text,
        }
