class AuctionRiskEngine:

    @staticmethod
    def _level_to_penalty(level):
        if level == "LOW":
            return 0
        if level == "NORMAL":
            return 10
        if level == "HIGH":
            return 25
        if level == "VERY_HIGH":
            return 40
        return 15

    @staticmethod
    def evaluate(auction, rights_result, eviction_result, bid_result):
        score = 100
        flags = []

        rights_level = rights_result.get("risk_level")
        eviction_level = eviction_result.get("risk_level")
        bid_action = bid_result.get("action")

        rights_penalty = AuctionRiskEngine._level_to_penalty(rights_level)
        eviction_penalty = AuctionRiskEngine._level_to_penalty(eviction_level)

        score -= rights_penalty
        score -= eviction_penalty

        if bid_action == "PASS":
            score -= 30
            flags.append("입찰가 조건 미충족")

        if rights_level in ["HIGH", "VERY_HIGH"]:
            flags.append("권리분석 위험 높음")

        if eviction_level in ["HIGH", "VERY_HIGH"]:
            flags.append("명도위험 높음")

        if score >= 85:
            risk_level = "LOW"
        elif score >= 70:
            risk_level = "NORMAL"
        elif score >= 55:
            risk_level = "HIGH"
        else:
            risk_level = "VERY_HIGH"

        return {
            "score": score,
            "risk_level": risk_level,
            "flags": flags,
            "rights_level": rights_level,
            "eviction_level": eviction_level,
            "bid_action": bid_action,
            "message": "Auction AI Engine 통합 리스크 평가 완료"
        }
