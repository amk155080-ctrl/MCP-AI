from app.core.database import Base
from app.core.database import engine

from app.models.auction_asset import AuctionAsset


def main():
    Base.metadata.create_all(bind=engine)

    print(
        "MCP 15.2 auction_asset table created successfully"
    )


if __name__ == "__main__":
    main()
