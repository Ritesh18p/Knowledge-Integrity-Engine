from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Any
import re


from .graph import knowledge_graph


app = FastAPI(
    title="Knowledge Integrity Engine",
    description="Evidence-grounded knowledge verification API",
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# REQUEST MODEL
# =========================================================

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1)


# =========================================================
# HELPERS
# =========================================================

def clean_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def normalize_text(text: str) -> str:
    text = clean_text(text).lower()

    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def keyword_overlap(question: str, evidence: str) -> float:
    q_words = set(normalize_text(question).split())
    e_words = set(normalize_text(evidence).split())

    if not q_words or not e_words:
        return 0.0

    stop_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "to",
        "of",
        "in",
        "on",
        "for",
        "and",
        "or",
        "what",
        "how",
        "many",
        "does",
        "do",
        "can",
        "could",
        "should",
        "would",
    }

    q_words -= stop_words
    e_words -= stop_words

    if not q_words:
        return 0.0

    overlap = q_words.intersection(e_words)

    return len(overlap) / len(q_words)


def get_score(item: Any) -> float:
    try:
        score = float(getattr(item, "score", 0.0) or 0.0)

        if score < 0:
            return 0.0

        if score > 1:
            return 1.0

        return score

    except (TypeError, ValueError):
        return 0.0


def get_payload(item: Any) -> dict:
    payload = getattr(item, "payload", None)

    if not isinstance(payload, dict):
        return {}

    return payload


# =========================================================
# ENDPOINTS
# =========================================================

@app.get("/")
def root():
    return {
        "message": "Knowledge Integrity Engine API is running.",
        "status": "online",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Knowledge Integrity Engine",
        "version": "1.0.0",
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = clean_text(request.question)

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        result = knowledge_graph.invoke(
            {
                "question": question
            }
        )

        if not isinstance(result, dict):
            raise HTTPException(
                status_code=500,
                detail="Knowledge graph returned an invalid response.",
            )

        raw_results = result.get("results", [])

        if raw_results is None:
            raw_results = []

        evidence = []

        for item in raw_results:
            payload = get_payload(item)

            text = clean_text(
                payload.get("text")
                or payload.get("content")
                or payload.get("claim")
            )

            if not text:
                continue

            semantic_score = get_score(item)

            lexical_score = keyword_overlap(
                question,
                text,
            )

            combined_score = max(
                semantic_score,
                lexical_score,
            )

            evidence.append(
                {
                    "claim": text,
                    "source": payload.get("source"),
                    "chunk_id": payload.get("chunk_id"),
                    "similarity_score": round(semantic_score, 4),
                    "lexical_score": round(lexical_score, 4),
                    "confidence_score": round(combined_score, 4),
                    "updated_at": payload.get("updated_at"),
                }
            )

        evidence.sort(
            key=lambda x: x["confidence_score"],
            reverse=True,
        )

        unique_evidence = []
        seen = set()

        for item in evidence:
            normalized_claim = normalize_text(item["claim"])

            if normalized_claim in seen:
                continue

            seen.add(normalized_claim)
            unique_evidence.append(item)

        evidence = unique_evidence

        answer = clean_text(result.get("answer"))
        verification = result.get("verification", {})

        if not isinstance(verification, dict):
            verification = {}

        best_evidence = evidence[0] if evidence else None

        if best_evidence:
            confidence = best_evidence["confidence_score"]
            claim = best_evidence["claim"]

            if confidence >= 0.20:
                if not answer or "could not be verified" in answer:
                    answer = f"According to organizational policy: {claim}"

                verification = {
                    **verification,
                    "verified": True,
                    "status": "verified",
                    "confidence": round(confidence, 4),
                    "reason": "Answer supported by retrieved knowledge-base evidence.",
                }
            else:
                answer = "The available knowledge-base evidence is insufficient to verify this information."
                verification = {
                    **verification,
                    "verified": False,
                    "status": "unverified",
                    "confidence": round(confidence, 4),
                    "reason": "Retrieved evidence was not strong enough to verify the answer.",
                }
        else:
            answer = "The requested information could not be verified from the current knowledge base."
            verification = {
                **verification,
                "verified": False,
                "status": "unverified",
                "confidence": 0.0,
                "reason": "No relevant evidence was retrieved from the knowledge base.",
            }

        return {
            "question": question,
            "answer": answer,
            "verification": verification,
            "evidence": evidence,
            "evidence_count": len(evidence),
        }

    except HTTPException:
        raise

    except Exception as exc:
        print("Knowledge graph error:", repr(exc))
        raise HTTPException(
            status_code=500,
            detail="Knowledge engine failed while processing the question.",
        )