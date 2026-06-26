from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/")
def root():
    return {"system": "MCP 4.0 v1", "status": "running"}
