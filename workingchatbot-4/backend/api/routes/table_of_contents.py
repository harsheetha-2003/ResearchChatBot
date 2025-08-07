# api/routes/table_of_contents.py

from fastapi import APIRouter, HTTPException, Query
from database.schema import SessionLocal, Document, TableOfContents
from services.toc_extractor import extract_table_of_contents
import os

router = APIRouter()

@router.get("/")
async def get_table_of_contents(doc_id: str = Query(..., description="Document ID to get table of contents for")):
    """Get table of contents for a document"""
    try:
        db = SessionLocal()
        
        # Check if document exists
        document = db.query(Document).filter(Document.doc_id == doc_id).first()
        if not document:
            db.close()
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Extract needed fields before closing session
        filename = document.filename
        filepath = document.filepath
        
        # Check if TOC already exists in database
        existing_toc = db.query(TableOfContents).filter(TableOfContents.doc_id == doc_id).order_by(TableOfContents.id).all()
        
        if existing_toc:
            toc_data = [
                {
                    "section_number": entry.section_number,
                    "section_title": entry.section_title,
                    "level": entry.level
                }
                for entry in existing_toc
            ]
            db.close()
            return {
                "doc_id": doc_id,
                "filename": filename,
                "table_of_contents": toc_data,
                "message": "Table of contents retrieved successfully"
            }
        
        # Generate new TOC if none exists
        if not os.path.exists(filepath):
            db.close()
            raise HTTPException(status_code=404, detail="Document file not found")
        
        # Read document content
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                doc_content = f.read()
        except UnicodeDecodeError:
            doc_content = f"Document: {filename}\n\nThis is a binary document that requires text extraction."
        
        # Extract table of contents
        toc_entries = extract_table_of_contents(doc_content, doc_id)
        
        # Save TOC to database
        toc_data = []
        for entry in toc_entries:
            toc_record = TableOfContents(
                doc_id=doc_id,
                section_number=entry['section_number'],
                section_title=entry['section_title'],
                level=entry['level']
            )
            db.add(toc_record)
            toc_data.append(entry)
        
        db.commit()
        db.close()
        
        return {
            "doc_id": doc_id,
            "filename": filename,
            "table_of_contents": toc_data,
            "message": "Table of contents extracted and saved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Table of contents error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while extracting table of contents")
