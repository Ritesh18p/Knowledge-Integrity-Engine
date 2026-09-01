import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing from the .env file.")

client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "openai/gpt-oss-20b"


def generate_answer(question: str, verification: dict) -> str:
    """
    Generate a grounded answer using only verified knowledge.
    """

    claims = verification.get("claims", [])
    status = verification.get("status", "unverified")
    warnings = verification.get("warnings", [])

    if not claims:
        return (
            "The requested information could not be verified "
            "from the current knowledge base."
        )

    evidence_text = "\n".join(
        [
            f"- {claim['claim']} "
            f"(Source: {claim.get('source')})"
            for claim in claims
        ]
    )

    warning_text = "\n".join(
        f"- {warning}"
        for warning in warnings
    ) or "None"

    prompt = f"""
You are an enterprise Knowledge Integrity Engine.

Your job is to answer the user's question using ONLY the supplied
knowledge claims.

Strict rules:
1. Do not invent facts, people, roles, dates, or policies.
2. Do not use outside knowledge.
3. Do not assume information that is not explicitly supported.
4. If the evidence does not answer the exact question, say so clearly.
5. If verification status is "needs_review", do not present the
   information as completely verified.
6. Keep the answer concise.
7. Mention the source when available.

User question:
{question}

Verification status:
{status}

Verification warnings:
{warning_text}

Verified knowledge claims:
{evidence_text}

Now answer the user's question.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict enterprise knowledge "
                    "integrity assistant. Ground every answer "
                    "in the supplied evidence."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=500,
    )

    return response.choices[0].message.content or (
        "The information could not be verified."
    )