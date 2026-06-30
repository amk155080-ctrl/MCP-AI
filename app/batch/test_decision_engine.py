from app.services.auction_decision.engine import analyze_auction_decision


def run():
    print("=" * 60)
    print("MCP17 Auction Decision Engine Test")
    print("=" * 60)

    result = analyze_auction_decision(
        appraisal_price=300_000_000,
        minimum_bid_price=210_000_000,
        expected_sale_price=320_000_000,
        rights_score=80,
        takeover_amount=0,
        repair_cost=10_000_000,
        eviction_cost=5_000_000,
        tax_cost=8_000_000,
        etc_cost=3_000_000,
        target_roi=15.0,
    )

    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    run()
