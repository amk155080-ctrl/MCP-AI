ocr_text = (
    getattr(document, "ocr_text", None)
    or getattr(document, "pdf_text", None)
    or getattr(document, "extracted_text", None)
    or getattr(document, "text", None)
    or getattr(document, "content", None)
)

if not ocr_text:
    return {
        "found": False,
        "version": "MCP 16.3",
        "message": "OCR text is empty or text column not found",
        "document_id": document_id,
        "ocr_status": document.ocr_status,
        "analysis_status": document.analysis_status,
    }

parsed = parse_rights_from_text(ocr_text)
