from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from fastapi.responses import HTMLResponse


router = APIRouter(
    prefix="/api/v19/cases",
    tags=["MCP19 Auction Cases"],
)


@router.post("/create")
def create_auction_case(
    document_id: int = None,
    auction_id: int = None,
    case_no: str = "",
    court_name: str = "",
    property_address: str = "",
    property_type: str = "",
    appraisal_price: int = 0,
    minimum_bid_price: int = 0,
    expected_sale_price: int = 0,
    status: str = "WATCH",
    memo: str = "",
    db: Session = Depends(get_db),
):
    saved = db.execute(
        text("""
            INSERT INTO auction_cases (
                document_id,
                auction_id,
                case_no,
                court_name,
                property_address,
                property_type,
                appraisal_price,
                minimum_bid_price,
                expected_sale_price,
                status,
                memo
            )
            VALUES (
                :document_id,
                :auction_id,
                :case_no,
                :court_name,
                :property_address,
                :property_type,
                :appraisal_price,
                :minimum_bid_price,
                :expected_sale_price,
                :status,
                :memo
            )
            RETURNING id
        """),
        {
            "document_id": document_id,
            "auction_id": auction_id,
            "case_no": case_no,
            "court_name": court_name,
            "property_address": property_address,
            "property_type": property_type,
            "appraisal_price": appraisal_price,
            "minimum_bid_price": minimum_bid_price,
            "expected_sale_price": expected_sale_price,
            "status": status,
            "memo": memo,
        },
    )

    case_id = saved.scalar()
    db.commit()

    return {
        "found": True,
        "version": "MCP 19.2",
        "case_id": case_id,
        "message": "경매 후보 물건 등록 완료",
    }

