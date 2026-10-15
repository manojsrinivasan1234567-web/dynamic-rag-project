import json
from pathlib import Path
from app.config import PROCESSED_DIR
from app.ingestion.document_classifier import classify_document
from app.parsing.parser_factory import parse_document
from app.chunking.chunking_factory import create_chunks
from app.vectorstore.vector_database import vector_db

def process_document(filename: str, path: Path, force_ocr: bool = False,
                     min_words: int = 80, max_words: int = 180,
                     overlap_words: int = 30) -> dict:
    parsed = parse_document(path, force_ocr=force_ocr)
    text = parsed["text"]
    if not text.strip():
        raise ValueError("No text was extracted. Check the PDF or OCR installation.")

    classification = classify_document(text)
    chunks = create_chunks(
        text=text,
        document_type=classification["category"],
        min_words=min_words,
        max_words=max_words,
        overlap_words=overlap_words,
    )
    if not chunks:
        raise ValueError("No chunks were created from this document.")

    vector_db.upsert_document(filename, chunks)

    result = {
        "filename": filename,
        "parser": parsed["parser"],
        "page_count": parsed["page_count"],
        "character_count": len(text),
        "classification": classification,
        "chunk_count": len(chunks),
        "chunks": chunks,
        "text": text,
    }

    output_path = PROCESSED_DIR / f"{Path(filename).stem}.json"
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result
