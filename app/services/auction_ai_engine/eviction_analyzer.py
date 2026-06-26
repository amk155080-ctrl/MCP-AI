from app.models.auction_rights import AuctionRights


class EvictionAnalyzer:

    @staticmethod
    def analyze(auction, db=None):
        score = 100
        flags = []

        rights = None

        if db is not None:
            rights = (
                db.query(AuctionRights)
                .filter(AuctionRights.auction_id == auction.id)
                .order_by(AuctionRights.id.desc())
                .first()
            )

        if rights is None:
            score -= 10
            flags.append("명도 데이터 없음")

            return {
                "score": score,
                "risk_level": EvictionAnalyzer._risk_level(score),
                "flags": flags,
                "message": "명도 데이터 없이 기본 평가 완료"
            }

        if rights.occupancy == "소유자":
            score -= 5
            flags.append("소유자 점유")

        elif rights.occupancy == "임차인":
            score -= 20
            flags.append("임차인 점유")

        elif rights.occupancy == "공실":
            flags.append("공실")

        else:
            score -= 10
            flags.append("점유 형태 불명확")

        if rights.eviction_level == "LOW":
            flags.append("명도 난이도 낮음")
        elif rights.eviction_level == "NORMAL":
            score -= 10
            flags.append("명도 난이도 보통")
        elif rights.eviction_level == "HIGH":
            score -= 25
            flags.append("명도 난이도 높음")
        elif rights.eviction_level == "VERY_HIGH":
            score -= 40
            flags.append("명도 난이도 매우 높음")

        return {
            "score": max(score, 0),
            "risk_level": EvictionAnalyzer._risk_level(score),
            "flags": flags,
            "occupancy": rights.occupancy,
            "eviction_level": rights.eviction_level,
            "message": "DB 기반 명도위험 평가 완료"
        }

    @staticmethod
    def _risk_level(score):
        if score >= 85:
            return "LOW"
        if score >= 70:
            return "NORMAL"
        if score >= 55:
            return "HIGH"
        return "VERY_HIGH"
