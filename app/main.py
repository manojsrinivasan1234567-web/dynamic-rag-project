from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.ingestion.document_loader import save_upload, get_uploaded_path
from app.ingestion.ingestion_pipeline import process_document
from app.parsing.parser_factory import parse_document
from app.ingestion.document_classifier import classify_document
from app.chunking.chunking_factory import create_chunks
from app.rag.retriever import retrieve
from app.rag.answer_generator import generate_answer
from app.vectorstore.vector_database import vector_db

app = FastAPI(
    title="Dynamic RAG Document API",
    description="Upload PDFs, parse/OCR, classify, chunk, index, search and ask questions.",
    version="1.0.0",
)

class ProcessRequest(BaseModel):
    force_ocr: bool = False
    min_words: int = Field(default=80, ge=20, le=1000)
    max_words: int = Field(default=180, ge=40, le=2000)
    overlap_words: int = Field(default=30, ge=0, le=500)

class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=20)

class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=20)

@app.get("/")
def home():
    return {"message": "Dynamic RAG API is running", "docs": "/docs"}

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    filename, path, size = await save_upload(file)
    return {"message": "Uploaded successfully", "filename": filename, "size_bytes": size}

@app.get("/documents/{filename}/ocr")
def extract_pdf(filename: str):
    path = get_uploaded_path(filename)
    try:
        result = parse_document(path, force_ocr=False)
        return {
            "filename": filename,
            "parser": result["parser"],
            "page_count": result["page_count"],
            "character_count": len(result["text"]),
            "pages": result["pages"],
            "text": result["text"],
        }
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"PDF parsing failed: {exc}")

@app.get("/documents/{filename}/ocr-scanned")
def extract_scanned_pdf(filename: str):
    path = get_uploaded_path(filename)
    try:
        result = parse_document(path, force_ocr=True)
        return {
            "filename": filename,
            "parser": result["parser"],
            "page_count": result["page_count"],
            "character_count": len(result["text"]),
            "pages": result["pages"],
            "text": result["text"],
        }
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"OCR failed. Check Tesseract and Poppler: {exc}")

@app.post("/process/{filename}")
def process_pdf(filename: str, request: ProcessRequest):
    path = get_uploaded_path(filename)
    if request.min_words > request.max_words:
        raise HTTPException(status_code=400, detail="min_words must be <= max_words")
    if request.overlap_words >= request.max_words:
        raise HTTPException(status_code=400, detail="overlap_words must be < max_words")
    try:
        result = process_document(
            filename, path,
            force_ocr=request.force_ocr,
            min_words=request.min_words,
            max_words=request.max_words,
            overlap_words=request.overlap_words,
        )
        # Avoid returning the entire document and all chunk text by default.
        return {
            "message": "Document processed and indexed",
            "filename": filename,
            "parser": result["parser"],
            "page_count": result["page_count"],
            "character_count": result["character_count"],
            "classification": result["classification"],
            "chunk_count": result["chunk_count"],
            "chunks": result["chunks"],
        }
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Document processing failed: {exc}")

@app.post("/classify/{filename}")
def classify_pdf(filename: str):
    path = get_uploaded_path(filename)
    try:
        parsed = parse_document(path)
        return {"filename": filename, **classify_document(parsed["text"])}
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Classification failed: {exc}")

@app.post("/documents/{filename}/chunks")
def create_document_chunks(filename: str, request: ProcessRequest):
    path = get_uploaded_path(filename)
    try:
        parsed = parse_document(path, force_ocr=request.force_ocr)
        category = classify_document(parsed["text"])["category"]
        chunks = create_chunks(parsed["text"], category, request.min_words,
                               request.max_words, request.overlap_words)
        return {"filename": filename, "total_chunks": len(chunks), "chunks": chunks}
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Chunking failed: {exc}")

@app.post("/index/{filename}")
def index_pdf(filename: str, request: ProcessRequest):
    path = get_uploaded_path(filename)
    try:
        result = process_document(
            filename, path, request.force_ocr,
            request.min_words, request.max_words, request.overlap_words
        )
        return {
            "message": "Document indexed",
            "filename": filename,
            "indexed_chunks": result["chunk_count"],
        }
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Indexing failed: {exc}")

@app.post("/search")
def search_documents(request: SearchRequest):
    results = retrieve(request.query, request.top_k)
    return {"query": request.query, "results_count": len(results), "results": results}

@app.post("/ask")
def ask_question(request: AskRequest):
    results = retrieve(request.question, request.top_k)
    return generate_answer(request.question, results)

@app.get("/health")
def health():
    return {"status": "ok", "indexed_chunks": len(vector_db.items)}
