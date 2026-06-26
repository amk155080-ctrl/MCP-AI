from app.services.rights_engine import rights_engine


sample = """
Auction Document Test

case_number:202610005

base_right: mortgage

tenant_priority:none

occupancy:owner
"""

result = rights_engine.analyze(sample)

print("=" * 60)
print("MCP16.4 Rights Engine")
print("=" * 60)

for k, v in result.items():
    print(f"{k}: {v}")
