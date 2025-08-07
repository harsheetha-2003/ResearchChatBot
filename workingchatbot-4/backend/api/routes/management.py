# api/routes/management.py

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from database.schema import SessionLocal, Document, Question, SuggestedQuestion
from services.chat_history import _get_history_path
import os
import shutil

router = APIRouter()

class RenameDocumentRequest(BaseModel):
    doc_id: str
    new_filename: str

@router.delete("/chat")
async def delete_chat_history(doc_id: str = Query(..., description="Document ID to delete chat history for")):
    """Delete chat history for a specific document (keeps the document)"""
    try:
        db = SessionLocal()
        
        # Check if document exists
        document = db.query(Document).filter(Document.doc_id == doc_id).first()
        if not document:
            db.close()
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete questions from database
        deleted_questions = db.query(Question).filter(Question.doc_id == doc_id).delete()
        
        # Delete suggested questions from database (so they can be regenerated)
        deleted_suggested = db.query(SuggestedQuestion).filter(SuggestedQuestion.doc_id == doc_id).delete()
        
        db.commit()
        
        # Delete chat history file
        history_path = _get_history_path(doc_id)
        if os.path.exists(history_path):
            os.remove(history_path)
            history_deleted = True
        else:
            history_deleted = False
        
        db.close()
        
        return {
            "message": "Chat history deleted successfully",
            "doc_id": doc_id,
            "deleted_questions": deleted_questions,
            "deleted_suggested_questions": deleted_suggested,
            "history_file_deleted": history_deleted
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while deleting chat history")

@router.delete("/document")
async def delete_document(doc_id: str = Query(..., description="Document ID to delete completely")):
    """Delete entire document along with all associated chat history"""
    try:
        db = SessionLocal()
        
        # Find document
        document = db.query(Document).filter(Document.doc_id == doc_id).first()
        if not document:
            db.close()
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete questions associated with this document
        deleted_questions = db.query(Question).filter(Question.doc_id == doc_id).delete()
        
        # Delete document record
        db.delete(document)
        db.commit()
        
        # Delete chat history file
        history_path = _get_history_path(doc_id)
        history_deleted = False
        if os.path.exists(history_path):
            os.remove(history_path)
            history_deleted = True
        
        # Delete uploaded file
        file_deleted = False
        if document.filepath and os.path.exists(document.filepath):
            os.remove(document.filepath)
            file_deleted = True
        
        # Delete embeddings index
        embeddings_path = f"data/embeddings/{doc_id}_index"
        embeddings_deleted = False
        if os.path.exists(embeddings_path):
            shutil.rmtree(embeddings_path)
            embeddings_deleted = True
        
        db.close()
        
        return {
            "message": "Document and all associated data deleted successfully",
            "doc_id": doc_id,
            "filename": document.filename,
            "deleted_questions": deleted_questions,
            "history_file_deleted": history_deleted,
            "uploaded_file_deleted": file_deleted,
            "embeddings_deleted": embeddings_deleted
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete document error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while deleting document")

@router.put("/document/rename")
async def rename_document(request: RenameDocumentRequest):
    """Rename a document (keeps the same doc_id)"""
    try:
        db = SessionLocal()
        
        # Find document
        document = db.query(Document).filter(Document.doc_id == request.doc_id).first()
        if not document:
            db.close()
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Check if new filename already exists (if you want to enforce uniqueness)
        existing_with_name = db.query(Document).filter(
            Document.filename == request.new_filename,
            Document.doc_id != request.doc_id
        ).first()
        if existing_with_name:
            db.close()
            raise HTTPException(status_code=400, detail="A document with this filename already exists")
        
        # Update filename
        old_filename = document.filename
        document.filename = request.new_filename
        db.commit()
        db.close()
        
        return {
            "message": "Document renamed successfully",
            "doc_id": request.doc_id,
            "old_filename": old_filename,
            "new_filename": request.new_filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Rename document error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while renaming document")