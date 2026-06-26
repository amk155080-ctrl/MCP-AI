from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.rights_ai_service import analyze_rights_by_document_id


router = APIRouter(
    prefix="/api/v16",
    tags=["MCP16 Rights Intelligence AI"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/rights-analysis/{document_id}")
def rights_analysis(
    document_id: int,
    db: Session = Depends(get_db)
):
    return analyze_rights_by_document_id(
        db=db,
        document_id=document_id
    )


@router.get("/rights-analysis/{document_id}")
def get_rights_analysis(
    document_id: int,
    db: Session = Depends(get_db)
):
    return analyze_rights_by_document_id(
        db=db,
        document_id=document_id
    )
