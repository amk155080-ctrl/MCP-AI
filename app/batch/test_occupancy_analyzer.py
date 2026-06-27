from app.services.rights.analyzers.occupancy import occupancy_analyzer


samples = [
    "occupancy:owner",
    "occupancy:tenant",
    "occupancy:debtor",
    "occupancy:third",
    "현재 공실 상태입니다.",
    "점유자 관련 내용 없음",
]


if __name__ == "__main__":
    print("=" * 60)
    print("MCP16 Occupancy Analyzer Test")
    print("=" * 60)

    for sample in samples:
        result = occupancy_analyzer.analyze(sample)

        print()
        print("TEXT:", sample)

        for key, value in result.items():
            print(f"{key}: {value}")