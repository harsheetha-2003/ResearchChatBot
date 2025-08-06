#trial 
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from api.routes.upload import router as upload_router
from api.routes.chat import router as chat_router
from api.routes.citation import router as citation_router
from api.routes.view_docs import router as view_docs_router
from api.routes.chat_history_api import router as chat_history_router

from database.schema import Base, engine
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Research Chatbot API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(upload_router, prefix="/upload")
app.include_router(chat_router, prefix="/chat")
app.include_router(view_docs_router, prefix="/documents")
app.include_router(chat_history_router)

# Serve static files (frontend)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def serve_frontend():
    """Serve the main frontend HTML file"""
    frontend_file = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    if os.path.exists(frontend_file):
        return FileResponse(frontend_file)
    return {"message": "Frontend not found. Please ensure frontend files are in the correct location."}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Research Analyser API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)