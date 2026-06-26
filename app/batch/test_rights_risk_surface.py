from app.services.rights_engine import rights_engine
from app.services.rights_risk import rights_risk_engine


sample = """
Auction Document Test

case_number:202610005

base_right:mortgage
tenant_priority:none
occupancy:owner

본 건은 법정지상권 성립 여부 검토 대상임.
"""


rights = rights_engine.analyze(sample)
risk = rights_risk_engine.calculate(rights)

print("=" * 60)
print("Rights Engine Result")
print("=" * 60)

for k, v in rights.items():
    print(f"{k}: {v}")

print()
print("=" * 60)
print("Risk Engine Result")
print("=" * 60)

for k, v in risk.items():
    print(f"{k}: {v}")
