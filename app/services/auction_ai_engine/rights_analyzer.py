from app.models.auction_rights import AuctionRights


class RightsAnalyzer:

    @staticmethod
    def _to_float(value):
        try:
            return float(value or 0)
        except Exception:
            return 0.0

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

        if not auction.case_number:
            score -= 20
            flags.append("사건번호 없음")

        if not auction.address:
            score -= 20
            flags.append("주소 정보 없음")

        if rights is None:
            score -= 15
            flags.append("권리분석 데이터 없음")

            return {
                "score": score,
                "risk_level": RightsAnalyzer._risk_level(score),
                "flags": flags,
                "rights_data": None,
                "message": "권리분석 데이터 없이 기본 평가 완료"
            }

        takeover_amount = RightsAnalyzer._to_float(rights.takeover_amount)
        lease_deposit = RightsAnalyzer._to_float(rights.lease_deposit)

        if rights.tenant_priority == "선순위":
            score -= 25
            flags.append("선순위 임차인 존재")

        if takeover_amount > 0:
            score -= 25
            flags.append("인수금액 발생")

        if lease_deposit > 0 and rights.tenant_priority == "선순위":
            score -= 10
            flags.append("선순위 보증금 확인 필요")

        if rights.base_right not in ["근저당", "압류", "가압류"]:
            score -= 10
            flags.append("말소기준권리 확인 필요")

        if rights.occupancy == "임차인":
            score -= 5
            flags.append("임차인 점유")

        if rights.eviction_level == "HIGH":
            score -= 15
            flags.append("명도 난이도 높음")
        elif rights.eviction_level == "VERY_HIGH":
            score -= 30
            flags.append("명도 난이도 매우 높음")

        return {
            "score": max(score, 0),
            "risk_level": RightsAnalyzer._risk_level(score),
            "flags": flags,
            "rights_data": {
                "base_right": rights.base_right,
                "tenant_priority": rights.tenant_priority,
                "lease_deposit": lease_deposit,
                "takeover_amount": takeover_amount,
                "occupancy": rights.occupancy,
                "eviction_level": rights.eviction_level,
                "comment": rights.comment,
            },
            "message": "DB 기반 권리분석 평가 완료"
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
