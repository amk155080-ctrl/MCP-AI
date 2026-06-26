import csv
import io
import openpyxl

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auction_import_service import AuctionImportService


router = APIRouter(
    prefix="/api/v15/auction/import",
    tags=["MCP 15 Auction Import Engine"]
)


@router.post("/items")
def import_auction_items(
    items: list,
    db: Session = Depends(get_db),
):
    result = AuctionImportService.import_items(db, items)

    return {
        "found": True,
        "version": "MCP 15.15",
        "import_result": result,
        "message": "경매 물건 리스트 Import 완료",
    }


@router.post("/csv")
async def import_auction_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    content = await file.read()
    text = content.decode("utf-8-sig")

    reader = csv.DictReader(io.StringIO(text))
    items = [row for row in reader]

    result = AuctionImportService.import_items(db, items)

    return {
        "found": True,
        "version": "MCP 15.15",
        "filename": file.filename,
        "row_count": len(items),
        "import_result": result,
        "message": "CSV 경매 데이터 Import 완료",
    }

@router.post("/excel")
async def import_auction_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    content = await file.read()

    workbook = openpyxl.load_workbook(
        io.BytesIO(content),
        data_only=True
    )

    sheet = workbook.active

    rows = list(sheet.iter_rows(values_only=True))

    if not rows:
        return {
            "found": False,
            "version": "MCP 15.15-2",
            "message": "엑셀 파일에 데이터가 없습니다.",
        }

    headers = [
        str(h).strip() if h is not None else ""
        for h in rows[0]
    ]

    items = []

    for row in rows[1:]:
        item = {}

        for idx, header in enumerate(headers):
            if not header:
                continue

            value = row[idx] if idx < len(row) else None
            item[header] = value

        items.append(item)

    result = AuctionImportService.import_items(db, items)

    return {
        "found": True,
        "version": "MCP 15.15-2",
        "filename": file.filename,
        "row_count": len(items),
        "import_result": result,
        "message": "Excel 경매 데이터 Import 완료",
    }
