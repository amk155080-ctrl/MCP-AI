from app.services.rights.analyzers.tenant import tenant_analyzer


samples = [
    "tenant_priority:none",
    "tenant_priority:senior",
    "tenant_priority:junior",
    """
    임차인 홍길동
    보증금 120,000,000원
    전입신고 2020.12.20
    확정일자 2020.12.21
    배당요구 있음
    """,
    """
    임차인 김철수
    보증금 80,000,000원
    전입신고 2021.01.15
    """,
    "특별한 임차인 문구 없음",
]


if __name__ == "__main__":
    print("=" * 60)
    print("MCP16 Tenant Analyzer Test")
    print("=" * 60)

    for sample in samples:
        result = tenant_analyzer.analyze(sample)
        print()
        print("TEXT:", sample.strip())
        for key, value in result.items():
            print(f"{key}: {value}")
