from pathlib import Path
import pytesseract
from pdf2image import convert_from_path

def parse_scanned_pdf(path: Path) -> dict:
    """OCR a scanned PDF. Requires Tesseract OCR and Poppler installed."""
    images = convert_from_path(str(path))
    pages = []
    for page_number, image in enumerate(images, start=1):
        text = pytesseract.image_to_string(image, lang="eng")
        pages.append({"page": page_number, "text": text})

    combined = "\\n\\n".join(
        f"[Page {p['page']}]\\n{p['text']}"
        for p in pages if p["text"].strip()
    )
    return {
        "text": combined,
        "pages": pages,
        "page_count": len(images),
        "parser": "tesseract_ocr",
    }
