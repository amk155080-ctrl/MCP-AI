from app.services.rights.analyzers.registry import analyzer_registry

sample = """
Auction Document Test

case_number: 2026타경10005

base_right:mortgage
tenant_priority:none
occupancy:owner
"""


if __name__ == "__main__":
    result = analyzer_registry.analyze_all(sample)

    print("=" * 60)
    print("MCP16 Analyzer Registry Test")
    print("=" * 60)

    print("version:", result["version"])

    for name, value in result["analyzers"].items():
        print()
        print(f"[{name}]")
        for key, item in value.items():
            print(f"{key}: {item}")
