def build_rights_summary(result: dict) -> str:
    return (
        f"말소기준권리는 {result.get('base_right')}입니다. "
        f"임차인 권리상태는 {result.get('tenant_priority')}입니다. "
        f"점유상태는 {result.get('occupancy')}입니다. "
        f"예상 인수금액은 {result.get('takeover_amount', 0):,}원입니다. "
        f"특이 법률 위험요소는 {result.get('legal_risk_count', 0)}건 감지되었습니다. "
        f"권리점수는 {result.get('rights_score')}점이며 "
        f"위험등급은 {result.get('risk_level')}입니다."
    )