@router.get("")
def list_auction_cases(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    rows = db.execute(
        text("""
            SELECT *
            FROM auction_cases
            ORDER BY created_at DESC, id DESC
            LIMIT :limit
        """),
        {"limit": limit},
    ).mappings().all()

    return {
        "found": True,
        "version": "MCP 19.3",
        "count": len(rows),
        "items": [dict(row) for row in rows],
        "message": "경매 후보 물건 목록 조회 완료",
    }


@router.get("/{case_id}")
def get_auction_case(
    case_id: int,
    db: Session = Depends(get_db),
):
    row = db.execute(
        text("""
            SELECT *
            FROM auction_cases
            WHERE id = :case_id
        """),
        {"case_id": case_id},
    ).mappings().first()

    if not row:
        return {
            "found": False,
            "version": "MCP 19.3",
            "case_id": case_id,
            "message": "경매 후보 물건을 찾을 수 없습니다.",
        }

    return {
        "found": True,
        "version": "MCP 19.3",
        "case": dict(row),
        "message": "경매 후보 물건 상세 조회 완료",
    }


@router.get("/document/{document_id}")
def get_auction_case_by_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    row = db.execute(
        text("""
            SELECT *
            FROM auction_cases
            WHERE document_id = :document_id
            ORDER BY created_at DESC, id DESC
            LIMIT 1
        """),
        {"document_id": document_id},
    ).mappings().first()

    if not row:
        return {
            "found": False,
            "version": "MCP 19.3",
            "document_id": document_id,
            "message": "document_id에 해당하는 후보 물건이 없습니다.",
        }

    return {
        "found": True,
        "version": "MCP 19.3",
        "case": dict(row),
        "message": "document_id 기반 후보 물건 조회 완료",
    }
@router.put("/{case_id}/status")
def update_case_status(
    case_id: int,
    status: str,
    memo: str = "",
    db: Session = Depends(get_db),
):
    row = db.execute(
        text("""
            SELECT id
            FROM auction_cases
            WHERE id=:case_id
        """),
        {"case_id": case_id},
    ).first()

    if not row:
        return {
            "found": False,
            "version": "MCP 19.4",
            "case_id": case_id,
            "message": "후보 물건을 찾을 수 없습니다.",
        }

    db.execute(
        text("""
            UPDATE auction_cases
            SET
                status=:status,
                memo=:memo,
                updated_at=NOW()
            WHERE id=:case_id
        """),
        {
            "case_id": case_id,
            "status": status,
            "memo": memo,
        },
    )

    db.commit()

    updated = db.execute(
        text("""
            SELECT *
            FROM auction_cases
            WHERE id=:case_id
        """),
        {"case_id": case_id},
    ).mappings().first()

    return {
        "found": True,
        "version": "MCP 19.4",
        "case": dict(updated),
        "message": "후보 물건 상태 변경 완료",
    }
@router.get("/portfolio/summary")
def auction_case_portfolio_summary(
    db: Session = Depends(get_db),
):
    total = db.execute(
        text("""
            SELECT COUNT(*) AS count
            FROM auction_cases
        """)
    ).mappings().first()

    status_stats = db.execute(
        text("""
            SELECT status, COUNT(*) AS count
            FROM auction_cases
            GROUP BY status
            ORDER BY count DESC
        """)
    ).mappings().all()

    return {
        "found": True,
        "version": "MCP 19.5",
        "total_count": total.get("count") if total else 0,
        "status_stats": [dict(row) for row in status_stats],
        "message": "경매 후보 물건 포트폴리오 요약 조회 완료",
    }


@router.get("/portfolio/by-status/{status}")
def auction_cases_by_status(
    status: str,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    rows = db.execute(
        text("""
            SELECT *
            FROM auction_cases
            WHERE status = :status
            ORDER BY updated_at DESC, id DESC
            LIMIT :limit
        """),
        {
            "status": status,
            "limit": limit,
        },
    ).mappings().all()

    return {
        "found": True,
        "version": "MCP 19.5",
        "status": status,
        "count": len(rows),
        "items": [dict(row) for row in rows],
        "message": "상태별 경매 후보 물건 조회 완료",
    }


@router.get("/portfolio/ranking")
def auction_case_portfolio_ranking(
    sort_by: str = "auction_score",
    limit: int = 20,
    db: Session = Depends(get_db),
):
    allowed_sort = {
        "auction_score": "d.auction_score",
        "expected_roi": "d.expected_roi",
        "expected_profit": "d.expected_profit",
        "rights_score": "d.rights_score",
        "recommended_bid": "d.recommended_bid",
    }

    order_column = allowed_sort.get(sort_by, "d.auction_score")

    rows = db.execute(
        text(f"""
            SELECT
                c.id AS case_id,
                c.document_id,
                c.auction_id,
                c.case_no,
                c.court_name,
                c.property_address,
                c.property_type,
                c.status,
                c.memo,
                c.appraisal_price,
                c.minimum_bid_price,
                c.expected_sale_price,

                d.id AS decision_result_id,
                d.auction_score,
                d.rights_score,
                d.profit_score,
                d.risk_score,
                d.confidence,
                d.decision,
                d.recommended_bid,
                d.expected_profit,
                d.expected_roi,
                d.created_at AS decision_created_at

            FROM auction_cases c
            LEFT JOIN auction_decision_results d
                ON c.document_id = d.document_id
            WHERE d.id IS NOT NULL
            ORDER BY {order_column} DESC, d.created_at DESC
            LIMIT :limit
        """),
        {"limit": limit},
    ).mappings().all()

    return {
        "found": True,
        "version": "MCP 19.5",
        "sort_by": sort_by,
        "count": len(rows),
        "items": [dict(row) for row in rows],
        "message": "경매 후보 물건 포트폴리오 랭킹 조회 완료",
    }
@router.get("/{case_id}/integrated-report")
def get_case_integrated_report(
    case_id: int,
    db: Session = Depends(get_db),
):
    case_row = db.execute(
        text("""
            SELECT *
            FROM auction_cases
            WHERE id = :case_id
        """),
        {"case_id": case_id},
    ).mappings().first()

    if not case_row:
        return {
            "found": False,
            "version": "MCP 19.6",
            "case_id": case_id,
            "message": "후보 물건을 찾을 수 없습니다.",
        }

    case = dict(case_row)
    document_id = case.get("document_id")

    if not document_id:
        return {
            "found": False,
            "version": "MCP 19.6",
            "case_id": case_id,
            "message": "후보 물건에 document_id가 연결되어 있지 않습니다.",
        }

    rights_row = db.execute(
        text("""
            SELECT *
            FROM rights_v2_results
            WHERE document_id = :document_id
            ORDER BY created_at DESC, id DESC
            LIMIT 1
        """),
        {"document_id": document_id},
    ).mappings().first()

    decision_row = db.execute(
        text("""
            SELECT *
            FROM auction_decision_results
            WHERE document_id = :document_id
            ORDER BY created_at DESC, id DESC
            LIMIT 1
        """),
        {"document_id": document_id},
    ).mappings().first()

    if not rights_row or not decision_row:
        return {
            "found": False,
            "version": "MCP 19.6",
            "case_id": case_id,
            "document_id": document_id,
            "message": "MCP16 또는 MCP17 분석 결과가 부족합니다.",
        }

    rights = dict(rights_row)
    decision = dict(decision_row)

    return {
        "found": True,
        "version": "MCP 19.6",
        "case": case,
        "rights": {
            "rights_result_id": rights.get("id"),
            "rights_score": rights.get("rights_score"),
            "risk_level": rights.get("risk_level"),
            "recommendation": rights.get("recommendation"),
            "summary": rights.get("summary"),
        },
        "decision": {
            "decision_result_id": decision.get("id"),
            "auction_score": decision.get("auction_score"),
            "decision": decision.get("decision"),
            "recommended_bid": decision.get("recommended_bid"),
            "expected_profit": decision.get("expected_profit"),
            "expected_roi": decision.get("expected_roi"),
            "summary": decision.get("summary"),
        },
        "summary": (
            f"{case.get('case_no')} 후보 물건은 "
            f"권리점수 {rights.get('rights_score')}점, "
            f"경매 종합점수 {decision.get('auction_score')}점입니다. "
            f"최종 판단은 {decision.get('decision')}이며, "
            f"추천 입찰가는 {decision.get('recommended_bid'):,}원입니다."
        ),
        "message": "후보 물건 통합 리포트 조회 완료",
    }

def _build_case_dashboard_html(data: dict) -> str:
    case = data["case"]
    rights = data["rights"]
    decision = data["decision"]

    return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>MCP19 Auction Case Dashboard</title>
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 40px;
    background: #f5f5f5;
}}
.container {{
    background: white;
    padding: 30px;
    border-radius: 10px;
}}
.section {{
    margin-top: 25px;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
}}
.score {{
    font-size: 34px;
    color: #1976d2;
    font-weight: bold;
}}
table {{
    width: 100%;
    border-collapse: collapse;
}}
td {{
    padding: 8px;
    border-bottom: 1px solid #eee;
}}
.summary {{
    background: #fafafa;
    padding: 20px;
    line-height: 1.7;
}}
</style>
</head>
<body>
<div class="container">

