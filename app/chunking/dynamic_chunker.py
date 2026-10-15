import re
import uuid

def dynamic_chunk_text(
    text: str,
    min_words: int = 80,
    max_words: int = 180,
    overlap_words: int = 30,
) -> list[dict]:
    """Create overlapping word-bounded chunks, preferring sentence boundaries."""
    if min_words < 1 or max_words < 1 or min_words > max_words:
        raise ValueError("Use positive word counts and min_words <= max_words.")
    if overlap_words < 0 or overlap_words >= max_words:
        raise ValueError("overlap_words must be >= 0 and smaller than max_words.")

    text = re.sub(r"\\s+", " ", text).strip()
    if not text:
        return []

    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + max_words, len(words))

       
        if end < len(words):
            lower = min(start + min_words, end)
            boundary = next(
                (i + 1 for i in range(end - 1, lower - 1, -1)
                 if words[i].endswith((".", "!", "?"))),
                None,
            )
            if boundary and boundary > start:
                end = boundary

        content = " ".join(words[start:end]).strip()
        if content:
            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "text": content,
                "word_count": len(content.split()),
            })

        if end >= len(words):
            break
        start = max(end - overlap_words, start + 1)

    return chunks
