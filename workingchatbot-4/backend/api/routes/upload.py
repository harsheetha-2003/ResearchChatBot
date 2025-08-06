# api/routes/upload.py

from fastapi import APIRouter, UploadFile, File
from services.embedder import embed_document
from database.schema import SessionLocal, Document
import os

router = APIRouter()
UPLOAD_DIR = "data/uploads"

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Save file to disk
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Embed document and get doc_id + chunks
        doc_id, chunks = embed_document(file_path)

        # ✅ Check for duplicate filename BEFORE inserting
        db = SessionLocal()
        existing = db.query(Document).filter(Document.filename == file.filename).first()
        if existing:
            db.close()
            return {
                "error": "This file has already been uploaded.",
                "filename": file.filename,
                "doc_id": existing.doc_id
            }

        # Insert new document metadata
        doc = Document(doc_id=doc_id, filename=file.filename, filepath=file_path)
        db.add(doc)
        db.commit()
        db.close()

        full_text = "\n\n".join(chunks)

        return {
            "message": "Upload successful. Document parsed and embedded.",
            "doc_id": doc_id,
            "filename": file.filename,
            "content": full_text,
            "status": "LLM is ready to chat using this document."
        }

    except Exception as e:
        print(f"Upload error: {e}")
        return {"error": str(e)}
