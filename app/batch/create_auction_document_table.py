from app.core.database import Base
from app.core.database import engine

from app.models.auction_document import AuctionDocument


def main():
    Base.metadata.create_all(bind=engine)

    print("MCP 16.1 auction_document table created successfully")


if __name__ == "__main__":
    main()

