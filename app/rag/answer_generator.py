import re

def generate_answer(question: str, retrieved_chunks: list[dict]) -> dict:
    """Extractive answer baseline: selects relevant sentences; no LLM is called."""
    if not retrieved_chunks:
        return {
            "question": question,
            "answer": "I could not find relevant information in the indexed documents.",
            "sources": [],
        }

    sentences = []
    for chunk in retrieved_chunks:
        for sentence in re.split(r"(?<=[.!?])\\s+", chunk["text"]):
            sentence = sentence.strip()
            if sentence:
                sentences.append({
                    "text": sentence,
                    "filename": chunk["filename"],
                    "chunk_id": chunk["chunk_id"],
                    "score": chunk["score"],
                })

    # The retrieval rank is used as a simple ranking proxy.
    selected = []
    seen = set()
    for item in sentences:
        key = item["text"].lower()
        if key not in seen:
            selected.append(item)
            seen.add(key)
        if len(selected) == 3:
            break

    return {
        "question": question,
        "answer": " ".join(item["text"] for item in selected),
        "sources": [
            {
                "filename": item["filename"],
                "chunk_id": item["chunk_id"],
                "text": item["text"],
                "similarity": item["score"],
            }
            for item in selected
        ],
    }
