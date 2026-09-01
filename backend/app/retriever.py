from .embeddings import embeddings
from .qdrant import client, COLLECTION_NAME


def search_knowledge(query: str, limit: int = 12):
    """
    Search the knowledge base for semantically relevant information.

    Returns the strongest matching knowledge chunks from Qdrant.
    """

    query = str(query).strip()

    if not query:
        return []

    # Create the query embedding using the same embedding model
    # used during document indexing.
    query_vector = embeddings.embed_query(query)

    # Query Qdrant.
    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        with_payload=True,
    )

    # Safely extract points.
    results = getattr(response, "points", None)

    if not results:
        return []

    # Make sure every result has usable payload data.
    valid_results = []

    for item in results:

        payload = getattr(item, "payload", None)

        if not isinstance(payload, dict):
            continue

        text = (
            payload.get("text")
            or payload.get("content")
            or payload.get("claim")
        )

        if not text:
            continue

        valid_results.append(item)

    # Highest similarity first.
    valid_results.sort(
        key=lambda item: float(
            getattr(item, "score", 0.0) or 0.0
        ),
        reverse=True,
    )

    return valid_results