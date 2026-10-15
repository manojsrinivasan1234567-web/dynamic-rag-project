# Dynamic RAG Document API

A modular FastAPI learning project for PDF upload, text extraction, OCR, rule-based classification,
dynamic chunking, TF-IDF retrieval, and extractive question answering.

## Features
- Upload PDF files (20 MB limit)
- Extract selectable PDF text
- OCR scanned PDFs (requires Tesseract and Poppler)
- Classify documents using keyword rules
- Split text into overlapping chunks
- Index chunks with TF-IDF and cosine similarity
- Search and return source chunks
- Answer questions by selecting sentences from retrieved text

## Setup (Windows Command Prompt)
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs.

## Test flow
1. `POST /upload/` — upload a PDF and copy the returned filename.
2. `POST /process/{filename}` — process, chunk, and index it.
   Example body:
   ```json
   {"force_ocr": false, "min_words": 80, "max_words": 180, "overlap_words": 30}
   ```
3. `POST /search` — body: `{"query": "your question", "top_k": 3}`
4. `POST /ask` — body: `{"question": "your question", "top_k": 3}`

Use `force_ocr: true` or `GET /documents/{filename}/ocr-scanned` for scanned PDFs.
Tesseract and Poppler must be installed separately for OCR.

## Notes
- TF-IDF is a lexical baseline, not a neural semantic embedding model.
- `/ask` is extractive: it selects existing sentences and does not use an LLM.
- The vector index is in memory and resets when the server restarts. Reprocess documents after restart.
- This is a learning project; review and harden file handling and resource limits before production use.
