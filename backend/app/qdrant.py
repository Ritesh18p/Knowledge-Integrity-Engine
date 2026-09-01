# Import QdrantClient to communicate with our local Qdrant database.
from qdrant_client import QdrantClient

# Import the vector configuration classes required to create a collection.
from qdrant_client.models import Distance, VectorParams


# Connect to the Qdrant instance running locally on our computer.
# No Qdrant Cloud URL or API key is required.
client = QdrantClient(
    host="localhost",
    port=6333,
)


# Define the name of our knowledge collection.
COLLECTION_NAME = "knowledge_integrity"


# Define the vector size produced by all-MiniLM-L6-v2.
VECTOR_SIZE = 384


def create_collection():
    """
    Create the Qdrant collection used by the Knowledge Integrity Engine.
    """

    # Check whether our collection already exists.
    existing_collections = client.get_collections().collections

    # Extract the names of the existing collections.
    collection_names = [
        collection.name
        for collection in existing_collections
    ]

    # Create our collection only if it doesn't already exist.
    if COLLECTION_NAME not in collection_names:

        # Configure Qdrant to store 384-dimensional vectors.
        client.create_collection(
            collection_name=COLLECTION_NAME,

            # Use cosine similarity to compare semantic embeddings.
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

        # Confirm that the collection was created.
        print(f"Created Qdrant collection: {COLLECTION_NAME}")

    else:

        # Tells us that the collection already exists.
        print(f"Qdrant collection already exists: {COLLECTION_NAME}")