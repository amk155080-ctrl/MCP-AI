from app.services.rights_parser import parse_rights_from_text


sample_text = """
말소기준권리 근저당권 2021.03.15
임차인 홍길동
보증금 120,000,000원
전입신고 2020.12.20
확정일자 2020.12.21
배당요구 있음
현재 점유중
"""


if __name__ == "__main__":
    result = parse_rights_from_text(sample_text)

    print("=" * 60)
    print("MCP16.3 Rights Parser Test")
    print("=" * 60)

    for key, value in result.items():
        print(f"{key}: {value}")
