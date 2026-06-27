from app.services.rights.analyzers.takeover import takeover_analyzer


samples = [
    {
        "name": "임차인 없음",
        "context": {
            "TenantAnalyzer": {
                "tenant_priority": "임차인 없음"
            },
            "DepositAnalyzer": {
                "lease_deposit": 0
            }
        }
    },
    {
        "name": "선순위 임차인 + 보증금",
        "context": {
            "TenantAnalyzer": {
                "tenant_priority": "선순위 임차인 가능성 있음"
            },
            "DepositAnalyzer": {
                "lease_deposit": 120000000
            }
        }
    },
    {
        "name": "대항력 가능성 + 보증금",
        "context": {
            "TenantAnalyzer": {
                "tenant_priority": "대항력 가능성 있음"
            },
            "DepositAnalyzer": {
                "lease_deposit": 80000000
            }
        }
    },
    {
        "name": "후순위 임차인",
        "context": {
            "TenantAnalyzer": {
                "tenant_priority": "후순위 임차인 가능성 있음"
            },
            "DepositAnalyzer": {
                "lease_deposit": 50000000
            }
        }
    },
]


if __name__ == "__main__":
    print("=" * 60)
    print("MCP16 Takeover Analyzer Test")
    print("=" * 60)

    for sample in samples:
        print()
        print("CASE:", sample["name"])

        result = takeover_analyzer.analyze(
            text="",
            context=sample["context"]
        )

        for key, value in result.items():
            print(f"{key}: {value}")
