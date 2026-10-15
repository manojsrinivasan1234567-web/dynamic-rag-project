from pathlib import Path
from app.parsing.pdf_parser import parse_pdf
from app.parsing.ocr_parser import parse_scanned_pdf

def parse_document(path: Path, force_ocr: bool = False) -> dict:
    """Extract embedded PDF text; automatically use OCR if no text is found."""
    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    if force_ocr:
        return parse_scanned_pdf(path)

    result = parse_pdf(path)
    if not result["text"].strip():
        return parse_scanned_pdf(path)
    return result
