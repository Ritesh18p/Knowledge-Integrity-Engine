from uuid import uuid4
from pathlib import Path
from datetime import datetime

from qdrant_client.models import PointStruct

from ingestion import load_documents
from chunking import split_document
from embeddings import embeddings
from qdrant import client, COLLECTION_NAME


def index_documents():
    documents = load_documents()
    points = []

    for document in documents:

        # Get the original document path.
        source = document.metadata.get("source")

        # Get the real file modification time.
        updated_at = None

        if source:
            try:
                modified_timestamp = Path(source).stat().st_mtime
                updated_at = datetime.fromtimestamp(
                    modified_timestamp
                ).isoformat(timespec="seconds")
            except (FileNotFoundError, OSError):
                updated_at = None

        # Split the document into chunks.
        chunks = split_document(document.page_content)

        for chunk_index, chunk in enumerate(chunks):

            # Generate the embedding vector.
            vector = embeddings.embed_query(chunk)

            # Store metadata with the vector.
            payload = {
                "text": chunk,
                "source": source,
                "chunk_id": chunk_index,
                "updated_at": updated_at,
            }

            point = PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload=payload,
            )

            points.append(point)

    # Store all vectors in Qdrant.
    if points:
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

    print(f"Indexed {len(points)} knowledge chunks into Qdrant.")


if __name__ == "__main__":

    # Start document indexing.
    index_documents()

    print("Knowledge indexing completed successfully.")