from pathlib import Path
from pypdf import PdfReader

def parse_pdf(path: Path) -> dict:
    """Extract selectable text from a PDF, preserving page numbers."""
    reader = PdfReader(str(path))
    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append({"page": page_number, "text": text})

    combined = "\\n\\n".join(
        f"[Page {p['page']}]\\n{p['text']}"
        for p in pages if p["text"].strip()
    )
    return {
        "text": combined,
        "pages": pages,
        "page_count": len(reader.pages),
        "parser": "pypdf",
    }
