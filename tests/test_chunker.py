from app.chunking.dynamic_chunker import dynamic_chunk_text

def test_empty_text_returns_no_chunks():
    assert dynamic_chunk_text("") == []

def test_chunking_creates_chunks():
    text = " ".join(["policy"] * 250)
    chunks = dynamic_chunk_text(text, min_words=40, max_words=60, overlap_words=10)
    assert len(chunks) > 1
    assert all(chunk["word_count"] <= 60 for chunk in chunks)
