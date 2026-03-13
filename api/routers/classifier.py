"""
Legal Clause Classifier API (extended)
- Accepts DOCX or PDF uploads (or raw text)
- Extracts text (pdf: text extraction + OCR fallback)
- Splits into sentences, strips numbering/bullets, filters short list-items
- Classifies each segment with a HuggingFace sequence-classification model (LegalBERT)
- Groups classified clauses into the provided category sets and returns JSON lists
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import io
import re

# Optional dependencies for document extraction / OCR
try:
    from docx import Document
except Exception:
    Document = None

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

try:
    from pdf2image import convert_from_bytes
    import pytesseract
except Exception:
    convert_from_bytes = None
    pytesseract = None

import nltk

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab")

router = APIRouter()

# ── Model Loading ──────────────────────────────────────────────
MODEL_PATH = "./routers/models/classifier"

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    model.eval()
except Exception as e:
    print(f"⚠️  Classifier model not loaded: {e}")
    tokenizer = None
    model = None

# ── Label Map  ────────────────
label_list = ['Adjustments', 'Agreements', 'Amendments', 'Anti-Corruption Laws', 'Applicable Laws', 'Approvals', 'Arbitration', 'Assignments', 'Assigns', 'Authority', 'Authorizations', 'Base Salary', 'Benefits', 'Binding Effects', 'Books', 'Brokers', 'Capitalization', 'Change In Control', 'Closings', 'Compliance With Laws', 'Confidentiality', 'Consent To Jurisdiction', 'Consents', 'Construction', 'Cooperation', 'Costs', 'Counterparts', 'Death', 'Defined Terms', 'Definitions', 'Disability', 'Disclosures', 'Duties', 'Effective Dates', 'Effectiveness', 'Employment', 'Enforceability', 'Enforcements', 'Entire Agreements', 'Erisa', 'Existence', 'Expenses', 'Fees', 'Financial Statements', 'Forfeitures', 'Further Assurances', 'General', 'Governing Laws', 'Headings', 'Indemnifications', 'Indemnity', 'Insurances', 'Integration', 'Intellectual Property', 'Interests', 'Interpretations', 'Jurisdictions', 'Liens', 'Litigations', 'Miscellaneous', 'Modifications', 'No Conflicts', 'No Defaults', 'No Waivers', 'Non-Disparagement', 'Notices', 'Organizations', 'Participations', 'Payments', 'Positions', 'Powers', 'Publicity', 'Qualifications', 'Records', 'Releases', 'Remedies', 'Representations', 'Sales', 'Sanctions', 'Severability', 'Solvency', 'Specific Performance', 'Submission To Jurisdiction', 'Subsidiaries', 'Successors', 'Survival', 'Tax Withholdings', 'Taxes', 'Terminations', 'Terms', 'Titles', 'Transactions With Affiliates', 'Use Of Proceeds', 'Vacations', 'Venues', 'Vesting', 'Waiver Of Jury Trials', 'Waivers', 'Warranties', 'Withholdings']

label2id = {label: idx for idx, label in enumerate(label_list)}
id2label = {idx: label for idx, label in enumerate(label_list)}

# ── Predefined category sets (user provided) ------------------
termination = {
    "Terminations", "Employment", "Base Salary", "Benefits", "Vacations",
    "Positions", "Duties", "Death", "Disability", "Forfeitures", "Vesting",
    "Effective Dates", "Effectiveness", "Survival"
}

confidentiality = {
    "Confidentiality", "Intellectual Property", "Non-Disparagement",
    "Publicity", "Disclosures"
}

liability = {
    "Indemnifications", "Indemnity", "Remedies", "Warranties", "Representations",
    "Specific Performance", "Waiver Of Jury Trials", "Waivers", "No Waivers",
    "No Defaults", "No Conflicts", "Liens", "Insurances", "Enforcements",
    "Enforceability", "Sanctions", "Litigations", "Costs", "Releases"
}

governance = {
    "Applicable Laws", "Governing Laws", "Compliance With Laws", "Anti-Corruption Laws",
    "Erisa", "Jurisdictions", "Consent To Jurisdiction", "Submission To Jurisdiction",
    "Venues", "Arbitration", "Consents", "Approvals", "Authorizations", "Authority",
    "Change In Control", "Organizations", "Existence", "Further Assurances", "Assignments", "Assigns"
}

finance = {
    "Payments", "Fees", "Expenses", "Withholdings", "Tax Withholdings", "Taxes",
    "Financial Statements", "Books", "Records", "Capitalization", "Closings",
    "Sales", "Transactions With Affiliates", "Use Of Proceeds", "Interests",
    "Solvency", "Brokers", "Participations",
    "Successors", "Subsidiaries", "Powers"
}

def map_label_to_category(label: str) -> str:

    if label in termination:
        return "termination"

    if label in confidentiality:
        return "confidentiality"

    if label in liability:
        return "liability"

    if label in governance:
        return "governance"

    if label in finance:
        return "finance"

    return "other"

# ── Helpers: text extraction ----------------------------------

def extract_text_from_docx(file_bytes: bytes) -> str:
    if Document is None:
        raise RuntimeError("python-docx is required to parse DOCX files (pip install python-docx)")
    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
    return "\n".join(paragraphs)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    # Try PyMuPDF text extraction first
    if fitz is not None:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text_pages = [page.get_text("text") for page in doc]
            full = "\n".join(p for p in text_pages if p and p.strip())
            if full.strip():
                return full
        except Exception:
            pass

    # Fallback: try pdfplumber if installed (optional)
    try:
        import pdfplumber

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
            joined = "\n".join(p for p in pages if p and p.strip())
            if joined.strip():
                return joined
    except Exception:
        pass

    # If still empty, return empty string — caller may attempt OCR
    return ""


def ocr_pdf_bytes(file_bytes: bytes) -> str:
    if convert_from_bytes is None or pytesseract is None:
        raise RuntimeError("pdf2image and pytesseract are required for OCR of scanned PDFs (pip install pdf2image pytesseract)")
    images = convert_from_bytes(file_bytes)
    text_chunks = []
    for img in images:
        text_chunks.append(pytesseract.image_to_string(img))
    return "\n".join(t.strip() for t in text_chunks if t and t.strip())


# ── Clean / split text into meaningful segments ----------------
NUMBERING_REGEX = re.compile(r"^\s*(?:\d+[\.|\)]|\([a-zA-Z0-9]+\)|[-\u2022\*\u25E6\u2023])\s*")
MIN_SEGMENT_CHARS = 30  # heuristic — drop short list items

HEADER_PATTERNS = [
    "this agreement is made",
    "in witness whereof",
    "witnesses",
    "rental agreement",
]

def normalize_and_split(text: str) -> List[str]:
    """
    Produce complete sentence segments from legal text.

    Strategy:
    1. Normalize newlines and collapse multiple blank lines into paragraph separators.
    2. For each paragraph:
       - Fix hyphenation at line breaks (e.g., "exam-\nple" -> "example")
       - Replace remaining single newlines inside a paragraph with spaces so sentences
         broken by line-wrapping are reflowed.
       - Remove leading numbering/bullets.
       - Split into sentences with nltk.sent_tokenize (fallback to regex).
       - Filter very short fragments.
    """
    # Normalize newlines and trim
    text = text.replace("\r", "\n").strip()

    if not text:
        return []

    # Split on one-or-more blank lines to preserve paragraph grouping
    paragraphs = re.split(r'\n\s*\n+', text)

    segments: List[str] = []

    # Use nltk sentence tokenizer when available
    try:
        from nltk.tokenize import sent_tokenize
        use_nltk = True
    except Exception:
        use_nltk = False

    for para in paragraphs:
        # Fix common hyphenation at line end: "exam-\nple" -> "example"
        para = re.sub(r'-\s*\n\s*', '', para)

        # Replace remaining single newlines (line wraps) with a space so sentences join back
        para = re.sub(r'\s*\n\s*', ' ', para).strip()

        # Remove leading numbering/bullets at paragraph level
        para = NUMBERING_REGEX.sub('', para).strip()
        if not para:
            continue

        # Sentence-split the paragraph (keeps complete sentences)
        if use_nltk:
            sents = sent_tokenize(para)
        else:
            # fallback: split on punctuation followed by whitespace
            sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', para) if s.strip()]

        for s in sents:
            lower_s = s.lower()

            if any(p in lower_s for p in HEADER_PATTERNS):
                continue

            s_clean = NUMBERING_REGEX.sub('', s).strip()

            # ignore headings / short fragments
            if len(s_clean.split()) < 6:
                continue

            if len(s_clean) < MIN_SEGMENT_CHARS:
                continue

            segments.append(s_clean)

    return segments

# ── Inference helper -----------------------------------------

def classify_segment(segment: str) -> Dict[str, Any]:

    if tokenizer is None or model is None:
        raise RuntimeError("Classifier model is not loaded")

    inputs = tokenizer(
        segment,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    )

    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.softmax(outputs.logits, dim=-1)

    topk = torch.topk(probs, k=3)

    predicted_ids = topk.indices[0].tolist()
    confidences = topk.values[0].tolist()

    label = None
    confidence = None

    for i, pid in enumerate(predicted_ids):
        candidate_label = id2label[pid]
        category = map_label_to_category(candidate_label)

        if category != "other":
            label = candidate_label
            confidence = confidences[i]
            break

    if label is None:
        label = id2label[predicted_ids[0]]
        confidence = confidences[0]

    category = map_label_to_category(label)

    return {
        "clause_type": category,
        "label": label,
        "confidence": round(float(confidence), 4),
        "text": segment
    }


# ── Endpoint: accepts file (docx/pdf) or raw text --------------
@router.post("/clauses")
async def classify_clauses(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    threshold: float = Form(0.5),
):
    """
    Accepts a DOCX or PDF upload (multipart/form-data) or raw text (form field "text").
    Extracts/normalizes text, splits into sentences, filters short items and numbering,
    classifies each segment, groups results by the provided category sets and returns JSON.
    """
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Classifier model is not loaded.")

    if file is None and (text is None or not text.strip()):
        raise HTTPException(status_code=400, detail="No file uploaded and no text provided.")

    extracted_text = ""

    if file is not None:
        contents = await file.read()
        filename = (file.filename or "").lower()
        if filename.endswith('.docx'):
            try:
                extracted_text = extract_text_from_docx(contents)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        elif filename.endswith('.pdf'):
            # try text extraction
            extracted_text = extract_text_from_pdf(contents)
            if not extracted_text.strip():
                # attempt OCR
                try:
                    extracted_text = ocr_pdf_bytes(contents)
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed OCR: {e}")
        else:
            # try to treat as text fallback
            try:
                extracted_text = contents.decode('utf-8')
            except Exception:
                raise HTTPException(status_code=400, detail="Unsupported file type. Upload .pdf or .docx or pass raw text.")

    if text and text.strip():
        # if text provided in form, append to extracted_text
        extracted_text = (extracted_text + "\n\n" + text) if extracted_text else text

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from the provided file/text.")

    segments = normalize_and_split(extracted_text)

    # prepare grouped response
    grouped: Dict[str, List[Dict[str, Any]]] = {
        "termination": [],
        "confidentiality": [],
        "liability": [],
        "governance": [],
        "finance": []
    }

    total_found = 0

    for seg in segments:
        try:
            r = classify_segment(seg)
        except Exception as e:
            # skip segment on classification error but continue
            continue

        if r["confidence"] < threshold:
            continue

        # decide category
        category = r["clause_type"]

        if category in grouped:
            grouped[category].append(r)

        total_found += 1

    # include total counts
    response = {"groups": grouped, "total_clauses_found": total_found}
    return response
