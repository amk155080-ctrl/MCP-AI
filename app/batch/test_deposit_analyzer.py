from app.services.rights.analyzers.deposit import deposit_analyzer


samples = [
    "보증금 120,000,000원",
    "임대차보증금: 85,000,000원",
    "전세금 1억",
    "보증금 1억2천만원",
    "보증금 8천만원",
    "deposit:85000000",
    "보증금 없음",
]


if __name__ == "__main__":
    print("=" * 60)
    print("MCP16 Deposit Analyzer Test")
    print("=" * 60)

    for sample in samples:
        result = deposit_analyzer.analyze(sample)

        print()
        print("TEXT:", sample)

        for key, value in result.items():
            print(f"{key}: {value}")
