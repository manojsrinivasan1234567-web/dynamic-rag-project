from sklearn.feature_extraction.text import TfidfVectorizer

class EmbeddingService:
    """Lightweight local text vectors using TF-IDF (not neural embeddings)."""
    def __init__(self):
        self.model = None
        self.matrix = None

    def fit(self, texts: list[str]):
        if not texts:
            self.model = None
            self.matrix = None
            return
        self.model = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.model.fit_transform(texts)

    def encode_query(self, query: str):
        if self.model is None:
            return None
        return self.model.transform([query])
