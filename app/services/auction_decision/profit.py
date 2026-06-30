def calculate_profit(
    expected_sale_price: int,
    bid_price: int,
    repair_cost: int = 0,
    eviction_cost: int = 0,
    tax_cost: int = 0,
    etc_cost: int = 0,
) -> dict:
    total_cost = bid_price + repair_cost + eviction_cost + tax_cost + etc_cost
    expected_profit = expected_sale_price - total_cost

    if total_cost > 0:
        expected_roi = round((expected_profit / total_cost) * 100, 2)
    else:
        expected_roi = 0

    return {
        "expected_sale_price": expected_sale_price,
        "bid_price": bid_price,
        "repair_cost": repair_cost,
        "eviction_cost": eviction_cost,
        "tax_cost": tax_cost,
        "etc_cost": etc_cost,
        "total_cost": total_cost,
        "expected_profit": expected_profit,
        "expected_roi": expected_roi,
    }
