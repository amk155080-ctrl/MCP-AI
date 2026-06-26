from fastapi import APIRouter
from app.core.kis_token import get_kis_access_token

router = APIRouter(
    prefix="/api/v11/kis",
    tags=["MCP 11.0 KIS Auth"]
)


@router.get("/token")
def issue_kis_token():
    result = get_kis_access_token()

    if not result.get("found"):
        return {
            "found": False,
            "version": "MCP 11.0.1",
            "message": "KIS 접근토큰 발급 실패",
            "response": result
        }

    token = result.get("access_token")

    return {
        "found": True,
        "version": "MCP 11.0.1",
        "token_type": "Bearer",
        "access_token_preview": token[:20] + "..." if token else None,
        "cached": result.get("cached"),
        "expired_at": result.get("expired_at"),
        "message": "KIS 접근토큰 준비 완료"
    }
