"""
Legal Document Summarizer API
Generates concise summaries of legal documents.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

router = APIRouter()

# ── Model Loading ──────────────────────────────────────────────
MODEL_PATH = "./models/summarizer"

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH)
    model.eval()
except Exception as e:
    print(f"⚠️  Summarizer model not loaded: {e}")
    tokenizer = None
    model = None


# ── Schemas ────────────────────────────────────────────────────
class SummarizeRequest(BaseModel):
    text: str = Field(..., description="The full legal document text to summarize.")
    max_length: Optional[int] = Field(
        300,
        description="Maximum length of the generated summary in tokens.",
    )
    min_length: Optional[int] = Field(
        50,
        description="Minimum length of the generated summary in tokens.",
    )


class SummarizeResponse(BaseModel):
    summary: str = Field(..., description="The generated summary of the legal document.")
    original_length: int = Field(..., description="Character count of the original document.")
    summary_length: int = Field(..., description="Character count of the generated summary.")
    compression_ratio: float = Field(
        ..., description="Ratio of summary length to original length."
    )


# ── Endpoint ───────────────────────────────────────────────────
@router.post("/document", response_model=SummarizeResponse)
async def summarize_document(request: SummarizeRequest):
    """
    Summarize a legal document.

    Accepts full legal document text and returns a concise summary,
    preserving key legal terms and obligations.
    """
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Summarizer model is not loaded.")

    inputs = tokenizer(
        request.text,
        return_tensors="pt",
        truncation=True,
        max_length=1024,
        padding=True,
    )

    with torch.no_grad():
        summary_ids = model.generate(
            inputs["input_ids"],
            max_length=request.max_length,
            min_length=request.min_length,
            num_beams=4,
            length_penalty=2.0,
            early_stopping=True,
        )

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    original_len = len(request.text)
    summary_len = len(summary)

    return SummarizeResponse(
        summary=summary,
        original_length=original_len,
        summary_length=summary_len,
        compression_ratio=round(summary_len / original_len, 4) if original_len > 0 else 0,
    )
