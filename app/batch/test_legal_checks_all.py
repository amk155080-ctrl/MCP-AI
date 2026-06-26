from app.services.legal_checks import run_all_legal_checks


sample = """
base_right:mortgage
tenant_priority:none
occupancy:owner

본 건은 법정지상권 검토 대상이며,
유치권 신고가 있고,
가처분 및 가등기 가능성이 있음.
공유지분 매각 물건.
"""


result = run_all_legal_checks(sample)

print("=" * 60)
print("MCP16.4 Legal Checks All Test")
print("=" * 60)

for key, value in result.items():
    print(f"{key}: {value}")
