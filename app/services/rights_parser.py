import re
from typing import Dict, Any


PARSER_VERSION = "MCP16.3-RIGHTS-PARSER-1.2"


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def parse_money_to_number(value: str) -> float:
    if not value:
        return 0.0

    value = value.replace(",", "")
    numbers = re.findall(r"\d+", value)

    if not numbers:
        return 0.0

    return float("".join(numbers))


def extract_lease_deposit(text: str) -> float:
    lower_text = text.lower()

    patterns = [
        r"보증금\s*[:：]?\s*([0-9,]+)\s*원",
        r"임대차보증금\s*[:：]?\s*([0-9,]+)\s*원",
        r"전세금\s*[:：]?\s*([0-9,]+)\s*원",
        r"lease_deposit\s*[:：]?\s*([0-9,]+)",
        r"deposit\s*[:：]?\s*([0-9,]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, lower_text)
        if match:
            return parse_money_to_number(match.group(1))

    return 0.0


def extract_base_right(text: str) -> str:
    lower_text = text.lower()

    if re.search(r"base_right\s*:\s*mortgage", lower_text):
        return "근저당"

    if "mortgage" in lower_text:
        return "근저당"

    if re.search(r"base_right\s*:\s*seizure", lower_text):
        return "압류"

    if re.search(r"base_right\s*:\s*provisional_seizure", lower_text):
        return "가압류"

    if re.search(r"base_right\s*:\s*auction_start", lower_text):
        return "경매개시결정"

    if "근저당권" in text or "근저당" in text:
        return "근저당"

    if "저당권" in text:
        return "저당권"

    if "가압류" in text:
        return "가압류"

    if "압류" in text:
        return "압류"

    if "담보가등기" in text:
        return "담보가등기"

    if "강제경매개시결정" in text:
        return "강제경매개시결정"

    if "임의경매개시결정" in text:
        return "임의경매개시결정"

    if "경매개시결정" in text:
        return "경매개시결정"

    return "미확인"


def has_tenant(text: str) -> bool:
    lower_text = text.lower()

    english_keywords = [
        "tenant",
        "tenant_priority",
        "lease",
        "deposit",
    ]

    korean_keywords = [
        "임차인",
        "세입자",
        "전입",
        "확정일자",
        "배당요구",
        "임대차",
        "보증금",
    ]

    for keyword in english_keywords:
        if keyword in lower_text:
            return True

    for keyword in korean_keywords:
        if keyword in text:
            return True

    return False


def extract_tenant_priority(text: str) -> str:
    lower_text = text.lower()

    if re.search(r"tenant_priority\s*:\s*none", lower_text):
        return "임차인 없음"

    if re.search(r"tenant_priority\s*:\s*senior", lower_text):
        return "선순위 임차인 가능성 있음"

    if re.search(r"tenant_priority\s*:\s*junior", lower_text):
        return "후순위 임차인 가능성 있음"

    if re.search(r"tenant_priority\s*:\s*unknown", lower_text):
        return "임차인 권리 미확인"

    if not has_tenant(text):
        return "임차인 미확인"

    has_move_in = "전입" in text or "전입신고" in text
    has_fixed_date = "확정일자" in text
    has_distribution = "배당요구" in text

    if has_move_in and has_fixed_date and has_distribution:
        return "대항력 및 우선변제 가능성 있음"

    if has_move_in and has_fixed_date:
        return "대항력 가능성 있음"

    if has_move_in:
        return "대항력 검토 필요"

    if "임차인" in text or "보증금" in text:
        return "임차인 있음 / 대항력 미확인"

    return "임차인 미확인"


def extract_occupancy(text: str) -> str:
    lower_text = text.lower()

    if re.search(r"occupancy\s*:\s*owner", lower_text):
        return "소유자 점유"

    if re.search(r"occupancy\s*:\s*tenant", lower_text):
        return "임차인 점유"

    if re.search(r"occupancy\s*:\s*vacant", lower_text):
        return "공실"

    if re.search(r"occupancy\s*:\s*unknown", lower_text):
        return "점유 미확인"

    vacant_keywords = [
        "공실",
        "미점유",
        "폐문",
        "점유자 없음",
        "현황 공실",
    ]

    occupied_keywords = [
        "점유",
        "점유중",
        "거주",
        "거주중",
        "임차인",
        "세입자",
        "전입",
    ]

    for keyword in vacant_keywords:
        if keyword in text:
            return "공실 또는 미점유 가능성"

    for keyword in occupied_keywords:
        if keyword in text:
            return "점유중"

    return "미확인"


def calculate_takeover_amount(
    tenant_priority: str,
    lease_deposit: float
) -> float:
    if lease_deposit <= 0:
        return 0.0

    risk_keywords = [
        "대항력",
        "선순위",
        "우선변제",
    ]

    for keyword in risk_keywords:
        if keyword in tenant_priority:
            return lease_deposit

    return 0.0


def calculate_confidence(
    base_right: str,
    tenant_priority: str,
    occupancy: str,
    lease_deposit: float
) -> float:
    score = 50.0

    if base_right != "미확인":
        score += 15.0

    if tenant_priority not in ["임차인 미확인", "임차인 권리 미확인"]:
        score += 15.0

    if occupancy not in ["미확인", "점유 미확인"]:
        score += 10.0

    if lease_deposit > 0:
        score += 10.0

    return min(score, 98.0)


def make_summary(
    base_right: str,
    tenant_priority: str,
    occupancy: str,
    lease_deposit: float,
    takeover_amount: float,
    confidence: float
) -> str:
    return (
        f"말소기준권리: {base_right}, "
        f"임차인 권리상태: {tenant_priority}, "
        f"점유상태: {occupancy}, "
        f"보증금: {int(lease_deposit):,}원, "
        f"예상 인수금액: {int(takeover_amount):,}원, "
        f"AI 신뢰도: {confidence}%"
    )


def parse_rights_from_text(ocr_text: str) -> Dict[str, Any]:
    text = normalize_text(ocr_text)

    base_right = extract_base_right(text)
    tenant_priority = extract_tenant_priority(text)
    occupancy = extract_occupancy(text)
    lease_deposit = extract_lease_deposit(text)

    takeover_amount = calculate_takeover_amount(
        tenant_priority=tenant_priority,
        lease_deposit=lease_deposit
    )

    confidence = calculate_confidence(
        base_right=base_right,
        tenant_priority=tenant_priority,
        occupancy=occupancy,
        lease_deposit=lease_deposit
    )

    raw_summary = make_summary(
        base_right=base_right,
        tenant_priority=tenant_priority,
        occupancy=occupancy,
        lease_deposit=lease_deposit,
        takeover_amount=takeover_amount,
        confidence=confidence
    )

    return {
        "base_right": base_right,
        "tenant_priority": tenant_priority,
        "occupancy": occupancy,
        "lease_deposit": lease_deposit,
        "takeover_amount": takeover_amount,
        "confidence": confidence,
        "parser_version": PARSER_VERSION,
        "raw_summary": raw_summary,
    }
