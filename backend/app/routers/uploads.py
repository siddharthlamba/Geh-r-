import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(prefix="/api/upload", tags=["Uploads"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".pdf"}

@router.post("")
async def upload_file(file: UploadFile = File(...)):
    """
    Saves an uploaded photo or screenshot and returns accessible URL.
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Allowed formats: PNG, JPG, JPEG, WEBP, PDF")
        
    unique_name = f"{uuid.uuid4().hex[:12]}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {
        "filename": file.filename,
        "url": f"/uploads/{unique_name}",
        "size": os.path.getsize(file_path)
    }
