from app.services.rights.analyzers.base_right import base_right_analyzer


samples = [
    "base_right:mortgage",
    "근저당권 설정",
    "가압류 등기",
    "강제경매개시결정",
    "특별한 권리 문구 없음",
]


if __name__ == "__main__":
    print("=" * 60)
    print("MCP16 BaseRight Analyzer Test")
    print("=" * 60)

    for sample in samples:
        result = base_right_analyzer.analyze(sample)
        print()
        print("TEXT:", sample)
        for key, value in result.items():
            print(f"{key}: {value}")
