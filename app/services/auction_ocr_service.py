from pypdf import PdfReader

from app.models.auction_document import AuctionDocument


class AuctionOCRService:

    @staticmethod
    def extract_text_from_pdf(file_path: str):
        try:
            reader = PdfReader(file_path)
            texts = []

            for page in reader.pages:
                text = page.extract_text() or ""
                texts.append(text.strip())

            full_text = "\n\n".join(texts).strip()

            return {
                "success": True,
                "pages": len(reader.pages),
                "text": full_text,
            }

        except Exception as e:
            return {
                "success": False,
                "pages": 0,
                "text": "",
                "error": str(e),
            }

    @staticmethod
    def run_ocr(db, document_id: int):
        document = (
            db.query(AuctionDocument)
            .filter(AuctionDocument.id == document_id)
            .first()
        )

        if not document:
            return None

        result = AuctionOCRService.extract_text_from_pdf(
            document.file_path
        )

        if result.get("success"):
            document.pages = result.get("pages", 0)
            document.summary = result.get("text", "")[:5000]
            document.ocr_status = "DONE"
            document.analysis_status = "TEXT_READY"
        else:
            document.ocr_status = "FAILED"
            document.analysis_status = "FAILED"
            document.summary = result.get("error", "")

        db.commit()
        db.refresh(document)

        return {
            "document_id": document.id,
            "auction_id": document.auction_id,
            "file_name": document.file_name,
            "file_path": document.file_path,
            "pages": document.pages,
            "ocr_status": document.ocr_status,
            "analysis_status": document.analysis_status,
            "text_preview": (document.summary or "")[:500],
        }
