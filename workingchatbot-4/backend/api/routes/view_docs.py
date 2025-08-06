# from fastapi import APIRouter
# from database.schema import SessionLocal, Document

# router = APIRouter()

# @router.get("/")
# async def list_documents():
#     db = SessionLocal()
#     docs = db.query(Document).all()
#     db.close()

#     return [
#         {
#             "doc_id": doc.doc_id,
#             "filename": doc.filename,
#             "upload_date": doc.upload_date.strftime("%Y-%m-%d %H:%M:%S"),
#             "chat_link": f"/chat?doc_id={doc.doc_id}"  # ✅ Link to chat
#         }
#         for doc in docs
#     ]
# api/routes/view_docs.py

from fastapi import APIRouter
from database.schema import SessionLocal, Document

router = APIRouter()

@router.get("/")
async def list_documents():
    db = SessionLocal()
    docs = db.query(Document).all()
    db.close()

    return [
        {
            "doc_id": doc.doc_id,
            "filename": doc.filename,
            "upload_date": doc.upload_date.strftime("%Y-%m-%d %H:%M:%S"),
            "chat_history_link": f"/chat-history?doc_id={doc.doc_id}"  # ✅ Link to chat history
        }
        for doc in docs
    ]

