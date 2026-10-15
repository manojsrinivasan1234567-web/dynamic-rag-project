from sklearn.metrics.pairwise import cosine_similarity
from app.embeddings.embedding_service import EmbeddingService

class VectorDatabase:
    """In-memory vector index. It resets when the API process restarts."""
    def __init__(self):
        self.items: list[dict] = []
        self.embedding_service = EmbeddingService()

    def upsert_document(self, filename: str, chunks: list[dict]):
        self.items = [item for item in self.items if item["filename"] != filename]
        for chunk in chunks:
            self.items.append({
                "filename": filename,
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "word_count": chunk["word_count"],
            })
        try:
            self.embedding_service.fit([item["text"] for item in self.items])
        except ValueError:
            self.embedding_service = EmbeddingService()

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        service = self.embedding_service
        if not self.items or service.model is None or service.matrix is None:
            return []
        query_vector = service.encode_query(query)
        if query_vector is None or query_vector.nnz == 0:
            return []
        scores = cosine_similarity(query_vector, service.matrix).ravel()
        ranked = sorted(enumerate(scores), key=lambda pair: pair[1], reverse=True)
        results = []
        for index, score in ranked:
            if score <= 0:
                continue
            item = self.items[index]
            results.append({**item, "score": round(float(score), 4)})
            if len(results) >= top_k:
                break
        return results

vector_db = VectorDatabase()