<h1>MCP19 경매 후보 물건 Dashboard</h1>

<div class="section">
<h2>후보 물건 정보</h2>
<table>
<tr><td>사건번호</td><td>{case["case_no"]}</td></tr>
<tr><td>법원</td><td>{case["court_name"]}</td></tr>
<tr><td>주소</td><td>{case["property_address"]}</td></tr>
<tr><td>물건종류</td><td>{case["property_type"]}</td></tr>
<tr><td>상태</td><td>{case["status"]}</td></tr>
<tr><td>메모</td><td>{case["memo"]}</td></tr>
</table>
</div>

<div class="section">
<h2>가격 정보</h2>
<table>
<tr><td>감정가</td><td>{case["appraisal_price"]:,} 원</td></tr>
<tr><td>최저입찰가</td><td>{case["minimum_bid_price"]:,} 원</td></tr>
<tr><td>예상 매각가</td><td>{case["expected_sale_price"]:,} 원</td></tr>
</table>
</div>

<div class="section">
<h2>권리분석</h2>
<div class="score">{rights["rights_score"]} 점</div>
<table>
<tr><td>위험등급</td><td>{rights["risk_level"]}</td></tr>
<tr><td>추천</td><td>{rights["recommendation"]}</td></tr>
</table>
<p>{rights["summary"]}</p>
</div>

<div class="section">
<h2>경매 종합판정</h2>
<div class="score">{decision["auction_score"]} 점</div>
<table>
<tr><td>최종판단</td><td>{decision["decision"]}</td></tr>
<tr><td>추천 입찰가</td><td>{decision["recommended_bid"]:,} 원</td></tr>
<tr><td>예상 수익</td><td>{decision["expected_profit"]:,} 원</td></tr>
<tr><td>예상 수익률</td><td>{decision["expected_roi"]}%</td></tr>
</table>
<p>{decision["summary"]}</p>
</div>

<div class="section summary">
<h2>AI 통합 요약</h2>
<p>{data["summary"]}</p>
</div>

</div>
</body>
</html>
"""

@router.get("/{case_id}/dashboard/html", response_class=HTMLResponse)
def case_dashboard_html(
    case_id: int,
    db: Session = Depends(get_db),
):
    response = get_case_integrated_report(
        case_id=case_id,
        db=db,
    )

    if not response["found"]:
        return HTMLResponse(
            "<h1>Case Dashboard Not Found</h1>",
            status_code=404,
        )

    html = _build_case_dashboard_html(response)

    return HTMLResponse(html)
