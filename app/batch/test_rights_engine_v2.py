from app.services.rights_engine_v2.engine_v2 import analyze


def run():
    print("=" * 60)
    print("MCP16 Rights Engine 2.0 Test")
    print("=" * 60)

    cases = [
        "본 부동산은 근저당이 설정되어 있으며 임차인 없음. 소유자 점유 상태입니다.",
        "전입신고가 있는 임차인이 있으며 배당요구 없음. 유치권 주장 가능성이 있습니다.",
        "가압류와 근저당이 존재하고 점유자 확인 필요. 체납 내역이 있습니다.",
    ]

    for idx, text in enumerate(cases, start=1):
        print()
        print(f"CASE {idx}")
        result = analyze(text)

        for key, value in result.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    run()
