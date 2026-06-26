from app.core.database import SessionLocal
from app.services.rights_ai_service import analyze_rights_by_document_id


DOCUMENT_ID = 2


if __name__ == "__main__":
    db = SessionLocal()

    try:
        result = analyze_rights_by_document_id(
            db=db,
            document_id=DOCUMENT_ID
        )

        print("=" * 60)
        print("MCP16.3 Rights AI Service Test")
        print("=" * 60)

        for key, value in result.items():
            print(f"{key}: {value}")

    finally:
        db.close()
