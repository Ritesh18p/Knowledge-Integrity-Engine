from uuid import uuid4
from pathlib import Path
from datetime import datetime

from qdrant_client.models import PointStruct

from app.ingestion import load_documents
from app.chunking import split_document
from app.embeddings import embeddings
from app.qdrant import client, COLLECTION_NAME


def index_documents():
    """Load documents, create embeddings, and store them in Qdrant."""

    client.delete_collection(COLLECTION_NAME)

    from app.qdrant import create_collection
    create_collection()

    documents = load_documents()

    points = []

    for document in documents:

        # Get the original document path.
        source = document.metadata.get("source")

        # Get the real file modification time for freshness tracking.
        updated_at = None
        if source:
            try:
                modified_timestamp = Path(source).stat().st_mtime
                updated_at = datetime.fromtimestamp(
                    modified_timestamp
                ).isoformat(timespec="seconds")
            except (FileNotFoundError, OSError):
                updated_at = None

        chunks = split_document(document.page_content)

        for chunk_index, chunk in enumerate(chunks):

            vector = embeddings.embed_query(chunk)

            payload = {
                "text": chunk,
                "source": source,
                "chunk_id": chunk_index,
                "updated_at": updated_at,  # Now tracking freshness!
                "version": 1,
            }

            points.append(
                PointStruct(
                    id=str(uuid4()),
                    vector=vector,
                    payload=payload,
                )
            )

    if points:
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

    print(f"Indexed {len(points)} knowledge chunks into Qdrant.")


if __name__ == "__main__":
    index_documents()
    print("Knowledge indexing completed successfully.")