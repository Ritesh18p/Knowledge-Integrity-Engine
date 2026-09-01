import re
from typing import Any

from qdrant_client.models import ScoredPoint


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

MIN_SIMILARITY_SCORE = 0.25
MIN_LEXICAL_SCORE = 0.10
MIN_SUPPORT_SCORE = 0.15


# ---------------------------------------------------------
# TEXT NORMALIZATION
# ---------------------------------------------------------

def _normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower()

    # Normalize common punctuation
    text = re.sub(r"[-_/]", " ", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _tokenize(text: str) -> set[str]:
    """
    Extract meaningful words from text.
    """

    normalized = _normalize_text(text)

    words = re.findall(
        r"\b[a-zA-Z]{2,}\b",
        normalized,
    )

    return set(words)


# ---------------------------------------------------------
# STOP WORDS
# ---------------------------------------------------------

STOP_WORDS = {
    "what",
    "which",
    "where",
    "when",
    "who",
    "whom",
    "whose",
    "why",
    "how",
    "many",
    "much",
    "does",
    "do",
    "did",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "should",
    "could",
    "would",
    "can",
    "may",
    "might",
    "must",
    "the",
    "a",
    "an",
    "this",
    "that",
    "these",
    "those",
    "to",
    "of",
    "for",
    "from",
    "with",
    "in",
    "on",
    "at",
    "by",
    "and",
    "or",
    "as",
    "about",
    "into",
    "their",
    "they",
    "them",
    "there",
    "have",
    "has",
    "had",
}


def _meaningful_terms(text: str) -> set[str]:

    words = _tokenize(text)

    return {
        word
        for word in words
        if word not in STOP_WORDS
    }


# ---------------------------------------------------------
# QUESTION INTENT
# ---------------------------------------------------------

def _question_type(question: str) -> str:

    q = _normalize_text(question)

    # HOW MANY / NUMERIC
    if re.search(
        r"\bhow many\b"
        r"|\bhow much\b"
        r"|\bnumber of\b"
        r"|\bcount of\b"
        r"|\bquantity of\b"
        r"|\btotal\b"
        r"|\bamount\b",
        q,
    ):
        return "numeric"

    # FREQUENCY
    if re.search(
        r"\bhow often\b"
        r"|\bhow frequently\b"
        r"|\bfrequency\b"
        r"|\breview frequency\b",
        q,
    ):
        return "frequency"

    # WHO
    if re.search(
        r"\bwho\b"
        r"|\bwhom\b"
        r"\bowner\b"
        r"\bresponsible\b",
        q,
    ):
        return "who"

    # WHEN
    if re.search(
        r"\bwhen\b"
        r"|\bdate\b"
        r"|\bdeadline\b",
        q,
    ):
        return "when"

    # WHERE
    if re.search(
        r"\bwhere\b"
        r"|\blocation\b"
        r"|\brepository\b"
        r"|\bsystem\b"
        r"|\bplatform\b",
        q,
    ):
        return "where"

    return "general"


# ---------------------------------------------------------
# SYNONYMS
# ---------------------------------------------------------

SYNONYMS = {

    "employee": {
        "employee",
        "employees",
        "emplyoee",
        "staff",
        "worker",
        "workers",
        "personnel",
        "team",
        "people",
    },

    "holiday": {
        "holiday",
        "holidays",
        "leave",
        "leaves",
        "vacation",
        "vacations",
        "days",
    },

    "assign": {
        "assign",
        "assigned",
        "assigning",
        "allocation",
        "allocated",
        "entitled",
        "entitlement",
        "given",
        "receive",
        "receives",
        "provided",
    },

    "review": {
        "review",
        "reviews",
        "reviewed",
        "frequency",
        "frequently",
        "period",
        "periodic",
    },

    "approve": {
        "approve",
        "approved",
        "approval",
        "approver",
        "approves",
    },

    "owner": {
        "owner",
        "owns",
        "responsible",
        "responsibility",
        "manager",
        "lead",
        "administrator",
        "admin",
    },
}


def _expand_terms(terms: set[str]) -> set[str]:

    expanded = set(terms)

    for term in list(terms):

        for group in SYNONYMS.values():

            if term in group:
                expanded.update(group)

    return expanded


# ---------------------------------------------------------
# NUMERIC EXTRACTION
# ---------------------------------------------------------

def _extract_numbers(text: str) -> list[str]:

    if not text:
        return []

    return re.findall(
        r"\b\d+(?:\.\d+)?\b",
        text,
    )


# ---------------------------------------------------------
# SENTENCE SPLITTING
# ---------------------------------------------------------

def _split_sentences(text: str) -> list[str]:

    if not text:
        return []

    text = text.strip()

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+|(?<=;)\s+",
        text,
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# ---------------------------------------------------------
# LEXICAL SCORE
# ---------------------------------------------------------

def _lexical_score(
    question: str,
    claim: str,
) -> float:

    question_terms = _expand_terms(
        _meaningful_terms(question)
    )

    claim_terms = _expand_terms(
        _meaningful_terms(claim)
    )

    if not question_terms or not claim_terms:
        return 0.0

    overlap = question_terms.intersection(
        claim_terms
    )

    return len(overlap) / max(
        len(question_terms),
        1,
    )


# ---------------------------------------------------------
# CLAIM EXTRACTION
# ---------------------------------------------------------

def extract_claims(
    results: list[ScoredPoint],
    question: str | None = None,
):

    claims = []

    if not question:
        question = ""

    question_type = _question_type(question)

    for result in results:

        payload = result.payload or {}

        text = payload.get("text", "")

        if not text:
            continue

        similarity = float(
            result.score or 0.0
        )

        for sentence in _split_sentences(text):

            sentence = sentence.strip()

            if not sentence:
                continue

            lexical = _lexical_score(
                question,
                sentence,
            )

            numbers = _extract_numbers(
                sentence
            )

            if question_type == "numeric":
                if (
                    not numbers
                    and lexical < MIN_LEXICAL_SCORE
                    and similarity < MIN_SIMILARITY_SCORE
                ):
                    continue

            elif question_type == "frequency":
                frequency_terms = {
                    "frequency",
                    "frequently",
                    "often",
                    "every",
                    "daily",
                    "weekly",
                    "monthly",
                    "quarterly",
                    "annually",
                    "yearly",
                    "days",
                    "weeks",
                    "months",
                    "years",
                    "review",
                }

                sentence_terms = _meaningful_terms(
                    sentence
                )

                if not (
                    sentence_terms.intersection(
                        frequency_terms
                    )
                    or lexical >= 0.25
                ):
                    continue

            elif question_type == "who":
                responsibility_terms = {
                    "owner",
                    "owns",
                    "responsible",
                    "responsibility",
                    "approver",
                    "approval",
                    "manager",
                    "lead",
                    "administrator",
                    "admin",
                    "team",
                }

                sentence_terms = _meaningful_terms(
                    sentence
                )

                if not (
                    sentence_terms.intersection(
                        responsibility_terms
                    )
                    or lexical >= 0.25
                ):
                    continue

            else:
                if (
                    lexical < MIN_LEXICAL_SCORE
                    and similarity < MIN_SIMILARITY_SCORE
                ):
                    continue

            support_score = (
                similarity * 0.60
                + lexical * 0.40
            )

            claims.append(
                {
                    "claim": sentence,
                    "source": payload.get(
                        "source"
                    ),
                    "chunk_id": payload.get(
                        "chunk_id"
                    ),
                    "updated_at": payload.get(
                        "updated_at"
                    ),
                    "similarity_score": similarity,
                    "lexical_score": round(
                        lexical,
                        3,
                    ),
                    "support_score": round(
                        support_score,
                        3,
                    ),
                    "numbers": numbers,
                }
            )

    claims.sort(
        key=lambda x: x.get(
            "support_score",
            0,
        ),
        reverse=True,
    )

    return claims


def _question_is_supported(
    question: str,
    claims: list[dict],
) -> bool:

    if not claims:
        return False

    question_type = _question_type(
        question
    )

    for claim_data in claims:

        claim = claim_data.get(
            "claim",
            "",
        )

        lexical = float(
            claim_data.get(
                "lexical_score",
                0,
            )
        )

        similarity = float(
            claim_data.get(
                "similarity_score",
                0,
            )
        )

        numbers = claim_data.get(
            "numbers",
            [],
        )

        if (
            lexical >= 0.20
            or similarity >= 0.45
        ):
            return True

        if (
            question_type == "numeric"
            and numbers
            and lexical >= 0.10
        ):
            return True

    return False


def _detect_conflicts(
    claims: list[dict],
) -> bool:
    return False


def verify_claims(
    claims: list[dict],
    question: str | None = None,
):

    verification = {
        "status": "verified",
        "confidence": 0.0,
        "warnings": [],
        "claims": claims,
    }

    if not claims:
        verification["status"] = "unverified"
        verification["warnings"].append(
            "No supporting evidence was found for the question."
        )
        return verification

    if question:
        supported = _question_is_supported(
            question,
            claims,
        )

        if not supported:
            verification["status"] = "unverified"
            verification["warnings"].append(
                "Retrieved evidence does not sufficiently support the requested question."
            )
            verification["claims"] = []
            return verification

    scores = [
        float(
            claim.get(
                "support_score",
                claim.get(
                    "similarity_score",
                    0,
                ),
            )
        )
        for claim in claims
    ]

    confidence = max(
        scores,
        default=0.0,
    )

    verification["confidence"] = round(
        confidence,
        3,
    )

    if confidence < MIN_SUPPORT_SCORE:
        verification["status"] = "needs_review"
        verification["warnings"].append(
            "The retrieved evidence has relatively low support confidence."
        )

    return verification