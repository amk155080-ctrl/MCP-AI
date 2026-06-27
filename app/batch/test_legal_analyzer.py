from app.services.rights.analyzers.legal import legal_analyzer


samples = [
    "특이한 법률 위험요소 없음",
    "본 건은 법정지상권 성립 여부 검토 대상입니다.",
    "유치권 신고가 있습니다.",
    "예고등기 및 가처분 존재",
    "가등기와 공유지분 매각 물건",
    "선순위 전세권 및 배당요구종기 확인 필요",
]


if __name__ == "__main__":
    print("=" * 60)
    print("MCP16 Legal Analyzer Test")
    print("=" * 60)

    for sample in samples:
        result = legal_analyzer.analyze(sample)

        print()
        print("TEXT:", sample)

        for key, value in result.items():
            print(f"{key}: {value}")