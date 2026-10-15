from app.chunking.dynamic_chunker import dynamic_chunk_text

def create_chunks(text: str, document_type: str, min_words: int = 80,
                  max_words: int = 180, overlap_words: int = 30) -> list[dict]:
    """Choose chunk settings based on document category."""
   
    if document_type in {"product_documentation", "troubleshooting_guide"}:
        max_words = min(max_words, 150)
        overlap_words = min(overlap_words, max_words - 1)
    return dynamic_chunk_text(text, min_words, max_words, overlap_words)
