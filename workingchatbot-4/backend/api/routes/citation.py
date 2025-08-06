from fastapi import APIRouter, Request
from database.schema import SessionLocal, Question

router = APIRouter()

@router.post("/")
async def get_citations(request: Request):
    data = await request.json()
    doc_id = data.get("doc_id")
    question = data.get("question")

    db = SessionLocal()
    result = db.query(Question).filter_by(doc_id=doc_id, question_text=question).first()
    db.close()

    if not result:
        return {"citations": [], "message": "No matching question found."}

    return {
        "citations": [
            {
                "source": doc_id,
                "excerpt": result.answer_text[:200] + "...",
                "confidence": "high"
            }
        ]
    }
