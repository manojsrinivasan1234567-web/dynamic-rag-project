from pathlib import Path
import uuid
from fastapi import HTTPException, UploadFile
from app.config import UPLOAD_DIR, MAX_FILE_SIZE, ALLOWED_EXTENSIONS

async def save_upload(upload: UploadFile) -> tuple[str, Path, int]:
    original_name = Path(upload.filename or "").name
    if not original_name:
        raise HTTPException(status_code=400, detail="A filename is required.")
    if Path(original_name).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    content = await upload.read(MAX_FILE_SIZE + 1)
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Maximum upload size is 20 MB.")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="The file does not appear to be a valid PDF.")

    safe_name = f"{uuid.uuid4().hex}_{original_name}"
    destination = UPLOAD_DIR / safe_name
    destination.write_bytes(content)
    return safe_name, destination, len(content)

def get_uploaded_path(filename: str) -> Path:
    if Path(filename).name != filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    path = UPLOAD_DIR / filename
    if not path.is_file() or path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=404, detail="Uploaded PDF not found.")
    return path
