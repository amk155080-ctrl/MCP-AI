from app.core.database import Base
from app.core.database import engine

from app.models.family_asset import FamilyAsset


def main():
    Base.metadata.create_all(bind=engine)

    print(
        "MCP 15.0 family_asset table created successfully"
    )


if __name__ == "__main__":
    main()

