"""
Legal AI API Suite — FastAPI Application
==========================================
Three endpoints:
  1. POST /classify/clauses    — Legal clause classifier
  2. POST /summarize/document  — Legal document summarizer
  3. POST /chat/rag            — RAG-powered legal chat

Deploy with:
  uvicorn main:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.classifier import router as classifier_router
from routers.summarizer import router as summarizer_router
from routers.rag_chat import router as rag_chat_router

app = FastAPI(
    title="Legal AI API Suite",
    description="AI-powered APIs for legal clause classification, document summarization, and RAG-based chat.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(classifier_router, prefix="/classify", tags=["Classifier"])
app.include_router(summarizer_router, prefix="/summarize", tags=["Summarizer"])
app.include_router(rag_chat_router, prefix="/chat", tags=["RAG Chat"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
