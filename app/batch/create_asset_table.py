from app.core.database import engine, Base
from app.models.asset import AssetAccount


def main():
    Base.metadata.create_all(bind=engine)
    print("MCP 14 asset_account table created successfully")


if __name__ == "__main__":
    main()
