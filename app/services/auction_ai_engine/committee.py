class AuctionCommittee:

    @staticmethod
    def decide(auction, rights_result, eviction_result, bid_result, risk_result):
        score = 35
        comments = []

        rights_score = rights_result.get("score", 0)
        eviction_score = eviction_result.get("score", 0)
        risk_score = risk_result.get("score", 0)
        bid_action = bid_result.get("action")

        appraisal_price = float(auction.appraisal_price or 0)
        minimum_price = float(auction.minimum_price or 0)
        expected_bid_price = float(auction.expected_bid_price or 0)
        expected_sale_price = float(auction.expected_sale_price or 0)
        recommended_bid_price = float(
            bid_result.get("recommended_bid_price", 0) or 0
        )

        profit = expected_sale_price - recommended_bid_price
        roi = 0
        if recommended_bid_price > 0:
            roi = round(profit / recommended_bid_price * 100, 2)

        score += rights_score * 0.10
        score += eviction_score * 0.10
        score += risk_score * 0.20

        if bid_action == "BID_OK":
            score += 10
            comments.append("입찰가 조건 충족")
        else:
            score -= 25
            comments.append("입찰가 조건 미충족")

        if roi >= 30:
            score += 15
            comments.append("예상 수익률 매우 우수")
        elif roi >= 20:
            score += 8
            comments.append("예상 수익률 양호")
        elif roi >= 15:
            score += 3
            comments.append("예상 수익률 보통")
        else:
            score -= 15
            comments.append("예상 수익률 부족")

        if appraisal_price > 0 and recommended_bid_price > 0:
            bid_to_appraisal = recommended_bid_price / appraisal_price * 100

            if bid_to_appraisal >= 90:
                score -= 15
                comments.append("감정가 대비 추천입찰가 높음")
            elif bid_to_appraisal >= 80:
                score -= 7
                comments.append("감정가 대비 추천입찰가 다소 높음")
            else:
                comments.append("감정가 대비 입찰가 안정적")

        if minimum_price > 0 and recommended_bid_price > 0:
            min_gap = recommended_bid_price - minimum_price
            min_gap_ratio = min_gap / minimum_price * 100

            if min_gap_ratio >= 15:
                score -= 10
                comments.append("최저가 대비 입찰가 과도")
            elif min_gap_ratio >= 8:
                score -= 5
                comments.append("최저가 대비 입찰가 다소 높음")
            else:
                comments.append("최저가 대비 입찰가 안정적")

        if auction.status == "BID":
            score -= 5
            comments.append("입찰 진행 중 보수적 판단 적용")

        if risk_result.get("risk_level") == "LOW":
            score += 5
            comments.append("종합 리스크 낮음")
        elif risk_result.get("risk_level") == "NORMAL":
            score -= 5
            comments.append("종합 리스크 보통")
        elif risk_result.get("risk_level") == "HIGH":
            score -= 15
            comments.append("종합 리스크 높음")
        elif risk_result.get("risk_level") == "VERY_HIGH":
            score -= 30
            comments.append("종합 리스크 매우 높음")

        final_score = round(min(max(score, 0), 100), 2)

        if final_score >=90:
            final_opinion = "적극 입찰"
            decision = "STRONG_BID"
        elif final_score >= 80:
            final_opinion = "입찰 가능"
            decision = "BID_OK"
        elif final_score >= 65:
            final_opinion = "관찰"
            decision = "WATCH"
        else:
            final_opinion = "입찰 보류"
            decision = "HOLD"

        return {
            "final_score": final_score,
            "decision": decision,
            "final_opinion": final_opinion,
            "roi_percent": roi,
            "comments": comments,
            "message": "Auction AI 입찰위원회 보수적 최종 판단 완료"
        }
