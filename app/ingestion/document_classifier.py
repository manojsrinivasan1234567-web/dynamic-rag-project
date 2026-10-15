import re

KEYWORDS = {
    "employee_policy": ["employee", "leave", "attendance", "salary", "human resources", "hr policy"],
    "product_documentation": ["installation", "configuration", "api", "endpoint", "parameter", "documentation"],
    "invoice": ["invoice", "invoice number", "total amount", "tax", "subtotal", "billing"],
    "troubleshooting_guide": ["troubleshooting", "error", "warning", "failed", "solution", "fix"],
}

def classify_document(text: str) -> dict:
    """Simple keyword-based baseline classifier, not a trained ML model."""
    normalized = text.lower()
    scores = {
        category: sum(
            len(re.findall(rf"\\b{re.escape(word)}\\b", normalized))
            for word in words
        )
        for category, words in KEYWORDS.items()
    }
    best = max(scores, key=scores.get) if scores else "general_document"
    if not scores or scores[best] == 0:
        best = "general_document"
    return {"category": best, "scores": scores}
