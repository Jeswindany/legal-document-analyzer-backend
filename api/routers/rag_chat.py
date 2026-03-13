"""
RAG-Powered Legal Chat API
Retrieval-augmented generation for legal Q&A.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
import torch
import faiss
import numpy as np

router = APIRouter()

# ── Model Loading ──────────────────────────────────────────────
CHAT_MODEL_PATH = "./models/rag_chat"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

try:
    chat_tokenizer = AutoTokenizer.from_pretrained(CHAT_MODEL_PATH)
    chat_model = AutoModelForCausalLM.from_pretrained(CHAT_MODEL_PATH)
    chat_model.eval()
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)
except Exception as e:
    print(f"⚠️  RAG Chat model not loaded: {e}")
    chat_tokenizer = None
    chat_model = None
    embedding_model = None

# ── In-memory document store ──────────────────────────────────
document_chunks: List[str] = []
faiss_index: Optional[faiss.IndexFlatL2] = None


# ── Schemas ────────────────────────────────────────────────────
class IngestRequest(BaseModel):
    documents: List[str] = Field(
        ..., description="List of document text chunks to index for retrieval."
    )
    chunk_size: Optional[int] = Field(
        500, description="Target size (in characters) for splitting documents into chunks."
    )


class IngestResponse(BaseModel):
    chunks_indexed: int = Field(..., description="Number of chunks added to the index.")
    total_chunks: int = Field(..., description="Total chunks currently in the index.")


class ChatRequest(BaseModel):
    query: str = Field(..., description="The legal question to answer.")
    top_k: Optional[int] = Field(
        3, description="Number of relevant document chunks to retrieve."
    )
    max_tokens: Optional[int] = Field(
        512, description="Maximum tokens in the generated response."
    )


class RetrievedChunk(BaseModel):
    text: str
    relevance_score: float


class ChatResponse(BaseModel):
    answer: str = Field(..., description="The AI-generated answer based on retrieved context.")
    sources: List[RetrievedChunk] = Field(
        ..., description="Document chunks used as context for the answer."
    )


# ── Helper Functions ──────────────────────────────────────────
def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """Split text into chunks of approximately chunk_size characters."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        current_length += len(word) + 1
        current_chunk.append(word)
        if current_length >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def retrieve_chunks(query: str, top_k: int = 3) -> List[tuple]:
    """Retrieve the most relevant chunks for a query."""
    global faiss_index, document_chunks

    if faiss_index is None or len(document_chunks) == 0:
        return []

    query_embedding = embedding_model.encode([query])
    distances, indices = faiss_index.search(
        np.array(query_embedding, dtype=np.float32), min(top_k, len(document_chunks))
    )

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx < len(document_chunks):
            # Convert L2 distance to a similarity score
            score = 1 / (1 + dist)
            results.append((document_chunks[idx], float(score)))

    return results


# ── Endpoints ─────────────────────────────────────────────────
@router.post("/ingest", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest):
    """
    Ingest and index legal documents for RAG retrieval.

    Splits documents into chunks, generates embeddings, and adds them
    to the FAISS vector index.
    """
    global faiss_index, document_chunks

    if embedding_model is None:
        raise HTTPException(status_code=503, detail="Embedding model is not loaded.")

    new_chunks = []
    for doc in request.documents:
        new_chunks.extend(chunk_text(doc, request.chunk_size))

    embeddings = embedding_model.encode(new_chunks)
    embeddings_np = np.array(embeddings, dtype=np.float32)

    if faiss_index is None:
        dimension = embeddings_np.shape[1]
        faiss_index = faiss.IndexFlatL2(dimension)

    faiss_index.add(embeddings_np)
    document_chunks.extend(new_chunks)

    return IngestResponse(
        chunks_indexed=len(new_chunks),
        total_chunks=len(document_chunks),
    )


@router.post("/rag", response_model=ChatResponse)
async def rag_chat(request: ChatRequest):
    """
    Ask a legal question using RAG (Retrieval-Augmented Generation).

    Retrieves relevant document chunks from the index, then generates
    an answer grounded in the retrieved context.
    """
    if chat_model is None or chat_tokenizer is None:
        raise HTTPException(status_code=503, detail="Chat model is not loaded.")

    # Retrieve relevant chunks
    retrieved = retrieve_chunks(request.query, request.top_k)

    # Build context from retrieved chunks
    context = "\n\n".join([chunk for chunk, _ in retrieved])

    # Construct prompt
    prompt = f"""You are a legal AI assistant. Answer the question based on the provided legal context.
If the context doesn't contain enough information, say so clearly.

Context:
{context}

Question: {request.query}

Answer:"""

    inputs = chat_tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=2048,
    )

    with torch.no_grad():
        output_ids = chat_model.generate(
            inputs["input_ids"],
            max_new_tokens=request.max_tokens,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
        )

    # Decode only the new tokens
    answer = chat_tokenizer.decode(
        output_ids[0][inputs["input_ids"].shape[-1]:],
        skip_special_tokens=True,
    )

    sources = [
        RetrievedChunk(text=chunk, relevance_score=round(score, 4))
        for chunk, score in retrieved
    ]

    return ChatResponse(answer=answer.strip(), sources=sources)
