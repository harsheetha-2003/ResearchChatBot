
# api/routes/chat.py

# from fastapi import APIRouter
# from pydantic import BaseModel
# from orchestrator import generate_answer
# from database.schema import SessionLocal, Question
# from services.retriever import retrieve_chunks
# from services.citation_mapper import map_citations  # Optional if you want to use your own mapper

# router = APIRouter()

# class ChatRequest(BaseModel):
#     doc_id: str
#     question: str

# @router.post("/")
# async def ask_question(request: ChatRequest):
#     try:
#         doc_id = request.doc_id
#         question = request.question

#         # ✅ Updated retrieval logic
#         retrieval = retrieve_chunks(doc_id, question)
#         chunks = retrieval.get("chunks", [])
#         fallback_answer = retrieval.get("answer", "")
#         citations = retrieval.get("citations", [])

#         if not chunks:
#             return {
#                 "error": "No relevant content found for this document ID.",
#                 "doc_id": doc_id,
#                 "question": question
#             }

#         # ✅ Build context from chunks
#         context = "\n\n".join([chunk["content"] for chunk in chunks])

#         # ✅ Prompt for LLM
#         prompt = f"""You are a research assistant. Answer the question using only the context below.

# Context:
# {context}

# Question: {question}
# """

#         # ✅ Generate answer using LLM
#         final_answer = generate_answer(prompt)

#         # ✅ Fallback to plain summary if LLM fails
#         if not final_answer:
#             final_answer = fallback_answer

#         # ✅ Save to database
#         db = SessionLocal()
#         q = Question(doc_id=doc_id, question_text=question, answer_text=final_answer)
#         db.add(q)
#         db.commit()
#         db.close()

#         # ✅ Return structured response
#         return {
#             "answer": final_answer,
#             "citations": citations,
#             "doc_id": doc_id,
#             "question": question
#         }

#     except Exception as e:
#         print(f"Chat error: {e}")
#         return {
#             "error": "Internal Server Error",
#             "details": str(e),
#             "doc_id": request.doc_id,
#             "question": request.question
#         }

from fastapi import APIRouter
from pydantic import BaseModel
from orchestrator import generate_answer
from database.schema import SessionLocal, Question
from services.retriever import retrieve_chunks
from services.citation_mapper import map_citations  # Optional if you want to use your own mapper
from services.chat_history import load_chat_history, save_chat_entry

router = APIRouter()

class ChatRequest(BaseModel):
    doc_id: str
    question: str

@router.post("/")
async def ask_question(request: ChatRequest):
    try:
        doc_id = request.doc_id
        question = request.question

        # ✅ Check if answer already exists in history
        history = load_chat_history(doc_id)
        for entry in history:
            if entry["query"] == question:
                return {
                    "answer": entry["answer"],
                    "citations": [],  # Optional: you can store citations in history if needed
                    "doc_id": doc_id,
                    "question": question,
                    "cached": True
                }

        # ✅ Updated retrieval logic
        retrieval = retrieve_chunks(doc_id, question)
        chunks = retrieval.get("chunks", [])
        fallback_answer = retrieval.get("answer", "")
        citations = retrieval.get("citations", [])

        if not chunks:
            return {
                "error": "No relevant content found for this document ID.",
                "doc_id": doc_id,
                "question": question
            }

        # ✅ Build context from chunks
        context = "\n\n".join([chunk["content"] for chunk in chunks])

        # ✅ Prompt for LLM
        prompt = f"""You are a research assistant. Answer the question using only the context below. 
        Answer in at least a few sentances.
        Do not give one sentence or two answers. Give a proper descriptive answer that match the context inside the paper. 
        If i ask you to summarize, then summarize with at least 7-8 lines instead of a brief answer. 

        If a specific number of characters or lines are asked in the question, then keep the answer in that boundaries only. 
        Do not exceed ONLY when asked. Otherwise answer in more than a few sentences

Context:
{context}

Question: {question}
"""

        # ✅ Generate answer using LLM
        final_answer = generate_answer(prompt)

        # ✅ Fallback to plain summary if LLM fails
        if not final_answer:
            final_answer = fallback_answer

        # ✅ Ensure doc_id and question are included in fallback answer
        if final_answer == fallback_answer:
            final_answer = (
                f"Document ID: {doc_id}\n"
                f"Question: {question}\n\n"
                f"{fallback_answer}"
            )

        # ✅ Save to database
        db = SessionLocal()
        q = Question(doc_id=doc_id, question_text=question, answer_text=final_answer)
        db.add(q)
        db.commit()
        db.close()

        # ✅ Save to chat history
        save_chat_entry(doc_id, question, final_answer)

        # ✅ Return structured response
        return {
            "answer": final_answer,
            "citations": citations,
            "doc_id": doc_id,
            "question": question,
            "cached": False
        }

    except Exception as e:
        print(f"Chat error: {e}")
        return {
            "error": "Internal Server Error",
            "details": str(e),
            "doc_id": request.doc_id,
            "question": request.question
        }
