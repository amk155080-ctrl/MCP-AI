from app.services.rights.engine_v2 import rights_engine_v2


samples = [
    """
    base_right:mortgage
    tenant_priority:none
    occupancy:owner
    """,
    """
    base_right:mortgage
    tenant_priority:senior
    occupancy:tenant
    보증금 1억2천만원
    """,
    """
    base_right:mortgage
    tenant_priority:none
    occupancy:owner
    유치권 신고
    가처분 존재
    """,
]


if __name__ == "__main__":
    print("=" * 60)
    print("MCP16 Rights Engine 2.0 Test")
    print("=" * 60)

    for idx, sample in enumerate(samples, start=1):
        print()
        print(f"CASE {idx}")

        result = rights_engine_v2.analyze(sample)

        for key in [
            "version",
            "base_right",
            "tenant_priority",
            "occupancy",
            "lease_deposit",
            "takeover_amount",
            "takeover_required",
            "legal_risk_count",
            "legal_risk_score",
            "rights_score",
            "risk_level",
            "recommendation",
            "summary",
        ]:
            print(f"{key}: {result.get(key)}")
