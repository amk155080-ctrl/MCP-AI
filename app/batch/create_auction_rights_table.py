from app.core.database import Base, engine
from app.models.auction_rights import AuctionRights


def main():
    Base.metadata.create_all(bind=engine)
    print("MCP 15.13 auction_rights table created")


if __name__ == "__main__":
    main()
