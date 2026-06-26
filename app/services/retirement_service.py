class RetirementService:

    @staticmethod
    def simulate(
        current_asset: float,
        annual_return: float,
        years: int
    ):

        future_asset = (
            current_asset
            * ((1 + annual_return) ** years)
        )

        target_asset = 1000000000

        return {
            "current_asset": current_asset,
            "future_asset": round(future_asset),
            "target_asset": target_asset,
            "retirement_ok":
                future_asset >= target_asset,
            "annual_return":
                annual_return,
            "years":
                years
        }
