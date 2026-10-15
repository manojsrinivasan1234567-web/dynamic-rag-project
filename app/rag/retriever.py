from app.vectorstore.vector_database import vector_db

def retrieve(query: str, top_k: int = 3) -> list[dict]:
    return vector_db.search(query, top_k)
