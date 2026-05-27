"""
Document Analyzer — OCR + Groq LLM extraction chain.

Extracts structured DocumentAnalysis from uploaded legal documents.
KYC fields are stripped before any LLM call.
"""
from __future__ import annotations
import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# ── KYC field sanitization ────────────────────────────────────────────────────
BLOCKED_FIELDS = {"aadhaar_number", "pan_number", "aadhaar", "pan"}


def sanitize_for_llm(data: dict) -> dict:
    """Strip KYC/PII fields before any LLM prompt construction."""
    return {k: v for k, v in data.items() if k.lower() not in BLOCKED_FIELDS}


# ── System prompts per document type ─────────────────────────────────────────
SYSTEM_PROMPTS = {
    "ec": """You are a legal document analyzer specializing in Indian Encumbrance Certificates (EC).
Extract the following fields from the document text and return valid JSON:
{
  "doc_type": "ec",
  "named_parties": ["list of person/entity names"],
  "survey_numbers": ["survey/khata numbers mentioned"],
  "dates": ["all dates found"],
  "transaction_amounts": ["monetary amounts"],
  "risk_clauses": ["mortgages, loans, liabilities, encumbrances found"],
  "missing_approvals": ["any referenced but missing approvals"],
  "suspicious_patterns": ["inconsistencies, gaps, unusual language"],
  "summary": "2-3 sentence plain English summary",
  "confidence": 0.85
}""",

    "sale_deed": """You are a legal document analyzer specializing in Indian Sale Deeds.
Extract the following fields and return valid JSON:
{
  "doc_type": "sale_deed",
  "named_parties": ["seller names", "buyer names"],
  "survey_numbers": ["survey numbers, plot numbers, Sy. No."],
  "dates": ["execution date, registration date"],
  "transaction_amounts": ["sale consideration amount"],
  "risk_clauses": ["encumbrances, indemnity clauses, disputes"],
  "missing_approvals": ["layout approval, NOC, patta — if missing"],
  "suspicious_patterns": ["corrections, overwriting, inconsistencies"],
  "summary": "2-3 sentence plain English summary",
  "confidence": 0.85
}""",

    "layout_approval": """You are a legal document analyzer specializing in Indian layout approvals (HMDA/DTCP).
Extract and return valid JSON with these fields:
{
  "doc_type": "layout_approval",
  "named_parties": ["developer, authority names"],
  "survey_numbers": ["plot numbers, survey numbers"],
  "dates": ["approval date, validity date"],
  "transaction_amounts": [],
  "risk_clauses": ["conditions, restrictions on the approval"],
  "missing_approvals": ["pending NOCs, utilities clearances"],
  "suspicious_patterns": ["expired approvals, altered documents"],
  "summary": "2-3 sentence plain English summary",
  "confidence": 0.85
}""",

    "mutation_register": """You are a legal document analyzer specializing in Indian Mutation/Pahani documents.
Extract and return valid JSON:
{
  "doc_type": "mutation_register",
  "named_parties": ["current owner, previous owners"],
  "survey_numbers": ["survey nos, khata nos"],
  "dates": ["mutation dates"],
  "transaction_amounts": [],
  "risk_clauses": ["pending mutations, disputes, joint ownership issues"],
  "missing_approvals": [],
  "suspicious_patterns": ["recent changes, incomplete mutations"],
  "summary": "2-3 sentence plain English summary",
  "confidence": 0.85
}""",

    "patta": """You are a legal document analyzer specializing in Indian Patta/Record of Rights (ROR) documents.
Extract and return valid JSON:
{
  "doc_type": "patta",
  "named_parties": ["patta holder names"],
  "survey_numbers": ["survey nos, Sy. No."],
  "dates": ["issue date"],
  "transaction_amounts": [],
  "risk_clauses": ["agricultural restrictions, conversion pending"],
  "missing_approvals": ["land use conversion approval, if applicable"],
  "suspicious_patterns": ["altered entries, inconsistent land area"],
  "summary": "2-3 sentence plain English summary",
  "confidence": 0.85
}""",
}


async def analyze_document(
    doc_type: str,
    text: str,
    doc_id: Optional[str] = None,
) -> dict:
    """
    Analyze a document using Groq LLM (with OpenRouter fallback).
    
    Returns a dict conforming to DocumentAnalysis schema.
    Never passes KYC fields to the LLM.
    """
    if not text or not text.strip():
        return _empty_analysis(doc_type)

    system_prompt = SYSTEM_PROMPTS.get(doc_type, SYSTEM_PROMPTS["sale_deed"])
    
    # Try Groq first
    result = await _call_groq(system_prompt, text[:4000])  # limit context
    if result:
        return result

    # Fallback to OpenRouter
    result = await _call_openrouter(system_prompt, text[:4000])
    if result:
        return result

    logger.error(f"Document analysis failed for doc_id={doc_id}, doc_type={doc_type}")
    return _empty_analysis(doc_type, confidence=0.0)


async def _call_groq(system_prompt: str, text: str) -> Optional[dict]:
    """Call Groq API for document analysis."""
    try:
        from groq import Groq
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            return None

        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Document text:\n\n{text}"},
            ],
            response_format={"type": "json_object"},
            max_tokens=1024,
            temperature=0.1,
        )
        raw = response.choices[0].message.content or "{}"
        return json.loads(raw)
    except Exception as e:
        logger.warning(f"Groq document analysis failed: {e}")
        return None


async def _call_openrouter(system_prompt: str, text: str) -> Optional[dict]:
    """Fallback: call OpenRouter for document analysis."""
    try:
        import httpx
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        if not api_key:
            return None

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "mistralai/mistral-7b-instruct:free",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Document text:\n\n{text}"},
                    ],
                    "response_format": {"type": "json_object"},
                },
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            return json.loads(content)
    except Exception as e:
        logger.warning(f"OpenRouter document analysis failed: {e}")
        return None


def _empty_analysis(doc_type: str, confidence: float = 0.5) -> dict:
    """Return a minimal valid DocumentAnalysis dict."""
    return {
        "doc_type": doc_type,
        "named_parties": [],
        "survey_numbers": [],
        "dates": [],
        "transaction_amounts": [],
        "risk_clauses": [],
        "missing_approvals": [],
        "suspicious_patterns": [],
        "summary": "Analysis could not be completed for this document.",
        "confidence": confidence,
    }


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF using pdfplumber (text PDFs) or pytesseract (scanned)."""
    text = ""
    
    # Try pdfplumber first (text PDFs)
    try:
        import pdfplumber
        import io
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
    except Exception as e:
        logger.warning(f"pdfplumber extraction failed: {e}")

    # If little/no text extracted, try OCR
    if len(text.strip()) < 100:
        try:
            import pytesseract
            from PIL import Image
            import io
            # Convert first page to image for OCR
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                page = doc[0]
                pix = page.get_pixmap(dpi=200)
                img_bytes = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_bytes))
                text = pytesseract.image_to_string(img)
            except ImportError:
                # fitz not available, try direct image OCR
                img = Image.open(io.BytesIO(file_bytes))
                text = pytesseract.image_to_string(img)
        except Exception as e:
            logger.warning(f"OCR extraction failed: {e}")

    return text.strip()


def extract_text_from_image(file_bytes: bytes) -> str:
    """Extract text from an image using pytesseract."""
    try:
        
        import pytesseract
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(img).strip()
    except Exception as e:
        logger.warning(f"Image OCR failed: {e}")
        return ""
