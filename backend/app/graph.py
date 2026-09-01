from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, START, END

from .retriever import search_knowledge
from .verification import extract_claims, verify_claims
from .llm import generate_answer


class KnowledgeState(TypedDict, total=False):
    """State shared across the Knowledge Integrity workflow."""

    question: str
    results: Any
    claims: List[Dict[str, Any]]
    verification: Dict[str, Any]
    answer: str


# =========================================================
# RETRIEVAL
# =========================================================

def retrieve_node(state: KnowledgeState):
    """
    Retrieve relevant evidence from the knowledge base.
    """

    question = state.get("question", "").strip()

    if not question:
        return {
            "results": []
        }

    results = search_knowledge(question)

    if results is None:
        results = []

    return {
        "results": results
    }


# =========================================================
# CLAIM EXTRACTION
# =========================================================

def claims_node(state: KnowledgeState):
    """
    Extract claims from retrieved evidence.

    If evidence exists, it is passed to the verification layer.
    """

    results = state.get("results", [])
    question = state.get("question", "")

    if not results:
        return {
            "claims": []
        }

    claims = extract_claims(
        results,
        question,
    )

    if claims is None:
        claims = []

    return {
        "claims": claims
    }


# =========================================================
# VERIFICATION
# =========================================================

def verification_node(state: KnowledgeState):
    """
    Verify retrieved claims against the knowledge base.
    """

    claims = state.get("claims", [])
    question = state.get("question", "")

    if not claims:
        return {
            "verification": {
                "verified": False,
                "status": "unverified",
                "confidence": 0.0,
                "reason": "No relevant claims were retrieved."
            }
        }

    verification = verify_claims(
        claims,
        question,
    )

    if verification is None:
        verification = {
            "verified": False,
            "status": "unverified",
            "confidence": 0.0,
            "reason": "Verification produced no result."
        }

    return {
        "verification": verification
    }


# =========================================================
# ANSWER GENERATION
# =========================================================

def answer_node(state: KnowledgeState):
    """
    Generate the final answer using verified evidence.

    The LLM is NOT responsible for deciding whether
    information is verified.
    """

    question = state.get("question", "")
    verification = state.get("verification", {})

    # -----------------------------------------------------
    # No verification
    # -----------------------------------------------------

    if not verification.get("verified", False):

        return {
            "answer": (
                "The requested information could not be "
                "verified from the current knowledge base."
            )
        }

    # -----------------------------------------------------
    # Verified information
    # -----------------------------------------------------

    answer = generate_answer(
        question,
        verification,
    )

    # -----------------------------------------------------
    # Safety fallback
    # -----------------------------------------------------

    if not answer or not str(answer).strip():

        answer = verification.get(
            "answer",
            verification.get(
                "claim",
                ""
            )
        )

    return {
        "answer": str(answer).strip()
    }


# =========================================================
# LANGGRAPH WORKFLOW
# =========================================================

workflow = StateGraph(KnowledgeState)

workflow.add_node(
    "retrieve",
    retrieve_node,
)

workflow.add_node(
    "claims",
    claims_node,
)

workflow.add_node(
    "verify",
    verification_node,
)

workflow.add_node(
    "answer",
    answer_node,
)


# =========================================================
# FLOW
# =========================================================

workflow.add_edge(
    START,
    "retrieve",
)

workflow.add_edge(
    "retrieve",
    "claims",
)

workflow.add_edge(
    "claims",
    "verify",
)

workflow.add_edge(
    "verify",
    "answer",
)

workflow.add_edge(
    "answer",
    END,
)


# =========================================================
# COMPILE
# =========================================================

knowledge_graph = workflow.compile()